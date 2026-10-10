@echo off
echo ========================================
echo AI DECISION ENGINE - Quick Start
echo ========================================
echo.

echo [1] Starting API Server...
start "API Server" cmd /k "cd api && python main.py"
timeout /t 3 /nobreak >nul

echo [2] Starting Waitlist Backend...
start "Waitlist Backend" cmd /k "cd saas_landing && python waitlist_backend.py"
timeout /t 3 /nobreak >nul

echo [3] Opening Landing Page...
start "" "saas_landing\index.html"

echo.
echo ========================================
echo All services starting...
echo.
echo API: http://localhost:8000
echo API Docs: http://localhost:8000/docs
echo Waitlist API: http://localhost:8001
echo Landing Page: Opened in browser
echo.
echo Press any key to exit...
pause >nul

