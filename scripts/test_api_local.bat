@echo off
REM Test API components locally without starting server

echo ========================================
echo AI DECISION ENGINE - LOCAL API TEST
echo ========================================
echo.

cd /d "%~dp0\.."
cd api

echo Testing decision engine components...
python test_local.py

if %ERRORLEVEL% EQU 0 (
    echo.
    echo ========================================
    echo ✅ Local tests passed!
    echo ========================================
    echo.
    echo Next step: Start API server and test endpoints
    echo   Run: api\run_api.bat
    echo   Then: python api\test_api.py
) else (
    echo.
    echo ========================================
    echo ❌ Local tests failed!
    echo ========================================
    echo.
    echo Please fix the errors above before proceeding.
)

pause

