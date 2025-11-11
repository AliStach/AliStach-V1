@echo off
echo ========================================
echo FINAL FIX - FUNCTION_INVOCATION_FAILED
echo ========================================
echo.
echo ROOT CAUSE: Module-level SecurityManager instantiation
echo           causing filesystem access during import
echo.
echo FIX APPLIED: Lazy initialization pattern
echo.
echo ========================================
echo Files Changed:
echo ========================================
echo   1. src/middleware/security.py - Lazy init SecurityManager
echo   2. src/utils/logging_config.py - Serverless-aware logging
echo   3. requirements.txt - Pure Python dependencies
echo   4. src/middleware/audit_logger.py - Lazy init AuditLogger
echo.
echo ========================================
echo Staging Changes...
echo ========================================
git add src/middleware/security.py
git add src/utils/logging_config.py
git add requirements.txt
git add src/middleware/audit_logger.py
git add ROOT_CAUSE_FIX_SUMMARY.md
git add deploy_final_fix.cmd

echo.
echo ========================================
echo Current Status:
echo ========================================
git status --short

echo.
echo ========================================
echo Creating Commit...
echo ========================================
git commit -m "fix: Lazy initialization of SecurityManager to prevent FUNCTION_INVOCATION_FAILED - Module-level instantiation was causing filesystem access during import"

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
echo Monitor at: https://vercel.com/dashboard
echo.
echo Expected in Vercel logs:
echo   [INIT] Starting Vercel function initialization
echo   [INIT] Attempting to import src.api.main...
echo   [INIT] ✓ Successfully imported main app  ^<-- THIS SHOULD APPEAR
echo   [INIT] Final app type: ^<class 'fastapi.applications.FastAPI'^>
echo.
echo Once deployed (2-3 minutes), verify:
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
echo 4. Check Logs:
echo    - No FUNCTION_INVOCATION_FAILED errors
echo    - No import errors
echo    - No filesystem permission errors
echo.
echo ========================================
echo ROOT CAUSE SUMMARY
echo ========================================
echo.
echo PROBLEM:
echo   SecurityManager was instantiated at module level
echo   This triggered audit_logger initialization
echo   audit_logger tried to create SQLite database
echo   Filesystem access failed during import phase
echo   Result: FUNCTION_INVOCATION_FAILED
echo.
echo SOLUTION:
echo   Changed to lazy initialization pattern
echo   SecurityManager only created on first request
echo   No filesystem access during import
echo   Result: Import succeeds, app works
echo.
pause
