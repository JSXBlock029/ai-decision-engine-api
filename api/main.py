"""
AI Decision Engine API - FastAPI Implementation
Main API server with enhanced error handling and validation
"""

from fastapi import FastAPI, Header, HTTPException, Depends, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, HTMLResponse
from fastapi.exceptions import RequestValidationError
from pydantic import BaseModel, Field, field_validator
from typing import Optional, Dict, Any, List
import html
import re
import time
from collections import defaultdict, deque
from api.admin_auth import verify_admin
from api.api_key_manager import hash_key
from datetime import datetime
import os
import logging
import traceback

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Import our existing decision engine
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from ai_decision_engine import AIDecisionEngine, DecisionCategory, RiskLevel

app = FastAPI(
    title="AI Decision Engine API",
    description="RESTful API for AI-driven decision-making framework",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS middleware - configure for production
cors_origins = os.getenv("ALLOWED_ORIGINS", "*").split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins if "*" not in cors_origins else ["*"],
    allow_credentials="*" not in cors_origins,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Analytics middleware
from api.analytics_middleware import AnalyticsMiddleware
app.add_middleware(AnalyticsMiddleware)

# Initialize decision engine
try:
    decision_engine = AIDecisionEngine()
    logger.info("Decision engine initialized successfully")
except Exception as e:
    logger.error(f"Failed to initialize decision engine: {e}")
    raise

# Import API key manager and analytics
from api.api_key_manager import api_key_manager
from api.analytics import api_analytics
import time

# API Key authentication
def verify_api_key(x_api_key: Optional[str] = Header(None, alias="X-API-Key")) -> Dict[str, Any]:
    """
    Verify API key from header
    
    Args:
        x_api_key: API key from X-API-Key header
    
    Returns:
        API key information if valid
    
    Raises:
        HTTPException: If API key is invalid or missing
    """
    if not x_api_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="API key required. Include X-API-Key header."
        )
    
    # Validate API key
    key_info = api_key_manager.validate_api_key(x_api_key)
    
    if not key_info:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or inactive API key"
        )
    
    # Record request for rate limiting
    api_key_manager.record_request(x_api_key)

    # Return key info
    return {
        "tier": key_info.get("tier", "free"),
        "requests_per_month": key_info.get("requests_per_month", 100),
        "api_key": x_api_key[:10] + "...",  # Partial key for logging
        "_full_key": x_api_key  # Full key for internal use (not exposed in logs)
    }


_EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]{2,}$")


def _valid_email(value: Optional[str]) -> bool:
    return bool(value) and len(value) <= 254 and bool(_EMAIL_RE.match(value.strip()))


_FREE_KEY_LIMIT = int(os.getenv("FREE_KEY_LIMIT_PER_HOUR", "5"))
_free_key_hits: Dict[str, deque] = defaultdict(deque)


def _client_ip(request: Request) -> str:
    if os.getenv("TRUST_PROXY", "").lower() in ("1", "true", "yes"):
        fwd = request.headers.get("x-forwarded-for", "")
        if fwd:
            return fwd.split(",")[0].strip()
    return request.client.host if request.client else "unknown"


def _free_key_allowed(ip: str) -> bool:
    """Sliding one-hour window per client IP. In-memory: resets on restart."""
    now = time.time()
    hits = _free_key_hits[ip]
    while hits and now - hits[0] > 3600:
        hits.popleft()
    if len(hits) >= _FREE_KEY_LIMIT:
        return False
    hits.append(now)
    return True


# Pydantic models for request validation
class DecisionEvaluationRequest(BaseModel):
    category: str = Field(..., description="Decision category")
    amount: float = Field(default=0.0, ge=0, description="Amount involved")
    description: str = Field(default="", max_length=1000, description="Decision description")
    
    @field_validator('category')
    @classmethod
    def validate_category(cls, v):
        valid_categories = [cat.name for cat in DecisionCategory]
        if v.upper() not in valid_categories:
            raise ValueError(f"Category must be one of: {', '.join(valid_categories)}")
        return v.upper()


class RiskAssessmentRequest(BaseModel):
    amount: float = Field(default=0.0, ge=0, description="Amount involved")
    category: str = Field(default="OPERATIONAL", description="Decision category")
    description: str = Field(default="", max_length=1000, description="Risk assessment description")
    
    @field_validator('category')
    @classmethod
    def validate_category(cls, v):
        valid_categories = [cat.name for cat in DecisionCategory]
        if v.upper() not in valid_categories:
            raise ValueError(f"Category must be one of: {', '.join(valid_categories)}")
        return v.upper()


class AutoExecuteRequest(BaseModel):
    task_type: str = Field(..., description="Type of task")
    risk_level: str = Field(default="LOW", description="Risk level")
    
    @field_validator('risk_level')
    @classmethod
    def validate_risk_level(cls, v):
        valid_levels = ["LOW", "MEDIUM", "HIGH", "CRITICAL"]
        if v.upper() not in valid_levels:
            raise ValueError(f"Risk level must be one of: {', '.join(valid_levels)}")
        return v.upper()


class MemoryInsightsRequest(BaseModel):
    decision_data: Dict[str, Any] = Field(default_factory=dict, description="Decision data for insights")


