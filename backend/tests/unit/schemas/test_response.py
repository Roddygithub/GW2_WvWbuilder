"""
Tests unitaires pour app/schemas/response.py
"""
import pytest
from typing import List

from app.schemas.response import (
    APIResponse,
    PaginatedResponse,
    ErrorResponse,
    SuccessResponse,
    create_success_response,
    create_error_response,
    create_paginated_response,
)


class TestAPIResponse:
    """Tests pour APIResponse schema."""

    def test_api_response_success(self):
        """Test création APIResponse avec succès."""
        response = APIResponse[dict](
            success=True,
            data={"id": 1, "name": "Test"},
            message="Success"
        )
        assert response.success is True
        assert response.data == {"id": 1, "name": "Test"}
        assert response.message == "Success"
        assert response.error is None

    def test_api_response_error(self):
        """Test création APIResponse avec erreur."""
        response = APIResponse[None](
            success=False,
            error="Something went wrong"
        )
        assert response.success is False
        assert response.error == "Something went wrong"
        assert response.data is None


class TestPaginatedResponse:
    """Tests pour PaginatedResponse schema."""

    def test_paginated_response_first_page(self):
        """Test réponse paginée première page."""
        response = PaginatedResponse[dict](
            data=[{"id": 1}, {"id": 2}],
            total=100,
            page=1,
            page_size=10,
            total_pages=10,
            has_next=True,
            has_prev=False
        )
        assert response.success is True
        assert len(response.data) == 2
        assert response.page == 1
        assert response.has_next is True
        assert response.has_prev is False

    def test_paginated_response_middle_page(self):
        """Test réponse paginée page intermédiaire."""
        response = PaginatedResponse[dict](
            data=[{"id": 11}, {"id": 12}],
            total=100,
            page=5,
            page_size=10,
            total_pages=10,
            has_next=True,
            has_prev=True
        )
        assert response.page == 5
        assert response.has_next is True
        assert response.has_prev is True

    def test_paginated_response_last_page(self):
        """Test réponse paginée dernière page."""
        response = PaginatedResponse[dict](
            data=[{"id": 91}],
            total=91,
            page=10,
            page_size=10,
            total_pages=10,
            has_next=False,
            has_prev=True
        )
        assert response.page == 10
        assert response.has_next is False
        assert response.has_prev is True


class TestErrorResponse:
    """Tests pour ErrorResponse schema."""

    def test_error_response_simple(self):
        """Test réponse erreur simple."""
        response = ErrorResponse(error="Not found")
        assert response.success is False
        assert response.error == "Not found"
        assert response.detail is None
        assert response.code is None

    def test_error_response_with_details(self):
        """Test réponse erreur avec détails."""
        response = ErrorResponse(
            error="Validation error",
            detail="Field 'name' is required",
            code="VALIDATION_ERROR"
        )
        assert response.success is False
        assert response.error == "Validation error"
        assert response.detail == "Field 'name' is required"
        assert response.code == "VALIDATION_ERROR"


class TestSuccessResponse:
    """Tests pour SuccessResponse schema."""

    def test_success_response(self):
        """Test réponse succès simple."""
        response = SuccessResponse(message="Operation completed")
        assert response.success is True
        assert response.message == "Operation completed"


class TestHelperFunctions:
    """Tests pour les fonctions helper."""

    def test_create_success_response_minimal(self):
        """Test création réponse succès minimale."""
        response = create_success_response()
        assert response["success"] is True
        assert response["data"] is None
        assert "message" not in response
        assert "meta" not in response

    def test_create_success_response_with_data(self):
        """Test création réponse succès avec données."""
        data = {"id": 1, "name": "Test"}
        response = create_success_response(data=data)
        assert response["success"] is True
        assert response["data"] == data

    def test_create_success_response_with_message(self):
        """Test création réponse succès avec message."""
        response = create_success_response(
            data={"id": 1},
            message="Created successfully"
        )
        assert response["success"] is True
        assert response["message"] == "Created successfully"

    def test_create_success_response_with_meta(self):
        """Test création réponse succès avec metadata."""
        meta = {"timestamp": "2025-10-16T23:00:00Z"}
        response = create_success_response(meta=meta)
        assert response["success"] is True
        assert response["meta"] == meta

    def test_create_error_response_minimal(self):
        """Test création réponse erreur minimale."""
        response = create_error_response(error="Error occurred")
        assert response["success"] is False
        assert response["error"] == "Error occurred"
        assert "detail" not in response
        assert "code" not in response

    def test_create_error_response_with_detail(self):
        """Test création réponse erreur avec détail."""
        response = create_error_response(
            error="Not found",
            detail="Resource with ID 123 not found"
        )
        assert response["success"] is False
        assert response["error"] == "Not found"
        assert response["detail"] == "Resource with ID 123 not found"

    def test_create_error_response_with_code(self):
        """Test création réponse erreur avec code."""
        response = create_error_response(
            error="Unauthorized",
            code="AUTH_REQUIRED"
        )
        assert response["success"] is False
        assert response["error"] == "Unauthorized"
        assert response["code"] == "AUTH_REQUIRED"

    def test_create_paginated_response_first_page(self):
        """Test création réponse paginée première page."""
        data = [{"id": 1}, {"id": 2}, {"id": 3}]
        response = create_paginated_response(
            data=data,
            total=30,
            page=1,
            page_size=10
        )
        assert response["success"] is True
        assert response["data"] == data
        assert response["total"] == 30
        assert response["page"] == 1
        assert response["page_size"] == 10
        assert response["total_pages"] == 3
        assert response["has_next"] is True
        assert response["has_prev"] is False

    def test_create_paginated_response_last_page(self):
        """Test création réponse paginée dernière page."""
        data = [{"id": 21}]
        response = create_paginated_response(
            data=data,
            total=21,
            page=3,
            page_size=10
        )
        assert response["total_pages"] == 3
        assert response["has_next"] is False
        assert response["has_prev"] is True

    def test_create_paginated_response_empty(self):
        """Test création réponse paginée vide."""
        response = create_paginated_response(
            data=[],
            total=0,
            page=1,
            page_size=10
        )
        assert response["data"] == []
        assert response["total"] == 0
        assert response["total_pages"] == 0
        assert response["has_next"] is False
        assert response["has_prev"] is False

    def test_create_paginated_response_ceiling_division(self):
        """Test calcul correct du nombre de pages (division avec arrondi supérieur)."""
        # 25 items avec page_size=10 devrait donner 3 pages
        response = create_paginated_response(
            data=[],
            total=25,
            page=1,
            page_size=10
        )
        assert response["total_pages"] == 3
