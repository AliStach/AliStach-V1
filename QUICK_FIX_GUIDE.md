# ⚡ Quick Fix Guide - AliExpress API Credentials

## 🎯 The Problem
Your AliExpress API is approved, but the credentials in the system are incorrect, causing a **signature error**.

## ✅ The Solution (10 minutes)

### Step 1: Get Your Real Credentials
1. Go to: https://portals.aliexpress.com/
2. Log in
3. Find your approved app
4. Copy these 3 values:
   - **App Key** (example: 123456)
   - **App Secret** (example: abc123def456...)
   - **Tracking ID** (example: your_affiliate_id)

### Step 2: Update Local `.env` File
```bash
# Open .env file and replace these lines:
ALIEXPRESS_APP_KEY="your_actual_app_key"
ALIEXPRESS_APP_SECRET="your_actual_app_secret"
ALIEXPRESS_TRACKING_ID=your_tracking_id
FORCE_MOCK_MODE=false
```

### Step 3: Test Locally
```bash
python diagnose_credentials.py
```

**Expected output:**
```
✅ ALL CHECKS PASSED!
   Your AliExpress API credentials appear to be valid and working.
```

### Step 4: Update Vercel
```bash
# Remove old credentials
vercel env rm ALIEXPRESS_APP_KEY production
vercel env rm ALIEXPRESS_APP_SECRET production

# Add new credentials (paste when prompted)
vercel env add ALIEXPRESS_APP_KEY production
vercel env add ALIEXPRESS_APP_SECRET production

# Redeploy
vercel --prod
```

### Step 5: Verify Live API
```bash
python verify_aliexpress_api.py
```

**Expected output:**
```
✅ VERDICT: ALIEXPRESS API IS FULLY OPERATIONAL
```

## 🎉 Done!
Your API should now be working with real AliExpress data.

---

## 🆘 Still Having Issues?

### Check These Common Mistakes:
- ❌ Using test/sandbox credentials instead of production
- ❌ Extra spaces in APP_SECRET
- ❌ APP_KEY and APP_SECRET from different apps
- ❌ Credentials not fully copied (truncated)

### Get Help:
1. Run: `python diagnose_credentials.py`
2. Check the error message
3. Verify credentials at https://portals.aliexpress.com/
4. Contact AliExpress support if needed

---

**Quick Test Command:**
```bash
python diagnose_credentials.py && python verify_aliexpress_api.py
```

This will test both locally and verify everything works!
