#!/usr/bin/env python3
"""
Seed Demo Data Script - GW2 WvW Builder
========================================

This script populates the database with demo data for testing and development.

Usage:
    cd /path/to/GW2_WvWbuilder
    poetry run python scripts/seed_demo_data.py

What it creates:
    - Users (frontenduser, adminuser, testuser)
    - Roles (Admin, User, Moderator)
    - Tags (WvW, PvE, PvP, etc.)
    - Builds (sample character builds)
    - Compositions (squad compositions)
    - Teams (guilds/teams)
    - Activities (recent user actions)

Author: GW2 WvW Builder Team
Date: 2025-10-13
"""

import asyncio
import sys
from pathlib import Path

# Add backend to path
backend_path = Path(__file__).parent.parent / "backend"
sys.path.insert(0, str(backend_path))

from datetime import datetime, timedelta
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import AsyncSessionLocal, engine
from app.models.base_model import Base
from app.models.user import User
from app.models.role import Role
from app.models.tag import Tag
from app.models.build import Build
from app.models.composition import Composition
from app.models.team import Team
from app.core.security import get_password_hash


async def create_tables():
    """Create all database tables."""
    print("📊 Creating database tables...")
    # Import all models to ensure they're registered
    import app.models  # noqa: F401
    
    # Create tables directly using SQLAlchemy
    from sqlalchemy import create_engine as sync_create_engine
    
    # Use absolute path for test.db
    db_path = Path(__file__).parent.parent / "test.db"
    sync_db_url = f"sqlite:///{db_path.absolute()}"
    
    sync_engine = sync_create_engine(sync_db_url, echo=False)
    Base.metadata.create_all(bind=sync_engine)
    sync_engine.dispose()
    
    print("✅ Database tables created")


async def seed_roles(db: AsyncSession) -> dict:
    """Seed roles."""
    print("\n🎭 Seeding roles...")
    
    roles_data = [
        {
            "name": "Admin",
            "description": "Administrator with full access",
            "permission_level": 100,
            "is_default": False,
        },
        {
            "name": "User",
            "description": "Standard user with basic access",
            "permission_level": 10,
            "is_default": True,
        },
        {
            "name": "Moderator",
            "description": "Moderator with elevated permissions",
            "permission_level": 50,
            "is_default": False,
        },
    ]
    
    roles = {}
    for role_data in roles_data:
        # Check if role exists
        stmt = select(Role).where(Role.name == role_data["name"])
        result = await db.execute(stmt)
        existing_role = result.scalars().first()
        
        if existing_role:
            print(f"  ⚠️  Role '{role_data['name']}' already exists")
            roles[role_data["name"]] = existing_role
        else:
            role = Role(**role_data)
            db.add(role)
            await db.flush()
            roles[role_data["name"]] = role
            print(f"  ✅ Created role: {role_data['name']}")
    
    await db.commit()
    return roles


async def seed_users(db: AsyncSession, roles: dict) -> dict:
    """Seed users with roles."""
    print("\n👥 Seeding users...")
    
    users_data = [
        {
            "username": "frontenduser",
            "email": "frontend@user.com",
            "password": "Frontend123!",
            "full_name": "Frontend User",
            "is_active": True,
            "is_superuser": False,
            "role": "User",
        },
        {
            "username": "adminuser",
            "email": "admin@example.com",
            "password": "Admin123!",
            "full_name": "Admin User",
            "is_active": True,
            "is_superuser": True,
            "role": "Admin",
        },
        {
            "username": "testuser",
            "email": "test@example.com",
            "password": "Test123!",
            "full_name": "Test User",
            "is_active": True,
            "is_superuser": False,
            "role": "User",
        },
        {
            "username": "moduser",
            "email": "mod@example.com",
            "password": "Mod123!",
            "full_name": "Moderator User",
            "is_active": True,
            "is_superuser": False,
            "role": "Moderator",
        },
    ]
    
    users = {}
    for user_data in users_data:
        # Check if user exists
        stmt = select(User).where(User.email == user_data["email"])
        result = await db.execute(stmt)
        existing_user = result.scalars().first()
        
        if existing_user:
            print(f"  ⚠️  User '{user_data['email']}' already exists")
            users[user_data["username"]] = existing_user
        else:
            role_name = user_data.pop("role")
            password = user_data.pop("password")
            
            user = User(
                username=user_data["username"],
                email=user_data["email"],
                hashed_password=get_password_hash(password),
                full_name=user_data["full_name"],
                is_active=user_data["is_active"],
                is_superuser=user_data["is_superuser"],
            )
            db.add(user)
            await db.flush()
            
            # Assign role
            if role_name in roles:
                from app.models.user_role import UserRole
                user_role = UserRole(user_id=user.id, role_id=roles[role_name].id)
                db.add(user_role)
            
            users[user_data["username"]] = user
            print(f"  ✅ Created user: {user_data['email']} (password: {password})")
    
    await db.commit()
    return users


