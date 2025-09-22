"""Test data generation and management."""

import random
import string
from datetime import datetime, timedelta
from typing import Any, Dict, Optional, TypeVar

from faker import Faker

from app.models import User, Role, Profession, Build, Composition
from app.schemas import (
    UserCreate,
    UserUpdate,
    UserInDB,
    RoleCreate,
    RoleUpdate,
    RoleInDB,
    ProfessionCreate,
    ProfessionUpdate,
    ProfessionInDB,
    BuildCreate,
    BuildUpdate,
    BuildInDB,
    CompositionCreate,
    CompositionUpdate,
    CompositionInDB,
    GameMode,
)

# Initialize Faker
fake = Faker()

# Type variable for models
T = TypeVar("T")


def random_string(length: int = 10) -> str:
    """Generate a random string of fixed length."""
    letters = string.ascii_letters + string.digits
    return "".join(random.choice(letters) for _ in range(length))


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


def random_datetime(
    start: Optional[datetime] = None, end: Optional[datetime] = None
) -> datetime:
    """Generate a random datetime between two dates."""
    if start is None:
        start = datetime(2020, 1, 1)
    if end is None:
        end = datetime.now()

    delta = end - start
    int_delta = (delta.days * 24 * 60 * 60) + delta.seconds
    random_second = random.randrange(int_delta)
    return start + timedelta(seconds=random_second)


class UserFactory:
    """Factory for creating User test data."""

    @staticmethod
    def create_user(
        username: Optional[str] = None,
        email: Optional[str] = None,
        password: Optional[str] = None,
        is_active: Optional[bool] = None,
        is_superuser: bool = False,
        **kwargs,
    ) -> User:
        """Create a User instance with test data."""
        return User(
            username=username or random_username(),
            email=email or random_email(),
            hashed_password=password or random_password(),
            is_active=is_active if is_active is not None else random_bool(),
            is_superuser=is_superuser,
            **kwargs,
        )

    @staticmethod
    def create_user_create(
        username: Optional[str] = None,
        email: Optional[str] = None,
        password: Optional[str] = None,
        is_active: Optional[bool] = None,
        is_superuser: bool = False,
        **kwargs,
    ) -> UserCreate:
        """Create a UserCreate instance with test data."""
        return UserCreate(
            username=username or random_username(),
            email=email or random_email(),
            password=password or random_password(),
            is_active=is_active if is_active is not None else random_bool(),
            is_superuser=is_superuser,
            **kwargs,
        )

    @staticmethod
    def create_user_update(
        email: Optional[str] = None,
        password: Optional[str] = None,
        is_active: Optional[bool] = None,
        **kwargs,
    ) -> UserUpdate:
        """Create a UserUpdate instance with test data."""
        data = {}

        if email is not None:
            data["email"] = email
        if password is not None:
            data["password"] = password
        if is_active is not None:
            data["is_active"] = is_active

        data.update(kwargs)
        return UserUpdate(**data)

    @staticmethod
    def create_user_in_db(
        username: Optional[str] = None,
        email: Optional[str] = None,
        password: Optional[str] = None,
        is_active: bool = True,
        is_superuser: bool = False,
        **kwargs,
    ) -> UserInDB:
        """Create a UserInDB instance with test data."""
        return UserInDB(
            username=username or random_username(),
            email=email or random_email(),
            hashed_password=password or random_password(),
            is_active=is_active,
            is_superuser=is_superuser,
            **kwargs,
        )


