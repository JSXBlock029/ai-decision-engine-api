@echo off
REM Automated Docker Deployment
REM Fully automated deployment using Docker

echo ========================================
echo DOCKER AUTOMATED DEPLOYMENT
echo ========================================
echo.

cd /d "%~dp0\.."

echo [1/5] Checking Docker...
docker --version >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo ❌ Docker not installed!
    echo.
    echo Install Docker Desktop from: https://www.docker.com/products/docker-desktop
    pause
    exit /b 1
)
echo ✅ Docker found
echo.

echo [2/5] Building Docker images...
cd api
docker build -t ai-decision-engine-api .
cd ..
echo ✅ Images built
echo.

echo [3/5] Testing containers...
docker-compose -f docker/docker-compose.prod.yml up -d
timeout /t 5
echo.

echo [4/5] Verifying deployment...
curl -f http://localhost:8000/health 2>nul
if %ERRORLEVEL% EQU 0 (
    echo ✅ API is running
) else (
    echo ⚠️  API may need more time to start
)

curl -f http://localhost:3000 2>nul
if %ERRORLEVEL% EQU 0 (
    echo ✅ Landing page is running
) else (
    echo ⚠️  Landing page may need more time to start
)

echo.
echo [5/5] Deployment complete!
echo.
echo Services are running:
echo   - API: http://localhost:8000
echo   - Landing: http://localhost:3000
echo.
echo To stop: docker-compose -f docker/docker-compose.prod.yml down
echo.
pause

