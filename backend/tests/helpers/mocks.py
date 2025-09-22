"""Mock objects and helpers for testing."""

from typing import Any, Dict, List, Optional, Union
from unittest.mock import AsyncMock, MagicMock, patch

from httpx import Response


def mock_http_response(
    status_code: int = 200,
    json_data: Optional[Union[Dict, List]] = None,
    text: str = "",
    headers: Optional[Dict[str, str]] = None,
) -> Response:
    """Create a mock HTTP response.

    Args:
        status_code: HTTP status code
        json_data: JSON response data
        text: Response text
        headers: Response headers

    Returns:
        A mock Response object
    """
    response = Response(
        status_code=status_code,
        json=json_data or {},
        text=text,
        headers=headers or {},
    )

    if json_data is not None:
        response.json = MagicMock(return_value=json_data)

    return response


def mock_async_context_manager(result: Any = None, exception: Exception = None):
    """Create a mock async context manager.

    Args:
        result: Value to return when entering the context
        exception: Exception to raise when entering the context

    Returns:
        A mock async context manager
    """
    mock = AsyncMock()

    if exception:
        mock.__aenter__.side_effect = exception
    else:
        mock.__aenter__.return_value = result or AsyncMock()

    mock.__aexit__.return_value = None
    return mock


class MockRedis:
    """Mock Redis client for testing."""

    def __init__(self):
        self.data = {}
        self.expirations = {}

    async def get(self, key: str) -> Optional[bytes]:
        """Get a value from the mock Redis store."""
        return self.data.get(key)

    async def set(
        self,
        key: str,
        value: Any,
        ex: Optional[int] = None,
        px: Optional[int] = None,
        nx: bool = False,
        xx: bool = False,
    ) -> bool:
        """Set a value in the mock Redis store."""
        if nx and key in self.data:
            return False
        if xx and key not in self.data:
            return False

        self.data[key] = value

        if ex is not None:
            self.expirations[key] = ex

        return True

    async def delete(self, key: str) -> int:
        """Delete a key from the mock Redis store."""
        if key in self.data:
            del self.data[key]
            if key in self.expirations:
                del self.expirations[key]
            return 1
        return 0

    async def exists(self, key: str) -> int:
        """Check if a key exists in the mock Redis store."""
        return 1 if key in self.data else 0

    async def expire(self, key: str, time: int) -> bool:
        """Set a key's time to live in seconds."""
        if key in self.data:
            self.expirations[key] = time
            return True
        return False


class MockAIOKafkaProducer:
    """Mock AIOKafka producer for testing."""

    def __init__(self):
        self.messages = []
        self.started = False
        self.stopped = False

    async def start(self):
        """Start the mock producer."""
        self.started = True

    async def stop(self):
        """Stop the mock producer."""
        self.stopped = True

    async def send_and_wait(self, topic: str, value: Any, key: Any = None):
        """Send a message to the mock producer."""
        self.messages.append({"topic": topic, "key": key, "value": value})
        return MagicMock()

    def __aenter__(self):
        """Async context manager entry."""
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.stop()


class MockAIOKafkaConsumer:
    """Mock AIOKafka consumer for testing."""

    def __init__(self, *topics):
        self.topics = topics
        self.messages = []
        self.stopped = False

    async def start(self):
        """Start the mock consumer."""

    async def stop(self):
        """Stop the mock consumer."""
        self.stopped = True

    def __aiter__(self):
        """Async iterator implementation."""
        return self

    async def __anext__(self):
        """Get the next message."""
        if not self.messages:
            raise StopAsyncIteration
        return self.messages.pop(0)

    def add_message(self, message: Dict):
        """Add a message to the mock consumer."""
        self.messages.append(message)

    def __aenter__(self):
        """Async context manager entry."""
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.stop()


def mock_coroutine(return_value=None, exception=None):
    """Create a mock coroutine.

    Args:
        return_value: Value to return when awaited
        exception: Exception to raise when awaited

    Returns:
        A mock coroutine
    """

    async def coro(*args, **kwargs):
        if exception:
            raise exception
        return return_value

    return coro


def patch_aiohttp_session(mock_responses: Optional[Dict[str, Any]] = None):
    """Patch aiohttp.ClientSession for testing.

    Args:
        mock_responses: Dictionary mapping URLs to mock responses

    Returns:
        A context manager that patches aiohttp.ClientSession
    """
    mock_responses = mock_responses or {}

    async def mock_request(self, method, url, **kwargs):
        if url in mock_responses:
            response = mock_responses[url]
            if isinstance(response, Exception):
                raise response
            return response
        return mock_http_response(status_code=404, text="Not Found")

    return patch("aiohttp.ClientSession._request", new=mock_request)
