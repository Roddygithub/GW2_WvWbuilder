"""Tests for error handling and custom exceptions."""
import pytest
from fastapi import FastAPI, HTTPException, status
from fastapi.testclient import TestClient
from pydantic import ValidationError
from sqlalchemy.exc import IntegrityError, NoResultFound

from app.api.exception_handlers import (
    http_exception_handler,
    validation_exception_handler,
    integrity_error_handler,
    not_found_exception_handler,
    generic_exception_handler
)
from app.core.exceptions import CustomException

# Test app for error handling
app = FastAPI()

# Test routes that raise different types of exceptions
@app.get("/test/http-exception")
async def test_http_exception():
    raise HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail="Test HTTP Exception"
    )

@app.get("/test/validation-error")
async def test_validation_error():
    raise ValidationError(errors=[], model=None)

@app.get("/test/integrity-error")
async def test_integrity_error():
    raise IntegrityError(
        statement=None,
        params=None,
        orig=Exception("duplicate key value violates unique constraint")
    )

@app.get("/test/not-found")
async def test_not_found():
    raise NoResultFound()

@app.get("/test/custom-exception")
async def test_custom_exception():
    raise CustomException(code=400, error="Test Custom Exception")

@app.get("/test/generic-exception")
async def test_generic_exception():
    raise Exception("Test Generic Exception")

# Register exception handlers
app.add_exception_handler(HTTPException, http_exception_handler)
app.add_exception_handler(ValidationError, validation_exception_handler)
app.add_exception_handler(IntegrityError, integrity_error_handler)
app.add_exception_handler(NoResultFound, not_found_exception_handler)
app.add_exception_handler(CustomException, http_exception_handler)
app.add_exception_handler(Exception, generic_exception_handler)

client = TestClient(app)

def test_http_exception_handler():
    """Test that HTTP exceptions are handled correctly."""
    response = client.get("/test/http-exception")
    
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json() == {
        "detail": {
            "code": 400,
            "error": "Test HTTP Exception"
        }
    }

def test_validation_exception_handler():
    """Test that validation errors are handled correctly."""
    response = client.get("/test/validation-error")
    
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    assert "validation_error" in response.json()
    assert "body" in response.json()["validation_error"]

def test_integrity_error_handler():
    """Test that database integrity errors are handled correctly."""
    response = client.get("/test/integrity-error")
    
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json() == {
        "detail": {
            "code": 400,
            "error": "Database integrity error",
            "details": "duplicate key value violates unique constraint"
        }
    }

def test_not_found_exception_handler():
    """Test that not found errors are handled correctly."""
    response = client.get("/test/not-found")
    
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json() == {
        "detail": {
            "code": 404,
            "error": "Resource not found"
        }
    }

def test_custom_exception_handler():
    """Test that custom exceptions are handled correctly."""
    response = client.get("/test/custom-exception")
    
    assert response.status_code == 400
    assert response.json() == {
        "detail": {
            "code": 400,
            "error": "Test Custom Exception"
        }
    }

def test_generic_exception_handler():
    """Test that unhandled exceptions are caught and returned as 500 errors."""
    response = client.get("/test/generic-exception")
    
    assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
    assert response.json() == {
        "detail": {
            "code": 500,
            "error": "Internal Server Error"
        }
    }

def test_custom_exception():
    """Test the CustomException class."""
    exc = CustomException(code=400, error="Test Error")
    
    assert exc.code == 400
    assert exc.error == "Test Error"
    assert str(exc) == "Test Error"
    
    # Test with details
    exc_with_details = CustomException(
        code=400, 
        error="Test Error",
        details={"field": "error details"}
    )
    assert exc_with_details.details == {"field": "error details"}

@pytest.mark.asyncio
async def test_http_exception_handler_direct():
    """Test the HTTP exception handler directly."""
    exc = HTTPException(status_code=400, detail="Test Error")
    response = await http_exception_handler(None, exc)
    
    assert response.status_code == 400
    assert response.body == b'{"detail":{"code":400,"error":"Test Error"}}'

@pytest.mark.asyncio
async def test_validation_exception_handler_direct():
    """Test the validation exception handler directly."""
    errors = [
        {
            "loc": ("body", "field"),
            "msg": "field required",
            "type": "value_error.missing"
        }
    ]
    exc = ValidationError(errors=errors, model=None)
    response = await validation_exception_handler(None, exc)
    
    assert response.status_code == 422
    assert b"validation_error" in response.body
    assert b"field required" in response.body
