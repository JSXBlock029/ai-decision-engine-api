@echo off
REM Deploy API Locally (No external tools needed)
REM Starts API server on localhost

echo ========================================
echo DEPLOYING API LOCALLY
echo ========================================
echo.

cd /d "%~dp0\.."

echo [1/3] Testing API...
python api\test_local.py
if %ERRORLEVEL% NEQ 0 (
    echo ❌ Tests failed!
    pause
    exit /b 1
)
echo ✅ Tests passed
echo.

echo [2/3] Installing dependencies...
pip install fastapi uvicorn python-multipart -q
echo ✅ Dependencies installed
echo.

echo [3/3] Starting API server...
echo.
echo API will be available at:
echo   http://localhost:8000
echo.
echo API Documentation at:
echo   http://localhost:8000/docs
echo.
echo Press Ctrl+C to stop the server
echo.

cd api
python -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload

pause

