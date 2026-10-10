#!/bin/bash
# Deployment script for AI Decision Engine API

echo "🚀 Deploying AI Decision Engine API..."

# Check if dependencies are installed
if ! command -v python &> /dev/null; then
    echo "❌ Python not found"
    exit 1
fi

# Install dependencies
echo "📦 Installing dependencies..."
cd api
pip install -r requirements.txt

# Check if API can start
echo "🔍 Testing API startup..."
python -c "from main import app; print('✅ API imports successfully')" || {
    echo "❌ API import failed"
    exit 1
}

echo "✅ API ready for deployment"
echo ""
echo "To start the API:"
echo "  cd api && python main.py"
echo ""
echo "Or with uvicorn:"
echo "  cd api && uvicorn main:app --reload"

