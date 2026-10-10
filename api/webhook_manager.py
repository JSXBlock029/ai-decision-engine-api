"""
Webhook Implementation
Complete webhook system for real-time notifications
"""

import json
import requests
import hmac
import hashlib
from typing import Dict, List, Any, Optional
from datetime import datetime
from pathlib import Path

class WebhookManager:
    """Manage webhook subscriptions and delivery"""
    
    def __init__(self):
        self.webhooks_file = "webhooks.json"
        self.webhooks = self._load_webhooks()
    
    def _load_webhooks(self) -> List[Dict[str, Any]]:
        """Load webhooks from file"""
        try:
            if Path(self.webhooks_file).exists():
                with open(self.webhooks_file, "r") as f:
                    return json.load(f)
        except:
            pass
        return []
    
    def _save_webhooks(self):
        """Save webhooks to file"""
        with open(self.webhooks_file, "w") as f:
            json.dump(self.webhooks, f, indent=2)
    
    def subscribe(self, url: str, events: List[str], secret: Optional[str] = None) -> str:
        """
        Subscribe to webhook events
        
        Args:
            url: Webhook URL
            events: List of events to subscribe to
            secret: Optional secret for signature verification
        
        Returns:
            Webhook ID
        """
        webhook_id = f"wh_{datetime.now().strftime('%Y%m%d%H%M%S')}"
        
        webhook = {
            "id": webhook_id,
            "url": url,
            "events": events,
            "secret": secret,
            "active": True,
            "created_at": datetime.now().isoformat(),
            "last_triggered": None,
            "failure_count": 0
        }
        
        self.webhooks.append(webhook)
        self._save_webhooks()
        
        return webhook_id
    
    def unsubscribe(self, webhook_id: str) -> bool:
        """Unsubscribe from webhook"""
        for webhook in self.webhooks:
            if webhook["id"] == webhook_id:
                webhook["active"] = False
                self._save_webhooks()
                return True
        return False
    
    def _generate_signature(self, payload: str, secret: str) -> str:
        """Generate HMAC signature"""
        return hmac.new(
            secret.encode(),
            payload.encode(),
            hashlib.sha256
        ).hexdigest()
    
    def trigger(self, event: str, data: Dict[str, Any]):
        """
        Trigger webhook for an event
        
        Args:
            event: Event name
            data: Event data
        """
        payload = {
            "event": event,
            "data": data,
            "timestamp": datetime.now().isoformat()
        }
        
        payload_str = json.dumps(payload)
        
        for webhook in self.webhooks:
            if not webhook["active"]:
                continue
            
            if event not in webhook["events"]:
                continue
            
            try:
                headers = {
                    "Content-Type": "application/json",
                    "X-Webhook-Event": event
                }
                
                # Add signature if secret exists
                if webhook.get("secret"):
                    signature = self._generate_signature(payload_str, webhook["secret"])
                    headers["X-Webhook-Signature"] = f"sha256={signature}"
                
                response = requests.post(
                    webhook["url"],
                    json=payload,
                    headers=headers,
                    timeout=5
                )
                
                response.raise_for_status()
                
                # Update webhook status
                webhook["last_triggered"] = datetime.now().isoformat()
                webhook["failure_count"] = 0
                
            except Exception as e:
                webhook["failure_count"] = webhook.get("failure_count", 0) + 1
                
                # Deactivate after 5 failures
                if webhook["failure_count"] >= 5:
                    webhook["active"] = False
                
                print(f"Webhook {webhook['id']} failed: {e}")
        
        self._save_webhooks()
    
    def list_webhooks(self) -> List[Dict[str, Any]]:
        """List all webhooks"""
        return self.webhooks
    
    def get_webhook(self, webhook_id: str) -> Optional[Dict[str, Any]]:
        """Get webhook by ID"""
        for webhook in self.webhooks:
            if webhook["id"] == webhook_id:
                return webhook
        return None

# Global webhook manager instance
webhook_manager = WebhookManager()

# Event types
EVENT_DECISION_EVALUATED = "decision.evaluated"
EVENT_RISK_ASSESSED = "risk.assessed"
EVENT_AUTONOMY_CHANGED = "autonomy.changed"
EVENT_RATE_LIMIT_EXCEEDED = "rate_limit.exceeded"
EVENT_ERROR_OCCURRED = "error.occurred"

def trigger_webhook(event: str, data: Dict[str, Any]):
    """Trigger webhook for an event"""
    webhook_manager.trigger(event, data)

if __name__ == "__main__":
    # Example usage
    manager = WebhookManager()
    
    # Subscribe to events
    webhook_id = manager.subscribe(
        url="https://example.com/webhook",
        events=[EVENT_DECISION_EVALUATED, EVENT_RISK_ASSESSED],
        secret="your_secret_key"
    )
    
    print(f"Webhook subscribed: {webhook_id}")
    
    # Trigger event
    manager.trigger(EVENT_DECISION_EVALUATED, {
        "decision_id": "dec_123",
        "risk_level": "LOW"
    })