# Global exception handlers
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Handle validation errors"""
    logger.warning(f"Validation error: {exc.errors()}")
    return JSONResponse(
        status_code=422,
        content={
            "error": "Validation Error",
            "details": [{"loc": list(e.get("loc", [])), "msg": str(e.get("msg", "")), "type": e.get("type", "")} for e in exc.errors()],
            "message": "Invalid request data"
        }
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """Handle unexpected errors"""
    logger.error(f"Unexpected error: {exc}", exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": "Internal Server Error",
            "message": "An unexpected error occurred",
            "timestamp": datetime.now().isoformat()
        }
    )


# Landing page HTML (embedded to avoid file path issues)
LANDING_PAGE_HTML = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>AI Decision Engine API - RESTful API for AI-driven Decision Making</title>
    <meta name="description" content="RESTful API for AI-driven decision-making, risk assessment, and autonomy tracking. Built for developers creating autonomous AI systems.">
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif; line-height: 1.6; color: #333; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); min-height: 100vh; }
        .container { max-width: 1200px; margin: 0 auto; padding: 0 20px; }
        header { background: rgba(255, 255, 255, 0.95); padding: 20px 0; box-shadow: 0 2px 10px rgba(0,0,0,0.1); position: sticky; top: 0; z-index: 100; }
        nav { display: flex; justify-content: space-between; align-items: center; }
        .logo { font-size: 24px; font-weight: bold; color: #667eea; }
        .nav-links { display: flex; gap: 30px; list-style: none; }
        .nav-links a { text-decoration: none; color: #333; font-weight: 500; transition: color 0.3s; }
        .nav-links a:hover { color: #667eea; }
        .hero { text-align: center; padding: 100px 20px; color: white; }
        .hero h1 { font-size: 48px; margin-bottom: 20px; animation: fadeInUp 0.8s; }
        .hero p { font-size: 22px; margin-bottom: 40px; opacity: 0.95; animation: fadeInUp 1s; }
        .cta-buttons { display: flex; gap: 20px; justify-content: center; flex-wrap: wrap; animation: fadeInUp 1.2s; margin-top: 40px; }
        .cta-button { display: inline-block; padding: 15px 40px; background: white; color: #667eea; text-decoration: none; border-radius: 50px; font-weight: bold; font-size: 18px; transition: transform 0.3s, box-shadow 0.3s; }
        .cta-button:hover { transform: translateY(-2px); box-shadow: 0 10px 25px rgba(0,0,0,0.2); }
        .cta-button.secondary { background: transparent; border: 2px solid white; color: white; }
        .cta-button.secondary:hover { background: white; color: #667eea; }
        .features { background: white; padding: 80px 20px; }
        .features h2 { text-align: center; font-size: 36px; margin-bottom: 50px; color: #333; }
        .features-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 30px; margin-top: 40px; }
        .feature-card { padding: 30px; background: #f8f9fa; border-radius: 15px; transition: transform 0.3s, box-shadow 0.3s; }
        .feature-card:hover { transform: translateY(-5px); box-shadow: 0 10px 25px rgba(0,0,0,0.1); }
        .feature-icon { font-size: 40px; margin-bottom: 15px; }
        .feature-card h3 { font-size: 24px; margin-bottom: 10px; color: #667eea; }
        .pricing-section { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 80px 20px; color: white; text-align: center; }
        .pricing-section h2 { font-size: 36px; margin-bottom: 20px; }
        .pricing-section p { font-size: 18px; margin-bottom: 40px; opacity: 0.95; }
        .footer { background: #333; color: white; padding: 40px 20px; text-align: center; }
        .status-badge { display: inline-block; padding: 5px 15px; background: #4caf50; color: white; border-radius: 20px; font-size: 14px; margin-left: 10px; }
        @keyframes fadeInUp { from { opacity: 0; transform: translateY(30px); } to { opacity: 1; transform: translateY(0); } }
        @media (max-width: 768px) { .hero h1 { font-size: 36px; } .nav-links { display: none; } .cta-buttons { flex-direction: column; align-items: center; } }
    </style>
</head>
<body>
    <header>
        <nav class="container">
            <div class="logo">🚀 AI Decision Engine API</div>
            <ul class="nav-links">
                <li><a href="#features">Features</a></li>
                <li><a href="#pricing">Pricing</a></li>
                <li><a href="/docs">API Docs</a></li>
            </ul>
        </nav>
    </header>
    <section class="hero">
        <div class="container">
            <h1>AI Decision Engine API</h1>
            <p>RESTful API for AI-driven decision-making, risk assessment, and autonomy tracking</p>
            <span class="status-badge">● Operational</span>
            <div class="cta-buttons">
                <a href="/docs" class="cta-button">View API Documentation</a>
                <a href="#pricing" class="cta-button secondary">View Pricing</a>
            </div>
        </div>
    </section>
    <section class="features" id="features">
        <div class="container">
            <h2>Powerful API Features</h2>
            <div class="features-grid">
                <div class="feature-card">
                    <div class="feature-icon">🎯</div>
                    <h3>Decision Evaluation</h3>
                    <p>Evaluate decisions using AI frameworks with risk assessment and autonomy level checking.</p>
                </div>
                <div class="feature-card">
                    <div class="feature-icon">⚠️</div>
                    <h3>Risk Assessment</h3>
                    <p>Automatically assess risk levels (LOW/MEDIUM/HIGH/CRITICAL) with detailed recommendations.</p>
                </div>
                <div class="feature-card">
                    <div class="feature-icon">🤖</div>
                    <h3>Autonomy Tracking</h3>
                    <p>Track AI autonomy progression and determine when AI should autonomously execute tasks.</p>
                </div>
                <div class="feature-card">
                    <div class="feature-icon">🧠</div>
                    <h3>Memory Insights</h3>
                    <p>Get insights from AI memory system with similar decisions and success patterns.</p>
                </div>
                <div class="feature-card">
                    <div class="feature-icon">📊</div>
                    <h3>Analytics</h3>
                    <p>Real-time usage tracking, performance metrics, and endpoint analytics.</p>
                </div>
                <div class="feature-card">
                    <div class="feature-icon">🔐</div>
                    <h3>Secure Authentication</h3>
                    <p>API key-based authentication with tiered access control and rate limiting.</p>
                </div>
            </div>
        </div>
    </section>
    <section class="pricing-section" id="pricing">
        <div class="container">
            <h2>Simple, Transparent Pricing</h2>
            <p>Start free, upgrade when you need more</p>
            <div style="margin-top: 40px;">
                <a href="/pricing" class="cta-button" style="background: white; color: #667eea;">View All Plans</a>
            </div>
        </div>
    </section>
    <footer class="footer">
        <div class="container">
            <p>&copy; 2025 AI Decision Engine. Built by AI, for developers.</p>
            <p style="margin-top: 10px;">
                <a href="https://github.com/lowriskbtc/ai-decision-engine-api" style="color: white; text-decoration: none;">GitHub</a> | 
                <a href="/docs" style="color: white; text-decoration: none;">API Documentation</a> | 
                <a href="/health" style="color: white; text-decoration: none;">Health Check</a>
            </p>
        </div>
    </footer>
    <script>
        document.querySelectorAll('a[href^="#"]').forEach(anchor => {
            anchor.addEventListener('click', function (e) {
                e.preventDefault();
                const target = document.querySelector(this.getAttribute('href'));
                if (target) target.scrollIntoView({ behavior: 'smooth', block: 'start' });
            });
        });
    </script>
</body>
</html>"""


@app.get("/", response_class=HTMLResponse)
async def root(request: Request):
    """
    Root endpoint - serves HTML landing page for browsers, JSON for API clients
    """
    # Check if request is from a browser (has Accept: text/html) or API client
    accept_header = request.headers.get("accept", "")
    
    if "text/html" in accept_header.lower():
        # Serve embedded HTML landing page for browsers
        return HTMLResponse(content=LANDING_PAGE_HTML)
    
    # Return JSON for API clients
    return JSONResponse(content={
        "message": "AI Decision Engine API",
        "version": "1.0.0",
        "status": "operational",
        "documentation": "/docs",
        "health": "/health",
        "endpoints": {
            "health": "/health",
            "docs": "/docs",
            "redoc": "/redoc",
            "evaluate_decision": "/decisions/evaluate",
            "assess_risk": "/risk/assess",
            "autonomy_level": "/autonomy/level",
            "pricing": "/pricing"
        }
    })


@app.get("/health")
async def health_check():
    """Health check endpoint with detailed system status"""
    try:
        # Check decision engine status
        autonomy_status = decision_engine.autonomy.get_autonomy_level()
        
        return {
            "status": "healthy",
            "version": "1.0.0",
            "timestamp": datetime.now().isoformat(),
            "autonomy_level": autonomy_status,
            "system": "operational"
        }
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content={
                "status": "unhealthy",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
        )


@app.post("/decisions/evaluate", response_model=Dict[str, Any])
async def evaluate_decision(
    decision_request: DecisionEvaluationRequest,
    api_info: Dict[str, Any] = Depends(verify_api_key)
):
    """
    Evaluate a decision using AI decision-making framework
    
    - **category**: Decision category (STRATEGIC, OPERATIONAL, FINANCIAL, etc.)
    - **amount**: Amount involved (default: 0)
    - **description**: Description of the decision
    """
    try:
        logger.info(f"Evaluating decision: {decision_request.category} - ${decision_request.amount}")
        
        # Convert to decision data format
        decision_data = {
            "category": decision_request.category,
            "amount": decision_request.amount,
            "description": decision_request.description
        }
        
        # Convert category string to enum value
        category_str = decision_data.get("category", "OPERATIONAL")
        decision_data["category"] = DecisionCategory[category_str].value if category_str in DecisionCategory.__members__ else category_str
        
        # Evaluate decision
        result = decision_engine.evaluate_decision(decision_data)
        
        # Convert to JSON-serializable format
        response = {
            "id": result.get("id"),
            "timestamp": result.get("timestamp"),
            "category": result.get("category"),
            "risk_level": result.get("risk_level"),
            "description": result.get("description"),
            "amount": result.get("amount"),
            "status": result.get("status"),
            "action_required": result.get("action_required"),
            "ai_can_decide": result.get("ai_can_decide"),
            "autonomy_level": result.get("autonomy_level"),
            "memory_insights": result.get("memory_insights", {})
        }
        
        logger.info(f"Decision evaluated: {result.get('id')} - Risk: {result.get('risk_level')}")
        return response
        
    except KeyError as e:
        logger.error(f"Invalid category: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid category. Must be one of: {', '.join([cat.name for cat in DecisionCategory])}"
        )
    except Exception as e:
        logger.error(f"Error evaluating decision: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error evaluating decision"
        )


@app.post("/risk/assess", response_model=Dict[str, Any])
async def assess_risk(
    risk_request: RiskAssessmentRequest,
    api_info: Dict[str, Any] = Depends(verify_api_key)
):
    """
    Assess risk level for a decision or action
    
    - **amount**: Amount involved
    - **category**: Decision category
    - **description**: Description of the risk assessment
    """
    try:
        logger.info(f"Assessing risk: {risk_request.category} - ${risk_request.amount}")
        
        # Create decision data for risk assessment
        decision_data = {
            "amount": risk_request.amount,
            "category": risk_request.category,
            "description": risk_request.description
        }
        
        # Get memory insights for context
        memory_insights = decision_engine.memory.inform_decision(decision_data)
        
        # Assess risk
        risk_level = decision_engine._assess_risk(decision_data, memory_insights)
        
        # Get risk thresholds
        thresholds = decision_engine.risk_thresholds.get(risk_level, {})
        
        response = {
            "risk_level": risk_level.value,
            "risk_score": _calculate_risk_score(risk_level, risk_request.amount),
            "recommendation": _get_risk_recommendation(risk_level),
            "thresholds": {
                "max_amount": thresholds.get("max_amount"),
                "auto_execute": thresholds.get("auto_execute", False)
            },
            "timestamp": datetime.now().isoformat()
        }
        
        logger.info(f"Risk assessed: {risk_level.value} - Score: {response['risk_score']}")
        return response
        
    except Exception as e:
        logger.error(f"Error assessing risk: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error assessing risk"
        )


