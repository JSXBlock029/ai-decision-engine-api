@echo off
REM Automated Full Deployment
REM Deploys both landing page and API automatically

echo ========================================
echo AI DECISION ENGINE - AUTOMATED DEPLOYMENT
echo ========================================
echo.
echo This script will deploy:
echo   1. Landing Page (Netlify)
echo   2. API Service (Heroku)
echo.
echo Press any key to continue or Ctrl+C to cancel...
pause >nul
echo.

echo ========================================
echo [1/2] Deploying Landing Page
echo ========================================
echo.
call scripts\deploy_landing_auto.bat

echo.
echo ========================================
echo [2/2] Deploying API
echo ========================================
echo.
call scripts\deploy_api_auto.bat

echo.
echo ========================================
echo DEPLOYMENT COMPLETE
echo ========================================
echo.
echo Check the output above for deployment status.
echo.
echo If first time, you may need to:
echo   - Login to platforms (one-time)
echo   - Initialize apps (one-time)
echo   - Run scripts again
echo.
pause

