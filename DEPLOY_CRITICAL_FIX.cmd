@echo off
echo ========================================
echo CRITICAL FIX - Module-Level SecurityManager
echo ========================================
echo.
echo ACTUAL ROOT CAUSE:
echo   src/api/main.py was calling get_security_manager()
echo   at module level (during import)
echo   This created SecurityManager which tried to access
echo   filesystem for audit_logger SQLite database
echo   Result: FUNCTION_INVOCATION_FAILED
echo.
echo FIX APPLIED:
echo   1. Removed get_security_manager() call at module level
echo   2. Set security_manager = None (just a variable)
echo   3. Fixed CORS to use environment variable directly
echo   4. No filesystem access during import
echo.
echo ========================================
echo Staging Changes...
echo ========================================
git add src/api/main.py
git add CRITICAL_FIX.md
git add api/minimal_test.py

echo.
git status --short

echo.
echo ========================================
echo Creating Commit...
echo ========================================
git commit -m "fix: Remove module-level SecurityManager instantiation in main.py - CRITICAL FIX for FUNCTION_INVOCATION_FAILED"

echo.
echo ========================================
echo Pushing to Main...
echo ========================================
git push origin main

echo.
echo ========================================
echo Deployment Triggered!
echo ========================================
echo.
echo This was the ACTUAL root cause!
echo.
echo Monitor at: https://vercel.com/dashboard
echo.
echo Expected in logs:
echo   [INIT] ✓ Successfully imported main app
echo.
echo Wait 2-3 minutes, then test:
echo.
echo 1. Health Check:
echo    curl https://alistach.vercel.app/health
echo    Expected: {"status": "healthy", ...}
echo.
echo 2. OpenAPI Spec:
echo    curl https://alistach.vercel.app/openapi-gpt.json
echo    Expected: Valid JSON
echo.
echo 3. Interactive Docs:
echo    https://alistach.vercel.app/docs
echo    Expected: Swagger UI loads
echo.
echo ========================================
echo ALL FIXES APPLIED:
echo ========================================
echo   1. SecurityManager in middleware - Lazy init
echo   2. SecurityManager in main.py - Removed module-level call
echo   3. ImageProcessingService - Fixed torch check
echo   4. Logging - Serverless-aware
echo   5. Dependencies - Pure Python
echo   6. CORS - Environment variable
echo.
pause
