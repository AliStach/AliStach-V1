# 🚨 EMERGENCY DEBUG - Ultra Minimal Test

## 🎯 **SITUATION**

- **Local**: All imports work perfectly ✅
- **Vercel**: FUNCTION_INVOCATION_FAILED ❌
- **All fixes applied**: Yes ✅
- **Conclusion**: Must be Vercel-specific issue

## 🧪 **EMERGENCY STRATEGY**

Deployed **ultra-minimal** FastAPI app:
- No imports from `src/`
- Just FastAPI + 2 routes
- Absolute minimum code

### **Test Deployed**

File: `api/ultra_minimal.py`
```python
from fastapi import FastAPI

app = FastAPI(title="Ultra Minimal")

@app.get("/")
def root():
    return {"status": "ok"}

@app.get("/health")
def health():
    return {"status": "healthy"}

handler = app
```

## 📊 **POSSIBLE OUTCOMES**

### **Outcome 1: Ultra minimal works**
```bash
curl https://alistach.vercel.app/health
# Returns: {"status": "healthy", "test": "ultra_minimal"}
```

**Conclusion**: Problem is in our code imports  
**Action**: Gradually add imports to find the breaking one

### **Outcome 2: Ultra minimal STILL fails**
```bash
curl https://alistach.vercel.app/health
# Returns: FUNCTION_INVOCATION_FAILED
```

**Conclusion**: Problem is Vercel configuration or FastAPI version  
**Possible causes**:
1. Vercel Python runtime issue
2. FastAPI version incompatibility
3. Vercel project settings
4. Region-specific issue

**Action**: Check Vercel dashboard settings

## 🔍 **NEXT STEPS**

### **If Ultra Minimal Works**:
1. Restore `vercel_original.json` → `vercel.json`
2. Gradually add imports to `api/index.py`:
   - First: `from src.utils.config import Config`
   - Then: `from src.middleware.security import get_security_manager`
   - Then: `from src.services.aliexpress_service import AliExpressService`
   - Finally: `from src.api.main import app`
3. Find the exact import that breaks
4. Fix that specific import

### **If Ultra Minimal Fails**:
1. Check Vercel project settings
2. Try different Python version
3. Try different FastAPI version
4. Contact Vercel support with minimal reproduction

## 📝 **DEPLOYMENT**

```bash
git add api/ultra_minimal.py vercel.json
git commit -m "test: Ultra minimal FastAPI"
git push origin main
```

Wait 2 minutes, then test:
```bash
curl https://alistach.vercel.app/health
```

---

**Status**: Ultra minimal test deployed, awaiting results...
