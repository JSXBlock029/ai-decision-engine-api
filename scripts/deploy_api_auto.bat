@echo off
REM Automated API Deployment
REM Uses Heroku CLI for automatic deployment

echo ========================================
echo DEPLOYING API (AUTOMATED)
echo ========================================
echo.

cd /d "%~dp0\.."

echo Step 1: Testing API...
python api\test_local.py
if %ERRORLEVEL% NEQ 0 (
    echo ❌ API tests failed!
    pause
    exit /b 1
)
echo ✅ API tests passed
echo.

echo Step 2: Checking Heroku CLI...
where heroku >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo ❌ Heroku CLI not installed!
    echo.
    echo Run: scripts\setup_deployment.bat
    pause
    exit /b 1
)
echo ✅ Heroku CLI found
echo.

echo Step 3: Preparing API for deployment...
cd api

REM Check if Heroku app exists
if exist "Procfile" (
    echo ✅ Procfile found
) else (
    echo Creating Procfile...
    echo web: uvicorn main:app --host 0.0.0.0 --port $PORT > Procfile
)

echo.
echo Step 4: Deploying to Heroku...
echo.
echo NOTE: First time requires:
echo   - heroku login (one-time)
echo   - heroku create (one-time)
echo.

REM Try to deploy
heroku info >nul 2>&1
if %ERRORLEVEL% EQU 0 (
    echo ✅ Heroku app configured, deploying...
    git add .
    git commit -m "Deploy API" 2>nul
    heroku git:remote -a ai-decision-engine-api 2>nul
    git push heroku main
) else (
    echo ℹ️  First time setup needed
    echo.
    echo Please run these commands:
    echo   1. heroku login
    echo   2. heroku create ai-decision-engine-api
    echo   3. heroku config:set API_KEY=your_key
    echo   4. Run this script again
    echo.
    echo Or create app now:
    heroku create ai-decision-engine-api
    if %ERRORLEVEL% EQU 0 (
        echo ✅ App created! Setting environment...
        heroku config:set API_KEY=dev_key_123
        echo.
        echo Now deploying...
        git init
        git add .
        git commit -m "Initial commit"
        git push heroku main
    )
)

cd ..

if %ERRORLEVEL% EQU 0 (
    echo.
    echo ========================================
    echo ✅ DEPLOYMENT SUCCESSFUL!
    echo ========================================
    echo.
    echo API is now live!
    echo URL: https://ai-decision-engine-api.herokuapp.com
) else (
    echo.
    echo ========================================
    echo ⚠️  Deployment needs setup
    echo ========================================
    echo.
    echo First time steps:
    echo   1. heroku login
    echo   2. heroku create ai-decision-engine-api
    echo   3. heroku config:set API_KEY=your_key
    echo   4. Run this script again
)

echo.
pause

