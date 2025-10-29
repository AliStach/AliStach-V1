# 🚀 Quick Start Guide

Your AliExpress API Proxy MVP is ready! Follow these steps to get it live.

## ⚡ Immediate Deployment (5 minutes)

### 1. Get AliExpress Credentials
- Visit [AliExpress Open Platform](https://open.aliexpress.com/)
- Register/login to your developer account
- Create a new app and get your `App Key` and `App Secret`

### 2. Deploy to Vercel
```bash
# Install Vercel CLI
npm install -g vercel

# Deploy (will prompt for configuration)
npx vercel --prod
```

### 3. Set Environment Variables
In Vercel Dashboard → Your Project → Settings → Environment Variables:

| Variable | Value | Required |
|----------|-------|----------|
| `ALIEXPRESS_APP_KEY` | Your AliExpress app key | ✅ Yes |
| `ALIEXPRESS_APP_SECRET` | Your AliExpress app secret | ✅ Yes |
| `API_TOKEN` | Your chosen security token | ⚠️ Recommended |

### 4. Test Your API
```bash
# Replace YOUR_DEPLOYMENT_URL with your Vercel URL
curl -X POST https://YOUR_DEPLOYMENT_URL.vercel.app/api/aliexpress \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_API_TOKEN" \
  -d '{
    "method": "aliexpress.affiliate.product.query",
    "keywords": "wireless headphones",
    "page_size": 5
  }'
```

## 🤖 Connect to Custom GPT

### 1. Get OpenAPI Spec
Visit: `https://YOUR_DEPLOYMENT_URL.vercel.app/openapi.json`

### 2. Create Custom GPT
1. Go to ChatGPT → Create a GPT
2. Configure → Actions → Create new action
3. Import your OpenAPI spec URL
4. Set authentication (Bearer token if using `API_TOKEN`)

### 3. Test GPT Integration
Ask your GPT: "Find me some wireless headphones under $50"

## 📊 Monitor Your API

- **Health Check**: `GET /health`
- **Documentation**: `GET /docs`
- **Logs**: Check Vercel dashboard

## 🔧 What's Included

✅ **Core Features**
- SHA256 signature generation for AliExpress API
- 5 supported AliExpress affiliate methods
- Rate limiting (100 req/min per IP)
- Request validation and sanitization
- Comprehensive error handling
- CORS configured for OpenAI domains

✅ **Security**
- Optional API token authentication
- Input sanitization
- Security headers (Helmet.js)
- Request size limits

✅ **Documentation**
- Interactive Swagger UI at `/docs`
- OpenAPI 3.1.0 specification
- Complete README and deployment guides

✅ **Production Ready**
- Vercel serverless deployment
- Environment variable configuration
- Health monitoring endpoint
- Request/response logging

## 🎯 Supported AliExpress Methods

| Method | Description | Use Case |
|--------|-------------|----------|
| `aliexpress.affiliate.product.query` | Search products | Main product search |
| `aliexpress.affiliate.category.get` | Get categories | Browse categories |
| `aliexpress.affiliate.hotproduct.query` | Hot products | Trending items |
| `aliexpress.affiliate.link.generate` | Generate links | Create affiliate links |
| `aliexpress.affiliate.order.get` | Order info | Track commissions |

## 🚨 Troubleshooting

### Common Issues

**"App key not configured"**
- Set `ALIEXPRESS_APP_KEY` in Vercel environment variables
- Redeploy after setting variables

**"Invalid signature"**
- Verify `ALIEXPRESS_APP_SECRET` is correct
- Check AliExpress app has affiliate API permissions

**CORS errors**
- Ensure using HTTPS
- Check domain is whitelisted in CORS config

### Need Help?
- Check `/health` endpoint for configuration status
- View logs in Vercel dashboard
- Test with curl before GPT integration

## 🎉 You're Done!

Your AliExpress API Proxy is now live and ready for your custom GPT. The MVP includes all core functionality needed for product searches and affiliate operations.

**Your URLs:**
- API Endpoint: `https://YOUR_DEPLOYMENT_URL.vercel.app/api/aliexpress`
- Documentation: `https://YOUR_DEPLOYMENT_URL.vercel.app/docs`
- Health Check: `https://YOUR_DEPLOYMENT_URL.vercel.app/health`

---

**Next Phase**: Consider adding the optional features like caching, comprehensive testing, and performance optimizations from the task list.