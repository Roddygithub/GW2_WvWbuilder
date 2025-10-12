"""Comprehensive unit tests for the WebhookService."""

import pytest
import pytest_asyncio
import json
from unittest.mock import patch, MagicMock, AsyncMock, call

from sqlalchemy.orm import Session

from app.services.webhook_service import WebhookService
from app.models.webhook import Webhook
from app.schemas.webhook import WebhookCreate, WebhookUpdate
from app.core.exceptions import ServiceUnavailableException as WebhookDeliveryError

pytestmark = pytest.mark.asyncio


class TestWebhookService:
    """Test suite for WebhookService."""

    @pytest.fixture
    def mock_db(self):
        """Fixture for a mock database session."""
        return MagicMock(spec=Session)

    @pytest.fixture
    def sample_webhook_data(self):
        """Sample webhook data for testing."""
        return {
            "url": "https://example.com/webhook",
            "event_types": ["build.created", "deployment.started"],
            "is_active": True,
            "secret": "test_secret_123",
        }

    def test_create_webhook(self, mock_db, sample_webhook_data):
        """Test creating a new webhook."""
        # Arrange
        webhook_in = WebhookCreate(**sample_webhook_data)
        user_id = 1

        with patch("app.services.webhook_service.generate_secret_key", return_value=sample_webhook_data["secret"]):
            # Act
            result = WebhookService.create_webhook(mock_db, webhook_in, user_id)

            # Assert
            assert result.url == sample_webhook_data["url"]
            assert result.user_id == user_id
            assert result.secret == sample_webhook_data["secret"]
            assert result.event_types == sample_webhook_data["event_types"]
            mock_db.add.assert_called_once()
            mock_db.commit.assert_called_once()
            mock_db.refresh.assert_called_once()

    @pytest.mark.parametrize(
        "secret,payload,expected",
        [
            ("secret", b'{"test": "data"}', "3dca279e801a85c6c3b3bcccbde6d5c9cbb8f7aef8b7f0c7a8b3f8e9d0a1b2c3"),
            ("", b"{}", "5f70bf18a0880070e7368c8b1a9f2dcd6324cff400b9f9d3a769626e2ada9345"),
        ],
    )
    def test_generate_signature(self, secret, payload, expected):
        """Test HMAC signature generation with various inputs."""
        result = WebhookService.generate_signature(secret, payload)
        assert result == expected

    @pytest.mark.asyncio
    async def test_send_webhook_success(self, sample_webhook_data):
        """Test successful webhook delivery."""
        # Arrange
        webhook = Webhook(**sample_webhook_data, id=1, user_id=1)
        event_type = "build.created"
        payload = {"build_id": 123, "status": "success"}

        mock_response = AsyncMock()
        mock_response.status_code = 200

        with patch("httpx.AsyncClient.post", new_callable=AsyncMock) as mock_post:
            mock_post.return_value = mock_response

            # Act
            await WebhookService.send_webhook(webhook, event_type, payload)

            # Assert
            mock_post.assert_awaited_once()
            args, kwargs = mock_post.call_args
            assert args[0] == webhook.url
            assert kwargs["headers"]["X-Webhook-Event"] == event_type
            assert "X-Webhook-Signature" in kwargs["headers"]
            assert json.loads(kwargs["content"]) == payload

    @pytest.mark.asyncio
    async def test_send_webhook_retry_on_failure(self, sample_webhook_data):
        """Test webhook delivery with retries on failure."""
        # Arrange
        webhook = Webhook(**sample_webhook_data, id=1, user_id=1)
        event_type = "deployment.started"
        payload = {"deployment_id": 456}

        # Mock to fail twice then succeed
        mock_response = AsyncMock()
        mock_response.status_code = 500

        success_response = AsyncMock()
        success_response.status_code = 200

        with patch("httpx.AsyncClient.post", new_callable=AsyncMock) as mock_post:
            mock_post.side_effect = [
                Exception("Connection error"),  # First attempt fails
                mock_response,  # Second attempt returns 500
                success_response,  # Third attempt succeeds
            ]

            # Act & Assert (should not raise)
            await WebhookService.send_webhook(webhook, event_type, payload, max_retries=3, retry_delay=0.1)

            # Should have been called 3 times (initial + 2 retries)
            assert mock_post.await_count == 3

    @pytest.mark.asyncio
    async def test_send_webhook_all_retries_fail(self, sample_webhook_data):
        """Test webhook delivery when all retries fail."""
        # Arrange
        webhook = Webhook(**sample_webhook_data, id=1, user_id=1)

        with patch("httpx.AsyncClient.post", new_callable=AsyncMock) as mock_post:
            mock_post.side_effect = Exception("Connection failed")

            # Act & Assert
            with pytest.raises(WebhookDeliveryError) as exc_info:
                await WebhookService.send_webhook(webhook, "test.event", {}, max_retries=2, retry_delay=0.1)

            assert "Failed after 3 attempts" in str(exc_info.value)
            assert mock_post.await_count == 3

    def test_verify_webhook_signature(self, sample_webhook_data):
        """Test webhook signature verification."""
        # Arrange
        secret = "test_secret_123"
        payload = b'{"test": "data"}'
        signature = WebhookService.generate_signature(secret, payload)

        # Act & Assert
        assert WebhookService.verify_webhook_signature(secret, payload, signature) is True
        assert WebhookService.verify_webhook_signature("wrong_secret", payload, signature) is False
        assert WebhookService.verify_webhook_signature(secret, b'{"different": "data"}', signature) is False

    def test_update_webhook(self, mock_db, sample_webhook_data):
        """Test updating a webhook."""
        # Arrange
        webhook = Webhook(**sample_webhook_data, id=1, user_id=1)
        update_data = WebhookUpdate(url="https://new-url.com/webhook", event_types=["new.event"], is_active=False)

        mock_db.query.return_value.filter.return_value.first.return_value = webhook

        # Act
        updated = WebhookService.update_webhook(mock_db, 1, update_data)

        # Assert
        assert updated.url == update_data.url
        assert updated.event_types == update_data.event_types
        assert updated.is_active == update_data.is_active
        mock_db.commit.assert_called_once()
        mock_db.refresh.assert_called_once_with(updated)

    def test_delete_webhook(self, mock_db, sample_webhook_data):
        """Test deleting a webhook."""
        # Arrange
        webhook = Webhook(**sample_webhook_data, id=1, user_id=1)
        mock_db.query.return_value.filter.return_value.first.return_value = webhook

        # Act
        WebhookService.delete_webhook(mock_db, 1)

        # Assert
        mock_db.delete.assert_called_once_with(webhook)
        mock_db.commit.assert_called_once()

    @pytest.mark.asyncio
    async def test_process_webhook_event(self, sample_webhook_data):
        """Test processing a webhook event with multiple subscribers."""
        # Arrange
        webhook1 = Webhook(
            id=1,
            url="https://webhook1.example.com",
            event_types=["build.created"],
            secret="secret1",
            is_active=True,
            user_id=1,
        )

        webhook2 = Webhook(
            id=2,
            url="https://webhook2.example.com",
            event_types=["build.created", "deployment.started"],
            secret="secret2",
            is_active=True,
            user_id=2,
        )

        mock_db = MagicMock()
        mock_db.query.return_value.filter.return_value.all.return_value = [webhook1, webhook2]

        event_type = "build.created"
        payload = {"build_id": 123}

        with patch("app.services.webhook_service.WebhookService.send_webhook", new_callable=AsyncMock) as mock_send:
            # Act
            await WebhookService.process_webhook_event(mock_db, event_type, payload)

            # Assert
            assert mock_send.await_count == 2  # Both webhooks should be notified

            # Verify the correct webhooks were called with correct parameters
            expected_calls = [
                call(webhook1, event_type, payload, None, 3, 1.0, 0.1),
                call(webhook2, event_type, payload, None, 3, 1.0, 0.1),
            ]
            mock_send.assert_has_awaits(expected_calls, any_order=True)
