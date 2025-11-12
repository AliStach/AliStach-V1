#!/bin/bash

# Vercel Alias Setup Script
# This script sets up the permanent alias for the AliStach deployment

echo "=========================================="
echo "Vercel Alias Setup for AliStach"
echo "=========================================="
echo ""

# Check if Vercel CLI is installed
if ! command -v vercel &> /dev/null; then
    echo "❌ Vercel CLI is not installed"
    echo "Installing Vercel CLI..."
    npm install -g vercel
fi

echo "✅ Vercel CLI is installed"
echo ""

# Login to Vercel
echo "Logging in to Vercel..."
vercel login

echo ""
echo "Linking to project..."
vercel link

echo ""
echo "Setting permanent alias..."
echo "Alias: alistach.vercel.app"
echo "Target: aliexpress-api-proxy.vercel.app"
echo ""

# Set the alias
vercel alias set aliexpress-api-proxy.vercel.app alistach.vercel.app

echo ""
echo "=========================================="
echo "Verification"
echo "=========================================="
echo ""

# Test the alias
echo "Testing alias..."
echo ""

echo "1. Testing root endpoint:"
curl -s https://alistach.vercel.app/ | head -n 5
echo ""

echo "2. Testing health endpoint:"
curl -s https://alistach.vercel.app/health | head -n 5
echo ""

echo "3. Testing system info:"
curl -s https://alistach.vercel.app/system/info | head -n 5
echo ""

echo "=========================================="
echo "✅ Alias setup complete!"
echo "=========================================="
echo ""
echo "Your API is now accessible at:"
echo "  https://alistach.vercel.app"
echo ""
echo "Documentation:"
echo "  https://alistach.vercel.app/docs"
echo ""
