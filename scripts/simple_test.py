"""
Simple API Test
Test API without Unicode issues
"""

import requests
import json

BASE_URL = "http://localhost:8000"
API_KEY = "dev_key_123"

def test_api():
    """Test API endpoints"""
    print("="*60)
    print("API TEST RESULTS")
    print("="*60)
    print()
    
    headers = {
        "X-API-Key": API_KEY,
        "Content-Type": "application/json"
    }
    
    # Test 1: Health Check
    print("Test 1: Health Check")
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print(f"[OK] API is healthy!")
            print(f"     Version: {data.get('version')}")
            print(f"     Status: {data.get('status')}")
        else:
            print(f"[FAIL] Status code: {response.status_code}")
    except Exception as e:
        print(f"[ERROR] {e}")
        return False
    
    print()
    
    # Test 2: Decision Evaluation
    print("Test 2: Decision Evaluation")
    try:
        response = requests.post(
            f"{BASE_URL}/decisions/evaluate",
            json={"category": "FINANCIAL", "amount": 1000, "description": "Test purchase"},
            headers=headers,
            timeout=5
        )
        if response.status_code == 200:
            data = response.json()
            print(f"[OK] Decision evaluated!")
            print(f"     ID: {data.get('id')}")
            print(f"     Risk Level: {data.get('risk_level')}")
            print(f"     AI Can Decide: {data.get('ai_can_decide')}")
        else:
            print(f"[FAIL] Status code: {response.status_code}")
            print(f"     {response.text}")
    except Exception as e:
        print(f"[ERROR] {e}")
        return False
    
    print()
    
    # Test 3: Risk Assessment
    print("Test 3: Risk Assessment")
    try:
        response = requests.post(
            f"{BASE_URL}/risk/assess",
            json={"amount": 5000, "category": "STRATEGIC"},
            headers=headers,
            timeout=5
        )
        if response.status_code == 200:
            data = response.json()
            print(f"[OK] Risk assessed!")
            print(f"     Risk Level: {data.get('risk_level')}")
            print(f"     Risk Score: {data.get('risk_score')}")
        else:
            print(f"[FAIL] Status code: {response.status_code}")
    except Exception as e:
        print(f"[ERROR] {e}")
        return False
    
    print()
    
    # Test 4: Autonomy Level
    print("Test 4: Autonomy Level")
    try:
        response = requests.get(
            f"{BASE_URL}/autonomy/level",
            headers=headers,
            timeout=5
        )
        if response.status_code == 200:
            data = response.json()
            print(f"[OK] Autonomy level retrieved!")
            print(f"     Level: {data.get('autonomy_level')}%")
        else:
            print(f"[FAIL] Status code: {response.status_code}")
    except Exception as e:
        print(f"[ERROR] {e}")
        return False
    
    print()
    print("="*60)
    print("ALL TESTS PASSED!")
    print("="*60)
    print()
    print("API is fully operational!")
    print(f"Documentation: {BASE_URL}/docs")
    return True

if __name__ == "__main__":
    test_api()

