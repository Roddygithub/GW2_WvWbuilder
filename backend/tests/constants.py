"""Constants and test data for API tests."""

from typing import Dict, Any


class Headers:
    """HTTP headers for API requests."""

    JSON = {"Content-Type": "application/json"}
    FORM = {"Content-Type": "application/x-www-form-urlencoded"}

    @staticmethod
    def with_auth(token: str) -> Dict[str, str]:
        """Return headers with Authorization token."""
        return {**Headers.JSON, "Authorization": f"Bearer {token}"}


class ExpectedErrors:
    """Expected error responses from the API."""

    INVALID_CREDENTIALS = {"detail": "Incorrect username or password"}
    INACTIVE_USER = {"detail": "Inactive user"}
    UNAUTHORIZED = {"detail": "Not authenticated"}
    FORBIDDEN = {"detail": "Not enough permissions"}
    NOT_FOUND = {"detail": "Not Found"}
    VALIDATION_ERROR = {"detail": []}  # Will be populated with validation errors


class TestData:
    """Test data for API tests."""

    # User data
    TEST_USER_EMAIL = "test@example.com"
    TEST_USER_PASSWORD = "testpassword"
    TEST_USER_FULL_NAME = "Test User"

    # Build data
    TEST_BUILD_NAME = "Test Build"
    TEST_BUILD_DESCRIPTION = "A test build"
    TEST_BUILD_IS_PUBLIC = True

    # Profession data
    TEST_PROFESSION_NAME = "Guardian"

    # Composition data
    TEST_COMPOSITION_TITLE = "Test Composition"
    TEST_COMPOSITION_DESCRIPTION = "A test composition"
    TEST_COMPOSITION_IS_PUBLIC = True

    @classmethod
    def user_create_data(cls, **overrides) -> Dict[str, Any]:
        """Generate user creation data with optional overrides."""
        data = {
            "email": cls.TEST_USER_EMAIL,
            "password": cls.TEST_USER_PASSWORD,
            "full_name": cls.TEST_USER_FULL_NAME,
        }
        data.update(overrides)
        return data

    @classmethod
    def user_login_data(cls, **overrides) -> Dict[str, str]:
        """Generate user login data with optional overrides."""
        data = {
            "username": cls.TEST_USER_EMAIL,
            "password": cls.TEST_USER_PASSWORD,
        }
        data.update(overrides)
        return data

    @classmethod
    def build_create_data(cls, **overrides) -> Dict[str, Any]:
        """Generate build creation data with optional overrides."""
        data = {
            "name": cls.TEST_BUILD_NAME,
            "description": cls.TEST_BUILD_DESCRIPTION,
            "is_public": cls.TEST_BUILD_IS_PUBLIC,
            "profession_name": cls.TEST_PROFESSION_NAME,
        }
        data.update(overrides)
        return data

    @classmethod
    def composition_create_data(cls, **overrides) -> Dict[str, Any]:
        """Generate composition creation data with optional overrides."""
        data = {
            "title": cls.TEST_COMPOSITION_TITLE,
            "description": cls.TEST_COMPOSITION_DESCRIPTION,
            "is_public": cls.TEST_COMPOSITION_IS_PUBLIC,
        }
        data.update(overrides)
        return data
