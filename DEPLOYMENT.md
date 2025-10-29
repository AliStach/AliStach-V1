# Deployment Guide

This guide covers deploying the AliExpress API Proxy to various platforms.

## 🚀 Vercel (Recommended)

Vercel provides the best experience for this Node.js serverless application.

### Quick Deploy

1. **One-Click Deploy**
   ```
   https://vercel.com/new/clone?repository-url=https://github.com/your-username/aliexpress-api-proxy
   ```

2. **Manual Deploy**
   ```bash
   # Install Vercel CLI
   npm i -g vercel
   
   # Deploy
   vercel --prod
   ```

### Environment Variables Setup

In Vercel Dashboard → Project → Settings → Environment Variables:

| Variable | Value | Notes |
|----------|-------|-------|
| `ALIEXPRESS_APP_KEY` | Your app key | Required |
| `ALIEXPRESS_APP_SECRET` | Your app secret | Required, keep secret |
| `API_TOKEN` | Your chosen token | Optional, for authentication |
| `NODE_ENV` | `production` | Recommended |

### Custom Domain (Optional)

1. Go to Vercel Dashboard → Project → Settings → Domains
2. Add your custom domain
3. Update DNS records as instructed
4. Update OpenAPI spec with new URL

## 🐳 Docker Deployment

### Build and Run

```bash
# Create Dockerfile
cat > Dockerfile << 'EOF'
FROM node:18-alpine

WORKDIR /app

COPY package*.json ./
RUN npm ci --only=production

COPY . .

EXPOSE 3000

CMD ["npm", "start"]
EOF

# Build image
docker build -t aliexpress-proxy .

# Run container
docker run -d \
  -p 3000:3000 \
  -e ALIEXPRESS_APP_KEY=your_key \
  -e ALIEXPRESS_APP_SECRET=your_secret \
  -e API_TOKEN=your_token \
  --name aliexpress-proxy \
  aliexpress-proxy
```

### Docker Compose

```yaml
# docker-compose.yml
version: '3.8'

services:
  aliexpress-proxy:
    build: .
    ports:
      - "3000:3000"
    environment:
      - ALIEXPRESS_APP_KEY=${ALIEXPRESS_APP_KEY}
      - ALIEXPRESS_APP_SECRET=${ALIEXPRESS_APP_SECRET}
      - API_TOKEN=${API_TOKEN}
      - NODE_ENV=production
    restart: unless-stopped
```

## ☁️ Other Platforms

### Netlify Functions

1. **Install Netlify CLI**
   ```bash
   npm install -g netlify-cli
   ```

2. **Create netlify.toml**
   ```toml
   [build]
     functions = "netlify/functions"
   
   [[redirects]]
     from = "/api/*"
     to = "/.netlify/functions/api/:splat"
     status = 200
   
   [[redirects]]
     from = "/*"
     to = "/.netlify/functions/api"
     status = 200
   ```

3. **Adapt for Netlify**
   ```bash
   mkdir -p netlify/functions
   cp api/index.js netlify/functions/api.js
   # Modify exports for Netlify handler format
   ```

### Railway

1. **Connect Repository**
   - Go to [Railway](https://railway.app)
   - Connect your GitHub repository

2. **Set Environment Variables**
   - Add `ALIEXPRESS_APP_KEY`
   - Add `ALIEXPRESS_APP_SECRET`
   - Add `API_TOKEN` (optional)

3. **Deploy**
   - Railway auto-deploys on git push

### Render

1. **Create Web Service**
   - Go to [Render](https://render.com)
   - Connect repository

2. **Configuration**
   - Build Command: `npm install`
   - Start Command: `npm start`
   - Environment: Node.js

3. **Environment Variables**
   - Set required variables in Render dashboard

## 🔧 Configuration for Production

### Environment Variables Checklist

- [ ] `ALIEXPRESS_APP_KEY` - Your AliExpress app key
- [ ] `ALIEXPRESS_APP_SECRET` - Your AliExpress app secret  
- [ ] `API_TOKEN` - Optional authentication token
- [ ] `NODE_ENV` - Set to `production`
- [ ] `RATE_LIMIT_MAX` - Optional, default 100
- [ ] `RATE_LIMIT_WINDOW` - Optional, default 60000

### Security Considerations

1. **Never commit secrets to git**
   ```bash
   # Add to .gitignore
   echo ".env" >> .gitignore
   echo ".env.local" >> .gitignore
   ```

2. **Use platform secret management**
   - Vercel: Environment Variables
   - Railway: Variables tab
   - Render: Environment tab

3. **Enable API token authentication**
   ```bash
   # Generate secure token
   openssl rand -hex 32
   ```

### Performance Optimization

1. **Enable compression** (handled by platforms)
2. **Set appropriate timeouts**
3. **Monitor memory usage**
4. **Use CDN for static assets** (if any)

## 📊 Monitoring

### Health Checks

Most platforms support health checks using:
```
GET /health
```

### Logging

- **Vercel**: View logs in dashboard
- **Railway**: Built-in logging
- **Render**: Log streaming available

### Metrics

Monitor these key metrics:
- Response time
- Error rate
- Request volume
- Memory usage

## 🚨 Troubleshooting

### Common Deployment Issues

1. **Build Failures**
   ```bash
   # Check Node.js version compatibility
   node --version  # Should be 18+
   
   # Clear npm cache
   npm cache clean --force
   ```

2. **Environment Variable Issues**
   ```bash
   # Test locally first
   cp .env.example .env
   # Edit .env with real values
   npm run dev
   ```

3. **Memory Limits**
   - Increase memory allocation in platform settings
   - Optimize code for lower memory usage

4. **Timeout Issues**
   - Increase function timeout (Vercel: 30s max on free tier)
   - Optimize AliExpress API calls

### Platform-Specific Issues

#### Vercel
- **Cold starts**: First request may be slower
- **Function size**: Keep under 50MB
- **Timeout**: 10s hobby, 30s pro

#### Railway
- **Port binding**: Use `process.env.PORT`
- **Memory**: Monitor usage in dashboard

#### Render
- **Sleep mode**: Free tier sleeps after inactivity
- **Build time**: Can be slower than other platforms

## 🔄 CI/CD Setup

### GitHub Actions (Vercel)

```yaml
# .github/workflows/deploy.yml
name: Deploy to Vercel

on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - uses: amondnet/vercel-action@v20
        with:
          vercel-token: ${{ secrets.VERCEL_TOKEN }}
          vercel-org-id: ${{ secrets.ORG_ID }}
          vercel-project-id: ${{ secrets.PROJECT_ID }}
          vercel-args: '--prod'
```

### Automated Testing

```yaml
# Add to workflow before deploy
- name: Run tests
  run: |
    npm install
    npm test
```

## 📈 Scaling Considerations

### Traffic Growth
- Monitor request patterns
- Consider caching strategies
- Implement request queuing if needed

### Multiple Regions
- Deploy to multiple regions for lower latency
- Use platform-specific multi-region features

### Load Balancing
- Most serverless platforms handle this automatically
- Consider API Gateway for complex routing

---

**Next Steps**: After deployment, test your API and integrate with your custom GPT!