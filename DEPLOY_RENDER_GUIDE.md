# 🚀 Render.com Deployment Guide

**Project**: AliStach-V1 (AliExpress API Proxy)  
**Platform**: Render.com  
**Runtime**: Python 3.11  
**Framework**: FastAPI + Uvicorn + Gunicorn  
**Status**: Ready for deployment

---

## 📋 Table of Contents

1. [Prerequisites](#prerequisites)
2. [Quick Start](#quick-start)
3. [Step-by-Step Deployment](#step-by-step-deployment)
4. [Environment Variables Configuration](#environment-variables-configuration)
5. [Verification & Testing](#verification--testing)
6. [Troubleshooting](#troubleshooting)
7. [Monitoring & Logs](#monitoring--logs)
8. [Comparison: Render vs Vercel](#comparison-render-vs-vercel)

---

## 🎯 Prerequisites

### Required
- ✅ GitHub account with access to AliStach-V1 repository
- ✅ Render.com account (free tier available)
- ✅ AliExpress API credentials (App Key & App Secret)

### Optional
- ⚠️ Custom domain (for production)
- ⚠️ Redis instance (for advanced caching)

---

## ⚡ Quick Start

### Option 1: Deploy via render.yaml (Recommended)

1. **Push render.yaml to your repository**
   ```bash
   git add render.yaml
   git commit -m "feat: Add Render deployment configuration"
   git push origin main
   ```

2. **Connect to Render**
   - Go to [Render Dashboard](https://dashboard.render.com/)
   - Click **"New +"** → **"Blueprint"**
   - Connect your GitHub repository
   - Select **AliStach-V1** repository
   - Render will automatically detect `render.yaml`
   - Click **"Apply"**

3. **Configure Secrets**
   - In Render dashboard, go to your service
   - Navigate to **"Environment"** tab
   - Add these secret values:
     - `ALIEXPRESS_APP_KEY` = your_app_key
     - `ALIEXPRESS_APP_SECRET` = your_app_secret
     - `ADMIN_API_KEY` = generate_strong_key
     - `JWT_SECRET_KEY` = generate_strong_key

4. **Deploy**
   - Render will automatically build and deploy
   - Wait 3-5 minutes for first deployment
   - Your service will be live at: `https://alistach-api.onrender.com`

### Option 2: Manual Deployment

Follow the [Step-by-Step Deployment](#step-by-step-deployment) section below.

---

## 📝 Step-by-Step Deployment

### Step 1: Create New Web Service

1. **Login to Render**
   - Go to [https://dashboard.render.com/](https://dashboard.render.com/)
   - Sign in with GitHub

2. **Create New Service**
   - Click **"New +"** button (top right)
   - Select **"Web Service"**

3. **Connect Repository**
   - Click **"Connect a repository"**
   - Authorize Render to access your GitHub
   - Select **"AliStach-V1"** repository
   - Click **"Connect"**

### Step 2: Configure Service Settings

#### Basic Settings
| Setting | Value |
|---------|-------|
| **Name** | `alistach-api` (or your preferred name) |
| **Region** | **Frankfurt** (closest to Israel) |
| **Branch** | `main` |
| **Runtime** | **Python 3** |
| **Build Command** | `pip install -r requirements.txt && pip install gunicorn` |
| **Start Command** | `gunicorn -k uvicorn.workers.UvicornWorker -w 2 --bind 0.0.0.0:$PORT api.index:app` |

#### Advanced Settings
| Setting | Value |
|---------|-------|
| **Plan** | Free (or Starter for production) |
| **Auto-Deploy** | ✅ Yes |
| **Health Check Path** | `/health` |
| **Python Version** | 3.11.0 |

### Step 3: Configure Environment Variables

Click **"Advanced"** → **"Add Environment Variable"**

#### Required Secrets (Add Manually)
```bash
ALIEXPRESS_APP_KEY=your_actual_app_key_here
ALIEXPRESS_APP_SECRET=your_actual_app_secret_here
ADMIN_API_KEY=generate_strong_random_key_here
JWT_SECRET_KEY=generate_strong_random_key_here
```

**Generate Strong Keys**:
```bash
# Run this in your terminal to generate secure keys
python -c "import secrets; print('ADMIN_API_KEY=' + secrets.token_urlsafe(32))"
python -c "import secrets; print('JWT_SECRET_KEY=' + secrets.token_urlsafe(32))"
```

#### Standard Configuration (Copy-Paste)
```bash
# AliExpress Configuration
ALIEXPRESS_TRACKING_ID=gpt_chat
ALIEXPRESS_LANGUAGE=EN
ALIEXPRESS_CURRENCY=USD

# Server Configuration
API_HOST=0.0.0.0
API_PORT=8000
LOG_LEVEL=INFO

# Cache Configuration
ENABLE_REDIS_CACHE=false
ENABLE_DB_CACHE=true
CACHE_PRODUCT_TTL=86400
CACHE_AFFILIATE_TTL=2592000
CACHE_SEARCH_TTL=3600
CACHE_PRICE_TTL=1800
CACHE_DATABASE_URL=sqlite:///cache.db

# Image Processing
ENABLE_IMAGE_SEARCH=true
IMAGE_PROCESSING_METHOD=clip
MAX_IMAGE_SIZE_MB=10
IMAGE_CACHE_TTL=86400

# Security
INTERNAL_API_KEY=ALIINSIDER-2025
MAX_REQUESTS_PER_MINUTE=60
MAX_REQUESTS_PER_SECOND=5

# CORS & Deployment
ALLOWED_ORIGINS=https://chat.openai.com,https://chatgpt.com,https://platform.openai.com
ENVIRONMENT=production
DEBUG=false
ENABLE_HTTPS_REDIRECT=true
RENDER=true
```

### Step 4: Deploy

1. Click **"Create Web Service"**
2. Render will start building your application
3. Monitor the build logs in real-time
4. Wait 3-5 minutes for first deployment

### Step 5: Get Your Production URL

Once deployed, your service will be available at:
```
https://alistach-api.onrender.com
```

Or your custom name:
```
https://your-service-name.onrender.com
```

---

## 🔐 Environment Variables Configuration

### Critical Variables (Must Configure)

| Variable | Description | Example | Required |
|----------|-------------|---------|----------|
| `ALIEXPRESS_APP_KEY` | Your AliExpress App Key | `520934` | ✅ Yes |
| `ALIEXPRESS_APP_SECRET` | Your AliExpress App Secret | `inC2NFrIr1SvtTGlUWxyQec6EvHyjIno` | ✅ Yes |
| `ADMIN_API_KEY` | Admin endpoint access key | `generate_random_32_chars` | ✅ Yes |
| `JWT_SECRET_KEY` | JWT token signing key | `generate_random_32_chars` | ✅ Yes |

### Optional Variables (Recommended)

| Variable | Description | Default | Notes |
|----------|-------------|---------|-------|
| `ALIEXPRESS_TRACKING_ID` | Affiliate tracking ID | `gpt_chat` | For commission tracking |
| `ALIEXPRESS_LANGUAGE` | API response language | `EN` | EN, ES, FR, etc. |
| `ALIEXPRESS_CURRENCY` | Price currency | `USD` | USD, EUR, GBP, etc. |
| `LOG_LEVEL` | Logging verbosity | `INFO` | DEBUG, INFO, WARNING, ERROR |
| `MAX_REQUESTS_PER_MINUTE` | Rate limit per IP | `60` | Prevent abuse |
| `ALLOWED_ORIGINS` | CORS allowed domains | See above | Comma-separated |

### Cache Configuration

| Variable | Description | Default | Notes |
|----------|-------------|---------|-------|
| `ENABLE_DB_CACHE` | Enable SQLite caching | `true` | Recommended for Render |
| `ENABLE_REDIS_CACHE` | Enable Redis caching | `false` | Requires Redis add-on |
| `CACHE_PRODUCT_TTL` | Product cache duration | `86400` | 24 hours in seconds |
| `CACHE_SEARCH_TTL` | Search cache duration | `3600` | 1 hour in seconds |

---

## ✅ Verification & Testing

### Step 1: Check Deployment Status

1. **In Render Dashboard**
   - Go to your service
   - Check **"Events"** tab for deployment status
   - Look for: ✅ **"Deploy live"**

2. **Check Logs**
   - Click **"Logs"** tab
   - Look for successful startup messages:
   ```
   [INIT] Starting Vercel function initialization
   [INIT] ✓ Successfully imported main app
   Application startup complete.
   Uvicorn running on http://0.0.0.0:8000
   ```

### Step 2: Test Health Endpoint

```bash
# Test health check
curl https://alistach-api.onrender.com/health
```

**Expected Response** (200 OK):
```json
{
  "status": "healthy",
  "timestamp": "2025-01-15T12:00:00Z",
  "version": "1.0.0",
  "environment": "production",
  "platform": "render"
}
```

### Step 3: Test OpenAPI Specification

```bash
# Get OpenAPI spec
curl https://alistach-api.onrender.com/openapi-gpt.json
```

**Expected**: Valid JSON with API documentation

### Step 4: Test API Endpoints

```bash
# Test product search
curl -X POST https://alistach-api.onrender.com/api/products/search \
  -H "Content-Type: application/json" \
  -d '{
    "keywords": "smartphone",
    "page_size": 5
  }'
```

**Expected**: JSON response with product data

### Step 5: Test Interactive Documentation

Open in browser:
```
https://alistach-api.onrender.com/docs
```

**Expected**: Swagger UI with interactive API documentation

---

## 🔧 Troubleshooting

### Issue 1: Build Fails

**Symptom**: Build fails with dependency errors

**Solution**:
```bash
# Check requirements.txt is complete
# Ensure gunicorn is installed
pip install -r requirements.txt
pip install gunicorn
```

**Fix in render.yaml**:
```yaml
buildCommand: pip install -r requirements.txt && pip install gunicorn
```

### Issue 2: Application Won't Start

**Symptom**: Service shows "Deploy failed" or crashes on startup

**Possible Causes**:
1. **Wrong start command**
   - Check: `gunicorn -k uvicorn.workers.UvicornWorker -w 2 --bind 0.0.0.0:$PORT api.index:app`
   - Note: `$PORT` is automatically set by Render

2. **Missing environment variables**
   - Verify all required variables are set
   - Check for typos in variable names

3. **Import errors**
   - Check logs for Python import errors
   - Verify all dependencies are in requirements.txt

**Debug Steps**:
```bash
# Check logs in Render dashboard
# Look for error messages like:
# - ModuleNotFoundError
# - ImportError
# - Configuration errors
```

### Issue 3: Health Check Fails

**Symptom**: Service shows "Unhealthy" status

**Solution**:
1. Verify `/health` endpoint is accessible
2. Check health check path in service settings
3. Ensure application is listening on `0.0.0.0:$PORT`

**Test Locally**:
```bash
# Run locally to test
export PORT=8000
gunicorn -k uvicorn.workers.UvicornWorker -w 2 --bind 0.0.0.0:$PORT api.index:app

# Test health endpoint
curl http://localhost:8000/health
```

### Issue 4: 503 Service Unavailable

**Symptom**: All requests return 503 errors

**Possible Causes**:
1. **Application initialization failed**
   - Check logs for startup errors
   - Verify environment variables

2. **Port binding issue**
   - Ensure using `$PORT` environment variable
   - Don't hardcode port 8000

3. **Worker timeout**
   - Increase worker timeout in start command:
   ```bash
   gunicorn -k uvicorn.workers.UvicornWorker -w 2 --timeout 120 --bind 0.0.0.0:$PORT api.index:app
   ```

### Issue 5: Slow Cold Starts

**Symptom**: First request after inactivity takes 30+ seconds

**Explanation**: Render free tier spins down after 15 minutes of inactivity

**Solutions**:
1. **Upgrade to Starter plan** ($7/month) - no spin down
2. **Use a ping service** to keep service warm
3. **Accept cold starts** as trade-off for free tier

**Ping Service Setup**:
```bash
# Use a service like UptimeRobot or cron-job.org
# Ping your health endpoint every 10 minutes
curl https://alistach-api.onrender.com/health
```

### Issue 6: Environment Variables Not Loading

**Symptom**: Application can't find configuration

**Solution**:
1. **Check variable names** - must match exactly
2. **Restart service** after adding variables
3. **Verify in logs**:
   ```
   [INIT] Environment variables loaded
   ALIEXPRESS_APP_KEY: SET
   ALIEXPRESS_APP_SECRET: SET
   ```

---

## 📊 Monitoring & Logs

### Accessing Logs

1. **Real-Time Logs**
   - Go to Render Dashboard
   - Select your service
   - Click **"Logs"** tab
   - View live log stream

2. **Log Levels**
   ```
   INFO  - Normal operations
   WARNING - Potential issues
   ERROR - Errors that need attention
   DEBUG - Detailed debugging info
   ```

3. **Key Log Messages**
   ```
   ✅ [INIT] ✓ Successfully imported main app
   ✅ Application startup complete
   ✅ Uvicorn running on http://0.0.0.0:8000
   ❌ [INIT] ✗ Failed to import main app
   ❌ ModuleNotFoundError
   ```

### Monitoring Metrics

**In Render Dashboard**:
- **CPU Usage** - Monitor for spikes
- **Memory Usage** - Watch for memory leaks
- **Response Time** - Track performance
- **Error Rate** - Monitor failures

**Health Check Monitoring**:
- Render automatically monitors `/health`
- Service marked unhealthy if check fails
- Automatic restart on repeated failures

### Setting Up Alerts

1. **Email Notifications**
   - Go to service settings
   - Enable **"Deploy notifications"**
   - Enable **"Health check notifications"**

2. **Webhook Integration**
   - Configure webhook URL
   - Receive alerts in Slack/Discord
   - Custom notification handling

---

## 🆚 Comparison: Render vs Vercel

### Render.com

**Pros**:
- ✅ Long-running processes supported
- ✅ Persistent disk storage
- ✅ WebSocket support
- ✅ Background workers
- ✅ More predictable pricing
- ✅ Better for traditional web apps
- ✅ No function timeout limits

**Cons**:
- ❌ Cold starts on free tier (15 min inactivity)
- ❌ Slower deployment (3-5 minutes)
- ❌ Less global edge locations
- ❌ Manual scaling configuration

**Best For**:
- Traditional web applications
- Long-running API services
- WebSocket applications
- Background job processing

### Vercel

**Pros**:
- ✅ Instant global deployment
- ✅ Edge network (fast worldwide)
- ✅ Zero cold starts (paid plans)
- ✅ Automatic scaling
- ✅ Great for Next.js/React
- ✅ Fast deployments (1-2 minutes)

**Cons**:
- ❌ 10-second function timeout (Hobby)
- ❌ 50-second timeout (Pro)
- ❌ No persistent storage
- ❌ Limited Python support
- ❌ Serverless constraints

**Best For**:
- Serverless functions
- Static sites with API routes
- Next.js applications
- Global CDN requirements

### Recommendation

**Use Both in Parallel**:
1. **Vercel** - Primary production (fast, global)
2. **Render** - Backup/testing (reliable, traditional)

**Migration Strategy**:
- Start with both deployed
- Monitor performance and reliability
- Choose primary based on your needs
- Keep secondary as failover

---

## 🚀 Production Checklist

### Before Going Live

- [ ] All environment variables configured
- [ ] Strong random keys generated for secrets
- [ ] Health check endpoint returns 200 OK
- [ ] OpenAPI spec accessible
- [ ] API endpoints tested and working
- [ ] CORS configured for your domains
- [ ] Rate limiting enabled
- [ ] Logging configured properly
- [ ] Error handling tested
- [ ] Documentation updated with Render URL

### Security Checklist

- [ ] `DEBUG=false` in production
- [ ] Strong `ADMIN_API_KEY` set
- [ ] Strong `JWT_SECRET_KEY` set
- [ ] `ALLOWED_ORIGINS` restricted to your domains
- [ ] Rate limiting enabled
- [ ] HTTPS redirect enabled
- [ ] No sensitive data in logs
- [ ] Environment variables not in code

### Performance Checklist

- [ ] Caching enabled (`ENABLE_DB_CACHE=true`)
- [ ] Appropriate cache TTL values set
- [ ] Worker count optimized (2-4 workers)
- [ ] Health check path configured
- [ ] Monitoring and alerts set up

---

## 📚 Additional Resources

### Render Documentation
- [Render Python Guide](https://render.com/docs/deploy-fastapi)
- [Environment Variables](https://render.com/docs/environment-variables)
- [Health Checks](https://render.com/docs/health-checks)
- [Logs & Monitoring](https://render.com/docs/logs)

### FastAPI + Gunicorn
- [FastAPI Deployment](https://fastapi.tiangolo.com/deployment/server-workers/)
- [Gunicorn Configuration](https://docs.gunicorn.org/en/stable/settings.html)
- [Uvicorn Workers](https://www.uvicorn.org/deployment/#gunicorn)

### Project Documentation
- [Main README](README.md)
- [API Documentation](https://alistach-api.onrender.com/docs)
- [OpenAPI Spec](https://alistach-api.onrender.com/openapi-gpt.json)

---

## 🆘 Support

### Getting Help

1. **Check Logs First**
   - Most issues are visible in logs
   - Look for error messages and stack traces

2. **Render Community**
   - [Render Community Forum](https://community.render.com/)
   - Search for similar issues
   - Ask questions with logs

3. **Project Issues**
   - [GitHub Issues](https://github.com/AliStach/AliStach-V1/issues)
   - Report bugs or request features

4. **Render Support**
   - Free tier: Community support
   - Paid plans: Email support
   - Enterprise: Priority support

---

## 📝 Deployment Summary

### What We Deployed

- **Application**: AliStach-V1 AliExpress API Proxy
- **Framework**: FastAPI + Uvicorn + Gunicorn
- **Runtime**: Python 3.11
- **Platform**: Render.com
- **Region**: Frankfurt (closest to Israel)
- **Plan**: Free tier (upgradeable)

### URLs

- **Production**: `https://alistach-api.onrender.com`
- **Health Check**: `https://alistach-api.onrender.com/health`
- **API Docs**: `https://alistach-api.onrender.com/docs`
- **OpenAPI Spec**: `https://alistach-api.onrender.com/openapi-gpt.json`

### Next Steps

1. ✅ Verify deployment is working
2. ✅ Test all endpoints
3. ✅ Update README with Render URL
4. ✅ Configure custom domain (optional)
5. ✅ Set up monitoring and alerts
6. ✅ Test GPT Actions integration

---

**Deployment Status**: ✅ Ready for production  
**Last Updated**: January 2025  
**Maintained By**: AliStach Team
