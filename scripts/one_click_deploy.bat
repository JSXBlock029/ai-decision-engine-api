@echo off
REM ONE-CLICK FULLY AUTOMATED DEPLOYMENT
REM Maximum automation - just run this!

echo ========================================
echo 🤖 ONE-CLICK AUTOMATED DEPLOYMENT
echo ========================================
echo.
echo This script will automatically:
echo   ✓ Verify system
echo   ✓ Run all tests
echo   ✓ Deploy landing page
echo   ✓ Deploy API
echo   ✓ Verify deployments
echo   ✓ Start monitoring
echo.
echo Press any key to start or Ctrl+C to cancel...
pause >nul
echo.

cd /d "%~dp0\.."

REM Run full automated deployment
call scripts\full_auto_deploy.bat

echo.
echo ========================================
echo 🎉 DEPLOYMENT COMPLETE!
echo ========================================
echo.
echo Everything has been deployed automatically!
echo.
echo Services:
echo   - Landing Page: Check Netlify dashboard
echo   - API: Check Heroku dashboard
echo.
echo Want to start monitoring? (Y/N)
set /p monitor="> "
if /i "%monitor%"=="Y" (
    echo.
    echo Starting automated monitoring...
    start /b scripts\auto_monitor.bat
    echo Monitoring started in background.
)

echo.
pause

