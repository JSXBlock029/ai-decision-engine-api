@echo off
REM Automated Landing Page Deployment
REM Uses Netlify CLI for automatic deployment

echo ========================================
echo DEPLOYING LANDING PAGE (AUTOMATED)
echo ========================================
echo.

cd /d "%~dp0\.."

echo Step 1: Testing landing page...
if not exist "saas_landing\index.html" (
    echo ❌ Landing page not found!
    pause
    exit /b 1
)
echo ✅ Landing page found
echo.

echo Step 2: Checking Netlify CLI...
where netlify >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo ❌ Netlify CLI not installed!
    echo.
    echo Run: scripts\setup_deployment.bat
    pause
    exit /b 1
)
echo ✅ Netlify CLI found
echo.

echo Step 3: Deploying to Netlify...
echo.
echo NOTE: First time requires:
echo   - netlify login (one-time)
echo   - netlify init (one-time)
echo.
echo Attempting automatic deployment...
echo.

cd saas_landing

REM Check if already initialized
if exist "netlify.toml" (
    echo ✅ Netlify configured, deploying...
    netlify deploy --prod
) else (
    echo ℹ️  First time setup needed
    echo.
    echo Please run these commands manually:
    echo   1. netlify login
    echo   2. netlify init
    echo   3. netlify deploy --prod
    echo.
    echo Or use: netlify deploy --dir=. --prod
    echo.
    
    REM Try direct deploy without init
    echo Attempting direct deploy...
    netlify deploy --dir=. --prod
)

cd ..

if %ERRORLEVEL% EQU 0 (
    echo.
    echo ========================================
    echo ✅ DEPLOYMENT SUCCESSFUL!
    echo ========================================
    echo.
    echo Landing page is now live!
    echo Check the URL shown above.
) else (
    echo.
    echo ========================================
    echo ⚠️  Deployment needs manual step
    echo ========================================
    echo.
    echo If this is first time:
    echo   1. Run: netlify login
    echo   2. Run: netlify init (in saas_landing folder)
    echo   3. Run this script again
    echo.
    echo Or deploy manually:
    echo   cd saas_landing
    echo   netlify deploy --dir=. --prod
)

echo.
pause

