# 🚀 Render.com Deployment Instructions

**Status**: ✅ All configuration files are ready  
**Expected URL**: `https://alistach-api.onrender.com`  
**Deployment Method**: Blueprint (render.yaml)  
**Runtime**: Python 3.11 (Native, no Docker)

---

## ✅ Pre-Deployment Verification

### Configuration Status
- ✅ `render.yaml` - Ready and configured
- ✅ `requirements.txt` - All dependencies listed
- ✅ `api/index.py` - Entry point ready
- ✅ Environment variables - Pre-configured in render.yaml
- ✅ Health check - Configured at `/health`
- ✅ Auto-deploy - Enabled from main branch

### Vercel Configuration (Untouched)
- ✅ `vercel.json` - Unchanged
- ✅ `runtime.txt` - Unchanged
- ✅ Vercel deployment - Still active

---

## 🎯 Deployment Steps (15 minutes)

### Step 1: Access Render Dashboard (1 minute)

1. Open your browser and go to:
   ```
   https://dashboard.render.com/
   ```

2. Sign in with your GitHub account

### Step 2: Create New Web Service via Blueprint (3 minutes)

1. Click the **"New +"** button (top right corner)

2. Select **"Blueprint"** from the dropdown menu

3. **Connect Repository**:
   - If not already connected, click "Connect account"
   - Authorize Render to access your GitHub
   - Search for and select **"AliStach-V1"** repository
   - Click **"Connect"**

4. **Blueprint Detection**:
   - Render will automatically detect `render.yaml`
   - You'll see: "Found render.yaml in repository"
   - Service name will be pre-filled as: **alistach-api**
   - Region will be: **Frankfurt**

5. Click **"Apply"** button

### Step 3: Configure Secret Environment Variables (5 minutes)

After clicking "Apply", Render will create the service but you need to add the secret values:

1. **Navigate to Environment Tab**:
   - Go to your service dashboard
   - Click on **"Environment"** tab in the left sidebar

2. **Add Secret Variables**:
   
   Find these variables (marked with `sync: false` in render.yaml) and add their values:

   ```bash
   ALIEXPRESS_APP_KEY
   ```
   - Click "Edit" or the pencil icon
   - Enter your actual AliExpress App Key
   - Example: `520934`
   - Click "Save"

   ```bash
   ALIEXPRESS_APP_SECRET
   ```
   - Click "Edit"
   - Enter your actual AliExpress App Secret
   - Example: `inC2NFrIr1SvtTGlUWxyQec6EvHyjIno`
   - Click "Save"

   ```bash
   ADMIN_API_KEY
   ```
   - Click "Edit"
   - Generate a strong random key (see below)
   - Click "Save"

   ```bash
   JWT_SECRET_KEY
   ```
   - Click "Edit"
   - Generate a strong random key (see below)
   - Click "Save"

3. **Generate Strong Keys** (run in your terminal):
   ```bash
   # Generate ADMIN_API_KEY
   python -c "import secrets; print(secrets.token_urlsafe(32))"
   
   # Generate JWT_SECRET_KEY
   python -c "import secrets; print(secrets.token_urlsafe(32))"
   ```

4. **Save Changes**:
   - After adding all 4 secrets, click "Save Changes" at the bottom
   - Render will automatically trigger a new deployment

### Step 4: Monitor Deployment (5 minutes)

1. **Go to Logs Tab**:
   - Click on **"Logs"** tab in the left sidebar
   - Watch the build process in real-time

2. **Expected Build Log Output**:
   ```
   ==> Cloning from https://github.com/AliStach/AliStach-V1...
   ==> Checking out commit 3559f70 in branch main
   ==> Running build command 'pip install -r requirements.txt && pip install gunicorn'...
   Collecting fastapi>=0.100.0
   Collecting uvicorn>=0.20.0
   ...
   Successfully installed fastapi-0.116.1 uvicorn-0.20.0 ...
   Collecting gunicorn
   Successfully installed gunicorn-21.2.0
   ==> Build successful!
   ==> Starting service with 'gunicorn -k uvicorn.workers.UvicornWorker -w 2 --bind 0.0.0.0:$PORT api.index:app'...
   [INIT] Starting Vercel function initialization
   [INIT] Python version: 3.11.0
   [INIT] ✓ Successfully imported main app
   Application startup complete.
   [INFO] Uvicorn running on http://0.0.0.0:10000
   ```