class RoleFactory:
    """Factory for creating Role test data."""

    @staticmethod
    def create_role(
        name: Optional[str] = None,
        description: Optional[str] = None,
        permission_level: Optional[int] = None,
        is_default: bool = False,
        **kwargs,
    ) -> Role:
        """Create a Role instance with test data."""
        return Role(
            name=name or f"role_{random_string(8).lower()}",
            description=description or fake.sentence(),
            permission_level=permission_level or random.randint(1, 10),
            is_default=is_default,
            **kwargs,
        )

    @staticmethod
    def create_role_create(
        name: Optional[str] = None,
        description: Optional[str] = None,
        permission_level: Optional[int] = None,
        is_default: bool = False,
        **kwargs,
    ) -> RoleCreate:
        """Create a RoleCreate instance with test data."""
        return RoleCreate(
            name=name or f"role_{random_string(8).lower()}",
            description=description or fake.sentence(),
            permission_level=permission_level or random.randint(1, 10),
            is_default=is_default,
            **kwargs,
        )

    @staticmethod
    def create_role_update(
        description: Optional[str] = None,
        permission_level: Optional[int] = None,
        is_default: Optional[bool] = None,
        **kwargs,
    ) -> RoleUpdate:
        """Create a RoleUpdate instance with test data."""
        data = {}

        if description is not None:
            data["description"] = description
        if permission_level is not None:
            data["permission_level"] = permission_level
        if is_default is not None:
            data["is_default"] = is_default

        data.update(kwargs)
        return RoleUpdate(**data)

    @staticmethod
    def create_role_in_db(
        name: Optional[str] = None,
        description: Optional[str] = None,
        permission_level: Optional[int] = None,
        is_default: bool = False,
        **kwargs,
    ) -> RoleInDB:
        """Create a RoleInDB instance with test data."""
        return RoleInDB(
            name=name or f"role_{random_string(8).lower()}",
            description=description or fake.sentence(),
            permission_level=permission_level or random.randint(1, 10),
            is_default=is_default,
            **kwargs,
        )


class ProfessionFactory:
    """Factory for creating Profession test data."""

    @staticmethod
    def create_profession(
        name: Optional[str] = None,
        description: Optional[str] = None,
        icon: Optional[str] = None,
        **kwargs,
    ) -> Profession:
        """Create a Profession instance with test data."""
        return Profession(
            name=name or f"profession_{random_string(8).lower()}",
            description=description or fake.paragraph(),
            icon=icon or f"icon_{random_string(8)}.png",
            **kwargs,
        )

    @staticmethod
    def create_profession_create(
        name: Optional[str] = None,
        description: Optional[str] = None,
        icon: Optional[str] = None,
        **kwargs,
    ) -> ProfessionCreate:
        """Create a ProfessionCreate instance with test data."""
        return ProfessionCreate(
            name=name or f"profession_{random_string(8).lower()}",
            description=description or fake.paragraph(),
            icon=icon or f"icon_{random_string(8)}.png",
            **kwargs,
        )

    @staticmethod
    def create_profession_update(
        description: Optional[str] = None, icon: Optional[str] = None, **kwargs
    ) -> ProfessionUpdate:
        """Create a ProfessionUpdate instance with test data."""
        data = {}

        if description is not None:
            data["description"] = description
        if icon is not None:
            data["icon"] = icon

        data.update(kwargs)
        return ProfessionUpdate(**data)

    @staticmethod
    def create_profession_in_db(
        name: Optional[str] = None,
        description: Optional[str] = None,
        icon: Optional[str] = None,
        **kwargs,
    ) -> ProfessionInDB:
        """Create a ProfessionInDB instance with test data."""
        return ProfessionInDB(
            name=name or f"profession_{random_string(8).lower()}",
            description=description or fake.paragraph(),
            icon=icon or f"icon_{random_string(8)}.png",
            **kwargs,
        )


