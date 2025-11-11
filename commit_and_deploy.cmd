@echo off
echo ========================================
echo Committing Fix for FUNCTION_INVOCATION_FAILED
echo ========================================
echo.

git add src/api/main.py
git add FUNCTION_INVOCATION_FAILED_FIX.md
git status --short

echo.
echo ========================================
echo Creating commit...
echo ========================================
git commit -m "fix: Remove logging.basicConfig() from lifespan to fix FUNCTION_INVOCATION_FAILED"

echo.
echo ========================================
echo Pushing to main (triggers Vercel deployment)...
echo ========================================
git push origin main

echo.
echo ========================================
echo Deployment triggered!
echo ========================================
echo.
echo Monitor deployment at: https://vercel.com/dashboard
echo.
echo Once deployed, verify:
echo   1. Health: https://alistach.vercel.app/health
echo   2. OpenAPI: https://alistach.vercel.app/openapi-gpt.json
echo   3. Docs: https://alistach.vercel.app/docs
echo.
pause
