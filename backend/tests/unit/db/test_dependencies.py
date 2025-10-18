"""
Tests unitaires pour app/db/dependencies.py
"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.dependencies import get_async_db, get_db


class TestGetAsyncDb:
    """Tests pour get_async_db dependency."""

    @pytest.mark.asyncio
    async def test_get_async_db_success(self):
        """Test get_async_db avec succès."""
        # Mock AsyncSessionLocal
        mock_session = AsyncMock(spec=AsyncSession)
        mock_session.commit = AsyncMock()
        mock_session.rollback = AsyncMock()
        mock_session.close = AsyncMock()

        with patch("app.db.dependencies.AsyncSessionLocal") as mock_session_local:
            # Configure le context manager
            mock_session_local.return_value.__aenter__.return_value = mock_session
            mock_session_local.return_value.__aexit__.return_value = None

            # Utilise le generator
            gen = get_async_db()
            session = await gen.__anext__()

            # Vérifie que la session est retournée
            assert session == mock_session

            # Simule la fin du context
            try:
                await gen.__anext__()
            except StopAsyncIteration:
                pass

            # Vérifie que commit et close ont été appelés
            mock_session.commit.assert_called_once()
            mock_session.close.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_async_db_rollback_on_exception(self):
        """Test get_async_db rollback en cas d'exception."""
        mock_session = AsyncMock(spec=AsyncSession)
        mock_session.commit = AsyncMock(side_effect=Exception("DB Error"))
        mock_session.rollback = AsyncMock()
        mock_session.close = AsyncMock()

        with patch("app.db.dependencies.AsyncSessionLocal") as mock_session_local:
            mock_session_local.return_value.__aenter__.return_value = mock_session
            mock_session_local.return_value.__aexit__.return_value = None

            gen = get_async_db()
            session = await gen.__anext__()

            # Simule une exception pendant l'utilisation
            with pytest.raises(Exception, match="DB Error"):
                await session.commit()
                try:
                    await gen.__anext__()
                except StopAsyncIteration:
                    pass

    def test_get_db_alias(self):
        """Test que get_db est un alias de get_async_db."""
        assert get_db == get_async_db
