# CORS Fix - Code Changes Summary

## Problem
FastAPI app returns: `{"success": false, "error": "Unauthorized origin. This API is restricted to authorized domains."}`

## Root Cause
The security middleware's origin validation was blocking requests from the Vercel domain itself because:
1. The allowed origins list didn't include the Vercel domain
2. No self-origin check existed (requests from same domain were validated against allowed list)
3. Limited default origins (only OpenAI domains)

## Solution
Updated origin validation to:
1. Always allow same-origin requests (requests from the app's own domain)
2. Include Vercel domain in default allowed origins
3. Maintain security by still validating against allowed origins list

---

## Code Changes

### 1. Updated `validate_origin()` Method
**File:** `src/middleware/security.py`

**Before:**
```python
def validate_origin(self, request: Request) -> bool:
    """Validate request origin against allowed origins."""
    origin = request.headers.get("origin")
    referer = request.headers.get("referer")
    
    # Allow requests without origin/referer for direct API access
    if not origin and not referer:
        return True
    
    # Check origin
    if origin:
        for allowed in self.allowed_origins:
            if origin == allowed or origin.startswith(allowed):
                return True
    
    # Check referer as fallback
    if referer:
        for allowed in self.allowed_origins:
            if referer.startswith(allowed):
                return True
    
    return False
```

**After:**
```python
def validate_origin(self, request: Request) -> bool:
    """Validate request origin against allowed origins."""
    origin = request.headers.get("origin")
    referer = request.headers.get("referer")
    host = request.headers.get("host", "")
    
    # Allow requests without origin/referer for direct API access (curl, Postman, etc.)
    if not origin and not referer:
        return True
    
    # Always allow requests from the same host (self-origin)
    if origin:
        # Extract domain from origin (e.g., "https://example.com" -> "example.com")
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
        # Extract domain from referer
        referer_domain = referer.replace("https://", "").replace("http://", "").split("/")[0]
        if referer_domain == host:
            return True
        
        for allowed in self.allowed_origins:
            if referer.startswith(allowed):
                return True
    
    return False
```

**Key Changes:**
- ✅ Added `host` header extraction
- ✅ Compare origin domain with host domain (allows same-origin)
- ✅ Compare referer domain with host domain (fallback)
- ✅ Maintains security by checking allowed origins list

---

### 2. Updated Default Allowed Origins
**File:** `src/middleware/security.py`

**Before:**
```python
self.allowed_origins = [
    "https://chat.openai.com",
    "https://chatgpt.com", 
    "https://platform.openai.com",
    "http://localhost:3000",  # Development
    "http://localhost:8000",  # Development
    "https://your-domain.com"  # Replace with your actual domain
]
```

**After:**
```python
self.allowed_origins = [
    "https://chat.openai.com",
    "https://chatgpt.com", 
    "https://platform.openai.com",
    "http://localhost:3000",  # Development
    "http://localhost:8000",  # Development
    "http://127.0.0.1:3000",  # Development
    "http://127.0.0.1:8000",  # Development
    "https://aliexpress-api-proxy.vercel.app",  # Production Vercel domain
]
```

**Key Changes:**
- ✅ Added `127.0.0.1` variants for localhost
- ✅ Added Vercel production domain
- ✅ Removed placeholder domain

---

### 3. Updated Config Defaults
**File:** `src/utils/config.py`

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

**Key Changes:**
- ✅ Expanded default origins to include all necessary domains
- ✅ Added Vercel domain to defaults
- ✅ Added localhost variants

---

## Security Maintained

All security features remain intact:

✅ **Origin Validation**: Unknown origins still blocked
✅ **Rate Limiting**: 60 req/min, 5 req/sec per IP
✅ **API Key Authentication**: Required for `/api/*` endpoints
✅ **IP Blocking**: Automatic and manual IP blocking
✅ **Audit Logging**: All requests logged to SQLite
✅ **CSRF Protection**: Token validation for web requests

---

## Allowed Origins After Fix

### Automatically Allowed
- **Self-origin**: Any request from the same domain as the `host` header
- **Direct access**: Requests without origin/referer (curl, Postman)

### Configured Allowed Origins
1. **OpenAI** (for GPT Actions):
   - `https://chat.openai.com`
   - `https://chatgpt.com`
   - `https://platform.openai.com`

2. **Development**:
   - `http://localhost:3000`
   - `http://localhost:8000`
   - `http://127.0.0.1:3000`
   - `http://127.0.0.1:8000`

3. **Production**:
   - `https://aliexpress-api-proxy.vercel.app`

---

## Verification After Deployment

### Test 1: Same-Origin (Should Work)
```bash
curl https://aliexpress-api-proxy.vercel.app/
```
Expected: JSON response (not 403)

### Test 2: OpenAI Origin (Should Work)
```bash
curl -H "Origin: https://chat.openai.com" https://aliexpress-api-proxy.vercel.app/
```
Expected: JSON response (not 403)

### Test 3: Unauthorized Origin (Should Block)
```bash
curl -H "Origin: https://evil-domain.com" https://aliexpress-api-proxy.vercel.app/
```
Expected: 403 error with "Unauthorized origin" message

### Test 4: Health Endpoint (Always Works)
```bash
curl https://aliexpress-api-proxy.vercel.app/health
```
Expected: JSON response (health endpoint bypasses security)

---

## Files Changed

- ✅ `src/middleware/security.py` (2 changes)
  - Updated `validate_origin()` method
  - Updated default allowed origins list

- ✅ `src/utils/config.py` (1 change)
  - Updated default `ALLOWED_ORIGINS` configuration

---

## Deployment Command

```bash
git add src/middleware/security.py src/utils/config.py
git commit -m "fix: Allow Vercel domain and improve origin validation"
git push
```

Vercel will auto-deploy, or manually:
```bash
vercel --prod
```

---

## Expected Results

After deployment:
- ✅ Root endpoint returns JSON (not 403)
- ✅ `/docs` loads without CORS errors
- ✅ GPT Actions work
- ✅ Localhost development works
- ✅ Unauthorized domains blocked
- ✅ All security features active
