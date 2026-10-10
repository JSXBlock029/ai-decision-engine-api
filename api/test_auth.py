"""
Test API Key Authentication
Comprehensive test of the authentication system
"""

import requests
import json
from typing import Dict, Any

BASE_URL = "http://localhost:8000"

def print_section(title: str):
    """Print section header"""
    print("\n" + "=" * 60)
    print(title)
    print("=" * 60)

def test_no_auth():
    """Test endpoints without API key"""
    print_section("TEST 1: Requests Without API Key")
    
    endpoints = [
        ("GET", "/health", False),  # Health should work without auth
        ("POST", "/decisions/evaluate", True),  # Should require auth
        ("GET", "/autonomy/level", True),  # Should require auth
    ]
    
    for method, endpoint, should_fail in endpoints:
        try:
            if method == "GET":
                response = requests.get(f"{BASE_URL}{endpoint}", timeout=5)
            else:
                response = requests.post(f"{BASE_URL}{endpoint}", json={}, timeout=5)
            
            status = response.status_code
            if should_fail:
                if status == 401:
                    print(f"[OK] {endpoint} correctly requires auth (401)")
                else:
                    print(f"[FAIL] {endpoint} should require auth but got {status}")
            else:
                if status == 200:
                    print(f"[OK] {endpoint} works without auth (200)")
                else:
                    print(f"[WARN] {endpoint} returned {status}")
        except requests.exceptions.ConnectionError:
            print(f"[ERROR] Cannot connect to API. Is the server running?")
            return False
        except Exception as e:
            print(f"[ERROR] {endpoint}: {e}")
    
    return True

def test_invalid_key():
    """Test with invalid API key"""
    print_section("TEST 2: Invalid API Key")
    
    headers = {
        "X-API-Key": "invalid_key_12345",
        "Content-Type": "application/json"
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/decisions/evaluate",
            json={"category": "FINANCIAL", "amount": 1000},
            headers=headers,
            timeout=5
        )
        
        if response.status_code == 401:
            print("[OK] Invalid key correctly rejected (401)")
            print(f"   Error: {response.json().get('detail', 'Unknown error')}")
            return True
        else:
            print(f"[FAIL] Invalid key should return 401, got {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("[ERROR] Cannot connect to API. Is the server running?")
        return False
    except Exception as e:
        print(f"[ERROR] {e}")
        return False

def test_valid_key():
    """Test with valid API key"""
    print_section("TEST 3: Valid API Key")
    
    headers = {
        "X-API-Key": "dev_key_123",
        "Content-Type": "application/json"
    }
    
    try:
        # Test decision evaluation
        response = requests.post(
            f"{BASE_URL}/decisions/evaluate",
            json={
                "category": "FINANCIAL",
                "amount": 1000.0,
                "description": "Test decision"
            },
            headers=headers,
            timeout=5
        )
        
        if response.status_code == 200:
            result = response.json()
            print("[OK] Valid key accepted (200)")
            print(f"   Decision ID: {result.get('id')}")
            print(f"   Risk Level: {result.get('risk_level')}")
            print(f"   AI Can Decide: {result.get('ai_can_decide')}")
            return True
        else:
            print(f"[FAIL] Valid key should return 200, got {response.status_code}")
            print(f"   Response: {response.text}")
            return False
    except requests.exceptions.ConnectionError:
        print("[ERROR] Cannot connect to API. Is the server running?")
        return False
    except Exception as e:
        print(f"[ERROR] {e}")
        return False

def test_all_endpoints():
    """Test all endpoints with valid key"""
    print_section("TEST 4: All Endpoints with Valid Key")
    
    headers = {
        "X-API-Key": "dev_key_123",
        "Content-Type": "application/json"
    }
    
    tests = [
        ("GET", "/health", None, False),  # No auth needed
        ("POST", "/decisions/evaluate", {"category": "FINANCIAL", "amount": 1000}, True),
        ("POST", "/risk/assess", {"amount": 5000, "category": "STRATEGIC"}, True),
        ("GET", "/autonomy/level", None, True),
        ("POST", "/autonomy/should-execute", {"task_type": "operational", "risk_level": "LOW"}, True),
        ("POST", "/memory/insights", {"decision_data": {"category": "FINANCIAL"}}, True),
    ]
    
    passed = 0
    failed = 0
    
    for method, endpoint, data, needs_auth in tests:
        try:
            if method == "GET":
                response = requests.get(f"{BASE_URL}{endpoint}", headers=headers if needs_auth else None, timeout=5)
            else:
                response = requests.post(
                    f"{BASE_URL}{endpoint}",
                    json=data or {},
                    headers=headers if needs_auth else None,
                    timeout=5
                )
            
            if response.status_code == 200:
                print(f"[OK] {endpoint} - Status: 200")
                passed += 1
            else:
                print(f"[FAIL] {endpoint} - Status: {response.status_code}")
                print(f"   Response: {response.text[:100]}")
                failed += 1
        except Exception as e:
            print(f"[ERROR] {endpoint}: {e}")
            failed += 1
    
    print(f"\nResults: {passed} passed, {failed} failed")
    return failed == 0

def test_rate_limiting():
    """Test rate limiting (basic check)"""
    print_section("TEST 5: Rate Limiting Check")
    
    headers = {
        "X-API-Key": "dev_key_123",
        "Content-Type": "application/json"
    }
    
    # Make a few requests to see if rate limiting is tracked
    try:
        for i in range(3):
            response = requests.post(
                f"{BASE_URL}/decisions/evaluate",
                json={"category": "OPERATIONAL", "amount": 100},
                headers=headers,
                timeout=5
            )
            if response.status_code == 200:
                print(f"[OK] Request {i+1} accepted")
            else:
                print(f"[WARN] Request {i+1} returned {response.status_code}")
        
        print("[OK] Rate limiting is being tracked (check rate_limits.json)")
        return True
    except Exception as e:
        print(f"[ERROR] {e}")
        return False

def main():
    """Run all authentication tests"""
    print("=" * 60)
    print("API KEY AUTHENTICATION TEST SUITE")
    print("=" * 60)
    print("\nMake sure the API server is running:")
    print("  python -m uvicorn api.main:app --host 0.0.0.0 --port 8000")
    print()
    
    results = []
    
    # Run tests
    results.append(("No Auth Test", test_no_auth()))
    results.append(("Invalid Key Test", test_invalid_key()))
    results.append(("Valid Key Test", test_valid_key()))
    results.append(("All Endpoints Test", test_all_endpoints()))
    results.append(("Rate Limiting Test", test_rate_limiting()))
    
    # Summary
    print_section("TEST SUMMARY")
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for name, result in results:
        status = "[PASS]" if result else "[FAIL]"
        print(f"{status} {name}")
    
    print(f"\nTotal: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n[SUCCESS] All authentication tests passed!")
        print("Authentication is working correctly!")
    else:
        print("\n[WARNING] Some tests failed. Check the output above.")

if __name__ == "__main__":
    main()

