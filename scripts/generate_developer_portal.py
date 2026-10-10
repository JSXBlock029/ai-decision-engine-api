"""
Developer Portal
Web-based developer portal for API management
"""

import json
from pathlib import Path

def generate_developer_portal():
    """Generate developer portal HTML"""
    html = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Developer Portal - AI Decision Engine API</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: #f5f5f5;
            color: #333;
        }
        .header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 40px 20px;
            text-align: center;
        }
        .header h1 {
            font-size: 2.5em;
            margin-bottom: 10px;
        }
        .container {
            max-width: 1200px;
            margin: 0 auto;
            padding: 40px 20px;
        }
        .nav {
            background: white;
            padding: 20px;
            border-radius: 10px;
            margin-bottom: 30px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        .nav ul {
            list-style: none;
            display: flex;
            gap: 20px;
            flex-wrap: wrap;
        }
        .nav a {
            color: #667eea;
            text-decoration: none;
            padding: 10px 20px;
            border-radius: 5px;
            transition: background 0.3s;
        }
        .nav a:hover {
            background: #f0f0f0;
        }
        .section {
            background: white;
            padding: 30px;
            border-radius: 10px;
            margin-bottom: 30px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        .section h2 {
            color: #667eea;
            margin-bottom: 20px;
            font-size: 1.8em;
        }
        .code-block {
            background: #f5f5f5;
            padding: 20px;
            border-radius: 5px;
            overflow-x: auto;
            margin: 15px 0;
        }
        .code-block code {
            font-family: 'Courier New', monospace;
            font-size: 14px;
        }
        .btn {
            background: #667eea;
            color: white;
            padding: 12px 24px;
            border: none;
            border-radius: 5px;
            cursor: pointer;
            font-size: 16px;
            margin: 10px 5px;
            text-decoration: none;
            display: inline-block;
        }
        .btn:hover {
            background: #5568d3;
        }
        .feature-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            margin: 20px 0;
        }
        .feature-card {
            background: #f9f9f9;
            padding: 20px;
            border-radius: 8px;
            border-left: 4px solid #667eea;
        }
        .feature-card h3 {
            color: #667eea;
            margin-bottom: 10px;
        }
    </style>
</head>
<body>
    <div class="header">
        <h1>🚀 Developer Portal</h1>
        <p>AI Decision Engine API - Everything you need to build</p>
    </div>
    
    <div class="container">
        <nav class="nav">
            <ul>
                <li><a href="#quickstart">Quick Start</a></li>
                <li><a href="#docs">Documentation</a></li>
                <li><a href="#sdks">SDKs</a></li>
                <li><a href="#examples">Examples</a></li>
                <li><a href="#tools">Tools</a></li>
                <li><a href="#support">Support</a></li>
            </ul>
        </nav>
        
        <section id="quickstart" class="section">
            <h2>Quick Start</h2>
            <p>Get started with the AI Decision Engine API in minutes.</p>
            
            <h3>1. Get Your API Key</h3>
            <div class="code-block">
                <code>python api/manage_api_keys.py generate pro</code>
            </div>
            
            <h3>2. Make Your First Request</h3>
            <div class="code-block">
                <code>curl -X POST "https://api.example.com/decisions/evaluate" \\
  -H "X-API-Key: YOUR_API_KEY" \\
  -H "Content-Type: application/json" \\
  -d '{"category": "FINANCIAL", "amount": 1000}'</code>
            </div>
            
            <a href="/docs" class="btn">View Full Documentation</a>
        </section>
        
        <section id="docs" class="section">
            <h2>Documentation</h2>
            <div class="feature-grid">
                <div class="feature-card">
                    <h3>API Reference</h3>
                    <p>Complete API endpoint documentation</p>
                    <a href="/docs" class="btn">View Docs</a>
                </div>
                <div class="feature-card">
                    <h3>Integration Guide</h3>
                    <p>Step-by-step integration instructions</p>
                    <a href="/docs/integration" class="btn">Read Guide</a>
                </div>
                <div class="feature-card">
                    <h3>Code Examples</h3>
                    <p>Ready-to-use code examples</p>
                    <a href="/examples" class="btn">View Examples</a>
                </div>
            </div>
        </section>
        
        <section id="sdks" class="section">
            <h2>SDKs & Libraries</h2>
            <p>Use our official SDKs for easier integration:</p>
            
            <h3>Python SDK</h3>
            <div class="code-block">
                <code>from sdk.python.ai_decision_engine import AIDecisionEngineClient

client = AIDecisionEngineClient(api_key="YOUR_KEY")
decision = client.evaluate_decision(
    category="FINANCIAL",
    amount=1000
)</code>
            </div>
            
            <h3>JavaScript SDK</h3>
            <div class="code-block">
                <code>import { AIDecisionEngine } from '@example/sdk';

const client = new AIDecisionEngine('YOUR_KEY');
const decision = await client.evaluateDecision({
    category: 'FINANCIAL',
    amount: 1000
});</code>
            </div>
        </section>
        
        <section id="examples" class="section">
            <h2>Code Examples</h2>
            <p>Check out our examples directory for complete integration examples:</p>
            <ul>
                <li><a href="/examples/integration_example_python.py">Python Example</a></li>
                <li><a href="/examples/integration_example_javascript.js">JavaScript Example</a></li>
                <li><a href="/examples/integration_example_nodejs.js">Node.js Example</a></li>
                <li><a href="/examples/integration_example_curl.sh">cURL Example</a></li>
            </ul>
        </section>
        
        <section id="tools" class="section">
            <h2>Developer Tools</h2>
            <div class="feature-grid">
                <div class="feature-card">
                    <h3>CLI Tool</h3>
                    <p>Command-line interface for quick testing</p>
                    <code>python sdk/cli/ai_decision_cli.py evaluate FINANCIAL --amount 1000</code>
                </div>
                <div class="feature-card">
                    <h3>Dashboard</h3>
                    <p>Web-based dashboard for API management</p>
                    <a href="/dashboard" class="btn">Open Dashboard</a>
                </div>
                <div class="feature-card">
                    <h3>Status Page</h3>
                    <p>Real-time API status and metrics</p>
                    <a href="/status" class="btn">View Status</a>
                </div>
            </div>
        </section>
        
        <section id="support" class="section">
            <h2>Support & Resources</h2>
            <p>Need help? We're here for you:</p>
            <ul>
                <li><strong>Documentation:</strong> <a href="/docs">Full API Docs</a></li>
                <li><strong>Email:</strong> support@example.com</li>
                <li><strong>GitHub:</strong> <a href="#">Issues & Discussions</a></li>
                <li><strong>Community:</strong> Join our developer community</li>
            </ul>
        </section>
    </div>
</body>
</html>"""
    
    with open("developer_portal.html", "w", encoding="utf-8") as f:
        f.write(html)
    
    print("Developer portal generated: developer_portal.html")

if __name__ == "__main__":
    generate_developer_portal()

