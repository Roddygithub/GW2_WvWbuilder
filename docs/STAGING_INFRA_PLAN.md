# 🏗️ Staging Infrastructure Plan - v3.2.0

**Document Version**: 1.0  
**Created**: 2025-10-15 21:35 UTC+2  
**Status**: ✅ READY FOR IMPLEMENTATION  
**Target Release**: v3.2.0-pre

---

## 🎯 Overview

This document outlines the complete infrastructure plan for the staging environment of GW2_WvWbuilder. The staging environment serves as a pre-production testing ground that mirrors the production setup.

---

## 📋 Infrastructure Components

### Core Services

| Service | Technology | Port | Purpose |
|---------|------------|------|---------|
| **Backend API** | FastAPI (Python 3.11) | 8000 | REST API & Business Logic |
| **Frontend** | React 18 + Vite 5 | 3000 | User Interface |
| **Database** | PostgreSQL 15 | 5432 | Primary Data Store |
| **Cache** | Redis 7 | 6379 | Session & Cache Layer |
| **Reverse Proxy** | Nginx latest | 80/443 | Load Balancing & SSL |
| **Prometheus** | Prometheus latest | 9090 | Metrics Collection |
| **Grafana** | Grafana latest | 3001 | Monitoring Dashboards |

### Supporting Services

| Service | Purpose | Configuration |
|---------|---------|---------------|
| **Docker Compose** | Container Orchestration | `docker-compose.staging.yml` |
| **GitHub Actions** | CI/CD Pipeline | `deploy-staging.yml` |
| **Backup System** | Database Backups | Daily automated backups |
| **Log Aggregation** | Centralized Logging | File-based + rotation |

---

## 🔧 Configuration

### Environment Variables

**Backend (`backend/.env.staging`)**:
```bash
# Application
ENVIRONMENT=staging
DEBUG=false
TESTING=false
PROJECT_NAME="GW2 WvW Builder API - Staging"
API_V1_STR="/api/v1"
SERVER_NAME=staging.gw2wvwbuilder.example.com
SERVER_HOST=https://staging.gw2wvwbuilder.example.com

# Security
SECRET_KEY=${STAGING_SECRET_KEY}
JWT_SECRET_KEY=${STAGING_JWT_SECRET}
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=480
REFRESH_TOKEN_EXPIRE_DAYS=30

# Database
DATABASE_TYPE=postgresql
DATABASE_URL=postgresql://staging_user:${STAGING_DB_PASSWORD}@postgres:5432/staging_db
ASYNC_SQLALCHEMY_DATABASE_URI=postgresql+asyncpg://staging_user:${STAGING_DB_PASSWORD}@postgres:5432/staging_db

# Redis
REDIS_URL=redis://redis:6379/0

# CORS
BACKEND_CORS_ORIGINS=["https://staging.gw2wvwbuilder.example.com","http://localhost:3000"]

# Logging
LOG_LEVEL=INFO
LOG_TO_FILE=true
LOG_FILE=/var/log/gw2/backend.log

# Monitoring
PROMETHEUS_ENABLED=true
METRICS_PORT=9090
```

**Frontend (`frontend/.env.staging`)**:
```bash
VITE_API_URL=https://staging.gw2wvwbuilder.example.com/api/v1
VITE_ENVIRONMENT=staging
VITE_ENABLE_ANALYTICS=false
VITE_ENABLE_DEBUG=false
```

### Docker Compose Configuration

**File**: `docker-compose.staging.yml`

Key features:
- Health checks for all services
- Resource limits (CPU & memory)
- Automatic restart policies
- Volume persistence
- Network isolation
- Logging configuration

---

## 🌐 Network Architecture

```
Internet
   ↓
[Nginx Reverse Proxy :80/443]
   ├── → Frontend :3000 (React/Vite)
   └── → Backend :8000 (FastAPI)
         ├── → PostgreSQL :5432
         ├── → Redis :6379
         └── → Prometheus :9090
               └→ Grafana :3001
```

### Network Segmentation

- **Public Network**: Nginx (port 80/443)
- **App Network**: Frontend + Backend
- **Data Network**: PostgreSQL + Redis
- **Monitoring Network**: Prometheus + Grafana

---

## 🚀 Deployment Process

### Automated Deployment (GitHub Actions)

**Workflow**: `.github/workflows/deploy-staging.yml`

**Stages**:
1. **Pre-deployment Validation**
   - Validate Docker Compose config
   - Check environment variables
   - Verify secrets availability

