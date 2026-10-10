@echo off
REM Start API server and run tests

echo ========================================
echo AI DECISION ENGINE API - START AND TEST
echo ========================================
echo.

cd /d "%~dp0\.."

echo Step 1: Testing local components...
cd api
python test_local.py
if %ERRORLEVEL% NEQ 0 (
    echo.
    echo ❌ Local tests failed! Fix errors before starting server.
    pause
    exit /b 1
)

echo.
echo ✅ Local tests passed!
echo.
echo ========================================
echo Starting API server...
echo ========================================
echo.
echo Server will start on http://localhost:8000
echo Press Ctrl+C to stop the server
echo.
echo After server starts, open another terminal and run:
echo   python api\test_api.py
echo.
echo OR visit http://localhost:8000/docs for API documentation
echo.
echo ========================================
echo.

REM Check if uvicorn is installed
python -c "import uvicorn" 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo Installing required packages...
    pip install fastapi uvicorn python-multipart
)

REM Start the server
python -m uvicorn api.main:app --host 0.0.0.0 --port 8000 --reload

pause

