"""
Advanced Analytics Dashboard
Enhanced analytics with visualizations
"""

import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any

class AdvancedAnalytics:
    """Advanced analytics with insights"""
    
    def __init__(self):
        self.analytics_file = "api/api_analytics.json"
        self.analytics = self._load_analytics()
    
    def _load_analytics(self) -> Dict[str, Any]:
        """Load analytics data"""
        try:
            if Path(self.analytics_file).exists():
                with open(self.analytics_file, "r") as f:
                    return json.load(f)
        except:
            pass
        return {"requests": []}
    
    def get_trends(self, days: int = 7) -> Dict[str, Any]:
        """Get usage trends"""
        cutoff = datetime.now() - timedelta(days=days)
        requests = [
            r for r in self.analytics.get("requests", [])
            if datetime.fromisoformat(r["timestamp"]) > cutoff
        ]
        
        # Group by day
        daily_counts = {}
        for req in requests:
            date = datetime.fromisoformat(req["timestamp"]).date()
            daily_counts[date] = daily_counts.get(date, 0) + 1
        
        return {
            "total_requests": len(requests),
            "daily_breakdown": {str(k): v for k, v in daily_counts.items()},
            "average_per_day": len(requests) / days if days > 0 else 0
        }
    
    def get_endpoint_performance(self) -> Dict[str, Any]:
        """Get endpoint performance metrics"""
        requests = self.analytics.get("requests", [])
        
        endpoint_stats = {}
        for req in requests:
            endpoint = req.get("endpoint", "unknown")
            if endpoint not in endpoint_stats:
                endpoint_stats[endpoint] = {
                    "count": 0,
                    "total_time": 0,
                    "errors": 0
                }
            
            endpoint_stats[endpoint]["count"] += 1
            endpoint_stats[endpoint]["total_time"] += req.get("response_time", 0)
            
            if req.get("status_code", 200) >= 400:
                endpoint_stats[endpoint]["errors"] += 1
        
        # Calculate averages
        for endpoint, stats in endpoint_stats.items():
            if stats["count"] > 0:
                stats["avg_response_time"] = stats["total_time"] / stats["count"]
                stats["error_rate"] = (stats["errors"] / stats["count"]) * 100
        
        return endpoint_stats
    
    def get_user_insights(self) -> Dict[str, Any]:
        """Get user usage insights"""
        requests = self.analytics.get("requests", [])
        
        user_stats = {}
        for req in requests:
            api_key = req.get("api_key", "unknown")[:10] + "..."
            if api_key not in user_stats:
                user_stats[api_key] = {
                    "requests": 0,
                    "endpoints": set()
                }
            
            user_stats[api_key]["requests"] += 1
            user_stats[api_key]["endpoints"].add(req.get("endpoint", "unknown"))
        
        # Convert sets to counts
        for api_key, stats in user_stats.items():
            stats["unique_endpoints"] = len(stats["endpoints"])
            del stats["endpoints"]
        
        return user_stats
    
    def generate_report(self) -> str:
        """Generate analytics report"""
        trends = self.get_trends(30)
        performance = self.get_endpoint_performance()
        users = self.get_user_insights()
        
        report = f"""
========================================
ANALYTICS REPORT
========================================
Generated: {datetime.now().isoformat()}

USAGE TRENDS (Last 30 Days)
----------------------------------------
Total Requests: {trends['total_requests']}
Average per Day: {trends['average_per_day']:.2f}

ENDPOINT PERFORMANCE
----------------------------------------
"""
        for endpoint, stats in sorted(performance.items(), key=lambda x: x[1]["count"], reverse=True)[:10]:
            report += f"""
{endpoint}:
  Requests: {stats['count']}
  Avg Response Time: {stats.get('avg_response_time', 0):.2f}ms
  Error Rate: {stats.get('error_rate', 0):.2f}%
"""
        
        report += f"""
TOP USERS
----------------------------------------
"""
        for user, stats in sorted(users.items(), key=lambda x: x[1]["requests"], reverse=True)[:10]:
            report += f"{user}: {stats['requests']} requests, {stats['unique_endpoints']} endpoints\n"
        
        return report

def main():
    """Generate analytics report"""
    analytics = AdvancedAnalytics()
    report = analytics.generate_report()
    print(report)
    
    # Save report
    with open("analytics_report.txt", "w") as f:
        f.write(report)
    
    print("\nReport saved to: analytics_report.txt")

if __name__ == "__main__":
    main()

