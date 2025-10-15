"""
Tests simplifiés pour le module app.api.deps.

Ce module contient des tests pour les dépendances de l'API,
notamment l'authentification et l'autorisation.
"""

import pytest
import pytest_asyncio
from unittest.mock import AsyncMock, MagicMock, patch
from fastapi import HTTPException, status, Request
from jose import JWTError
from datetime import datetime, timezone
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import Table, Column, Integer, Boolean, ForeignKey, MetaData

# Enable async test support
pytestmark = pytest.mark.asyncio

# Importer les modèles avant les mocks pour éviter les problèmes de références circulaires
from app.models.team import Team
from app.models.team_member import TeamMember
from app.models.user import User

# Créer une table team_members factice pour les tests
metadata = MetaData()


# Créer une classe pour remplacer le ColumnCollection
class MockColumnCollection:
    def __init__(self, table):
        self._columns = {}
        for col in table.columns:
            self._columns[col.name] = col

    def __getattr__(self, name):
        if name in self._columns:
            return self._columns[name]
        raise AttributeError(f"No column named '{name}'")


# Créer la table avec les colonnes
team_members = Table(
    "team_members",
    metadata,
    Column("team_id", Integer, ForeignKey("teams.id"), primary_key=True),
    Column("user_id", Integer, ForeignKey("users.id"), primary_key=True),
    Column("is_admin", Boolean, default=False, nullable=False),
)


# Créer un mock pour .c qui retourne nos colonnes
class MockCTable:
    def __init__(self, table):
        self.table = table
        self.columns = MockColumnCollection(table)

    def __getattr__(self, name):
        return getattr(self.columns, name)


# Remplacer .c par notre mock
team_members.c = MockCTable(team_members)

# Créer les modèles SQLAlchemy pour les tests
metadata = MetaData()


# Modèle User pour les tests
class User:
    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)

    def __eq__(self, other):
        if not isinstance(other, (User, MagicMock)):
            return False
        return getattr(self, "id", None) == getattr(other, "id", None)

    def __hash__(self):
        return hash(
            (
                getattr(self, "id", None),
                getattr(self, "username", None),
                getattr(self, "email", None),
            )
        )


# Modèle Team pour les tests
class Team:
    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)

    def __eq__(self, other):
        if not isinstance(other, (Team, MagicMock)):
            return False
        return getattr(self, "id", None) == getattr(other, "id", None)


# Modèle TeamMember pour les tests
class TeamMember:
    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)


# Créer la table team_members
team_members = Table(
    "team_members",
    metadata,
    Column("team_id", Integer, ForeignKey("teams.id"), primary_key=True),
    Column("user_id", Integer, ForeignKey("users.id"), primary_key=True),
    Column("is_admin", Boolean, default=False, nullable=False),
)

# Mock de la configuration avant d'importer les dépendances
with (
    patch("app.api.deps.oauth2_scheme") as mock_oauth2_scheme,
    patch("app.api.deps.jwt") as mock_jwt,
    patch("app.core.config.settings") as mock_settings,
    patch("app.crud.user_crud") as mock_user_crud,
    patch("app.crud.team_crud") as mock_team_crud,
    patch("app.crud.team_member_crud") as mock_team_member_crud,
):

    # Configurer le mock pour oauth2_scheme
    mock_oauth2_scheme.return_value = "test_token"

    # Configurer le mock pour jwt.decode
    mock_jwt.decode.return_value = {"sub": "1", "email": "test@example.com"}

    # Configurer le mock pour jwt.encode
    mock_jwt.encode.return_value = "mocked_jwt_token"

    # Configurer les paramètres de test
    mock_settings.ENVIRONMENT = "test"
    mock_settings.TEST_ACCESS_TOKEN = "test_token"
    mock_settings.TEST_USER_EMAIL = "test@example.com"
    mock_settings.TEST_USER_PASSWORD = "testpass"
    mock_settings.TEST_USER_FULLNAME = "Test User"
    mock_settings.SECRET_KEY = "test_secret"
    mock_settings.JWT_ALGORITHM = "HS256"
    mock_settings.API_V1_STR = "/api/v1"

    # Configurer les mocks CRUD
    mock_team_crud.get = AsyncMock()
    mock_team_member_crud.get = AsyncMock()

    # Importer les dépendances après avoir configuré les mocks
    import app.api.deps as deps_module

    # Injecter les dépendances nécessaires dans le module deps
    deps_module.team_members = team_members
    deps_module.team_crud = mock_team_crud
    deps_module.team_member_crud = mock_team_member_crud

    # Maintenant importer les fonctions à tester
    from app.api.deps import (
        get_current_user,
        get_current_active_user,
        get_current_active_superuser,
        check_team_admin,
    )

    # Patcher get_async_db pour retourner notre session mockée
    deps_module.get_async_db = AsyncMock(return_value=AsyncMock())

    # Créer des alias pour les mocks globaux
    global_mock_team_crud = mock_team_crud
    global_mock_team_member_crud = mock_team_member_crud

