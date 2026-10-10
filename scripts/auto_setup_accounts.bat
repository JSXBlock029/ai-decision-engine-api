@echo off
REM Automated Account Setup Guide
REM Opens browser to create accounts automatically

echo ========================================
echo AUTOMATED ACCOUNT SETUP
echo ========================================
echo.
echo This script will help you create accounts automatically.
echo.

echo Creating accounts...
echo.

echo [1/4] Opening Netlify signup...
start https://app.netlify.com/signup
timeout /t 3

echo [2/4] Opening Heroku signup...
start https://signup.heroku.com
timeout /t 3

echo [3/4] Opening ProductHunt signup...
start https://www.producthunt.com/signup
timeout /t 3

echo [4/4] Opening IndieHackers signup...
start https://www.indiehackers.com/signup
timeout /t 3

echo.
echo ========================================
echo Account Setup Complete
echo ========================================
echo.
echo Please:
echo   1. Complete signups in the opened browsers
echo   2. Get your API tokens from:
echo      - Netlify: Settings ^> Applications ^> New access token
echo      - Heroku: Account Settings ^> API Key
echo   3. Save tokens securely
echo   4. Run: scripts\configure_secrets.bat
echo.
pause

