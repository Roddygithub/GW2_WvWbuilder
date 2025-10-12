"""
Tests pour le module app.api.deps.

Ce module contient des tests pour les dépendances de l'API,
notamment l'authentification et l'autorisation.
"""

import pytest
import pytest_asyncio
from unittest.mock import AsyncMock, MagicMock, patch
from fastapi import HTTPException, status, Request
from jose import JWTError
from datetime import datetime, timedelta, timezone
from sqlalchemy.ext.asyncio import AsyncSession

# Enable async test support
pytestmark = pytest.mark.asyncio

# Import CRUD modules first to avoid circular imports

# Mock the deps module with patches
with (
    patch("app.crud.user_crud", autospec=True),
    patch("app.crud.team_crud", autospec=True),
    patch("app.crud.team_member_crud", autospec=True),
):

    # Now import the deps module
    from app.api.deps import (
        get_current_user,
        get_current_active_user,
        get_current_active_superuser,
        get_team_and_check_access,
        check_team_admin,
    )

# Import other dependencies
from app.core.config import settings
from app.core.exceptions import (
    CredentialsException,
    InactiveUserException,
    NotSuperUserException,
    ForbiddenException,
)
from app.models.team import Team as TeamModel

# Test data
TEST_USER_ID = 1
TEST_EMAIL = "test@example.com"
TEST_USERNAME = "testuser"
TEST_IS_SUPERUSER = False
TEST_IS_ACTIVE = True
TEST_TOKEN = "test_token"
TEST_TEAM_ID = 1
TEST_TEAM_NAME = "Test Team"


# Fixtures
@pytest_asyncio.fixture
async def mock_db_session():
    """Mock for async database session."""
    session = AsyncMock(spec=AsyncSession)
    session.scalar.return_value = None

    # Add commit and refresh methods
    session.commit = AsyncMock()
    session.refresh = AsyncMock()

    return session


@pytest.fixture
def create_test_user():
    """Crée un utilisateur de test."""

    def _create_test_user(
        user_id=TEST_USER_ID,
        email=TEST_EMAIL,
        username=TEST_USERNAME,
        is_superuser=TEST_IS_SUPERUSER,
        is_active=TEST_IS_ACTIVE,
    ):
        # Create a mock for the user
        user = MagicMock()
        user.id = user_id
        user.email = email
        user.username = username
        user.is_superuser = is_superuser
        user.is_active = is_active
        user.hashed_password = "hashed_password"

        # Mock the relationships that might be accessed
        user.roles = []
        user.role_associations = []
        user.teams = []
        user.team_associations = []
        user.compositions = []
        user.builds = []
        user.tokens = []
        user.owned_teams = []
        user.webhooks = []  # Add missing webhooks relationship

        return user

    return _create_test_user


@pytest.fixture
def create_test_team():
    """Crée une équipe de test."""

    def _create_test_team(team_id=TEST_TEAM_ID, name=TEST_TEAM_NAME, owner_id=1):
        team = MagicMock(spec=TeamModel)
        team.id = team_id
        team.name = name
        team.description = "Test team description"
        team.owner_id = owner_id
        team.is_active = True
        team.members = []
        return team

    return _create_test_team


# Tests pour get_current_user
@pytest.mark.asyncio
async def test_get_current_user_valid_token(mock_db_session, create_test_user):
    """Teste la récupération d'un utilisateur avec un token valide."""
    # Configuration du mock pour la base de données
    test_user = create_test_user()

    # Mock de la requête
    mock_request = MagicMock(spec=Request)

    # Mock pour user_crud.get
    with patch("app.api.deps.user_crud.get") as mock_crud_get, patch("app.api.deps.jwt.decode") as mock_jwt_decode:

        # Configuration des mocks
        mock_crud_get.return_value = test_user
        mock_jwt_decode.return_value = {
            "sub": str(TEST_USER_ID),
            "exp": (datetime.now(timezone.utc) + timedelta(minutes=30)).timestamp(),
        }

        # Appel de la fonction à tester
        result = await get_current_user(request=mock_request, token=TEST_TOKEN, db=mock_db_session)

        # Vérifications
        assert result == test_user
        mock_jwt_decode.assert_called_once_with(
            TEST_TOKEN, settings.SECRET_KEY, algorithms=[settings.JWT_ALGORITHM], options={"verify_aud": False}
        )
        mock_crud_get.assert_called_once_with(mock_db_session, id=TEST_USER_ID)


