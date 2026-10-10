@echo off
REM Automated Monitoring Script
REM Monitors deployments automatically

echo ========================================
echo AUTOMATED DEPLOYMENT MONITORING
echo ========================================
echo.

cd /d "%~dp0\.."

:monitor_loop
echo.
echo [%TIME%] Checking deployment health...
echo.

echo Checking API...
curl -f https://ai-decision-engine-api.herokuapp.com/health 2>nul
if %ERRORLEVEL% EQU 0 (
    echo ✅ API: HEALTHY
) else (
    echo ❌ API: DOWN or not responding
)

echo.
echo Checking Landing Page...
curl -f https://your-site.netlify.app 2>nul
if %ERRORLEVEL% EQU 0 (
    echo ✅ Landing Page: ACCESSIBLE
) else (
    echo ⚠️  Landing Page: Check URL manually
)

echo.
echo Waiting 60 seconds before next check...
echo Press Ctrl+C to stop monitoring...

timeout /t 60 /nobreak >nul
goto monitor_loop