async def seed_tags(db: AsyncSession) -> dict:
    """Seed tags."""
    print("\n🏷️  Seeding tags...")
    
    tags_data = [
        {"name": "WvW", "description": "World vs World content", "color": "#FF5733"},
        {"name": "PvE", "description": "Player vs Environment", "color": "#33FF57"},
        {"name": "PvP", "description": "Player vs Player", "color": "#3357FF"},
        {"name": "Zerg", "description": "Large scale combat", "color": "#FF33F5"},
        {"name": "Roaming", "description": "Small scale combat", "color": "#F5FF33"},
        {"name": "Support", "description": "Support builds", "color": "#33FFF5"},
        {"name": "DPS", "description": "Damage builds", "color": "#FF3333"},
        {"name": "Tank", "description": "Tanking builds", "color": "#3333FF"},
        {"name": "Meta", "description": "Meta builds", "color": "#FFD700"},
        {"name": "Beginner", "description": "Beginner friendly", "color": "#90EE90"},
    ]
    
    tags = {}
    for tag_data in tags_data:
        # Check if tag exists
        stmt = select(Tag).where(Tag.name == tag_data["name"])
        result = await db.execute(stmt)
        existing_tag = result.scalars().first()
        
        if existing_tag:
            print(f"  ⚠️  Tag '{tag_data['name']}' already exists")
            tags[tag_data["name"]] = existing_tag
        else:
            tag = Tag(**tag_data)
            db.add(tag)
            await db.flush()
            tags[tag_data["name"]] = tag
            print(f"  ✅ Created tag: {tag_data['name']}")
    
    await db.commit()
    return tags


async def seed_builds(db: AsyncSession, users: dict, tags: dict) -> dict:
    """Seed sample builds."""
    print("\n⚔️  Seeding builds...")
    
    builds_data = [
        {
            "name": "Zerg Guardian Support",
            "description": "Full support guardian for large scale battles",
            "game_mode": "wvw",
            "team_size": 50,
            "is_public": True,
            "created_by": "frontenduser",
            "config": {
                "profession": "Guardian",
                "specialization": "Firebrand",
                "weapons": ["Staff", "Mace/Shield"],
                "armor": "Minstrel",
                "skills": ["Mantra of Solace", "Mantra of Liberation"],
            },
            "tags": ["WvW", "Zerg", "Support", "Meta"],
        },
        {
            "name": "Roaming Thief Assassin",
            "description": "High mobility thief for roaming",
            "game_mode": "wvw",
            "team_size": 5,
            "is_public": True,
            "created_by": "testuser",
            "config": {
                "profession": "Thief",
                "specialization": "Deadeye",
                "weapons": ["Dagger/Pistol", "Shortbow"],
                "armor": "Marauder",
                "skills": ["Shadowstep", "Infiltrator's Signet"],
            },
            "tags": ["WvW", "Roaming", "DPS"],
        },
        {
            "name": "Frontline Warrior",
            "description": "Tanky warrior for frontline combat",
            "game_mode": "wvw",
            "team_size": 50,
            "is_public": True,
            "created_by": "adminuser",
            "config": {
                "profession": "Warrior",
                "specialization": "Spellbreaker",
                "weapons": ["Hammer", "Greatsword"],
                "armor": "Soldier",
                "skills": ["Balanced Stance", "Signet of Fury"],
            },
            "tags": ["WvW", "Zerg", "Tank", "Meta"],
        },
    ]
    
    builds = {}
    for build_data in builds_data:
        # Check if build exists
        stmt = select(Build).where(Build.name == build_data["name"])
        result = await db.execute(stmt)
        existing_build = result.scalars().first()
        
        if existing_build:
            print(f"  ⚠️  Build '{build_data['name']}' already exists")
            builds[build_data["name"]] = existing_build
        else:
            username = build_data.pop("created_by")
            tag_names = build_data.pop("tags")
            
            build = Build(
                name=build_data["name"],
                description=build_data["description"],
                game_mode=build_data["game_mode"],
                team_size=build_data["team_size"],
                is_public=build_data["is_public"],
                created_by_id=users[username].id,
                config=build_data["config"],
            )
            db.add(build)
            await db.flush()
            
            # Add tags
            for tag_name in tag_names:
                if tag_name in tags:
                    from app.models.association_tables import build_tags
                    stmt = build_tags.insert().values(build_id=build.id, tag_id=tags[tag_name].id)
                    await db.execute(stmt)
            
            builds[build_data["name"]] = build
            print(f"  ✅ Created build: {build_data['name']}")
    
    await db.commit()
    return builds


