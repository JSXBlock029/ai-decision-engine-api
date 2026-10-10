# Evaluate a decision
curl -X POST "https://api.example.com/decisions/evaluate" \
  -H "X-API-Key: YOUR_API_KEY_HERE" \
  -H "Content-Type: application/json" \
  -d '{
    "category": "FINANCIAL",
    "amount": 1000.0,
    "description": "Purchase new equipment"
  }'

# Assess risk
curl -X POST "https://api.example.com/risk/assess" \
  -H "X-API-Key: YOUR_API_KEY_HERE" \
  -H "Content-Type: application/json" \
  -d '{
    "amount": 5000,
    "category": "STRATEGIC"
  }'

# Get autonomy level
curl -X GET "https://api.example.com/autonomy/level" \
  -H "X-API-Key: YOUR_API_KEY_HERE"

# Get analytics
curl -X GET "https://api.example.com/analytics/stats" \
  -H "X-API-Key: YOUR_API_KEY_HERE"