"""
Demo Application
Example application using the API
"""

import sys
from pathlib import Path

# Add SDK to path
sys.path.insert(0, str(Path(__file__).parent.parent / "sdk" / "python"))

try:
    from ai_decision_engine import AIDecisionEngineClient
except ImportError:
    print("SDK not available. Using direct API calls.")
    import requests
    AIDecisionEngineClient = None

class DecisionDemo:
    """Demo application for decision making"""
    
    def __init__(self, api_key: str, base_url: str = "http://localhost:8000"):
        if AIDecisionEngineClient:
            self.client = AIDecisionEngineClient(api_key, base_url)
        else:
            self.api_key = api_key
            self.base_url = base_url
            self.headers = {
                "X-API-Key": api_key,
                "Content-Type": "application/json"
            }
    
    def make_decision(self, category: str, amount: float, description: str):
        """Make a decision using the API"""
        if hasattr(self, 'client'):
            result = self.client.evaluate_decision(category, amount, description)
        else:
            response = requests.post(
                f"{self.base_url}/decisions/evaluate",
                json={"category": category, "amount": amount, "description": description},
                headers=self.headers
            )
            result = response.json()
        
        print(f"\n{'='*60}")
        print(f"DECISION EVALUATION")
        print(f"{'='*60}")
        print(f"Decision ID: {result.get('id')}")
        print(f"Category: {result.get('category')}")
        print(f"Amount: ${result.get('amount', 0):,.2f}")
        print(f"Risk Level: {result.get('risk_level')}")
        print(f"AI Can Decide: {result.get('ai_can_decide', False)}")
        print(f"Action Required: {result.get('action_required', 'N/A')}")
        
        if result.get('ai_can_decide'):
            print(f"\n✅ AI can make this decision autonomously!")
        else:
            print(f"\n⚠️  Human approval required")
        
        return result
    
    def assess_risk(self, amount: float, category: str = "OPERATIONAL"):
        """Assess risk"""
        if hasattr(self, 'client'):
            result = self.client.assess_risk(amount, category)
        else:
            response = requests.post(
                f"{self.base_url}/risk/assess",
                json={"amount": amount, "category": category},
                headers=self.headers
            )
            result = response.json()
        
        print(f"\n{'='*60}")
        print(f"RISK ASSESSMENT")
        print(f"{'='*60}")
        print(f"Amount: ${amount:,.2f}")
        print(f"Category: {category}")
        print(f"Risk Level: {result.get('risk_level')}")
        print(f"Risk Score: {result.get('risk_score', 0):.2f}")
        print(f"Recommendation: {result.get('recommendation', 'N/A')}")
        
        return result
    
    def run_demo(self):
        """Run interactive demo"""
        print("="*60)
        print("AI DECISION ENGINE - DEMO APPLICATION")
        print("="*60)
        print()
        
        # Demo 1: Small purchase decision
        print("Demo 1: Small Purchase Decision")
        self.make_decision(
            category="FINANCIAL",
            amount=500.0,
            description="Purchase office supplies"
        )
        
        # Demo 2: Large strategic decision
        print("\n\nDemo 2: Large Strategic Decision")
        self.make_decision(
            category="STRATEGIC",
            amount=50000.0,
            description="Major infrastructure upgrade"
        )
        
        # Demo 3: Risk assessment
        print("\n\nDemo 3: Risk Assessment")
        self.assess_risk(amount=10000, category="FINANCIAL")
        
        print("\n\n" + "="*60)
        print("DEMO COMPLETE")
        print("="*60)

def main():
    """Run demo"""
    import argparse
    
    parser = argparse.ArgumentParser(description="AI Decision Engine Demo")
    parser.add_argument("--api-key", default="dev_key_123", help="API key")
    parser.add_argument("--base-url", default="http://localhost:8000", help="Base URL")
    
    args = parser.parse_args()
    
    demo = DecisionDemo(args.api_key, args.base_url)
    demo.run_demo()

if __name__ == "__main__":
    main()