async def seed_compositions(db: AsyncSession, users: dict, builds: dict) -> dict:
    """Seed sample compositions."""
    print("\n📋 Seeding compositions...")
    
    compositions_data = [
        {
            "name": "Meta Zerg Composition",
            "description": "Standard 50-man zerg composition for organized play",
            "squad_size": 50,
            "is_public": True,
            "status": "active",
            "game_mode": "wvw",
            "created_by": "adminuser",
            "build": "Zerg Guardian Support",
        },
        {
            "name": "Roaming Squad",
            "description": "5-man roaming composition for havoc tactics",
            "squad_size": 5,
            "is_public": True,
            "status": "active",
            "game_mode": "wvw",
            "created_by": "testuser",
            "build": "Roaming Thief Assassin",
        },
        {
            "name": "Defense Team",
            "description": "Defensive composition for tower/keep defense",
            "squad_size": 20,
            "is_public": True,
            "status": "active",
            "game_mode": "wvw",
            "created_by": "frontenduser",
            "build": "Frontline Warrior",
        },
    ]
    
    compositions = {}
    for comp_data in compositions_data:
        # Check if composition exists
        stmt = select(Composition).where(Composition.name == comp_data["name"])
        result = await db.execute(stmt)
        existing_comp = result.scalars().first()
        
        if existing_comp:
            print(f"  ⚠️  Composition '{comp_data['name']}' already exists")
            compositions[comp_data["name"]] = existing_comp
        else:
            username = comp_data.pop("created_by")
            build_name = comp_data.pop("build")
            
            composition = Composition(
                name=comp_data["name"],
                description=comp_data["description"],
                squad_size=comp_data["squad_size"],
                is_public=comp_data["is_public"],
                status=comp_data["status"],
                game_mode=comp_data["game_mode"],
                created_by=users[username].id,
                build_id=builds[build_name].id if build_name in builds else None,
            )
            db.add(composition)
            await db.flush()
            
            compositions[comp_data["name"]] = composition
            print(f"  ✅ Created composition: {comp_data['name']}")
    
    await db.commit()
    return compositions


async def seed_teams(db: AsyncSession, users: dict) -> dict:
    """Seed sample teams."""
    print("\n🛡️  Seeding teams...")
    
    teams_data = [
        {
            "name": "Elite Zerg Squad",
            "description": "Competitive WvW guild focused on large scale battles",
            "status": "active",
            "is_public": True,
            "owner": "adminuser",
        },
        {
            "name": "Roaming Havoc",
            "description": "Small group specializing in havoc tactics",
            "status": "active",
            "is_public": True,
            "owner": "testuser",
        },
        {
            "name": "Casual WvW Group",
            "description": "Friendly guild for casual WvW players",
            "status": "active",
            "is_public": True,
            "owner": "frontenduser",
        },
    ]
    
    teams = {}
    for team_data in teams_data:
        # Check if team exists
        stmt = select(Team).where(Team.name == team_data["name"])
        result = await db.execute(stmt)
        existing_team = result.scalars().first()
        
        if existing_team:
            print(f"  ⚠️  Team '{team_data['name']}' already exists")
            teams[team_data["name"]] = existing_team
        else:
            owner_username = team_data.pop("owner")
            
            team = Team(
                name=team_data["name"],
                description=team_data["description"],
                status=team_data["status"],
                is_public=team_data["is_public"],
                owner_id=users[owner_username].id,
            )
            db.add(team)
            await db.flush()
            
            teams[team_data["name"]] = team
            print(f"  ✅ Created team: {team_data['name']}")
    
    await db.commit()
    return teams


async def create_recent_activities(db: AsyncSession, users: dict, compositions: dict, builds: dict, teams: dict):
    """Create recent activities for the dashboard."""
    print("\n📊 Creating recent activities...")
    
    # Update timestamps to simulate recent activity
    now = datetime.utcnow()
    
    # Update composition timestamps
    for i, (name, comp) in enumerate(compositions.items()):
        comp.created_at = now - timedelta(hours=i * 2)
        comp.updated_at = now - timedelta(hours=i)
        await db.flush()
    
    # Update build timestamps
    for i, (name, build) in enumerate(builds.items()):
        build.created_at = now - timedelta(hours=i * 3)
        build.updated_at = now - timedelta(hours=i * 2)
        await db.flush()
    
    # Update team timestamps
    for i, (name, team) in enumerate(teams.items()):
        team.created_at = now - timedelta(hours=i * 4)
        team.updated_at = now - timedelta(hours=i * 3)
        await db.flush()
    
    await db.commit()
    print("  ✅ Recent activities timestamps updated")


async def main():
    """Main seed function."""
    print("=" * 60)
    print("🌱 GW2 WvW Builder - Seed Demo Data")
    print("=" * 60)
    
    try:
        # Create tables
        await create_tables()
        
        # Create database session
        async with AsyncSessionLocal() as db:
            # Seed data
            roles = await seed_roles(db)
            users = await seed_users(db, roles)
            tags = await seed_tags(db)
            builds = await seed_builds(db, users, tags)
            compositions = await seed_compositions(db, users, builds)
            teams = await seed_teams(db, users)
            await create_recent_activities(db, users, compositions, builds, teams)
        
        print("\n" + "=" * 60)
        print("✅ SEED COMPLETED SUCCESSFULLY!")
        print("=" * 60)
        print("\n📝 Test Credentials:")
        print("   Frontend User: frontend@user.com / Frontend123!")
        print("   Admin User:    admin@example.com / Admin123!")
        print("   Test User:     test@example.com / Test123!")
        print("   Mod User:      mod@example.com / Mod123!")
        print("\n🚀 You can now start the backend and login!")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
