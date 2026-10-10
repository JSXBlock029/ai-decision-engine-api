"""
Quick Deploy Script for Free Platforms
One-click deployment to free platforms
"""

import subprocess
import sys
from pathlib import Path

def deploy_railway():
    """Deploy to Railway (free tier)"""
    print("="*60)
    print("DEPLOYING TO RAILWAY (FREE)")
    print("="*60)
    print()
    print("Steps:")
    print("1. Install Railway CLI: npm i -g @railway/cli")
    print("2. Login: railway login")
    print("3. Initialize: railway init")
    print("4. Deploy: railway up")
    print()
    print("Or use Railway web interface:")
    print("1. Go to railway.app")
    print("2. Sign up (free)")
    print("3. New Project")
    print("4. Connect GitHub")
    print("5. Deploy!")
    print()
    print("Cost: $0/month (free tier)")

def deploy_render():
    """Deploy to Render (free tier)"""
    print("="*60)
    print("DEPLOYING TO RENDER (FREE)")
    print("="*60)
    print()
    print("Steps:")
    print("1. Go to render.com")
    print("2. Sign up (free)")
    print("3. New Web Service")
    print("4. Connect GitHub repository")
    print("5. Configure:")
    print("   - Build Command: pip install -r api/requirements.txt")
    print("   - Start Command: cd api && uvicorn main:app --host 0.0.0.0 --port $PORT")
    print("6. Deploy!")
    print()
    print("Cost: $0/month (free tier)")

def create_railway_config():
    """Create Railway configuration"""
    railway_json = {
        "$schema": "https://railway.app/railway.schema.json",
        "build": {
            "builder": "NIXPACKS"
        },
        "deploy": {
            "startCommand": "cd api && uvicorn main:app --host 0.0.0.0 --port $PORT",
            "healthcheckPath": "/health",
            "healthcheckTimeout": 100
        }
    }
    
    config_file = Path("railway.json")
    with open(config_file, "w", encoding="utf-8") as f:
        import json
        json.dump(railway_json, f, indent=2)
    
    print("Railway config created: railway.json")

def create_render_config():
    """Create Render configuration"""
    render_yaml = """services:
  - type: web
    name: ai-decision-engine-api
    env: python
    buildCommand: pip install -r api/requirements.txt
    startCommand: cd api && uvicorn main:app --host 0.0.0.0 --port $PORT
    healthCheckPath: /health
    envVars:
      - key: API_ENV
        value: production
"""
    
    config_file = Path("render.yaml")
    with open(config_file, "w", encoding="utf-8") as f:
        f.write(render_yaml)
    
    print("Render config created: render.yaml")

def main():
    """Main deployment helper"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Free Deployment Helper")
    parser.add_argument("platform", choices=["railway", "render", "both"], 
                       help="Platform to deploy to")
    
    args = parser.parse_args()
    
    if args.platform == "railway":
        create_railway_config()
        deploy_railway()
    elif args.platform == "render":
        create_render_config()
        deploy_render()
    elif args.platform == "both":
        create_railway_config()
        create_render_config()
        print("\nConfigs created for both platforms!")
        print("Choose one to deploy to.")

if __name__ == "__main__":
    if len(sys.argv) == 1:
        print("Free Deployment Helper")
        print()
        print("Usage:")
        print("  python scripts/free_deploy.py railway")
        print("  python scripts/free_deploy.py render")
        print("  python scripts/free_deploy.py both")
        print()
        print("Or follow FREE_DEPLOYMENT_GUIDE.md")
    else:
        main()

