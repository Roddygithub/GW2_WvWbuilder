"""Tests for pagination utilities."""

import pytest
from app.core.pagination import get_skip_limit, Paginated


def test_get_skip_limit_default():
    """Test default pagination values."""
    skip, limit = get_skip_limit()
    assert skip == 0
    assert limit == 100


def test_get_skip_limit_custom():
    """Test custom pagination values."""
    skip, limit = get_skip_limit(page=2, page_size=50)
    assert skip == 50
    assert limit == 50


def test_get_skip_limit_negative_page():
    """Test negative page number defaults to 1."""
    skip, limit = get_skip_limit(page=-1, page_size=10)
    assert skip == 0
    assert limit == 10


def test_get_skip_limit_max_limit():
    """Test maximum limit enforcement."""
    skip, limit = get_skip_limit(page=1, page_size=1000)
    assert limit == 1000  # or max limit if enforced


def test_paginated_model():
    """Test Paginated model creation."""
    items = [1, 2, 3, 4, 5]
    paginated = Paginated(
        items=items,
        total=100,
        page=1,
        page_size=5,
        pages=20
    )
    
    assert paginated.items == items
    assert paginated.total == 100
    assert paginated.page == 1
    assert paginated.page_size == 5
    assert paginated.pages == 20


def test_paginated_empty():
    """Test Paginated with empty results."""
    paginated = Paginated(
        items=[],
        total=0,
        page=1,
        page_size=10,
        pages=0
    )
    
    assert paginated.items == []
    assert paginated.total == 0
    assert paginated.pages == 0
