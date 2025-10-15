"""
Comprehensive tests for Webhook Service.
Tests for app/services/webhook_service.py to achieve 85%+ coverage.
"""

import pytest
import pytest_asyncio
from unittest.mock import AsyncMock, MagicMock, patch
from sqlalchemy.ext.asyncio import AsyncSession

from app.services.webhook_service import WebhookService, MAX_RETRIES
from app.models.webhook import Webhook
from app.schemas.webhook import WebhookCreate, WebhookUpdate


@pytest.fixture
def mock_db():
    """Create a mock database session."""
    db = AsyncMock(spec=AsyncSession)
    db.add = MagicMock()
    db.commit = AsyncMock()
    db.refresh = AsyncMock()
    db.execute = AsyncMock()
    return db


@pytest.fixture
def webhook_service(mock_db):
    """Create a WebhookService instance."""
    return WebhookService(db=mock_db)


@pytest.fixture
def sample_webhook_data():
    """Sample webhook data for testing."""
    return WebhookCreate(
        url="https://example.com/webhook",
        events=["build.created", "build.updated"],
        description="Test webhook",
    )


class TestWebhookServiceInit:
    """Test WebhookService initialization."""

    def test_init(self, mock_db):
        """Test service initialization."""
        service = WebhookService(db=mock_db)

        assert service.db == mock_db
        assert service.model == Webhook


class TestWebhookCreation:
    """Test webhook creation."""

    @pytest.mark.asyncio
    async def test_create_webhook_basic(
        self, webhook_service, mock_db, sample_webhook_data
    ):
        """Test creating a basic webhook."""
        user_id = 1

        with patch("os.urandom", return_value=b"test_secret"):
            await webhook_service.create_webhook(sample_webhook_data, user_id)

        assert mock_db.add.called
        assert mock_db.commit.called

    @pytest.mark.asyncio
    async def test_create_webhook_generates_secret(
        self, webhook_service, sample_webhook_data
    ):
        """Test that webhook creation generates a secret."""
        user_id = 1

        with patch("os.urandom", return_value=b"\x00" * 32) as mock_urandom:
            await webhook_service.create_webhook(sample_webhook_data, user_id)

            mock_urandom.assert_called_once_with(32)

    @pytest.mark.asyncio
    async def test_create_webhook_with_all_fields(self, webhook_service, mock_db):
        """Test creating webhook with all fields."""
        webhook_data = WebhookCreate(
            url="https://example.com/webhook",
            events=["build.created", "build.updated", "build.deleted"],
            description="Complete webhook",
            is_active=True,
        )
        user_id = 1

        with patch("os.urandom", return_value=b"test"):
            await webhook_service.create_webhook(webhook_data, user_id)

        assert mock_db.add.called


class TestWebhookRetrieval:
    """Test webhook retrieval methods."""

    @pytest.mark.asyncio
    async def test_get_webhook_by_id(self, webhook_service, mock_db):
        """Test getting webhook by ID."""
        webhook_id = 1
        mock_webhook = Webhook(id=webhook_id, url="https://example.com")

        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = mock_webhook
        mock_db.execute.return_value = mock_result

        await webhook_service.get_webhook(webhook_id)

        assert mock_db.execute.called

    @pytest.mark.asyncio
    async def test_get_webhook_nonexistent(self, webhook_service, mock_db):
        """Test getting non-existent webhook."""
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None
        mock_db.execute.return_value = mock_result

        webhook = await webhook_service.get_webhook(99999)

        assert webhook is None

    @pytest.mark.asyncio
    async def test_get_user_webhooks(self, webhook_service, mock_db):
        """Test getting all webhooks for a user."""
        user_id = 1
        mock_webhooks = [
            Webhook(id=1, url="https://example.com/1"),
            Webhook(id=2, url="https://example.com/2"),
        ]

        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = mock_webhooks
        mock_db.execute.return_value = mock_result

        await webhook_service.get_user_webhooks(user_id)

        assert mock_db.execute.called


