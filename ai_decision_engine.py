"""
AI Decision-Making Framework
Autonomous decision engine for AI Decision Engine
"""

from enum import Enum
from datetime import datetime
from typing import Dict, Any, List
import json
from ai_memory_system import AIMemory, MemoryAwareDecisionEngine
from autonomy_tracker import GradualAutonomySystem

class RiskLevel(Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"

class DecisionCategory(Enum):
    STRATEGIC = "STRATEGIC"
    OPERATIONAL = "OPERATIONAL"
    FINANCIAL = "FINANCIAL"
    MARKETING = "MARKETING"
    RND = "RND"
    COMPLIANCE = "COMPLIANCE"

class AIDecisionEngine:
    """Core AI decision-making system"""
    
    def __init__(self):
        self.decision_log = []
        self.memory = AIMemory()  # Integrate memory system
        self.autonomy = GradualAutonomySystem()  # Integrate autonomy tracker
        self.risk_thresholds = {
            RiskLevel.LOW: {"max_amount": 1000, "auto_execute": True},
            RiskLevel.MEDIUM: {"max_amount": 10000, "auto_execute": True, "log_required": True},
            RiskLevel.HIGH: {"max_amount": 50000, "auto_execute": False, "human_approval": True},
            RiskLevel.CRITICAL: {"max_amount": None, "auto_execute": False, "human_review": True}
        }
    
    def evaluate_decision(self, decision_data: Dict[str, Any]) -> Dict[str, Any]:
        """Evaluate a decision and determine risk level"""
        
        # Get memory insights before evaluation
        memory_insights = self.memory.inform_decision(decision_data)
        
        # Use memory to inform risk assessment
        risk_level = self._assess_risk(decision_data, memory_insights)
        
        # Check if AI should make this decision based on autonomy level
        # Use autonomy system to check if AI can decide
        category = decision_data.get("category", DecisionCategory.OPERATIONAL.value).lower()
        should_ai_decide = self.autonomy.should_auto_execute(category, risk_level.value)
        current_autonomy = self.autonomy.get_autonomy_level()
        
        decision = {
            "id": f"DEC_{datetime.now().strftime('%Y%m%d%H%M%S')}",
            "timestamp": datetime.now().isoformat(),
            "category": decision_data.get("category", DecisionCategory.OPERATIONAL.value),
            "risk_level": risk_level.value,  # Already a string from .value
            "description": decision_data.get("description", ""),
            "amount": decision_data.get("amount", 0),
            "data": {k: (v.value if isinstance(v, (RiskLevel, DecisionCategory)) else v) for k, v in decision_data.items()},  # Convert enums to strings
            "status": "PENDING",
            "action_required": self._determine_action(risk_level, should_ai_decide),
            "memory_insights": memory_insights,  # Include memory insights
            "ai_can_decide": should_ai_decide,
            "autonomy_level": current_autonomy
        }
        
        # Record decision in memory
        self.memory.record_decision(decision)
        
        return decision
    
    def _assess_risk(self, decision_data: Dict[str, Any], memory_insights: Dict[str, Any] = None) -> RiskLevel:
        """AI risk assessment (uses memory if available)"""
        amount = decision_data.get("amount", 0)
        
        # Base risk assessment
        if amount <= 1000:
            base_risk = RiskLevel.LOW
        elif amount <= 10000:
            base_risk = RiskLevel.MEDIUM
        elif amount <= 50000:
            base_risk = RiskLevel.HIGH
        else:
            base_risk = RiskLevel.CRITICAL
        
        # Adjust based on memory if available
        if memory_insights:
            # If similar decisions were successful, might reduce risk slightly
            successful_similar = memory_insights.get("success_patterns", {}).get("successful_decisions", [])
            if successful_similar:
                # If we have successful similar decisions, confidence increases
                pass  # Keep base risk for now, can add adjustment logic
        
        return base_risk
    
    def _determine_action(self, risk_level: RiskLevel, should_ai_decide: bool = False) -> str:
        """Determine required action based on risk level and autonomy"""
        thresholds = self.risk_thresholds[risk_level]
        
        # If AI can decide at current autonomy level
        if should_ai_decide:
            if thresholds.get("auto_execute"):
                return "AI_EXECUTE_IMMEDIATELY"
            else:
                return "AI_PROPOSE_HUMAN_REVIEW"
        
        # Standard flow based on risk
        if thresholds.get("auto_execute"):
            return "EXECUTE_IMMEDIATELY"
        elif thresholds.get("human_approval"):
            return "WAIT_HUMAN_APPROVAL"
        elif thresholds.get("human_review"):
            return "WAIT_HUMAN_REVIEW"
        else:
            return "LOG_ONLY"
    
    def execute_decision(self, decision: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a decision"""
        # Check if AI can auto-execute based on autonomy level
        task_type = decision.get("category", "OPERATIONAL").lower()
        risk_level = decision.get("risk_level", "LOW")
        
        can_auto = self.autonomy.should_auto_execute(task_type, risk_level)
        
        if can_auto or decision.get("action_required") == "EXECUTE_IMMEDIATELY":
            decision["status"] = "EXECUTED"
            decision["executed_at"] = datetime.now().isoformat()
            decision["auto_executed"] = True
            self.decision_log.append(decision)
            
            # Record execution in memory
            self.memory.record_event(
                "DECISION_EXECUTION",
                f"Decision {decision['id']} executed autonomously",
                {"decision": decision}
            )
            
            # Record success for autonomy progression
            self.autonomy.record_success("decision")
            
            return decision
        else:
            decision["status"] = "REQUIRES_HUMAN_APPROVAL"
            decision["human_approval_needed"] = True
            return decision
    
    def log_decision(self, decision: Dict[str, Any]):
        """Log decision for tracking"""
        decision["logged_at"] = datetime.now().isoformat()
        self.decision_log.append(decision)
        return decision
    
    def get_decisions(self, limit: int = 100) -> List[Dict[str, Any]]:
        """Get recent decisions"""
        return self.decision_log[-limit:]
    
    def export_log(self, filename: str = "decision_log.json"):
        """Export decision log"""
        with open(filename, 'w') as f:
            json.dump(self.decision_log, f, indent=2)
    
    def record_outcome(self, decision_id: str, outcome: str, success: bool, metrics: Dict[str, Any] = None):
        """Record outcome of a decision and learn from it"""
        self.memory.record_outcome(decision_id, outcome, success, metrics)
        
        # Record in autonomy system
        decision = next((d for d in self.decision_log if d.get("id") == decision_id), None)
        if decision:
            ai_made = decision.get("ai_can_decide", False)
            if ai_made and success:
                # Record success for autonomy progression
                self.autonomy.record_success("decision")
        
        # Generate learning if successful
        if success:
            insight = f"Decision {decision_id} succeeded: {outcome}"
            self.memory.record_learning(insight, "decision_outcome", "Apply similar approach in future")
        
        # Update decision in log
        for decision in self.decision_log:
            if decision.get("id") == decision_id:
                decision["outcome"] = outcome
                decision["success"] = success
                break

# Income Strategy Evaluator
class IncomeStrategyEvaluator:
    """AI system for evaluating income generation strategies"""
    
    STRATEGIES = {
        "CRYPTO_TRADING": {"roi_potential": "high", "risk": "high", "scalability": "medium"},
        "DEFI_YIELD": {"roi_potential": "medium", "risk": "medium", "scalability": "high"},
        "SAAS_PRODUCT": {"roi_potential": "high", "risk": "low", "scalability": "high"},
        "E_COMMERCE": {"roi_potential": "medium", "risk": "low", "scalability": "high"},
        "CONTENT_CREATION": {"roi_potential": "medium", "risk": "low", "scalability": "medium"},
        "CONSULTING": {"roi_potential": "high", "risk": "low", "scalability": "low"},
        "AFFILIATE_MARKETING": {"roi_potential": "medium", "risk": "low", "scalability": "high"},
        "API_SERVICES": {"roi_potential": "high", "risk": "low", "scalability": "very_high"}
    }
    
    def evaluate_strategies(self, initial_capital: float) -> List[Dict[str, Any]]:
        """Evaluate all potential income strategies"""
        
        evaluated = []
        
        for strategy_name, attributes in self.STRATEGIES.items():
            score = self._calculate_score(attributes, initial_capital)
            
            evaluated.append({
                "strategy": strategy_name,
                "attributes": attributes,
                "score": score,
                "recommended_allocation": self._calculate_allocation(score, initial_capital),
                "risk_level": self._map_risk(attributes["risk"]),
                "recommendation": "RECOMMENDED" if score > 70 else "CONSIDER" if score > 50 else "LOW_PRIORITY"
            })
        
        # Sort by score
        evaluated.sort(key=lambda x: x["score"], reverse=True)
        
        return evaluated
    
    def _calculate_score(self, attributes: Dict[str, str], capital: float) -> float:
        """Calculate strategy score"""
        score = 0
        
        # ROI potential scoring
        roi_scores = {"very_high": 40, "high": 30, "medium": 20, "low": 10}
        score += roi_scores.get(attributes.get("roi_potential", "medium"), 20)
        
        # Scalability scoring
        scale_scores = {"very_high": 30, "high": 25, "medium": 15, "low": 5}
        score += scale_scores.get(attributes.get("scalability", "medium"), 15)
        
        # Risk adjustment (lower risk = higher score)
        risk_adjustments = {"low": 30, "medium": 20, "high": 10}
        score += risk_adjustments.get(attributes.get("risk", "medium"), 20)
        
        return score
    
    def _calculate_allocation(self, score: float, capital: float) -> float:
        """Calculate recommended capital allocation"""
        if score > 70:
            return capital * 0.30  # 30% for top strategies
        elif score > 50:
            return capital * 0.15  # 15% for good strategies
        else:
            return capital * 0.05  # 5% for low priority
    
    def _map_risk(self, risk_str: str) -> RiskLevel:
        """Map risk string to RiskLevel"""
        mapping = {
            "low": RiskLevel.LOW,
            "medium": RiskLevel.MEDIUM,
            "high": RiskLevel.HIGH
        }
        return mapping.get(risk_str, RiskLevel.MEDIUM)

# Performance Tracker
class PerformanceTracker:
    """Track performance metrics"""
    
    def __init__(self):
        self.metrics = {
            "revenue": 0.0,
            "capital_base": 0.0,
            "active_streams": 0,
            "growth_rate": 0.0,
            "risk_score": 0.0,
            "compliance_score": 100.0,
            "decisions_made": 0,
            "success_rate": 0.0
        }
        self.history = []
    
    def update_metric(self, metric_name: str, value: float):
        """Update a metric"""
        if metric_name in self.metrics:
            self.metrics[metric_name] = value
            self._record_history()
    
    def get_metrics(self) -> Dict[str, float]:
        """Get current metrics"""
        return self.metrics.copy()
    
    def _record_history(self):
        """Record metrics history"""
        self.history.append({
            "timestamp": datetime.now().isoformat(),
            "metrics": self.metrics.copy()
        })

# Main System
class DecisionEngineSystem:
    """Main AI system orchestrator"""
    
    def __init__(self):
        self.decision_engine = AIDecisionEngine()
        self.strategy_evaluator = IncomeStrategyEvaluator()
        self.performance_tracker = PerformanceTracker()
        self.phase = 1
        self.status = "INITIALIZING"
    
    def initialize(self, initial_capital: float = 0.0):
        """Initialize the system"""
        self.performance_tracker.update_metric("capital_base", initial_capital)
        self.status = "ACTIVE"
        print(f"AI Decision Engine System initialized with capital: ${initial_capital:,.2f}")
    
    def evaluate_income_strategies(self) -> List[Dict[str, Any]]:
        """Evaluate potential income strategies"""
        capital = self.performance_tracker.metrics["capital_base"]
        strategies = self.strategy_evaluator.evaluate_strategies(capital)
        
        # Log the evaluation
        decision = self.decision_engine.evaluate_decision({
            "category": DecisionCategory.STRATEGIC.value,
            "description": "Income strategy evaluation",
            "amount": 0,
            "strategies": strategies
        })
        
        self.decision_engine.log_decision(decision)
        
        return strategies
    
    def make_decision(self, decision_data: Dict[str, Any]) -> Dict[str, Any]:
        """Make a decision through the AI system"""
        decision = self.decision_engine.evaluate_decision(decision_data)
        
        # Auto-execute if low/medium risk
        if decision["action_required"] == "EXECUTE_IMMEDIATELY":
            decision = self.decision_engine.execute_decision(decision)
        
        return decision
    
    def get_status(self) -> Dict[str, Any]:
        """Get system status"""
        return {
            "phase": self.phase,
            "status": self.status,
            "metrics": self.performance_tracker.get_metrics(),
            "recent_decisions": self.decision_engine.get_decisions(10)
        }

if __name__ == "__main__":
    # Initialize system
    system = DecisionEngineSystem()
    system.initialize(initial_capital=0.0)  # Will be updated after contract analysis
    
    # Evaluate strategies
    strategies = system.evaluate_income_strategies()
    
    print("\n=== TOP RECOMMENDED STRATEGIES ===")
    for i, strategy in enumerate(strategies[:5], 1):
        print(f"{i}. {strategy['strategy']}: Score {strategy['score']:.1f} - {strategy['recommendation']}")
    
    print(f"\n=== SYSTEM STATUS ===")
    status = system.get_status()
    print(json.dumps(status, indent=2))

