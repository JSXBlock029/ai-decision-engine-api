"""
Stripe Payment Service
Handles subscription management, payment processing, and billing
"""

import os
import json
import logging
from typing import Dict, Any, Optional
from datetime import datetime
from pathlib import Path

logger = logging.getLogger(__name__)

# Try to import stripe, but handle if not installed
try:
    import stripe
    STRIPE_AVAILABLE = True
    # Set API key if available
    stripe_key = os.getenv("STRIPE_SECRET_KEY", "")
    if stripe_key:
        stripe.api_key = stripe_key
    else:
        logger.warning("Stripe module installed but API key not configured in environment variables.")
except ImportError:
    stripe = None
    STRIPE_AVAILABLE = False
    logger.warning("Stripe module not installed. Payment features will be disabled.")

STRIPE_WEBHOOK_SECRET = os.getenv("STRIPE_WEBHOOK_SECRET", "")

# Pricing tiers with hybrid model (flat rate + usage-based overage)
PRICING_TIERS = {
    "free": {
        "price_id": None,
        "amount": 0,  # $0/month
        "requests_per_month": 100,  # Included requests
        "overage_rate": None,  # No overage allowed (hard limit)
        "overage_per_1000": None,
        "name": "Free"
    },
    "pro": {
        "price_id": os.getenv("STRIPE_PRO_PRICE_ID", ""),
        "amount": 900,  # $9.00/month base
        "requests_per_month": 10000,  # Included requests
        "overage_rate": 0.001,  # $0.001 per request over limit
        "overage_per_1000": 100,  # $1.00 per 1,000 requests
        "name": "Pro"
    },
    "enterprise": {
        "price_id": os.getenv("STRIPE_ENTERPRISE_PRICE_ID", ""),
        "amount": 4900,  # $49.00/month base
        "requests_per_month": 1000000,  # Included requests (1M)
        "overage_rate": 0.0005,  # $0.0005 per request over limit (volume discount)
        "overage_per_1000": 50,  # $0.50 per 1,000 requests
        "name": "Enterprise"
    }
}

SUBSCRIPTIONS_FILE = os.getenv("SUBSCRIPTIONS_FILE", "subscriptions.json")


