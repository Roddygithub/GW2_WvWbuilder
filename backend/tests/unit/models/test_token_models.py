"""Tests for token models."""

import pytest
from datetime import datetime, timedelta
from pydantic import ValidationError

from app.models.token import Token, TokenPayload


def test_token_creation():
    """Test creating a token with valid data."""
    token_data = {"access_token": "test_access_token", "token_type": "bearer"}
    token = Token(**token_data)

    assert token.access_token == "test_access_token"
    assert token.token_type == "bearer"


def test_token_required_fields():
    """Test that required fields are enforced."""
    with pytest.raises(ValidationError):
        Token(access_token=None)  # type: ignore

    with pytest.raises(ValidationError):
        Token(access_token="token", token_type=None)  # type: ignore


def test_token_defaults():
    """Test default values for optional fields."""
    token = Token(access_token="test_token")
    assert token.token_type == "bearer"


def test_token_payload_creation():
    """Test creating a token payload with valid data."""
    now = datetime.utcnow()
    exp = now + timedelta(days=1)

    payload_data = {"sub": "123", "exp": exp, "iat": now, "is_superuser": False}

    payload = TokenPayload(**payload_data)

    assert payload.sub == "123"
    assert payload.exp == exp
    assert payload.iat == now
    assert payload.is_superuser is False


def test_token_payload_optional_fields():
    """Test that optional fields in token payload work as expected."""
    payload = TokenPayload(sub="123")
    assert payload.is_superuser is False
    assert payload.exp is None
    assert payload.iat is not None


def test_token_payload_required_fields():
    """Test that required fields are enforced in token payload."""
    with pytest.raises(ValidationError):
        TokenPayload(sub=None)  # type: ignore


def test_token_payload_timestamps():
    """Test token payload timestamp handling."""
    # Test with timestamps as datetime objects
    now = datetime.utcnow()
    exp = now + timedelta(days=1)

    payload = TokenPayload(sub="123", iat=now, exp=exp)
    assert payload.iat == now
    assert payload.exp == exp

    # Test with timestamps as floats (UNIX timestamps)
    now_ts = now.timestamp()
    exp_ts = exp.timestamp()

    payload = TokenPayload(sub="123", iat=now_ts, exp=exp_ts)
    assert int(payload.iat.timestamp()) == int(now_ts)
    assert int(payload.exp.timestamp()) == int(exp_ts)
