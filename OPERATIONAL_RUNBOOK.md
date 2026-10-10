# Operational Runbook

Complete guide for operating and maintaining the AI Decision Engine API.

---

## Table of Contents

1. [Quick Start](#quick-start)
2. [Common Tasks](#common-tasks)
3. [Troubleshooting](#troubleshooting)
4. [Monitoring](#monitoring)
5. [Backup & Recovery](#backup--recovery)
6. [Scaling](#scaling)
7. [Security](#security)
8. [Emergency Procedures](#emergency-procedures)

---

## Quick Start

### Start API Server

```bash
cd api
uvicorn main:app --host 0.0.0.0 --port 8000
```

### Start with Production Config

```bash
uvicorn main:app --host 0.0.0.0 --port 8000 --env-file .env
```

### Check Health

```bash
curl http://localhost:8000/health
```

---

## Common Tasks

### Generate API Key

```bash
python api/manage_api_keys.py generate pro
```

### List All Keys

```bash
python api/manage_api_keys.py list
```

### Deactivate Key

```bash
python api/manage_api_keys.py deactivate <api_key>
```

### View Analytics

```bash
python api/analytics_dashboard.py
```

### Run Tests

```bash
python api/test_api.py
python api/test_comprehensive.py
```

### Check Launch Readiness

```bash
python scripts/prepare_launch.py
```

---

## Troubleshooting

### API Not Responding

1. Check if server is running:
   ```bash
   curl http://localhost:8000/health
   ```

2. Check logs:
   ```bash
   tail -f api.log
   ```

3. Restart server:
   ```bash
   pkill -f uvicorn
   uvicorn main:app --reload
   ```

### Authentication Errors

1. Verify API key is valid:
   ```bash
   python api/manage_api_keys.py info <api_key>
   ```

2. Check rate limits:
   ```bash
   python api/manage_api_keys.py info <api_key>
   ```

3. Generate new key if needed:
   ```bash
   python api/manage_api_keys.py generate pro
   ```

### High Response Times

1. Check server resources:
   ```bash
   top
   htop
   ```

2. Check analytics:
   ```bash
   python api/analytics_dashboard.py
   ```

3. Review caching:
   - Check cache hit rate
   - Adjust cache TTL if needed

### Database Issues (if applicable)

1. Check connection:
   ```bash
   python -c "from api.database import check_connection; check_connection()"
   ```

2. Backup database:
   ```bash
   python scripts/backup_database.py
   ```

---

## Monitoring

### Health Checks

- Endpoint: `/health`
- Frequency: Every 60 seconds
- Alert if: Status != "healthy"

### Metrics to Monitor

- Response time (p50, p95, p99)
- Error rate
- Request rate
- API key usage
- System resources (CPU, memory, disk)

### Set Up Alerts

1. Configure monitoring_config.py
2. Set alert thresholds
3. Add notification channels (email, webhook, Slack)

---

## Backup & Recovery

### Backup API Keys

```bash
cp api/api_keys.json backups/api_keys_$(date +%Y%m%d).json
```

### Backup Analytics Data

```bash
cp api/api_analytics.json backups/analytics_$(date +%Y%m%d).json
```

### Restore from Backup

```bash
cp backups/api_keys_YYYYMMDD.json api/api_keys.json
```

### Full Project Backup

```bash
python scripts/create_backup.py
```

---

## Scaling

### Horizontal Scaling

1. Deploy multiple instances
2. Use load balancer
3. Configure shared session storage (if needed)

### Vertical Scaling

1. Increase server resources
2. Optimize code
3. Enable caching
4. Database optimization (if applicable)

### Rate Limiting

- Adjust limits per tier in `api/api_key_manager.py`
- Monitor usage patterns
- Upgrade users as needed

---

## Security

### Rotate API Keys

1. Generate new key
2. Update clients
3. Deactivate old key

### Review Access Logs

```bash
grep "401\|403" api.log
```

### Update Dependencies

```bash
pip list --outdated
pip install --upgrade <package>
```

### Security Audit

1. Review API key security
2. Check for exposed secrets
3. Verify rate limiting
4. Review access controls

---

## Emergency Procedures

### API Down

1. Check health endpoint
2. Review error logs
3. Restart server
4. Rollback if needed
5. Notify users

### Security Breach

1. Rotate all API keys immediately
2. Review access logs
3. Identify compromised keys
4. Deactivate compromised keys
5. Notify affected users
6. Document incident

### High Error Rate

1. Check error logs
2. Identify failing endpoint
3. Review recent changes
4. Rollback if needed
5. Fix and redeploy

### Data Loss

1. Stop writes immediately
2. Restore from backup
3. Verify data integrity
4. Resume operations
5. Investigate root cause

---

## Maintenance Windows

### Scheduled Maintenance

1. Notify users 48 hours in advance
2. Schedule during low-traffic hours
3. Perform maintenance
4. Verify system health
5. Resume operations

### Zero-Downtime Updates

1. Deploy to staging
2. Test thoroughly
3. Deploy to production (blue-green)
4. Monitor closely
5. Rollback if issues

---

## Contact & Support

- Technical Issues: Check logs and runbooks
- Security Incidents: Follow emergency procedures
- User Support: support@example.com

---

*Last Updated: 2025-11-05*
*Version: 1.0.0*

