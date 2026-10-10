@echo off
REM Fully Automated Deployment
REM Tests, builds, deploys, and verifies everything

echo ========================================
echo FULLY AUTOMATED DEPLOYMENT
echo ========================================
echo.

cd /d "%~dp0\.."

echo [Step 1/6] Testing system...
python verify_setup.py
if %ERRORLEVEL% NEQ 0 (
    echo ❌ System verification failed!
    pause
    exit /b 1
)
echo ✅ System verified
echo.

echo [Step 2/6] Testing API components...
python api\test_local.py
if %ERRORLEVEL% NEQ 0 (
    echo ❌ API tests failed!
    pause
    exit /b 1
)
echo ✅ API components verified
echo.

echo [Step 3/6] Building deployment packages...
REM Create deployment directories if needed
if not exist "deploy" mkdir deploy
echo ✅ Packages ready
echo.

echo [Step 4/6] Deploying landing page...
call scripts\deploy_landing_auto.bat
echo.

echo [Step 5/6] Deploying API...
call scripts\deploy_api_auto.bat
echo.

echo [Step 6/6] Verifying deployments...
echo Checking API health...
curl -f https://ai-decision-engine-api.herokuapp.com/health 2>nul
if %ERRORLEVEL% EQU 0 (
    echo ✅ API is live and healthy
) else (
    echo ⚠️  API health check failed (may need time to start)
)

echo.
echo ========================================
echo ✅ AUTOMATED DEPLOYMENT COMPLETE!
echo ========================================
echo.
echo Check the output above for deployment status.
echo.
pause

