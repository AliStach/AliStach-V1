#!/bin/bash

# Render.com Deployment Script
# This script helps you deploy to Render.com quickly

set -e

echo "🚀 Render.com Deployment Helper"
echo "================================"
echo ""

# Check if render.yaml exists
if [ ! -f "render.yaml" ]; then
    echo "❌ Error: render.yaml not found!"
    echo "Please ensure render.yaml is in the project root."
    exit 1
fi

echo "✅ render.yaml found"
echo ""

# Check if git is initialized
if [ ! -d ".git" ]; then
    echo "❌ Error: Not a git repository!"
    echo "Please initialize git first: git init"
    exit 1
fi

echo "✅ Git repository detected"
echo ""

# Check for uncommitted changes
if ! git diff-index --quiet HEAD --; then
    echo "⚠️  Warning: You have uncommitted changes"
    echo ""
    read -p "Do you want to commit them now? (y/n) " -n 1 -r
    echo ""
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        echo ""
        read -p "Enter commit message: " commit_msg
        git add .
        git commit -m "$commit_msg"
        echo "✅ Changes committed"
    else
        echo "⚠️  Proceeding with uncommitted changes..."
    fi
fi

echo ""
echo "📋 Pre-deployment Checklist:"
echo "----------------------------"
echo ""

# Check if render.yaml is staged
if git ls-files --error-unmatch render.yaml > /dev/null 2>&1; then
    echo "✅ render.yaml is tracked by git"
else
    echo "⚠️  render.yaml is not tracked by git"
    read -p "Add render.yaml to git? (y/n) " -n 1 -r
    echo ""
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        git add render.yaml
        git commit -m "feat: Add Render deployment configuration"
        echo "✅ render.yaml added and committed"
    fi
fi

echo ""
echo "📝 Deployment Steps:"
echo "-------------------"
echo ""
echo "1. Push your code to GitHub:"
echo "   git push origin main"
echo ""
echo "2. Go to Render Dashboard:"
echo "   https://dashboard.render.com/"
echo ""
echo "3. Create New Web Service:"
echo "   - Click 'New +' → 'Blueprint'"
echo "   - Connect your GitHub repository"
echo "   - Select 'AliStach-V1'"
echo "   - Render will detect render.yaml automatically"
echo "   - Click 'Apply'"
echo ""
echo "4. Configure Secret Environment Variables:"
echo "   In Render dashboard, add these secrets:"
echo "   - ALIEXPRESS_APP_KEY=your_app_key"
echo "   - ALIEXPRESS_APP_SECRET=your_app_secret"
echo "   - ADMIN_API_KEY=generate_random_key"
echo "   - JWT_SECRET_KEY=generate_random_key"
echo ""
echo "5. Deploy!"
echo "   Render will automatically build and deploy"
echo ""

read -p "Push to GitHub now? (y/n) " -n 1 -r
echo ""
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo ""
    echo "🚀 Pushing to GitHub..."
    git push origin main
    echo ""
    echo "✅ Code pushed successfully!"
    echo ""
    echo "🌐 Next steps:"
    echo "1. Go to https://dashboard.render.com/"
    echo "2. Follow steps 3-5 above"
    echo "3. Your service will be live at: https://alistach-api.onrender.com"
else
    echo ""
    echo "ℹ️  Skipping push. You can push manually later:"
    echo "   git push origin main"
fi

echo ""
echo "📖 For detailed instructions, see:"
echo "   DEPLOY_RENDER_GUIDE.md"
echo ""
echo "✅ Deployment preparation complete!"
