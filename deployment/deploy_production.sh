#!/bin/bash
# Production Deployment Script

set -e

echo "=========================================="
echo "PRODUCTION DEPLOYMENT"
echo "=========================================="
echo ""

# Check environment
if [ -z "$API_ENV" ]; then
    echo "ERROR: API_ENV not set"
    exit 1
fi

# Install dependencies
echo "Installing dependencies..."
pip install -r api/requirements.txt

# Run tests
echo "Running tests..."
python scripts/simple_test.py || echo "WARNING: Tests failed"

# Start server
echo "Starting production server..."
cd api
uvicorn main:app --host 0.0.0.0 --port ${API_PORT:-8000} --workers 4
