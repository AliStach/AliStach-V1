# Vercel Alias Setup Script (PowerShell)
# This script sets up the permanent alias for the AliStach deployment

Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "Vercel Alias Setup for AliStach" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host ""

# Check if Vercel CLI is installed
$vercelInstalled = Get-Command vercel -ErrorAction SilentlyContinue

if (-not $vercelInstalled) {
    Write-Host "❌ Vercel CLI is not installed" -ForegroundColor Red
    Write-Host "Installing Vercel CLI..." -ForegroundColor Yellow
    npm install -g vercel
} else {
    Write-Host "✅ Vercel CLI is installed" -ForegroundColor Green
}

Write-Host ""

# Login to Vercel
Write-Host "Logging in to Vercel..." -ForegroundColor Yellow
vercel login

Write-Host ""
Write-Host "Linking to project..." -ForegroundColor Yellow
vercel link

Write-Host ""
Write-Host "Setting permanent alias..." -ForegroundColor Yellow
Write-Host "Alias: alistach.vercel.app" -ForegroundColor Cyan
Write-Host "Target: aliexpress-api-proxy.vercel.app" -ForegroundColor Cyan
Write-Host ""

# Set the alias
vercel alias set aliexpress-api-proxy.vercel.app alistach.vercel.app

Write-Host ""
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "Verification" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host ""

# Test the alias
Write-Host "Testing alias..." -ForegroundColor Yellow
Write-Host ""

Write-Host "1. Testing root endpoint:" -ForegroundColor Cyan
try {
    $response = Invoke-WebRequest -Uri "https://alistach.vercel.app/" -UseBasicParsing
    Write-Host "   Status: $($response.StatusCode)" -ForegroundColor Green
    $content = $response.Content | ConvertFrom-Json
    Write-Host "   Service: $($content.service)" -ForegroundColor White
    Write-Host "   Version: $($content.version)" -ForegroundColor White
} catch {
    Write-Host "   Error: $($_.Exception.Message)" -ForegroundColor Red
}
Write-Host ""

Write-Host "2. Testing health endpoint:" -ForegroundColor Cyan
try {
    $response = Invoke-WebRequest -Uri "https://alistach.vercel.app/health" -UseBasicParsing
    Write-Host "   Status: $($response.StatusCode)" -ForegroundColor Green
} catch {
    Write-Host "   Status: $($_.Exception.Response.StatusCode.value__)" -ForegroundColor Yellow
    Write-Host "   Note: 503 is expected if environment variables are not set" -ForegroundColor Yellow
}
Write-Host ""

Write-Host "3. Testing system info:" -ForegroundColor Cyan
try {
    $response = Invoke-WebRequest -Uri "https://alistach.vercel.app/system/info" -UseBasicParsing
    Write-Host "   Status: $($response.StatusCode)" -ForegroundColor Green
} catch {
    Write-Host "   Status: $($_.Exception.Response.StatusCode.value__)" -ForegroundColor Yellow
}
Write-Host ""

Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "✅ Alias setup complete!" -ForegroundColor Green
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Your API is now accessible at:" -ForegroundColor White
Write-Host "  https://alistach.vercel.app" -ForegroundColor Cyan
Write-Host ""
Write-Host "Documentation:" -ForegroundColor White
Write-Host "  https://alistach.vercel.app/docs" -ForegroundColor Cyan
Write-Host ""
