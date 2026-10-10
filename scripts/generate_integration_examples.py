"""
Integration Examples Generator
Generate code examples for various languages
"""

import json
from typing import Dict, List

class IntegrationExamples:
    """Generate integration examples"""
    
    def __init__(self):
        self.base_url = "https://api.example.com"
        self.api_key = "YOUR_API_KEY_HERE"
    
    def python_example(self) -> str:
        """Python integration example"""
        return '''import requests

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
print(f"Risk Level: {risk['risk_level']}")'''
    
    def javascript_example(self) -> str:
        """JavaScript integration example"""
        return '''// Configure API
const API_URL = "https://api.example.com";
const API_KEY = "YOUR_API_KEY_HERE";

// Evaluate a decision
async function evaluateDecision() {
    const response = await fetch(`${API_URL}/decisions/evaluate`, {
        method: "POST",
        headers: {
            "X-API-Key": API_KEY,
            "Content-Type": "application/json"
        },
        body: JSON.stringify({
            category: "FINANCIAL",
            amount: 1000.0,
            description: "Purchase new equipment"
        })
    });
    
    const decision = await response.json();
    console.log("Decision ID:", decision.id);
    console.log("Risk Level:", decision.risk_level);
    console.log("AI Can Decide:", decision.ai_can_decide);
}

// Assess risk
async function assessRisk() {
    const response = await fetch(`${API_URL}/risk/assess`, {
        method: "POST",
        headers: {
            "X-API-Key": API_KEY,
            "Content-Type": "application/json"
        },
        body: JSON.stringify({
            amount: 5000,
            category: "STRATEGIC"
        })
    });
    
    const risk = await response.json();
    console.log("Risk Score:", risk.risk_score);
    console.log("Risk Level:", risk.risk_level);
}

// Call functions
evaluateDecision();
assessRisk();'''
    
    def curl_example(self) -> str:
        """cURL integration example"""
        return '''# Evaluate a decision
curl -X POST "https://api.example.com/decisions/evaluate" \\
  -H "X-API-Key: YOUR_API_KEY_HERE" \\
  -H "Content-Type: application/json" \\
  -d '{
    "category": "FINANCIAL",
    "amount": 1000.0,
    "description": "Purchase new equipment"
  }'

# Assess risk
curl -X POST "https://api.example.com/risk/assess" \\
  -H "X-API-Key: YOUR_API_KEY_HERE" \\
  -H "Content-Type: application/json" \\
  -d '{
    "amount": 5000,
    "category": "STRATEGIC"
  }'

# Get autonomy level
curl -X GET "https://api.example.com/autonomy/level" \\
  -H "X-API-Key: YOUR_API_KEY_HERE"

# Get analytics
curl -X GET "https://api.example.com/analytics/stats" \\
  -H "X-API-Key: YOUR_API_KEY_HERE"'''
    
    def nodejs_example(self) -> str:
        """Node.js integration example"""
        return '''const axios = require('axios');

// Configure API
const API_URL = "https://api.example.com";
const API_KEY = "YOUR_API_KEY_HERE";

const headers = {
    "X-API-Key": API_KEY,
    "Content-Type": "application/json"
};

// Evaluate a decision
async function evaluateDecision() {
    try {
        const response = await axios.post(
            `${API_URL}/decisions/evaluate`,
            {
                category: "FINANCIAL",
                amount: 1000.0,
                description: "Purchase new equipment"
            },
            { headers }
        );
        
        console.log("Decision:", response.data);
    } catch (error) {
        console.error("Error:", error.response?.data || error.message);
    }
}

// Assess risk
async function assessRisk() {
    try {
        const response = await axios.post(
            `${API_URL}/risk/assess`,
            {
                amount: 5000,
                category: "STRATEGIC"
            },
            { headers }
        );
        
        console.log("Risk:", response.data);
    } catch (error) {
        console.error("Error:", error.response?.data || error.message);
    }
}

// Run examples
evaluateDecision();
assessRisk();'''
    
    def generate_all(self) -> Dict[str, str]:
        """Generate all examples"""
        return {
            "python": self.python_example(),
            "javascript": self.javascript_example(),
            "curl": self.curl_example(),
            "nodejs": self.nodejs_example()
        }
    
    def save_examples(self):
        """Save all examples to files"""
        examples = self.generate_all()
        
        # Save individual files
        for lang, code in examples.items():
            ext = {
                "python": ".py",
                "javascript": ".js",
                "curl": ".sh",
                "nodejs": ".js"
            }.get(lang, ".txt")
            
            filename = f"examples/integration_example_{lang}{ext}"
            with open(filename, "w", encoding="utf-8") as f:
                f.write(code)
        
        # Save JSON
        with open("examples/integration_examples.json", "w", encoding="utf-8") as f:
            json.dump(examples, f, indent=2, ensure_ascii=False)
        
        return examples

def main():
    """Generate integration examples"""
    generator = IntegrationExamples()
    examples = generator.save_examples()
    
    print("=" * 60)
    print("INTEGRATION EXAMPLES GENERATED")
    print("=" * 60)
    print()
    print("Examples created for:")
    for lang in examples.keys():
        print(f"  - {lang}")
    print()
    print("Files saved to: examples/")

if __name__ == "__main__":
    import os
    os.makedirs("examples", exist_ok=True)
    main()

