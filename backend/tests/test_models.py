"""Tests pour les modèles de base de données."""
import pytest
from sqlalchemy.exc import IntegrityError

def test_user_model(db_session, test_data):
    """Test de création d'un utilisateur."""
    from app.models.user import User
    
    user_data = test_data["user"]
    user = User(
        email=user_data["email"],
        username=user_data["username"],
        hashed_password=user_data["password"],  # Dans un vrai cas, utiliser get_password_hash
        is_active=user_data["is_active"],
        is_superuser=user_data["is_superuser"],
    )
    
    db_session.add(user)
    db_session.commit()
    
    # Vérifier que l'utilisateur a été créé avec succès
    assert user.id is not None
    assert user.email == user_data["email"]
    assert user.username == user_data["username"]
    assert user.is_active == user_data["is_active"]
    assert user.is_superuser == user_data["is_superuser"]

def test_role_model(db_session, test_data):
    """Test de création d'un rôle."""
    from app.models.role import Role
    
    role_data = test_data["role"]
    role = Role(
        name=role_data["name"],
        description=role_data["description"],
    )
    
    db_session.add(role)
    db_session.commit()
    
    # Vérifier que le rôle a été créé avec succès
    assert role.id is not None
    assert role.name == role_data["name"]
    assert role.description == role_data["description"]

@pytest.mark.asyncio
async def test_profession_model(db_session, test_data):
    """Test de création d'une profession."""
    from app.models.profession import Profession
    
    profession_data = test_data["profession"]
    profession = Profession(
        name=profession_data["name"],
        description=profession_data["description"],
    )
    
    db_session.add(profession)
    db_session.commit()
    
    # Vérifier que la profession a été créée avec succès
    assert profession.id is not None
    assert profession.name == profession_data["name"]
    assert profession.description == profession_data["description"]

def test_user_role_relationship(db_session, test_data):
    """Test de la relation entre utilisateur et rôle."""
    from app.models.user import User
    from app.models.role import Role
    
    # Créer un rôle
    role = Role(
        name=test_data["role"]["name"],
        description=test_data["role"]["description"],
    )
    db_session.add(role)
    db_session.commit()
    
    # Créer un utilisateur avec ce rôle
    user_data = test_data["user"]
    user = User(
        email=user_data["email"],
        username=user_data["username"],
        hashed_password=user_data["password"],
        is_active=user_data["is_active"],
        is_superuser=user_data["is_superuser"],
        roles=[role],
    )
    db_session.add(user)
    db_session.commit()
    
    # Vérifier la relation
    assert user.roles == [role]
    assert role in user.roles
    assert user in role.users

def test_unique_constraint_violation(db_session, test_data):
    """Test de la contrainte d'unicité sur l'email."""
    from app.models.user import User
    
    # Créer un premier utilisateur
    user1 = User(
        email="test@example.com",
        username="user1",
        hashed_password="password123",
    )
    db_session.add(user1)
    db_session.commit()
    
    # Essayer de créer un deuxième utilisateur avec le même email
    user2 = User(
        email="test@example.com",
        username="user2",
        hashed_password="password456",
    )
    db_session.add(user2)
    
    # Vérifier que cela génère une erreur d'intégrité
    with pytest.raises(IntegrityError):
        db_session.commit()
    
    # Annuler la transaction pour éviter de polluer la base de données
    db_session.rollback()
