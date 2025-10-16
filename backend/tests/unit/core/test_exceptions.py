"""
Tests unitaires pour app/core/exceptions.py
"""
import pytest
from fastapi import status

from app.core.exceptions import (
    CustomException,
    BaseAPIException,
    NotFoundException,
    UnauthorizedException,
    ForbiddenException,
    ValidationException,
    ConflictException,
    ServiceUnavailableException,
    BadRequestException,
)


class TestCustomException:
    """Tests pour CustomException."""

    def test_custom_exception_default(self):
        """Test CustomException avec valeurs par défaut."""
        exc = CustomException()
        assert exc.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
        assert exc.detail == "An unexpected error occurred"

    def test_custom_exception_custom_values(self):
        """Test CustomException avec valeurs personnalisées."""
        exc = CustomException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Custom error message"
        )
        assert exc.status_code == status.HTTP_400_BAD_REQUEST
        assert exc.detail == "Custom error message"


class TestBaseAPIException:
    """Tests pour BaseAPIException."""

    def test_base_api_exception_default(self):
        """Test BaseAPIException avec valeurs par défaut."""
        exc = BaseAPIException()
        assert exc.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
        assert exc.detail == "An unexpected error occurred"

    def test_base_api_exception_custom_detail(self):
        """Test BaseAPIException avec detail personnalisé."""
        exc = BaseAPIException(detail="Custom detail")
        assert exc.detail == "Custom detail"
        assert exc.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR

    def test_base_api_exception_custom_status_code(self):
        """Test BaseAPIException avec status_code personnalisé."""
        exc = BaseAPIException(status_code=status.HTTP_400_BAD_REQUEST)
        assert exc.status_code == status.HTTP_400_BAD_REQUEST

    def test_base_api_exception_both_custom(self):
        """Test BaseAPIException avec detail et status_code personnalisés."""
        exc = BaseAPIException(
            detail="Custom error",
            status_code=status.HTTP_418_IM_A_TEAPOT
        )
        assert exc.detail == "Custom error"
        assert exc.status_code == status.HTTP_418_IM_A_TEAPOT


class TestNotFoundException:
    """Tests pour NotFoundException."""

    def test_not_found_exception_default(self):
        """Test NotFoundException avec valeurs par défaut."""
        exc = NotFoundException()
        assert exc.status_code == status.HTTP_404_NOT_FOUND
        assert exc.detail == "The requested resource was not found"

    def test_not_found_exception_custom_detail(self):
        """Test NotFoundException avec detail personnalisé."""
        exc = NotFoundException(detail="Build not found")
        assert exc.status_code == status.HTTP_404_NOT_FOUND
        assert exc.detail == "Build not found"


class TestUnauthorizedException:
    """Tests pour UnauthorizedException."""

    def test_unauthorized_exception_default(self):
        """Test UnauthorizedException avec valeurs par défaut."""
        exc = UnauthorizedException()
        assert exc.status_code == status.HTTP_401_UNAUTHORIZED
        assert exc.detail == "Could not validate credentials"

    def test_unauthorized_exception_custom_detail(self):
        """Test UnauthorizedException avec detail personnalisé."""
        exc = UnauthorizedException(detail="Token expired")
        assert exc.status_code == status.HTTP_401_UNAUTHORIZED
        assert exc.detail == "Token expired"


class TestForbiddenException:
    """Tests pour ForbiddenException."""

    def test_forbidden_exception_default(self):
        """Test ForbiddenException avec valeurs par défaut."""
        exc = ForbiddenException()
        assert exc.status_code == status.HTTP_403_FORBIDDEN
        assert exc.detail == "Not enough permissions"

    def test_forbidden_exception_custom_detail(self):
        """Test ForbiddenException avec detail personnalisé."""
        exc = ForbiddenException(detail="Admin access required")
        assert exc.status_code == status.HTTP_403_FORBIDDEN
        assert exc.detail == "Admin access required"


class TestValidationException:
    """Tests pour ValidationException."""

    def test_validation_exception_default(self):
        """Test ValidationException avec valeurs par défaut."""
        exc = ValidationException()
        assert exc.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
        assert exc.detail == "Validation error"

    def test_validation_exception_custom_detail(self):
        """Test ValidationException avec detail personnalisé."""
        exc = ValidationException(detail="Invalid email format")
        assert exc.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
        assert exc.detail == "Invalid email format"


class TestConflictException:
    """Tests pour ConflictException."""

    def test_conflict_exception_default(self):
        """Test ConflictException avec valeurs par défaut."""
        exc = ConflictException()
        assert exc.status_code == status.HTTP_409_CONFLICT
        assert exc.detail == "A conflict occurred with the current state of the resource"

    def test_conflict_exception_custom_detail(self):
        """Test ConflictException avec detail personnalisé."""
        exc = ConflictException(detail="Build name already exists")
        assert exc.status_code == status.HTTP_409_CONFLICT
        assert exc.detail == "Build name already exists"


class TestServiceUnavailableException:
    """Tests pour ServiceUnavailableException."""

    def test_service_unavailable_exception_default(self):
        """Test ServiceUnavailableException avec valeurs par défaut."""
        exc = ServiceUnavailableException()
        assert exc.status_code == status.HTTP_503_SERVICE_UNAVAILABLE
        assert exc.detail == "Service temporarily unavailable, please try again later"

    def test_service_unavailable_exception_custom_detail(self):
        """Test ServiceUnavailableException avec detail personnalisé."""
        exc = ServiceUnavailableException(detail="Database connection failed")
        assert exc.status_code == status.HTTP_503_SERVICE_UNAVAILABLE
        assert exc.detail == "Database connection failed"


class TestBadRequestException:
    """Tests pour BadRequestException."""

    def test_bad_request_exception_default(self):
        """Test BadRequestException avec valeurs par défaut."""
        exc = BadRequestException()
        assert exc.status_code == status.HTTP_400_BAD_REQUEST
        # Le detail par défaut devrait être défini dans la classe

    def test_bad_request_exception_custom_detail(self):
        """Test BadRequestException avec detail personnalisé."""
        exc = BadRequestException(detail="Invalid request parameters")
        assert exc.status_code == status.HTTP_400_BAD_REQUEST
        assert exc.detail == "Invalid request parameters"


class TestExceptionInheritance:
    """Tests pour vérifier l'héritage des exceptions."""

    def test_all_api_exceptions_inherit_from_base(self):
        """Test que toutes les exceptions API héritent de BaseAPIException."""
        exceptions = [
            NotFoundException,
            UnauthorizedException,
            ForbiddenException,
            ValidationException,
            ConflictException,
            ServiceUnavailableException,
            BadRequestException,
        ]
        for exc_class in exceptions:
            assert issubclass(exc_class, BaseAPIException)

    def test_exceptions_can_be_raised(self):
        """Test que les exceptions peuvent être levées."""
        with pytest.raises(NotFoundException):
            raise NotFoundException()

        with pytest.raises(UnauthorizedException):
            raise UnauthorizedException()

        with pytest.raises(ForbiddenException):
            raise ForbiddenException()