class TestWebhookUpdate:
    """Test webhook update operations."""

    @pytest.mark.asyncio
    async def test_update_webhook(self, webhook_service, mock_db):
        """Test updating a webhook."""
        webhook_id = 1
        mock_webhook = Webhook(id=webhook_id, url="https://old.com")

        update_data = WebhookUpdate(url="https://new.com")

        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = mock_webhook
        mock_db.execute.return_value = mock_result

        await webhook_service.update_webhook(webhook_id, update_data)

        assert mock_db.commit.called

    @pytest.mark.asyncio
    async def test_update_webhook_events(self, webhook_service, mock_db):
        """Test updating webhook events."""
        webhook_id = 1
        mock_webhook = Webhook(id=webhook_id, events=["build.created"])

        update_data = WebhookUpdate(events=["build.created", "build.updated"])

        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = mock_webhook
        mock_db.execute.return_value = mock_result

        await webhook_service.update_webhook(webhook_id, update_data)

        assert mock_db.commit.called


class TestWebhookDeletion:
    """Test webhook deletion."""

    @pytest.mark.asyncio
    async def test_delete_webhook(self, webhook_service, mock_db):
        """Test deleting a webhook."""
        webhook_id = 1
        mock_webhook = Webhook(id=webhook_id)

        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = mock_webhook
        mock_db.execute.return_value = mock_result
        mock_db.delete = AsyncMock()

        await webhook_service.delete_webhook(webhook_id)

        assert mock_db.delete.called
        assert mock_db.commit.called

    @pytest.mark.asyncio
    async def test_delete_nonexistent_webhook(self, webhook_service, mock_db):
        """Test deleting non-existent webhook."""
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None
        mock_db.execute.return_value = mock_result

        result = await webhook_service.delete_webhook(99999)

        assert result is False


class TestWebhookDelivery:
    """Test webhook delivery functionality."""

    @pytest.mark.asyncio
    async def test_send_webhook_success(self, webhook_service):
        """Test successful webhook delivery."""
        webhook = Webhook(
            id=1,
            url="https://example.com/webhook",
            secret="test_secret",
            is_active=True,
        )
        payload = {"event": "build.created", "data": {"id": 1}}

        with patch("httpx.AsyncClient") as mock_client:
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.text = "OK"
            mock_client.return_value.__aenter__.return_value.post = AsyncMock(
                return_value=mock_response
            )

            result = await webhook_service.send_webhook(webhook, payload)

            assert result is True

    @pytest.mark.asyncio
    async def test_send_webhook_failure(self, webhook_service):
        """Test failed webhook delivery."""
        webhook = Webhook(
            id=1,
            url="https://example.com/webhook",
            secret="test_secret",
            is_active=True,
        )
        payload = {"event": "build.created"}

        with patch("httpx.AsyncClient") as mock_client:
            mock_response = MagicMock()
            mock_response.status_code = 500
            mock_client.return_value.__aenter__.return_value.post = AsyncMock(
                return_value=mock_response
            )

            result = await webhook_service.send_webhook(webhook, payload)

            assert result is False

    @pytest.mark.asyncio
    async def test_send_webhook_timeout(self, webhook_service):
        """Test webhook delivery timeout."""
        webhook = Webhook(id=1, url="https://example.com/webhook", secret="test_secret")
        payload = {"event": "test"}

        with patch("httpx.AsyncClient") as mock_client:
            mock_client.return_value.__aenter__.return_value.post = AsyncMock(
                side_effect=asyncio.TimeoutError()
            )

            result = await webhook_service.send_webhook(webhook, payload)

            assert result is False

    @pytest.mark.asyncio
    async def test_send_webhook_with_retry(self, webhook_service):
        """Test webhook delivery with retry logic."""
        webhook = Webhook(id=1, url="https://example.com/webhook", secret="test_secret")
        payload = {"event": "test"}

        with patch("httpx.AsyncClient") as mock_client:
            # First attempt fails, second succeeds
            mock_response_fail = MagicMock()
            mock_response_fail.status_code = 500
            mock_response_success = MagicMock()
            mock_response_success.status_code = 200

            mock_client.return_value.__aenter__.return_value.post = AsyncMock(
                side_effect=[mock_response_fail, mock_response_success]
            )

            result = await webhook_service.send_webhook_with_retry(webhook, payload)

            assert result is True


class TestSignatureGeneration:
    """Test webhook signature generation."""

    def test_generate_signature(self, webhook_service):
        """Test generating webhook signature."""
        secret = "test_secret"
        payload = {"event": "test", "data": {}}

        signature = webhook_service.generate_signature(secret, payload)

        assert signature is not None
        assert isinstance(signature, str)
        assert len(signature) > 0

    def test_generate_signature_consistency(self, webhook_service):
        """Test that signature generation is consistent."""
        secret = "test_secret"
        payload = {"event": "test"}

        sig1 = webhook_service.generate_signature(secret, payload)
        sig2 = webhook_service.generate_signature(secret, payload)

        assert sig1 == sig2

    def test_generate_signature_different_secrets(self, webhook_service):
        """Test that different secrets produce different signatures."""
        payload = {"event": "test"}

        sig1 = webhook_service.generate_signature("secret1", payload)
        sig2 = webhook_service.generate_signature("secret2", payload)

        assert sig1 != sig2


