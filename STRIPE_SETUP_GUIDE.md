# Stripe Integration Setup Guide

## Overview

Stripe payment processing has been integrated into the AI Decision Engine API. This guide will help you set up Stripe to enable paid subscriptions.

---

## Step 1: Create Stripe Account

1. Go to [https://stripe.com](https://stripe.com)
2. Sign up for a free account
3. Complete account verification (if required)

**Cost:** Free to set up. Stripe charges 2.9% + $0.30 per transaction.

---

## Step 2: Get API Keys

1. Log into Stripe Dashboard
2. Go to **Developers** → **API keys**
3. Copy your **Publishable key** and **Secret key**
   - Use **Test mode** keys for development
   - Use **Live mode** keys for production

---

## Step 3: Create Products and Prices

### Create Pro Tier Product

1. Go to **Products** in Stripe Dashboard
2. Click **Add product**
3. Set up:
   - **Name:** Pro Plan
   - **Description:** 10,000 requests/month
   - **Pricing:** $9.00/month (recurring)
   - **Billing period:** Monthly
4. Copy the **Price ID** (starts with `price_`)

### Create Enterprise Tier Product

1. Click **Add product** again
2. Set up:
   - **Name:** Enterprise Plan
   - **Description:** Unlimited requests/month
   - **Pricing:** $49.00/month (recurring)
   - **Billing period:** Monthly
3. Copy the **Price ID** (starts with `price_`)

---

## Step 4: Set Environment Variables

Add these environment variables to your Railway deployment (or local `.env` file):

```bash
# Stripe API Keys
STRIPE_SECRET_KEY=sk_test_...  # Your Stripe secret key
STRIPE_WEBHOOK_SECRET=whsec_...  # Webhook secret (see Step 5)

# Stripe Price IDs
STRIPE_PRO_PRICE_ID=price_...  # Pro tier price ID
STRIPE_ENTERPRISE_PRICE_ID=price_...  # Enterprise tier price ID

# API Base URL (for redirects)
API_BASE_URL=https://web-production-62146.up.railway.app
```

### Setting Environment Variables in Railway

1. Go to your Railway project
2. Click on your service
3. Go to **Variables** tab
4. Add each environment variable
5. Redeploy your service

---

## Step 5: Set Up Webhooks

Webhooks allow Stripe to notify your API about subscription events.

### Create Webhook Endpoint

1. In Stripe Dashboard, go to **Developers** → **Webhooks**
2. Click **Add endpoint**
3. Set **Endpoint URL:** `https://web-production-62146.up.railway.app/webhooks/stripe`
4. Select events to listen for:
   - `checkout.session.completed`
   - `customer.subscription.updated`
   - `customer.subscription.deleted`
5. Copy the **Signing secret** (starts with `whsec_`)
6. Add it to your environment variables as `STRIPE_WEBHOOK_SECRET`

---

## Step 6: Test the Integration

### Test Checkout Flow

1. Visit your pricing page: `https://web-production-62146.up.railway.app/pricing`
2. Click "Subscribe Now" on Pro or Enterprise
3. Use Stripe test card: `4242 4242 4242 4242`
4. Use any future expiry date and any CVC
5. Complete checkout
6. Verify API key is generated and linked to subscription

### Test Webhooks Locally (Optional)

If testing locally, use Stripe CLI:

```bash
# Install Stripe CLI
# https://stripe.com/docs/stripe-cli

# Forward webhooks to local server
stripe listen --forward-to localhost:8000/webhooks/stripe
```

---

## Step 7: Verify Integration

### Check Endpoints

1. **Pricing endpoint:**
   ```bash
   curl https://web-production-62146.up.railway.app/pricing
   ```

2. **Create checkout session:**
   ```bash
   curl -X POST https://web-production-62146.up.railway.app/payment/checkout \
     -H "Content-Type: application/json" \
     -d '{"email": "test@example.com", "tier": "pro"}'
   ```

3. **Check subscription status:**
   ```bash
   curl https://web-production-62146.up.railway.app/subscription/status \
     -H "X-API-Key: YOUR_API_KEY"
   ```

---

## Pricing Configuration

Current pricing tiers are defined in `api/stripe_service.py`:

```python
PRICING_TIERS = {
    "free": {
        "price_id": None,
        "amount": 0,
        "requests_per_month": 100,
        "name": "Free"
    },
    "pro": {
        "price_id": os.getenv("STRIPE_PRO_PRICE_ID", ""),
        "amount": 900,  # $9.00 in cents
        "requests_per_month": 10000,
        "name": "Pro"
    },
    "enterprise": {
        "price_id": os.getenv("STRIPE_ENTERPRISE_PRICE_ID", ""),
        "amount": 4900,  # $49.00 in cents
        "requests_per_month": 1000000,
        "name": "Enterprise"
    }
}
```

---

## How It Works

1. **User subscribes:**
   - User visits pricing page
   - Clicks "Subscribe Now"
   - Enters email
   - Redirected to Stripe Checkout

2. **Payment processed:**
   - Stripe processes payment
   - Redirects to success page
   - API key is automatically generated
   - Subscription linked to API key

3. **Webhook events:**
   - Stripe sends webhook events
   - API updates subscription status
   - API key tier updated automatically

4. **Subscription management:**
   - Users can check status via `/subscription/status`
   - Cancellations handled via webhooks
   - API keys downgraded to free tier on cancellation

---

## Troubleshooting

### Checkout session not created

- Verify `STRIPE_SECRET_KEY` is set correctly
- Check `STRIPE_PRO_PRICE_ID` or `STRIPE_ENTERPRISE_PRICE_ID` matches Stripe dashboard
- Ensure price IDs are from the same mode (test/live) as your secret key

### Webhooks not working

- Verify `STRIPE_WEBHOOK_SECRET` is set correctly
- Check webhook endpoint URL in Stripe dashboard
- Ensure webhook events are enabled
- Check API logs for webhook errors

### API key not generated after payment

- Check `/payment/success` endpoint logs
- Verify subscription exists in Stripe dashboard
- Check `subscriptions.json` file for linked subscriptions

---

## Security Notes

- **Never commit Stripe keys to Git**
- Use environment variables for all secrets
- Use test mode keys during development
- Switch to live mode keys only in production
- Regularly rotate webhook secrets

---

## Next Steps

1. ✅ Set up Stripe account
2. ✅ Create products and prices
3. ✅ Configure environment variables
4. ✅ Set up webhooks
5. ✅ Test integration
6. ✅ Launch paid tiers!

---

## Support

- **Stripe Documentation:** https://stripe.com/docs
- **Stripe Support:** https://support.stripe.com
- **API Documentation:** `/docs` endpoint

---

**Ready to start accepting payments! 💰**

