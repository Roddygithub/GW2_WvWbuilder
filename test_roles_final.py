#!/usr/bin/env python3
"""Test final pour vérifier le chargement des rôles"""
import requests
import json

BASE_URL = "http://localhost:8000/api/v1"

def test_roles_loading():
    print("=" * 60)
    print("🧪 TEST: Chargement des rôles ORM")
    print("=" * 60)
    
    # 1. Login
    print("\n1️⃣ Login...")
    response = requests.post(
        f"{BASE_URL}/auth/login",
        data={
            "username": "frontend@user.com",
            "password": "Frontend123!"
        }
    )
    
    if response.status_code != 200:
        print(f"❌ Login failed: {response.status_code}")
        print(response.text)
        return False
    
    token = response.json()["access_token"]
    print("✅ Login successful")
    
    # 2. Get user info
    print("\n2️⃣ GET /users/me...")
    response = requests.get(
        f"{BASE_URL}/users/me",
        headers={"Authorization": f"Bearer {token}"}
    )
    
    if response.status_code != 200:
        print(f"❌ Request failed: {response.status_code}")
        print(response.text)
        return False
    
    user_data = response.json()
    print("✅ Request successful")
    
    # 3. Display result
    print("\n3️⃣ User data:")
    print(json.dumps(user_data, indent=2))
    
    # 4. Check roles
    print("\n4️⃣ Roles check:")
    roles = user_data.get("roles", [])
    
    if not roles:
        print("❌ FAILED: No roles loaded")
        print(f"   User: {user_data.get('username')}")
        print(f"   Email: {user_data.get('email')}")
        return False
    
    print(f"✅ SUCCESS! User has {len(roles)} role(s):")
    for role in roles:
        print(f"   - {role.get('name')} (ID: {role.get('id')})")
    
    return True

if __name__ == "__main__":
    success = test_roles_loading()
    print("\n" + "=" * 60)
    if success:
        print("✅ TEST PASSED: Roles ORM fixed!")
    else:
        print("❌ TEST FAILED: Roles not loading")
    print("=" * 60)
    exit(0 if success else 1)
