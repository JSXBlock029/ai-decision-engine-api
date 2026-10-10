@echo off
REM Automated Secret Configuration
REM Configures API keys and tokens for deployment

echo ========================================
echo CONFIGURING DEPLOYMENT SECRETS
echo ========================================
echo.
echo This will configure your API keys and tokens.
echo.

set /p NETLIFY_TOKEN="Enter Netlify Auth Token: "
set /p HEROKU_API_KEY="Enter Heroku API Key: "
set /p HEROKU_EMAIL="Enter Heroku Email: "

echo.
echo Configuring secrets...
echo.

REM Create .env files if needed
if not exist "api\.env" (
    echo NETLIFY_AUTH_TOKEN=%NETLIFY_TOKEN% > api\.env
    echo HEROKU_API_KEY=%HEROKU_API_KEY% >> api\.env
    echo HEROKU_EMAIL=%HEROKU_EMAIL% >> api\.env
    echo ✅ Created api\.env
)

REM For GitHub Actions (if using GitHub)
if exist ".github" (
    echo.
    echo To configure GitHub Secrets:
    echo   1. Go to your repository on GitHub
    echo   2. Settings ^> Secrets and variables ^> Actions
    echo   3. Add these secrets:
    echo      - NETLIFY_AUTH_TOKEN = %NETLIFY_TOKEN%
    echo      - HEROKU_API_KEY = %HEROKU_API_KEY%
    echo      - HEROKU_EMAIL = %HEROKU_EMAIL%
    echo.
)

echo.
echo ✅ Configuration complete!
echo.
echo Next: Run scripts\deploy_all.bat
echo.
pause

