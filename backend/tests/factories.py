"""Test data factories for the test suite."""
import factory
import factory.fuzzy
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Type, TypeVar

from app.models import (
    User, Role, Profession, EliteSpecialization, Build, Composition, CompositionTag
)
from app.schemas.user import UserCreate, UserUpdate
from app.schemas.role import RoleCreate, RoleUpdate
from app.schemas.profession import ProfessionCreate, ProfessionUpdate
from app.schemas.build import BuildCreate, BuildUpdate
from app.schemas.composition import CompositionCreate, CompositionUpdate
from app.core.security import get_password_hash

T = TypeVar('T')

class BaseFactory(factory.Factory):
    """Base factory with common functionality."""
    
    @classmethod
    def _create(cls, model_class: Type[T], *args: Any, **kwargs: Any) -> T:
        """Create an instance of the model."""
        return model_class(*args, **kwargs)


class RoleFactory(BaseFactory):
    """Factory for creating Role instances."""
    
    class Meta:
        model = Role
    
    id = factory.Sequence(lambda n: n + 1)
    name = factory.Sequence(lambda n: f"role_{n}")
    description = factory.Faker('sentence')
    permission_level = factory.fuzzy.FuzzyInteger(1, 10)
    is_default = False
    created_at = factory.LazyFunction(datetime.utcnow)
    updated_at = factory.LazyFunction(datetime.utcnow)


class UserFactory(BaseFactory):
    """Factory for creating User instances."""
    
    class Meta:
        model = User
    
    id = factory.Sequence(lambda n: n + 1)
    username = factory.Sequence(lambda n: f"user_{n}")
    email = factory.Sequence(lambda n: f"user_{n}@example.com")
    hashed_password = factory.LazyFunction(lambda: get_password_hash("testpassword"))
    is_active = True
    role_id = 1
    created_at = factory.LazyFunction(datetime.utcnow)
    updated_at = factory.LazyFunction(datetime.utcnow)
    
    @classmethod
    def _create(cls, model_class: Type[T], *args: Any, **kwargs: Any) -> T:
        """Create a user with a role if not provided."""
        if "role" not in kwargs and "role_id" not in kwargs:
            kwargs["role_id"] = 1
        return super()._create(model_class, *args, **kwargs)


class ProfessionFactory(BaseFactory):
    """Factory for creating Profession instances."""
    
    class Meta:
        model = Profession
    
    id = factory.Sequence(lambda n: n + 1)
    name = factory.Sequence(lambda n: f"profession_{n}")
    description = factory.Faker('sentence')
    icon = factory.Faker('file_name', extension='png')
    created_at = factory.LazyFunction(datetime.utcnow)
    updated_at = factory.LazyFunction(datetime.utcnow)


class EliteSpecializationFactory(BaseFactory):
    """Factory for creating EliteSpecialization instances."""
    
    class Meta:
        model = EliteSpecialization
    
    id = factory.Sequence(lambda n: n + 1)
    name = factory.Sequence(lambda n: f"elite_spec_{n}")
    description = factory.Faker('sentence')
    icon = factory.Faker('file_name', extension='png')
    profession_id = factory.Sequence(lambda n: n + 1)
    created_at = factory.LazyFunction(datetime.utcnow)
    updated_at = factory.LazyFunction(datetime.utcnow)


class BuildFactory(BaseFactory):
    """Factory for creating Build instances."""
    
    class Meta:
        model = Build
    
    id = factory.Sequence(lambda n: n + 1)
    name = factory.Sequence(lambda n: f"build_{n}")
    description = factory.Faker('sentence')
    is_public = True
    created_by = factory.Sequence(lambda n: n + 1)
    profession_id = factory.Sequence(lambda n: n + 1)
    created_at = factory.LazyFunction(datetime.utcnow)
    updated_at = factory.LazyFunction(datetime.utcnow)


class CompositionFactory(BaseFactory):
    """Factory for creating Composition instances."""
    
    class Meta:
        model = Composition
    
    id = factory.Sequence(lambda n: n + 1)
    name = factory.Sequence(lambda n: f"composition_{n}")
    description = factory.Faker('sentence')
    squad_size = 10
    is_public = True
    created_by = factory.Sequence(lambda n: n + 1)
    build_id = factory.Sequence(lambda n: n + 1)
    created_at = factory.LazyFunction(datetime.utcnow)
    updated_at = factory.LazyFunction(datetime.utcnow)


class CompositionTagFactory(BaseFactory):
    """Factory for creating CompositionTag instances."""
    
    class Meta:
        model = CompositionTag
    
    id = factory.Sequence(lambda n: n + 1)
    name = factory.Sequence(lambda n: f"tag_{n}")
    created_at = factory.LazyFunction(datetime.utcnow)


# Schema factories
class UserCreateFactory(factory.Factory):
    """Factory for creating UserCreate schemas."""
    
    class Meta:
        model = UserCreate
    
    username = factory.Sequence(lambda n: f"user_{n}")
    email = factory.Sequence(lambda n: f"user_{n}@example.com")
    password = "testpassword"
    is_active = True


class RoleCreateFactory(factory.Factory):
    """Factory for creating RoleCreate schemas."""
    
    class Meta:
        model = RoleCreate
    
    name = factory.Sequence(lambda n: f"role_{n}")
    description = factory.Faker('sentence')
    permission_level = factory.fuzzy.FuzzyInteger(1, 10)
    is_default = False


class BuildCreateFactory(factory.Factory):
    """Factory for creating BuildCreate schemas."""
    
    class Meta:
        model = BuildCreate
    
    name = factory.Sequence(lambda n: f"build_{n}")
    description = factory.Faker('sentence')
    is_public = True
    profession_id = factory.Sequence(lambda n: n + 1)
