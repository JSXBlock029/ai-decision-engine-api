# API Integration Guide

Complete guide for integrating with the AI Decision Engine API

## Quick Start

### 1. Get Your API Key
Contact us to get your API key for authentication.

### 2. Base URL
- **Production**: `https://api.example.com/v1` (coming soon)
- **Development**: `http://localhost:8000`

### 3. Authentication
Include your API key in the `X-API-Key` header:
```python
headers = {
    "X-API-Key": "your_api_key_here",
    "Content-Type": "application/json"
}
```

## Endpoints

### Health Check
```python
import requests

response = requests.get("http://localhost:8000/health")
print(response.json())
```

### Evaluate Decision
```python
import requests

url = "http://localhost:8000/decisions/evaluate"
headers = {"X-API-Key": "your_key", "Content-Type": "application/json"}
data = {
    "category": "FINANCIAL",
    "amount": 1000.0,
    "description": "Invest in marketing campaign"
}

response = requests.post(url, json=data, headers=headers)
result = response.json()

print(f"Risk Level: {result['risk_level']}")
print(f"AI Can Decide: {result['ai_can_decide']}")
```

### Assess Risk
```python
data = {
    "amount": 5000.0,
    "category": "STRATEGIC",
    "description": "Launch new product line"
}

response = requests.post(
    "http://localhost:8000/risk/assess",
    json=data,
    headers=headers
)
```

### Get Autonomy Level
```python
response = requests.get(
    "http://localhost:8000/autonomy/level",
    headers=headers
)
autonomy = response.json()
print(f"Current Autonomy: {autonomy['autonomy_level']}%")
```

### Check Auto-Execute
```python
data = {
    "task_type": "operational",
    "risk_level": "LOW"
}

response = requests.post(
    "http://localhost:8000/autonomy/should-execute",
    json=data,
    headers=headers
)
```

### Get Memory Insights
```python
data = {
    "decision_data": {
        "category": "FINANCIAL",
        "amount": 1000
    }
}

response = requests.post(
    "http://localhost:8000/memory/insights",
    json=data,
    headers=headers
)
```

## Error Handling

All endpoints return standard HTTP status codes:
- `200`: Success
- `400`: Bad Request (validation error)
- `401`: Unauthorized (invalid API key)
- `422`: Unprocessable Entity (validation error)
- `500`: Internal Server Error

Error response format:
```json
{
    "error": true,
    "error_code": "VALIDATION_ERROR",
    "message": "Invalid category",
    "timestamp": "2025-11-05T01:30:00"
}
```

## Rate Limiting

Free tier: 100 requests/month
Pro tier: 10,000 requests/month

Rate limit headers are included in responses:
- `X-RateLimit-Limit`: Request limit
- `X-RateLimit-Remaining`: Remaining requests
- `X-RateLimit-Reset`: Reset timestamp

## Best Practices

1. **Always check response status**
   ```python
   if response.status_code == 200:
       data = response.json()
   else:
       error = response.json()
       print(f"Error: {error['message']}")
   ```

2. **Handle errors gracefully**
   ```python
   try:
       response = requests.post(url, json=data, headers=headers)
       response.raise_for_status()
   except requests.exceptions.HTTPError as e:
       print(f"HTTP Error: {e}")
   except requests.exceptions.RequestException as e:
       print(f"Request Error: {e}")
   ```

3. **Use connection pooling**
   ```python
   session = requests.Session()
   session.headers.update({"X-API-Key": "your_key"})
   ```

4. **Cache responses when appropriate**
   ```python
   import time
   
   cache = {}
   cache_timeout = 300  # 5 minutes
   
   def get_cached_autonomy():
       if 'autonomy' in cache:
           if time.time() - cache['autonomy']['timestamp'] < cache_timeout:
               return cache['autonomy']['data']
       # Fetch fresh data
       response = requests.get(url, headers=headers)
       cache['autonomy'] = {
           'data': response.json(),
           'timestamp': time.time()
       }
       return cache['autonomy']['data']
   ```

## SDK Examples

### Python SDK (Simple)
```python
class AIDecisionAPI:
    def __init__(self, api_key, base_url="http://localhost:8000"):
        self.api_key = api_key
        self.base_url = base_url
        self.headers = {
            "X-API-Key": api_key,
            "Content-Type": "application/json"
        }
    
    def evaluate_decision(self, category, amount, description=""):
        url = f"{self.base_url}/decisions/evaluate"
        data = {
            "category": category,
            "amount": amount,
            "description": description
        }
        response = requests.post(url, json=data, headers=self.headers)
        response.raise_for_status()
        return response.json()
    
    def assess_risk(self, amount, category, description=""):
        url = f"{self.base_url}/risk/assess"
        data = {"amount": amount, "category": category, "description": description}
        response = requests.post(url, json=data, headers=self.headers)
        response.raise_for_status()
        return response.json()

# Usage
api = AIDecisionAPI("your_api_key")
result = api.evaluate_decision("FINANCIAL", 1000, "Marketing campaign")
```

## Support

For issues or questions:
- Email: support@example.com
- Documentation: https://docs.example.com
- Status Page: https://status.example.com

