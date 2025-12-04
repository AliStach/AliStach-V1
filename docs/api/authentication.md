# API Authentication

## Overview

The AliExpress Affiliate API Service supports multiple authentication methods depending on the endpoint being accessed.

## Public Endpoints

Most endpoints are publicly accessible without authentication:
- Product search
- Category retrieval
- Affiliate link generation
- Health checks

## Admin Endpoints

Admin endpoints require API key authentication:
- `/admin/dashboard`
- `/admin/cache/clear`
- `/admin/metrics`

### Using Admin API Key

Set the `X-Admin-API-Key` header:

```bash
curl -H "X-Admin-API-Key: your_admin_key" \
  https://alistach.vercel.app/admin/dashboard
```

## Rate Limiting

All endpoints are subject to rate limiting:
- 60 requests per minute per IP
- 5 requests per second per IP

Rate limit headers are included in responses:
```
X-RateLimit-Limit: 60
X-RateLimit-Remaining: 45
X-RateLimit-Reset: 1638360000
```

## CORS

CORS is configured for:
- `https://chat.openai.com`
- `https://chatgpt.com`

Additional origins can be configured via environment variables.

---

*Last Updated: December 4, 2025*
