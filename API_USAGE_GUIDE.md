# API Usage Guide

**Base URL:** `https://web-production-62146.up.railway.app`

## Authentication

All API requests require an API key. Include it in the `X-API-Key` header:

```bash
curl -H "X-API-Key: your_api_key_here" https://web-production-62146.up.railway.app/api/usage
```

---

## Getting Started

### 1. Get Your Free API Key

Visit: https://web-production-62146.up.railway.app/

Click "Get Free API Key" and enter your email to receive:
- 100 free requests/month
- Full API access
- All endpoints included

### 2. Upgrade for More Requests

**Pro Tier ($9/month):**
- 10,000 requests/month included
- $1.00 per 1,000 overage requests
- Priority support

**Enterprise Tier ($49/month):**
- 1,000,000 requests/month included
- $0.50 per 1,000 overage requests
- Custom integrations

---

## Dashboard Endpoints

### Monitor Your Usage

```bash
GET /api/usage
```

**Example Request:**
```bash
curl -H "X-API-Key: production_abc123..." \
  https://web-production-62146.up.railway.app/api/usage
```

**Example Response:**
```json
{
  "success": true,
  "usage": {
    "total_requests": 2547,
    "included_requests": 2547,
    "overage_requests": 0,
    "max_requests": 10000,
    "tier": "pro",
    "month": "2025-11"
  },
  "reset_date": "2025-11-01",
  "tier_info": {
    "tier": "pro",
    "included_requests": 10000
  }
}
```

---

### Check Your Billing

```bash
GET /api/billing
```

**Example Request:**
```bash
curl -H "X-API-Key: production_abc123..." \
  https://web-production-62146.up.railway.app/api/billing
```

**Example Response:**
```json
{
  "success": true,
  "billing": {
    "tier": "pro",
    "base_price": 9.0,
    "included_requests": 10000,
    "total_requests": 12453,
    "overage_requests": 2453,
    "overage_charge": 2.45,
    "total_charge": 11.45,
    "month": "2025-11"
  },
  "note": "Overage charges are billed monthly"
}
```

**Breakdown:**
- Base: $9.00 (Pro tier monthly fee)
- Overage: 2,453 requests × $0.001 = $2.45
- **Total: $11.45**

---

### View API Key Info

```bash
GET /api/key/info
```

**Example Request:**
```bash
curl -H "X-API-Key: production_abc123..." \
  https://web-production-62146.up.railway.app/api/key/info
```

**Example Response:**
```json
{
  "success": true,
  "key_info": {
    "tier": "pro",
    "requests_per_month": 10000,
    "created_at": "2025-11-07T01:28:00.619605",
    "active": true,
    "key_preview": "production_...",
    "email": "user@example.com"
  }
}
```

---

## Core API Endpoints

### 1. Health Check

```bash
GET /health
```

Check if the API is operational.

**Example:**
```bash
curl https://web-production-62146.up.railway.app/health
```

**Response:**
```json
{
  "status": "healthy",
  "system_state": "operational",
  "version": "1.0.0",
  "autonomy_level": 25.0
}
```

---

### 2. Decision Evaluation

```bash
POST /decisions/evaluate
```

Evaluate a decision using the AI engine.

**Example:**
```bash
curl -X POST https://web-production-62146.up.railway.app/decisions/evaluate \
  -H "Content-Type: application/json" \
  -H "X-API-Key: your_api_key" \
  -d '{
    "category": "strategic",
    "description": "Should we expand to the European market?",
    "options": [
      {"name": "Expand now", "score": 0.8},
      {"name": "Wait 6 months", "score": 0.6}
    ],
    "context": {
      "budget": 500000,
      "timeline": "Q2 2025"
    }
  }'
```

**Response:**
```json
{
  "decision_id": "dec_abc123",
  "recommendation": "Expand now",
  "confidence": 0.85,
  "reasoning": "Strong market opportunity with available budget",
  "alternatives": ["Wait 6 months"],
  "risk_level": "medium"
}
```

---

### 3. Risk Assessment

```bash
POST /risk/assess
```

Assess risk for a proposed action.

**Example:**
```bash
curl -X POST https://web-production-62146.up.railway.app/risk/assess \
  -H "Content-Type: application/json" \
  -H "X-API-Key: your_api_key" \
  -d '{
    "action": "Launch new product line",
    "factors": {
      "market_volatility": 0.6,
      "competition": 0.7,
      "resources": 0.8
    }
  }'
```

**Response:**
```json
{
  "risk_level": "medium",
  "risk_score": 0.63,
  "factors_analyzed": 3,
  "recommendations": [
    "Monitor market conditions closely",
    "Prepare contingency plans"
  ]
}
```

---

### 4. Pricing Information

```bash
GET /pricing
```

Get current pricing tiers (returns HTML for browsers, JSON for API clients).

**For JSON response:**
```bash
curl -H "Accept: application/json" \
  https://web-production-62146.up.railway.app/pricing
```

**Response:**
```json
{
  "tiers": {
    "free": {
      "name": "Free",
      "price": 0,
      "requests_per_month": 100,
      "overage_per_1000": null,
      "features": [...]
    },
    "pro": {
      "name": "Pro",
      "price": 9,
      "requests_per_month": 10000,
      "overage_per_1000": 1.0,
      "features": [...]
    },
    "enterprise": {
      "name": "Enterprise",
      "price": 49,
      "requests_per_month": 1000000,
      "overage_per_1000": 0.5,
      "features": [...]
    }
  },
  "currency": "USD"
}
```

