"""Unit tests for the WebhookService."""

import pytest
import hmac
import hashlib
import json
from unittest.mock import patch, MagicMock, AsyncMock
from datetime import datetime, timezone, timedelta

import httpx
from sqlalchemy.orm import Session

from app.services.webhook_service import WebhookService, MAX_RETRIES
from app.models.webhook import Webhook
from app.schemas.webhook import WebhookCreate, WebhookUpdate

pytestmark = pytest.mark.asyncio


@pytest.fixture
def mock_db_session():
    """Fixture for a mock SQLAlchemy session."""
    session = MagicMock(spec=Session)
    session.query.return_value.filter.return_value.all.return_value = []
    session.query.return_value.filter.return_value.first.return_value = None
    session.query.return_value.filter.return_value.offset.return_value.limit.return_value.all.return_value = []
    return session


class TestWebhookService:
    """Test suite for WebhookService."""

    def test_create_webhook(self, mock_db_session: MagicMock):
        """Test creating a new webhook."""
        webhook_in = WebhookCreate(url="https://example.com/hook", event_types=["build.create"])
        user_id = 1
        mock_webhook = MagicMock()
        mock_db_session.add.return_value = mock_webhook

        with patch("app.services.webhook_service.generate_secret_key", return_value="test_secret"):
            with patch("app.models.webhook.Webhook") as mock_webhook_cls:
                mock_webhook_instance = MagicMock()
                mock_webhook_cls.return_value = mock_webhook_instance

                result = WebhookService.create_webhook(mock_db_session, webhook_in, user_id)

                # Check Webhook was instantiated with correct parameters
                mock_webhook_cls.assert_called_once_with(
                    url=str(webhook_in.url),
                    secret="test_secret",
                    event_types=webhook_in.event_types,
                    is_active=webhook_in.is_active,
                    user_id=user_id,
                )

                # Check session methods were called
                mock_db_session.add.assert_called_once_with(mock_webhook_instance)
                mock_db_session.commit.assert_called_once()
                mock_db_session.refresh.assert_called_once_with(mock_webhook_instance)

                # Check the result is our webhook instance
                assert result == mock_webhook_instance

    def test_generate_signature(self):
        """Test HMAC signature generation."""
        secret = "my_super_secret"
        payload = b'{"key": "value"}'
        expected_signature = hmac.new(secret.encode(), msg=payload, digestmod=hashlib.sha256).hexdigest()

        signature = WebhookService.generate_signature(secret, payload)
        assert signature == expected_signature

    async def test_send_single_webhook_success(self):
        """Test sending a single webhook successfully."""
        mock_client = AsyncMock(spec=httpx.AsyncClient)
        mock_response = MagicMock(spec=httpx.Response)
        mock_response.status_code = 200
        mock_client.post.return_value = mock_response

        webhook = Webhook(
            id=1,
            url="https://example.com/hook",
            secret="test_secret",
            is_active=True,
            event_types=["build.create"],
            user_id=1,
            created_at=datetime.now(timezone.utc),
        )
        event_type = "build.create"
        payload_json = b'{"data": "test"}'

        await WebhookService._send_single_webhook(mock_client, webhook, event_type, payload_json)

        mock_client.post.assert_awaited_once()
        args, kwargs = mock_client.post.await_args
        assert args[0] == str(webhook.url)
        assert kwargs["content"] == payload_json
        assert "X-Webhook-Signature" in kwargs["headers"]
        mock_response.raise_for_status.assert_called_once()

    async def test_send_single_webhook_failure_with_retry(self):
        """Test that sending a webhook fails after multiple retries and deactivates the webhook."""
        mock_client = AsyncMock(spec=httpx.AsyncClient)
        # Simulate a persistent server error
        mock_client.post.side_effect = httpx.HTTPStatusError(
            "Server Error", request=MagicMock(), response=MagicMock(status_code=500)
        )

        webhook = Webhook(
            id=1,
            url="https://example.com/hook",
            secret="test_secret",
            is_active=True,
            event_types=["build.create"],
            user_id=1,
            created_at=datetime.now(timezone.utc),
        )
        event_type = "build.create"
        payload_json = b'{"data": "test"}'

        # The function should handle the exception and not raise it
        await WebhookService._send_single_webhook(mock_client, webhook, event_type, payload_json)

        # Verify it was called MAX_RETRIES times
        assert mock_client.post.await_count == MAX_RETRIES
        # Verify the webhook is marked as inactive
        assert webhook.is_active is False

    async def test_dispatch_webhook(self, mock_db_session: MagicMock):
        """Test dispatching an event to multiple webhooks."""
        event_type = "build.create"

        # Create test webhooks
        webhook1 = Webhook(
            id=1,
            url="https://example.com/hook1",
            secret="secret1",
            event_types=["build.create"],
            is_active=True,
            user_id=1,
            created_at=datetime.now(timezone.utc),
        )
        webhook2 = Webhook(
            id=2,
            url="https://example.com/hook2",
            secret="secret2",
            event_types=["build.update"],
            is_active=True,
            user_id=1,
            created_at=datetime.now(timezone.utc),
        )

        # Mock the query to return our test webhooks
        mock_db_session.query.return_value.filter.return_value.all.return_value = [webhook1, webhook2]

        # Mock the async client
        mock_client = AsyncMock(spec=httpx.AsyncClient)
        mock_response = MagicMock(spec=httpx.Response)
        mock_response.status_code = 200
        mock_client.post.return_value = mock_response

        # Create test payload
        payload = {"event": "test"}

        # Patch the async client and run the test
        with patch("httpx.AsyncClient", return_value=mock_client) as mock_async_client:
            await WebhookService.dispatch_webhook(mock_db_session, event_type, payload)

            # Verify the client was created and closed
            mock_async_client.assert_called_once()
            mock_client.__aenter__.assert_awaited_once()
            mock_client.__aexit__.assert_awaited_once()

            # Verify webhook1 was called (matching event type) but not webhook2
            assert mock_client.post.await_count == 1
            args, kwargs = mock_client.post.await_args
            assert str(webhook1.url) in str(args[0])
            assert kwargs["content"] == json.dumps(payload).encode("utf-8")
            assert "X-Webhook-Signature" in kwargs["headers"]
        payload = {"build_id": 123, "name": "Test Build"}
        user_id = 1

        # Mock webhooks subscribed to the event
        webhook1 = Webhook(
            id=1, url="https://site1.com/hook", secret="secret1", event_types=[event_type], is_active=True
        )
        webhook2 = Webhook(
            id=2, url="https://site2.com/hook", secret="secret2", event_types=[event_type], is_active=True
        )

        # Mock the database query to return these webhooks
        mock_query = MagicMock()
        mock_query.filter.return_value.all.return_value = [webhook1, webhook2]
        mock_db_session.query.return_value = mock_query

        # Patch the underlying send function to avoid actual HTTP calls
        with patch(
            "app.services.webhook_service.WebhookService._send_single_webhook", new_callable=AsyncMock
        ) as mock_send:
            await WebhookService.dispatch_webhook(mock_db_session, event_type, payload, user_id)

            # Verify that the query was constructed correctly
            assert mock_db_session.query.call_count == 1

            # Verify that _send_single_webhook was called for each webhook
            assert mock_send.call_count == 2

            # Check the call arguments for one of the calls
            call_args = mock_send.call_args_list[0].args
            sent_webhook = call_args[1]
            sent_payload = call_args[3]

            assert sent_webhook.id in [webhook1.id, webhook2.id]
            assert json.loads(sent_payload) == payload

    async def test_dispatch_webhook_no_subscribers(self, mock_db_session: MagicMock):
        """Test dispatching an event with no subscribed webhooks."""
        # Mock the database query to return an empty list
        mock_query = MagicMock()
        mock_query.filter.return_value.all.return_value = []
        mock_db_session.query.return_value = mock_query

        with patch(
            "app.services.webhook_service.WebhookService._send_single_webhook", new_callable=AsyncMock
        ) as mock_send:
            await WebhookService.dispatch_webhook(mock_db_session, "some.event", {}, 1)

            # Ensure no send attempts were made
            mock_send.assert_not_called()

    async def test_dispatch_webhook_serialization_error(self, mock_db_session: MagicMock):
        """Test that dispatching fails gracefully on payload serialization error."""
        # A complex object that json.dumps can't handle by default
        unserializable_payload = {"time": datetime.now()}

        webhook1 = Webhook(
            id=1, url="https://site1.com/hook", secret="secret1", event_types=["test.event"], is_active=True
        )
        mock_query = MagicMock()
        mock_query.filter.return_value.all.return_value = [webhook1]
        mock_db_session.query.return_value = mock_query

        # Patch json.dumps to simulate the error
        with patch("json.dumps", side_effect=TypeError("Test serialization error")):
            with patch(
                "app.services.webhook_service.WebhookService._send_single_webhook", new_callable=AsyncMock
            ) as mock_send:
                await WebhookService.dispatch_webhook(mock_db_session, "test.event", unserializable_payload, 1)

                # The service should log the error and not attempt to send anything
                mock_send.assert_not_called()

    async def test_send_single_webhook_does_not_retry_on_4xx_error(self):
        """Test that client errors (4xx) are not retried."""
        mock_client = AsyncMock(spec=httpx.AsyncClient)
        # Simulate a client error (e.g., 400 Bad Request)
        mock_client.post.side_effect = httpx.HTTPStatusError(
            "Bad Request", request=MagicMock(), response=MagicMock(status_code=400)
        )

        webhook = Webhook(
            id=1,
            url="https://example.com/hook",
            secret="test_secret",
            is_active=True,
            event_types=["build.create"],
            user_id=1,
            created_at=datetime.now(timezone.utc),
        )
        event_type = "build.create"
        payload_json = b'{"data": "test"}'

        await WebhookService._send_single_webhook(mock_client, webhook, event_type, payload_json)

        # Verify it was called only once
        assert mock_client.post.await_count == 1
        # Webhook should be disabled on persistent client error
        assert webhook.is_active is False

    def test_get_webhook(self, mock_db_session: MagicMock):
        """Test getting a webhook by ID and user ID."""
        # Setup test data
        webhook_id = 1
        user_id = 1

        # Create a test webhook
        test_webhook = Webhook(
            id=webhook_id,
            url="https://example.com/hook",
            secret="test_secret",
            event_types=["test.event"],
            is_active=True,
            user_id=user_id,
            created_at=datetime.now(timezone.utc),
        )

        # Mock the query to return our test webhook
        mock_db_session.query.return_value.filter.return_value.first.return_value = test_webhook

        # Call the method
        result = WebhookService.get_webhook(mock_db_session, webhook_id, user_id)

        # Assertions
        assert result == test_webhook

        # Verify the query was built correctly
        mock_db_session.query.assert_called_once_with(Webhook)

        # Verify the filter was called with the correct conditions
        filter_call = mock_db_session.query.return_value.filter
        filter_call.assert_called_once()

        # Verify first() was called to get a single result
        filter_call.return_value.first.assert_called_once()

    def test_get_webhooks(self, mock_db_session: MagicMock):
        """Test getting webhooks for a user with pagination."""
        # Setup test data
        user_id = 1
        skip = 0
        limit = 10

        # Create test webhooks
        test_webhooks = [
            Webhook(
                id=1,
                url="https://example.com/hook1",
                secret="secret1",
                event_types=["test.event1"],
                is_active=True,
                user_id=user_id,
                created_at=datetime.now(timezone.utc),
            ),
            Webhook(
                id=2,
                url="https://example.com/hook2",
                secret="secret2",
                event_types=["test.event2"],
                is_active=True,
                user_id=user_id,
                created_at=datetime.now(timezone.utc) - timedelta(days=1),
            ),
        ]

        # Mock the query to return our test webhooks
        mock_db_session.query.return_value.filter.return_value.offset.return_value.limit.return_value.all.return_value = (
            test_webhooks
        )

        # Call the method
        result = WebhookService.get_webhooks(mock_db_session, user_id, skip=skip, limit=limit)

        # Assertions
        assert result == test_webhooks

        # Verify the query was built correctly
        mock_db_session.query.assert_called_once_with(Webhook)

        # Verify the filter was called with the user_id condition
        filter_call = mock_db_session.query.return_value.filter
        filter_call.assert_called_once()

        # Verify pagination was applied
        offset_call = filter_call.return_value.offset
        offset_call.assert_called_once_with(skip)

        limit_call = offset_call.return_value.limit
        limit_call.assert_called_once_with(limit)

        # Verify all() was called to get the results
        limit_call.return_value.all.assert_called_once()

    def test_update_webhook(self, mock_db_session: MagicMock):
        """Test updating a webhook."""
        # Setup test data
        webhook_id = 1
        user_id = 1

        # Create an update object with some changes
        webhook_in = WebhookUpdate(
            url="https://updated.example.com/hook", event_types=["updated.event"], is_active=False
        )

        # Create a test webhook that will be updated
        test_webhook = Webhook(
            id=webhook_id,
            url="https://example.com/original",
            secret="test_secret",
            event_types=["original.event"],
            is_active=True,
            user_id=user_id,
            created_at=datetime.now(timezone.utc) - timedelta(days=1),
        )

        # Mock the query to return our test webhook
        mock_db_session.query.return_value.filter.return_value.first.return_value = test_webhook

        # Call the method
        result = WebhookService.update_webhook(mock_db_session, webhook_id, user_id, webhook_in)

        # Assertions
        assert result == test_webhook

        # Verify the webhook was updated with new values
        assert test_webhook.url == str(webhook_in.url)
        assert test_webhook.event_types == webhook_in.event_types
        assert test_webhook.is_active == webhook_in.is_active

        # Verify the session was used correctly
        mock_db_session.add.assert_called_once_with(test_webhook)
        mock_db_session.commit.assert_called_once()
        mock_db_session.refresh.assert_called_once_with(test_webhook)

    async def test_dispatch_webhook_serialization_error(self, mock_db_session: MagicMock):
        """Test handling of serialization errors during webhook dispatch."""
        # Create a test webhook
        webhook = Webhook(
            id=1,
            url="https://example.com/hook",
            secret="test_secret",
            event_types=["test.event"],
            is_active=True,
            user_id=1,
            created_at=datetime.now(timezone.utc),
        )
        mock_db_session.query.return_value.filter.return_value.all.return_value = [webhook]

        # Create a payload with unserializable data
        class Unserializable:
            pass

        # Mock the async client
        mock_client = AsyncMock(spec=httpx.AsyncClient)

        with patch("httpx.AsyncClient", return_value=mock_client) as mock_async_client:
            with pytest.raises(TypeError):
                await WebhookService.dispatch_webhook(
                    mock_db_session, "test.event", {"unserializable": Unserializable()}
                )

            # Verify the client was properly cleaned up even on error
            mock_async_client.assert_called_once()
            mock_client.__aenter__.assert_awaited_once()
            mock_client.__aexit__.assert_awaited_once()