class BuildFactory:
    """Factory for creating Build test data."""

    @staticmethod
    def create_build(
        name: Optional[str] = None,
        description: Optional[str] = None,
        game_mode: Optional[GameMode] = None,
        is_public: bool = True,
        user_id: Optional[int] = None,
        profession_id: Optional[int] = None,
        **kwargs,
    ) -> Build:
        """Create a Build instance with test data."""
        return Build(
            name=name or f"build_{random_string(8)}",
            description=description or fake.paragraph(),
            game_mode=game_mode or random_choice(list(GameMode)),
            is_public=is_public,
            user_id=user_id or random.randint(1, 1000),
            profession_id=profession_id or random.randint(1, 1000),
            **kwargs,
        )

    @staticmethod
    def create_build_create(
        name: Optional[str] = None,
        description: Optional[str] = None,
        game_mode: Optional[GameMode] = None,
        is_public: bool = True,
        user_id: Optional[int] = None,
        profession_id: Optional[int] = None,
        **kwargs,
    ) -> BuildCreate:
        """Create a BuildCreate instance with test data."""
        return BuildCreate(
            name=name or f"build_{random_string(8)}",
            description=description or fake.paragraph(),
            game_mode=game_mode or random_choice(list(GameMode)),
            is_public=is_public,
            user_id=user_id or random.randint(1, 1000),
            profession_id=profession_id or random.randint(1, 1000),
            **kwargs,
        )

    @staticmethod
    def create_build_update(
        name: Optional[str] = None,
        description: Optional[str] = None,
        game_mode: Optional[GameMode] = None,
        is_public: Optional[bool] = None,
        **kwargs,
    ) -> BuildUpdate:
        """Create a BuildUpdate instance with test data."""
        data = {}

        if name is not None:
            data["name"] = name
        if description is not None:
            data["description"] = description
        if game_mode is not None:
            data["game_mode"] = game_mode
        if is_public is not None:
            data["is_public"] = is_public

        data.update(kwargs)
        return BuildUpdate(**data)

    @staticmethod
    def create_build_in_db(
        name: Optional[str] = None,
        description: Optional[str] = None,
        game_mode: Optional[GameMode] = None,
        is_public: bool = True,
        user_id: Optional[int] = None,
        profession_id: Optional[int] = None,
        **kwargs,
    ) -> BuildInDB:
        """Create a BuildInDB instance with test data."""
        return BuildInDB(
            name=name or f"build_{random_string(8)}",
            description=description or fake.paragraph(),
            game_mode=game_mode or random_choice(list(GameMode)),
            is_public=is_public,
            user_id=user_id or random.randint(1, 1000),
            profession_id=profession_id or random.randint(1, 1000),
            **kwargs,
        )


class CompositionFactory:
    """Factory for creating Composition test data."""

    @staticmethod
    def create_composition(
        name: Optional[str] = None,
        description: Optional[str] = None,
        squad_size: int = 10,
        is_public: bool = True,
        game_mode: Optional[str] = None,
        user_id: Optional[int] = None,
        **kwargs,
    ) -> Composition:
        """Create a Composition instance with test data."""
        return Composition(
            name=name or f"comp_{random_string(8)}",
            description=description or fake.paragraph(),
            squad_size=squad_size,
            is_public=is_public,
            game_mode=game_mode or random_choice(["pve", "wvw", "pvp"]),
            user_id=user_id or random.randint(1, 1000),
            **kwargs,
        )

    @staticmethod
    def create_composition_create(
        name: Optional[str] = None,
        description: Optional[str] = None,
        squad_size: int = 10,
        is_public: bool = True,
        game_mode: Optional[str] = None,
        user_id: Optional[int] = None,
        **kwargs,
    ) -> CompositionCreate:
        """Create a CompositionCreate instance with test data."""
        return CompositionCreate(
            name=name or f"comp_{random_string(8)}",
            description=description or fake.paragraph(),
            squad_size=squad_size,
            is_public=is_public,
            game_mode=game_mode or random_choice(["pve", "wvw", "pvp"]),
            user_id=user_id or random.randint(1, 1000),
            **kwargs,
        )

    @staticmethod
    def create_composition_update(
        name: Optional[str] = None,
        description: Optional[str] = None,
        squad_size: Optional[int] = None,
        is_public: Optional[bool] = None,
        game_mode: Optional[str] = None,
        **kwargs,
    ) -> CompositionUpdate:
        """Create a CompositionUpdate instance with test data."""
        data = {}

        if name is not None:
            data["name"] = name
        if description is not None:
            data["description"] = description
        if squad_size is not None:
            data["squad_size"] = squad_size
        if is_public is not None:
            data["is_public"] = is_public
        if game_mode is not None:
            data["game_mode"] = game_mode

        data.update(kwargs)
        return CompositionUpdate(**data)

    @staticmethod
    def create_composition_in_db(
        name: Optional[str] = None,
        description: Optional[str] = None,
        squad_size: int = 10,
        is_public: bool = True,
        game_mode: Optional[str] = None,
        user_id: Optional[int] = None,
        **kwargs,
    ) -> CompositionInDB:
        """Create a CompositionInDB instance with test data."""
        return CompositionInDB(
            name=name or f"comp_{random_string(8)}",
            description=description or fake.paragraph(),
            squad_size=squad_size,
            is_public=is_public,
            game_mode=game_mode or random_choice(["pve", "wvw", "pvp"]),
            user_id=user_id or random.randint(1, 1000),
            **kwargs,
        )


