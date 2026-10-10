@echo off
REM Check Deployment Status
REM Shows current deployment status

echo ========================================
echo DEPLOYMENT STATUS CHECK
echo ========================================
echo.

cd /d "%~dp0\.."

echo [1/4] Checking system status...
python verify_setup.py
echo.

echo [2/4] Checking API components...
python api\test_local.py
echo.

echo [3/4] Checking for deployment processes...
tasklist | findstr /i "python netlify heroku docker"
echo.

echo [4/4] Deployment Status:
echo.

REM Check if API is running locally
curl -f http://localhost:8000/health 2>nul
if %ERRORLEVEL% EQU 0 (
    echo ✅ API: Running locally on http://localhost:8000
) else (
    echo ⚠️  API: Not running locally
)

echo.
echo Checking remote deployments...
echo.
echo API (Heroku):
curl -f https://ai-decision-engine-api.herokuapp.com/health 2>nul
if %ERRORLEVEL% EQU 0 (
    echo ✅ API: Deployed and healthy
) else (
    echo ⚠️  API: Not deployed or not accessible
)

echo.
echo Landing Page (Netlify):
echo ⚠️  Check Netlify dashboard for status
echo    URL: https://app.netlify.com
echo.

pause

