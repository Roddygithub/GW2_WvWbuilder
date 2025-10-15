"""Tests for core utilities."""

import pytest
from datetime import datetime
from app.core.utils import (
    generate_random_string,
    slugify,
    validate_url,
    format_datetime,
    parse_datetime,
    truncate_string,
)


def test_generate_random_string():
    """Test random string generation."""
    result = generate_random_string(10)
    assert len(result) == 10
    assert result.isalnum()
    
    # Test different lengths
    assert len(generate_random_string(5)) == 5
    assert len(generate_random_string(20)) == 20


def test_generate_random_string_uniqueness():
    """Test that random strings are unique."""
    str1 = generate_random_string(10)
    str2 = generate_random_string(10)
    assert str1 != str2


def test_slugify():
    """Test string slugification."""
    assert slugify("Hello World") == "hello-world"
    assert slugify("Test 123") == "test-123"
    assert slugify("CamelCase") == "camelcase"
    assert slugify("  spaces  ") == "spaces"


def test_slugify_special_chars():
    """Test slugify with special characters."""
    assert slugify("test@email.com") == "test-email-com"
    assert slugify("hello_world") == "hello-world"
    assert slugify("a/b/c") == "a-b-c"


def test_validate_url():
    """Test URL validation."""
    assert validate_url("https://example.com") is True
    assert validate_url("http://localhost:8000") is True
    assert validate_url("ftp://files.example.com") is True
    
    # Invalid URLs
    assert validate_url("not-a-url") is False
    assert validate_url("") is False
    assert validate_url("javascript:alert(1)") is False


def test_format_datetime():
    """Test datetime formatting."""
    dt = datetime(2025, 1, 15, 12, 30, 45)
    formatted = format_datetime(dt)
    assert isinstance(formatted, str)
    assert "2025" in formatted


def test_format_datetime_none():
    """Test formatting None datetime."""
    assert format_datetime(None) is None


def test_parse_datetime():
    """Test datetime parsing."""
    date_str = "2025-01-15T12:30:45"
    dt = parse_datetime(date_str)
    assert isinstance(dt, datetime)
    assert dt.year == 2025
    assert dt.month == 1
    assert dt.day == 15


def test_parse_datetime_invalid():
    """Test parsing invalid datetime string."""
    with pytest.raises((ValueError, TypeError)):
        parse_datetime("invalid-date")


def test_truncate_string():
    """Test string truncation."""
    text = "This is a long text that needs truncation"
    truncated = truncate_string(text, 20)
    assert len(truncated) <= 23  # 20 + "..."
    assert truncated.endswith("...")


def test_truncate_string_short():
    """Test truncating a short string."""
    text = "Short"
    truncated = truncate_string(text, 20)
    assert truncated == text
    assert not truncated.endswith("...")


def test_truncate_string_exact_length():
    """Test truncating at exact length."""
    text = "1234567890"
    truncated = truncate_string(text, 10)
    assert truncated == text
