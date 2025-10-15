# 🚀 Deployment Guide - GW2 WvW Builder

Complete guide for deploying the GW2 WvW Builder application to production.

---

## Table of Contents

- [Prerequisites](#prerequisites)
- [CI/CD Pipeline](#cicd-pipeline)
- [GitHub Secrets Configuration](#github-secrets-configuration)
- [Local Development Deployment](#local-development-deployment)
- [Staging Deployment](#staging-deployment)
- [Production Deployment](#production-deployment)
- [Docker Deployment](#docker-deployment)
- [Health Checks & Monitoring](#health-checks--monitoring)
- [Troubleshooting](#troubleshooting)

---

## Prerequisites

### Required Software

**Backend**:
- Python 3.11+
- Poetry 1.7+
- PostgreSQL 15+
- Redis 7+ (optional, for caching)

**Frontend**:
- Node.js 20+
- npm 10+

**DevOps**:
- Git
- Docker & Docker Compose (optional)
- Nginx (for production)

### Required Accounts

- GitHub account with repository access
- (Optional) Cloud provider account (AWS/GCP/Azure)
- (Optional) Domain name for production

---

## CI/CD Pipeline

### Overview

The project uses GitHub Actions with a modern, parallelized CI/CD pipeline (`ci-cd-modern.yml`).

### Pipeline Structure

```mermaid
graph TD
    A[Push to develop/main] --> B[Backend Jobs]
    A --> C[Frontend Jobs]
    
    B --> B1[Lint & Format]
    B --> B2[Unit Tests]
    B --> B3[Integration Tests]
    B --> B4[Optimizer Tests]
    B --> B5[Security Audit]
    
    C --> C1[Lint & Format]
    C --> C2[Unit Tests Vitest]
    C --> C3[E2E Tests Cypress]
    C --> C4[Production Build]
    C --> C5[Security Audit]
    
    B1 --> D[Validate All]
    B2 --> D
    B3 --> D
    B4 --> D
    B5 --> D
    C1 --> D
    C2 --> D
    C3 --> D
    C4 --> D
    C5 --> D
    
    D --> E[Deploy to Staging]
    E --> F[Deploy to Production]
```

### Jobs Breakdown

#### Backend Jobs (Parallel)

1. **Backend Lint** (~2min)
   - Ruff linter
   - Black formatter check
   - MyPy type checking

2. **Backend Unit Tests** (~5min)
   - Pure unit tests
   - No database required
   - Parallel execution with pytest-xdist
   - Coverage report uploaded to Codecov

3. **Backend Integration Tests** (~8min)
   - API endpoint tests
   - Database interactions
   - PostgreSQL service container
   - Coverage report uploaded to Codecov

4. **Backend Optimizer Tests** (~4min)
   - Optimizer engine tests
   - Mode effects tests
   - Builder endpoint tests
   - Dedicated coverage for optimizer module

5. **Backend Security** (~3min)
   - pip-audit for vulnerability scanning
   - Bandit for security issues detection

#### Frontend Jobs (Parallel)

1. **Frontend Lint** (~2min)
   - ESLint
   - Prettier format check
   - TypeScript type checking

2. **Frontend Unit Tests** (~3min)
   - Vitest tests
   - React component tests
   - Hooks tests
   - Coverage report

3. **Frontend E2E Tests** (~10min)
   - Cypress tests
   - Full backend + frontend stack
   - Screenshot/video on failure
   - Tests Builder V2 flow

4. **Frontend Build** (~3min)
   - Production build
   - Bundle size analysis
   - Artifact upload

5. **Frontend Security** (~2min)
   - npm audit
   - Trivy vulnerability scan

#### Total Pipeline Time

- **Parallel execution**: ~12-15 minutes (longest job = E2E tests)
- **Sequential execution would be**: ~40+ minutes

### Triggering the Pipeline

```bash
# Automatic trigger
git push origin develop    # Triggers full pipeline
git push origin main        # Triggers full pipeline + production deploy

# Manual trigger
# Go to GitHub Actions → ci-cd-modern → Run workflow
```

### Pipeline Artifacts

After each run, the following artifacts are generated:

- `frontend-dist`: Production build (~2-5 MB)
- `backend-security-reports`: Security audit results
- `cypress-screenshots`: Screenshots on E2E failure
- `cypress-videos`: E2E test recordings
- `validation-report`: Final validation summary

---

## GitHub Secrets Configuration

### Required Secrets

Go to **Settings → Secrets and variables → Actions** and add:

#### Backend Secrets

```bash
# Database
DATABASE_URL=postgresql://user:password@host:5432/db_name

# JWT Authentication
SECRET_KEY=your-super-secret-jwt-key-min-32-chars
REFRESH_SECRET_KEY=your-refresh-token-secret-key

# GW2 API
GW2_API_KEY=your-gw2-api-key-from-arena-net

# Redis (optional)
REDIS_URL=redis://localhost:6379/0
REDIS_PASSWORD=your-redis-password

# Email (optional)
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@example.com
SMTP_PASSWORD=your-app-password
```

#### Frontend Secrets

```bash
VITE_API_URL=https://api.yourdomain.com
VITE_ENABLE_ANALYTICS=false
```

#### Deployment Secrets

```bash
# Staging
STAGING_HOST=staging.yourdomain.com
STAGING_USER=deploy
STAGING_SSH_KEY=<private SSH key>

# Production
PROD_HOST=yourdomain.com
PROD_USER=deploy
PROD_SSH_KEY=<private SSH key>

# Notifications
SLACK_WEBHOOK=https://hooks.slack.com/services/YOUR/WEBHOOK/URL
```

#### Third-party Services

```bash
# Codecov (for coverage reports)
CODECOV_TOKEN=your-codecov-token

# Docker Registry (if using)
DOCKER_USERNAME=your-dockerhub-username
DOCKER_PASSWORD=your-dockerhub-password
```

### Generating Secrets

#### SECRET_KEY (JWT)

```bash
# Python
python -c "import secrets; print(secrets.token_urlsafe(32))"

# OpenSSL
openssl rand -base64 32
```

#### SSH Keys for Deployment

```bash
# Generate new SSH key pair
ssh-keygen -t ed25519 -C "github-actions-deploy" -f deploy_key

# Add public key to server
cat deploy_key.pub >> ~/.ssh/authorized_keys

# Add private key to GitHub Secrets as STAGING_SSH_KEY or PROD_SSH_KEY
cat deploy_key
```

---

## Local Development Deployment

### 1. Clone Repository

```bash
git clone https://github.com/Roddygithub/GW2_WvWbuilder.git
cd GW2_WvWbuilder
```

### 2. Backend Setup

```bash
cd backend

# Install Poetry
curl -sSL https://install.python-poetry.org | python3 -

# Install dependencies
poetry install

# Copy example env
cp .env.example .env

# Edit .env with your values
nano .env

# Run database migrations
poetry run alembic upgrade head

# Create initial data (optional)
poetry run python scripts/create_initial_data.py

# Start backend server
poetry run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Backend will be available at: `http://localhost:8000`

API docs at: `http://localhost:8000/docs`

### 3. Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Copy example env
cp .env.example .env

# Edit .env
nano .env

# Start development server
npm run dev
```

Frontend will be available at: `http://localhost:5173`

### 4. Run Tests Locally

```bash
# Backend tests
cd backend
poetry run pytest -v

# Backend with coverage
poetry run pytest --cov=app --cov-report=html

# Frontend tests
cd frontend
npm run test

# E2E tests
npm run e2e
```

---

## Staging Deployment

### Prerequisites

- Ubuntu 20.04+ server
- Domain or subdomain (e.g., staging.gw2builder.com)
- SSH access

### 1. Server Setup

```bash
# SSH into server
ssh user@staging.gw2builder.com

# Update system
sudo apt update && sudo apt upgrade -y

# Install required packages
sudo apt install -y python3.11 python3.11-venv postgresql nginx redis-server

# Install Poetry
curl -sSL https://install.python-poetry.org | python3 -

# Install Node.js 20
curl -fsSL https://deb.nodesource.com/setup_20.x | sudo -E bash -
sudo apt install -y nodejs

# Create application directory
sudo mkdir -p /opt/gw2_wvw_builder
sudo chown $USER:$USER /opt/gw2_wvw_builder
```

### 2. Clone and Configure

```bash
cd /opt/gw2_wvw_builder
git clone https://github.com/Roddygithub/GW2_WvWbuilder.git .

# Backend setup
cd backend
cp .env.example .env
nano .env  # Configure with staging credentials

poetry install --no-dev
poetry run alembic upgrade head

# Frontend setup
cd ../frontend
npm ci --production
npm run build
```

### 3. Systemd Services

Create backend service:

```bash
sudo nano /etc/systemd/system/gw2-backend.service
```

```ini
[Unit]
Description=GW2 WvW Builder Backend
After=network.target postgresql.service

[Service]
Type=simple
User=deploy
WorkingDirectory=/opt/gw2_wvw_builder/backend
ExecStart=/home/deploy/.local/bin/poetry run uvicorn app.main:app --host 0.0.0.0 --port 8000
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Start services:

```bash
sudo systemctl daemon-reload
sudo systemctl enable gw2-backend
sudo systemctl start gw2-backend
sudo systemctl status gw2-backend
```

### 4. Nginx Configuration

```bash
sudo nano /etc/nginx/sites-available/gw2builder-staging
```

```nginx
server {
    listen 80;
    server_name staging.gw2builder.com;

    # Frontend
    location / {
        root /opt/gw2_wvw_builder/frontend/dist;
        try_files $uri $uri/ /index.html;
    }

    # Backend API
    location /api {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

Enable and restart:

```bash
sudo ln -s /etc/nginx/sites-available/gw2builder-staging /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

### 5. SSL/TLS with Let's Encrypt

```bash
sudo apt install -y certbot python3-certbot-nginx
sudo certbot --nginx -d staging.gw2builder.com
```

---

## Production Deployment

Production deployment follows the same steps as staging with these differences:

### Key Differences

1. **Environment**: Use `production` environment in GitHub Actions
2. **Domain**: Use production domain (e.g., gw2builder.com)
3. **Database**: Use production PostgreSQL with backups
4. **Redis**: Enable Redis for caching
5. **Monitoring**: Add monitoring tools (Sentry, Prometheus, etc.)

### Production Checklist

- [ ] All secrets configured in GitHub
- [ ] Database backups automated
- [ ] SSL certificate installed
- [ ] Monitoring and alerts configured
- [ ] Error tracking (Sentry) setup
- [ ] CDN configured for static assets
- [ ] Rate limiting enabled
- [ ] Firewall rules configured
- [ ] Backup restoration tested
- [ ] Health checks passing

### Production Deployment Command

```bash
# From local machine
git checkout main
git pull origin main
git tag -a v1.0.0 -m "Production release v1.0.0"
git push origin v1.0.0

# GitHub Actions will automatically deploy to production
```

---

## Docker Deployment

### Using Docker Compose

```bash
# Copy docker-compose template
cp docker-compose.prod.yml docker-compose.yml

# Edit environment variables
nano .env

# Start services
docker-compose up -d

# Check logs
docker-compose logs -f

# Stop services
docker-compose down
```

### Individual Docker Builds

```bash
# Backend
cd backend
docker build -t gw2builder-backend:latest .
docker run -d -p 8000:8000 --env-file .env gw2builder-backend:latest

# Frontend
cd frontend
docker build -t gw2builder-frontend:latest .
docker run -d -p 80:80 gw2builder-frontend:latest
```

---

## Health Checks & Monitoring

### Backend Health Check

```bash
curl http://localhost:8000/api/v1/health

# Expected response:
{
  "status": "healthy",
  "database": "connected",
  "version": "1.0.0"
}
```

### Frontend Health Check

```bash
curl http://localhost:5173/

# Should return HTML with status 200
```

### Monitoring Endpoints

- `/api/v1/health` - Overall health status
- `/api/v1/metrics` - Prometheus metrics (if enabled)
- `/docs` - API documentation (disable in production)

---

## Troubleshooting

### Backend Issues

**Database connection failed**:
```bash
# Check PostgreSQL is running
sudo systemctl status postgresql

# Test connection
psql -U user -d db_name -h localhost

# Check logs
poetry run tail -f logs/app.log
```

**Migration errors**:
```bash
# Check current migration
poetry run alembic current

# Rollback one version
poetry run alembic downgrade -1

# Upgrade to head
poetry run alembic upgrade head
```

### Frontend Issues

**Build fails**:
```bash
# Clear cache
rm -rf node_modules dist
npm cache clean --force
npm install
npm run build
```

**API connection issues**:
```bash
# Check .env configuration
cat .env | grep VITE_API_URL

# Test API from browser console
fetch('http://localhost:8000/api/v1/health').then(r => r.json()).then(console.log)
```

### CI/CD Issues

**Tests failing**:
```bash
# Run tests locally first
cd backend && poetry run pytest -v
cd frontend && npm run test

# Check GitHub Actions logs for details
```

**Deployment failing**:
```bash
# Verify SSH keys
ssh -T user@server

# Check server disk space
df -h

# Check server logs
sudo journalctl -u gw2-backend -n 100
```

---

## Additional Resources

- [Backend README](backend/README.md)
- [Frontend README](frontend/README.md)
- [API Documentation](API.md)
- [Architecture Guide](BACKEND_GUIDE.md)
- [Optimizer Documentation](OPTIMIZER.md)
- [E2E Testing Guide](E2E_TESTING.md)

---

## Support

For deployment issues, please:

1. Check this documentation
2. Review GitHub Actions logs
3. Check server logs
4. Create an issue on GitHub

---

**Last Updated**: October 15, 2025
**Version**: 3.0.0
