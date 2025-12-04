# Vercel Deployment Guide

## Overview

Deploy the AliExpress Affiliate API Service to Vercel as serverless functions.

## Prerequisites

- Vercel account
- GitHub repository
- AliExpress API credentials

## Deployment Steps

### 1. Connect Repository

1. Go to [Vercel Dashboard](https://vercel.com/dashboard)
2. Click "New Project"
3. Import your GitHub repository
4. Select the repository

### 2. Configure Environment Variables

Add the following environment variables in Vercel:

```
ALIEXPRESS_APP_KEY=your_app_key
ALIEXPRESS_APP_SECRET=your_app_secret
ALIEXPRESS_TRACKING_ID=your_tracking_id
ADMIN_API_KEY=your_admin_key
```

### 3. Deploy

Click "Deploy" and wait for the build to complete.

## Configuration Files

### vercel.json
```json
{
  "version": 2,
  "builds": [
    {
      "src": "api/index.py",
      "use": "@vercel/python"
    }
  ],
  "routes": [
    {
      "src": "/(.*)",
      "dest": "api/index.py"
    }
  ]
}
```

## Verification

Test your deployment:
```bash
curl https://your-project.vercel.app/health
```

## Troubleshooting

### Function Timeout
- Vercel free tier has 10-second timeout
- Optimize slow endpoints
- Consider upgrading to Pro

### Environment Variables
- Ensure all required variables are set
- Check for typos in variable names
- Redeploy after changing variables

---

*Last Updated: December 4, 2025*