2. **Build & Test**
   - Run backend unit tests
   - Run frontend unit tests
   - Build production artifacts
   - Upload build artifacts

3. **Deploy**
   - SSH to staging server
   - Pull latest code
   - Build Docker images
   - Run database migrations
   - Deploy services with docker-compose
   - Run health checks

4. **Post-deployment Verification**
   - Verify all endpoints responding
   - Run smoke tests
   - Check service health
   - Generate deployment summary

### Manual Deployment

```bash
# 1. SSH to staging server
ssh user@staging.gw2wvwbuilder.example.com

# 2. Navigate to project directory
cd /opt/gw2-wvwbuilder

# 3. Pull latest changes
git pull origin develop

# 4. Deploy with Docker Compose
docker-compose -f docker-compose.staging.yml pull
docker-compose -f docker-compose.staging.yml up -d

# 5. Run migrations
docker-compose -f docker-compose.staging.yml exec backend poetry run alembic upgrade head

# 6. Verify deployment
curl -fsS https://staging.gw2wvwbuilder.example.com/health
```

---

## 📊 Monitoring & Observability

### Health Checks

**Endpoints**:
- `/health` - Overall application health
- `/api/v1/health` - Backend API health
- `/metrics` - Prometheus metrics

**Monitored Metrics**:
- Request rate (req/s)
- Response time (p50, p95, p99)
- Error rate (%)
- CPU & Memory usage
- Database connection pool
- Cache hit/miss rate
- Active users

### Logging

**Log Levels**:
- `ERROR`: Application errors
- `WARNING`: Performance issues
- `INFO`: Normal operations
- `DEBUG`: Detailed debugging (disabled in staging)

**Log Aggregation**:
- Backend logs: `/var/log/gw2/backend.log`
- Frontend logs: Browser console + server logs
- Nginx logs: `/var/log/nginx/access.log`, `/var/log/nginx/error.log`

**Log Rotation**:
- Daily rotation
- Keep 30 days of logs
- Compress old logs

### Alerting

**Alert Conditions**:
- API response time > 2s for 5 minutes
- Error rate > 5% for 2 minutes
- CPU usage > 80% for 10 minutes
- Memory usage > 90% for 5 minutes
- Disk usage > 85%
- Service unhealthy for 3 minutes

**Alert Channels**:
- Email notifications
- Slack webhook (optional)
- PagerDuty (optional)

---

## 🔒 Security

### SSL/TLS Configuration

**Certificate Management**:
- Let's Encrypt automatic certificates
- Auto-renewal with certbot
- HTTPS enforced for all traffic
- TLS 1.2+ only

**Nginx SSL Configuration**:
```nginx
ssl_protocols TLSv1.2 TLSv1.3;
ssl_ciphers 'ECDHE-ECDSA-AES128-GCM-SHA256:ECDHE-RSA-AES128-GCM-SHA256';
ssl_prefer_server_ciphers on;
ssl_session_cache shared:SSL:10m;
ssl_session_timeout 10m;
```

### Secrets Management

**Secret Storage**:
- GitHub Secrets for CI/CD
- Environment variables on server
- No secrets in code or configs

**Required Secrets**:
- `STAGING_SECRET_KEY`
- `STAGING_JWT_SECRET`
- `STAGING_DB_PASSWORD`
- `STAGING_SSH_KEY`
- `STAGING_HOST`
- `STAGING_USER`

### Access Control

**SSH Access**:
- Key-based authentication only
- No password authentication
- Limited user access

**Database Access**:
- Internal network only
- Strong passwords
- Limited privileges per user

**API Security**:
- JWT token authentication
- Rate limiting (100 req/min per IP)
- CORS restrictions
- Input validation

---

## 💾 Backup Strategy

### Database Backups

**Automated Backups**:
- **Frequency**: Daily at 2:00 AM UTC
- **Retention**: 30 days
- **Location**: `/backups/postgres/`
- **Format**: SQL dump (gzip compressed)

**Backup Script**:
```bash
#!/bin/bash
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="/backups/postgres/staging_db_$DATE.sql.gz"

docker-compose -f docker-compose.staging.yml exec -T postgres \
  pg_dump -U staging_user staging_db | gzip > $BACKUP_FILE

# Keep only last 30 days
find /backups/postgres/ -name "*.sql.gz" -mtime +30 -delete
```

### Application Backups