class StripeService:
    """Handle Stripe payment operations"""
    
    def __init__(self):
        self.subscriptions_file = SUBSCRIPTIONS_FILE
        self._ensure_file_exists()
    
    def _ensure_file_exists(self):
        """Ensure subscriptions file exists"""
        if not os.path.exists(self.subscriptions_file):
            with open(self.subscriptions_file, "w") as f:
                json.dump({}, f)
    
    def _load_subscriptions(self) -> Dict[str, Any]:
        """Load subscriptions from file"""
        try:
            with open(self.subscriptions_file, "r") as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return {}
    
    def _save_subscriptions(self, subscriptions: Dict[str, Any]):
        """Save subscriptions to file"""
        with open(self.subscriptions_file, "w") as f:
            json.dump(subscriptions, f, indent=2)
    
    def create_checkout_session(
        self, 
        customer_email: str, 
        tier: str = "pro",
        success_url: str = None,
        cancel_url: str = None
    ) -> Dict[str, Any]:
        """
        Create Stripe checkout session for subscription
        
        Args:
            customer_email: Customer email
            tier: Subscription tier (pro, enterprise)
            success_url: URL to redirect after successful payment
            cancel_url: URL to redirect after cancelled payment
        
        Returns:
            Checkout session object
        """
        if not STRIPE_AVAILABLE:
            raise ValueError("Stripe module not installed. Please install stripe package.")
        
        if not stripe.api_key:
            raise ValueError("Stripe API key not configured")
        
        tier_info = PRICING_TIERS.get(tier.lower())
        if not tier_info:
            raise ValueError(f"Invalid tier: {tier}. Valid tiers are: pro, enterprise")
        
        # If price_id is not set, try to get it from environment or create it
        if not tier_info.get("price_id"):
            # Try to get from environment variable
            env_var_name = f"STRIPE_{tier.upper()}_PRICE_ID"
            price_id = os.getenv(env_var_name, "")
            if price_id:
                tier_info["price_id"] = price_id
            else:
                raise ValueError(f"Price ID not configured for {tier} tier. Please set {env_var_name} environment variable or create product in Stripe.")
        
        try:
            # Create checkout session
            session = stripe.checkout.Session.create(
                customer_email=customer_email,
                payment_method_types=["card"],
                line_items=[{
                    "price": tier_info["price_id"],
                    "quantity": 1,
                }],
                mode="subscription",
                success_url=success_url or f"{os.getenv('API_BASE_URL', 'https://web-production-62146.up.railway.app')}/payment/success?session_id={{CHECKOUT_SESSION_ID}}",
                cancel_url=cancel_url or f"{os.getenv('API_BASE_URL', 'https://web-production-62146.up.railway.app')}/payment/cancel",
                metadata={
                    "tier": tier,
                    "customer_email": customer_email
                }
            )
            
            logger.info(f"Created checkout session for {customer_email}, tier: {tier}")
            return {
                "session_id": session.id,
                "url": session.url,
                "tier": tier
            }
        except stripe.error.StripeError as e:
            logger.error(f"Stripe error creating checkout session: {e}")
            raise
    
    def get_subscription(self, subscription_id: str) -> Optional[Dict[str, Any]]:
        """Get subscription from Stripe"""
        if not STRIPE_AVAILABLE or not stripe.api_key:
            return None
        
        try:
            subscription = stripe.Subscription.retrieve(subscription_id)
            return {
                "id": subscription.id,
                "status": subscription.status,
                "customer": subscription.customer,
                "current_period_end": subscription.current_period_end,
                "tier": subscription.metadata.get("tier", "pro"),
                "cancel_at_period_end": subscription.cancel_at_period_end
            }
        except stripe.error.StripeError as e:
            logger.error(f"Error retrieving subscription: {e}")
            return None
    
    def cancel_subscription(self, subscription_id: str) -> bool:
        """Cancel a subscription"""
        if not STRIPE_AVAILABLE or not stripe.api_key:
            return False
        
        try:
            subscription = stripe.Subscription.modify(
                subscription_id,
                cancel_at_period_end=True
            )
            return True
        except stripe.error.StripeError as e:
            logger.error(f"Error cancelling subscription: {e}")
            return False
    
    def link_subscription_to_api_key(
        self, 
        api_key: str, 
        subscription_id: str,
        customer_email: str,
        tier: str
    ):
        """Link a Stripe subscription to an API key"""
        subscriptions = self._load_subscriptions()
        
        subscriptions[subscription_id] = {
            "api_key": api_key,
            "customer_email": customer_email,
            "tier": tier,
            "created_at": datetime.now().isoformat(),
            "status": "active"
        }
        
        self._save_subscriptions(subscriptions)
        logger.info(f"Linked subscription {subscription_id} to API key {api_key[:10]}...")
    
    def get_api_key_from_subscription(self, subscription_id: str) -> Optional[str]:
        """Get API key associated with subscription"""
        subscriptions = self._load_subscriptions()
        sub = subscriptions.get(subscription_id)
        return sub.get("api_key") if sub else None
    
    def update_subscription_status(self, subscription_id: str, status: str):
        """Update subscription status"""
        subscriptions = self._load_subscriptions()
        if subscription_id in subscriptions:
            subscriptions[subscription_id]["status"] = status
            subscriptions[subscription_id]["updated_at"] = datetime.now().isoformat()
            self._save_subscriptions(subscriptions)
    
    def calculate_overage(self, tier: str, overage_requests: int) -> float:
        """
        Calculate overage charges for a tier
        
        Args:
            tier: Subscription tier
            overage_requests: Number of requests over the included limit
        
        Returns:
            Overage charge in dollars
        """
        if overage_requests <= 0:
            return 0.0
        
        tier_info = PRICING_TIERS.get(tier.lower())
        if not tier_info:
            return 0.0
        
        overage_rate = tier_info.get("overage_rate")
        if overage_rate is None:
            return 0.0
        
        return overage_requests * overage_rate
    
    def get_billing_summary(self, api_key: str, usage_stats: Dict[str, Any]) -> Dict[str, Any]:
        """
        Get billing summary including base subscription and overage
        
        Args:
            api_key: API key
            usage_stats: Usage statistics from APIKeyManager
        
        Returns:
            Billing summary with base price, overage, and total
        """
        tier = usage_stats.get("tier", "free")
        overage_requests = usage_stats.get("overage_requests", 0)
        
        tier_info = PRICING_TIERS.get(tier.lower(), {})
        base_price = tier_info.get("amount", 0) / 100  # Convert cents to dollars
        overage_charge = self.calculate_overage(tier, overage_requests)
        
        return {
            "tier": tier,
            "base_price": base_price,
            "included_requests": usage_stats.get("max_requests", 0),
            "total_requests": usage_stats.get("total_requests", 0),
            "overage_requests": overage_requests,
            "overage_charge": round(overage_charge, 2),
            "total_charge": round(base_price + overage_charge, 2),
            "month": usage_stats.get("month", "")
        }
    
    def verify_webhook(self, payload: bytes, signature: str) -> Optional[Dict[str, Any]]:
        """Verify Stripe webhook signature"""
        if not STRIPE_AVAILABLE:
            logger.warning("Stripe module not installed")
            return None
        
        if not STRIPE_WEBHOOK_SECRET:
            logger.warning("Stripe webhook secret not configured")
            return None
        
        try:
            event = stripe.Webhook.construct_event(
                payload, signature, STRIPE_WEBHOOK_SECRET
            )
            return event
        except ValueError as e:
            logger.error(f"Invalid payload: {e}")
            return None
        except stripe.error.SignatureVerificationError as e:
            logger.error(f"Invalid signature: {e}")
            return None


# Global instance
stripe_service = StripeService()

