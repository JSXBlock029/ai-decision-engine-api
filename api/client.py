"""
Python SDK for AI Decision Engine API
Easy-to-use client library for integrating with the API
"""

import requests
from typing import Dict, Any, Optional, List
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class AIDecisionAPIClient:
    """Python client for AI Decision Engine API"""
    
    def __init__(self, api_key: str, base_url: str = "http://localhost:8000"):
        """
        Initialize API client
        
        Args:
            api_key: Your API key
            base_url: API base URL (default: http://localhost:8000)
        """
        self.api_key = api_key
        self.base_url = base_url.rstrip('/')
        self.headers = {
            "X-API-Key": api_key,
            "Content-Type": "application/json"
        }
        self.session = requests.Session()
        self.session.headers.update(self.headers)
    
    def health_check(self) -> Dict[str, Any]:
        """Check API health"""
        try:
            response = self.session.get(f"{self.base_url}/health", timeout=10)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"Health check failed: {e}")
            raise
    
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
        data = {
            "category": category.upper(),
            "amount": amount,
            "description": description
        }
        
        try:
            response = self.session.post(
                f"{self.base_url}/decisions/evaluate",
                json=data,
                timeout=10
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"Decision evaluation failed: {e}")
            raise
    
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
        data = {
            "amount": amount,
            "category": category.upper(),
            "description": description
        }
        
        try:
            response = self.session.post(
                f"{self.base_url}/risk/assess",
                json=data,
                timeout=10
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"Risk assessment failed: {e}")
            raise
    
    def get_autonomy_level(self) -> Dict[str, Any]:
        """Get current AI autonomy level"""
        try:
            response = self.session.get(
                f"{self.base_url}/autonomy/level",
                timeout=10
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to get autonomy level: {e}")
            raise
    
    def should_auto_execute(
        self,
        task_type: str,
        risk_level: str = "LOW"
    ) -> Dict[str, Any]:
        """
        Check if AI should auto-execute
        
        Args:
            task_type: Type of task
            risk_level: Risk level (LOW, MEDIUM, HIGH, CRITICAL)
        
        Returns:
            Auto-execute decision
        """
        data = {
            "task_type": task_type,
            "risk_level": risk_level.upper()
        }
        
        try:
            response = self.session.post(
                f"{self.base_url}/autonomy/should-execute",
                json=data,
                timeout=10
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"Auto-execute check failed: {e}")
            raise
    
    def get_memory_insights(self, decision_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Get memory insights
        
        Args:
            decision_data: Decision data dictionary
        
        Returns:
            Memory insights
        """
        data = {"decision_data": decision_data}
        
        try:
            response = self.session.post(
                f"{self.base_url}/memory/insights",
                json=data,
                timeout=10
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"Memory insights failed: {e}")
            raise

# Example usage
if __name__ == "__main__":
    # Initialize client
    client = AIDecisionAPIClient(
        api_key="dev_key_123",
        base_url="http://localhost:8000"
    )
    
    # Check health
    print("Checking API health...")
    health = client.health_check()
    print(f"API Status: {health.get('status')}")
    
    # Evaluate a decision
    print("\nEvaluating decision...")
    decision = client.evaluate_decision(
        category="FINANCIAL",
        amount=1000.0,
        description="Test decision"
    )
    print(f"Risk Level: {decision.get('risk_level')}")
    print(f"AI Can Decide: {decision.get('ai_can_decide')}")
    
    # Get autonomy level
    print("\nGetting autonomy level...")
    autonomy = client.get_autonomy_level()
    print(f"Autonomy: {autonomy.get('autonomy_level')}%")

