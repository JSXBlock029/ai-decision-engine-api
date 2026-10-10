"""
Test script for AI Decision Engine API
Tests all endpoints to ensure they work correctly
"""

import requests
import json
from typing import Dict, Any

BASE_URL = "http://localhost:8000"
API_KEY = "dev_key_123"  # Development API key

headers = {
    "X-API-Key": API_KEY,
    "Content-Type": "application/json"
}

def test_health_check():
    """Test health check endpoint"""
    print("🔍 Testing /health endpoint...")
    try:
        response = requests.get(f"{BASE_URL}/health")
        print(f"   Status: {response.status_code}")
        print(f"   Response: {response.json()}")
        return response.status_code == 200
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False

def test_evaluate_decision():
    """Test decision evaluation endpoint"""
    print("\n🔍 Testing /decisions/evaluate endpoint...")
    try:
        decision_data = {
            "category": "FINANCIAL",
            "amount": 1000,
            "description": "Invest in marketing campaign"
        }
        
        response = requests.post(
            f"{BASE_URL}/decisions/evaluate",
            json=decision_data,
            headers=headers
        )
        
        print(f"   Status: {response.status_code}")
        result = response.json()
        print(f"   Decision ID: {result.get('id')}")
        print(f"   Risk Level: {result.get('risk_level')}")
        print(f"   AI Can Decide: {result.get('ai_can_decide')}")
        print(f"   Action Required: {result.get('action_required')}")
        return response.status_code == 200
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False

def test_assess_risk():
    """Test risk assessment endpoint"""
    print("\n🔍 Testing /risk/assess endpoint...")
    try:
        risk_data = {
            "amount": 5000,
            "category": "STRATEGIC",
            "description": "Launch new product line"
        }
        
        response = requests.post(
            f"{BASE_URL}/risk/assess",
            json=risk_data,
            headers=headers
        )
        
        print(f"   Status: {response.status_code}")
        result = response.json()
        print(f"   Risk Level: {result.get('risk_level')}")
        print(f"   Risk Score: {result.get('risk_score')}")
        print(f"   Recommendation: {result.get('recommendation')}")
        return response.status_code == 200
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False

def test_get_autonomy_level():
    """Test autonomy level endpoint"""
    print("\n🔍 Testing /autonomy/level endpoint...")
    try:
        response = requests.get(
            f"{BASE_URL}/autonomy/level",
            headers=headers
        )
        
        print(f"   Status: {response.status_code}")
        result = response.json()
        print(f"   Autonomy Level: {result.get('autonomy_level')}%")
        print(f"   AI Tasks: {len(result.get('ai_tasks', []))}")
        print(f"   Human Tasks: {len(result.get('human_tasks', []))}")
        return response.status_code == 200
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False

def test_should_auto_execute():
    """Test should auto-execute endpoint"""
    print("\n🔍 Testing /autonomy/should-execute endpoint...")
    try:
        execute_data = {
            "task_type": "operational",
            "risk_level": "LOW"
        }
        
        response = requests.post(
            f"{BASE_URL}/autonomy/should-execute",
            json=execute_data,
            headers=headers
        )
        
        print(f"   Status: {response.status_code}")
        result = response.json()
        print(f"   Should Execute: {result.get('should_execute')}")
        print(f"   Reason: {result.get('reason')}")
        return response.status_code == 200
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False

def test_memory_insights():
    """Test memory insights endpoint"""
    print("\n🔍 Testing /memory/insights endpoint...")
    try:
        memory_data = {
            "decision_data": {
                "category": "FINANCIAL",
                "amount": 1000
            }
        }
        
        response = requests.post(
            f"{BASE_URL}/memory/insights",
            json=memory_data,
            headers=headers
        )
        
        print(f"   Status: {response.status_code}")
        result = response.json()
        similar_decisions = result.get('similar_decisions', 0)
        if isinstance(similar_decisions, int):
            print(f"   Similar Decisions: {similar_decisions}")
        else:
            print(f"   Similar Decisions: {len(similar_decisions) if isinstance(similar_decisions, list) else 0}")
        print(f"   Recommendations: {result.get('recommendations', [])}")
        return response.status_code == 200
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False

def main():
    """Run all tests"""
    print("=" * 60)
    print("AI DECISION ENGINE API - TEST SUITE")
    print("=" * 60)
    print(f"Base URL: {BASE_URL}")
    print(f"API Key: {API_KEY[:10]}...")
    print("\n")
    
    tests = [
        ("Health Check", test_health_check),
        ("Evaluate Decision", test_evaluate_decision),
        ("Assess Risk", test_assess_risk),
        ("Get Autonomy Level", test_get_autonomy_level),
        ("Should Auto-Execute", test_should_auto_execute),
        ("Memory Insights", test_memory_insights)
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"   ❌ Test failed with exception: {e}")
            results.append((test_name, False))
    
    print("\n" + "=" * 60)
    print("TEST RESULTS")
    print("=" * 60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status}: {test_name}")
    
    print(f"\nTotal: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 All tests passed! API is ready for deployment.")
    else:
        print(f"\n⚠️  {total - passed} test(s) failed. Review errors above.")

if __name__ == "__main__":
    main()
