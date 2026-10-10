import requests

# Configure API
API_URL = "https://api.example.com"
API_KEY = "YOUR_API_KEY_HERE"

headers = {
    "X-API-Key": API_KEY,
    "Content-Type": "application/json"
}

# Evaluate a decision
response = requests.post(
    f"{API_URL}/decisions/evaluate",
    json={
        "category": "FINANCIAL",
        "amount": 1000.0,
        "description": "Purchase new equipment"
    },
    headers=headers
)

decision = response.json()
print(f"Decision ID: {decision['id']}")
print(f"Risk Level: {decision['risk_level']}")
print(f"AI Can Decide: {decision['ai_can_decide']}")

# Assess risk
response = requests.post(
    f"{API_URL}/risk/assess",
    json={
        "amount": 5000,
        "category": "STRATEGIC"
    },
    headers=headers
)

risk = response.json()
print(f"Risk Score: {risk['risk_score']}")
print(f"Risk Level: {risk['risk_level']}")