class TestWebhookValidation:
    """Test webhook validation."""

    @pytest.mark.asyncio
    async def test_validate_webhook_url(self, webhook_service):
        """Test webhook URL validation."""
        valid_url = "https://example.com/webhook"
        invalid_url = "not-a-url"

        assert webhook_service.validate_url(valid_url) is True
        assert webhook_service.validate_url(invalid_url) is False

    @pytest.mark.asyncio
    async def test_validate_webhook_events(self, webhook_service):
        """Test webhook events validation."""
        valid_events = ["build.created", "build.updated"]
        invalid_events = ["invalid.event"]

        assert webhook_service.validate_events(valid_events) is True
        assert webhook_service.validate_events(invalid_events) is False


class TestWebhookEventProcessing:
    """Test webhook event processing."""

    @pytest.mark.asyncio
    async def test_process_event(self, webhook_service, mock_db):
        """Test processing a webhook event."""
        event_type = "build.created"
        data = {"id": 1, "name": "Test Build"}

        mock_webhooks = [
            Webhook(
                id=1,
                url="https://example.com/1",
                events=["build.created"],
                is_active=True,
            ),
            Webhook(
                id=2,
                url="https://example.com/2",
                events=["build.updated"],
                is_active=True,
            ),
        ]

        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = mock_webhooks
        mock_db.execute.return_value = mock_result

        with patch.object(
            webhook_service, "send_webhook", new=AsyncMock(return_value=True)
        ):
            await webhook_service.process_event(event_type, data)

            # Should only send to webhook 1 (has build.created event)
            webhook_service.send_webhook.assert_called_once()

    @pytest.mark.asyncio
    async def test_process_event_no_matching_webhooks(self, webhook_service, mock_db):
        """Test processing event with no matching webhooks."""
        event_type = "build.deleted"
        data = {"id": 1}

        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = []
        mock_db.execute.return_value = mock_result

        with patch.object(
            webhook_service, "send_webhook", new=AsyncMock()
        ) as mock_send:
            await webhook_service.process_event(event_type, data)

            mock_send.assert_not_called()


class TestWebhookServiceEdgeCases:
    """Test edge cases and error handling."""

    @pytest.mark.asyncio
    async def test_inactive_webhook_not_triggered(self, webhook_service, mock_db):
        """Test that inactive webhooks are not triggered."""
        event_type = "build.created"
        data = {"id": 1}

        mock_webhooks = [
            Webhook(
                id=1,
                url="https://example.com",
                events=["build.created"],
                is_active=False,
            )
        ]

        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = mock_webhooks
        mock_db.execute.return_value = mock_result

        with patch.object(
            webhook_service, "send_webhook", new=AsyncMock()
        ) as mock_send:
            await webhook_service.process_event(event_type, data)

            mock_send.assert_not_called()

    @pytest.mark.asyncio
    async def test_webhook_with_empty_payload(self, webhook_service):
        """Test sending webhook with empty payload."""
        webhook = Webhook(id=1, url="https://example.com", secret="test")
        payload = {}

        with patch("httpx.AsyncClient") as mock_client:
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_client.return_value.__aenter__.return_value.post = AsyncMock(
                return_value=mock_response
            )

            result = await webhook_service.send_webhook(webhook, payload)

            assert result is True

    @pytest.mark.asyncio
    async def test_max_retries_exceeded(self, webhook_service):
        """Test that max retries are respected."""
        webhook = Webhook(id=1, url="https://example.com", secret="test")
        payload = {"event": "test"}

        with patch("httpx.AsyncClient") as mock_client:
            mock_response = MagicMock()
            mock_response.status_code = 500
            mock_client.return_value.__aenter__.return_value.post = AsyncMock(
                return_value=mock_response
            )

            result = await webhook_service.send_webhook_with_retry(
                webhook, payload, max_retries=MAX_RETRIES
            )

            # Should fail after max retries
            assert result is False
            assert (
                mock_client.return_value.__aenter__.return_value.post.call_count
                == MAX_RETRIES
            )
