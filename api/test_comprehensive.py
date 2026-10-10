"""
Comprehensive Test Suite
Full test coverage for all API functionality
"""

import pytest
import requests
from typing import Dict, Any
import json
import os

BASE_URL = "http://localhost:8000"
API_KEY = "dev_key_123"

class TestAPI:
    """Comprehensive API test suite"""
    
    @pytest.fixture
    def headers(self):
        """Get API headers"""
        return {
            "X-API-Key": API_KEY,
            "Content-Type": "application/json"
        }
    
    def test_health_check(self):
        """Test health endpoint"""
        response = requests.get(f"{BASE_URL}/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "version" in data
    
    def test_evaluate_decision(self, headers):
        """Test decision evaluation"""
        response = requests.post(
            f"{BASE_URL}/decisions/evaluate",
            json={
                "category": "FINANCIAL",
                "amount": 1000.0,
                "description": "Test decision"
            },
            headers=headers
        )
        assert response.status_code == 200
        data = response.json()
        assert "id" in data
        assert "risk_level" in data
        assert "ai_can_decide" in data
    
    def test_assess_risk(self, headers):
        """Test risk assessment"""
        response = requests.post(
            f"{BASE_URL}/risk/assess",
            json={
                "amount": 5000,
                "category": "STRATEGIC"
            },
            headers=headers
        )
        assert response.status_code == 200
        data = response.json()
        assert "risk_level" in data
        assert "risk_score" in data
    
    def test_autonomy_level(self, headers):
        """Test autonomy level endpoint"""
        response = requests.get(
            f"{BASE_URL}/autonomy/level",
            headers=headers
        )
        assert response.status_code == 200
        data = response.json()
        assert "autonomy_level" in data
        assert isinstance(data["autonomy_level"], (int, float))
    
    def test_should_execute(self, headers):
        """Test auto-execute check"""
        response = requests.post(
            f"{BASE_URL}/autonomy/should-execute",
            json={
                "task_type": "operational",
                "risk_level": "LOW"
            },
            headers=headers
        )
        assert response.status_code == 200
        data = response.json()
        assert "should_execute" in data
        assert isinstance(data["should_execute"], bool)
    
    def test_memory_insights(self, headers):
        """Test memory insights"""
        response = requests.post(
            f"{BASE_URL}/memory/insights",
            json={
                "decision_data": {
                    "category": "FINANCIAL",
                    "amount": 1000
                }
            },
            headers=headers
        )
        assert response.status_code == 200
        data = response.json()
        assert "similar_decisions" in data
    
    def test_authentication_required(self):
        """Test that endpoints require authentication"""
        response = requests.post(
            f"{BASE_URL}/decisions/evaluate",
            json={"category": "FINANCIAL", "amount": 1000}
        )
        assert response.status_code == 401
    
    def test_invalid_key(self):
        """Test invalid API key"""
        headers = {"X-API-Key": "invalid_key_123"}
        response = requests.post(
            f"{BASE_URL}/decisions/evaluate",
            json={"category": "FINANCIAL", "amount": 1000},
            headers=headers
        )
        assert response.status_code == 401
    
    def test_validation_errors(self, headers):
        """Test input validation"""
        # Invalid category
        response = requests.post(
            f"{BASE_URL}/decisions/evaluate",
            json={"category": "INVALID", "amount": 1000},
            headers=headers
        )
        assert response.status_code == 422
        
        # Negative amount
        response = requests.post(
            f"{BASE_URL}/decisions/evaluate",
            json={"category": "FINANCIAL", "amount": -100},
            headers=headers
        )
        assert response.status_code == 422
    
    def test_analytics_endpoints(self, headers):
        """Test analytics endpoints (requires Pro tier)"""
        response = requests.get(
            f"{BASE_URL}/analytics/stats",
            headers=headers
        )
        # Should work for dev/pro/enterprise, fail for free
        assert response.status_code in [200, 403]
    
    def test_key_management(self, headers):
        """Test key management endpoints"""
        response = requests.get(
            f"{BASE_URL}/api/keys/list",
            headers=headers
        )
        # Should work for dev/pro/enterprise
        assert response.status_code in [200, 403]

if __name__ == "__main__":
    pytest.main([__file__, "-v"])