3. **Wait for "Deploy live" Event**:
   - Go to **"Events"** tab
   - Look for: ✅ **"Deploy live"**
   - This means your service is now running

4. **Get Your Production URL**:
   - At the top of the dashboard, you'll see your service URL
   - It should be: `https://alistach-api.onrender.com`
   - Copy this URL for testing

### Step 5: Verify Deployment (2 minutes)

Run these tests to verify your deployment:

#### Test 1: Health Check
```bash
curl https://alistach-api.onrender.com/health
```

**Expected Response** (200 OK):
```json
{
  "status": "healthy",
  "timestamp": "2025-01-15T...",
  "version": "1.0.0",
  "environment": "production",
  "platform": "render"
}
```

#### Test 2: OpenAPI Specification
```bash
curl https://alistach-api.onrender.com/openapi-gpt.json
```

**Expected**: Valid JSON with API documentation (should start with `{"openapi": "3.1.0"...`)

#### Test 3: Interactive Documentation
Open in your browser:
```
https://alistach-api.onrender.com/docs
```

**Expected**: Swagger UI with interactive API documentation

#### Test 4: Root Endpoint
```bash
curl https://alistach-api.onrender.com/
```

**Expected**: JSON response with API information

---

## 🔧 Troubleshooting

### Issue: Build Fails

**Symptom**: Build logs show errors during `pip install`

**Solution**:
1. Check that `requirements.txt` is complete
2. Verify Python version is 3.11
3. Look for specific dependency errors in logs
4. If needed, add missing dependencies to `requirements.txt`

### Issue: Service Won't Start

**Symptom**: Build succeeds but service crashes on startup

**Possible Causes**:
1. **Missing environment variables**
   - Go to Environment tab
   - Verify all 4 secret variables are set
   - Check for typos in variable names

2. **Import errors**
   - Check logs for Python import errors
   - Look for: `ModuleNotFoundError` or `ImportError`
   - Verify all dependencies are in `requirements.txt`

3. **Port binding issue**
   - Ensure start command uses `$PORT` variable
   - Current command: `gunicorn ... --bind 0.0.0.0:$PORT api.index:app`

**Debug Steps**:
```bash
# Check the logs for specific error messages
# Look for lines starting with:
# [INIT] ✗ Failed to import main app
# [ERROR] ...
```

### Issue: Health Check Fails

**Symptom**: Service shows "Unhealthy" status

**Solution**:
1. Verify `/health` endpoint is accessible
2. Check that app is listening on `0.0.0.0:$PORT`
3. Review startup logs for initialization errors
4. Test locally:
   ```bash
   export PORT=8000
   gunicorn -k uvicorn.workers.UvicornWorker -w 2 --bind 0.0.0.0:$PORT api.index:app
   curl http://localhost:8000/health
   ```

### Issue: 503 Service Unavailable

**Symptom**: All requests return 503 errors

**Possible Causes**:
1. **Application initialization failed**
   - Check logs for startup errors
   - Verify environment variables are loaded
   - Look for configuration errors

2. **Cold start (Free Tier)**
   - First request after 15 min inactivity takes 30-60 seconds
   - This is normal on free tier
   - Upgrade to Starter plan ($7/month) to eliminate cold starts

**Solution**:
- Wait 30-60 seconds and try again
- Check logs for error messages
- Verify all environment variables are set correctly

### Issue: Environment Variables Not Loading

**Symptom**: Application can't find configuration

**Solution**:
1. Go to **Environment** tab
2. Verify all variables are present
3. Check for typos in variable names (case-sensitive)
4. Click "Save Changes" to trigger redeploy
5. Check logs for confirmation:
   ```
   [INIT] Environment variables loaded
   ALIEXPRESS_APP_KEY: SET
   ALIEXPRESS_APP_SECRET: SET
   ```

---

## 📊 Post-Deployment Checklist

### Immediate Verification ✅

- [ ] Service shows "Deploy live" in Events tab
- [ ] Health endpoint returns 200 OK
- [ ] OpenAPI spec is accessible
- [ ] Interactive docs load at `/docs`
- [ ] No errors in logs
- [ ] Response times < 500ms (warm requests)

### Configuration Verification ✅

