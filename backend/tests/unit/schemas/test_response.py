"""Tests for response schemas."""

import pytest
from app.schemas.response import (
    SuccessResponse,
    ErrorResponse,
    PaginatedResponse,
)


def test_success_response_creation():
    """Test SuccessResponse model creation."""
    response = SuccessResponse(
        success=True,
        message="Operation successful",
        data={"id": 1, "name": "Test"}
    )
    assert response.success is True
    assert response.message == "Operation successful"
    assert response.data["id"] == 1


def test_success_response_without_data():
    """Test SuccessResponse without data."""
    response = SuccessResponse(
        success=True,
        message="Success"
    )
    assert response.success is True
    assert response.data is None


def test_error_response_creation():
    """Test ErrorResponse model creation."""
    response = ErrorResponse(
        success=False,
        message="An error occurred",
        error="ValidationError",
        details={"field": "email"}
    )
    assert response.success is False
    assert response.message == "An error occurred"
    assert response.error == "ValidationError"


def test_error_response_minimal():
    """Test ErrorResponse with minimal fields."""
    response = ErrorResponse(
        success=False,
        message="Error"
    )
    assert response.success is False
    assert response.error is None
    assert response.details is None


def test_paginated_response_creation():
    """Test PaginatedResponse model creation."""
    items = [{"id": 1}, {"id": 2}, {"id": 3}]
    response = PaginatedResponse(
        items=items,
        total=100,
        page=1,
        page_size=10,
        pages=10
    )
    assert len(response.items) == 3
    assert response.total == 100
    assert response.page == 1
    assert response.pages == 10


def test_paginated_response_empty():
    """Test PaginatedResponse with empty items."""
    response = PaginatedResponse(
        items=[],
        total=0,
        page=1,
        page_size=10,
        pages=0
    )
    assert len(response.items) == 0
    assert response.total == 0


def test_paginated_response_calculations():
    """Test PaginatedResponse page calculations."""
    response = PaginatedResponse(
        items=[1, 2, 3, 4, 5],
        total=47,
        page=2,
        page_size=5,
        pages=10
    )
    assert response.pages == 10
    assert len(response.items) == 5
