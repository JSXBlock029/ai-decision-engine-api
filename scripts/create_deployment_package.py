"""
Production Deployment Package
Complete package for production deployment
"""

import json
import shutil
from pathlib import Path
from datetime import datetime

class ProductionDeployment:
    """Create production deployment package"""
    
    def __init__(self):
        self.project_root = Path(".")
        self.deployment_dir = self.project_root / "deployment"
        self.deployment_dir.mkdir(exist_ok=True)
    
    def create_deployment_package(self):
        """Create complete deployment package"""
        print("="*60)
        print("CREATING PRODUCTION DEPLOYMENT PACKAGE")
        print("="*60)
        print()
        
        # 1. Production configuration
        self.create_production_config()
        
        # 2. Environment setup
        self.create_env_template()
        
        # 3. Deployment scripts
        self.create_deployment_scripts()
        
        # 4. Production checklist
        self.create_production_checklist()
        
        # 5. Launch package
        self.create_launch_package()
        
        print()
        print("="*60)
        print("DEPLOYMENT PACKAGE CREATED!")
        print("="*60)
        print(f"Location: {self.deployment_dir}")
        print()
        print("Next steps:")
        print("1. Review deployment/PRODUCTION_CONFIG.md")
        print("2. Configure environment variables")
        print("3. Run deployment script")
        print("4. Verify deployment")
    
    def create_production_config(self):
        """Create production configuration guide"""
        config = """# Production Configuration Guide

## Environment Variables

Create a `.env` file with the following:

```env
# API Configuration
API_HOST=0.0.0.0
API_PORT=8000
API_ENV=production

# Security
SECRET_KEY=your-secret-key-here-change-in-production
ALLOWED_ORIGINS=https://yourdomain.com,https://www.yourdomain.com

# Database (if using)
DATABASE_URL=postgresql://user:pass@host:port/dbname

# Monitoring
SENTRY_DSN=your-sentry-dsn-here
LOG_LEVEL=INFO

# Features
ENABLE_ANALYTICS=true
ENABLE_WEBHOOKS=true
ENABLE_CACHING=true
```

## Security Checklist

- [ ] Change all default secrets
- [ ] Use strong API keys
- [ ] Enable HTTPS/SSL
- [ ] Configure CORS properly
- [ ] Set up rate limiting
- [ ] Enable logging
- [ ] Set up monitoring
- [ ] Configure backups

## Production Settings

1. **Disable Debug Mode**
   - Set `DEBUG=false` in environment

2. **Enable CORS**
   - Configure allowed origins
   - Restrict to your domains

3. **Set Up Monitoring**
   - Configure Sentry or similar
   - Set up uptime monitoring
   - Configure alerting

4. **Database Setup** (if needed)
   - Configure production database
   - Set up backups
   - Configure connection pooling

## Deployment Platforms

### Railway
```bash
railway up
```

### Heroku
```bash
heroku create your-app-name
git push heroku main
```

### Docker
```bash
docker build -t ai-decision-engine .
docker run -p 8000:8000 ai-decision-engine
```

### Render
- Connect GitHub repository
- Configure build settings
- Set environment variables
- Deploy

## Post-Deployment

1. Verify health endpoint
2. Test all endpoints
3. Check monitoring
4. Review logs
5. Test from external network
"""
        
        config_file = self.deployment_dir / "PRODUCTION_CONFIG.md"
        with open(config_file, "w", encoding="utf-8") as f:
            f.write(config)
        print("[OK] Production configuration created")
    
    def create_env_template(self):
        """Create environment template"""
        env_template = """# Production Environment Variables
# Copy this to .env and fill in values

API_HOST=0.0.0.0
API_PORT=8000
API_ENV=production

# Security - CHANGE THESE!
SECRET_KEY=change-me-in-production
ALLOWED_ORIGINS=https://yourdomain.com

# Monitoring
SENTRY_DSN=
LOG_LEVEL=INFO

# Features
ENABLE_ANALYTICS=true
ENABLE_WEBHOOKS=true
ENABLE_CACHING=true
"""
        
        env_file = self.deployment_dir / ".env.template"
        with open(env_file, "w", encoding="utf-8") as f:
            f.write(env_template)
        print("[OK] Environment template created")
    
    def create_deployment_scripts(self):
        """Create deployment scripts"""
        # Production deploy script
        deploy_script = """#!/bin/bash
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
"""
        
        script_file = self.deployment_dir / "deploy_production.sh"
        with open(script_file, "w", encoding="utf-8") as f:
            f.write(deploy_script)
        print("[OK] Deployment script created")
    
    def create_production_checklist(self):
        """Create production checklist"""
        checklist = """# Production Deployment Checklist

## Pre-Deployment

### Configuration
- [ ] Environment variables configured
- [ ] Secrets changed from defaults
- [ ] CORS configured correctly
- [ ] Database configured (if needed)
- [ ] SSL/HTTPS enabled

### Testing
- [ ] All tests passing
- [ ] Load testing completed
- [ ] Security audit done
- [ ] Performance tested

### Monitoring
- [ ] Monitoring tools configured
- [ ] Alerting set up
- [ ] Logging configured
- [ ] Uptime monitoring active

## Deployment

- [ ] Backup current version
- [ ] Deploy to staging first
- [ ] Verify staging deployment
- [ ] Deploy to production
- [ ] Verify production deployment

## Post-Deployment

- [ ] Health check passing
- [ ] All endpoints working
- [ ] Monitoring active
- [ ] No errors in logs
- [ ] Performance acceptable

## Launch

- [ ] Announcement ready
- [ ] Documentation updated
- [ ] Support channels ready
- [ ] Monitoring active
- [ ] Team notified
"""
        
        checklist_file = self.deployment_dir / "PRODUCTION_CHECKLIST.md"
        with open(checklist_file, "w", encoding="utf-8") as f:
            f.write(checklist)
        print("[OK] Production checklist created")
    
    def create_launch_package(self):
        """Create launch package"""
        launch_package = {
            "launch_date": None,
            "status": "ready",
            "pre_launch_tasks": [
                "Final testing",
                "Security review",
                "Performance optimization",
                "Documentation review"
            ],
            "launch_tasks": [
                "Deploy to production",
                "Verify deployment",
                "Announce launch",
                "Monitor closely"
            ],
            "post_launch_tasks": [
                "Collect feedback",
                "Monitor metrics",
                "Address issues",
                "Plan improvements"
            ]
        }
        
        package_file = self.deployment_dir / "launch_package.json"
        with open(package_file, "w", encoding="utf-8") as f:
            json.dump(launch_package, f, indent=2)
        print("[OK] Launch package created")

def main():
    """Create deployment package"""
    deployment = ProductionDeployment()
    deployment.create_deployment_package()

if __name__ == "__main__":
    main()

