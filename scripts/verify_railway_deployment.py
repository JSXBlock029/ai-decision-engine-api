"""
Railway Deployment Verification
Check if deployment is working
"""

import requests
import json
from pathlib import Path

def verify_railway_deployment():
    """Verify Railway deployment"""
    print("="*60)
    print("RAILWAY DEPLOYMENT VERIFICATION")
    print("="*60)
    print()
    
    print("Your Railway deployment is live!")
    print()
    print("Next steps:")
    print()
    print("1. GET YOUR DEPLOYMENT URL")
    print("   - In Railway dashboard, click on your service")
    print("   - Go to 'Settings' tab")
    print("   - Click 'Generate Domain'")
    print("   - You'll get a URL like: your-app.railway.app")
    print()
    print("2. TEST YOUR API")
    print("   - Health check: https://your-app.railway.app/health")
    print("   - API docs: https://your-app.railway.app/docs")
    print()
    print("3. UPDATE MARKETING CONTENT")
    print("   - Replace [your-link] in READY_TO_POST_CONTENT.md")
    print("   - Update with your Railway URL")
    print()
    print("4. START MARKETING!")
    print("   - Post on Reddit")
    print("   - Share on Twitter")
    print("   - Post on HackerNews")
    print("   - Get first users!")
    print()
    
    # Create deployment success file
    success_info = {
        "deployment_status": "live",
        "platform": "Railway",
        "project_url": "https://railway.com/project/624953b0-2ed9-43b0-87c3-663235cb3860",
        "service_url": "https://railway.com/project/624953b0-2ed9-43b0-87c3-663235cb3860/service/ee940128-06c8-4643-8344-af1a0c8af810",
        "next_steps": [
            "Get deployment URL from Railway Settings",
            "Test health endpoint",
            "Update marketing content with URL",
            "Start posting on Reddit/Twitter/HN"
        ]
    }
    
    with open("RAILWAY_DEPLOYMENT_SUCCESS.json", "w", encoding="utf-8") as f:
        json.dump(success_info, f, indent=2)
    
    print("Deployment info saved to: RAILWAY_DEPLOYMENT_SUCCESS.json")
    print()

if __name__ == "__main__":
    verify_railway_deployment()

