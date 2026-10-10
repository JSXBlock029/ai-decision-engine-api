@echo off
REM Automated Deployment Script for Windows
REM Handles deployment to various platforms

echo ========================================
echo AI DECISION ENGINE - AUTOMATED DEPLOYMENT
echo ========================================
echo.

cd /d "%~dp0\.."

REM Check prerequisites
echo Checking prerequisites...
python --version >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Python not found!
    pause
    exit /b 1
)
echo [OK] Python found

git --version >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo [WARN] Git not found (optional)
) else (
    echo [OK] Git found
)

echo.

REM Menu
echo Select deployment platform:
echo   1. Local (for testing)
echo   2. Docker
echo   3. Railway
echo   4. Heroku
echo   5. Render (manual instructions)
echo   6. Create deployment package
echo.
set /p choice="Enter choice (1-6): "

if "%choice%"=="1" goto local
if "%choice%"=="2" goto docker
if "%choice%"=="3" goto railway
if "%choice%"=="4" goto heroku
if "%choice%"=="5" goto render
if "%choice%"=="6" goto package
goto end

:local
echo.
echo Starting local deployment...
start "API Server" cmd /k "cd /d %~dp0\.. && python -m uvicorn api.main:app --host 0.0.0.0 --port 8000 --reload"
timeout /t 3 /nobreak >nul
echo.
echo [OK] API server started
echo      URL: http://localhost:8000
echo      Docs: http://localhost:8000/docs
goto end

:docker
echo.
echo Building Docker image...
docker --version >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Docker not found!
    echo Install Docker Desktop from: https://www.docker.com/products/docker-desktop
    pause
    exit /b 1
)

docker build -t ai-decision-engine -f api/Dockerfile.prod .
if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Docker build failed!
    pause
    exit /b 1
)

echo.
echo [OK] Docker image built
echo Run with: docker run -p 8000:8000 ai-decision-engine
goto end

:railway
echo.
echo Deploying to Railway...
railway --version >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Railway CLI not found!
    echo Install: npm install -g @railway/cli
    pause
    exit /b 1
)

railway up
if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Railway deployment failed!
    pause
    exit /b 1
)

echo [OK] Deployed to Railway
goto end

:heroku
echo.
echo Deploying to Heroku...
heroku --version >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Heroku CLI not found!
    echo Install from: https://devcenter.heroku.com/articles/heroku-cli
    pause
    exit /b 1
)

set /p app_name="Enter Heroku app name (or press Enter for default): "
if "%app_name%"=="" set app_name=ai-decision-engine-api

heroku create %app_name% 2>nul
git push heroku main
if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Heroku deployment failed!
    pause
    exit /b 1
)

echo [OK] Deployed to Heroku: https://%app_name%.herokuapp.com
goto end

:render
echo.
echo Render Deployment Instructions:
echo.
echo 1. Go to render.com and sign up/login
echo 2. Click "New +" and select "Web Service"
echo 3. Connect your GitHub repository
echo 4. Configure:
echo    - Build Command: pip install -r api/requirements.txt
echo    - Start Command: uvicorn api.main:app --host 0.0.0.0 --port $PORT
echo 5. Add environment variables from api/.env.example
echo 6. Deploy!
echo.
goto end

:package
echo.
echo Creating deployment package...
if not exist "deploy_package" mkdir deploy_package

REM Copy necessary files
xcopy /E /I /Y api deploy_package\api
xcopy /Y ai_decision_engine.py deploy_package\
xcopy /Y ai_memory_system.py deploy_package\
xcopy /Y autonomy_tracker.py deploy_package\

echo [OK] Deployment package created in: deploy_package\
goto end

:end
echo.
echo ========================================
echo Deployment process complete
echo ========================================
pause

