# Operations Runbook

## Daily Operations

### Morning Checks
1. Check health endpoint
2. Review error logs from past 24 hours
3. Check cache hit rate
4. Verify API success rate

### Monitoring Dashboard
```bash
curl -H "X-Admin-API-Key: your_key" \
  https://alistach.vercel.app/admin/dashboard
```

## Routine Maintenance

### Weekly Tasks
- Review performance metrics
- Check for outdated dependencies
- Review error patterns
- Optimize slow endpoints

### Monthly Tasks
- Update dependencies
- Review and rotate API keys
- Analyze usage patterns
- Capacity planning

## Incident Response

### Severity Levels

**P1 - Critical**: Service down
- Response time: Immediate
- Escalation: Immediate

**P2 - High**: Degraded performance
- Response time: 1 hour
- Escalation: 2 hours

**P3 - Medium**: Minor issues
- Response time: 4 hours
- Escalation: 1 day

**P4 - Low**: Cosmetic issues
- Response time: 1 day
- Escalation: 1 week

### Incident Response Steps

1. **Acknowledge**: Confirm incident
2. **Assess**: Determine severity
3. **Communicate**: Notify stakeholders
4. **Investigate**: Check logs and metrics
5. **Mitigate**: Apply temporary fix
6. **Resolve**: Implement permanent fix
7. **Document**: Write post-mortem

## Common Procedures

### Clear Cache
```bash
curl -X POST \
  -H "X-Admin-API-Key: your_key" \
  https://alistach.vercel.app/admin/cache/clear
```

### Restart Service

**Vercel**: Redeploy
```bash
vercel --prod
```

**Render**: Restart from dashboard

**Docker**:
```bash
docker restart aliexpress-api
```

### Update Environment Variables

**Vercel**:
1. Go to project settings
2. Update environment variables
3. Redeploy

**Render**:
1. Go to service settings
2. Update environment variables
3. Service auto-restarts

### Scale Service

**Vercel**: Auto-scales

**Render**: Upgrade plan or add instances

**Docker**: Increase replicas
```bash
docker-compose up -d --scale api=3
```

## Backup and Recovery

### Database Backup
```bash
# Backup SQLite databases
cp data/cache.db data/cache.db.backup
cp data/audit.db data/audit.db.backup
```

### Configuration Backup
```bash
# Backup environment variables
cp .env .env.backup
```

### Recovery
```bash
# Restore from backup
cp data/cache.db.backup data/cache.db
cp data/audit.db.backup data/audit.db
```

## Security Procedures

### Rotate API Keys

1. Generate new keys in AliExpress dashboard
2. Update environment variables
3. Test with new keys
4. Revoke old keys

### Review Access Logs
```bash
# Check for suspicious activity
grep "401\|403\|429" logs/aliexpress_api.log
```

### Update Dependencies
```bash
# Check for security vulnerabilities
pip install safety
safety check

# Update dependencies
pip install -U -r requirements.txt
```

## Performance Optimization

### Optimize Cache
- Increase TTL for stable data
- Decrease TTL for dynamic data
- Monitor cache hit rate

### Optimize Queries
- Use appropriate page sizes
- Implement pagination
- Cache frequently accessed data

### Scale Resources
- Monitor CPU and memory usage
- Scale horizontally when needed
- Optimize database queries

---

*Last Updated: December 4, 2025*