# Test data
TEST_USER_ID = 1
TEST_EMAIL = "test@example.com"
TEST_USERNAME = "testuser"
TEST_IS_SUPERUSER = False
TEST_IS_ACTIVE = True
TEST_TOKEN = "test_token"
TEST_TEAM_ID = 1
TEST_TEAM_NAME = "Test Team"
TEST_TEAM_DESCRIPTION = "A test team"
TEST_FULL_NAME = "Test User"

# La table team_members a déjà été définie plus haut avec la classe MockColumnCollection
# Assurons-nous qu'elle est correctement référencée dans le module deps
import app.api.deps as deps_module

deps_module.team_members = team_members


# Fixtures
@pytest_asyncio.fixture
async def mock_db_session():
    """Mock for async database session."""
    session = AsyncMock(spec=AsyncSession)
    session.scalar.return_value = None
    session.scalars.return_value = AsyncMock()
    session.scalars.return_value.first.return_value = None

    # Mock pour la méthode execute
    async def execute_mock(query, *args, **kwargs):
        # Simuler le comportement de base pour les requêtes de sélection
        if hasattr(query, "whereclause"):
            # Pour les requêtes avec filtre, retourner un mock avec une méthode first()
            result = AsyncMock()
            result.first.return_value = None
            return result
        return None

    session.execute.side_effect = execute_mock

    # Mock pour les requêtes spécifiques
    async def select_mock(query, *args, **kwargs):
        # Simuler la récupération d'une équipe
        if (
            hasattr(query, "_entities")
            and len(query._entities) > 0
            and hasattr(query._entities[0], "entity")
            and query._entities[0].entity == Team
        ):
            result = AsyncMock()
            result.scalar_one_or_none.return_value = None
            return result
        # Simuler la récupération d'un membre d'équipe
        elif hasattr(query, "whereclause") and hasattr(query, "compare"):
            result = AsyncMock()
            result.first.return_value = None
            return result
        # Pour les autres requêtes, utiliser le mock par défaut
        result = AsyncMock()
        result.first.return_value = None
        result.scalar_one_or_none.return_value = None
        return result

    session.execute.side_effect = select_mock

    # Add mock for the webhooks relationship to prevent AttributeError
    session.object_session.return_value = session

    return session


@pytest.fixture
def create_test_user():
    """Crée un utilisateur de test avec toutes les relations nécessaires."""

    def _create_test_user(
        user_id=TEST_USER_ID,
        email=TEST_EMAIL,
        username=TEST_USERNAME,
        is_superuser=TEST_IS_SUPERUSER,
        is_active=TEST_IS_ACTIVE,
        full_name=TEST_FULL_NAME,
    ):
        # Créer un mock pour l'utilisateur avec des attributs de base
        user = MagicMock(
            spec=User,
            id=user_id,
            email=email,
            username=username,
            is_superuser=is_superuser,
            is_active=is_active,
            full_name=full_name,
            hashed_password="hashed_password",
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
        )

        # Ajouter des méthodes qui pourraient être appelées
        user.dict = lambda: {
            "id": user_id,
            "email": email,
            "username": username,
            "is_superuser": is_superuser,
            "is_active": is_active,
            "full_name": full_name,
            "hashed_password": "hashed_password",
        }

        # Configurer les relations qui pourraient être accédées
        user.webhooks = MagicMock()
        user.webhooks.all.return_value = []

        user.teams = MagicMock()
        user.teams.all.return_value = []

        user.team_associations = MagicMock()
        user.team_associations.all.return_value = []

        user.owned_teams = MagicMock()
        user.owned_teams.all.return_value = []

        user.roles = MagicMock()
        user.roles.all.return_value = []

        user.role_associations = MagicMock()
        user.role_associations.all.return_value = []

        user.compositions = MagicMock()
        user.compositions.all.return_value = []

        user.builds = MagicMock()
        user.builds.all.return_value = []

        user.tokens = MagicMock()
        user.tokens.all.return_value = []

        # Utiliser l'implémentation par défaut de MagicMock pour __eq__
        # et définir un hash basé sur l'ID pour permettre l'utilisation dans des sets/dicts
        user.id = user_id  # S'assurer que l'ID est défini
        user.__hash__ = lambda s: hash(s.id) if hasattr(s, "id") else hash(id(s))

        return user

    return _create_test_user


