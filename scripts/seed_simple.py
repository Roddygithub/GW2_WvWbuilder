#!/usr/bin/env python3
"""
Simple Seed Script - Direct SQL approach
Populates database with demo data using raw SQL to avoid ORM issues
"""

import sqlite3
from pathlib import Path
from datetime import datetime
from app.core.security import get_password_hash

# Backend path
import sys
backend_path = Path(__file__).parent.parent / "backend"
sys.path.insert(0, str(backend_path))

# DB path
db_path = Path(__file__).parent.parent / "test.db"

def main():
    print("=" * 60)
    print("🌱 GW2 WvW Builder - Simple Seed (SQL Direct)")
    print("=" * 60)
    
    conn = sqlite3.connect(str(db_path))
    cursor = conn.cursor()
    
    try:
        # 1. Insert Roles
        print("\n🎭 Seeding roles...")
        roles_data = [
            (1, "Admin", "Administrator with full access", 100, 0),
            (2, "User", "Standard user", 10, 1),
            (3, "Moderator", "Moderator", 50, 0),
        ]
        
        cursor.executemany(
            "INSERT OR IGNORE INTO roles (id, name, description, permission_level, is_default) VALUES (?, ?, ?, ?, ?)",
            roles_data
        )
        print(f"  ✅ Created {cursor.rowcount} roles")
        
        # 2. Insert Users
        print("\n👥 Seeding users...")
        users_data = [
            (9, "frontenduser", "frontend@user.com", get_password_hash("Frontend123!"), "Frontend User", 1, 0),
            (10, "adminuser", "admin@example.com", get_password_hash("Admin123!"), "Admin User", 1, 1),
            (11, "testuser", "test@example.com", get_password_hash("Test123!"), "Test User", 1, 0),
        ]
        
        cursor.executemany(
            "INSERT OR IGNORE INTO users (id, username, email, hashed_password, full_name, is_active, is_superuser) VALUES (?, ?, ?, ?, ?, ?, ?)",
            users_data
        )
        print(f"  ✅ Created {cursor.rowcount} users")
        
        # 3. Link Users to Roles
        print("\n🔗 Linking users to roles...")
        user_roles_data = [
            (9, 2),  # frontenduser -> User
            (10, 1),  # adminuser -> Admin
            (11, 2),  # testuser -> User
        ]
        
        cursor.executemany(
            "INSERT OR IGNORE INTO user_roles (user_id, role_id) VALUES (?, ?)",
            user_roles_data
        )
        print(f"  ✅ Created {cursor.rowcount} user-role associations")
        
        conn.commit()
        
        print("\n" + "=" * 60)
        print("✅ SEED COMPLETED!")
        print("=" * 60)
        print("\n📝 Test Credentials:")
        print("   Frontend: frontend@user.com / Frontend123!")
        print("   Admin:    admin@example.com / Admin123!")
        print("   Test:     test@example.com / Test123!")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        conn.rollback()
        import traceback
        traceback.print_exc()
        return 1
    finally:
        conn.close()
    
    return 0

if __name__ == "__main__":
    exit(main())
