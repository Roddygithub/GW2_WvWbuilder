"""Test fixtures and data generators."""
import random
import string
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Type, TypeVar, Union

from faker import Faker
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import get_password_hash
from app.models import (
    User, Role, Profession, EliteSpecialization, Build, Composition, CompositionTag
)
from app.schemas.user import UserCreate, UserUpdate
from app.schemas.role import RoleCreate, RoleUpdate
from app.schemas.profession import ProfessionCreate, ProfessionUpdate
from app.schemas.build import BuildCreate, BuildUpdate, GameMode
from app.schemas.composition import CompositionCreate, CompositionUpdate

# Type variable for SQLAlchemy models
T = TypeVar('T')

# Initialize Faker
fake = Faker()


def random_string(length: int = 10) -> str:
    """Generate a random string of fixed length."""
    letters = string.ascii_letters + string.digits
    return ''.join(random.choice(letters) for _ in range(length))


def random_email() -> str:
    """Generate a random email address."""
    return f"{random_string(8).lower()}@example.com"


def random_username() -> str:
    """Generate a random username."""
    return f"user_{random_string(8).lower()}"


def random_password() -> str:
    """Generate a random password."""
    return f"P@ssw0rd{random_string(8)}"


def random_bool() -> bool:
    """Generate a random boolean value."""
    return random.choice([True, False])


def random_choice(choices: list) -> Any:
    """Randomly select an item from a list."""
    return random.choice(choices)


class ModelFactory:
    """Base factory for creating test data."""
    
    model: Type[T]
    
    @classmethod
    def _create_instance(cls, **kwargs: Any) -> T:
        """Create a model instance."""
        return cls.model(**kwargs)
    
    @classmethod
    def create(cls, **kwargs: Any) -> T:
        """Create a model instance with test data."""
        data = cls.get_test_data()
        data.update(kwargs)
        return cls._create_instance(**data)
    
    @classmethod
    def get_test_data(cls) -> Dict[str, Any]:
        """Get test data for the model."""
        raise NotImplementedError


class UserFactory(ModelFactory):
    """Factory for creating User test data."""
    
    model = User
    
    @classmethod
    def get_test_data(cls) -> Dict[str, Any]:
        """Get test data for a User."""
        return {
            "username": random_username(),
            "email": random_email(),
            "hashed_password": get_password_hash(random_password()),
            "is_active": True,
            "is_superuser": False,
        }
    
    @classmethod
    def create_user_create(cls, **kwargs: Any) -> UserCreate:
        """Create a UserCreate instance."""
        data = {
            "username": random_username(),
            "email": random_email(),
            "password": random_password(),
            "is_active": True,
            "is_superuser": False,
        }
        data.update(kwargs)
        return UserCreate(**data)
    
    @classmethod
    def create_user_update(cls, **kwargs: Any) -> UserUpdate:
        """Create a UserUpdate instance."""
        data = {
            "email": random_email(),
            "password": random_password(),
            "is_active": random_bool(),
            "is_superuser": random_bool(),
        }
        data.update(kwargs)
        return UserUpdate(**data)


class RoleFactory(ModelFactory):
    """Factory for creating Role test data."""
    
    model = Role
    
    @classmethod
    def get_test_data(cls) -> Dict[str, Any]:
        """Get test data for a Role."""
        return {
            "name": f"role_{random_string(8).lower()}",
            "description": fake.sentence(),
            "permission_level": random.randint(1, 10),
            "is_default": random_bool(),
        }
    
    @classmethod
    def create_role_create(cls, **kwargs: Any) -> RoleCreate:
        """Create a RoleCreate instance."""
        data = {
            "name": f"role_{random_string(8).lower()}",
            "description": fake.sentence(),
            "permission_level": random.randint(1, 10),
            "is_default": random_bool(),
        }
        data.update(kwargs)
        return RoleCreate(**data)
    
    @classmethod
    def create_role_update(cls, **kwargs: Any) -> RoleUpdate:
        """Create a RoleUpdate instance."""
        data = {
            "description": fake.sentence(),
            "permission_level": random.randint(1, 10),
            "is_default": random_bool(),
        }
        data.update(kwargs)
        return RoleUpdate(**data)


class ProfessionFactory(ModelFactory):
    """Factory for creating Profession test data."""
    
    model = Profession
    
    @classmethod
    def get_test_data(cls) -> Dict[str, Any]:
        """Get test data for a Profession."""
        return {
            "name": f"profession_{random_string(8).lower()}",
            "description": fake.paragraph(),
            "icon": f"icon_{random_string(8)}.png",
        }
    
    @classmethod
    def create_profession_create(cls, **kwargs: Any) -> ProfessionCreate:
        """Create a ProfessionCreate instance."""
        data = {
            "name": f"profession_{random_string(8).lower()}",
            "description": fake.paragraph(),
            "icon": f"icon_{random_string(8)}.png",
        }
        data.update(kwargs)
        return ProfessionCreate(**data)
    
    @classmethod
    def create_profession_update(cls, **kwargs: Any) -> ProfessionUpdate:
        """Create a ProfessionUpdate instance."""
        data = {
            "description": fake.paragraph(),
            "icon": f"icon_{random_string(8)}.png",
        }
        data.update(kwargs)
        return ProfessionUpdate(**data)


