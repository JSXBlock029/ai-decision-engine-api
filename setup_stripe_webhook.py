"""
Script to create Stripe webhook endpoint programmatically
Run this if you can't access webhooks in the Stripe dashboard
"""

import os
import sys

try:
    import stripe
except ImportError:
    print("❌ Stripe module not installed. Install with: pip install stripe")
    sys.exit(1)

# Get API key from environment or prompt
stripe_key = os.getenv("STRIPE_SECRET_KEY", "")
if not stripe_key:
    stripe_key = input("Enter your Stripe Secret Key (sk_test_... or sk_live_...): ").strip()
    if not stripe_key:
        print("❌ Stripe key required")
        sys.exit(1)

stripe.api_key = stripe_key

# Webhook configuration
WEBHOOK_URL = "https://web-production-62146.up.railway.app/webhooks/stripe"
EVENTS = [
    "checkout.session.completed",
    "customer.subscription.updated",
    "customer.subscription.deleted"
]

print(f"\n🚀 Creating Stripe webhook endpoint...")
print(f"   URL: {WEBHOOK_URL}")
print(f"   Events: {', '.join(EVENTS)}\n")

try:
    # Create webhook endpoint
    webhook = stripe.WebhookEndpoint.create(
        url=WEBHOOK_URL,
        enabled_events=EVENTS,
        description="AI Decision Engine API - Subscription events"
    )
    
    print("✅ Webhook created successfully!\n")
    print(f"📋 Webhook Details:")
    print(f"   ID: {webhook.id}")
    print(f"   URL: {webhook.url}")
    print(f"   Status: {webhook.status}")
    print(f"   Events: {len(webhook.enabled_events)} events")
    
    # Get signing secret
    if hasattr(webhook, 'secret') and webhook.secret:
        signing_secret = webhook.secret
    else:
        # Retrieve the signing secret separately
        signing_secret = stripe.WebhookEndpoint.retrieve(webhook.id).secret
    
    print(f"\n🔑 Signing Secret:")
    print(f"   {signing_secret}")
    print(f"\n⚠️  IMPORTANT: Copy this signing secret!")
    print(f"   Add it to Railway as: STRIPE_WEBHOOK_SECRET")
    print(f"\n📝 Next steps:")
    print(f"   1. Copy the signing secret above")
    print(f"   2. Go to Railway → Your service → Variables")
    print(f"   3. Add: STRIPE_WEBHOOK_SECRET = {signing_secret}")
    print(f"   4. Railway will auto-redeploy")
    
except stripe.error.StripeError as e:
    print(f"❌ Error creating webhook: {e}")
    print(f"\n💡 Alternative: Try accessing webhooks directly:")
    print(f"   Test mode: https://dashboard.stripe.com/test/webhooks")
    print(f"   Live mode: https://dashboard.stripe.com/webhooks")
    sys.exit(1)


