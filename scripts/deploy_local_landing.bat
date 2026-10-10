@echo off
REM Deploy Landing Page Locally (No external tools needed)
REM Starts local web server

echo ========================================
echo DEPLOYING LANDING PAGE LOCALLY
echo ========================================
echo.

cd /d "%~dp0\.."

echo [1/2] Checking landing page...
if not exist "saas_landing\index.html" (
    echo ❌ Landing page not found!
    pause
    exit /b 1
)
echo ✅ Landing page found
echo.

echo [2/2] Starting local server...
echo.
echo Landing page will be available at:
echo   http://localhost:3000
echo.
echo Opening in browser...
echo.
echo Press Ctrl+C to stop the server
echo.

cd saas_landing
python -m http.server 3000
start http://localhost:3000

pause

