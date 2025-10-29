# 🔑 How to Get AliExpress API Credentials

To see real data from AliExpress, you need to get API credentials from AliExpress. Here's how:

## Step 1: Register for AliExpress Developer Account

1. **Visit AliExpress Open Platform**
   - Go to: https://open.aliexpress.com/
   - Click "Register" or "Sign In"

2. **Complete Registration**
   - Use your existing AliExpress account or create a new one
   - Verify your email and phone number
   - Complete the developer profile

## Step 2: Create an Application

1. **Go to Developer Console**
   - Navigate to "My Apps" or "Applications"
   - Click "Create App" or "New Application"

2. **Fill Application Details**
   - **App Name**: "My GPT Proxy" (or any name)
   - **App Type**: Select "Web Application"
   - **Description**: "API proxy for custom GPT integration"
   - **Website URL**: You can use a placeholder like "https://example.com"

3. **Submit for Review**
   - Submit your application
   - Wait for approval (usually 1-3 business days)

## Step 3: Get API Credentials

Once approved, you'll get:
- **App Key** (Public): Something like `12345678`
- **App Secret** (Private): Something like `abcdef1234567890abcdef1234567890`

## Step 4: Apply for Affiliate API Access

1. **Request API Permissions**
   - In your app dashboard, request access to "Affiliate API"
   - This may require additional approval

2. **Available Methods**
   - `aliexpress.affiliate.product.query` - Search products
   - `aliexpress.affiliate.category.get` - Get categories  
   - `aliexpress.affiliate.hotproduct.query` - Hot products
   - `aliexpress.affiliate.link.generate` - Generate affiliate links
   - `aliexpress.affiliate.order.get` - Order tracking

## Step 5: Update Your Environment

Once you have credentials, update your `.env` file:

```bash
# Replace with your actual credentials
ALIEXPRESS_APP_KEY=12345678
ALIEXPRESS_APP_SECRET=abcdef1234567890abcdef1234567890

# Optional: Add API token for security
API_TOKEN=your_secure_random_token_here
```

## Step 6: Test with Real Data

After updating `.env`, restart the server and test:

```bash
# Restart server
npm run dev

# Test with real AliExpress data
curl -X POST http://localhost:3000/api/aliexpress \
  -H "Content-Type: application/json" \
  -d '{
    "method": "aliexpress.affiliate.product.query",
    "keywords": "wireless headphones",
    "page_size": 5
  }'
```

## 🚨 Important Notes

1. **Approval Time**: AliExpress approval can take 1-3 business days
2. **API Limits**: Free tier has rate limits (usually 1000 requests/day)
3. **Affiliate Program**: You may need to join AliExpress affiliate program
4. **Compliance**: Ensure your use case complies with AliExpress terms

## 🧪 Test Without Real Credentials

If you want to test the proxy structure without waiting for approval, I can create a mock mode that simulates AliExpress responses for development purposes.

## 📞 Need Help?

- **AliExpress Support**: Contact through their developer portal
- **API Documentation**: https://open.aliexpress.com/doc.htm
- **Developer Forum**: Check AliExpress developer community

---

**Once you have credentials, update the `.env` file and we'll test with real AliExpress data!**