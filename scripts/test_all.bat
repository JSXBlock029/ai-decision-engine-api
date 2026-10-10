@echo off
echo ========================================
echo AI DECISION ENGINE - Test Suite
echo ========================================
echo.

echo [1] Testing Main System...
python run_system.py
echo.

echo [2] Testing API (if running)...
cd api
python test_api.py
cd ..
echo.

echo [3] Checking Memory Status...
python check_memory.py
echo.

echo [4] Generating Tweet...
python autonomous_tweet_scheduler.py
echo.

echo ========================================
echo All tests complete!
echo ========================================
pause

