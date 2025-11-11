@echo off
echo ========================================
echo FINAL FIX - ImageProcessingService NameError
echo ========================================
echo.
echo ROOT CAUSE FOUND:
echo   ImageProcessingService.__init__ referenced torch.cuda
echo   even when torch import failed
echo   Result: NameError during import
echo.
echo FIX APPLIED:
echo   1. Check CLIP_AVAILABLE before using torch
echo   2. Added runtime.txt for Python 3.12
echo   3. Defensive coding in __init__
echo.
echo ========================================
echo Staging Changes...
echo ========================================
git add src/services/image_processing_service.py
git add runtime.txt
git add FINAL_DEPLOYMENT_FIX.md
git add test_import_vercel.py
git add DEPLOY_NOW.cmd
git add ROOT_CAUSE_FIX_SUMMARY.md

echo.
git status --short

echo.
echo ========================================
echo Creating Commit...
echo ========================================
git commit -m "fix: Prevent NameError in ImageProcessingService when torch unavailable - Final fix for FUNCTION_INVOCATION_FAILED"

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
echo Expected in logs:
echo   [INIT] ✓ Successfully imported main app
echo.
echo Once deployed (2-3 minutes):
echo.
echo 1. Test Health:
echo    curl https://alistach.vercel.app/health
echo    Expected: {"status": "healthy", ...}
echo.
echo 2. Test OpenAPI:
echo    curl https://alistach.vercel.app/openapi-gpt.json
echo    Expected: Valid JSON
echo.
echo 3. Test Docs:
echo    https://alistach.vercel.app/docs
echo    Expected: Swagger UI loads
echo.
echo 4. If Still Fails:
echo    curl https://alistach.vercel.app/debug
echo    Shows full error details
echo.
pause
