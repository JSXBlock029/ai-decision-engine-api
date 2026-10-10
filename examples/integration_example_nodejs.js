const axios = require('axios');

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
assessRisk();