@pytest.mark.asyncio
async def test_get_current_user_invalid_token(mock_db_session):
    """Teste la gestion d'un token invalide."""
    # Mock de la requête
    mock_request = MagicMock(spec=Request)

    with patch("app.api.deps.jwt.decode") as mock_jwt_decode:
        mock_jwt_decode.side_effect = JWTError("Invalid token")

        with pytest.raises(CredentialsException) as exc_info:
            await get_current_user(request=mock_request, token="invalid_token", db=mock_db_session)

        assert exc_info.value.status_code == status.HTTP_401_UNAUTHORIZED
        assert "Could not validate credentials" in str(exc_info.value.detail)


# Tests pour get_current_active_user
@pytest.mark.asyncio
async def test_get_current_active_user_active(create_test_user):
    """Teste la récupération d'un utilisateur actif."""
    active_user = create_test_user(is_active=True)
    result = await get_current_active_user(current_user=active_user)
    assert result == active_user


@pytest.mark.asyncio
async def test_get_current_active_user_inactive(create_test_user):
    """Teste la tentative de récupération d'un utilisateur inactif."""
    inactive_user = create_test_user(is_active=False)

    with pytest.raises(InactiveUserException) as exc_info:
        await get_current_active_user(current_user=inactive_user)

    assert exc_info.value.status_code == status.HTTP_400_BAD_REQUEST
    assert "Inactive user" in str(exc_info.value.detail)


# Tests pour get_current_active_superuser
@pytest.mark.asyncio
async def test_get_current_active_superuser_valid(create_test_user):
    """Teste la récupération d'un superutilisateur valide."""
    superuser = create_test_user(is_superuser=True)
    result = await get_current_active_superuser(current_user=superuser)
    assert result == superuser


@pytest.mark.asyncio
async def test_get_current_active_superuser_not_superuser(create_test_user):
    """Teste la tentative de récupération d'un utilisateur non superutilisateur."""
    regular_user = create_test_user(is_superuser=False)

    with pytest.raises(NotSuperUserException) as exc_info:
        await get_current_active_superuser(current_user=regular_user)

    assert exc_info.value.status_code == status.HTTP_403_FORBIDDEN
    assert "The user doesn't have enough privileges" in str(exc_info.value.detail)


# Tests pour get_team_and_check_access
@pytest.mark.asyncio
async def test_get_team_and_check_access_owner(mock_db_session, create_test_user, create_test_team):
    """Teste l'accès à une équipe dont l'utilisateur est propriétaire."""
    # Créer un utilisateur et une équipe
    user = create_test_user(user_id=1)
    team = create_test_team(owner_id=user.id)

    # Configurer le mock pour retourner l'équipe
    with patch("app.api.deps.team_crud.get") as mock_team_get:
        mock_team_get.return_value = team

        # Appeler la fonction
        result_team, is_admin = await get_team_and_check_access(team_id=team.id, db=mock_db_session, current_user=user)

        # Vérifications
        assert result_team == team
        assert is_admin is True
        mock_team_get.assert_called_once_with(mock_db_session, id=team.id)


@pytest.mark.asyncio
async def test_get_team_and_check_access_team_member(mock_db_session, create_test_user, create_test_team):
    """Teste l'accès à une équipe dont l'utilisateur est membre."""
    # Créer un utilisateur, un propriétaire et une équipe
    owner = create_test_user(user_id=1)
    user = create_test_user(user_id=2)
    team = create_test_team(owner_id=owner.id)

    # Créer un mock pour le membre d'équipe
    team_member = MagicMock()
    team_member.user_id = user.id
    team_member.team_id = team.id
    team_member.is_admin = False

    # Configurer les mocks
    with (
        patch("app.api.deps.team_crud.get") as mock_team_get,
        patch("app.api.deps.team_member_crud.get_by_user_and_team") as mock_get_member,
    ):

        mock_team_get.return_value = team
        mock_get_member.return_value = team_member

        # Appeler la fonction
        result_team, is_admin = await get_team_and_check_access(team_id=team.id, db=mock_db_session, current_user=user)

        # Vérifications
        assert result_team == team
        assert is_admin is False
        mock_team_get.assert_called_once_with(mock_db_session, id=team.id)
        mock_get_member.assert_called_once_with(mock_db_session, user_id=user.id, team_id=team.id)


