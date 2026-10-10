"""
Live Demo Runner
Run a live interactive demo
"""

import requests
import json
from datetime import datetime

class LiveDemo:
    """Interactive live demo"""
    
    def __init__(self, base_url: str = "http://localhost:8000", api_key: str = "dev_key_123"):
        self.base_url = base_url
        self.api_key = api_key
        self.headers = {
            "X-API-Key": api_key,
            "Content-Type": "application/json"
        }
    
    def check_health(self):
        """Check API health"""
        try:
            response = requests.get(f"{self.base_url}/health", timeout=2)
            if response.status_code == 200:
                data = response.json()
                print(f"✓ API is healthy!")
                print(f"  Version: {data.get('version', 'N/A')}")
                print(f"  Status: {data.get('status', 'N/A')}")
                return True
            else:
                print(f"✗ API returned status {response.status_code}")
                return False
        except Exception as e:
            print(f"✗ Cannot connect to API: {e}")
            print(f"  Make sure the server is running on {self.base_url}")
            return False
    
    def run_demo_scenarios(self):
        """Run demo scenarios"""
        print("\n" + "="*60)
        print("LIVE DEMO SCENARIOS")
        print("="*60)
        print()
        
        scenarios = [
            {
                "name": "Small Purchase Decision",
                "category": "FINANCIAL",
                "amount": 500.0,
                "description": "Purchase office supplies for team"
            },
            {
                "name": "Medium Strategic Decision",
                "category": "STRATEGIC",
                "amount": 10000.0,
                "description": "Upgrade development infrastructure"
            },
            {
                "name": "Large Financial Decision",
                "category": "FINANCIAL",
                "amount": 50000.0,
                "description": "Major equipment purchase"
            }
        ]
        
        for i, scenario in enumerate(scenarios, 1):
            print(f"\nScenario {i}: {scenario['name']}")
            print("-" * 60)
            
            try:
                response = requests.post(
                    f"{self.base_url}/decisions/evaluate",
                    json={
                        "category": scenario["category"],
                        "amount": scenario["amount"],
                        "description": scenario["description"]
                    },
                    headers=self.headers,
                    timeout=5
                )
                
                if response.status_code == 200:
                    data = response.json()
                    print(f"✓ Decision evaluated successfully!")
                    print(f"  ID: {data.get('id', 'N/A')}")
                    print(f"  Risk Level: {data.get('risk_level', 'N/A')}")
                    print(f"  AI Can Decide: {data.get('ai_can_decide', False)}")
                    print(f"  Action Required: {data.get('action_required', 'N/A')}")
                else:
                    print(f"✗ Request failed: {response.status_code}")
                    print(f"  {response.text}")
            
            except Exception as e:
                print(f"✗ Error: {e}")
    
    def run_risk_assessment_demo(self):
        """Run risk assessment demo"""
        print("\n" + "="*60)
        print("RISK ASSESSMENT DEMO")
        print("="*60)
        print()
        
        amounts = [100, 1000, 10000, 100000]
        
        for amount in amounts:
            try:
                response = requests.post(
                    f"{self.base_url}/risk/assess",
                    json={"amount": amount, "category": "FINANCIAL"},
                    headers=self.headers,
                    timeout=5
                )
                
                if response.status_code == 200:
                    data = response.json()
                    print(f"Amount: ${amount:>8,} → Risk: {data.get('risk_level', 'N/A')} (Score: {data.get('risk_score', 0):.2f})")
                else:
                    print(f"✗ Failed for ${amount:,}")
            
            except Exception as e:
                print(f"✗ Error for ${amount:,}: {e}")
    
    def show_analytics(self):
        """Show analytics"""
        print("\n" + "="*60)
        print("ANALYTICS")
        print("="*60)
        print()
        
        try:
            response = requests.get(
                f"{self.base_url}/analytics/stats",
                headers=self.headers,
                timeout=5
            )
            
            if response.status_code == 200:
                data = response.json()
                print(f"✓ Analytics retrieved!")
                print(f"  Total Requests: {data.get('total_requests', 0)}")
                print(f"  Successful: {data.get('successful_requests', 0)}")
                print(f"  Failed: {data.get('failed_requests', 0)}")
            else:
                print(f"✗ Analytics request failed: {response.status_code}")
        
        except Exception as e:
            print(f"✗ Error: {e}")

def main():
    """Run live demo"""
    print("="*60)
    print("AI DECISION ENGINE - LIVE DEMO")
    print("="*60)
    print()
    
    demo = LiveDemo()
    
    # Check health
    if not demo.check_health():
        print("\nPlease start the API server first:")
        print("  cd api")
        print("  uvicorn main:app --reload")
        return
    
    # Run demos
    demo.run_demo_scenarios()
    demo.run_risk_assessment_demo()
    demo.show_analytics()
    
    print("\n" + "="*60)
    print("DEMO COMPLETE!")
    print("="*60)
    print()
    print("Next steps:")
    print("  - View API docs: http://localhost:8000/docs")
    print("  - Try the dashboard: dashboard/index.html")
    print("  - Check status: status_page.html")
    print()

if __name__ == "__main__":
    main()

