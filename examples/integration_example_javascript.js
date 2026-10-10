// Configure API
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
assessRisk();