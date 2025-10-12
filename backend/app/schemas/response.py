"""
Standard API response schemas for consistent response formatting.
"""

from typing import Any, Dict, Generic, List, Optional, TypeVar
from pydantic import BaseModel, Field


DataT = TypeVar("DataT")


class APIResponse(BaseModel, Generic[DataT]):
    """
    Standard API response wrapper.

    Provides consistent response format across all endpoints.
    """

    success: bool = Field(..., description="Whether the request was successful")
    data: Optional[DataT] = Field(None, description="Response data")
    message: Optional[str] = Field(None, description="Human-readable message")
    error: Optional[str] = Field(None, description="Error message if success=False")
    meta: Optional[Dict[str, Any]] = Field(None, description="Additional metadata")

    class Config:
        json_schema_extra = {
            "example": {
                "success": True,
                "data": {"id": 1, "name": "Example"},
                "message": "Operation completed successfully",
                "error": None,
                "meta": {"timestamp": "2025-10-11T23:00:00Z"},
            }
        }


class PaginatedResponse(BaseModel, Generic[DataT]):
    """
    Paginated API response.

    Used for endpoints that return lists with pagination.
    """

    success: bool = Field(True, description="Whether the request was successful")
    data: List[DataT] = Field(..., description="List of items")
    total: int = Field(..., description="Total number of items")
    page: int = Field(..., description="Current page number")
    page_size: int = Field(..., description="Number of items per page")
    total_pages: int = Field(..., description="Total number of pages")
    has_next: bool = Field(..., description="Whether there is a next page")
    has_prev: bool = Field(..., description="Whether there is a previous page")

    class Config:
        json_schema_extra = {
            "example": {
                "success": True,
                "data": [{"id": 1, "name": "Item 1"}, {"id": 2, "name": "Item 2"}],
                "total": 100,
                "page": 1,
                "page_size": 10,
                "total_pages": 10,
                "has_next": True,
                "has_prev": False,
            }
        }


class ErrorResponse(BaseModel):
    """
    Standard error response.

    Used for all error responses.
    """

    success: bool = Field(False, description="Always False for errors")
    error: str = Field(..., description="Error message")
    detail: Optional[str] = Field(None, description="Detailed error information")
    code: Optional[str] = Field(None, description="Error code")

    class Config:
        json_schema_extra = {
            "example": {
                "success": False,
                "error": "Resource not found",
                "detail": "The requested build with ID 123 was not found",
                "code": "RESOURCE_NOT_FOUND",
            }
        }


class SuccessResponse(BaseModel):
    """
    Simple success response without data.

    Used for operations that don't return data (e.g., delete).
    """

    success: bool = Field(True, description="Always True for success")
    message: str = Field(..., description="Success message")

    class Config:
        json_schema_extra = {"example": {"success": True, "message": "Build deleted successfully"}}


def create_success_response(
    data: Any = None, message: Optional[str] = None, meta: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Helper function to create a success response.

    Args:
        data: Response data
        message: Success message
        meta: Additional metadata

    Returns:
        Dictionary with standard success response format
    """
    response = {
        "success": True,
        "data": data,
    }

    if message:
        response["message"] = message
    if meta:
        response["meta"] = meta

    return response


def create_error_response(error: str, detail: Optional[str] = None, code: Optional[str] = None) -> Dict[str, Any]:
    """
    Helper function to create an error response.

    Args:
        error: Error message
        detail: Detailed error information
        code: Error code

    Returns:
        Dictionary with standard error response format
    """
    response = {
        "success": False,
        "error": error,
    }

    if detail:
        response["detail"] = detail
    if code:
        response["code"] = code

    return response


def create_paginated_response(data: List[Any], total: int, page: int, page_size: int) -> Dict[str, Any]:
    """
    Helper function to create a paginated response.

    Args:
        data: List of items
        total: Total number of items
        page: Current page number
        page_size: Number of items per page

    Returns:
        Dictionary with standard paginated response format
    """
    total_pages = (total + page_size - 1) // page_size  # Ceiling division

    return {
        "success": True,
        "data": data,
        "total": total,
        "page": page,
        "page_size": page_size,
        "total_pages": total_pages,
        "has_next": page < total_pages,
        "has_prev": page > 1,
    }
