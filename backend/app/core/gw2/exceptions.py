"""GW2 API Exceptions.

This module contains custom exceptions for the Guild Wars 2 API client.
"""


class GW2APIError(Exception):
    """Base exception for all GW2 API errors."""

    pass


class GW2APINotFoundError(GW2APIError):
    """Raised when a requested resource is not found (HTTP 404)."""

    pass


class GW2APIUnauthorizedError(GW2APIError):
    """Raised when authentication fails or is not provided (HTTP 401/403)."""

    pass


class GW2APIRateLimitError(GW2APIError):
    """Raised when the rate limit is exceeded (HTTP 429)."""

    pass


class GW2APIUnavailableError(GW2APIError):
    """Raised when the GW2 API is temporarily unavailable (HTTP 5xx)."""

    pass


class GW2APIValidationError(GW2APIError):
    """Raised when there's a validation error in the request (HTTP 400)."""

    pass
