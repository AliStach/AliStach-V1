# Monitoring Guide

## Overview

This guide covers monitoring and observability for the AliExpress Affiliate API Service.

## Health Checks

### Basic Health Check
```bash
curl https://alistach.vercel.app/health
```

Response:
```json
{
  "status": "healthy",
  "timestamp": "2025-12-04T10:30:00Z",
  "version": "2.0.0"
}
```

### System Information
```bash
curl https://alistach.vercel.app/system/info
```

### Cache Statistics
```bash
curl https://alistach.vercel.app/api/cache/stats
```

## Metrics

### Available Metrics

- **Request Metrics**: Count, latency, status codes
- **Cache Metrics**: Hit rate, miss rate, size
- **API Metrics**: Success rate, error rate, response time
- **Rate Limit Metrics**: Violations, remaining quota

### Accessing Metrics
```bash
curl -H "X-Admin-API-Key: your_key" \
  https://alistach.vercel.app/admin/metrics
```

## Logging

### Log Levels
- **DEBUG**: Detailed diagnostic information
- **INFO**: General informational messages
- **WARNING**: Warning messages
- **ERROR**: Error messages
- **CRITICAL**: Critical errors

### Log Format
```json
{
  "timestamp": "2025-12-04T10:30:00Z",
  "level": "INFO",
  "request_id": "req_abc123",
  "message": "Product search completed",
  "duration_ms": 250,
  "cache_hit": true
}
```

### Viewing Logs

**Vercel**:
```bash
vercel logs
```

**Render**:
View logs in Render dashboard

**Docker**:
```bash
docker logs aliexpress-api
```

## Alerting

### Recommended Alerts

1. **High Error Rate**: > 5% errors in 5 minutes
2. **Slow Response**: > 2s average response time
3. **Cache Miss Rate**: > 50% cache misses
4. **Rate Limit Violations**: > 10 violations per minute
5. **API Failures**: > 10% AliExpress API failures

### Setting Up Alerts

Use monitoring tools like:
- Datadog
- New Relic
- Sentry
- Prometheus + Grafana

## Performance Monitoring

### Key Performance Indicators

- **Response Time**: Target < 500ms (cached), < 2s (uncached)
- **Throughput**: Requests per second
- **Error Rate**: Target < 1%
- **Cache Hit Rate**: Target > 80%
- **API Success Rate**: Target > 95%

### Performance Dashboard

Access admin dashboard:
```bash
curl -H "X-Admin-API-Key: your_key" \
  https://alistach.vercel.app/admin/dashboard
```

---

*Last Updated: December 4, 2025*
