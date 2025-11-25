# Deployment Fix Guide - Real AliExpress API

## Summary of Changes

We've fixed the proxy to use **real AliExpress data** instead of mock data. The key changes:

### 1. Removed Automatic Mock Fallback

**File:** `src/api/main.py`

**Changed:**
```python
from ..services.aliexpress_service_with_mock import AliExpressServiceWithMock as AliExpressService
```

**To:**
```python
from ..services.aliexpress_service import AliExpressService
```

This ensures the service uses real AliExpress API and doesn't automatically fall back to mock data when errors occur.

### 2. Updated Environment Variables

**File:** `.env`

Removed quotes from credentials:
```env
ALIEXPRESS_APP_KEY=520934
ALIEXPRESS_APP_SECRET=inC2NFrIr1SvtTGlUWxyQec6EvHyjIno
ALIEXPRESS_TRACKING_ID=gpt_chat
ALIEXPRESS_LANGUAGE=EN
ALIEXPRESS_CURRENCY=USD
FORCE_MOCK_MODE=false
```

## Verification - Local Testing

We've verified the service works locally with real AliExpress data:

```bash
$ python test_local_service.py
✓ SUCCESS! Got 40 categories from real AliExpress API
✓ SUCCESS! Found 1,659,078 products in search
✓ All endpoints returning REAL data
```

Sample real data received:
- **40 real categories** (not the 15 mock categories)
- **Real product data** with actual prices, images, and affiliate links
- **Real category names** like "Food", "Apparel & Accessories", etc.

## Deployment to Vercel

### Step 1: Set Environment Variables on Vercel

You need to set these environment variables in your Vercel project dashboard:

1. Go to: https://vercel.com/chana-jacobs-projects/aliexpress-api-proxy/settings/environment-variables

2. Add the following variables for **Production**, **Preview**, and **Development**:

```
ALIEXPRESS_APP_KEY=520934
ALIEXPRESS_APP_SECRET=inC2NFrIr1SvtTGlUWxyQec6EvHyjIno
ALIEXPRESS_TRACKING_ID=gpt_chat
ALIEXPRESS_LANGUAGE=EN
ALIEXPRESS_CURRENCY=USD
FORCE_MOCK_MODE=false
INTERNAL_API_KEY=ALIINSIDER-2025
```

### Step 2: Deploy to Vercel

Option A - Using Vercel CLI:
```bash
vercel --prod
```

Option B - Using Git:
```bash
git add .
git commit -m "Fix: Use real AliExpress API instead of mock data"
git push origin main
```

Vercel will automatically deploy when you push to your repository.

### Step 3: Verify Deployment

After deployment, test the endpoints:

```bash
curl -H "x-internal-key: ALIINSIDER-2025" \
  https://aliexpress-api-proxy.vercel.app/health
```

Check the response for:
```json
{
  "data": {
    "service_info": {
      "mock_mode": false,  // Should be false!
      "mock_mode_reason": "Using real AliExpress API"
    }
  }
}
```

Test categories:
```bash
curl -H "x-internal-key: ALIINSIDER-2025" \
  https://aliexpress-api-proxy.vercel.app/api/categories
```

You should see **40 real categories**, not 15 mock ones.

## Expected Results After Deployment

### Before (Mock Data):
- ✗ 15 generic categories (numbered 1-15)
- ✗ Mock affiliate links with `_mock_` in URL
- ✗ `mock_mode: true` in health check
- ✗ Empty child categories
- ✗ Product search returns 404

### After (Real Data):
- ✓ 40 real AliExpress categories
- ✓ Real affiliate links from AliExpress
- ✓ `mock_mode: false` in health check
- ✓ Real child categories
- ✓ Product search returns real products

## Troubleshooting

### If mock_mode is still true after deployment:

1. **Check environment variables are set on Vercel**
   - Go to Vercel dashboard → Settings → Environment Variables
   - Verify all variables are present
   - Make sure they're enabled for Production

2. **Check Vercel function logs**
   - Go to Vercel dashboard → Deployments → [Latest] → Functions
   - Look for initialization errors

3. **Redeploy**
   - Sometimes Vercel needs a fresh deployment to pick up env changes
   - Run: `vercel --prod --force`

### If you get signature errors:

The credentials are valid (we've tested them locally). If you see signature errors:
- Check that APP_SECRET doesn't have extra spaces or quotes
- Verify the environment variables are exactly as shown above
- Check Vercel logs for any initialization errors

## Testing Endpoints

Once deployed, test all endpoints:

### 1. Health Check
```bash
curl -H "x-internal-key: ALIINSIDER-2025" \
  https://aliexpress-api-proxy.vercel.app/health
```

### 2. Categories
```bash
curl -H "x-internal-key: ALIINSIDER-2025" \
  https://aliexpress-api-proxy.vercel.app/api/categories
```

### 3. Product Search
```bash
curl -H "x-internal-key: ALIINSIDER-2025" \
  "https://aliexpress-api-proxy.vercel.app/api/products/search?keywords=phone&page_size=3"
```

### 4. Affiliate Links
```bash
curl -X POST \
  -H "x-internal-key: ALIINSIDER-2025" \
  -H "Content-Type: application/json" \
  -d '{"urls":["https://www.aliexpress.com/item/1005004567890123.html"]}' \
  https://aliexpress-api-proxy.vercel.app/api/affiliate/links
```

## Files Changed

1. `src/api/main.py` - Removed mock service wrapper
2. `.env` - Updated credentials format
3. All service files remain unchanged (they already support real API)

## Next Steps

1. Set environment variables on Vercel dashboard
2. Deploy to Vercel
3. Test endpoints to verify real data
4. Monitor Vercel function logs for any issues

The proxy is now configured to use real AliExpress data!
