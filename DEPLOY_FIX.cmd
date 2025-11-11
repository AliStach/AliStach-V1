@echo off
echo ============================================================
echo DEPLOYING FIX FOR FUNCTION_INVOCATION_FAILED
echo ============================================================
echo.
echo Changes:
echo   - runtime.txt: python-3.12 -^> python-3.11
echo   - Entry point: api/ultra_minimal.py (unchanged)
echo.
echo Rationale:
echo   Python 3.12 may not be fully supported by @vercel/python
echo   Python 3.11 is the recommended version for Vercel
echo.
echo ============================================================
echo.

echo [1/4] Committing changes...
git add runtime.txt DIAGNOSTIC_REPORT.md DEPLOY_FIX.cmd test_vercel_simulation.py
git commit -m "fix: Change Python runtime to 3.11 for Vercel compatibility"

echo.
echo [2/4] Pushing to repository...
git push origin main

echo.
echo [3/4] Deploying to Vercel...
echo Note: Deployment will take 2-3 minutes
echo.

REM Wait for deployment
timeout /t 180 /nobreak

echo.
echo [4/4] Testing endpoints...
echo.

echo Testing: https://alistach.vercel.app/health
curl -s https://alistach.vercel.app/health
echo.
echo.

echo Testing: https://alistach.vercel.app/
curl -s https://alistach.vercel.app/
echo.
echo.

echo ============================================================
echo DEPLOYMENT COMPLETE
echo ============================================================
echo.
echo If you see JSON responses above, the fix worked!
echo If you see FUNCTION_INVOCATION_FAILED, check:
echo   1. Vercel build logs
echo   2. DIAGNOSTIC_REPORT.md for next steps
echo.
pause
