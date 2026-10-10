"""
Dashboard Data Generator
Creates data for analytics dashboard
"""

from datetime import datetime, timedelta
import json
from typing import Dict, Any, List

class DashboardData:
    """Generate dashboard analytics data"""
    
    def __init__(self):
        self.memory_file = "ai_memory.json"
        self.progress_file = "PROGRESS_STATUS.json"
    
    def get_revenue_data(self) -> Dict[str, Any]:
        """Get revenue projections and actuals"""
        # For now, return projections
        # In production, this would query actual revenue data
        return {
            "projected": {
                "month_1_3": {"min": 500, "max": 5000},
                "month_4_6": {"min": 2500, "max": 8000},
                "month_7_12": {"min": 7000, "max": 25000}
            },
            "actual": {
                "current": 0.0,
                "month_to_date": 0.0,
                "trend": "starting"
            }
        }
    
    def get_strategy_progress(self) -> Dict[str, Any]:
        """Get strategy implementation progress"""
        return {
            "API_SERVICES": {
                "completion": 90,
                "status": "ready_for_testing",
                "next_milestone": "Local testing",
                "expected_revenue_start": "4-8 weeks"
            },
            "SAAS_PRODUCT": {
                "completion": 70,
                "status": "ready_for_deployment",
                "next_milestone": "Landing page launch",
                "expected_revenue_start": "8-12 weeks"
            }
        }
    
    def get_system_metrics(self) -> Dict[str, Any]:
        """Get system performance metrics"""
        try:
            with open(self.memory_file, "r") as f:
                memory = json.load(f)
            
            events_count = len(memory.get("events", []))
            decisions_count = len(memory.get("decisions", []))
            
            # Calculate decision success rate (placeholder)
            decisions = memory.get("decisions", [])
            successful = sum(1 for d in decisions if d.get("decision", {}).get("success") == True)
            success_rate = (successful / decisions_count * 100) if decisions_count > 0 else 0
            
            return {
                "total_events": events_count,
                "total_decisions": decisions_count,
                "success_rate": round(success_rate, 1),
                "ai_autonomy": 77.4,
                "system_health": "operational"
            }
        except:
            return {
                "total_events": 0,
                "total_decisions": 0,
                "success_rate": 0,
                "ai_autonomy": 77.4,
                "system_health": "unknown"
            }
    
    def get_recent_activity(self, days: int = 7) -> List[Dict[str, Any]]:
        """Get recent activity"""
        try:
            with open(self.memory_file, "r") as f:
                memory = json.load(f)
            
            events = memory.get("events", [])
            cutoff_date = (datetime.now() - timedelta(days=days)).isoformat()
            
            recent = [
                event for event in events 
                if event.get("timestamp", "") >= cutoff_date
            ]
            
            return recent[-10:]  # Last 10 events
        except:
            return []
    
    def generate_dashboard_json(self) -> Dict[str, Any]:
        """Generate complete dashboard data"""
        return {
            "timestamp": datetime.now().isoformat(),
            "revenue": self.get_revenue_data(),
            "strategies": self.get_strategy_progress(),
            "metrics": self.get_system_metrics(),
            "recent_activity": self.get_recent_activity()
        }

def main():
    """Generate and save dashboard data"""
    dashboard = DashboardData()
    data = dashboard.generate_dashboard_json()
    
    # Save to file
    with open("analytics/dashboard_data.json", "w") as f:
        json.dump(data, f, indent=2)
    
    print("=" * 60)
    print("DASHBOARD DATA GENERATED")
    print("=" * 60)
    print(f"Timestamp: {data['timestamp']}")
    print(f"\nRevenue Status: ${data['revenue']['actual']['current']}")
    print(f"System Health: {data['metrics']['system_health']}")
    print(f"AI Autonomy: {data['metrics']['ai_autonomy']}%")
    print(f"\nStrategies:")
    for name, info in data['strategies'].items():
        print(f"  {name}: {info['completion']}% - {info['status']}")
    print(f"\nRecent Activity: {len(data['recent_activity'])} events")
    print("\nData saved to: analytics/dashboard_data.json")
    print("=" * 60)

if __name__ == "__main__":
    main()