- [ ] All 4 secret environment variables configured
- [ ] Auto-deploy enabled (check Settings tab)
- [ ] Health check path set to `/health`
- [ ] Region set to Frankfurt
- [ ] Python version 3.11
- [ ] Free tier plan active

### Security Verification ✅

- [ ] `DEBUG=false` in environment
- [ ] Strong `ADMIN_API_KEY` set
- [ ] Strong `JWT_SECRET_KEY` set
- [ ] `ALLOWED_ORIGINS` configured for GPT Actions
- [ ] Rate limiting enabled (60/min, 5/sec)
- [ ] HTTPS redirect enabled

---

## 🎯 Expected Results

### Production URL
```
https://alistach-api.onrender.com
```

### Key Endpoints
- **Health Check**: `https://alistach-api.onrender.com/health`
- **OpenAPI Spec**: `https://alistach-api.onrender.com/openapi-gpt.json`
- **Interactive Docs**: `https://alistach-api.onrender.com/docs`
- **API Status**: `https://alistach-api.onrender.com/api/status`

### Performance Expectations

**Free Tier**:
- Cold start (first request after 15 min): 30-60 seconds
- Warm requests: 100-300ms
- No timeout limits (vs 10s on Vercel)

**Starter Tier ($7/month)**:
- No cold starts (always on)
- Consistent 100-300ms response times
- Better for production use

---

## 🆚 Deployment Comparison

### After Deployment, You'll Have:

| Platform | Status | URL | Purpose |
|----------|--------|-----|---------|
| **Vercel** | ✅ LIVE | `https://alistach.vercel.app` | Primary (fast, global) |
| **Render** | ✅ LIVE | `https://alistach-api.onrender.com` | Backup (reliable, no limits) |

### Benefits of Dual Deployment:
1. ✅ **Reliability**: Failover capability
2. ✅ **Performance**: Choose best platform per use case
3. ✅ **Testing**: Compare platforms in production
4. ✅ **Migration**: Easy to switch if needed
5. ✅ **Cost**: Optimize based on traffic patterns

---

## 📝 Next Steps After Deployment

### 1. Update Documentation
- [ ] Update README.md with actual Render URL
- [ ] Add Render URL to API documentation
- [ ] Update GPT Actions configuration

### 2. Monitor Performance
- [ ] Check response times in Render dashboard
- [ ] Monitor error rates
- [ ] Compare with Vercel performance
- [ ] Analyze traffic patterns

### 3. Consider Upgrades
- [ ] Evaluate free tier cold starts
- [ ] Consider Starter plan ($7/month) for always-on
- [ ] Monitor resource usage (CPU, memory)
- [ ] Plan for scaling if needed

### 4. Set Up Monitoring
- [ ] Enable email notifications for deploys
- [ ] Enable health check notifications
- [ ] Set up uptime monitoring (UptimeRobot, etc.)
- [ ] Configure alerting for errors

---

## 🆘 Getting Help

### If You Encounter Issues:

1. **Check Logs First**
   - Render Dashboard → Your Service → Logs
   - Look for error messages and stack traces

2. **Review Documentation**
   - [DEPLOY_RENDER_GUIDE.md](DEPLOY_RENDER_GUIDE.md) - Complete guide
   - [Render Documentation](https://render.com/docs)

3. **Common Issues**
   - Build fails: Check requirements.txt
   - App won't start: Verify environment variables
   - Health check fails: Check /health endpoint
   - 503 errors: Wait for cold start or check logs

4. **Get Support**
   - [Render Community Forum](https://community.render.com/)
   - [GitHub Issues](https://github.com/AliStach/AliStach-V1/issues)
   - Render Support (paid plans)

---

## ✅ Success Confirmation

Once deployment is complete, you should see:

```bash
# Health check returns 200 OK
$ curl https://alistach-api.onrender.com/health
{"status":"healthy","timestamp":"2025-01-15T...","version":"1.0.0"}

# OpenAPI spec is accessible
$ curl https://alistach-api.onrender.com/openapi-gpt.json
{"openapi":"3.1.0","info":{"title":"AliExpress API"...}

# Interactive docs load
$ open https://alistach-api.onrender.com/docs
# Swagger UI loads successfully
```

**Congratulations! Your FastAPI backend is now deployed on Render.com!** 🎉

---

**Deployment Time**: ~15-20 minutes  
**Status**: Ready to deploy  
**Last Updated**: January 15, 2025
