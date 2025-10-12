# 🚀 GW2_WvWbuilder - Quick Start Guide

**Get the backend running in 5 minutes!**

---

## Prerequisites

- Python 3.11+
- Poetry 2.2.1+
- PostgreSQL 15+ (or use SQLite for development)
- Docker (optional, for containerized deployment)

---

## Option 1: Local Development (Fastest)

### Step 1: Install Dependencies

```bash
cd backend
poetry install
```

### Step 2: Configure Environment

```bash
# Copy example environment file
cp .env.example .env

# Edit .env with your settings (or use defaults for development)
# Minimum required:
# - SECRET_KEY (generate with: openssl rand -hex 32)
# - DATABASE_URL (default: sqlite:///./test.db)
```

### Step 3: Initialize Database

```bash
# Run migrations
poetry run alembic upgrade head

# (Optional) Seed test data
poetry run python -c "from app.db.init_db import init_db; init_db()"
```

### Step 4: Start Server

```bash
poetry run uvicorn app.main:app --reload
```

**✅ Done!** API is running at:
- **API**: http://localhost:8000
- **Docs**: http://localhost:8000/docs
- **Health**: http://localhost:8000/api/v1/health

---

## Option 2: Docker (Production-Like)

### Step 1: Configure Environment

```bash
# Copy example environment file
cp backend/.env.example backend/.env.production

# Edit backend/.env.production with production settings
# IMPORTANT: Set strong SECRET_KEY and database credentials
```

### Step 2: Start Services

```bash
# From project root
docker-compose up -d
```

### Step 3: Run Migrations

```bash
docker-compose exec backend poetry run alembic upgrade head
```

**✅ Done!** Services are running:
- **API**: http://localhost:8000
- **Docs**: http://localhost:8000/docs
- **pgAdmin**: http://localhost:5050 (admin@example.com / admin)
- **PostgreSQL**: localhost:5432

---

## Option 3: One-Command Start (Development)

```bash
cd backend && \
cp .env.example .env && \
poetry install && \
poetry run alembic upgrade head && \
poetry run uvicorn app.main:app --reload
```

---

## Quick Test

### Test API Health

```bash
curl http://localhost:8000/api/v1/health
```

**Expected response:**
```json
{
  "status": "healthy",
  "version": "1.0.0",
  "environment": "development"
}
```

### Register a User

```bash
curl -X POST http://localhost:8000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "email": "test@example.com",
    "password": "SecurePassword123!"
  }'
```

### Login

```bash
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=testuser&password=SecurePassword123!"
```

**Expected response:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

### Access Protected Endpoint

```bash
# Save token from login response
TOKEN="your-token-here"

curl http://localhost:8000/api/v1/tags/ \
  -H "Authorization: Bearer $TOKEN"
```

---

## Run Tests

```bash
cd backend

# Run all tests
poetry run pytest

# Run API tests only
poetry run pytest tests/api/

# Run with coverage
poetry run pytest --cov=app --cov-report=term-missing

# Run specific test
poetry run pytest tests/api/test_tags.py::TestTagsAPI::test_create_tag -v
```

---

## Common Issues & Solutions

### Issue: "ModuleNotFoundError: No module named 'app'"

**Solution:**
```bash
cd backend
poetry install
```

### Issue: "Database connection failed"

**Solution:**
```bash
# Check DATABASE_URL in .env
# For SQLite (development):
DATABASE_URL=sqlite:///./test.db

# For PostgreSQL (production):
DATABASE_URL=postgresql://user:pass@localhost:5432/gw2_wvwbuilder
```

### Issue: "Alembic migration failed"

**Solution:**
```bash
# Reset database (WARNING: deletes all data)
rm test.db  # For SQLite
poetry run alembic downgrade base
poetry run alembic upgrade head
```

### Issue: "Port 8000 already in use"

**Solution:**
```bash
# Find process using port 8000
lsof -i :8000

# Kill process
kill -9 <PID>

# Or use different port
poetry run uvicorn app.main:app --port 8001
```

### Issue: "Poetry not found"

**Solution:**
```bash
# Install Poetry
curl -sSL https://install.python-poetry.org | python3 -

# Or with pip
pip install poetry==2.2.1
```

---

## Environment Variables Quick Reference

### Minimal Configuration (Development)

```bash
# .env
ENVIRONMENT=development
DEBUG=True
SECRET_KEY=dev-secret-key-change-in-production
DATABASE_URL=sqlite:///./test.db
```

### Production Configuration

```bash
# .env.production
ENVIRONMENT=production
DEBUG=False
SECRET_KEY=<strong-random-key>
JWT_SECRET_KEY=<strong-random-key>
DATABASE_URL=postgresql://user:pass@host:5432/dbname
ASYNC_SQLALCHEMY_DATABASE_URI=postgresql+asyncpg://user:pass@host:5432/dbname
BACKEND_CORS_ORIGINS=["https://yourdomain.com"]
```

---

## Next Steps

1. **Read API Documentation**: http://localhost:8000/docs
2. **Review Frontend Integration Guide**: `backend/API_READY.md`
3. **Check Test Status**: `backend/tests/TEST_PROGRESS.md`
4. **Read Full Documentation**: `backend/README.md`

---

## Production Deployment

See `backend/FINAL_DELIVERY_REPORT.md` for:
- Complete deployment instructions
- Security checklist
- Performance tuning
- Monitoring setup
- Known issues and limitations

---

## Getting Help

- **Documentation**: `backend/docs/`
- **API Guide**: `backend/API_READY.md`
- **Test Guide**: `backend/tests/TEST_PROGRESS.md`
- **Issues**: GitHub Issues
- **Repository**: https://github.com/Roddygithub/GW2_WvWbuilder

---

**Happy Coding! 🎮⚔️**
