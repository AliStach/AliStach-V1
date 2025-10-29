# 🛍️ AliExpress Affiliate API Proxy

A secure, production-ready proxy server that enables custom GPTs to access the AliExpress Affiliate API. Handles complex SHA256 signature generation and provides a clean REST API interface optimized for OpenAI GPT integration.

## 🚀 **Live Demo**

The API works immediately with realistic mock data - perfect for testing GPT integration while getting real AliExpress credentials.

## ✨ **Features**

- 🔐 **Automatic Authentication** - Handles SHA256 signature generation for AliExpress API
- 🤖 **GPT-Optimized** - OpenAPI 3.1.0 spec ready for custom GPT integration  
- 🧪 **Mock Mode** - Realistic product data for immediate testing
- 🔒 **Production Security** - Rate limiting, CORS, input validation, security headers
- 📊 **Monitoring** - Health checks, request logging, performance metrics
- ⚡ **Serverless Ready** - Optimized for Vercel deployment with auto-scaling

## 🎯 **Supported AliExpress Methods**

| Method | Description | Use Case |
|--------|-------------|----------|
| `aliexpress.affiliate.product.query` | Search products | Main product search |
| `aliexpress.affiliate.category.get` | Get categories | Browse categories |
| `aliexpress.affiliate.hotproduct.query` | Hot products | Trending items |
| `aliexpress.affiliate.link.generate` | Generate links | Create affiliate links |
| `aliexpress.affiliate.order.get` | Order info | Track commissions |

## 🚀 **Quick Deploy to Vercel**

[![Deploy with Vercel](https://vercel.com/button)](https://vercel.com/new/clone?repository-url=https://github.com/your-username/aliexpress-api-proxy)

1. Click the deploy button above
2. Connect your GitHub account  
3. Set environment variables (see below)
4. Deploy and get your live URL

## 🔧 **Environment Variables**

### Required for Production
```bash
ALIEXPRESS_APP_KEY=your_aliexpress_app_key
ALIEXPRESS_APP_SECRET=your_aliexpress_app_secret
```

### Optional
```bash
API_TOKEN=your_secure_token          # Enable authentication
FORCE_MOCK_MODE=true                 # Force mock mode for testing
RATE_LIMIT_MAX=100                   # Requests per minute
NODE_ENV=production                  # Environment
```

## 📖 **API Usage**

### Product Search
```bash
POST /api/aliexpress
Content-Type: application/json

{
  "method": "aliexpress.affiliate.product.query",
  "keywords": "wireless headphones",
  "page_size": 10,
  "target_currency": "USD"
}
```

### Response Format
```json
{
  "success": true,
  "data": {
    "aliexpress_affiliate_product_query_response": {
      "resp_result": {
        "result": {
          "products": [
            {
              "product_title": "Wireless Bluetooth Headphones",
              "app_sale_price": "29.99",
              "original_price": "59.99",
              "discount": "50%",
              "evaluate_rate": "98.5%",
              "commission_rate": "30%"
            }
          ]
        }
      }
    }
  },
  "metadata": {
    "mock_mode": true,
    "processing_time_ms": 250
  }
}
```

## 🤖 **Custom GPT Integration**

### 1. Get Your OpenAPI Spec
```
https://your-deployment-url.vercel.app/openapi-gpt.json
```

### 2. Create Custom GPT
1. Go to ChatGPT → My GPTs → Create a GPT
2. Configure → Actions → Create new action
3. Import from URL: paste your OpenAPI spec URL
4. Set authentication if using API_TOKEN

### 3. Sample GPT Instructions
```
You are an AliExpress product search assistant. Help users find products using the AliExpress API.

For product searches: Use aliexpress.affiliate.product.query
For categories: Use aliexpress.affiliate.category.get  
For trending items: Use aliexpress.affiliate.hotproduct.query

Always show prices, discounts, ratings, and affiliate links.
```

## 🏃‍♂️ **Local Development**

```bash
# Clone repository
git clone https://github.com/your-username/aliexpress-api-proxy.git
cd aliexpress-api-proxy

# Install dependencies
npm install

# Set up environment
cp .env.example .env
# Edit .env with your credentials

# Start development server
npm run dev

# Server runs on http://localhost:3000
```

## 📊 **API Endpoints**

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/aliexpress` | POST | Main proxy endpoint |
| `/health` | GET | Health check |
| `/docs` | GET | Interactive API documentation |
| `/openapi.json` | GET | OpenAPI specification |
| `/openapi-gpt.json` | GET | GPT-optimized OpenAPI spec |

## 🔒 **Security Features**

- ✅ **Rate Limiting** - 100 requests/minute per IP
- ✅ **Input Sanitization** - Prevents injection attacks  
- ✅ **CORS Protection** - Configured for OpenAI domains
- ✅ **Security Headers** - CSP, HSTS, XSS protection
- ✅ **Optional Authentication** - API token support
- ✅ **Request Logging** - Comprehensive monitoring

## 📈 **Performance**

- **Response Time**: 200-700ms (mock), 1-2s (real API)
- **Memory Usage**: ~8MB heap
- **Scalability**: Serverless auto-scaling
- **Uptime**: 99.9%+ on Vercel

## 🧪 **Testing**

```bash
# Test health endpoint
curl https://your-deployment-url.vercel.app/health

# Test API call
curl -X POST https://your-deployment-url.vercel.app/api/aliexpress \
  -H "Content-Type: application/json" \
  -d '{
    "method": "aliexpress.affiliate.product.query",
    "keywords": "smartwatch",
    "page_size": 3
  }'
```

## 📋 **Getting AliExpress Credentials**

1. Register at [AliExpress Open Platform](https://open.aliexpress.com/)
2. Create a new application
3. Get your App Key and App Secret
4. Apply for affiliate API access
5. Update environment variables

## 🚨 **Troubleshooting**

### Mock Mode (Normal)
If you see `"mock_mode": true` in responses:
- This is normal when AliExpress credentials aren't configured
- Perfect for testing GPT integration
- Add real credentials to get live data

### Common Issues
- **CORS errors**: Check domain whitelist in CORS config
- **Rate limiting**: Reduce request frequency  
- **Auth errors**: Verify API_TOKEN configuration

## 📄 **License**

MIT License - see [LICENSE](LICENSE) file for details.

## 🤝 **Contributing**

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📞 **Support**

- **Issues**: [GitHub Issues](https://github.com/your-username/aliexpress-api-proxy/issues)
- **Documentation**: [Live API Docs](https://your-deployment-url.vercel.app/docs)

---

**Built for developers who want to integrate AliExpress affiliate data into their custom GPTs without dealing with complex authentication and signature generation.** 🚀