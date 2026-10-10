"""
Enhanced API Client Example
Complete example of using the AI Decision Engine API
"""

from api.client import AIDecisionAPIClient
import json
from datetime import datetime

def example_usage():
    """Complete example of API usage"""
    
    print("=" * 60)
    print("AI DECISION ENGINE API - CLIENT EXAMPLE")
    print("=" * 60)
    print()
    
    # Initialize client
    client = AIDecisionAPIClient(
        api_key="dev_key_123",
        base_url="http://localhost:8000"
    )
    
    # 1. Health Check
    print("1. Checking API health...")
    try:
        health = client.health_check()
        print(f"   ✅ API Status: {health.get('status')}")
        print(f"   ✅ Version: {health.get('version')}")
    except Exception as e:
        print(f"   ❌ Health check failed: {e}")
        return
    
    print()
    
    # 2. Evaluate a Decision
    print("2. Evaluating a financial decision...")
    try:
        decision = client.evaluate_decision(
            category="FINANCIAL",
            amount=5000.0,
            description="Invest in new marketing campaign"
        )
        print(f"   ✅ Decision ID: {decision.get('id')}")
        print(f"   ✅ Risk Level: {decision.get('risk_level')}")
        print(f"   ✅ AI Can Decide: {decision.get('ai_can_decide')}")
        print(f"   ✅ Action Required: {decision.get('action_required')}")
    except Exception as e:
        print(f"   ❌ Decision evaluation failed: {e}")
    
    print()
    
    # 3. Assess Risk
    print("3. Assessing risk for strategic decision...")
    try:
        risk = client.assess_risk(
            amount=10000.0,
            category="STRATEGIC",
            description="Launch new product line"
        )
        print(f"   ✅ Risk Level: {risk.get('risk_level')}")
        print(f"   ✅ Risk Score: {risk.get('risk_score')}")
        print(f"   ✅ Recommendation: {risk.get('recommendation')}")
    except Exception as e:
        print(f"   ❌ Risk assessment failed: {e}")
    
    print()
    
    # 4. Get Autonomy Level
    print("4. Getting AI autonomy level...")
    try:
        autonomy = client.get_autonomy_level()
        print(f"   ✅ Autonomy Level: {autonomy.get('autonomy_level')}%")
        print(f"   ✅ AI Tasks: {len(autonomy.get('ai_tasks', []))}")
        print(f"   ✅ Human Tasks: {len(autonomy.get('human_tasks', []))}")
    except Exception as e:
        print(f"   ❌ Failed to get autonomy level: {e}")
    
    print()
    
    # 5. Check Auto-Execute
    print("5. Checking if AI should auto-execute...")
    try:
        execute = client.should_auto_execute(
            task_type="operational",
            risk_level="LOW"
        )
        print(f"   ✅ Should Execute: {execute.get('should_execute')}")
        print(f"   ✅ Reason: {execute.get('reason')}")
    except Exception as e:
        print(f"   ❌ Auto-execute check failed: {e}")
    
    print()
    
    # 6. Get Memory Insights
    print("6. Getting memory insights...")
    try:
        insights = client.get_memory_insights({
            "category": "FINANCIAL",
            "amount": 1000
        })
        print(f"   ✅ Similar Decisions: {insights.get('similar_decisions', 0)}")
        print(f"   ✅ Recommendations: {len(insights.get('recommendations', []))}")
    except Exception as e:
        print(f"   ❌ Memory insights failed: {e}")
    
    print()
    print("=" * 60)
    print("✅ Example complete!")
    print("=" * 60)

if __name__ == "__main__":
    example_usage()
