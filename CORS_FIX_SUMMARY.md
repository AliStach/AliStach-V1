# CORS/Origin Validation Fix Summary

## Problem
The FastAPI app deployed on Vercel returns:
```json
{
  "success": false,
  "error": "Unauthorized origin. This API is restricted to authorized domains."
}
```

## Root Cause
The security middleware's `validate_origin()` method was blocking requests from the Vercel domain itself because:

1. **Missing Vercel domain**: The allowed origins list didn't include `https://aliexpress-api-proxy.vercel.app`
2. **No self-origin check**: Requests from the same domain (e.g., browser accessing the deployed app) were being validated against the allowed list, which didn't include the app's own domain
3. **Limited default origins**: Only OpenAI domains were in the default list

## Fixes Applied

### 1. Updated `validate_origin()` Method (src/middleware/security.py)

**Added self-origin validation:**
```python
def validate_origin(self, request: Request) -> bool:
    """Validate request origin against allowed origins."""
    origin = request.headers.get("origin")
    referer = request.headers.get("referer")
    host = request.headers.get("host", "")
    
    # Allow requests without origin/referer for direct API access
    if not origin and not referer:
        return True
    
    # Always allow requests from the same host (self-origin)
    if origin:
        origin_domain = origin.replace("https://", "").replace("http://", "").split("/")[0]
        if origin_domain == host:
            return True
    
    # Check origin against allowed list
    if origin:
        for allowed in self.allowed_origins:
            if origin == allowed or origin.startswith(allowed):
                return True
    
    # Check referer as fallback
    if referer:
        referer_domain = referer.replace("https://", "").replace("http://", "").split("/")[0]
        if referer_domain == host:
            return True
        
        for allowed in self.allowed_origins:
            if referer.startswith(allowed):
                return True
    
    return False
```

**Key changes:**
- ✅ Extracts `host` header from request
- ✅ Compares origin domain with host domain (allows same-origin requests)
- ✅ Compares referer domain with host domain (fallback for same-origin)
- ✅ Maintains security by still checking against allowed origins list

### 2. Updated Default Allowed Origins (src/middleware/security.py)

**Before:**
```python
self.allowed_origins = [
    "https://chat.openai.com",
    "https://chatgpt.com", 
    "https://platform.openai.com",
    "http://localhost:3000",
    "http://localhost:8000",
    "https://your-domain.com"
]
```

**After:**
```python
self.allowed_origins = [
    "https://chat.openai.com",
    "https://chatgpt.com", 
    "https://platform.openai.com",
    "http://localhost:3000",
    "http://localhost:8000",
    "http://127.0.0.1:3000",
    "http://127.0.0.1:8000",
    "https://aliexpress-api-proxy.vercel.app",  # Production Vercel domain
]
```

### 3. Updated Config Defaults (src/utils/config.py)

**Before:**
```python
allowed_origins = os.getenv('ALLOWED_ORIGINS', 'https://chat.openai.com,https://chatgpt.com')
```

**After:**
```python
allowed_origins = os.getenv(
    'ALLOWED_ORIGINS', 
    'https://chat.openai.com,https://chatgpt.com,https://platform.openai.com,'
    'http://localhost:3000,http://localhost:8000,http://127.0.0.1:3000,http://127.0.0.1:8000,'
    'https://aliexpress-api-proxy.vercel.app'
)
```

## Security Maintained

✅ **Still blocks unauthorized domains**: Unknown origins are still rejected
✅ **Rate limiting intact**: All rate limiting rules still apply
✅ **API key validation**: Internal API key still required for `/api/*` endpoints
✅ **IP blocking**: IP blocking functionality unchanged
✅ **Audit logging**: All requests still logged to SQLite database

## Allowed Origins After Fix

The following origins are now allowed:

1. **OpenAI Domains** (for GPT Actions):
   - `https://chat.openai.com`
   - `https://chatgpt.com`
   - `https://platform.openai.com`

2. **Development** (localhost):
   - `http://localhost:3000`
   - `http://localhost:8000`
   - `http://127.0.0.1:3000`
   - `http://127.0.0.1:8000`

3. **Production** (Vercel):
   - `https://aliexpress-api-proxy.vercel.app`

4. **Self-Origin** (automatic):
   - Any request from the same domain as the `host` header

## Verification Plan

### After Redeployment

1. **Test health endpoint from browser:**
   ```bash
   curl https://aliexpress-api-proxy.vercel.app/health
   ```
   Expected: JSON response with status (not 403 error)

2. **Test from browser (same-origin):**
   - Open `https://aliexpress-api-proxy.vercel.app/docs`
   - Should load FastAPI documentation without CORS errors

3. **Test from localhost:**
   ```bash
   curl -H "Origin: http://localhost:3000" https://aliexpress-api-proxy.vercel.app/health
   ```
   Expected: JSON response (not 403 error)

4. **Test from OpenAI (GPT Actions):**
   - Configure GPT Action with the API URL
   - Should work without "Unauthorized origin" errors

5. **Test unauthorized origin (should still block):**
   ```bash
   curl -H "Origin: https://evil-domain.com" https://aliexpress-api-proxy.vercel.app/health
   ```
   Expected: 403 error with "Unauthorized origin" message

### Verification Script

Run the included verification script:
```bash
python verify_cors_fix.py
```

## Deployment Steps

1. **Commit changes:**
   ```bash
   git add src/middleware/security.py src/utils/config.py
   git commit -m "fix: Allow Vercel domain and localhost in CORS validation"
   git push
   ```

2. **Vercel auto-deploys** (or manually):
   ```bash
   vercel --prod
   ```

3. **Verify:**
   ```bash
   curl https://aliexpress-api-proxy.vercel.app/health
   ```

## Environment Variable Override (Optional)

To customize allowed origins in Vercel, set the `ALLOWED_ORIGINS` environment variable:

```
ALLOWED_ORIGINS=https://chat.openai.com,https://chatgpt.com,https://your-custom-domain.com
```

**Note:** The self-origin check will still allow requests from the Vercel domain itself, regardless of this setting.

## Files Changed

- ✅ `src/middleware/security.py` - Updated `validate_origin()` method and default origins
- ✅ `src/utils/config.py` - Updated default `ALLOWED_ORIGINS` configuration

## Expected Results

After deployment:
- ✅ `/health` endpoint returns JSON (not 403)
- ✅ `/docs` loads in browser without CORS errors
- ✅ GPT Actions can call the API
- ✅ Localhost development works
- ✅ Unknown domains are still blocked
- ✅ All security features remain active
