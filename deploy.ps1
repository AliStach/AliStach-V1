# Deployment Script for AliStach-V1
# This script commits changes and provides deployment instructions

Write-Host "=== AliStach-V1 Deployment Script ===" -ForegroundColor Cyan
Write-Host ""

# Check if we're in the project directory
$projectPath = "c:\Users\ch058\OneDrive\שולחן העבודה\AliStach"
if (-not (Test-Path $projectPath)) {
    Write-Host "ERROR: Project directory not found: $projectPath" -ForegroundColor Red
    exit 1
}

Set-Location $projectPath
Write-Host "Current directory: $(Get-Location)" -ForegroundColor Green

# Check if git is initialized
if (-not (Test-Path .git)) {
    Write-Host "Initializing Git repository..." -ForegroundColor Yellow
    git init
}

# Add all project files
Write-Host "Adding files to Git..." -ForegroundColor Yellow
git add .gitignore
git add api/
git add src/
git add vercel.json
git add requirements.txt
git add openapi-gpt.json
git add *.md

# Commit changes
Write-Host "Committing changes..." -ForegroundColor Yellow
git commit -m "Fix Vercel deployment: import paths, audit logger, error handling

- Fixed api/index.py to import from src.api.main (secured version)
- Added lazy initialization for audit_logger to prevent import-time failures
- Improved error handling in lifespan to prevent app crashes
- Fixed audit logger to use /tmp in serverless environments
- Health endpoint now works even if service is not initialized"

Write-Host ""
Write-Host "=== Deployment Options ===" -ForegroundColor Cyan
Write-Host ""
Write-Host "Option 1: Deploy via Vercel Dashboard" -ForegroundColor Green
Write-Host "  1. Go to https://vercel.com/dashboard"
Write-Host "  2. Select your project: alistach"
Write-Host "  3. Go to Deployments -> Redeploy latest"
Write-Host ""
Write-Host "Option 2: Deploy via Vercel CLI" -ForegroundColor Green
Write-Host "  Run: vercel --prod"
Write-Host ""
Write-Host "Option 3: Connect to Git and Auto-Deploy" -ForegroundColor Green
Write-Host "  1. Create a GitHub repository"
Write-Host "  2. Add remote: git remote add origin <your-repo-url>"
Write-Host "  3. Push: git push -u origin main"
Write-Host "  4. Connect repository to Vercel for auto-deploy"
Write-Host ""
Write-Host "=== Verify Deployment ===" -ForegroundColor Cyan
Write-Host "After deployment, test: curl https://alistach.vercel.app/health"
Write-Host ""

