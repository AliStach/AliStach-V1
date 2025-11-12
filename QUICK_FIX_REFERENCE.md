# Quick Fix Reference - AliStach Deployment

## 🔥 Problem
`FUNCTION_INVOCATION_FAILED` (500 errors) on all endpoints

## 🎯 Root Cause
Route conflicts in `api/index.py` - duplicate `/health` route

## ⚡ Solution
Remove duplicate routes from `api/index.py`

## 📝 Files Changed
1. `api/index.py` - Removed duplicate routes
2. `src/api/main.py` - Added root route

## 🚀 Deploy
```bash
git add api/index.py src/api/main.py
git commit -m "fix: Resolve route conflicts"
git push
```

## 🌍 Set Alias
```bash
vercel alias set aliexpress-api-proxy.vercel.app alistach.vercel.app
```

## ✅ Verify
```bash
curl https://alistach.vercel.app/
curl https://alistach.vercel.app/health
```

## 📚 Full Documentation
See `DEPLOYMENT_FUNCTION_FIX_AND_ALIAS.md` for complete details.
