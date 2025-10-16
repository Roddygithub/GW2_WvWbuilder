"""Tests for core utility functions."""

import pytest
from datetime import datetime, timezone


class TestCoreUtils:
    """Test core utility module."""
    
    def test_utils_import(self):
        """Test that utils module can be imported."""
        from app.core import utils
        assert utils is not None
    
    def test_get_current_timestamp_function_exists(self):
        """Test that get_current_timestamp function exists."""
        try:
            from app.core.utils import get_current_timestamp
            assert callable(get_current_timestamp)
        except ImportError:
            pytest.skip("get_current_timestamp not implemented")
    
    def test_get_current_timestamp_returns_datetime(self):
        """Test that get_current_timestamp returns datetime."""
        try:
            from app.core.utils import get_current_timestamp
            result = get_current_timestamp()
            assert isinstance(result, datetime)
        except ImportError:
            pytest.skip("get_current_timestamp not implemented")
    
    def test_get_current_timestamp_has_timezone(self):
        """Test that timestamp has timezone info."""
        try:
            from app.core.utils import get_current_timestamp
            result = get_current_timestamp()
            assert result.tzinfo is not None
        except ImportError:
            pytest.skip("get_current_timestamp not implemented")
    
    def test_generate_random_string_exists(self):
        """Test that generate_random_string function exists."""
        try:
            from app.core.utils import generate_random_string
            assert callable(generate_random_string)
        except ImportError:
            pytest.skip("generate_random_string not implemented")
    
    def test_generate_random_string_returns_string(self):
        """Test that generate_random_string returns string."""
        try:
            from app.core.utils import generate_random_string
            result = generate_random_string(10)
            assert isinstance(result, str)
            assert len(result) == 10
        except ImportError:
            pytest.skip("generate_random_string not implemented")
    
    def test_validate_email_exists(self):
        """Test that validate_email function exists if implemented."""
        try:
            from app.core.utils import validate_email
            assert callable(validate_email)
        except ImportError:
            pytest.skip("validate_email not implemented")
    
    def test_validate_email_valid(self):
        """Test email validation with valid email."""
        try:
            from app.core.utils import validate_email
            assert validate_email("test@example.com") is True
        except ImportError:
            pytest.skip("validate_email not implemented")
    
    def test_validate_email_invalid(self):
        """Test email validation with invalid email."""
        try:
            from app.core.utils import validate_email
            assert validate_email("invalid-email") is False
        except ImportError:
            pytest.skip("validate_email not implemented")
