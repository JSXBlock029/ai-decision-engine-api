"""
Testing Framework
Comprehensive testing utilities and fixtures
"""

import pytest
import requests
from typing import Dict, Any
import json
from pathlib import Path

class APITestClient:
    """Test client for API testing"""
    
    def __init__(self, base_url: str = "http://localhost:8000", api_key: str = "dev_key_123"):
        self.base_url = base_url.rstrip('/')
        self.api_key = api_key
        self.headers = {
            "X-API-Key": api_key,
            "Content-Type": "application/json"
        }
    
    def health(self) -> Dict[str, Any]:
        """Check health"""
        response = requests.get(f"{self.base_url}/health")
        return response.json()
    
    def evaluate_decision(self, category: str, amount: float = 0, description: str = "") -> Dict[str, Any]:
        """Evaluate decision"""
        response = requests.post(
            f"{self.base_url}/decisions/evaluate",
            json={"category": category, "amount": amount, "description": description},
            headers=self.headers
        )
        response.raise_for_status()
        return response.json()
    
    def assess_risk(self, amount: float, category: str = "OPERATIONAL") -> Dict[str, Any]:
        """Assess risk"""
        response = requests.post(
            f"{self.base_url}/risk/assess",
            json={"amount": amount, "category": category},
            headers=self.headers
        )
        response.raise_for_status()
        return response.json()

@pytest.fixture
def api_client():
    """API test client fixture"""
    return APITestClient()

@pytest.fixture
def test_api_key():
    """Test API key"""
    return "dev_key_123"

class TestAPIHealth:
    """Health check tests"""
    
    def test_health_endpoint(self, api_client):
        """Test health endpoint"""
        result = api_client.health()
        assert result["status"] == "healthy"
        assert "version" in result

class TestDecisionEvaluation:
    """Decision evaluation tests"""
    
    def test_evaluate_financial_decision(self, api_client):
        """Test financial decision evaluation"""
        result = api_client.evaluate_decision(
            category="FINANCIAL",
            amount=1000.0,
            description="Test purchase"
        )
        assert "id" in result
        assert "risk_level" in result
        assert result["category"] == "FINANCIAL"
    
    def test_evaluate_operational_decision(self, api_client):
        """Test operational decision evaluation"""
        result = api_client.evaluate_decision(
            category="OPERATIONAL",
            amount=500.0
        )
        assert "id" in result
        assert "ai_can_decide" in result

class TestRiskAssessment:
    """Risk assessment tests"""
    
    def test_assess_low_risk(self, api_client):
        """Test low risk assessment"""
        result = api_client.assess_risk(amount=100, category="OPERATIONAL")
        assert "risk_level" in result
        assert "risk_score" in result
    
    def test_assess_high_risk(self, api_client):
        """Test high risk assessment"""
        result = api_client.assess_risk(amount=100000, category="STRATEGIC")
        assert "risk_level" in result
        assert result["risk_score"] > 0

class TestAuthentication:
    """Authentication tests"""
    
    def test_missing_api_key(self):
        """Test request without API key"""
        response = requests.post(
            "http://localhost:8000/decisions/evaluate",
            json={"category": "FINANCIAL", "amount": 1000}
        )
        assert response.status_code == 401
    
    def test_invalid_api_key(self):
        """Test request with invalid API key"""
        response = requests.post(
            "http://localhost:8000/decisions/evaluate",
            json={"category": "FINANCIAL", "amount": 1000},
            headers={"X-API-Key": "invalid_key"}
        )
        assert response.status_code == 401

# Test configuration
def pytest_configure(config):
    """Configure pytest"""
    config.addinivalue_line(
        "markers", "integration: marks tests as integration tests"
    )

if __name__ == "__main__":
    pytest.main([__file__, "-v"])

