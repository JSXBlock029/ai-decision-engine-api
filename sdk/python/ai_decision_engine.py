"""
API Client SDK
Python SDK for easy API integration
"""

import requests
from typing import Dict, Any, Optional, List
from datetime import datetime

class AIDecisionEngineClient:
    """Python SDK for AI Decision Engine API"""
    
    def __init__(self, api_key: str, base_url: str = "https://api.example.com"):
        """
        Initialize the API client
        
        Args:
            api_key: Your API key
            base_url: Base URL of the API (default: production)
        """
        self.api_key = api_key
        self.base_url = base_url.rstrip('/')
        self.headers = {
            "X-API-Key": api_key,
            "Content-Type": "application/json"
        }
    
    def health_check(self) -> Dict[str, Any]:
        """Check API health"""
        response = requests.get(f"{self.base_url}/health")
        response.raise_for_status()
        return response.json()
    
    def evaluate_decision(
        self,
        category: str,
        amount: float = 0.0,
        description: str = ""
    ) -> Dict[str, Any]:
        """
        Evaluate a decision
        
        Args:
            category: Decision category (STRATEGIC, OPERATIONAL, FINANCIAL, etc.)
            amount: Amount involved
            description: Decision description
        
        Returns:
            Decision evaluation result
        """
        response = requests.post(
            f"{self.base_url}/decisions/evaluate",
            json={
                "category": category,
                "amount": amount,
                "description": description
            },
            headers=self.headers
        )
        response.raise_for_status()
        return response.json()
    
    def assess_risk(
        self,
        amount: float,
        category: str = "OPERATIONAL",
        description: str = ""
    ) -> Dict[str, Any]:
        """
        Assess risk level
        
        Args:
            amount: Amount involved
            category: Decision category
            description: Risk assessment description
        
        Returns:
            Risk assessment result
        """
        response = requests.post(
            f"{self.base_url}/risk/assess",
            json={
                "amount": amount,
                "category": category,
                "description": description
            },
            headers=self.headers
        )
        response.raise_for_status()
        return response.json()
    
    def get_autonomy_level(self) -> Dict[str, Any]:
        """Get current AI autonomy level"""
        response = requests.get(
            f"{self.base_url}/autonomy/level",
            headers=self.headers
        )
        response.raise_for_status()
        return response.json()
    
    def should_execute(
        self,
        task_type: str,
        risk_level: str = "LOW"
    ) -> Dict[str, Any]:
        """
        Check if AI should auto-execute a task
        
        Args:
            task_type: Type of task
            risk_level: Risk level (LOW, MEDIUM, HIGH, CRITICAL)
        
        Returns:
            Auto-execute decision
        """
        response = requests.post(
            f"{self.base_url}/autonomy/should-execute",
            json={
                "task_type": task_type,
                "risk_level": risk_level
            },
            headers=self.headers
        )
        response.raise_for_status()
        return response.json()
    
    def get_memory_insights(self, decision_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Get memory insights
        
        Args:
            decision_data: Decision data for insights
        
        Returns:
            Memory insights
        """
        response = requests.post(
            f"{self.base_url}/memory/insights",
            json={"decision_data": decision_data},
            headers=self.headers
        )
        response.raise_for_status()
        return response.json()
    
    def get_analytics_stats(self, days: int = 30) -> Dict[str, Any]:
        """
        Get analytics statistics
        
        Args:
            days: Number of days to analyze
        
        Returns:
            Analytics statistics
        """
        response = requests.get(
            f"{self.base_url}/analytics/stats",
            params={"days": days},
            headers=self.headers
        )
        response.raise_for_status()
        return response.json()
    
    def list_api_keys(self) -> List[Dict[str, Any]]:
        """List all API keys (admin only)"""
        response = requests.get(
            f"{self.base_url}/api/keys/list",
            headers=self.headers
        )
        response.raise_for_status()
        return response.json()
    
    def generate_api_key(self, tier: str = "pro") -> Dict[str, Any]:
        """
        Generate a new API key (admin only)
        
        Args:
            tier: Key tier (free, dev, pro, enterprise)
        
        Returns:
            New API key information
        """
        response = requests.post(
            f"{self.base_url}/api/keys/generate",
            json={"tier": tier},
            headers=self.headers
        )
        response.raise_for_status()
        return response.json()

# Example usage
if __name__ == "__main__":
    # Initialize client
    client = AIDecisionEngineClient(
        api_key="your_api_key_here",
        base_url="http://localhost:8000"  # Use localhost for testing
    )
    
    # Check health
    health = client.health_check()
    print(f"API Status: {health['status']}")
    
    # Evaluate a decision
    decision = client.evaluate_decision(
        category="FINANCIAL",
        amount=1000.0,
        description="Purchase new equipment"
    )
    print(f"Decision ID: {decision['id']}")
    print(f"Risk Level: {decision['risk_level']}")
    
    # Assess risk
    risk = client.assess_risk(amount=5000, category="STRATEGIC")
    print(f"Risk Score: {risk['risk_score']}")