class BuildFactory(ModelFactory):
    """Factory for creating Build test data."""
    
    model = Build
    
    @classmethod
    def get_test_data(cls) -> Dict[str, Any]:
        """Get test data for a Build."""
        return {
            "name": f"build_{random_string(8)}",
            "description": fake.paragraph(),
            "game_mode": random_choice(list(GameMode)),
            "is_public": random_bool(),
            "weapon_set_1": {"main_hand": "Sword", "off_hand": "Focus"},
            "weapon_set_2": {"two_handed": "Greatsword"},
            "skills": {"heal": "Signet of Resolve", "elite": "Renewed Focus"},
            "traits": [
                ["Radiance", "Zeal", "Virtues"],
                ["Radiance", "Zeal", "Virtues"],
                ["Radiance", "Zeal", "Virtues"]
            ],
            "specializations": ["Radiance", "Zeal", "Virtues"],
            "attributes": {"Power": 2500, "Precision": 2000, "Ferocity": 1500},
            "infusions": ["+5 Agony Infusion"],
            "food": "Bowl of Sweet and Spicy Butternut Squash Soup",
            "utility": "Superior Sharpening Stone",
            "rune": "Scholar Rune",
            "sigils": ["Force", "Impact"],
        }
    
    @classmethod
    def create_build_create(
        cls,
        profession_id: int,
        user_id: int,
        **kwargs: Any
    ) -> BuildCreate:
        """Create a BuildCreate instance."""
        data = {
            "name": f"build_{random_string(8)}",
            "description": fake.paragraph(),
            "game_mode": random_choice(list(GameMode)).value,
            "is_public": random_bool(),
            "profession_id": profession_id,
            "user_id": user_id,
            "weapon_set_1": {"main_hand": "Sword", "off_hand": "Focus"},
            "weapon_set_2": {"two_handed": "Greatsword"},
            "skills": {"heal": "Signet of Resolve", "elite": "Renewed Focus"},
            "traits": [
                ["Radiance", "Zeal", "Virtues"],
                ["Radiance", "Zeal", "Virtues"],
                ["Radiance", "Zeal", "Virtues"]
            ],
            "specializations": ["Radiance", "Zeal", "Virtues"],
            "attributes": {"Power": 2500, "Precision": 2000, "Ferocity": 1500},
        }
        data.update(kwargs)
        return BuildCreate(**data)
    
    @classmethod
    def create_build_update(cls, **kwargs: Any) -> BuildUpdate:
        """Create a BuildUpdate instance."""
        data = {
            "name": f"updated_build_{random_string(8)}",
            "description": fake.paragraph(),
            "game_mode": random_choice(list(GameMode)).value,
            "is_public": not random_bool(),
            "weapon_set_1": {"main_hand": "Axe", "off_hand": "Torch"},
            "weapon_set_2": {"two_handed": "Greatsword"},
            "skills": {"heal": "Mantra of Solace", "elite": "Mantra of Liberation"},
        }
        data.update(kwargs)
        return BuildUpdate(**data)


class CompositionFactory(ModelFactory):
    """Factory for creating Composition test data."""
    
    model = Composition
    
    @classmethod
    def get_test_data(cls) -> Dict[str, Any]:
        """Get test data for a Composition."""
        return {
            "name": f"comp_{random_string(8)}",
            "description": fake.paragraph(),
            "squad_size": random.choice([5, 10, 15, 20, 25, 30, 35, 40, 45, 50]),
            "is_public": random_bool(),
            "game_mode": random_choice(["pve", "wvw", "pvp"]),
            "builds": [],
            "tags": [],
        }
    
    @classmethod
    def create_composition_create(
        cls,
        user_id: int,
        **kwargs: Any
    ) -> CompositionCreate:
        """Create a CompositionCreate instance."""
        data = {
            "name": f"comp_{random_string(8)}",
            "description": fake.paragraph(),
            "squad_size": random.choice([5, 10, 15, 20, 25, 30, 35, 40, 45, 50]),
            "is_public": random_bool(),
            "game_mode": random_choice(["pve", "wvw", "pvp"]),
            "builds": [],
            "tags": [],
            "user_id": user_id,
        }
        data.update(kwargs)
        return CompositionCreate(**data)
    
    @classmethod
    def create_composition_update(cls, **kwargs: Any) -> CompositionUpdate:
        """Create a CompositionUpdate instance."""
        data = {
            "name": f"updated_comp_{random_string(8)}",
            "description": fake.paragraph(),
            "squad_size": random.choice([5, 10, 15, 20, 25, 30, 35, 40, 45, 50]),
            "is_public": not random_bool(),
            "game_mode": random_choice(["pve", "wvw", "pvp"]),
        }
        data.update(kwargs)
        return CompositionUpdate(**data)