@pytest.fixture
def create_test_team():
    """Crée une équipe de test."""

    def _create_test_team(
        team_id=TEST_TEAM_ID,
        name=TEST_TEAM_NAME,
        description=TEST_TEAM_DESCRIPTION,
        owner_id=TEST_USER_ID,
        is_active=True,
    ):
        team = MagicMock()
        team.id = team_id
        team.name = name
        team.description = description
        team.owner_id = owner_id
        team.is_active = is_active

        # Add methods that might be called
        team.dict = lambda: {
            "id": team_id,
            "name": name,
            "description": description,
            "owner_id": owner_id,
            "is_active": is_active,
        }

        # Add relationships
        team.members = []
        team.owner = MagicMock()
        team.owner.id = owner_id

        return team

    return _create_test_team


@pytest.fixture
def create_team_member():
    """Crée un membre d'équipe de test."""

    def _create_team_member(team_id=TEST_TEAM_ID, user_id=TEST_USER_ID, is_admin=False):
        member = MagicMock()
        member.team_id = team_id
        member.user_id = user_id
        member.is_admin = is_admin

        # Add methods that might be called
        member.dict = lambda: {
            "team_id": team_id,
            "user_id": user_id,
            "is_admin": is_admin,
        }

        return member

    return _create_team_member


# Tests pour get_current_user
@pytest.mark.asyncio
async def test_get_current_user_valid_token(mock_db_session, create_test_user):
    """Teste la récupération d'un utilisateur avec un token valide."""
    # Créer un utilisateur de test
    test_user = create_test_user()

    # Créer un mock pour user_crud.get qui gère les arguments positionnels
    async def mock_user_get(*args, **kwargs):
        # Si des arguments positionnels sont passés, les convertir en arguments nommés
        if args:
            kwargs.update(
                {
                    "db": args[0] if len(args) > 0 else None,
                    "id": args[1] if len(args) > 1 else None,
                }
            )
        return test_user if kwargs.get("id") == test_user.id else None

    # Configurer les mocks
    with patch(
        "app.crud.user_crud.get", new=AsyncMock(side_effect=mock_user_get)
    ) as mock_user_get_func:
        # Configurer le mock pour jwt.decode
        with patch("app.api.deps.jwt.decode") as mock_jwt_decode:
            mock_jwt_decode.return_value = {"sub": str(test_user.id)}

            # Créer un mock pour la requête
            mock_request = MagicMock(spec=Request)
            mock_request.headers = {}

            # Appeler la fonction avec un token valide
            result = await get_current_user(
                request=mock_request, token="valid_token", db=mock_db_session
            )

            # Vérifier que l'utilisateur a été récupéré correctement
            assert result == test_user

            # Vérifier que user_crud.get a été appelé avec les bons paramètres
            mock_user_get_func.assert_called_once()

            # Vérifier que jwt.decode a été appelé avec les bons paramètres
            mock_jwt_decode.assert_called_once()

            # Récupérer les arguments avec lesquels la fonction a été appelée
            call_args = mock_jwt_decode.call_args

            # Vérifier les arguments positionnels (le token et la clé)
            assert len(call_args.args) >= 1
            assert call_args.args[0] == "valid_token"

            # Vérifier les arguments nommés
            assert call_args.kwargs.get("algorithms") == ["HS256"]

            # Vérifier si la clé est soit dans les arguments positionnels soit dans les arguments nommés
            assert len(call_args.args) > 1 or "key" in call_args.kwargs

            # Vérifier les options de vérification
            assert call_args.kwargs.get("options", {}).get("verify_aud") is False


