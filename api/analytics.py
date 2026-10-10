"""
API Usage Analytics
Track and analyze API usage patterns
"""

import json
import os
from datetime import datetime, timedelta
from typing import Dict, Any, List
from collections import defaultdict

ANALYTICS_FILE = "api_analytics.json"

class APIAnalytics:
    """Track and analyze API usage"""
    
    def __init__(self):
        self.analytics_file = ANALYTICS_FILE
        self._ensure_file_exists()
    
    def _ensure_file_exists(self):
        """Ensure analytics file exists"""
        if not os.path.exists(self.analytics_file):
            with open(self.analytics_file, "w") as f:
                json.dump({
                    "requests": [],
                    "endpoints": {},
                    "keys": {},
                    "daily_stats": {}
                }, f, indent=2)
    
    def _load_analytics(self) -> Dict[str, Any]:
        """Load analytics data"""
        try:
            with open(self.analytics_file, "r") as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return {
                "requests": [],
                "endpoints": {},
                "keys": {},
                "daily_stats": {}
            }
    
    def _save_analytics(self, data: Dict[str, Any]):
        """Save analytics data"""
        with open(self.analytics_file, "w") as f:
            json.dump(data, f, indent=2)
    
    def record_request(
        self,
        endpoint: str,
        method: str,
        api_key: str,
        status_code: int,
        response_time_ms: float = None
    ):
        """Record an API request"""
        data = self._load_analytics()
        
        request_record = {
            "timestamp": datetime.now().isoformat(),
            "endpoint": endpoint,
            "method": method,
            "api_key_prefix": api_key[:10] + "..." if api_key else "anonymous",
            "status_code": status_code,
            "response_time_ms": response_time_ms
        }
        
        # Add to requests list (keep last 1000)
        data["requests"].append(request_record)
        if len(data["requests"]) > 1000:
            data["requests"] = data["requests"][-1000:]
        
        # Update endpoint stats
        endpoint_key = f"{method} {endpoint}"
        if endpoint_key not in data["endpoints"]:
            data["endpoints"][endpoint_key] = {
                "count": 0,
                "success_count": 0,
                "error_count": 0,
                "avg_response_time": 0
            }
        
        endpoint_stats = data["endpoints"][endpoint_key]
        endpoint_stats["count"] += 1
        if status_code == 200:
            endpoint_stats["success_count"] += 1
        else:
            endpoint_stats["error_count"] += 1
        
        if response_time_ms:
            current_avg = endpoint_stats["avg_response_time"]
            count = endpoint_stats["count"]
            endpoint_stats["avg_response_time"] = (
                (current_avg * (count - 1) + response_time_ms) / count
            )
        
        # Update key stats
        key_prefix = api_key[:10] + "..." if api_key else "anonymous"
        if key_prefix not in data["keys"]:
            data["keys"][key_prefix] = {
                "count": 0,
                "last_used": None
            }
        
        data["keys"][key_prefix]["count"] += 1
        data["keys"][key_prefix]["last_used"] = datetime.now().isoformat()
        
        # Update daily stats
        today = datetime.now().strftime("%Y-%m-%d")
        if today not in data["daily_stats"]:
            data["daily_stats"][today] = {
                "total_requests": 0,
                "successful_requests": 0,
                "failed_requests": 0
            }
        
        daily = data["daily_stats"][today]
        daily["total_requests"] += 1
        if status_code == 200:
            daily["successful_requests"] += 1
        else:
            daily["failed_requests"] += 1
        
        self._save_analytics(data)
    
    def get_stats(self, days: int = 30) -> Dict[str, Any]:
        """Get analytics statistics"""
        data = self._load_analytics()
        
        # Calculate date range
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        
        # Filter requests by date
        recent_requests = [
            r for r in data["requests"]
            if datetime.fromisoformat(r["timestamp"]) >= start_date
        ]
        
        # Calculate stats
        total_requests = len(recent_requests)
        successful = sum(1 for r in recent_requests if r["status_code"] == 200)
        failed = total_requests - successful
        
        # Top endpoints
        endpoint_counts = defaultdict(int)
        for r in recent_requests:
            endpoint_counts[r["endpoint"]] += 1
        top_endpoints = sorted(
            endpoint_counts.items(),
            key=lambda x: x[1],
            reverse=True
        )[:10]
        
        # Response times
        response_times = [
            r["response_time_ms"]
            for r in recent_requests
            if r.get("response_time_ms")
        ]
        avg_response_time = (
            sum(response_times) / len(response_times)
            if response_times else 0
        )
        
        return {
            "period_days": days,
            "total_requests": total_requests,
            "successful_requests": successful,
            "failed_requests": failed,
            "success_rate": (successful / total_requests * 100) if total_requests > 0 else 0,
            "avg_response_time_ms": round(avg_response_time, 2),
            "top_endpoints": [
                {"endpoint": ep, "count": count}
                for ep, count in top_endpoints
            ],
            "endpoint_stats": data["endpoints"],
            "active_keys": len(data["keys"]),
            "daily_stats": data["daily_stats"]
        }
    
    def get_endpoint_stats(self, endpoint: str) -> Dict[str, Any]:
        """Get statistics for a specific endpoint"""
        data = self._load_analytics()
        
        # Find all matching endpoints
        stats = {}
        for key, value in data["endpoints"].items():
            if endpoint in key:
                stats[key] = value
        
        return stats
    
    def export_report(self, output_file: str = "api_analytics_report.json"):
        """Export analytics report"""
        stats = self.get_stats()
        
        report = {
            "generated_at": datetime.now().isoformat(),
            "summary": {
                "total_requests": stats["total_requests"],
                "success_rate": f"{stats['success_rate']:.2f}%",
                "avg_response_time_ms": stats["avg_response_time_ms"]
            },
            "top_endpoints": stats["top_endpoints"],
            "endpoint_details": stats["endpoint_stats"],
            "daily_breakdown": stats["daily_stats"]
        }
        
        with open(output_file, "w") as f:
            json.dump(report, f, indent=2)
        
        return report

# Global instance
api_analytics = APIAnalytics()

