# Troubleshooting Guide

## Common Issues

### 1. Rate Limit Exceeded

**Symptom**: 429 Too Many Requests

**Solution**:
- Wait for rate limit to reset (check `Retry-After` header)
- Reduce request frequency
- Implement client-side rate limiting
- Consider caching responses

### 2. API Authentication Errors

**Symptom**: 401 Unauthorized from AliExpress API

**Solution**:
- Verify `ALIEXPRESS_APP_KEY` is correct
- Verify `ALIEXPRESS_APP_SECRET` is correct
- Check API credentials haven't expired
- Ensure no extra whitespace in credentials

### 3. Slow Response Times

**Symptom**: Requests taking > 5 seconds

**Solution**:
- Check AliExpress API status
- Verify cache is working (check `/api/cache/stats`)
- Reduce page_size in requests
- Check network connectivity

### 4. Cache Not Working

**Symptom**: All requests hitting AliExpress API

**Solution**:
- Verify `CACHE_ENABLED=true`
- Check cache statistics
- Clear and rebuild cache
- Verify disk space for SQLite

### 5. CORS Errors

**Symptom**: Browser blocks requests

**Solution**:
- Add origin to `ALLOWED_ORIGINS`
- Verify CORS middleware is enabled
- Check request headers
- Use server-side requests instead

## Debugging

### Enable Debug Logging

Set environment variable:
```
LOG_LEVEL=DEBUG
```

### Check Application Logs

**Vercel**:
```bash
vercel logs --follow
```

**Render**:
View in dashboard

**Docker**:
```bash
docker logs -f aliexpress-api
```

### Test Endpoints

```bash
# Health check
curl https://alistach.vercel.app/health

# System info
curl https://alistach.vercel.app/system/info

# Cache stats
curl https://alistach.vercel.app/api/cache/stats
```

## Error Codes

| Code | Meaning | Solution |
|------|---------|----------|
| 400 | Bad Request | Check request parameters |
| 401 | Unauthorized | Verify API key |
| 429 | Rate Limit | Wait and retry |
| 500 | Server Error | Check logs |
| 502 | Bad Gateway | AliExpress API issue |
| 503 | Service Unavailable | Temporary outage |

## Performance Issues

### High Memory Usage

**Solution**:
- Clear cache: `POST /admin/cache/clear`
- Reduce cache TTL
- Restart service

### High CPU Usage

**Solution**:
- Check for infinite loops in logs
- Reduce concurrent requests
- Scale horizontally

## Getting Help

1. Check logs for error messages
2. Review this troubleshooting guide
3. Check [GitHub Issues](https://github.com/AliStach/AliStach-V1/issues)
4. Contact support with:
   - Error message
   - Request ID
   - Timestamp
   - Steps to reproduce

---

*Last Updated: December 4, 2025*
