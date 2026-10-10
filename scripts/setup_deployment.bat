@echo off
REM Setup deployment environment - Automated by AI
REM This script prepares everything for automated deployment

echo ========================================
echo AI DECISION ENGINE - DEPLOYMENT SETUP
echo ========================================
echo.

echo This script will set up automated deployment.
echo.
echo Checking prerequisites...
echo.

REM Check for Node.js (needed for Netlify/Heroku CLIs)
where node >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo ❌ Node.js not found!
    echo.
    echo Please install Node.js from https://nodejs.org/
    echo Then run this script again.
    pause
    exit /b 1
) else (
    echo ✅ Node.js found
)

REM Check for Python
where python >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo ❌ Python not found!
    pause
    exit /b 1
) else (
    echo ✅ Python found
)

echo.
echo ========================================
echo Installing deployment tools...
echo ========================================
echo.

echo Installing Netlify CLI...
call npm install -g netlify-cli
if %ERRORLEVEL% EQU 0 (
    echo ✅ Netlify CLI installed
) else (
    echo ⚠️  Netlify CLI installation failed (may need admin rights)
)

echo.
echo Installing Heroku CLI...
call npm install -g heroku
if %ERRORLEVEL% EQU 0 (
    echo ✅ Heroku CLI installed
) else (
    echo ⚠️  Heroku CLI installation failed (may need admin rights)
)

echo.
echo ========================================
echo Setup Complete!
echo ========================================
echo.
echo Next steps:
echo 1. Login to Netlify: netlify login
echo 2. Login to Heroku: heroku login
echo 3. Run: scripts\deploy_all.bat
echo.
pause

