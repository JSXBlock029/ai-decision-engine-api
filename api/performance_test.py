"""
Performance Testing Utilities
Test API performance and load
"""

import requests
import time
import statistics
from typing import List, Dict, Any
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime

class PerformanceTester:
    """Test API performance"""
    
    def __init__(self, base_url: str = "http://localhost:8000", api_key: str = "dev_key_123"):
        self.base_url = base_url
        self.headers = {
            "X-API-Key": api_key,
            "Content-Type": "application/json"
        }
    
    def test_endpoint(
        self,
        endpoint: str,
        method: str = "GET",
        data: Dict[str, Any] = None,
        iterations: int = 10
    ) -> Dict[str, Any]:
        """Test a single endpoint"""
        response_times = []
        errors = 0
        
        for _ in range(iterations):
            try:
                start_time = time.time()
                
                if method == "GET":
                    response = requests.get(
                        f"{self.base_url}{endpoint}",
                        headers=self.headers,
                        timeout=10
                    )
                else:
                    response = requests.post(
                        f"{self.base_url}{endpoint}",
                        json=data or {},
                        headers=self.headers,
                        timeout=10
                    )
                
                response_time = (time.time() - start_time) * 1000  # ms
                response_times.append(response_time)
                
                if response.status_code != 200:
                    errors += 1
                    
            except Exception as e:
                errors += 1
                print(f"Error: {e}")
        
        if not response_times:
            return {
                "endpoint": endpoint,
                "status": "failed",
                "errors": errors
            }
        
        return {
            "endpoint": endpoint,
            "iterations": iterations,
            "errors": errors,
            "success_rate": ((iterations - errors) / iterations) * 100,
            "avg_response_time_ms": statistics.mean(response_times),
            "min_response_time_ms": min(response_times),
            "max_response_time_ms": max(response_times),
            "median_response_time_ms": statistics.median(response_times),
            "p95_response_time_ms": self._percentile(response_times, 95),
            "p99_response_time_ms": self._percentile(response_times, 99)
        }
    
    def _percentile(self, data: List[float], percentile: int) -> float:
        """Calculate percentile"""
        sorted_data = sorted(data)
        index = int(len(sorted_data) * percentile / 100)
        return sorted_data[min(index, len(sorted_data) - 1)]
    
    def load_test(
        self,
        endpoint: str,
        method: str = "GET",
        data: Dict[str, Any] = None,
        concurrent_requests: int = 10,
        total_requests: int = 100
    ) -> Dict[str, Any]:
        """Run load test with concurrent requests"""
        response_times = []
        errors = 0
        start_time = time.time()
        
        def make_request():
            try:
                req_start = time.time()
                
                if method == "GET":
                    response = requests.get(
                        f"{self.base_url}{endpoint}",
                        headers=self.headers,
                        timeout=10
                    )
                else:
                    response = requests.post(
                        f"{self.base_url}{endpoint}",
                        json=data or {},
                        headers=self.headers,
                        timeout=10
                    )
                
                req_time = (time.time() - req_start) * 1000
                response_times.append(req_time)
                
                if response.status_code != 200:
                    return False
                return True
            except:
                return False
        
        with ThreadPoolExecutor(max_workers=concurrent_requests) as executor:
            futures = [executor.submit(make_request) for _ in range(total_requests)]
            
            for future in as_completed(futures):
                if not future.result():
                    errors += 1
        
        total_time = time.time() - start_time
        
        return {
            "endpoint": endpoint,
            "total_requests": total_requests,
            "concurrent_requests": concurrent_requests,
            "total_time_seconds": total_time,
            "requests_per_second": total_requests / total_time if total_time > 0 else 0,
            "errors": errors,
            "success_rate": ((total_requests - errors) / total_requests) * 100 if total_requests > 0 else 0,
            "avg_response_time_ms": statistics.mean(response_times) if response_times else 0,
            "min_response_time_ms": min(response_times) if response_times else 0,
            "max_response_time_ms": max(response_times) if response_times else 0,
            "p95_response_time_ms": self._percentile(response_times, 95) if response_times else 0
        }
    
    def test_all_endpoints(self, iterations: int = 5) -> Dict[str, Any]:
        """Test all main endpoints"""
        endpoints = [
            ("GET", "/health", None),
            ("POST", "/decisions/evaluate", {"category": "FINANCIAL", "amount": 1000}),
            ("POST", "/risk/assess", {"amount": 5000, "category": "STRATEGIC"}),
            ("GET", "/autonomy/level", None),
        ]
        
        results = {
            "timestamp": datetime.now().isoformat(),
            "endpoints": []
        }
        
        for method, endpoint, data in endpoints:
            result = self.test_endpoint(endpoint, method, data, iterations)
            results["endpoints"].append(result)
        
        return results

def main():
    """Run performance tests"""
    tester = PerformanceTester()
    
    print("=" * 60)
    print("API PERFORMANCE TEST")
    print("=" * 60)
    print()
    
    # Test all endpoints
    results = tester.test_all_endpoints(iterations=10)
    
    for endpoint_result in results["endpoints"]:
        print(f"Endpoint: {endpoint_result['endpoint']}")
        print(f"  Avg Response Time: {endpoint_result['avg_response_time_ms']:.2f} ms")
        print(f"  Success Rate: {endpoint_result['success_rate']:.1f}%")
        print()
    
    # Load test
    print("Running load test...")
    load_result = tester.load_test(
        "/decisions/evaluate",
        method="POST",
        data={"category": "FINANCIAL", "amount": 1000},
        concurrent_requests=5,
        total_requests=50
    )
    
    print(f"Load Test Results:")
    print(f"  Requests/sec: {load_result['requests_per_second']:.2f}")
    print(f"  Success Rate: {load_result['success_rate']:.1f}%")
    print(f"  Avg Response Time: {load_result['avg_response_time_ms']:.2f} ms")

if __name__ == "__main__":
    main()