@pytest.mark.asyncio
async def test_check_team_admin_success(mock_db_session, create_test_user, create_test_team):
    """Teste la vérification d'un administrateur d'équipe valide."""
    # Créer un utilisateur et une équipe
    user = create_test_user(user_id=1)
    team = create_test_team(owner_id=user.id)

    # Configurer le mock pour retourner l'équipe
    with patch("app.api.deps.team_crud.get") as mock_team_get:
        mock_team_get.return_value = team

        # Appeler la fonction
        result_team = await check_team_admin(team_id=team.id, db=mock_db_session, current_user=user)

        # Vérifications
        assert result_team == team
        mock_team_get.assert_called_once_with(mock_db_session, id=team.id)


@pytest.mark.asyncio
async def test_check_team_admin_not_found(mock_db_session, create_test_user):
    """Teste la vérification d'une équipe qui n'existe pas."""
    user = create_test_user(user_id=1)

    # Configurer le mock pour retourner None (équipe non trouvée)
    with patch("app.api.deps.team_crud.get") as mock_team_get:
        mock_team_get.return_value = None

        # Appeler la fonction et vérifier qu'elle lève une exception
        with pytest.raises(HTTPException) as exc_info:
            await check_team_admin(team_id=999, db=mock_db_session, current_user=user)  # ID qui n'existe pas

        # Vérifications
        assert exc_info.value.status_code == status.HTTP_404_NOT_FOUND
        assert "Team not found" in str(exc_info.value.detail)
        mock_team_get.assert_called_once_with(mock_db_session, id=999)


# Tests pour la couverture des branches conditionnelles
@pytest.mark.asyncio
async def test_get_team_and_check_access_not_found(mock_db_session, create_test_user):
    """Teste l'accès à une équipe qui n'existe pas."""
    user = create_test_user(user_id=1)

    # Configurer le mock pour retourner None (équipe non trouvée)
    with patch("app.api.deps.team_crud.get") as mock_team_get:
        mock_team_get.return_value = None

        # Appeler la fonction et vérifier qu'elle lève une exception
        with pytest.raises(HTTPException) as exc_info:
            await get_team_and_check_access(team_id=999, db=mock_db_session, current_user=user)  # ID qui n'existe pas

        # Vérifications
        assert exc_info.value.status_code == status.HTTP_404_NOT_FOUND
        assert "Team not found" in str(exc_info.value.detail)
        mock_team_get.assert_called_once_with(mock_db_session, id=999)


@pytest.mark.asyncio
async def test_get_team_and_check_access_not_member(mock_db_session, create_test_user, create_test_team):
    """Teste l'accès à une équipe dont l'utilisateur n'est pas membre."""
    # Créer un utilisateur, un propriétaire et une équipe
    owner = create_test_user(user_id=1)
    user = create_test_user(user_id=2)
    team = create_test_team(owner_id=owner.id)

    # Configurer les mocks pour simuler que l'utilisateur n'est pas membre
    with (
        patch("app.api.deps.team_crud.get") as mock_team_get,
        patch("app.api.deps.team_member_crud.get_by_user_and_team") as mock_get_member,
    ):

        mock_team_get.return_value = team
        mock_get_member.return_value = None

        # Appeler la fonction et vérifier qu'elle lève une exception
        with pytest.raises(ForbiddenException) as exc_info:
            await get_team_and_check_access(team_id=team.id, db=mock_db_session, current_user=user)

        # Vérifications
        assert exc_info.value.status_code == status.HTTP_403_FORBIDDEN
        assert "Not enough permissions" in str(exc_info.value.detail)
        mock_team_get.assert_called_once_with(mock_db_session, id=team.id)
        mock_get_member.assert_called_once_with(mock_db_session, user_id=user.id, team_id=team.id)