@app.get("/autonomy/level", response_model=Dict[str, Any])
async def get_autonomy_level(
    api_info: Dict[str, Any] = Depends(verify_api_key)
):
    """
    Get current AI autonomy level and system status
    
    Returns:
    - autonomy_level: Current autonomy percentage
    - target_autonomy: Target autonomy percentage
    - human_tasks: Remaining human tasks
    - ai_tasks: AI-managed tasks
    - proven_capabilities: List of proven AI capabilities
    """
    try:
        autonomy_system = decision_engine.autonomy
        tracker = autonomy_system.tracker
        
        status_data = tracker.get_autonomy_status()
        
        response = {
            "autonomy_level": status_data["current_autonomy"],
            "target_autonomy": status_data["target_autonomy"],
            "human_tasks": status_data["remaining_tasks"],
            "ai_tasks": status_data["ai_tasks"],
            "proven_capabilities": status_data["proven_capabilities"],
            "timestamp": datetime.now().isoformat()
        }
        
        return response
        
    except Exception as e:
        logger.error(f"Error getting autonomy level: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error getting autonomy level"
        )


@app.post("/autonomy/should-execute", response_model=Dict[str, Any])
async def should_auto_execute(
    execute_request: AutoExecuteRequest,
    api_info: Dict[str, Any] = Depends(verify_api_key)
):
    """
    Determine if AI should autonomously execute a task
    
    - **task_type**: Type of task (e.g., "operational", "financial")
    - **risk_level**: Risk level (LOW, MEDIUM, HIGH, CRITICAL)
    """
    try:
        logger.info(f"Checking auto-execute: {execute_request.task_type} - {execute_request.risk_level}")
        
        should_execute = decision_engine.autonomy.should_auto_execute(
            execute_request.task_type, 
            execute_request.risk_level
        )
        
        response = {
            "should_execute": should_execute,
            "reason": _get_execution_reason(should_execute, execute_request.task_type, execute_request.risk_level),
            "task_type": execute_request.task_type,
            "risk_level": execute_request.risk_level,
            "timestamp": datetime.now().isoformat()
        }
        
        return response
        
    except Exception as e:
        logger.error(f"Error checking execution: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error checking execution"
        )


@app.post("/memory/insights", response_model=Dict[str, Any])
async def get_memory_insights(
    insights_request: MemoryInsightsRequest,
    api_info: Dict[str, Any] = Depends(verify_api_key)
):
    """
    Get insights from AI memory system
    
    - **decision_data**: Decision data dictionary for context
    """
    try:
        logger.info("Fetching memory insights")
        
        decision_data = insights_request.decision_data
        
        insights = decision_engine.memory.inform_decision(decision_data)
        
        response = {
            "similar_decisions": len(insights.get("similar_decisions", [])) if isinstance(insights.get("similar_decisions"), list) else 0,
            "success_patterns": insights.get("success_patterns", {}),
            "recommendations": insights.get("recommendations", []) if isinstance(insights.get("recommendations"), list) else [],
            "timestamp": datetime.now().isoformat()
        }
        
        return response
        
    except Exception as e:
        logger.error(f"Error getting memory insights: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error getting memory insights"
        )


# Helper methods
def _calculate_risk_score(risk_level, amount):
    """Calculate risk score 0-100"""
    base_scores = {
        RiskLevel.LOW: 25,
        RiskLevel.MEDIUM: 50,
        RiskLevel.HIGH: 75,
        RiskLevel.CRITICAL: 100
    }
    base_score = base_scores.get(risk_level, 50)
    
    # Adjust based on amount (higher amounts = higher risk)
    if amount > 100000:
        base_score += 10
    elif amount > 50000:
        base_score += 5
    
    return min(base_score, 100)


def _get_risk_recommendation(risk_level):
    """Get recommendation based on risk level"""
    recommendations = {
        RiskLevel.LOW: "Safe to proceed",
        RiskLevel.MEDIUM: "Proceed with caution",
        RiskLevel.HIGH: "Requires review",
        RiskLevel.CRITICAL: "Requires human approval"
    }
    return recommendations.get(risk_level, "Evaluate carefully")


def _get_execution_reason(should_execute, task_type, risk_level):
    """Get reason for execution decision"""
    if should_execute:
        return f"AI autonomy level sufficient for {risk_level} risk {task_type} tasks"
    else:
        return f"Insufficient autonomy level or task requires human oversight"


# Payment and Subscription Models
class CheckoutRequest(BaseModel):
    email: str = Field(..., description="Customer email address")
    tier: str = Field(default="pro", description="Subscription tier (pro, enterprise)")

class SubscriptionStatusResponse(BaseModel):
    subscription_id: Optional[str] = None
    status: str
    tier: str
    current_period_end: Optional[int] = None
    cancel_at_period_end: bool = False


# Payment and Subscription Endpoints
@app.post("/payment/checkout", response_model=Dict[str, Any])
async def create_checkout_session(checkout_request: CheckoutRequest):
    """
    Create Stripe checkout session for subscription
    
    - **email**: Customer email address
    - **tier**: Subscription tier (pro, enterprise)
    
    Returns checkout session URL
    """
    try:
        # Validate email format
        if not _valid_email(checkout_request.email):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid email address format"
            )
        
        # Normalize email
        email = checkout_request.email.strip().lower()
        
        # Validate tier
        tier = checkout_request.tier.lower().strip()
        if tier not in ['pro', 'enterprise']:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid tier: {tier}. Valid tiers are: pro, enterprise"
            )
        from api.stripe_service import stripe_service, STRIPE_AVAILABLE, PRICING_TIERS
        
        # Import stripe and check availability
        try:
            import stripe
        except ImportError:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Stripe module not installed. Railway is deploying the update. Please wait a few minutes and try again."
            )
        
        # Check if Stripe API key is configured - try multiple ways
        stripe_key = os.getenv("STRIPE_SECRET_KEY", "") or os.getenv("STRIPE_KEY", "")
        
        if not stripe_key:
            # Log all environment variables that start with STRIPE for debugging
            stripe_vars = {k: "***" + v[-4:] if len(v) > 4 else "***" for k, v in os.environ.items() if "STRIPE" in k.upper()}
            logger.warning(f"Stripe key not found. Available Stripe env vars: {list(stripe_vars.keys())}")
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Stripe API key not configured. Please add STRIPE_SECRET_KEY to Railway environment variables and redeploy."
            )
        
        # Set the API key
        stripe.api_key = stripe_key
        logger.info(f"Stripe API key configured (length: {len(stripe_key)})")
        
        logger.info(f"Creating checkout for tier: {tier}, email: {email}")
        
        # Check if price ID is configured for this tier
        tier_info = PRICING_TIERS.get(tier)
        if not tier_info:
            logger.warning(f"Invalid tier requested: {tier}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid tier: {tier}. Valid tiers are: pro, enterprise"
            )
        
        if not tier_info.get("price_id"):
            # Try to create price dynamically if not configured
            try:
                # Create product and price on the fly
                product = stripe.Product.create(
                    name=f"{tier_info['name']} Plan",
                    description=f"{tier_info['requests_per_month']:,} requests/month"
                )
                
                price = stripe.Price.create(
                    product=product.id,
                    unit_amount=tier_info["amount"],
                    currency="usd",
                    recurring={"interval": "month"}
                )
                
                # Update the price ID
                tier_info["price_id"] = price.id
                logger.info(f"Created Stripe product and price for {tier}: {price.id}")
            except Exception as create_error:
                logger.error(f"Error creating Stripe product/price: {create_error}")
                raise HTTPException(
                    status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                    detail=f"Payment setup incomplete for {tier} tier. Please contact support."
                )
        
        session = stripe_service.create_checkout_session(
            customer_email=email,
            tier=tier
        )
        
        return {
            "checkout_url": session["url"],
            "session_id": session["session_id"],
            "tier": session["tier"]
        }
    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        error_msg = str(e)
        logger.error(f"Error creating checkout session: {e}", exc_info=True)
        
        # Provide more helpful error messages
        if "Price ID not configured" in error_msg:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail=f"Payment setup incomplete. The {tier} tier is being configured. Please try again in a moment."
            )
        elif "Stripe API key" in error_msg or "not configured" in error_msg:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Payment processing is not yet configured. Please contact support."
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error creating checkout session: {error_msg}"
            )


