#!/bin/bash
# Quick script to check if backend is running before E2E tests

echo "🔍 Checking if backend is running..."
echo ""

# Test if backend responds
if curl -s -f http://127.0.0.1:8000/docs > /dev/null 2>&1; then
    echo "✅ Backend is RUNNING on http://127.0.0.1:8000"
    echo ""
    
    # Test if test user exists by attempting login
    echo "🔑 Testing login with frontend@user.com..."
    RESPONSE=$(curl -s -X POST http://127.0.0.1:8000/api/v1/auth/login \
      -H "Content-Type: application/x-www-form-urlencoded" \
      -d "username=frontend@user.com&password=Frontend123!" 2>&1)
    
    if echo "$RESPONSE" | grep -q "access_token"; then
        echo "✅ Test user EXISTS and can login"
        echo "✅ Backend is READY for E2E tests!"
        echo ""
        echo "▶️  You can now run: npm run e2e:headless"
        exit 0
    else
        echo "⚠️  Test user NOT FOUND or login failed"
        echo ""
        echo "🔧 Run this to create test user:"
        echo "   cd backend && poetry run python scripts/seed_test_user.py"
        exit 1
    fi
else
    echo "❌ Backend is NOT running!"
    echo ""
    echo "🚀 Start backend with:"
    echo "   cd backend"
    echo "   poetry run uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload"
    echo ""
    echo "Then run this script again to verify."
    exit 1
fi
