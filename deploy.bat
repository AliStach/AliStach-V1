@echo off
REM Deployment script for AliStach-V1 to Vercel

echo ========================================
echo AliStach-V1 - Vercel Deployment
echo ========================================
echo.

cd /d "%~dp0"
echo Current directory: %CD%
echo.

echo Deploying to Vercel production...
vercel --prod --yes

echo.
echo ========================================
echo Deployment complete!
echo ========================================
echo.
echo Next steps:
echo 1. Check deployment status in Vercel dashboard
echo 2. Test health endpoint: curl https://alistach.vercel.app/health
echo 3. Verify environment variables are set in Vercel
echo.

pause

