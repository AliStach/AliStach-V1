# Deployment Instructions - CORS Fix

## Summary of Changes

Fixed the "Unauthorized origin" error by updating origin validation logic to allow:
1. Same-origin requests (requests from the Vercel domain itself)
2. Configured allowed origins (OpenAI, localhost, etc.)
3. Direct API access (no origin header)

## Files Modified

1. **src/middleware/security.py**
   - Updated `validate_origin()` to allow same-origin requests
   - Added Vercel domain to default allowed origins
   - Improved origin/referer validation logic

2. **src/utils/config.py**
   - Updated default `ALLOWED_ORIGINS` to include all necessary domains

## Important Notes

### Health Endpoint Behavior
The `/health` endpoint **intentionally bypasses all security checks** including origin validation. This is by design for monitoring services. The CORS fix applies to all other endpoints.

### Protected Endpoints
The following endpoints ARE protected by origin validation:
- `/` (root)
- `/api/*` (all API endpoints)
- `/admin/*` (admin endpoints)
- `/docs` (documentation)
- `/security/info`

### Exempt Endpoints
The following endpoints bypass origin validation:
- `/health` (for monitoring)
- `/docs` (for documentation access)
- `/redoc` (for documentation access)
- `/openapi.json` (for schema access)

## Deployment Steps

### 1. Commit Changes
```bash
git add src/middleware/security.py src/utils/config.py
git commit -m "fix: Allow Vercel domain and improve origin validation"
git push
```

### 2. Vercel Auto-Deploy
Vercel will automatically deploy when you push to the main branch.

Or manually deploy:
```bash
vercel --prod
```

### 3. Verify Deployment

#### Test Root Endpoint (Protected)
```bash
# Should work - same origin
curl https://aliexpress-api-proxy.vercel.app/

# Should work - allowed origin
curl -H "Origin: https://chat.openai.com" https://aliexpress-api-proxy.vercel.app/

# Should be blocked - unauthorized origin
curl -H "Origin: https://evil-domain.com" https://aliexpress-api-proxy.vercel.app/
```

#### Test Health Endpoint (Unprotected)
```bash
# Always works - bypasses security
curl https://aliexpress-api-proxy.vercel.app/health
```

#### Test API Endpoint (Protected + Requires API Key)
```bash
# Requires both valid origin AND API key
curl -H "Origin: https://chat.openai.com" \
     -H "x-internal-key: YOUR_KEY" \
     https://aliexpress-api-proxy.vercel.app/api/categories
```

## Environment Variables

Ensure these are set in Vercel Dashboard:

### Required
- `ALIEXPRESS_APP_KEY` - Your AliExpress API key
- `ALIEXPRESS_APP_SECRET` - Your AliExpress API secret
- `INTERNAL_API_KEY` - Internal API key for authentication
- `ADMIN_API_KEY` - Admin API key for admin endpoints
- `JWT_SECRET_KEY` - Secret key for JWT tokens

### Optional (with defaults)
- `ALLOWED_ORIGINS` - Comma-separated list of allowed origins
  - Default includes: OpenAI domains, localhost, Vercel domain
- `ENVIRONMENT` - Set to `production`
- `MAX_REQUESTS_PER_MINUTE` - Rate limit (default: 60)
- `MAX_REQUESTS_PER_SECOND` - Rate limit (default: 5)

## Custom Allowed Origins

To add custom domains, set the `ALLOWED_ORIGINS` environment variable in Vercel:

```
ALLOWED_ORIGINS=https://chat.openai.com,https://chatgpt.com,https://your-custom-domain.com,http://localhost:3000
```

**Note:** The Vercel domain itself will always be allowed due to the self-origin check, even if not in this list.

## Testing After Deployment

### 1. Test from Browser
Open `https://aliexpress-api-proxy.vercel.app/docs` in your browser.
- Should load without CORS errors
- Should show FastAPI documentation

### 2. Test from GPT Actions
Configure a GPT Action with the API URL:
```
https://aliexpress-api-proxy.vercel.app
```
- Should work without "Unauthorized origin" errors

### 3. Test from Localhost
```bash
curl -H "Origin: http://localhost:3000" https://aliexpress-api-proxy.vercel.app/
```
- Should return JSON response (not 403 error)

## Troubleshooting

### Still Getting "Unauthorized origin" Error

1. **Check which endpoint you're calling:**
   - `/health` always works (bypasses security)
   - Other endpoints require valid origin

2. **Check the origin header:**
   ```bash
   # Add -v to see request headers
   curl -v -H "Origin: YOUR_ORIGIN" https://aliexpress-api-proxy.vercel.app/
   ```

3. **Check Vercel logs:**
   - Go to Vercel Dashboard → Your Project → Functions
   - Look for origin validation warnings

4. **Verify environment variables:**
   - Check `ALLOWED_ORIGINS` in Vercel Dashboard
   - Ensure it's a comma-separated list (no spaces)

### Getting 503 "Service not initialized" Error

This means the AliExpress API credentials are missing:
1. Go to Vercel Dashboard → Your Project → Settings → Environment Variables
2. Add `ALIEXPRESS_APP_KEY` and `ALIEXPRESS_APP_SECRET`
3. Redeploy

### Getting "Missing or invalid internal API key" Error

For `/api/*` endpoints, you need to include the API key:
```bash
curl -H "x-internal-key: YOUR_KEY" https://aliexpress-api-proxy.vercel.app/api/categories
```

## Success Criteria

After deployment, you should see:
- ✅ Root endpoint (`/`) returns JSON (not 403 error)
- ✅ `/docs` loads in browser without CORS errors
- ✅ GPT Actions can call the API
- ✅ Localhost requests work
- ✅ Unauthorized domains are blocked (except `/health`)
- ✅ All security features remain active

## Rollback Plan

If something goes wrong:
```bash
git revert HEAD
git push
```

Vercel will automatically deploy the previous version.
