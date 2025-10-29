# 🤖 Connect Your AliExpress API to Custom GPT

## Step-by-Step Guide to GPT Integration

### Prerequisites
- ✅ Your API is deployed on Vercel (get URL from deployment)
- ✅ ChatGPT Plus subscription (required for custom GPTs)
- ✅ Your OpenAPI spec URL: `https://your-deployment-url.vercel.app/openapi.json`

---

## 🚀 **Step 1: Create Your Custom GPT**

### 1.1 Go to ChatGPT
- Visit: https://chat.openai.com/
- Make sure you're logged in with ChatGPT Plus

### 1.2 Access GPT Builder
- Click your **profile picture** (top right)
- Select **"My GPTs"**
- Click **"Create a GPT"**

### 1.3 Choose Creation Method
- Click **"Configure"** tab (skip the conversation builder)

---

## 🛠️ **Step 2: Configure Your GPT**

### 2.1 Basic Information
```
Name: AliExpress Product Assistant
Description: Find and recommend products from AliExpress with real prices, reviews, and affiliate links
```

### 2.2 Instructions (Copy this exactly)
```
You are an expert AliExpress product search assistant. Your job is to help users find the best products on AliExpress using the AliExpress Affiliate API.

## Your Capabilities:
- Search for products by keywords
- Browse product categories
- Find trending/hot products
- Generate affiliate links
- Check order information

## How to Help Users:

### For Product Searches:
1. Use aliexpress.affiliate.product.query with user's keywords
2. Show 3-5 best results with:
   - Product title and main features
   - Current price vs original price (highlight discounts)
   - Customer rating and review count
   - Estimated commission earnings
   - Direct product link

### For Category Browsing:
1. Use aliexpress.affiliate.category.get to show available categories
2. Help users navigate to specific product types

### For Trending Products:
1. Use aliexpress.affiliate.hotproduct.query for popular items
2. Highlight why they're trending (sales volume, ratings)

## Response Format:
Always format responses clearly with:
- 🏷️ Product name and key features
- 💰 Price (show discount percentage if available)
- ⭐ Rating and review count
- 🔗 Direct link to product
- 💵 Potential commission (if available)

## Important Rules:
- Always show prices in USD unless user specifies otherwise
- Highlight good deals and high-rated products
- Be honest about product quality based on ratings
- Include affiliate links when available
- If API returns mock data, mention it's sample data

Be helpful, enthusiastic, and focus on finding users the best deals!
```

### 2.3 Conversation Starters
Add these 4 conversation starters:
```
1. "Find me wireless headphones under $50"
2. "What are the trending electronics right now?"
3. "Show me the best deals in home & garden"
4. "Help me find phone accessories with good reviews"
```

---

## 🔗 **Step 3: Add Your API (Actions)**

### 3.1 Scroll to Actions Section
- In the Configure tab, scroll down to **"Actions"**
- Click **"Create new action"**

### 3.2 Import Your OpenAPI Spec
- **Method 1 - Import from URL (Recommended)**:
  ```
  https://your-deployment-url.vercel.app/openapi.json
  ```
  - Paste your URL in the import field
  - Click **"Import"**

- **Method 2 - Manual Schema**:
  - If URL import doesn't work, copy the schema from `/docs` endpoint
  - Paste it in the schema editor

### 3.3 Configure Authentication (If Using API Token)

**If you set `API_TOKEN` in your environment variables:**

1. **Authentication Type**: `API Key`
2. **API Key**: Your actual token value (from .env file)
3. **Auth Type**: `Bearer`
4. **Header Name**: `Authorization`

**If no API token (open access):**
- Leave authentication as "None"

### 3.4 Test the Connection
- Click **"Test"** next to your action
- Try a sample request:
  ```json
  {
    "method": "aliexpress.affiliate.product.query",
    "keywords": "bluetooth headphones",
    "page_size": 3
  }
  ```
- Should return product data (mock or real depending on your setup)

---

## 🎯 **Step 4: Finalize and Test**

### 4.1 Save Your GPT
- Click **"Save"** (top right)
- Choose visibility:
  - **"Only me"** - Private use
  - **"Anyone with a link"** - Shareable
  - **"Public"** - Listed in GPT store

### 4.2 Test Your GPT
Try these test queries:
```
1. "Find me some wireless earbuds under $30"
2. "What are the hot products right now?"
3. "Show me phone cases with good reviews"
4. "Browse electronics categories"
```

### 4.3 Verify API Calls
- Check that your GPT is making API calls
- Verify responses include product data
- Confirm links and prices are showing

---

## 🔧 **Troubleshooting**

### Common Issues:

#### 1. "Schema Import Failed"
**Solution**: 
- Check your deployment URL is correct
- Try accessing `/openapi.json` directly in browser
- Use manual schema copy if needed

#### 2. "Authentication Failed"
**Solutions**:
- Verify API token is correct
- Check token is set in Vercel environment variables
- Try without authentication first (remove API_TOKEN)

#### 3. "No Response from API"
**Solutions**:
- Check Vercel deployment is live
- Test API directly with curl/Postman
- Verify CORS settings allow OpenAI domains

#### 4. "Mock Data Warning"
**This is normal!** Your API is working correctly:
- Mock mode activates when AliExpress credentials aren't set
- Add real credentials to get live data
- Mock data is perfect for testing GPT integration

### 3. Test API Directly
```bash
# Test your deployed API
curl -X POST https://your-deployment-url.vercel.app/api/aliexpress \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{
    "method": "aliexpress.affiliate.product.query",
    "keywords": "test product",
    "page_size": 2
  }'
```

---

## 📋 **Quick Checklist**

Before connecting to GPT, ensure:
- [ ] API is deployed and accessible
- [ ] OpenAPI spec loads at `/openapi.json`
- [ ] Health check passes at `/health`
- [ ] Test API call returns data
- [ ] Authentication works (if using tokens)
- [ ] CORS allows OpenAI domains

---

## 🎉 **Success!**

Once connected, your GPT will be able to:
- ✅ Search AliExpress products by keywords
- ✅ Browse product categories
- ✅ Find trending items
- ✅ Show prices, ratings, and reviews
- ✅ Generate affiliate links
- ✅ Help users find the best deals

Your users can now ask natural language questions like:
- "Find me cheap wireless headphones with good reviews"
- "What are the best phone accessories under $20?"
- "Show me trending electronics this week"

**Your AliExpress GPT is ready to help users discover amazing products!** 🛍️

---

## 🔄 **Next Steps**

1. **Get Real AliExpress Credentials** (see GET_ALIEXPRESS_CREDENTIALS.md)
2. **Update Environment Variables** in Vercel
3. **Test with Live Data**
4. **Share Your GPT** with others
5. **Monitor Usage** in Vercel dashboard

**Your GPT will automatically switch from mock to real data once you add AliExpress credentials!**