# Render Deployment Guide

## Overview

Deploy the AliExpress Affiliate API Service to Render as a web service.

## Prerequisites

- Render account
- GitHub repository
- AliExpress API credentials

## Deployment Steps

### 1. Create Web Service

1. Go to [Render Dashboard](https://dashboard.render.com/)
2. Click "New +" → "Web Service"
3. Connect your GitHub repository

### 2. Configure Service

- **Name**: alistach-api
- **Environment**: Python 3
- **Build Command**: `pip install -r requirements.txt`
- **Start Command**: `gunicorn -w 4 -k uvicorn.workers.UvicornWorker src.api.main:app`
- **Plan**: Free or Starter

### 3. Environment Variables

Add environment variables:
```
ALIEXPRESS_APP_KEY=your_app_key
ALIEXPRESS_APP_SECRET=your_app_secret
ALIEXPRESS_TRACKING_ID=your_tracking_id
ADMIN_API_KEY=your_admin_key
```

### 4. Deploy

Click "Create Web Service" and wait for deployment.

## Configuration File

### render.yaml
```yaml
services:
  - type: web
    name: alistach-api
    env: python
    buildCommand: pip install -r requirements.txt
    startCommand: gunicorn -w 4 -k uvicorn.workers.UvicornWorker src.api.main:app
    envVars:
      - key: ALIEXPRESS_APP_KEY
        sync: false
      - key: ALIEXPRESS_APP_SECRET
        sync: false
```

## Advantages

- No function timeout limits
- Persistent disk storage
- WebSocket support
- Better for long-running requests

## Verification

```bash
curl https://alistach-api.onrender.com/health
```

---

*Last Updated: December 4, 2025*
