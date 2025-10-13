#!/usr/bin/env python3
"""Test roles are now loaded"""
import requests
import json

# Login
print("=== LOGIN ===")
response = requests.post(
    "http://localhost:8000/api/v1/auth/login",
    data={
        "username": "frontend@user.com",
        "password": "Frontend123!"
    }
)
print(f"Status: {response.status_code}")

if response.status_code == 200:
    token_data = response.json()
    token = token_data["access_token"]
    
    # Get user info
    print("\n=== GET /users/me ===")
    response = requests.get(
        "http://localhost:8000/api/v1/users/me",
        headers={"Authorization": f"Bearer {token}"}
    )
    
    user_data = response.json()
    print(json.dumps(user_data, indent=2))
    
    # Check roles
    print(f"\n=== ROLES CHECK ===")
    if user_data.get("roles"):
        print(f"✅ SUCCESS! User has {len(user_data['roles'])} role(s):")
        for role in user_data["roles"]:
            print(f"  - {role['name']}")
    else:
        print("❌ FAILED: No roles loaded")
else:
    print(f"Login failed: {response.text}")
