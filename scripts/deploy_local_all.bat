@echo off
REM Deploy Everything Locally (No external tools needed)
REM Starts both API and Landing Page locally

echo ========================================
echo DEPLOYING ALL SERVICES LOCALLY
echo ========================================
echo.

cd /d "%~dp0\.."

echo Starting services...
echo.

echo [1/2] Starting API server...
start "API Server" cmd /k "cd /d %~dp0\.. && cd api && python -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload"

timeout /t 3 /nobreak >nul

echo [2/2] Starting Landing Page...
start "Landing Page" cmd /k "cd /d %~dp0\.. && cd saas_landing && python -m http.server 3000"

timeout /t 2 /nobreak >nul

echo.
echo ========================================
echo ✅ SERVICES RUNNING!
echo ========================================
echo.
echo API: http://localhost:8000
echo API Docs: http://localhost:8000/docs
echo Landing: http://localhost:3000
echo.
echo Opening in browser...
start http://localhost:8000/docs
start http://localhost:3000
echo.
echo Services are running in separate windows.
echo Close those windows to stop the services.
echo.
pause