@pytest.mark.asyncio
async def test_get_current_user_invalid_token(mock_db_session):
    """Teste la gestion d'un token invalide."""
    # Configurer le mock pour jwt.decode pour lever une exception
    with patch("app.api.deps.jwt.decode") as mock_decode:
        mock_decode.side_effect = JWTError("Token invalide")

        # Créer un mock pour la requête
        mock_request = MagicMock(spec=Request)
        mock_request.headers = {}

        # Vérifier qu'une exception est levée avec un token invalide
        with pytest.raises(HTTPException) as exc_info:
            await get_current_user(
                request=mock_request, token="invalid_token", db=mock_db_session
            )

        # Vérifier que l'exception a le bon statut HTTP (401 pour des identifiants invalides)
        assert exc_info.value.status_code == status.HTTP_401_UNAUTHORIZED
        assert "Could not validate credentials" in str(exc_info.value.detail)
        assert "Could not validate credentials" in str(exc_info.value.detail)


# Tests pour get_current_active_user
@pytest.mark.asyncio
async def test_get_current_active_user_active(create_test_user):
    """Teste la récupération d'un utilisateur actif."""
    # Créer un utilisateur actif
    test_user = create_test_user(is_active=True)

    # Tester la fonction
    result = await get_current_active_user(test_user)

    # Vérifier que l'utilisateur est retourné tel quel
    assert result == test_user


@pytest.mark.asyncio
async def test_get_current_active_user_inactive(create_test_user):
    """Teste la tentative de récupération d'un utilisateur inactif."""
    # Créer un utilisateur inactif
    test_user = create_test_user(is_active=False)

    # Vérifier qu'une exception est levée pour un utilisateur inactif
    with pytest.raises(HTTPException) as exc_info:
        await get_current_active_user(test_user)

    # Vérifier que l'exception a le bon statut et message
    assert exc_info.value.status_code == 400
    assert "Inactive user" in str(exc_info.value.detail)


# Tests pour get_current_active_superuser
@pytest.mark.asyncio
async def test_get_current_active_superuser_valid(create_test_user):
    """Teste la récupération d'un superutilisateur valide."""
    # Créer un superutilisateur
    test_user = create_test_user(is_superuser=True)

    # Tester la fonction
    result = await get_current_active_superuser(test_user)

    # Vérifier que l'utilisateur est retourné tel quel
    assert result == test_user


@pytest.mark.asyncio
async def test_get_current_active_superuser_not_superuser(create_test_user):
    """Teste la tentative de récupération d'un utilisateur non superutilisateur."""
    # Créer un utilisateur non superutilisateur
    test_user = create_test_user(is_superuser=False)

    # Vérifier qu'une exception est levée pour un utilisateur non superutilisateur
    with pytest.raises(HTTPException) as exc_info:
        await get_current_active_superuser(test_user)

    # Vérifier que l'exception a le bon statut et message
    assert exc_info.value.status_code == 403
    assert "The user doesn't have enough privileges" in str(exc_info.value.detail)


# Tests pour get_team_and_check_access
@pytest.mark.asyncio
async def test_get_team_and_check_access_owner(
    mock_db_session, create_test_user, create_test_team
):
    # Créer un utilisateur et une équipe
    test_user = create_test_user()
    test_team = create_test_team(owner_id=test_user.id)

    # Configurer les mocks pour la session de base de données
    async def execute_mock(query, *args, **kwargs):
        # Pour les requêtes sur la table Team
        if (
            hasattr(query, "_entities")
            and len(query._entities) > 0
            and hasattr(query._entities[0], "entity")
            and query._entities[0].entity == Team
        ):
            result = AsyncMock()
            # Configurer les membres de l'équipe
            test_team.members = []
            test_team.is_public = False
            test_team.webhooks = []
            result.scalar_one_or_none.return_value = test_team
            return result
        # Pour les requêtes sur la table team_members
        elif hasattr(query, "whereclause"):
            result = AsyncMock()
            result.first.return_value = None
            return result
        # Pour les autres requêtes, retourner un mock par défaut
        result = AsyncMock()
        result.first.return_value = None
        result.scalar_one_or_none.return_value = None
        return result

    mock_db_session.execute.side_effect = execute_mock

    # Patcher la fonction get_team pour retourner notre équipe de test
    with patch("app.crud.team_crud.get", new_callable=AsyncMock) as mock_team_get:
        mock_team_get.return_value = test_team

    # Configurer les mocks pour retourner None (équipe non trouvée)
    async def execute_mock(query, *args, **kwargs):
        # Simuler la récupération d'une équipe
        if (
            hasattr(query, "_entities")
            and len(query._entities) > 0
            and hasattr(query._entities[0], "entity")
            and query._entities[0].entity == Team
        ):
            result = AsyncMock()
            result.scalar_one_or_none.return_value = None
            return result
        # Pour les autres requêtes, retourner un mock par défaut
        result = AsyncMock()
        result.first.return_value = None
        result.scalar_one_or_none.return_value = None
        return result
        assert "Team not found" in str(exc_info.value.detail)


