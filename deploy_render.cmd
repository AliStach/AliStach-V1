@echo off
REM Render.com Deployment Script for Windows
REM This script helps you deploy to Render.com quickly

echo.
echo ========================================
echo   Render.com Deployment Helper
echo ========================================
echo.

REM Check if render.yaml exists
if not exist "render.yaml" (
    echo [ERROR] render.yaml not found!
    echo Please ensure render.yaml is in the project root.
    pause
    exit /b 1
)

echo [OK] render.yaml found
echo.

REM Check if git is initialized
if not exist ".git" (
    echo [ERROR] Not a git repository!
    echo Please initialize git first: git init
    pause
    exit /b 1
)

echo [OK] Git repository detected
echo.

REM Check for uncommitted changes
git diff-index --quiet HEAD -- 2>nul
if errorlevel 1 (
    echo [WARNING] You have uncommitted changes
    echo.
    set /p commit_choice="Do you want to commit them now? (y/n): "
    if /i "%commit_choice%"=="y" (
        set /p commit_msg="Enter commit message: "
        git add .
        git commit -m "%commit_msg%"
        echo [OK] Changes committed
    ) else (
        echo [WARNING] Proceeding with uncommitted changes...
    )
)

echo.
echo ========================================
echo   Pre-deployment Checklist
echo ========================================
echo.

REM Check if render.yaml is tracked
git ls-files --error-unmatch render.yaml >nul 2>&1
if errorlevel 1 (
    echo [WARNING] render.yaml is not tracked by git
    set /p add_choice="Add render.yaml to git? (y/n): "
    if /i "%add_choice%"=="y" (
        git add render.yaml
        git commit -m "feat: Add Render deployment configuration"
        echo [OK] render.yaml added and committed
    )
) else (
    echo [OK] render.yaml is tracked by git
)

echo.
echo ========================================
echo   Deployment Steps
echo ========================================
echo.
echo 1. Push your code to GitHub:
echo    git push origin main
echo.
echo 2. Go to Render Dashboard:
echo    https://dashboard.render.com/
echo.
echo 3. Create New Web Service:
echo    - Click 'New +' -^> 'Blueprint'
echo    - Connect your GitHub repository
echo    - Select 'AliStach-V1'
echo    - Render will detect render.yaml automatically
echo    - Click 'Apply'
echo.
echo 4. Configure Secret Environment Variables:
echo    In Render dashboard, add these secrets:
echo    - ALIEXPRESS_APP_KEY=your_app_key
echo    - ALIEXPRESS_APP_SECRET=your_app_secret
echo    - ADMIN_API_KEY=generate_random_key
echo    - JWT_SECRET_KEY=generate_random_key
echo.
echo 5. Deploy!
echo    Render will automatically build and deploy
echo.

set /p push_choice="Push to GitHub now? (y/n): "
if /i "%push_choice%"=="y" (
    echo.
    echo [INFO] Pushing to GitHub...
    git push origin main
    echo.
    echo [OK] Code pushed successfully!
    echo.
    echo Next steps:
    echo 1. Go to https://dashboard.render.com/
    echo 2. Follow steps 3-5 above
    echo 3. Your service will be live at: https://alistach-api.onrender.com
) else (
    echo.
    echo [INFO] Skipping push. You can push manually later:
    echo    git push origin main
)

echo.
echo ========================================
echo   Additional Resources
echo ========================================
echo.
echo For detailed instructions, see:
echo    DEPLOY_RENDER_GUIDE.md
echo.
echo [OK] Deployment preparation complete!
echo.
pause
