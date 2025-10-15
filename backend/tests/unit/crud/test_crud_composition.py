import pytest
import pytest_asyncio
from unittest.mock import AsyncMock, MagicMock, patch
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud.crud_composition import CRUDComposition
from app.models import Composition, User, Tag
from app.schemas.composition import CompositionCreate

# Create an instance of the CRUD class for testing
composition_crud = CRUDComposition(Composition)


@pytest.fixture
def mock_user() -> User:
    """Fixture for a mock user."""
    return User(id=1, username="testuser")


@pytest.fixture
def mock_composition() -> Composition:
    """Fixture for a mock composition."""
    comp = Composition(id=1, name="Test Comp", created_by=1)
    comp.composition_tags = []  # Initialiser la relation avec une liste vide
    return comp


@pytest.fixture
def mock_tag() -> Tag:
    """Fixture for a mock tag."""
    return Tag(id=1, name="Test Tag")


# Helper function to create a mock result for SQLAlchemy queries
def create_mock_sql_result(return_value):
    mock_result = MagicMock()
    mock_result.scalars.return_value.first.return_value = return_value
    return mock_result


@patch(
    "app.crud.crud_composition.composition.invalidate_composition_cache",
    new_callable=AsyncMock,
)
class TestCRUDComposition:
    """Test suite for composition CRUD operations."""

    @pytest.mark.asyncio
    async def test_create_with_owner(self, mock_invalidate_cache, mock_user):
        """Test creating a composition with an owner."""
        db = AsyncMock(spec=AsyncSession)
        comp_in = CompositionCreate(name="New Comp")

        created_comp = await composition_crud.create_with_owner(
            db, obj_in=comp_in, user_id=mock_user.id
        )

        assert created_comp.name == comp_in.name
        assert created_comp.created_by == mock_user.id
        db.add.assert_called_once()
        db.commit.assert_awaited_once()
        db.refresh.assert_awaited_once()
        mock_invalidate_cache.assert_called_once_with(db, comp_id=created_comp.id)

    @pytest.mark.asyncio
    async def test_get_with_all_details(self, mock_invalidate_cache, mock_composition):
        """Test getting a composition with all its related details."""
        db = AsyncMock(spec=AsyncSession)
        db.execute.return_value = create_mock_sql_result(mock_composition)

        with patch("app.crud.crud_composition.settings.CACHE_ENABLED", False):
            result = await composition_crud.get_with_all_details(db, comp_id=1)

        assert result is not None
        assert result.id == mock_composition.id
        db.execute.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_add_tag(self, mock_invalidate_cache, mock_composition, mock_tag):
        """Test adding a tag to a composition."""
        db = AsyncMock(spec=AsyncSession)
        composition_id = 1
        tag_id = 1

        # Configurer le mock pour la requête de vérification
        mock_result = MagicMock()
        mock_result.first.return_value = None  # Aucune association existante
        db.execute.return_value = mock_result

        # Appeler la méthode à tester
        result = await composition_crud.add_tag(
            db, composition_id=composition_id, tag_id=tag_id
        )

        # Vérifier les appels
        assert result is True
        db.execute.assert_called_once()
        db.commit.assert_awaited_once()
        mock_invalidate_cache.assert_called_once_with(db, composition_id=composition_id)

    @pytest.mark.asyncio
    async def test_add_existing_tag(
        self, mock_invalidate_cache, mock_composition, mock_tag
    ):
        """Test that adding an existing tag does not cause issues."""
        db = AsyncMock(spec=AsyncSession)
        composition_id = 1
        tag_id = 1

        # Configurer le mock pour la requête de vérification
        mock_result = MagicMock()
        mock_result.first.return_value = True  # Association existante
        db.execute.return_value = mock_result

        # Appeler la méthode à tester
        result = await composition_crud.add_tag(
            db, composition_id=composition_id, tag_id=tag_id
        )

        # Vérifier les appels
        assert result is False
        db.execute.assert_called_once()
        db.commit.assert_not_called()
        mock_invalidate_cache.assert_not_called()

    @pytest.mark.asyncio
    async def test_remove_tag(self, mock_invalidate_cache, mock_composition, mock_tag):
        """Test removing a tag from a composition."""
        db = AsyncMock(spec=AsyncSession)
        composition_id = 1
        tag_id = 1

        # Configurer le mock pour la requête de vérification
        mock_result = MagicMock()
        mock_result.first.return_value = True  # Association existante
        db.execute.return_value = mock_result

        # Appeler la méthode à tester
        result = await composition_crud.remove_tag(
            db, composition_id=composition_id, tag_id=tag_id
        )

        # Vérifier les appels
        assert result is True
        db.execute.assert_called()  # Vérifie que execute a été appelé pour la suppression
        db.commit.assert_awaited_once()
        mock_invalidate_cache.assert_called_once_with(db, composition_id=composition_id)


@patch("app.crud.crud_composition.settings.CACHE_ENABLED", True)
@patch("app.crud.crud_composition.cache", new_callable=AsyncMock)
class TestCRUDCompositionCache:
    """Test suite for composition CRUD caching logic."""

    @pytest.mark.asyncio
    async def test_get_with_details_cache_hit(self, mock_cache, mock_composition):
        """Test cache hit when getting composition details."""
        db = AsyncMock(spec=AsyncSession)
        mock_cache.get.return_value = mock_composition

        result = await composition_crud.get_with_all_details(db, comp_id=1)

        assert result is not None
        mock_cache.get.assert_called_once_with("composition_details:1")
        db.execute.assert_not_called()

    @pytest.mark.asyncio
    async def test_get_with_details_cache_miss(self, mock_cache, mock_composition):
        """Test cache miss when getting composition details."""
        db = AsyncMock(spec=AsyncSession)
        mock_cache.get.return_value = None
        db.execute.return_value = create_mock_sql_result(mock_composition)

        result = await composition_crud.get_with_all_details(db, comp_id=1)

        assert result is not None
        mock_cache.get.assert_called_once_with("composition_details:1")
        db.execute.assert_awaited_once()
        mock_cache.set.assert_called_once()

    @pytest.mark.asyncio
    async def test_invalidate_composition_cache(self, mock_cache):
        """Test the cache invalidation method."""
        db = AsyncMock(spec=AsyncSession)
        await composition_crud.invalidate_composition_cache(db, comp_id=1)
        mock_cache.delete.assert_called_once_with("composition_details:1")