# Tests pour check_team_admin
@pytest.mark.asyncio
async def test_check_team_admin_success(
    mock_db_session, create_test_user, create_test_team
):
    """Teste la vérification d'un administrateur d'équipe valide."""
    # Créer un utilisateur et une équipe
    test_user = create_test_user()
    test_team = create_test_team(
        owner_id=test_user.id
    )  # L'utilisateur est propriétaire

    # Créer un mock pour get_team_and_check_access qui gère les arguments positionnels
    async def mock_get_team(*args, **kwargs):
        # Si des arguments positionnels sont passés, les convertir en arguments nommés
        if args:
            kwargs.update(
                {
                    "team_id": args[0] if len(args) > 0 else None,
                    "db": args[1] if len(args) > 1 else None,
                    "current_user": args[2] if len(args) > 2 else None,
                }
            )
        return test_team, True

    # Créer un mock pour get_team_and_check_access
    mock_get_team_func = AsyncMock(side_effect=mock_get_team)

    # Patcher get_team_and_check_access pour retourner notre équipe de test
    with patch("app.api.deps.get_team_and_check_access", new=mock_get_team_func):
        # Tester la fonction avec des arguments nommés
        result = await check_team_admin(
            team_id=test_team.id, db=mock_db_session, current_user=test_user
        )

        # Vérifier que l'équipe est retournée correctement
        assert result == test_team

        # Vérifier que get_team_and_check_access a été appelé avec les bons paramètres
        # Vérifier que la fonction a été appelée une fois
        assert mock_get_team_func.await_count == 1

        # Récupérer les arguments avec lesquels la fonction a été appelée
        call_args = mock_get_team_func.await_args

        # Vérifier les arguments positionnels (s'il y en a)
        if call_args.args:
            assert len(call_args.args) == 3
            assert call_args.args[0] == test_team.id  # team_id
            assert call_args.args[1] == mock_db_session  # db
            assert call_args.args[2] == test_user  # current_user

        # Vérifier les arguments nommés (s'il y en a)
        if call_args.kwargs:
            assert call_args.kwargs.get("team_id") == test_team.id
            assert call_args.kwargs.get("db") == mock_db_session
            assert call_args.kwargs.get("current_user") == test_user


@pytest.mark.asyncio
@pytest.mark.asyncio
async def test_check_team_admin_not_admin(
    mock_db_session, create_test_user, create_test_team
):
    """Teste la vérification d'un utilisateur qui n'est pas administrateur de l'équipe."""
    # Créer un utilisateur et une équipe
    test_user = create_test_user()
    other_user = create_test_user(
        user_id=2, email="other@example.com", username="otheruser"
    )
    test_team = create_test_team(
        owner_id=other_user.id
    )  # Un autre utilisateur est propriétaire

    # Configurer les mocks pour get_team_and_check_access
    async def get_team_mock(team_id, db, current_user):
        return test_team, False  # Retourne l'équipe mais is_admin=False

    # Patcher get_team_and_check_access pour retourner notre mock
    with patch(
        "app.api.deps.get_team_and_check_access",
        new=AsyncMock(side_effect=get_team_mock),
    ):
        # Tester la fonction et vérifier qu'elle lève une exception
        with pytest.raises(HTTPException) as exc_info:
            await check_team_admin(
                team_id=test_team.id, db=mock_db_session, current_user=test_user
            )

        # Vérifier que l'exception a le bon statut HTTP et le bon message
        assert exc_info.value.status_code == status.HTTP_403_FORBIDDEN
        assert (
            "Vous devez être administrateur de l'équipe pour effectuer cette action"
            in str(exc_info.value.detail)
        )
