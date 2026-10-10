#!/bin/bash
# Automated Deployment Script for Linux/Mac
# Handles deployment to various platforms

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

cd "$PROJECT_ROOT"

echo "========================================"
echo "AI DECISION ENGINE - AUTOMATED DEPLOYMENT"
echo "========================================"
echo ""

# Check prerequisites
echo "Checking prerequisites..."

if ! command -v python3 &> /dev/null; then
    echo "[ERROR] Python3 not found!"
    exit 1
fi
echo "[OK] Python found"

if ! command -v git &> /dev/null; then
    echo "[WARN] Git not found (optional)"
else
    echo "[OK] Git found"
fi

echo ""

# Menu
echo "Select deployment platform:"
echo "  1. Local (for testing)"
echo "  2. Docker"
echo "  3. Railway"
echo "  4. Heroku"
echo "  5. Render (manual instructions)"
echo "  6. Create deployment package"
echo ""
read -p "Enter choice (1-6): " choice

case $choice in
    1)
        echo ""
        echo "Starting local deployment..."
        python3 -m uvicorn api.main:app --host 0.0.0.0 --port 8000 --reload &
        echo ""
        echo "[OK] API server started"
        echo "     URL: http://localhost:8000"
        echo "     Docs: http://localhost:8000/docs"
        ;;
    2)
        echo ""
        echo "Building Docker image..."
        if ! command -v docker &> /dev/null; then
            echo "[ERROR] Docker not found!"
            exit 1
        fi
        
        docker build -t ai-decision-engine -f api/Dockerfile.prod .
        echo ""
        echo "[OK] Docker image built"
        echo "Run with: docker run -p 8000:8000 ai-decision-engine"
        ;;
    3)
        echo ""
        echo "Deploying to Railway..."
        if ! command -v railway &> /dev/null; then
            echo "[ERROR] Railway CLI not found!"
            echo "Install: npm install -g @railway/cli"
            exit 1
        fi
        
        railway up
        echo "[OK] Deployed to Railway"
        ;;
    4)
        echo ""
        echo "Deploying to Heroku..."
        if ! command -v heroku &> /dev/null; then
            echo "[ERROR] Heroku CLI not found!"
            exit 1
        fi
        
        read -p "Enter Heroku app name (or press Enter for default): " app_name
        app_name=${app_name:-ai-decision-engine-api}
        
        heroku create "$app_name" 2>/dev/null || true
        git push heroku main
        
        echo "[OK] Deployed to Heroku: https://$app_name.herokuapp.com"
        ;;
    5)
        echo ""
        echo "Render Deployment Instructions:"
        echo ""
        echo "1. Go to render.com and sign up/login"
        echo "2. Click 'New +' and select 'Web Service'"
        echo "3. Connect your GitHub repository"
        echo "4. Configure:"
        echo "   - Build Command: pip install -r api/requirements.txt"
        echo "   - Start Command: uvicorn api.main:app --host 0.0.0.0 --port \$PORT"
        echo "5. Add environment variables from api/.env.example"
        echo "6. Deploy!"
        echo ""
        ;;
    6)
        echo ""
        echo "Creating deployment package..."
        mkdir -p deploy_package
        
        cp -r api deploy_package/
        cp ai_decision_engine.py deploy_package/
        cp ai_memory_system.py deploy_package/
        cp autonomy_tracker.py deploy_package/
        
        echo "[OK] Deployment package created in: deploy_package/"
        ;;
    *)
        echo "[ERROR] Invalid choice"
        exit 1
        ;;
esac

echo ""
echo "========================================"
echo "Deployment process complete"
echo "========================================"