class TestDataGenerator:
    """Helper class for generating test data."""

    def __init__(self):
        """Initialize the test data generator."""
        self.user_factory = UserFactory()
        self.role_factory = RoleFactory()
        self.profession_factory = ProfessionFactory()
        self.build_factory = BuildFactory()
        self.composition_factory = CompositionFactory()

    def create_user(self, **kwargs) -> User:
        """Create a test user."""
        return self.user_factory.create_user(**kwargs)

    def create_role(self, **kwargs) -> Role:
        """Create a test role."""
        return self.role_factory.create_role(**kwargs)

    def create_profession(self, **kwargs) -> Profession:
        """Create a test profession."""
        return self.profession_factory.create_profession(**kwargs)

    def create_build(self, **kwargs) -> Build:
        """Create a test build."""
        return self.build_factory.create_build(**kwargs)

    def create_composition(self, **kwargs) -> Composition:
        """Create a test composition."""
        return self.composition_factory.create_composition(**kwargs)

    def create_user_create(self, **kwargs) -> UserCreate:
        """Create a test user create DTO."""
        return self.user_factory.create_user_create(**kwargs)

    def create_role_create(self, **kwargs) -> RoleCreate:
        """Create a test role create DTO."""
        return self.role_factory.create_role_create(**kwargs)

    def create_profession_create(self, **kwargs) -> ProfessionCreate:
        """Create a test profession create DTO."""
        return self.profession_factory.create_profession_create(**kwargs)

    def create_build_create(self, **kwargs) -> BuildCreate:
        """Create a test build create DTO."""
        return self.build_factory.create_build_create(**kwargs)

    def create_composition_create(self, **kwargs) -> CompositionCreate:
        """Create a test composition create DTO."""
        return self.composition_factory.create_composition_create(**kwargs)

    def generate_test_data(self) -> Dict[str, Any]:
        """Generate a complete set of test data."""
        # Create roles
        admin_role = self.role_factory.create_role(
            name="admin",
            description="Administrator role",
            permission_level=10,
            is_default=False,
        )

        user_role = self.role_factory.create_role(
            name="user",
            description="Regular user role",
            permission_level=1,
            is_default=True,
        )

        # Create users
        admin_user = self.user_factory.create_user(
            username="admin",
            email="admin@example.com",
            is_active=True,
            is_superuser=True,
        )

        test_user = self.user_factory.create_user(
            username="testuser",
            email="test@example.com",
            is_active=True,
            is_superuser=False,
        )

        # Create professions
        guardian = self.profession_factory.create_profession(
            name="Guardian",
            description="A versatile profession that can fill multiple roles.",
            icon="guardian.png",
        )

        warrior = self.profession_factory.create_profession(
            name="Warrior",
            description="A heavy armor profession that excels at melee combat.",
            icon="warrior.png",
        )

        # Create builds
        guardian_build = self.build_factory.create_build(
            name="Power Dragonhunter",
            description="High DPS Dragonhunter build for PvE.",
            game_mode=GameMode.pve,
            is_public=True,
            user_id=test_user.id,
            profession_id=guardian.id,
        )

        warrior_build = self.build_factory.create_build(
            name="Berserker Banner Slave",
            description="Support Warrior with banners for PvE.",
            game_mode=GameMode.pve,
            is_public=True,
            user_id=admin_user.id,
            profession_id=warrior.id,
        )

        # Create compositions
        raid_comp = self.composition_factory.create_composition(
            name="Power Quickness Firebrand",
            description="Support Firebrand with Quickness for raids.",
            squad_size=10,
            is_public=True,
            user_id=admin_user.id,
            game_mode="pve",
        )

        wvw_comp = self.composition_factory.create_composition(
            name="WvW Zerg Frontline",
            description="Frontline composition for WvW zergs.",
            squad_size=50,
            is_public=True,
            user_id=test_user.id,
            game_mode="wvw",
        )

        return {
            "users": {"admin": admin_user, "test": test_user},
            "roles": {"admin": admin_role, "user": user_role},
            "professions": {"guardian": guardian, "warrior": warrior},
            "builds": {"guardian": guardian_build, "warrior": warrior_build},
            "compositions": {"raid": raid_comp, "wvw": wvw_comp},
        }