class TestDataGenerator:
    """Helper class for generating test data."""
    
    def __init__(self, session: AsyncSession):
        """Initialize the test data generator."""
        self.session = session
        self._users: List[User] = []
        self._roles: List[Role] = []
        self._professions: List[Profession] = []
        self._builds: List[Build] = []
        self._compositions: List[Composition] = []
    
    async def create_user(self, **kwargs: Any) -> User:
        """Create a test user."""
        user = UserFactory.create(**kwargs)
        self.session.add(user)
        await self.session.commit()
        await self.session.refresh(user)
        self._users.append(user)
        return user
    
    async def create_role(self, **kwargs: Any) -> Role:
        """Create a test role."""
        role = RoleFactory.create(**kwargs)
        self.session.add(role)
        await self.session.commit()
        await self.session.refresh(role)
        self._roles.append(role)
        return role
    
    async def create_profession(self, **kwargs: Any) -> Profession:
        """Create a test profession."""
        profession = ProfessionFactory.create(**kwargs)
        self.session.add(profession)
        await self.session.commit()
        await self.session.refresh(profession)
        self._professions.append(profession)
        return profession
    
    async def create_build(
        self,
        user_id: int,
        profession_id: int,
        **kwargs: Any
    ) -> Build:
        """Create a test build."""
        build = BuildFactory.create(
            user_id=user_id,
            profession_id=profession_id,
            **kwargs
        )
        self.session.add(build)
        await self.session.commit()
        await self.session.refresh(build)
        self._builds.append(build)
        return build
    
    async def create_composition(
        self,
        user_id: int,
        **kwargs: Any
    ) -> Composition:
        """Create a test composition."""
        composition = CompositionFactory.create(
            user_id=user_id,
            **kwargs
        )
        self.session.add(composition)
        await self.session.commit()
        await self.session.refresh(composition)
        self._compositions.append(composition)
        return composition
    
    async def create_standard_test_data(self) -> Dict[str, Any]:
        """Create a standard set of test data."""
        # Create roles
        admin_role = await self.create_role(
            name="admin",
            description="Administrator",
            permission_level=10,
            is_default=False
        )
        
        user_role = await self.create_role(
            name="user",
            description="Regular User",
            permission_level=1,
            is_default=True
        )
        
        # Create users
        admin_user = await self.create_user(
            username="admin",
            email="admin@example.com",
            hashed_password=get_password_hash("admin123"),
            is_active=True,
            is_superuser=True,
            roles=[admin_role]
        )
        
        test_user = await self.create_user(
            username="testuser",
            email="test@example.com",
            hashed_password=get_password_hash("test123"),
            is_active=True,
            is_superuser=False,
            roles=[user_role]
        )
        
        # Create professions
        guardian = await self.create_profession(
            name="Guardian",
            description="A versatile profession that can fill multiple roles.",
            icon="guardian.png"
        )
        
        warrior = await self.create_profession(
            name="Warrior",
            description="A heavy armor profession that excels at melee combat.",
            icon="warrior.png"
        )
        
        # Create builds
        guardian_build = await self.create_build(
            name="Power Dragonhunter",
            description="High DPS Dragonhunter build for PvE.",
            game_mode=GameMode.pve,
            is_public=True,
            user_id=test_user.id,
            profession_id=guardian.id,
            specializations=["Radiance", "Zeal", "Dragonhunter"],
            weapon_set_1={"main_hand": "Sword", "off_hand": "Focus"},
            weapon_set_2={"two_handed": "Greatsword"},
            skills={"heal": "Signet of Resolve", "elite": "Renewed Focus"},
        )
        
        warrior_build = await self.create_build(
            name="Berserker Banner Slave",
            description="Support Warrior with banners for PvE.",
            game_mode=GameMode.pve,
            is_public=True,
            user_id=admin_user.id,
            profession_id=warrior.id,
            specializations=["Strength", "Tactics", "Berserker"],
            weapon_set_1={"two_handed": "Greatsword"},
            weapon_set_2={"main_hand": "Axe", "off_hand": "Axe"},
            skills={"heal": "Mending", "elite": "Head Butt"},
        )
        
        # Create compositions
        raid_comp = await self.create_composition(
            name="Power Quickness Firebrand",
            description="Support Firebrand with Quickness for raids.",
            squad_size=10,
            is_public=True,
            user_id=admin_user.id,
            game_mode="pve",
            builds=[guardian_build]
        )
        
        wvw_comp = await self.create_composition(
            name="WvW Zerg Frontline",
            description="Frontline composition for WvW zergs.",
            squad_size=50,
            is_public=True,
            user_id=test_user.id,
            game_mode="wvw",
            builds=[guardian_build, warrior_build]
        )
        
        return {
            "users": {"admin": admin_user, "test": test_user},
            "roles": {"admin": admin_role, "user": user_role},
            "professions": {"guardian": guardian, "warrior": warrior},
            "builds": {"guardian": guardian_build, "warrior": warrior_build},
            "compositions": {"raid": raid_comp, "wvw": wvw_comp},
        }
