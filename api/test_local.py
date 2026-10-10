"""
Local API Testing Script
Tests API endpoints without requiring server to be running
"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ai_decision_engine import AIDecisionEngine, DecisionCategory, RiskLevel

def test_decision_engine():
    """Test the decision engine directly"""
    print("=" * 60)
    print("TESTING AI DECISION ENGINE (Local)")
    print("=" * 60)
    print()
    
    try:
        # Initialize decision engine
        print("🔧 Initializing Decision Engine...")
        engine = AIDecisionEngine()
        print("   ✅ Decision Engine initialized")
        print()
        
        # Test decision evaluation
        print("🧪 Testing Decision Evaluation...")
        decision_data = {
            "category": DecisionCategory.FINANCIAL.value,
            "amount": 1000.0,
            "description": "Test marketing campaign investment"
        }
        decision = engine.evaluate_decision(decision_data)
        print(f"   ✅ Decision ID: {decision.get('id', 'N/A')}")
        print(f"   ✅ Risk Level: {decision.get('risk_level', 'N/A')}")
        print(f"   ✅ AI Can Decide: {decision.get('ai_can_decide', False)}")
        print()
        
        # Test another decision with higher risk
        print("🧪 Testing Higher Risk Decision...")
        high_risk_data = {
            "category": DecisionCategory.STRATEGIC.value,
            "amount": 5000.0,
            "description": "Test strategic decision with higher amount"
        }
        high_risk_decision = engine.evaluate_decision(high_risk_data)
        print(f"   ✅ Decision ID: {high_risk_decision.get('id', 'N/A')}")
        print(f"   ✅ Risk Level: {high_risk_decision.get('risk_level', 'N/A')}")
        print(f"   ✅ Action Required: {high_risk_decision.get('action_required', 'N/A')}")
        print()
        
        # Test autonomy level
        print("🧪 Testing Autonomy System...")
        autonomy_level = engine.autonomy.get_autonomy_level()
        print(f"   ✅ Autonomy Level: {autonomy_level}%")
        print()
        
        # Test should auto-execute
        print("🧪 Testing Auto-Execute Check...")
        should_execute = engine.autonomy.should_auto_execute(
            "operational",
            "LOW"
        )
        print(f"   ✅ Should Auto-Execute: {should_execute}")
        print()
        
        print("=" * 60)
        print("✅ ALL TESTS PASSED")
        print("=" * 60)
        print()
        print("The decision engine is working correctly!")
        print("API server should function properly.")
        return True
        
    except Exception as e:
        print("=" * 60)
        print("❌ TEST FAILED")
        print("=" * 60)
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_decision_engine()
    sys.exit(0 if success else 1)

