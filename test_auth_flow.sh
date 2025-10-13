#!/bin/bash
# Test complete auth flow

echo "=== 1. Login with frontend user ==="
RESPONSE=$(curl -s -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=frontend@user.com" \
  -d "password=Frontend123!")

echo "$RESPONSE"

# Extract access token
TOKEN=$(echo "$RESPONSE" | grep -o '"access_token":"[^"]*"' | cut -d'"' -f4)

if [ -z "$TOKEN" ]; then
  echo "ERROR: No token received!"
  exit 1
fi

echo -e "\n=== 2. Test /users/me with token ==="
curl -s http://localhost:8000/api/v1/users/me \
  -H "Authorization: Bearer $TOKEN" | python3 -m json.tool

echo -e "\n=== 3. Test /dashboard/stats ==="
curl -s http://localhost:8000/api/v1/dashboard/stats \
  -H "Authorization: Bearer $TOKEN" | python3 -m json.tool

echo -e "\n✅ Auth flow complete!"
