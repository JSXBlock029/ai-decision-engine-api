# Deployment Automation - Complete Guide

Comprehensive deployment automation scripts for the AI Decision Engine API.

## Available Scripts

### 1. Automated Deployment (Python)
**File:** `scripts/deploy_automated.py`

Full-featured deployment script with platform support.

```bash
python scripts/deploy_automated.py <platform>
```

**Platforms:**
- `railway` - Deploy to Railway
- `render` - Instructions for Render
- `heroku` - Deploy to Heroku
- `docker` - Build Docker image
- `local` - Start local server
- `package` - Create deployment package

**Options:**
- `--skip-tests` - Skip pre-deployment tests

### 2. Automated Deployment (Windows)
**File:** `scripts/deploy_automated.bat`

Interactive menu-based deployment for Windows.

```cmd
scripts\deploy_automated.bat
```

### 3. Automated Deployment (Linux/Mac)
**File:** `scripts/deploy_automated.sh`

Interactive menu-based deployment for Unix systems.

```bash
bash scripts/deploy_automated.sh
```

### 4. One-Click Deploy
**File:** `scripts/one_click_deploy.py`

Simplest deployment - just starts the server.

```bash
python scripts/one_click_deploy.py
```

## Quick Start

### Local Deployment (Testing)
```bash
# Windows
scripts\deploy_automated.bat
# Select option 1

# Linux/Mac
bash scripts/deploy_automated.sh
# Select option 1

# Python
python scripts/deploy_automated.py local
```

### Docker Deployment
```bash
# Windows
scripts\deploy_automated.bat
# Select option 2

# Linux/Mac
bash scripts/deploy_automated.sh
# Select option 2

# Python
python scripts/deploy_automated.py docker
```

### Railway Deployment
```bash
# Install Railway CLI first
npm install -g @railway/cli

# Deploy
python scripts/deploy_automated.py railway
```

### Heroku Deployment
```bash
# Install Heroku CLI first
# https://devcenter.heroku.com/articles/heroku-cli

# Deploy
python scripts/deploy_automated.py heroku
```

## Prerequisites

### Required
- Python 3.11+
- pip

### Optional (for specific platforms)
- Docker (for Docker deployment)
- Railway CLI (for Railway)
- Heroku CLI (for Heroku)
- Git (for version control)

## Pre-Deployment Checklist

- [ ] All tests passing
- [ ] Environment variables configured
- [ ] API keys generated
- [ ] Dependencies installed
- [ ] Database configured (if needed)
- [ ] SSL certificate ready (for production)

## Post-Deployment

1. Verify deployment:
   ```bash
   curl https://your-api-url.com/health
   ```

2. Check logs:
   - Platform-specific log viewing
   - Monitor for errors

3. Test endpoints:
   ```bash
   python api/test_api.py
   ```

## Troubleshooting

### Common Issues

**Import Errors:**
- Ensure all dependencies installed: `pip install -r api/requirements.txt`

**Port Already in Use:**
- Change port: `--port 8001`
- Kill existing process

**Authentication Errors:**
- Check API keys are set
- Verify environment variables

## Platform-Specific Notes

### Railway
- Automatic HTTPS
- Environment variables in dashboard
- Auto-deploy from Git

### Heroku
- Requires Procfile
- Environment variables via CLI or dashboard
- Free tier available

### Docker
- Build once, run anywhere
- Isolated environment
- Easy scaling

### Render
- Manual setup required
- Free tier available
- Automatic HTTPS

## Next Steps

After deployment:
1. Set up monitoring
2. Configure alerts
3. Set up backups
4. Update documentation with production URLs
5. Announce launch!

