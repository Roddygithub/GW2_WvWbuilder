"""
Factories pour générer des données de test pour les modèles.

Ce module fournit des fonctions pour générer facilement des instances de modèles
de test avec des données aléatoires ou spécifiques.
"""

import random
import string
from datetime import datetime
from typing import Any, Type, TypeVar

from faker import Faker

from app.models.base import BaseModel
from app.models.user import User
from app.models.role import Role
from app.models.permission import Permission
from app.models.profession import Profession
from app.models.build import Build
from app.models.composition import Composition

# Import des schémas Pydantic depuis app.schemas
from app.schemas.user import UserCreate
from app.schemas.role import RoleCreate
from app.schemas.permission import PermissionCreate
from app.schemas.profession import ProfessionCreate
from app.schemas.build import BuildCreate
from app.schemas.composition import CompositionCreate

# Initialiser Faker
fake = Faker()
Faker.seed(42)  # Pour des résultats reproductibles

# Type variable pour les modèles
ModelType = TypeVar("ModelType", bound=BaseModel)


def random_string(length: int = 10) -> str:
    """Génère une chaîne aléatoire de la longueur spécifiée."""
    letters = string.ascii_letters + string.digits
    return "".join(random.choice(letters) for _ in range(length))


def random_email() -> str:
    """Génère un email aléatoire."""
    return f"{random_string(10)}@example.com"


def random_password(length: int = 12) -> str:
    """Génère un mot de passe aléatoire sécurisé."""
    chars = string.ascii_letters + string.digits + "!@#$%^&*()"
    return "".join(random.choice(chars) for _ in range(length))


def create_user_data(**overrides) -> dict:
    """Génère des données pour la création d'un utilisateur."""
    data = {
        "email": random_email(),
        "password": random_password(),
        "first_name": fake.first_name(),
        "last_name": fake.last_name(),
        "is_active": True,
        "is_verified": True,
    }
    data.update(overrides)
    return data


def create_user_in(**overrides) -> UserCreate:
    """Crée un objet UserCreate avec des données aléatoires."""
    data = create_user_data(**overrides)
    return UserCreate(**data)


def create_user(db: Any, **overrides) -> User:
    """Crée et sauvegarde un utilisateur dans la base de données."""
    from app.crud.crud_user import user as crud_user

    data = create_user_data(**overrides)
    user_in = UserCreate(**data)
    return crud_user.create(db, obj_in=user_in)


def create_role_data(**overrides) -> dict:
    """Génère des données pour la création d'un rôle."""
    data = {
        "name": f"role_{random_string(8).lower()}",
        "description": fake.sentence(),
        "is_active": True,
        "is_default": False,
    }
    data.update(overrides)
    return data


def create_role_in(**overrides) -> RoleCreate:
    """Crée un objet RoleCreate avec des données aléatoires."""
    data = create_role_data(**overrides)
    return RoleCreate(**data)


def create_role(db: Any, **overrides) -> Role:
    """Crée et sauvegarde un rôle dans la base de données."""
    from app.crud.crud_role import role as crud_role

    data = create_role_data(**overrides)
    role_in = RoleCreate(**data)
    return crud_role.create(db, obj_in=role_in)


def create_permission_data(**overrides) -> dict:
    """Génère des données pour la création d'une permission."""
    data = {
        "name": f"perm_{random_string(8).lower()}",
        "description": fake.sentence(),
    }
    data.update(overrides)
    return data


def create_permission_in(**overrides) -> PermissionCreate:
    """Crée un objet PermissionCreate avec des données aléatoires."""
    data = create_permission_data(**overrides)
    return PermissionCreate(**data)


def create_permission(db: Any, **overrides) -> Permission:
    """Crée et sauvegarde une permission dans la base de données."""
    from app.crud.crud_permission import permission as crud_permission

    data = create_permission_data(**overrides)
    permission_in = PermissionCreate(**data)
    return crud_permission.create(db, obj_in=permission_in)


def create_profession_data(**overrides) -> dict:
    """Génère des données pour la création d'une profession."""
    professions = [
        "Garde",
        "Guerrier",
        "Ingénieur",
        "Voleur",
        "Rôdeur",
        "Élémentaliste",
        "Nécromancien",
        "Enchanteur",
        "Revenant",
    ]

    data = {
        "name": random.choice(professions),
        "description": fake.sentence(),
        "icon": f"icon_{random_string(6)}.png",
        "is_active": True,
    }
    data.update(overrides)
    return data


