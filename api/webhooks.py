"""
Webhook Support
Send webhooks for important events
"""

from typing import Dict, Any, List, Optional
from datetime import datetime
import requests
import json
import logging
from enum import Enum

logger = logging.getLogger(__name__)

class WebhookEvent(str, Enum):
    """Webhook event types"""
    DECISION_EVALUATED = "decision.evaluated"
    RISK_ASSESSED = "risk.assessed"
    AUTONOMY_CHANGED = "autonomy.changed"
    KEY_GENERATED = "key.generated"
    KEY_DEACTIVATED = "key.deactivated"
    RATE_LIMIT_EXCEEDED = "rate_limit.exceeded"

class WebhookManager:
    """Manage webhook subscriptions and delivery"""
    
    def __init__(self):
        self.webhooks_file = "webhooks.json"
        self.webhooks = self._load_webhooks()
    
    def _load_webhooks(self) -> Dict[str, List[Dict[str, Any]]]:
        """Load webhook subscriptions"""
        try:
            import os
            if os.path.exists(self.webhooks_file):
                with open(self.webhooks_file, "r") as f:
                    return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            pass
        return {}
    
    def _save_webhooks(self):
        """Save webhook subscriptions"""
        try:
            with open(self.webhooks_file, "w") as f:
                json.dump(self.webhooks, f, indent=2)
        except Exception as e:
            logger.error(f"Error saving webhooks: {e}")
    
    def subscribe(self, event: WebhookEvent, url: str, secret: Optional[str] = None) -> str:
        """Subscribe to a webhook event"""
        if event.value not in self.webhooks:
            self.webhooks[event.value] = []
        
        subscription = {
            "id": f"wh_{datetime.now().timestamp()}",
            "url": url,
            "secret": secret,
            "created_at": datetime.now().isoformat(),
            "active": True
        }
        
        self.webhooks[event.value].append(subscription)
        self._save_webhooks()
        
        return subscription["id"]
    
    def unsubscribe(self, subscription_id: str) -> bool:
        """Unsubscribe from webhook"""
        for event, subscriptions in self.webhooks.items():
            for sub in subscriptions:
                if sub["id"] == subscription_id:
                    sub["active"] = False
                    self._save_webhooks()
                    return True
        return False
    
    async def send_webhook(
        self,
        event: WebhookEvent,
        data: Dict[str, Any],
        retry: bool = True
    ):
        """Send webhook for an event"""
        if event.value not in self.webhooks:
            return
        
        payload = {
            "event": event.value,
            "timestamp": datetime.now().isoformat(),
            "data": data
        }
        
        for subscription in self.webhooks[event.value]:
            if not subscription.get("active", True):
                continue
            
            try:
                headers = {
                    "Content-Type": "application/json",
                    "User-Agent": "AI-Decision-Engine-Webhook/1.0"
                }
                
                # Add signature if secret provided
                if subscription.get("secret"):
                    import hmac
                    import hashlib
                    signature = hmac.new(
                        subscription["secret"].encode(),
                        json.dumps(payload).encode(),
                        hashlib.sha256
                    ).hexdigest()
                    headers["X-Webhook-Signature"] = f"sha256={signature}"
                
                response = requests.post(
                    subscription["url"],
                    json=payload,
                    headers=headers,
                    timeout=5
                )
                
                if response.status_code == 200:
                    logger.info(f"Webhook delivered: {event.value} to {subscription['url']}")
                else:
                    logger.warning(f"Webhook failed: {event.value} to {subscription['url']} - {response.status_code}")
                    
            except Exception as e:
                logger.error(f"Error sending webhook: {e}")
                if retry:
                    # Could implement retry logic here
                    pass
    
    def list_webhooks(self, event: Optional[WebhookEvent] = None) -> Dict[str, Any]:
        """List webhook subscriptions"""
        if event:
            return {event.value: self.webhooks.get(event.value, [])}
        return self.webhooks

# Global webhook manager
webhook_manager = WebhookManager()

