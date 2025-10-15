"""Tests for pagination utilities."""

import pytest
from app.core.pagination import (
    PaginationParams,
    PaginatedResponse,
    paginate,
    create_paginated_response,
)


def test_pagination_params_default():
    """Test default pagination parameters."""
    params = PaginationParams()
    assert params.page == 1
    assert params.size == 20
    assert params.offset == 0
    assert params.limit == 20


def test_pagination_params_custom():
    """Test custom pagination parameters."""
    params = PaginationParams(page=3, size=50)
    assert params.page == 3
    assert params.size == 50
    assert params.offset == 100  # (3-1) * 50
    assert params.limit == 50


def test_pagination_params_first_page():
    """Test pagination for first page."""
    params = PaginationParams(page=1, size=10)
    assert params.offset == 0
    assert params.limit == 10


def test_create_paginated_response():
    """Test creating paginated response."""
    items = [1, 2, 3, 4, 5]
    params = PaginationParams(page=1, size=5)
    
    response = create_paginated_response(items, total=100, pagination=params)
    
    assert response["items"] == items
    assert response["total"] == 100
    assert response["page"] == 1
    assert response["size"] == 5
    assert response["pages"] == 20


def test_create_paginated_response_empty():
    """Test paginated response with empty results."""
    params = PaginationParams(page=1, size=10)
    
    response = create_paginated_response([], total=0, pagination=params)
    
    assert response["items"] == []
    assert response["total"] == 0
    assert response["pages"] == 0


def test_create_paginated_response_last_page():
    """Test paginated response for last incomplete page."""
    items = [1, 2, 3]
    params = PaginationParams(page=3, size=10)
    
    response = create_paginated_response(items, total=23, pagination=params)
    
    assert response["pages"] == 3
    assert len(response["items"]) == 3
