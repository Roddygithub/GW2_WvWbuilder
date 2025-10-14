#!/bin/bash
# Test login endpoint

echo "Testing login with frontend user..."
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=frontend@user.com" \
  -d "password=Frontend123!" \
  -w "\nHTTP Status: %{http_code}\n"

echo -e "\n---\n"

echo "Testing login with admin user..."
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=admin@example.com" \
  -d "password=Admin123!" \
  -w "\nHTTP Status: %{http_code}\n"