# Payment success page HTML
PAYMENT_SUCCESS_HTML = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Payment Successful - AI Decision Engine API</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); min-height: 100vh; display: flex; align-items: center; justify-content: center; padding: 20px; }
        .success-card { background: white; border-radius: 20px; padding: 40px; max-width: 700px; box-shadow: 0 20px 60px rgba(0,0,0,0.3); text-align: center; }
        .success-icon { font-size: 80px; margin-bottom: 20px; animation: scaleIn 0.5s ease; }
        @keyframes scaleIn { from { transform: scale(0); } to { transform: scale(1); } }
        h1 { color: #4caf50; font-size: 2.5rem; margin-bottom: 10px; }
        .subtitle { color: #666; font-size: 1.1rem; margin-bottom: 30px; }
        .api-key-box { background: #f8f9fa; border: 2px solid #667eea; border-radius: 10px; padding: 25px; margin: 25px 0; position: relative; }
        .api-key { font-size: 1.2rem; color: #333; font-weight: bold; font-family: 'Courier New', monospace; word-break: break-all; margin-bottom: 15px; }
        .copy-button { background: #667eea; color: white; border: none; padding: 12px 24px; border-radius: 8px; cursor: pointer; font-weight: bold; font-size: 1rem; transition: all 0.3s; width: 100%; }
        .copy-button:hover { background: #5568d3; transform: translateY(-2px); box-shadow: 0 5px 15px rgba(102, 126, 234, 0.4); }
        .copy-button.copied { background: #4caf50; }
        .info-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 20px; margin: 25px 0; text-align: left; }
        .info-item { background: #f8f9fa; padding: 15px; border-radius: 8px; }
        .info-item strong { display: block; color: #667eea; margin-bottom: 5px; font-size: 0.9rem; }
        .info-item span { color: #333; font-size: 1.1rem; font-weight: 600; }
        .cta-buttons { display: flex; gap: 15px; margin-top: 30px; flex-wrap: wrap; justify-content: center; }
        .cta-button { display: inline-block; background: #667eea; color: white; padding: 15px 30px; border-radius: 10px; text-decoration: none; font-weight: bold; transition: all 0.3s; }
        .cta-button:hover { background: #5568d3; transform: translateY(-2px); box-shadow: 0 5px 15px rgba(102, 126, 234, 0.4); }
        .cta-button.secondary { background: transparent; border: 2px solid #667eea; color: #667eea; }
        .cta-button.secondary:hover { background: #667eea; color: white; }
        .warning { background: #fff3cd; border: 1px solid #ffc107; border-radius: 8px; padding: 15px; margin-top: 20px; color: #856404; font-size: 0.9rem; }
        .loading { color: #667eea; }
        @media (max-width: 600px) {
            .info-grid { grid-template-columns: 1fr; }
            .cta-buttons { flex-direction: column; }
            .cta-button { width: 100%; }
        }
    </style>
</head>
<body>
    <div class="success-card">
        <div class="success-icon">✅</div>
        <h1>Payment Successful!</h1>
        <p class="subtitle">Your subscription is now active. Welcome aboard! 🚀</p>
        
        <div class="api-key-box">
            <div style="text-align: left; margin-bottom: 10px; color: #666; font-size: 0.9rem;">
                <strong>Your API Key:</strong>
            </div>
            <div class="api-key" id="apiKey">Loading your API key...</div>
            <button class="copy-button" id="copyBtn" onclick="copyApiKey()">Copy API Key</button>
        </div>
        
        <div class="info-grid">
            <div class="info-item">
                <strong>Subscription Tier</strong>
                <span id="tier">-</span>
            </div>
            <div class="info-item">
                <strong>Monthly Requests</strong>
                <span id="requests">-</span>
            </div>
        </div>
        
        <div class="cta-buttons">
            <a href="/docs" class="cta-button">📚 View API Docs</a>
            <a href="/pricing" class="cta-button secondary">💳 Manage Subscription</a>
        </div>
        
        <div class="warning">
            ⚠️ <strong>Important:</strong> Save this API key securely. You will not be able to see it again after leaving this page.
        </div>
    </div>
    <script>
        // Get API key from URL or response
        const urlParams = new URLSearchParams(window.location.search);
        const sessionId = urlParams.get('session_id');
        
        if (sessionId) {
            fetch(`/payment/success?session_id=${sessionId}`)
                .then(r => r.json())
                .then(data => {
                    if (data.api_key) {
                        document.getElementById('apiKey').textContent = data.api_key;
                        document.getElementById('tier').textContent = data.tier.toUpperCase();
                        document.getElementById('requests').textContent = data.requests_per_month.toLocaleString();
                    } else {
                        document.getElementById('apiKey').textContent = 'Error loading API key. Please contact support.';
                        document.getElementById('apiKey').classList.add('loading');
                    }
                })
                .catch(error => {
                    console.error('Error:', error);
                    document.getElementById('apiKey').textContent = 'Error loading API key. Please contact support.';
                });
        } else {
            document.getElementById('apiKey').textContent = 'No session ID found. Please check your email for your API key.';
        }
        
        function copyApiKey() {
            const key = document.getElementById('apiKey').textContent;
            const copyBtn = document.getElementById('copyBtn');
            
            if (key && key !== 'Loading your API key...' && !key.includes('Error')) {
                navigator.clipboard.writeText(key).then(() => {
                    const originalText = copyBtn.textContent;
                    copyBtn.textContent = '✓ Copied!';
                    copyBtn.classList.add('copied');
                    setTimeout(() => {
                        copyBtn.textContent = originalText;
                        copyBtn.classList.remove('copied');
                    }, 2000);
                }).catch(err => {
                    alert('Failed to copy. Please select and copy manually.');
                });
            } else {
                alert('API key not available yet. Please wait...');
            }
        }
    </script>
</body>
</html>"""


@app.get("/payment/success")
async def payment_success(request: Request, session_id: Optional[str] = None):
    """
    Payment success page - called after successful Stripe checkout
    """
    # Check if browser request
    accept_header = request.headers.get("accept", "")
    
    if not session_id:
        if "text/html" in accept_header.lower():
            return HTMLResponse(content=PAYMENT_SUCCESS_HTML.replace("LOADING...", "No session ID provided. Check your email for your API key."))
        return {"message": "Payment successful! Check your email for API key."}
    
    try:
        from api.stripe_service import stripe_service, PRICING_TIERS
        from api.api_key_manager import api_key_manager
        import stripe
        
        # Set Stripe API key if not already set
        stripe_key = os.getenv("STRIPE_SECRET_KEY", "") or os.getenv("STRIPE_KEY", "")
        if stripe_key:
            stripe.api_key = stripe_key
        
        logger.info(f"Processing payment success for session: {session_id}")
        
        # Retrieve checkout session
        session = stripe.checkout.Session.retrieve(session_id)
        logger.info(f"Retrieved session: mode={session.mode}, subscription={session.subscription}, payment_status={session.payment_status}")
        
        # Get tier from session metadata (fallback to "pro")
        tier = session.metadata.get("tier", "pro") if session.metadata else "pro"
        customer_email = session.customer_email or session.metadata.get("customer_email", "") if session.metadata else ""
        
        # Never issue a key for an unpaid session
        if getattr(session, "payment_status", None) != "paid" or not getattr(session, "subscription", None):
            raise HTTPException(
                status_code=status.HTTP_402_PAYMENT_REQUIRED,
                detail="Payment has not been completed for this session.",
            )
        subscription_id = session.subscription

        if stripe_service.get_api_key_hash_from_subscription(subscription_id):
            # Keys are stored hashed, so a key can only be shown once, right after purchase.
            note = "An API key was already issued for this subscription. Contact support if you lost it."
            if "text/html" in accept_header.lower():
                return HTMLResponse(content=PAYMENT_SUCCESS_HTML.replace("Loading your API key...", html.escape(note)))
            return {"message": note, "tier": tier, "subscription_id": subscription_id}

        logger.info(f"Generating new API key for tier: {tier}")
        api_key = api_key_manager.generate_api_key(tier=tier, prefix=f"{tier}_sub")
        stripe_service.link_subscription_to_api_key(
            api_key=api_key,
            subscription_id=subscription_id,
            customer_email=customer_email,
            tier=tier,
        )

        # Return HTML for browsers, JSON for API clients
        if "text/html" in accept_header.lower():
            page = PAYMENT_SUCCESS_HTML.replace("Loading your API key...", html.escape(api_key))
            page = page.replace('id="tier">-</span>', f'id="tier">{html.escape(tier.upper())}</span>')
            page = page.replace('id="requests">-</span>', f'id="requests">{PRICING_TIERS.get(tier, {}).get("requests_per_month", 0):,}</span>')
            return HTMLResponse(content=page)

        return {
            "message": "Payment successful! Save this key now, it cannot be shown again.",
            "api_key": api_key,
            "tier": tier,
            "requests_per_month": PRICING_TIERS.get(tier, {}).get("requests_per_month", 0),
            "subscription_id": subscription_id,
        }
    except HTTPException:
        raise
    except stripe.StripeError as e:
        logger.error(f"Stripe error processing payment success: {e}", exc_info=True)
        if "text/html" in accept_header.lower():
            return HTMLResponse(content=PAYMENT_SUCCESS_HTML.replace("Loading your API key...", "A payment provider error occurred. Please contact support with session ID: " + html.escape(str(session_id))))
        return {"error": "Payment provider error", "session_id": session_id}
    except Exception as e:
        logger.error(f"Error processing payment success: {e}", exc_info=True)
        if "text/html" in accept_header.lower():
            return HTMLResponse(content=PAYMENT_SUCCESS_HTML.replace("Loading your API key...", "Something went wrong. Please contact support with session ID: " + html.escape(str(session_id))))
        return {"error": "Internal error", "session_id": session_id}


@app.get("/payment/cancel")
async def payment_cancel():
    """Payment cancellation page"""
    return {"message": "Payment cancelled. You can try again anytime."}


@app.post("/webhooks/stripe", response_model=Dict[str, Any])
async def stripe_webhook(request: Request):
    """
    Handle Stripe webhook events
    
    Processes subscription updates, cancellations, etc.
    """
    try:
        from api.stripe_service import stripe_service
        from api.api_key_manager import api_key_manager
        
        payload = await request.body()
        signature = request.headers.get("stripe-signature")
        
        if not signature:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Missing stripe-signature header"
            )
        
        # Verify webhook
        event = stripe_service.verify_webhook(payload, signature)
        
        if not event:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid webhook signature"
            )
        
        # Handle different event types
        event_type = event["type"]
        event_data = event["data"]["object"]
        
        if event_type == "checkout.session.completed":
            # Subscription created
            subscription_id = event_data.get("subscription")
            if subscription_id:
                subscription = stripe_service.get_subscription(subscription_id)
                if subscription:
                    tier = subscription.get("tier", "pro")
                    # Update subscription status
                    stripe_service.update_subscription_status(subscription_id, "active")
                    logger.info(f"Subscription activated: {subscription_id}")
        
        elif event_type == "customer.subscription.updated":
            # Subscription updated
            subscription_id = event_data.get("id")
            subscription_status = event_data.get("status")
            stripe_service.update_subscription_status(subscription_id, subscription_status)
            logger.info(f"Subscription updated: {subscription_id}, status: {subscription_status}")
        
        elif event_type == "customer.subscription.deleted":
            # Subscription cancelled
            subscription_id = event_data.get("id")
            stripe_service.update_subscription_status(subscription_id, "cancelled")
            
            # Optionally downgrade API key to free tier
            digest = stripe_service.get_api_key_hash_from_subscription(subscription_id)
            if digest and api_key_manager.set_tier_by_digest(digest, "free"):
                logger.info(f"Downgraded the API key for subscription {subscription_id} to free tier")

        return {"status": "success", "event": event_type}
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error processing webhook: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error processing webhook"
        )


@app.get("/subscription/status", response_model=SubscriptionStatusResponse)
async def get_subscription_status(
    x_api_key: Optional[str] = Header(None, alias="X-API-Key")
):
    """
    Get subscription status for current API key
    """
    try:
        from api.stripe_service import stripe_service
        
        if not x_api_key:
            return SubscriptionStatusResponse(
                status="free",
                tier="free"
            )
        
        # Find subscription for this API key
        subscriptions = stripe_service._load_subscriptions()
        subscription_id = None
        
        for sub_id, sub_data in subscriptions.items():
            if sub_data.get("api_key_hash") == hash_key(x_api_key):
                subscription_id = sub_id
                break
        
        if not subscription_id:
            # Check tier from API key manager
            from api.api_key_manager import api_key_manager
            key_info = api_key_manager.validate_api_key(x_api_key)
            tier = key_info.get("tier", "free") if key_info else "free"
            
            return SubscriptionStatusResponse(
                status="free",
                tier=tier
            )
        
        subscription = stripe_service.get_subscription(subscription_id)
        if subscription:
            return SubscriptionStatusResponse(
                subscription_id=subscription["id"],
                status=subscription["status"],
                tier=subscription["tier"],
                current_period_end=subscription.get("current_period_end"),
                cancel_at_period_end=subscription.get("cancel_at_period_end", False)
            )
        
        # Fallback to API key tier
        from api.api_key_manager import api_key_manager
        key_info = api_key_manager.validate_api_key(x_api_key)
        tier = key_info.get("tier", "free") if key_info else "free"
        
        return SubscriptionStatusResponse(
            status="unknown",
            tier=tier
        )
    
    except Exception as e:
        logger.error(f"Error getting subscription status: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error getting subscription status"
        )


# Pricing page HTML (embedded)
PRICING_PAGE_HTML = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Pricing - AI Decision Engine API</title>
    <script>
        // Define API base URL immediately
        const API_BASE_URL = window.location.origin;
        
        // Ensure functions are available immediately
        (function() {
            'use strict';
            
            // Subscribe function - handles Pro and Enterprise subscriptions
            window.subscribe = async function subscribe(tier, buttonElement) {
                console.log('[Subscribe] Function called with tier:', tier);
                
                // Get button reference
                const clickedButton = buttonElement || document.querySelector('button[data-tier="' + tier + '"]');
                const originalText = clickedButton ? clickedButton.textContent : 'Subscribe Now';
                
                // Validate tier
                if (!tier || (tier !== 'pro' && tier !== 'enterprise')) {
                    alert('Invalid subscription tier. Please select Pro or Enterprise.');
                    return;
                }
                
                try {
                    // Get email from user
                    const email = prompt('Enter your email address:');
                    if (!email) {
                        return; // User cancelled
                    }
                    
                    // Validate email
                    if (!email.includes('@') || email.length < 5) {
                        alert('Please enter a valid email address');
                        return;
                    }
                    
                    // Update button state
                    if (clickedButton) {
                        clickedButton.textContent = 'Processing...';
                        clickedButton.disabled = true;
                        clickedButton.style.opacity = '0.6';
                    }
                    
                    console.log('[Subscribe] Creating checkout session for tier:', tier, 'email:', email);
                    
                    // Make API call to create checkout session
                    const checkoutUrl = API_BASE_URL + '/payment/checkout';
                    const controller = new AbortController();
                    const timeoutId = setTimeout(() => controller.abort(), 30000); // 30 second timeout
                    
                    try {
                        const response = await fetch(checkoutUrl, {
                            method: 'POST',
                            headers: {
                                'Content-Type': 'application/json',
                                'Accept': 'application/json'
                            },
                            body: JSON.stringify({
                                email: email.trim(),
                                tier: tier.toLowerCase()
                            }),
                            signal: controller.signal
                        });
                        
                        clearTimeout(timeoutId);
                        
                        console.log('[Subscribe] Response status:', response.status, response.statusText);
                        
                        // Parse response
                        let data;
                        const contentType = response.headers.get('content-type') || '';
                        
                        if (contentType.includes('application/json')) {
                            data = await response.json();
                            console.log('[Subscribe] Response data:', data);
                        } else {
                            const text = await response.text();
                            console.error('[Subscribe] Non-JSON response:', text);
                            throw new Error('Server returned invalid response format');
                        }
                        
                        // Handle response
                        if (response.ok && data.checkout_url) {
                            console.log('[Subscribe] Redirecting to Stripe checkout:', data.checkout_url);
                            // Redirect to Stripe checkout
                            window.location.href = data.checkout_url;
                        } else {
                            // Handle error response
                            const errorMsg = data.detail || data.message || 'Error creating checkout session. Please try again.';
                            console.error('[Subscribe] Checkout error:', errorMsg);
                            alert('Error: ' + errorMsg + '\\n\\nIf this persists, please contact support.');
                            
                            // Reset button
                            if (clickedButton) {
                                clickedButton.textContent = originalText;
                                clickedButton.disabled = false;
                                clickedButton.style.opacity = '1';
                            }
                        }
                    } catch (fetchError) {
                        clearTimeout(timeoutId);
                        console.error('[Subscribe] Fetch error:', fetchError);
                        
                        if (fetchError.name === 'AbortError') {
                            throw new Error('Request timed out. Please check your connection and try again.');
                        } else if (fetchError.message) {
                            throw fetchError;
                        } else {
                            throw new Error('Network error. Please check your connection and try again.');
                        }
                    }
                } catch (error) {
                    console.error('[Subscribe] Error in subscribe function:', error);
                    const errorMsg = error.message || 'Unknown error occurred';
                    alert('Error: ' + errorMsg + '\\n\\nPlease check your connection and try again.\\n\\nIf this persists, please contact support.');
                    
                    // Reset button
                    const resetButton = buttonElement || document.querySelector('button[data-tier="' + tier + '"]');
                    if (resetButton) {
                        resetButton.textContent = originalText;
                        resetButton.disabled = false;
                        resetButton.style.opacity = '1';
                    }
                }
            };
        
            // Get free API key function
            window.getFreeKey = async function getFreeKey() {
                console.log('[FreeKey] Function called');
                
                try {
                    // Get email from user
                    const email = prompt('Enter your email address to get a free API key:');
                    if (!email) {
                        return; // User cancelled
                    }
                    
                    // Validate email
                    if (!email.includes('@') || email.length < 5) {
                        alert('Please enter a valid email address');
                        return;
                    }
                    
                    console.log('[FreeKey] Requesting free API key for email:', email);
                    
                    // Make API call
                    const freeKeyUrl = API_BASE_URL + '/api/keys/free';
                    const controller = new AbortController();
                    const timeoutId = setTimeout(() => controller.abort(), 30000); // 30 second timeout
                    
                    try {
                        const response = await fetch(freeKeyUrl, {
                            method: 'POST',
                            headers: {
                                'Content-Type': 'application/json',
                                'Accept': 'application/json'
                            },
                            body: JSON.stringify({
                                email: email.trim()
                            }),
                            signal: controller.signal
                        });
                        
                        clearTimeout(timeoutId);
                        
                        console.log('[FreeKey] Response status:', response.status, response.statusText);
                        
                        // Parse response
                        let data;
                        const contentType = response.headers.get('content-type') || '';
                        
                        if (contentType.includes('application/json')) {
                            data = await response.json();
                            console.log('[FreeKey] Response data:', data);
                        } else {
                            const text = await response.text();
                            console.error('[FreeKey] Non-JSON response:', text);
                            throw new Error('Server returned invalid response format');
                        }
                        
                        // Handle response
                        if (response.ok && data.api_key) {
                            const message = 'Your Free API Key:\\n\\n' + 
                                          data.api_key + 
                                          '\\n\\nRequests: ' + 
                                          (data.requests_per_month || 100) + 
                                          '/month\\n\\nCopy this key - you will not see it again!';
                            
                            // Show API key
                            alert(message);
                            
                            // Ask if user wants to open documentation
                            if (confirm('Would you like to open the API documentation?')) {
                                window.open(API_BASE_URL + '/docs', '_blank');
                            }
                        } else {
                            // Handle error response
                            const errorMsg = data.detail || data.message || 'Error generating API key. Please try again.';
                            console.error('[FreeKey] Error:', errorMsg);
                            alert('Error: ' + errorMsg);
                        }
                    } catch (fetchError) {
                        clearTimeout(timeoutId);
                        console.error('[FreeKey] Fetch error:', fetchError);
                        
                        if (fetchError.name === 'AbortError') {
                            throw new Error('Request timed out. Please check your connection and try again.');
                        } else if (fetchError.message) {
                            throw fetchError;
                        } else {
                            throw new Error('Network error. Please check your connection and try again.');
                        }
                    }
                } catch (error) {
                    console.error('[FreeKey] Error in getFreeKey function:', error);
                    const errorMsg = error.message || 'Unknown error occurred';
                    alert('Error generating API key: ' + errorMsg + '\\n\\nPlease visit the documentation to get started: ' + API_BASE_URL + '/docs');
                    
                    // Offer to open docs
                    if (confirm('Would you like to open the API documentation?')) {
                        window.open(API_BASE_URL + '/docs', '_blank');
                    }
                }
            };
        })();
        
        // Function to show API key in a copyable modal
        function showApiKeyModal(apiKey, tier, requestsPerMonth) {
            // Create modal overlay
            const overlay = document.createElement('div');
            overlay.style.cssText = 'position: fixed; top: 0; left: 0; width: 100%; height: 100%; background: rgba(0,0,0,0.7); z-index: 10000; display: flex; align-items: center; justify-content: center;';
            
            // Create modal content
            const modal = document.createElement('div');
            modal.style.cssText = 'background: white; border-radius: 15px; padding: 30px; max-width: 500px; width: 90%; box-shadow: 0 20px 60px rgba(0,0,0,0.5); position: relative;';
            
            // Create close button
            const closeBtn = document.createElement('button');
            closeBtn.textContent = '×';
            closeBtn.style.cssText = 'position: absolute; top: 10px; right: 15px; background: none; border: none; font-size: 30px; cursor: pointer; color: #666; line-height: 1;';
            closeBtn.onclick = () => document.body.removeChild(overlay);
            
            // Create title
            const title = document.createElement('h2');
            title.textContent = '🎉 Your Free API Key';
            title.style.cssText = 'margin: 0 0 20px 0; color: #667eea; font-size: 1.5rem;';
            
            // Create warning
            const warning = document.createElement('p');
            warning.textContent = '⚠️ Copy this key now - you will not see it again!';
            warning.style.cssText = 'color: #e74c3c; font-weight: bold; margin: 0 0 15px 0; font-size: 0.9rem;';
            
            // Create API key container
            const keyContainer = document.createElement('div');
            keyContainer.style.cssText = 'background: #f5f5f5; border: 2px solid #667eea; border-radius: 8px; padding: 15px; margin: 15px 0; position: relative;';
            
            // Create API key text
            const keyText = document.createElement('div');
            keyText.textContent = apiKey;
            keyText.style.cssText = 'font-family: monospace; font-size: 0.9rem; word-break: break-all; color: #333; margin-bottom: 10px; user-select: all;';
            keyText.id = 'api-key-text';
            
            // Create copy button
            const copyBtn = document.createElement('button');
            copyBtn.textContent = '📋 Copy API Key';
            copyBtn.style.cssText = 'width: 100%; padding: 12px; background: #667eea; color: white; border: none; border-radius: 8px; font-size: 1rem; font-weight: bold; cursor: pointer; margin-top: 10px; transition: background 0.3s;';
            copyBtn.onmouseover = () => copyBtn.style.background = '#5568d3';
            copyBtn.onmouseout = () => copyBtn.style.background = '#667eea';
            
            copyBtn.onclick = function() {
                // Select the API key text
                const range = document.createRange();
                range.selectNode(keyText);
                window.getSelection().removeAllRanges();
                window.getSelection().addRange(range);
                
                try {
                    // Copy to clipboard
                    document.execCommand('copy');
                    window.getSelection().removeAllRanges();
                    
                    // Update button text
                    const originalText = copyBtn.textContent;
                    copyBtn.textContent = '✓ Copied!';
                    copyBtn.style.background = '#27ae60';
                    
                    // Also try modern clipboard API
                    navigator.clipboard.writeText(apiKey).then(() => {
                        console.log('API key copied to clipboard');
                    }).catch(() => {
                        console.log('Fallback copy method used');
                    });
                    
                    // Reset button after 2 seconds
                    setTimeout(() => {
                        copyBtn.textContent = originalText;
                        copyBtn.style.background = '#667eea';
                    }, 2000);
                } catch (err) {
                    // Fallback: show alert with key
                    alert('Please manually copy: ' + apiKey);
                }
            };
            
            // Create info section
            const info = document.createElement('div');
            info.style.cssText = 'margin-top: 15px; padding-top: 15px; border-top: 1px solid #eee; color: #666; font-size: 0.9rem;';
            info.innerHTML = '<strong>Tier:</strong> ' + tier.charAt(0).toUpperCase() + tier.slice(1) + '<br>' +
                           '<strong>Requests:</strong> ' + requestsPerMonth.toLocaleString() + '/month';
            
            // Create documentation button
            const docsBtn = document.createElement('button');
            docsBtn.textContent = '📚 Open API Documentation';
            docsBtn.style.cssText = 'width: 100%; padding: 12px; background: #764ba2; color: white; border: none; border-radius: 8px; font-size: 1rem; font-weight: bold; cursor: pointer; margin-top: 15px; transition: background 0.3s;';
            docsBtn.onmouseover = () => docsBtn.style.background = '#5a3a7a';
            docsBtn.onmouseout = () => docsBtn.style.background = '#764ba2';
            docsBtn.onclick = () => {
                window.open(API_BASE_URL + '/docs', '_blank');
            };
            
            // Assemble modal
            keyContainer.appendChild(keyText);
            keyContainer.appendChild(copyBtn);
            modal.appendChild(closeBtn);
            modal.appendChild(title);
            modal.appendChild(warning);
            modal.appendChild(keyContainer);
            modal.appendChild(info);
            modal.appendChild(docsBtn);
            overlay.appendChild(modal);
            
            // Add to page
            document.body.appendChild(overlay);
            
            // Close on overlay click (but not on modal click)
            overlay.onclick = (e) => {
                if (e.target === overlay) {
                    document.body.removeChild(overlay);
                }
            };
            
            // Close on Escape key
            const escapeHandler = (e) => {
                if (e.key === 'Escape') {
                    document.body.removeChild(overlay);
                    document.removeEventListener('keydown', escapeHandler);
                }
            };
            document.addEventListener('keydown', escapeHandler);
        }
        
        // Log that functions are loaded
        console.log('[Pricing] Subscription functions loaded successfully');
        console.log('[Pricing] subscribe function available:', typeof window.subscribe);
        console.log('[Pricing] getFreeKey function available:', typeof window.getFreeKey);
        
        // Add event listeners when DOM is ready
        if (document.readyState === 'loading') {
            document.addEventListener('DOMContentLoaded', attachEventListeners);
        } else {
            // DOM already loaded
            attachEventListeners();
        }
        
        function attachEventListeners() {
            console.log('[Pricing] Attaching event listeners');
            
            // Attach to free key button
            const freeButton = document.querySelector('button[data-action="free"]');
            if (freeButton) {
                // Remove existing onclick and use event listener
                freeButton.removeAttribute('onclick');
                freeButton.addEventListener('click', function(e) {
                    e.preventDefault();
                    e.stopPropagation();
                    console.log('[Pricing] Free button clicked');
                    if (window.getFreeKey) {
                        window.getFreeKey();
                    } else {
                        alert('Error: Function not loaded. Please refresh the page.');
                    }
                });
                console.log('[Pricing] Free button listener attached');
            } else {
                console.warn('[Pricing] Free button not found');
            }
            
            // Attach to subscribe buttons
            const subscribeButtons = document.querySelectorAll('button[data-action="subscribe"]');
            subscribeButtons.forEach(function(button) {
                // Remove existing onclick and use event listener
                button.removeAttribute('onclick');
                button.addEventListener('click', function(e) {
                    e.preventDefault();
                    e.stopPropagation();
                    const tier = button.getAttribute('data-tier');
                    console.log('[Pricing] Subscribe button clicked, tier:', tier);
                    if (tier && window.subscribe) {
                        window.subscribe(tier, button);
                    } else {
                        alert('Error: Function not loaded. Please refresh the page.');
                    }
                });
            });
            console.log('[Pricing] Subscribe button listeners attached:', subscribeButtons.length);
        }
    </script>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); min-height: 100vh; padding: 40px 20px; }
        .container { max-width: 1200px; margin: 0 auto; }
        h1 { text-align: center; color: white; font-size: 2.5rem; margin-bottom: 10px; }
        .subtitle { text-align: center; color: rgba(255, 255, 255, 0.9); font-size: 1.2rem; margin-bottom: 50px; }
        .pricing-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 30px; margin-top: 40px; }
        .pricing-card { background: white; border-radius: 20px; padding: 40px; box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3); transition: transform 0.3s ease, box-shadow 0.3s ease; position: relative; overflow: hidden; }
        .pricing-card:hover { transform: translateY(-10px); box-shadow: 0 30px 80px rgba(0, 0, 0, 0.4); }
        .pricing-card.featured { border: 3px solid #667eea; transform: scale(1.05); }
        .pricing-card.featured::before { content: "POPULAR"; position: absolute; top: 20px; right: -30px; background: #667eea; color: white; padding: 5px 40px; transform: rotate(45deg); font-size: 0.8rem; font-weight: bold; }
        .tier-name { font-size: 1.8rem; font-weight: bold; color: #333; margin-bottom: 10px; }
        .price { font-size: 3rem; font-weight: bold; color: #667eea; margin: 20px 0; }
        .price .currency { font-size: 1.5rem; vertical-align: top; }
        .price .period { font-size: 1rem; color: #666; font-weight: normal; }
        .features { list-style: none; margin: 30px 0; }
        .features li { padding: 12px 0; border-bottom: 1px solid #eee; color: #555; }
        .features li:last-child { border-bottom: none; }
        .features li::before { content: "✓ "; color: #667eea; font-weight: bold; margin-right: 10px; }
        .cta-button { width: 100%; padding: 15px; background: #667eea; color: white; border: none; border-radius: 10px; font-size: 1.1rem; font-weight: bold; cursor: pointer; transition: background 0.3s ease; margin-top: 20px; }
        .cta-button:hover { background: #5568d3; }
        .cta-button.secondary { background: #764ba2; }
        .cta-button.secondary:hover { background: #5a3a7a; }
        @media (max-width: 768px) { .pricing-card.featured { transform: scale(1); } h1 { font-size: 2rem; } }
    </style>
</head>
<body>
    <div class="container">
        <h1>Choose Your Plan</h1>
        <p class="subtitle">Start free, upgrade when you need more</p>
        <div class="pricing-grid">
            <div class="pricing-card">
                <div class="tier-name">Free</div>
                <div class="price"><span class="currency">$</span>0<span class="period">/month</span></div>
                <ul class="features">
                    <li>100 requests/month included</li>
                    <li>Full API access</li>
                    <li>Community support</li>
                    <li>All endpoints included</li>
                    <li style="color: #999; font-size: 0.9rem;">Hard limit (no overage)</li>
                </ul>
                <button class="cta-button" data-action="free" onclick="getFreeKey(); return false;">Get Free API Key</button>
            </div>
            <div class="pricing-card featured">
                <div class="tier-name">Pro</div>
                <div class="price"><span class="currency">$</span>9<span class="period">/month</span></div>
                <ul class="features">
                    <li>10,000 requests/month included</li>
                    <li>Full API access</li>
                    <li>Priority support</li>
                    <li>All endpoints included</li>
                    <li>Advanced analytics</li>
                    <li style="color: #667eea; font-weight: bold;">$1 per 1,000 overage</li>
                </ul>
                <button class="cta-button" data-tier="pro" data-action="subscribe" onclick="subscribe('pro', this); return false;">Subscribe Now</button>
            </div>
            <div class="pricing-card">
                <div class="tier-name">Enterprise</div>
                <div class="price"><span class="currency">$</span>49<span class="period">/month</span></div>
                <ul class="features">
                    <li>1,000,000 requests/month included</li>
                    <li>Full API access</li>
                    <li>Priority support</li>
                    <li>All endpoints included</li>
                    <li>Advanced analytics</li>
                    <li>Custom integrations</li>
                    <li style="color: #667eea; font-weight: bold;">$0.50 per 1,000 overage</li>
                </ul>
                <button class="cta-button secondary" data-tier="enterprise" data-action="subscribe" onclick="subscribe('enterprise', this); return false;">Subscribe Now</button>
            </div>
        </div>
    </div>
</body>
</html>"""


@app.get("/pricing", response_class=HTMLResponse)
async def get_pricing(request: Request):
    """
    Get pricing information - serves HTML for browsers, JSON for API clients
    """
    # Check if request is from a browser or API client
    accept_header = request.headers.get("accept", "").lower()
    user_agent = request.headers.get("user-agent", "").lower()
    
    # Return JSON only if explicitly requested with Accept: application/json
    # Otherwise, default to HTML (for browsers)
    if "application/json" in accept_header and "text/html" not in accept_header:
        # Return JSON for API clients
        try:
            # Try to import from stripe_service, but fallback to hardcoded pricing if not available
            try:
                from api.stripe_service import PRICING_TIERS
                pricing_tiers = PRICING_TIERS
            except (ImportError, ModuleNotFoundError):
                # Fallback pricing if Stripe not installed yet
                pricing_tiers = {
                    "free": {
                        "name": "Free",
                        "amount": 0,
                        "requests_per_month": 100
                    },
                    "pro": {
                        "name": "Pro",
                        "amount": 900,  # $9.00 in cents
                        "requests_per_month": 10000
                    },
                    "enterprise": {
                        "name": "Enterprise",
                        "amount": 4900,  # $49.00 in cents
                        "requests_per_month": 1000000
                    }
                }
            
            pricing = {}
            for tier, info in pricing_tiers.items():
                features = [
                    f"{info['requests_per_month']:,} requests/month included",
                    "Full API access",
                    "Priority support" if tier != "free" else "Community support"
                ]
                
                # Add overage info for paid tiers
                if tier != "free" and info.get("overage_per_1000"):
                    overage_text = f"${info['overage_per_1000']/100:.2f} per 1,000 overage"
                    features.append(overage_text)
                elif tier == "free":
                    features.append("Hard limit (no overage)")
                
                pricing[tier] = {
                    "name": info["name"],
                    "price": info["amount"] / 100,  # Convert cents to dollars
                    "requests_per_month": info["requests_per_month"],
                    "overage_per_1000": info.get("overage_per_1000", 0) / 100 if info.get("overage_per_1000") else None,
                    "features": features
                }
            
            return JSONResponse(content={
                "tiers": pricing,
                "currency": "USD"
            })
        except Exception as e:
            logger.error(f"Error getting pricing: {e}", exc_info=True)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Error getting pricing"
            )
    
    # Default: Return HTML for browsers
    return HTMLResponse(content=PRICING_PAGE_HTML)


# Free API Key Generation Endpoint
class FreeKeyRequest(BaseModel):
    email: str = Field(..., description="Email address for the free API key")

@app.post("/api/keys/free", response_model=Dict[str, Any])
async def generate_free_api_key(request_body: FreeKeyRequest, http_request: Request):
    """
    Generate a free API key (public endpoint, no auth required)
    
    - **email**: Email address (for tracking purposes)
    
    Returns a free tier API key
    """
    try:
        from api.api_key_manager import api_key_manager
        
        # Validate email format
        if not _valid_email(request_body.email):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid email address format"
            )
        
        if not _free_key_allowed(_client_ip(http_request)):
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Too many key requests from this address. Try again later.",
            )

        # Normalize email
        email = request_body.email.strip().lower()
        
        logger.info(f"Generating free API key for email: {email}")
        
        # Get UTM parameters from request URL (if available)
        utm_source = None
        utm_campaign = None
        try:
            from urllib.parse import urlparse, parse_qs
            parsed_url = urlparse(str(http_request.url))
            query_params = parse_qs(parsed_url.query)
            utm_source = query_params.get("utm_source", [None])[0]
            utm_campaign = query_params.get("utm_campaign", [None])[0]
        except Exception as e:
            logger.debug(f"Could not parse UTM parameters: {e}")
        
        # Generate free tier API key
        api_key = api_key_manager.generate_api_key(tier="free", prefix="free")
        
        key_info = api_key_manager.get_key_info(api_key)
        
        # Track signup in marketing analytics
        try:
            from api.marketing_analytics import marketing_analytics
            marketing_analytics.track_signup(
                api_key=hash_key(api_key),
                utm_source=utm_source,
                utm_campaign=utm_campaign
            )
        except Exception as e:
            logger.error(f"Error tracking signup: {e}")
        
        logger.info(f"Successfully generated free API key for email: {email}, source: {utm_source}")
        
        return {
            "success": True,
            "api_key": api_key,
            "tier": "free",
            "requests_per_month": key_info.get("requests_per_month", 100),
            "message": "Free API key generated successfully!",
            "documentation": "/docs",
            "timestamp": datetime.now().isoformat()
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error generating free API key: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error generating API key"
        )


@app.get("/api/usage", response_model=Dict[str, Any])
async def get_usage(
    request: Request,
    api_info: Dict[str, Any] = Depends(verify_api_key)
):
    """
    Get usage statistics and billing summary for current API key
    
    Returns:
    - Usage statistics (total requests, included, overage)
    - Billing summary (base price, overage charge, total)
    """
    try:
        from api.api_key_manager import api_key_manager
        from api.stripe_service import stripe_service
        
        # Get API key from header
        api_key = request.headers.get("X-API-Key")
        if not api_key:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="API key required"
            )
        
        # Get usage statistics
        usage_stats = api_key_manager.get_usage_stats(api_key)
        
        # Get billing summary
        billing_summary = stripe_service.get_billing_summary(api_key, usage_stats)
        
        return {
            "usage": usage_stats,
            "billing": billing_summary
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting usage: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error getting usage"
        )


# Include analytics routes
from api.analytics_routes import router as analytics_router
app.include_router(analytics_router)

# Include key management routes
from api.key_management_routes import router as key_management_router
app.include_router(key_management_router)


# ==================== User Dashboard Endpoints ====================

@app.get("/api/billing")
async def get_billing(key_info: Dict[str, Any] = Depends(verify_api_key)):
    """
    Get billing summary for the authenticated API key

    Returns:
    - tier: Your subscription tier
    - base_price: Monthly base price
    - included_requests: Requests included in your plan
    - total_requests: Total requests this month
    - overage_requests: Requests beyond your plan
    - overage_charge: Additional charges for overage
    - total_charge: Total monthly charge (base + overage)
    - month: Current billing month

    Requires: X-API-Key header
    """
    try:
        from api.stripe_service import stripe_service

        # Get usage stats
        full_key = key_info.get("_full_key", "")
        usage_stats = api_key_manager.get_usage_stats(full_key)

        # Get billing summary
        billing_summary = stripe_service.get_billing_summary(full_key, usage_stats)

        return {
            "success": True,
            "billing": billing_summary,
            "note": "Overage charges are billed monthly" if billing_summary.get("overage_charge", 0) > 0 else None
        }
    except Exception as e:
        logger.error(f"Error getting billing: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error getting billing information"
        )


@app.get("/api/marketing/stats", response_model=Dict[str, Any])
async def get_marketing_stats(days: int = 30, _admin: bool = Depends(verify_admin)):
    """
    Get marketing analytics and traffic source statistics
    
    Returns:
    - Total visits and signups
    - Traffic by source (Reddit, HN, Twitter, etc.)
    - Conversion rates
    - Daily statistics
    
    Requires the admin key (X-Admin-Key).
    """
    try:
        from api.marketing_analytics import marketing_analytics
        
        stats = marketing_analytics.get_marketing_stats(days=days)
        top_sources = marketing_analytics.get_top_sources(limit=10)
        
        return {
            "success": True,
            "stats": stats,
            "top_sources": top_sources,
            "note": "Marketing analytics for tracking campaign performance"
        }
    except Exception as e:
        logger.error(f"Error getting marketing stats: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error getting marketing statistics"
        )


@app.get("/api/key/info")
async def get_key_info(key_info: Dict[str, Any] = Depends(verify_api_key)):
    """
    Get information about the authenticated API key

    Returns:
    - tier: Subscription tier
    - requests_per_month: Included requests
    - created_at: When the key was created
    - active: Whether the key is active
    - key_preview: First 10 characters of the key

    Requires: X-API-Key header
    """
    try:
        full_key = key_info.get("_full_key", "")
        detailed_info = api_key_manager.get_key_info(full_key)

        if not detailed_info:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="API key not found"
            )

        # Remove sensitive internal fields
        safe_info = {
            "tier": detailed_info.get("tier", "free"),
            "requests_per_month": detailed_info.get("requests_per_month", 100),
            "created_at": detailed_info.get("created_at"),
            "active": detailed_info.get("active", True),
            "key_preview": key_info.get("api_key", "")[:10] + "...",
            "email": detailed_info.get("email", "Not provided")
        }

        return {
            "success": True,
            "key_info": safe_info
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting key info: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error getting key information"
        )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