---

## Error Handling

### Authentication Errors

**Missing API Key:**
```json
{
  "detail": "API key required. Include X-API-Key header."
}
```
HTTP Status: 401

**Invalid API Key:**
```json
{
  "detail": "Invalid or inactive API key"
}
```
HTTP Status: 401

### Rate Limiting

**Free tier limit exceeded:**
```json
{
  "detail": "Rate limit exceeded. Upgrade to Pro for higher limits."
}
```
HTTP Status: 429

Note: Paid tiers allow overage (you'll be charged for extra requests).

---

## Best Practices

### 1. Monitor Your Usage
Check `/api/usage` regularly to avoid unexpected charges:
```bash
# Set up a daily check
curl -H "X-API-Key: $YOUR_KEY" \
  https://web-production-62146.up.railway.app/api/usage
```

### 2. Handle Rate Limits
```python
import requests
import time

def make_api_call(endpoint, data):
    response = requests.post(
        f"https://web-production-62146.up.railway.app{endpoint}",
        headers={"X-API-Key": YOUR_KEY},
        json=data
    )

    if response.status_code == 429:
        # Rate limited - wait and retry or upgrade tier
        print("Rate limit exceeded. Consider upgrading.")
        return None

    return response.json()
```

### 3. Secure Your API Key
```bash
# Use environment variables
export AI_API_KEY="your_api_key_here"

# Never commit keys to git
echo "AI_API_KEY=*" >> .gitignore
```

### 4. Track Billing
For paid tiers, check billing monthly:
```bash
# Check current month's charges
curl -H "X-API-Key: $YOUR_KEY" \
  https://web-production-62146.up.railway.app/api/billing
```

---

## Code Examples

### Python
```python
import requests

API_KEY = "your_api_key_here"
BASE_URL = "https://web-production-62146.up.railway.app"

def get_usage():
    response = requests.get(
        f"{BASE_URL}/api/usage",
        headers={"X-API-Key": API_KEY}
    )
    return response.json()

def evaluate_decision(description, options):
    response = requests.post(
        f"{BASE_URL}/decisions/evaluate",
        headers={
            "X-API-Key": API_KEY,
            "Content-Type": "application/json"
        },
        json={
            "category": "strategic",
            "description": description,
            "options": options
        }
    )
    return response.json()

# Use it
usage = get_usage()
print(f"Requests used: {usage['usage']['total_requests']}")

decision = evaluate_decision(
    "Should we hire 2 more developers?",
    [
        {"name": "Hire now", "score": 0.8},
        {"name": "Wait until Q2", "score": 0.6}
    ]
)
print(f"Recommendation: {decision['recommendation']}")
```

### JavaScript/Node.js
```javascript
const axios = require('axios');

const API_KEY = 'your_api_key_here';
const BASE_URL = 'https://web-production-62146.up.railway.app';

async function getUsage() {
  const response = await axios.get(`${BASE_URL}/api/usage`, {
    headers: { 'X-API-Key': API_KEY }
  });
  return response.data;
}

async function evaluateDecision(description, options) {
  const response = await axios.post(
    `${BASE_URL}/decisions/evaluate`,
    {
      category: 'strategic',
      description,
      options
    },
    {
      headers: {
        'X-API-Key': API_KEY,
        'Content-Type': 'application/json'
      }
    }
  );
  return response.data;
}

// Use it
(async () => {
  const usage = await getUsage();
  console.log(`Requests used: ${usage.usage.total_requests}`);

  const decision = await evaluateDecision(
    'Should we hire 2 more developers?',
    [
      { name: 'Hire now', score: 0.8 },
      { name: 'Wait until Q2', score: 0.6 }
    ]
  );
  console.log(`Recommendation: ${decision.recommendation}`);
})();
```

### cURL
```bash
#!/bin/bash

API_KEY="your_api_key_here"
BASE_URL="https://web-production-62146.up.railway.app"

# Get usage
curl -H "X-API-Key: $API_KEY" \
  $BASE_URL/api/usage

# Get billing
curl -H "X-API-Key: $API_KEY" \
  $BASE_URL/api/billing

# Evaluate decision
curl -X POST $BASE_URL/decisions/evaluate \
  -H "X-API-Key: $API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "category": "strategic",
    "description": "Expand to new market?",
    "options": [
      {"name": "Expand", "score": 0.8},
      {"name": "Stay focused", "score": 0.6}
    ]
  }'
```

---

## Support

### Documentation
- Interactive API docs: https://web-production-62146.up.railway.app/docs
- ReDoc: https://web-production-62146.up.railway.app/redoc

### Pricing & Billing Questions
Check `/api/billing` for transparent cost breakdown, or contact support.

### Technical Support
- **Free tier:** Community support
- **Pro/Enterprise:** Priority support

---

## Pricing Summary

| Tier | Base Price | Included Requests | Overage Cost |
|------|-----------|------------------|--------------|
| **Free** | $0/month | 100/month | No overage (hard limit) |
| **Pro** | $9/month | 10,000/month | $1.00 per 1,000 requests |
| **Enterprise** | $49/month | 1,000,000/month | $0.50 per 1,000 requests |

**Billing is transparent:** Use `/api/billing` to see exactly what you'll be charged each month.

---

**Ready to get started?** Get your free API key at https://web-production-62146.up.railway.app/