def create_profession_in(**overrides) -> ProfessionCreate:
    """Crée un objet ProfessionCreate avec des données aléatoires."""
    data = create_profession_data(**overrides)
    return ProfessionCreate(**data)


def create_profession(db: Any, **overrides) -> Profession:
    """Crée et sauvegarde une profession dans la base de données."""
    from app.crud.crud_profession import profession as crud_profession

    data = create_profession_data(**overrides)
    profession_in = ProfessionCreate(**data)
    return crud_profession.create(db, obj_in=profession_in)


def create_build_data(**overrides) -> dict:
    """Génère des données pour la création d'un build."""
    data = {
        "name": f"Build {fake.word().capitalize()}",
        "description": fake.paragraph(),
        "is_public": random.choice([True, False]),
        "is_featured": False,
        "game_mode": random.choice(["PvE", "PvP", "WvW"]),
    }
    data.update(overrides)
    return data


def create_build_in(**overrides) -> BuildCreate:
    """Crée un objet BuildCreate avec des données aléatoires."""
    data = create_build_data(**overrides)
    return BuildCreate(**data)


def create_build(db: Any, **overrides) -> Build:
    """Crée et sauvegarde un build dans la base de données."""
    from app.crud.crud_build import build as crud_build

    # S'assurer que l'utilisateur et la profession existent
    if "owner_id" not in overrides:
        user = create_user(db)
        overrides["owner_id"] = user.id

    if "profession_id" not in overrides:
        profession = create_profession(db)
        overrides["profession_id"] = profession.id

    data = create_build_data(**overrides)
    build_in = BuildCreate(**data)
    return crud_build.create(db, obj_in=build_in)


def create_composition_data(**overrides) -> dict:
    """Génère des données pour la création d'une composition."""
    data = {
        "name": f"Comp {fake.word().capitalize()}",
        "description": fake.paragraph(),
        "is_public": random.choice([True, False]),
        "game_mode": "WvW",
    }
    data.update(overrides)
    return data


def create_composition_in(**overrides) -> CompositionCreate:
    """Crée un objet CompositionCreate avec des données aléatoires."""
    data = create_composition_data(**overrides)
    return CompositionCreate(**data)


def create_composition(db: Any, **overrides) -> Composition:
    """Crée et sauvegarde une composition dans la base de données."""
    from app.crud.crud_composition import composition as crud_composition

    # S'assurer que l'utilisateur existe
    if "owner_id" not in overrides:
        user = create_user(db)
        overrides["owner_id"] = user.id

    data = create_composition_data(**overrides)
    composition_in = CompositionCreate(**data)
    return crud_composition.create(db, obj_in=composition_in)


def create_model_factory(model_class: Type[ModelType]) -> callable:
    """
    Crée une fonction factory pour un modèle spécifique.

    Args:
        model_class: La classe du modèle pour laquelle créer la factory

    Returns:
        Une fonction qui génère des instances du modèle avec des données aléatoires
    """

    def factory(**overrides):
        """Génère une instance du modèle avec des données aléatoires."""
        # Déterminer la classe de création appropriée
        create_class = getattr(sys.modules[__name__], f"{model_class.__name__}Create", None)
        if create_class is None:
            create_class = model_class

        # Générer des données par défaut
        data = {}
        if hasattr(create_class, "model_fields"):
            for field_name, field in create_class.model_fields.items():
                if field_name in overrides:
                    continue

                # Générer des valeurs par défaut en fonction du type
                if field_name == "email":
                    data[field_name] = random_email()
                elif field_name == "password":
                    data[field_name] = random_password()
                elif field_name.endswith("_at") or field_name in ["created_at", "updated_at"]:
                    data[field_name] = datetime.utcnow()
                elif field_name.endswith("_id"):
                    # Pour les clés étrangères, on laisse None par défaut
                    data[field_name] = None
                elif field.annotation == str:
                    data[field_name] = f"{field_name}_{random_string(5)}"
                elif field.annotation == int:
                    data[field_name] = random.randint(1, 1000)
                elif field.annotation == bool:
                    data[field_name] = random.choice([True, False])

        # Mettre à jour avec les valeurs fournies
        data.update(overrides)

        # Créer l'instance
        return model_class(**data)

    return factory


# Créer des factories pour tous les modèles
create_user_factory = create_model_factory(User)
create_role_factory = create_model_factory(Role)
create_permission_factory = create_model_factory(Permission)
create_profession_factory = create_model_factory(Profession)
create_build_factory = create_model_factory(Build)
create_composition_factory = create_model_factory(Composition)
