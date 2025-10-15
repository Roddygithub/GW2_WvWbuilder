"""Custom exceptions for the application."""

from fastapi import status
from fastapi.exceptions import HTTPException


class CustomException(Exception):
    """Base class for custom exceptions with status code and detail."""

    def __init__(
        self,
        status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR,
        detail: str = "An unexpected error occurred",
        **kwargs,
    ) -> None:
        self.status_code = status_code
        self.detail = detail
        super().__init__(**kwargs)


class BaseAPIException(HTTPException):
    """Base exception for all API exceptions."""

    status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR
    detail: str = "An unexpected error occurred"

    def __init__(
        self, detail: str | None = None, status_code: int | None = None, **kwargs
    ) -> None:
        if status_code is not None:
            self.status_code = status_code
        if detail is not None:
            self.detail = detail
        super().__init__(status_code=self.status_code, detail=self.detail, **kwargs)


class NotFoundException(BaseAPIException):
    """Raised when a requested resource is not found."""

    status_code = status.HTTP_404_NOT_FOUND
    detail = "The requested resource was not found"


class UnauthorizedException(BaseAPIException):
    """Raised when authentication is required but not provided or invalid."""

    status_code = status.HTTP_401_UNAUTHORIZED
    detail = "Could not validate credentials"


class ForbiddenException(BaseAPIException):
    """Raised when the user doesn't have permission to access a resource."""

    status_code = status.HTTP_403_FORBIDDEN
    detail = "Not enough permissions"


class ValidationException(BaseAPIException):
    """Raised when request data is invalid."""

    status_code = status.HTTP_422_UNPROCESSABLE_ENTITY
    detail = "Validation error"


class ConflictException(BaseAPIException):
    """Raised when a conflict occurs (e.g., duplicate resource)."""

    status_code = status.HTTP_409_CONFLICT
    detail = "A conflict occurred with the current state of the resource"


class ServiceUnavailableException(BaseAPIException):
    """Raised when an external service is unavailable."""

    status_code = status.HTTP_503_SERVICE_UNAVAILABLE
    detail = "Service temporarily unavailable, please try again later"


class BadRequestException(BaseAPIException):
    """Raised when the request is malformed or invalid."""

    status_code = status.HTTP_400_BAD_REQUEST
    detail = "Bad request"


class RateLimitExceededException(BaseAPIException):
    """Raised when rate limit is exceeded."""

    status_code = status.HTTP_429_TOO_MANY_REQUESTS
    detail = "Rate limit exceeded"


class InactiveUserException(BaseAPIException):
    """Raised when trying to use an inactive user account."""

    status_code = status.HTTP_403_FORBIDDEN
    detail = "Inactive user"


# Export all exceptions for easy importing
# Authentication specific exceptions
class CredentialsException(UnauthorizedException):
    """Raised when authentication credentials are invalid or missing."""

    detail = "Could not validate credentials"
    headers = {"WWW-Authenticate": "Bearer"}


class InvalidTokenException(UnauthorizedException):
    """Raised when the provided token is invalid or expired."""

    detail = "Invalid or expired token"
    headers = {"WWW-Authenticate": "Bearer"}


class UserNotFoundException(NotFoundException):
    """Raised when a user is not found in the database."""

    detail = "User not found"


class NotSuperUserException(ForbiddenException):
    """Raised when a superuser permission is required but not met."""

    detail = "The user doesn't have enough privileges"


__all__ = [
    "BaseAPIException",
    "CredentialsException",
    "InvalidTokenException",
    "UserNotFoundException",
    "NotSuperUserException",
    "NotFoundException",
    "UnauthorizedException",
    "ForbiddenException",
    "ValidationException",
    "ConflictException",
    "ServiceUnavailableException",
    "BadRequestException",
    "RateLimitExceededException",
    "InactiveUserException",
]
