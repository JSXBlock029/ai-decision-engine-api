# API Troubleshooting Guide

Common issues and solutions for the AI Decision Engine API.

## Quick Diagnostics

### Check API Status
```bash
# Health check
curl http://localhost:8000/health

# Or use Python
python -c "import requests; print(requests.get('http://localhost:8000/health').json())"
```

### Check Server Logs
```bash
# If running with uvicorn
# Check terminal output for errors
```

## Common Issues

### 1. API Not Starting

**Symptoms:**
- Connection refused
- Port already in use
- Import errors

**Solutions:**
1. Check if port is available:
   ```bash
   netstat -ano | findstr :8000
   ```

2. Kill process using port:
   ```bash
   # Find PID from above command, then:
   taskkill /PID <pid> /F
   ```

3. Verify Python version:
   ```bash
   python --version  # Needs 3.11+
   ```

4. Install dependencies:
   ```bash
   pip install -r api/requirements.txt
   ```

5. Test imports:
   ```bash
   python -c "from api.main import app; print('OK')"
   ```

### 2. 401 Unauthorized Errors

**Symptoms:**
- 401 status code
- "API key required" error

**Solutions:**
1. For development, auth is disabled - check server is running latest code
2. Restart server completely:
   ```bash
   Get-Process python | Stop-Process
   python -m uvicorn api.main:app --host 0.0.0.0 --port 8000
   ```
3. Clear Python cache:
   ```bash
   Remove-Item -Recurse -Force __pycache__
   ```

### 3. Validation Errors (422)

**Symptoms:**
- 422 status code
- "Validation error" message

**Solutions:**
1. Check request format matches API spec
2. Verify category is valid:
   - STRATEGIC
   - OPERATIONAL
   - FINANCIAL
   - MARKETING
   - RND
   - COMPLIANCE
3. Ensure amount is a number (not string)
4. Check description length (max 1000 characters)
5. Review API documentation: `api/INTEGRATION_GUIDE.md`

### 4. Import Errors

**Symptoms:**
- ModuleNotFoundError
- ImportError

**Solutions:**
1. Install all dependencies:
   ```bash
   pip install -r requirements.txt
   pip install -r api/requirements.txt
   ```
2. Verify files exist:
   - `ai_decision_engine.py`
   - `ai_memory_system.py`
   - `autonomy_tracker.py`
3. Check Python path

### 5. Test Failures

**Symptoms:**
- Tests failing
- Connection errors

**Solutions:**
1. Ensure API server is running:
   ```bash
   python -m uvicorn api.main:app
   ```
2. Run local tests first:
   ```bash
   python api/test_local.py
   ```
3. Check server logs for errors
4. Verify all dependencies installed

### 6. Deployment Issues

**Symptoms:**
- Deployment fails
- Build errors

**Solutions:**
1. Check environment variables are set
2. Verify Dockerfile syntax
3. Check platform requirements
4. Review deployment logs
5. Test locally first:
   ```bash
   scripts/deploy_local_all.bat
   ```

## Getting Help

1. Check logs: Look at server output for error messages
2. Verify setup: Run `python verify_setup.py`
3. Test locally: Use `scripts/deploy_local_all.bat`
4. Review docs: Check `api/INTEGRATION_GUIDE.md`

## Diagnostic Commands

```bash
# Check system
python verify_setup.py

# Test components
python api/test_local.py

# Monitor system
python monitor_system.py

# Check API health
python api/health_monitor.py
```
