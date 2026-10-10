"""
API Health Monitor
Continuously monitors API health and performance
"""

import requests
import time
import json
from datetime import datetime
from typing import Dict, Any, List
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class APIHealthMonitor:
    """Monitor API health and performance"""
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.health_history: List[Dict[str, Any]] = []
        self.max_history = 100
    
    def check_health(self) -> Dict[str, Any]:
        """Check API health endpoint"""
        try:
            start_time = time.time()
            response = requests.get(f"{self.base_url}/health", timeout=5)
            response_time = (time.time() - start_time) * 1000  # ms
            
            health_data = {
                "timestamp": datetime.now().isoformat(),
                "status_code": response.status_code,
                "response_time_ms": round(response_time, 2),
                "healthy": response.status_code == 200,
                "data": response.json() if response.status_code == 200 else None
            }
            
            self.health_history.append(health_data)
            if len(self.health_history) > self.max_history:
                self.health_history.pop(0)
            
            return health_data
            
        except requests.exceptions.ConnectionError:
            return {
                "timestamp": datetime.now().isoformat(),
                "status_code": 0,
                "response_time_ms": None,
                "healthy": False,
                "error": "Connection refused - API not running"
            }
        except Exception as e:
            return {
                "timestamp": datetime.now().isoformat(),
                "status_code": 0,
                "response_time_ms": None,
                "healthy": False,
                "error": str(e)
            }
    
    def check_all_endpoints(self) -> Dict[str, Any]:
        """Check all API endpoints"""
        endpoints = [
            ("/health", "GET"),
            ("/autonomy/level", "GET"),
        ]
        
        results = {
            "timestamp": datetime.now().isoformat(),
            "endpoints": {}
        }
        
        for endpoint, method in endpoints:
            try:
                if method == "GET":
                    response = requests.get(f"{self.base_url}{endpoint}", timeout=5)
                else:
                    response = requests.post(f"{self.base_url}{endpoint}", json={}, timeout=5)
                
                results["endpoints"][endpoint] = {
                    "status_code": response.status_code,
                    "healthy": response.status_code == 200,
                    "response_time_ms": response.elapsed.total_seconds() * 1000
                }
            except Exception as e:
                results["endpoints"][endpoint] = {
                    "status_code": 0,
                    "healthy": False,
                    "error": str(e)
                }
        
        return results
    
    def get_stats(self) -> Dict[str, Any]:
        """Get health statistics"""
        if not self.health_history:
            return {"error": "No health data available"}
        
        healthy_count = sum(1 for h in self.health_history if h.get("healthy"))
        response_times = [h["response_time_ms"] for h in self.health_history if h.get("response_time_ms")]
        
        return {
            "total_checks": len(self.health_history),
            "healthy_checks": healthy_count,
            "uptime_percentage": (healthy_count / len(self.health_history)) * 100 if self.health_history else 0,
            "avg_response_time_ms": sum(response_times) / len(response_times) if response_times else None,
            "min_response_time_ms": min(response_times) if response_times else None,
            "max_response_time_ms": max(response_times) if response_times else None
        }
    
    def monitor_continuous(self, interval: int = 60, duration: int = 3600):
        """Monitor continuously"""
        logger.info(f"Starting continuous monitoring (interval: {interval}s, duration: {duration}s)")
        start_time = time.time()
        
        while time.time() - start_time < duration:
            health = self.check_health()
            status = "✅ HEALTHY" if health.get("healthy") else "❌ UNHEALTHY"
            logger.info(f"{status} - Response time: {health.get('response_time_ms', 'N/A')}ms")
            time.sleep(interval)
        
        stats = self.get_stats()
        logger.info(f"Monitoring complete. Stats: {stats}")

def main():
    """Run API health monitor"""
    monitor = APIHealthMonitor()
    
    print("=" * 60)
    print("API HEALTH MONITOR")
    print("=" * 60)
    print()
    
    # Single check
    health = monitor.check_health()
    print(f"Status: {'✅ HEALTHY' if health.get('healthy') else '❌ UNHEALTHY'}")
    print(f"Response Time: {health.get('response_time_ms', 'N/A')}ms")
    print(f"Status Code: {health.get('status_code', 'N/A')}")
    
    if health.get("error"):
        print(f"Error: {health['error']}")
    
    print()
    
    # Check all endpoints
    print("Checking all endpoints...")
    endpoint_results = monitor.check_all_endpoints()
    for endpoint, result in endpoint_results["endpoints"].items():
        status = "✅" if result.get("healthy") else "❌"
        print(f"{status} {endpoint}: {result.get('status_code', 'N/A')}")
    
    print()
    print("=" * 60)

if __name__ == "__main__":
    main()

