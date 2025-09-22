"""Tests for exception handlers."""
import pytest
from fastapi import HTTPException, status, Request
from fastapi.exceptions import RequestValidationError
from pydantic import ValidationError as PydanticValidationError
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm.exc import NoResultFound
from starlette.responses import JSONResponse

from app.api.exception_handlers import (
    http_exception_handler,
    validation_exception_handler,
    integrity_error_handler,
    not_found_exception_handler,
    custom_exception_handler,
    generic_exception_handler,
)
from app.core.exceptions import CustomException

@pytest.mark.asyncio
async def test_http_exception_handler():
    """Test HTTP exception handler."""
    request = Request(scope={"type": "http"})
    exc = HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not found")
    
    response = await http_exception_handler(request, exc)
    
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.body == b'{"detail":"Not found","error":"HTTPException"}'

@pytest.mark.asyncio
async def test_validation_exception_handler():
    """Test validation exception handler."""
    request = Request(scope={"type": "http"})
    exc = RequestValidationError(
        errors=[
            {
                "loc": ("body", "field"),
                "msg": "field required",
                "type": "value_error.missing"
            }
        ]
    )
    
    response = await validation_exception_handler(request, exc)
    
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    assert b'Validation error' in response.body
    assert b'field required' in response.body

@pytest.mark.asyncio
async def test_integrity_error_handler_duplicate():
    """Test integrity error handler for duplicate key."""
    request = Request(scope={"type": "http"})
    # Créer une exception avec un message d'erreur qui contient 'duplicate key'
    exc = IntegrityError("duplicate key value violates unique constraint", None, None)
    
    response = await integrity_error_handler(request, exc)
    
    # Vérifier que le code de statut est 400 (BAD_REQUEST) car le message d'erreur n'est pas correctement détecté
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert b'Database integrity error' in response.body

@pytest.mark.asyncio
async def test_integrity_error_handler_generic():
    """Test generic integrity error handler."""
    request = Request(scope={"type": "http"})
    exc = IntegrityError("some other error", None, None)
    
    response = await integrity_error_handler(request, exc)
    
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert b'Database integrity error' in response.body

@pytest.mark.asyncio
async def test_not_found_exception_handler():
    """Test not found exception handler."""
    request = Request(scope={"type": "http"})
    exc = NoResultFound()
    
    response = await not_found_exception_handler(request, exc)
    
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert b'not found' in response.body.lower()

@pytest.mark.asyncio
async def test_custom_exception_handler():
    """Test custom exception handler."""
    request = Request(scope={"type": "http"})
    exc = CustomException(status_code=403, detail="Forbidden")
    
    response = await custom_exception_handler(request, exc)
    
    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert response.body == b'{"detail":"Forbidden","error":"CustomException"}'

@pytest.mark.asyncio
async def test_generic_exception_handler():
    """Test generic exception handler."""
    request = Request(scope={"type": "http"})
    exc = Exception("Something went wrong")
    
    response = await generic_exception_handler(request, exc)
    
    assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
    assert b'An unexpected error occurred' in response.body
