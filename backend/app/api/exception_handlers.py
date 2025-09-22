"""Exception handlers for the API."""

from fastapi import HTTPException, Request, status
from fastapi.exceptions import RequestValidationError
from pydantic import ValidationError as PydanticValidationError
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm.exc import NoResultFound
from starlette.responses import JSONResponse
from app.core.exceptions import CustomException

async def http_exception_handler(request: Request, exc: HTTPException) -> JSONResponse:
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail, "error": exc.__class__.__name__},
    )

async def validation_exception_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
    errors = [{"loc": e["loc"], "msg": e["msg"], "type": e["type"]} for e in exc.errors()]
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={"detail": "Validation error", "errors": errors},
    )

async def integrity_error_handler(request: Request, exc: IntegrityError) -> JSONResponse:
    error_msg = str(exc.orig) if exc.orig else "Database integrity error"
    if "duplicate key" in error_msg.lower():
        return JSONResponse(
            status_code=status.HTTP_409_CONFLICT,
            content={"detail": "Duplicate entry violates unique constraint"},
        )
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={"detail": "Database integrity error"},
    )

async def not_found_exception_handler(request: Request, exc: NoResultFound) -> JSONResponse:
    return JSONResponse(
        status_code=status.HTTP_404_NOT_FOUND,
        content={"detail": "The requested resource was not found"},
    )

async def custom_exception_handler(request: Request, exc: CustomException) -> JSONResponse:
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail, "error": exc.__class__.__name__},
    )

async def generic_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "An unexpected error occurred"},
    )
