"""Tests for the main FastAPI application."""
import os
import sys
from unittest.mock import patch, MagicMock, ANY

import pytest
from fastapi import FastAPI, status
from fastapi.testclient import TestClient
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from starlette.middleware.sessions import SessionMiddleware
from sqlalchemy.orm import sessionmaker

# Add the parent directory to the path so we can import app
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../app')))

from main import create_application, app
from app.core.config import settings
from app.db.session import Base, engine

# Test client
client = TestClient(app)

# Test application
@pytest.fixture(scope="module")
def test_app():
    """Create a test application with overridden settings."""
    # Use an in-memory SQLite database for testing
    settings.SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"
    settings.TESTING = True
    
    # Create the application
    test_app = create_application()
    
    # Create all database tables
    Base.metadata.create_all(bind=engine)
    
    yield test_app
    
    # Clean up
    Base.metadata.drop_all(bind=engine)


def test_application_creation():
    """Test that the FastAPI application is created with the correct settings."""
    # Create a test application
    test_app = create_application()
    
    # Check that the app is an instance of FastAPI
    assert isinstance(test_app, FastAPI)
    
    # Check that the title and version are set correctly
    assert test_app.title == settings.PROJECT_NAME
    assert test_app.version == "0.1.0"
    
    # Check that CORS middleware is added
    cors_middleware = next(
        (m for m in test_app.user_middleware if m.cls == CORSMiddleware), 
        None
    )
    assert cors_middleware is not None
    
    # Check that GZip middleware is added
    gzip_middleware = next(
        (m for m in test_app.user_middleware if m.cls == GZipMiddleware), 
        None
    )
    assert gzip_middleware is not None
    
    # Check that Session middleware is added
    session_middleware = next(
        (m for m in test_app.user_middleware if m.cls == SessionMiddleware), 
        None
    )
    assert session_middleware is not None


def test_root_endpoint():
    """Test the root endpoint."""
    response = client.get("/")
    assert response.status_code == status.HTTP_200_OK
    assert "message" in response.json()
    assert "Welcome to the GW2 WvW Builder API" in response.json()["message"]


def test_health_check():
    """Test the health check endpoint."""
    response = client.get("/health")
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {"status": "ok"}


def test_docs_endpoint():
    """Test that the API documentation is available."""
    response = client.get("/docs")
    assert response.status_code == status.HTTP_200_OK
    assert "text/html" in response.headers["content-type"]


def test_redoc_endpoint():
    """Test that the ReDoc documentation is available."""
    response = client.get("/redoc")
    assert response.status_code == status.HTTP_200_OK
    assert "text/html" in response.headers["content-type"]


def test_openapi_schema():
    """Test that the OpenAPI schema is available."""
    response = client.get("/api/v1/openapi.json")
    assert response.status_code == status.HTTP_200_OK
    assert "openapi" in response.json()
    assert response.json()["info"]["title"] == settings.PROJECT_NAME


def test_cors_headers():
    """Test that CORS headers are set correctly."""
    # Make a request with an Origin header
    response = client.get("/", headers={"Origin": settings.BACKEND_CORS_ORIGINS[0]})
    
    # Check that the CORS headers are set
    assert response.status_code == status.HTTP_200_OK
    assert "access-control-allow-origin" in response.headers
    assert response.headers["access-control-allow-origin"] == settings.BACKEND_CORS_ORIGINS[0]


def test_http_exception_handler():
    """Test the HTTP exception handler."""
    # Create a test client with a custom exception handler
    test_app = FastAPI()
    client = TestClient(test_app)
    
    # Add a route that raises an HTTPException
    @test_app.get("/test-http-exception")
    async def test_http_exception():
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Test error")
    
    # Make a request to the test route
    response = client.get("/test-http-exception")
    
    # Check that the response has the correct status code and error message
    assert response.status_code == 404
    assert response.json() == {"detail": "Test error"}


def test_validation_exception_handler():
    """Test the validation exception handler."""
    # Create a test client with a custom exception handler
    test_app = FastAPI()
    client = TestClient(test_app)
    
    # Add a route that raises a RequestValidationError
    @test_app.get("/test-validation-exception")
    async def test_validation_exception():
        from fastapi.exceptions import RequestValidationError
        from pydantic import ValidationError
        
        # Create a validation error
        error = ValidationError(errors=[{"loc": ["test"], "msg": "Test error"}], model=None)
        raise RequestValidationError(errors=error.errors())
    
    # Make a request to the test route
    response = client.get("/test-validation-exception")
    
    # Check that the response has the correct status code and error message
    assert response.status_code == 422
    assert "detail" in response.json()
    assert len(response.json()["detail"]) > 0


def test_internal_exception_handler():
    """Test the internal exception handler."""
    # Create a test client with a custom exception handler
    test_app = FastAPI()
    client = TestClient(test_app)
    
    # Add a route that raises an exception
    @test_app.get("/test-internal-exception")
    async def test_internal_exception():
        raise Exception("Test error")
    
    # Make a request to the test route
    response = client.get("/test-internal-exception")
    
    # Check that the response has the correct status code and error message
    assert response.status_code == 500
    assert response.json() == {"detail": "Internal server error"}


def test_static_files():
    """Test that static files are served correctly."""
    # Skip this test if the static directory doesn't exist
    if not os.path.isdir("static"):
        pytest.skip("Static directory not found")
    
    # Create a test file in the static directory
    test_file = os.path.join("static", "test.txt")
    with open(test_file, "w") as f:
        f.write("Test content")
    
    try:
        # Make a request to the static file
        response = client.get("/static/test.txt")
        
        # Check that the response has the correct content
        assert response.status_code == status.HTTP_200_OK
        assert response.text == "Test content"
    finally:
        # Clean up the test file
        if os.path.exists(test_file):
            os.remove(test_file)


def test_database_connection():
    """Test that the database connection is working."""
    # Create a test table
    from sqlalchemy import Column, Integer, String, create_engine
    from sqlalchemy.orm import sessionmaker
    
    # Create a test table
    Base = Base.metadata
    engine = create_engine("sqlite:///:memory:")
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    
    # Create all tables
    Base.create_all(bind=engine)
    
    # Test the connection
    db = SessionLocal()
    try:
        # Execute a simple query
        result = db.execute("SELECT 1").scalar()
        assert result == 1
    finally:
        db.close()


if __name__ == "__main__":
    pytest.main([__file__])
