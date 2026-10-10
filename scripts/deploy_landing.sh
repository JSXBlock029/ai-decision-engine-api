#!/bin/bash
# Deployment script for SaaS Landing Page

echo "🚀 Deploying AI Autonomy Tracker Landing Page..."

# Check for Node.js (for Netlify/Vercel CLI)
if command -v npm &> /dev/null; then
    echo "✅ Node.js found"
else
    echo "⚠️  Node.js not found (optional for some deployments)"
fi

# Check Python for backend
if command -v python &> /dev/null; then
    echo "✅ Python found for backend"
else
    echo "❌ Python not found"
    exit 1
fi

echo ""
echo "📁 Landing page files ready in: saas_landing/"
echo ""
echo "Deployment options:"
echo ""
echo "1. Netlify (Recommended):"
echo "   - Install Netlify CLI: npm install -g netlify-cli"
echo "   - Run: netlify deploy"
echo ""
echo "2. Vercel:"
echo "   - Install Vercel CLI: npm install -g vercel"
echo "   - Run: vercel"
echo ""
echo "3. GitHub Pages:"
echo "   - Push to GitHub"
echo "   - Enable Pages in repository settings"
echo ""
echo "4. Manual Upload:"
echo "   - Upload saas_landing/index.html to your hosting"
echo ""
echo "Backend (Waitlist API):"
echo "   - Deploy waitlist_backend.py as serverless function"
echo "   - Or deploy as separate API service"

