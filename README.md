# AliExpress Affiliate API Proxy

A secure proxy server that enables custom GPTs to access the AliExpress Affiliate API. The proxy handles complex SHA256 signature generation and provides a simplified REST API interface.

## 🚀 Quick Start

### 1. Deploy to Vercel (Recommended)

[![Deploy with Vercel](https://vercel.com/button)](https://vercel.com/new/clone?repository-url=https://github.com/your-username/aliexpress-api-proxy)

1. Click the deploy button above
2. Connect your GitHub account
3. Set the required environment variables:
   - `ALIEXPRESS_APP_KEY`: Your AliExpress app key
   - `ALIEXPRESS_APP_SECRET`: Your AliExpress app secret
   - `API_TOKEN`: (Optional) Token for proxy authentication
4. Deploy and get your live URL

### 2. Manual Deployment

```bash
# Clone the repository
git clone https://github.com/your-username/aliexpress-api-proxy.git
cd aliexpress-api-proxy

# Install dependencies
npm install

# Set environment variables
cp .env.example .env
# Edit .env with your AliExpress credentials

# Deploy to Vercel
npx vercel --prod
```

## 📋 Prerequisites

### AliExpress Developer Account

1. Register at [AliExpress Open Platform](https://open.aliexpress.com/)
2. Create a new application
3. Get your `App Key` and `App Secret`
4. Apply for affiliate API access

## 🔧 Configuration

### Required Environment Variables

| Variable | Description | Example |
|----------|-------------|---------|
| `ALIEXPRESS_APP_KEY` | Your AliExpress application key | `12345678` |
| `ALIEXPRESS_APP_SECRET` | Your AliExpress application secret | `abcdef123456...` |

### Optional Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `API_TOKEN` | Token for proxy authentication | None (open access) |
| `RATE_LIMIT_MAX` | Max requests per minute per IP | `100` |
| `RATE_LIMIT_WINDOW` | Rate limit window in milliseconds | `60000` |

## 📖 API Usage

### Base URL
```
https://your-deployment-url.vercel.app
```

### Authentication (Optional)
If `API_TOKEN` is configured, include it in requests:

```bash
# Header method
curl -H "Authorization: Bearer YOUR_TOKEN" \
     -H "Content-Type: application/json" \
     -d '{"method":"aliexpress.affiliate.product.query","keywords":"headphones"}' \
     https://your-deployment-url.vercel.app/api/aliexpress

# Header method (alternative)
curl -H "X-API-Key: YOUR_TOKEN" \
     -H "Content-Type: application/json" \
     -d '{"method":"aliexpress.affiliate.product.query","keywords":"headphones"}' \
     https://your-deployment-url.vercel.app/api/aliexpress
```

### Product Search Example

```bash
curl -X POST https://your-deployment-url.vercel.app/api/aliexpress \
  -H "Content-Type: application/json" \
  -d '{
    "method": "aliexpress.affiliate.product.query",
    "keywords": "wireless headphones",
    "page_no": 1,
    "page_size": 20,
    "target_currency": "USD",
    "target_language": "EN",
    "sort": "SALE_PRICE_ASC"
  }'
```

### Response Format

```json
{
  "success": true,
  "data": {
    "aliexpress_affiliate_product_query_response": {
      "resp_result": {
        "result": {
          "products": [...],
          "total_record_count": 1500
        }
      }
    }
  },
  "metadata": {
    "request_id": "uuid-here",
    "timestamp": "2024-01-01T00:00:00Z",
    "processing_time_ms": 250
  }
}
```

## 🔗 Supported AliExpress Methods

| Method | Description | Required Parameters |
|--------|-------------|-------------------|
| `aliexpress.affiliate.product.query` | Search products | `keywords` |
| `aliexpress.affiliate.category.get` | Get categories | None |
| `aliexpress.affiliate.link.generate` | Generate affiliate links | `promotion_link_type`, `source_values` |
| `aliexpress.affiliate.hotproduct.query` | Get hot products | None |
| `aliexpress.affiliate.order.get` | Get order information | `order_ids` |

## 🤖 Custom GPT Integration

### 1. Get Your OpenAPI Spec
Visit `https://your-deployment-url.vercel.app/openapi.json` to get the OpenAPI specification.

### 2. Configure Your GPT
1. Go to ChatGPT → Create a GPT
2. In the "Configure" tab, scroll to "Actions"
3. Click "Create new action"
4. Import your OpenAPI spec
5. Set authentication if you're using `API_TOKEN`

### 3. Example GPT Instructions
```
You are an AliExpress product search assistant. Use the AliExpress API to help users find products.

When users ask for products:
1. Use the aliexpress.affiliate.product.query method
2. Include relevant keywords from their request
3. Set appropriate page_size (10-20 for quick results)
4. Use USD currency and EN language by default
5. Present results in a user-friendly format with prices and links
```

## 🏥 Health Check

Check service status:
```bash
curl https://your-deployment-url.vercel.app/health
```

## 📚 Documentation

- **Interactive API Docs**: `https://your-deployment-url.vercel.app/docs`
- **OpenAPI Spec**: `https://your-deployment-url.vercel.app/openapi.json`

## 🛠️ Local Development

```bash
# Install dependencies
npm install

# Set environment variables
cp .env.example .env
# Edit .env with your credentials

# Start development server
npm run dev

# Server runs on http://localhost:3000
```

## 🔒 Security Features

- **Rate Limiting**: 100 requests per minute per IP
- **Input Validation**: Sanitizes all input parameters
- **CORS Protection**: Configured for OpenAI domains
- **Security Headers**: Helmet.js security middleware
- **Optional Authentication**: API token validation
- **Request Logging**: Comprehensive request/response logging

## 🚨 Troubleshooting

### Common Issues

#### 1. "ALIEXPRESS_APP_KEY not configured"
- Ensure environment variables are set in Vercel dashboard
- Check variable names match exactly (case-sensitive)

#### 2. "Invalid signature" from AliExpress
- Verify your `ALIEXPRESS_APP_SECRET` is correct
- Check that your AliExpress app has affiliate API permissions

#### 3. Rate limit errors
- Reduce request frequency
- Consider implementing client-side caching

#### 4. CORS errors in browser
- Ensure your domain is in the CORS whitelist
- Check that you're using HTTPS

### Debug Mode

Enable detailed logging by setting `NODE_ENV=development` in your environment variables.

## 📄 License

MIT License - see [LICENSE](LICENSE) file for details.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📞 Support

- **Issues**: [GitHub Issues](https://github.com/your-username/aliexpress-api-proxy/issues)
- **Documentation**: [API Docs](https://your-deployment-url.vercel.app/docs)
- **AliExpress API**: [Official Documentation](https://open.aliexpress.com/doc.htm)

---

**Note**: This proxy is for educational and development purposes. Ensure compliance with AliExpress API terms of service and rate limits.