**Configuration Backups**:
- Weekly backup of all config files
- Version controlled in Git
- Stored in separate repository

**File Backups**:
- User uploads (if applicable)
- Static assets
- Logs (30 days retention)

---

## 🔄 Rollback Procedure

### Automatic Rollback Triggers

- Deployment health check failures
- API error rate > 10%
- Critical service unavailable

### Manual Rollback Steps

```bash
# 1. SSH to staging server
ssh user@staging.gw2wvwbuilder.example.com

# 2. Stop current services
docker-compose -f docker-compose.staging.yml down

# 3. Checkout previous stable version
git checkout <previous_stable_tag>

# 4. Restore database backup (if needed)
gunzip < /backups/postgres/staging_db_YYYYMMDD_HHMMSS.sql.gz | \
  docker-compose -f docker-compose.staging.yml exec -T postgres \
  psql -U staging_user staging_db

# 5. Redeploy
docker-compose -f docker-compose.staging.yml up -d

# 6. Verify
curl -fsS https://staging.gw2wvwbuilder.example.com/health
```

---

## 📈 Performance Tuning

### Resource Allocation

**Backend API**:
- CPU: 1 core
- Memory: 512MB
- Workers: 4 (Gunicorn)

**Frontend**:
- CPU: 0.5 core
- Memory: 256MB
- Nginx workers: auto

**PostgreSQL**:
- CPU: 1 core
- Memory: 1GB
- max_connections: 100
- shared_buffers: 256MB

**Redis**:
- CPU: 0.5 core
- Memory: 512MB
- maxmemory-policy: allkeys-lru

### Optimization Settings

**Database**:
- Connection pooling (20 connections)
- Query optimization
- Index tuning
- Vacuum scheduling

**Caching**:
- Redis for session storage
- API response caching (TTL: 5 minutes)
- Static asset caching

**Frontend**:
- Gzip compression
- Asset minification
- Lazy loading
- Code splitting

---

## ✅ Deployment Checklist

### Pre-Deployment

- [ ] All tests passing in CI/CD
- [ ] Code review approved
- [ ] Database migration scripts reviewed
- [ ] Environment variables configured
- [ ] Secrets verified
- [ ] Backup verified
- [ ] Rollback plan documented

### Deployment

- [ ] Deploy to staging
- [ ] Run database migrations
- [ ] Verify all services healthy
- [ ] Run smoke tests
- [ ] Check application logs
- [ ] Verify monitoring active

### Post-Deployment

- [ ] Monitor for 1 hour
- [ ] Verify no errors in logs
- [ ] Check performance metrics
- [ ] Test critical user flows
- [ ] Update deployment documentation
- [ ] Notify team of deployment

---

## 🎯 Success Criteria

**Deployment is considered successful when**:
- ✅ All services healthy
- ✅ API response time < 500ms (p95)
- ✅ Error rate < 1%
- ✅ All critical endpoints responding
- ✅ Database migrations applied successfully
- ✅ Frontend assets loaded correctly
- ✅ No critical errors in logs
- ✅ Monitoring dashboards showing green

---

## 📞 Support & Escalation

**Team Contacts**:
- DevOps Lead: devops@example.com
- Backend Lead: backend@example.com
- Frontend Lead: frontend@example.com

**Escalation Path**:
1. Check monitoring dashboards
2. Review application logs
3. Contact on-call engineer
4. Execute rollback if critical

---

## 📝 Maintenance Windows

**Scheduled Maintenance**:
- **Weekly**: Sunday 2:00-4:00 AM UTC
- **Monthly**: First Sunday of month 2:00-6:00 AM UTC

**Maintenance Activities**:
- Database maintenance & optimization
- Security updates
- Performance tuning
- Log cleanup
- Backup verification

---

## 🔮 Future Enhancements

### Short-term (Next Sprint)
- [ ] Add ELK stack for log aggregation
- [ ] Implement blue-green deployment
- [ ] Add load testing automation
- [ ] Configure automated security scanning

### Medium-term (Next Quarter)
- [ ] Kubernetes migration
- [ ] Multi-region deployment
- [ ] Advanced monitoring (APM)
- [ ] Automated performance testing

### Long-term (Next Year)
- [ ] Service mesh implementation
- [ ] Chaos engineering
- [ ] AI-powered anomaly detection
- [ ] Self-healing infrastructure

---

**Document Maintained By**: DevOps Team  
**Last Updated**: 2025-10-15 21:35 UTC+2  
**Next Review**: 2025-11-15
