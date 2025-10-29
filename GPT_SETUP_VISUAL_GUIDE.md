# 📸 Visual Guide: Connect API to Custom GPT

## 🎯 **Quick Visual Walkthrough**

### **Step 1: Access GPT Builder**
```
ChatGPT → Profile Picture → "My GPTs" → "Create a GPT"
```
**What you'll see**: GPT creation interface with "Create" and "Configure" tabs

### **Step 2: Configure Tab**
```
Click "Configure" tab (not "Create")
```
**What you'll see**: Form with fields for Name, Description, Instructions, etc.

### **Step 3: Fill Basic Info**
```
Name: AliExpress Product Assistant
Description: Find and recommend products from AliExpress
```

### **Step 4: Add Instructions**
**Copy the instructions from CONNECT_TO_GPT.md** - this tells your GPT how to behave

### **Step 5: Scroll to Actions**
**What you'll see**: "Actions" section at the bottom with "Create new action" button

### **Step 6: Import Schema**
```
Click "Create new action"
→ You'll see a schema editor
→ Look for "Import from URL" or similar option
→ Paste: https://your-deployment-url.vercel.app/openapi.json
```

### **Step 7: Authentication (If Needed)**
**If you have API_TOKEN set**:
```
Authentication Type: API Key
API Key: [Your actual token]
Auth Type: Bearer
```

**If no token**: Leave as "None"

### **Step 8: Test**
```
Click "Test" button
→ Try sample request
→ Should see product data response
```

### **Step 9: Save**
```
Click "Save" (top right)
→ Choose visibility (Only me/Anyone with link/Public)
```

---

## 🔍 **What Each Screen Looks Like**

### **GPT Configuration Screen**
```
┌─────────────────────────────────────┐
│ Name: [AliExpress Product Assistant]│
│ Description: [Find and recommend...] │
│ Instructions: [Large text box]       │
│ Conversation starters: [4 examples]  │
│ Knowledge: [Upload files - skip]     │
│ Capabilities: [Web Browsing - off]   │
│ Actions: [Create new action] ←──────│
└─────────────────────────────────────┘
```

### **Actions Configuration Screen**
```
┌─────────────────────────────────────┐
│ Schema: [Large JSON editor]         │
│ ┌─────────────────────────────────┐ │
│ │ Import from URL: [text field]   │ │
│ │ [Import] button                 │ │
│ └─────────────────────────────────┘ │
│ Authentication: [Dropdown]           │
│ Privacy Policy: [Optional]           │
│ [Test] [Save] buttons               │
└─────────────────────────────────────┘
```

---

## 🚨 **Common Visual Cues**

### **✅ Success Indicators**
- Green checkmark next to imported schema
- "Test successful" message
- Schema loads without errors
- GPT saves without warnings

### **❌ Error Indicators**
- Red error messages in schema editor
- "Import failed" notifications
- Authentication errors during test
- CORS or network errors

### **⚠️ Warning Signs**
- Yellow warnings about schema format
- "Mock mode" in API responses (this is OK!)
- Rate limiting messages (normal)

---

## 🎯 **Pro Tips**

### **1. Test Your API First**
Before connecting to GPT, test your API:
```bash
# Open this in browser - should show JSON
https://your-deployment-url.vercel.app/openapi.json

# Test API call
https://your-deployment-url.vercel.app/health
```

### **2. Start Simple**
- First, get it working without authentication
- Add API token later if needed
- Test with simple product searches first

### **3. Use Mock Mode**
- Your API works in mock mode immediately
- Perfect for testing GPT integration
- Add real AliExpress credentials later

### **4. Check Vercel Logs**
- Go to Vercel dashboard
- Check function logs for API calls
- Verify requests are coming from OpenAI

---

## 📱 **Mobile vs Desktop**

### **Desktop (Recommended)**
- Full schema editor
- Better for copying/pasting
- Easier to test and debug

### **Mobile**
- Limited schema editing
- Harder to import URLs
- Use desktop for initial setup

---

## 🔧 **Troubleshooting Visual Cues**

### **Schema Import Issues**
**What you see**: Red error in import field
**Solution**: 
1. Check URL is accessible in browser
2. Try manual copy/paste from `/docs` endpoint
3. Verify deployment is live

### **Authentication Issues**
**What you see**: "Auth failed" during test
**Solution**:
1. Double-check token value
2. Verify token format (no extra spaces)
3. Try without auth first

### **No Response Issues**
**What you see**: Timeout or empty response
**Solution**:
1. Check Vercel deployment status
2. Test API directly in browser
3. Verify CORS settings

---

## 🎉 **Success Checklist**

When everything works, you'll see:
- [ ] ✅ Schema imports successfully
- [ ] ✅ Test returns product data
- [ ] ✅ GPT saves without errors
- [ ] ✅ Chat responses include API data
- [ ] ✅ Products show prices and links
- [ ] ✅ Multiple API methods work

---

## 📞 **Need Help?**

### **Quick Fixes**
1. **Can't import schema**: Use manual copy/paste
2. **Auth errors**: Try without authentication first
3. **No data**: Check if API is in mock mode (normal!)
4. **CORS errors**: Verify deployment includes CORS headers

### **Test Commands**
```bash
# Test your deployment
curl https://your-url.vercel.app/health

# Test OpenAPI spec
curl https://your-url.vercel.app/openapi.json

# Test API call
curl -X POST https://your-url.vercel.app/api/aliexpress \
  -H "Content-Type: application/json" \
  -d '{"method":"aliexpress.affiliate.product.query","keywords":"test"}'
```

**Remember**: Your API works in mock mode immediately - perfect for testing GPT integration while you get real AliExpress credentials! 🚀