# 🚀 Start E2E Tests - Step by Step Guide

## ⚠️ Critical: Backend Must Be Running First!

The Cypress tests failed because **the backend API is not running**. Follow these steps **in order**:

---

## Step 1: Start the Backend (Terminal 1)

```bash
cd /home/roddy/GW2_WvWbuilder/backend

# Install dependencies if needed
poetry install

# Start the backend server
poetry run uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```

**Expected output:**
```
INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
INFO:     Started reloader process [xxxxx] using StatReload
INFO:     Started server process [xxxxx]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
```

**✅ Verification:**
Open another terminal and test:
```bash
curl http://127.0.0.1:8000/api/v1/health
# or
curl http://127.0.0.1:8000/docs
```

**⏸️ WAIT - Do NOT proceed until backend is running!**

---

## Step 2: Seed the Test User (Terminal 2)

Once backend is running, seed the test user:

```bash
cd /home/roddy/GW2_WvWbuilder/backend
poetry run python scripts/seed_test_user.py
```

**Expected output:**
```
============================================================
Seed Test User Script
============================================================
✓ Successfully seeded user: frontend@user.com
  Username: frontend
  Password: Frontend123!
  Role: user
  ID: 1
============================================================
Done!
```

**If user already exists:**
```
✓ User already exists: frontend@user.com
```
This is fine! The script is idempotent.

**✅ Verification:**
Test login via API:
```bash
curl -X POST http://127.0.0.1:8000/api/v1/auth/login \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=frontend@user.com&password=Frontend123!"
```

Should return:
```json
{
  "access_token": "eyJ...",
  "token_type": "bearer",
  "refresh_token": "eyJ..."
}
```

---

## Step 3: Run Cypress Tests (Terminal 2 or 3)

Now you can run the E2E tests:

```bash
cd /home/roddy/GW2_WvWbuilder/frontend

# Headless mode (faster, for CI/CD)
npm run e2e:headless

# OR Interactive mode (for debugging)
npm run e2e
```

---

## 📊 Expected Test Results

With backend running and user seeded, you should see:

### ✅ Passing Tests
- ✓ should display registration page
- ✓ should show error with invalid credentials
- ✓ should have "Remember me" option
- ✓ should have "Forgot password" link
- ✓ should toggle password visibility
- ✓ should navigate from login to register
- ✓ should navigate from register to login
- ✓ should redirect to dashboard if already logged in
- ✓ should have proper form labels
- ✓ should have proper ARIA attributes
- ✓ should display dashboard with stats
- ✓ should display activity chart
- ✓ should display quick actions
- ✓ should have working sidebar navigation
- ✓ should redirect to login when not authenticated
- ✓ should store JWT token
- ✓ should include JWT in API requests
- ✓ Responsive design tests
- ✓ should show loading states
- ✓ should load dashboard quickly

### ⚠️ May Still Fail (Need Backend Implementation)
Some tests might still fail if backend endpoints aren't fully implemented:
- Registration validation errors
- Duplicate email detection
- Login with valid credentials (if API endpoint differs)
- Activity feed data

---

## 🐛 Troubleshooting

### Problem: "Connection refused" or "ECONNREFUSED"
**Solution:** Backend is not running. Go to Step 1.

### Problem: "should login with valid credentials" fails
**Causes:**
1. Backend not running → Check Step 1
2. Test user not seeded → Check Step 2
3. API endpoint path wrong → Check cypress.config.ts

**Debug:**
```bash
# Check backend is responding
curl http://127.0.0.1:8000/api/v1/auth/login

# Check test user exists
cd backend
poetry run python -c "
from app.core.database import AsyncSessionLocal
from app.models.user import User
from sqlalchemy import select
import asyncio

async def check():
    async with AsyncSessionLocal() as session:
        result = await session.execute(select(User).where(User.email == 'frontend@user.com'))
        user = result.scalars().first()
        if user:
            print(f'✓ User found: {user.username} ({user.email})')
        else:
            print('✗ User NOT found!')
asyncio.run(check())
"
```

### Problem: Port 5173 in use
**Solution:** Frontend dev server auto-switches to 5174. This is normal.

### Problem: "should validate email format" fails
**Cause:** Register page needs client-side validation.
**Status:** Non-critical for login/dashboard tests.

---

## 🔑 Test User Credentials

**For ALL E2E tests:**
- Email: `frontend@user.com`
- Username: `frontend`
- Password: `Frontend123!`

---

## 📁 Quick Commands Reference

```bash
# Terminal 1: Backend
cd /home/roddy/GW2_WvWbuilder/backend
poetry run uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload

# Terminal 2: Seed User (run once)
cd /home/roddy/GW2_WvWbuilder/backend
poetry run python scripts/seed_test_user.py

# Terminal 3: Frontend Tests
cd /home/roddy/GW2_WvWbuilder/frontend
npm run e2e:headless
```

---

## 🎯 Current Status

Based on your test output:
- ✅ Frontend is working
- ✅ Loading indicator is visible
- ✅ Error normalization is working
- ❌ **Backend is NOT running** (all login tests fail)
- ❌ **Test user not seeded** (can't authenticate)

**Next Action:** Start backend (Step 1), then seed user (Step 2), then rerun tests (Step 3).

---

## 📈 Expected Improvement

**Before (Current):**
- 26 passing / 17 failing (60% pass rate)

**After (With backend + seed):**
- 35+ passing / <10 failing (80%+ pass rate)

Remaining failures will be validation/UI polish, not critical flow issues.
