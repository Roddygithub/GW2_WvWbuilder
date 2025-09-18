"""
Comprehensive tests for the Authentication API endpoints.
"""
import logging
import json
import uuid
import pytest
from fastapi import status
from fastapi.testclient import TestClient
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.config import settings
from app.models import User
from app.schemas.user import UserCreate, UserUpdate, Token, TokenData
from app.core.security import get_password_hash, verify_password, create_access_token
from app.api.deps import get_async_db
from jose import jwt

pytestmark = pytest.mark.asyncio

class TestAuthAPI:
    """Test suite for Authentication API endpoints."""

    async def test_login_success(
        self, async_client: AsyncClient, test_user: User
    ):
        """Test successful user login."""
        login_data = {
            "username": test_user.email,
            "password": "testpassword"  # From the test user fixture
        }
        
        response = await async_client.post(
            f"{settings.API_V1_STR}/auth/login",
            data=login_data
        )
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"
        
        # Verify the token is valid
        token_data = jwt.decode(
            data["access_token"],
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM],
            options={"verify_aud": False}
        )
        assert token_data["sub"] == str(test_user.id)

    async def test_login_wrong_password(
        self, async_client: AsyncClient, test_user: User
    ):
        """Test login with wrong password."""
        login_data = {
            "username": test_user.email,
            "password": "wrongpassword"
        }
        
        response = await async_client.post(
            f"{settings.API_V1_STR}/auth/login",
            data=login_data
        )
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "Incorrect email or password" in response.text

    async def test_login_nonexistent_user(
        self, async_client: AsyncClient, caplog
    ):
        """Test login with non-existent user."""
        import logging
        import json
        
        # Enable debug logging
        caplog.set_level(logging.DEBUG)
        
        login_data = {
            "username": "nonexistent@example.com",
            "password": "doesntmatter"
        }
        
        # Log the request
        print(f"\nSending login request to: {settings.API_V1_STR}/auth/login")
        print(f"Request data: {login_data}")
        
        try:
            response = await async_client.post(
                f"{settings.API_V1_STR}/auth/login",
                data=login_data
            )
            
            # Log the response
            print(f"Response status: {response.status_code}")
            try:
                print(f"Response body: {response.text}")
                print(f"Response JSON: {response.json()}")
            except Exception as e:
                print(f"Could not parse response as JSON: {e}")
            
            # Log any server errors
            if response.status_code >= 500:
                print("\nServer error details:")
                print(f"Status code: {response.status_code}")
                print(f"Headers: {dict(response.headers)}")
                print(f"Response text: {response.text}")
            
            # Check the response
            assert response.status_code == status.HTTP_400_BAD_REQUEST, \
                f"Expected status code 400, got {response.status_code}. Response: {response.text}"
            assert "Incorrect email or password" in response.text, \
                f"Expected 'Incorrect email or password' in response, got: {response.text}"
                
        except Exception as e:
            print(f"\nException during test: {str(e)}")
            print(f"Exception type: {type(e).__name__}")
            import traceback
            traceback.print_exc()
            raise

    async def test_use_access_token(
        self, async_client: AsyncClient, test_user: User
    ):
        """Test using the access token to access a protected endpoint."""
        # First get a token
        login_data = {
            "username": test_user.email,
            "password": "testpassword"
        }
        token_response = await async_client.post(
            f"{settings.API_V1_STR}/login/access-token",
            data=login_data
        )
        access_token = token_response.json()["access_token"]
        
        # Use the token to access a protected endpoint
        response = await async_client.get(
            f"{settings.API_V1_STR}/users/me",
            headers={"Authorization": f"Bearer {access_token}"}
        )
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["email"] == test_user.email

    async def test_refresh_token(
        self, async_client: AsyncClient, test_user: User
    ):
        """Test refreshing an access token."""
        # First get a refresh token
        refresh_token = create_access_token(
            subject=test_user.id,
            expires_delta=settings.REFRESH_TOKEN_EXPIRE_MINUTES,
            token_type="refresh"
        )
        
        # Use the refresh token to get a new access token
        response = await async_client.post(
            f"{settings.API_V1_STR}/login/refresh-token",
            json={"refresh_token": refresh_token}
        )
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"

    async def test_reset_password(
        self, async_client: AsyncClient, test_user: User
    ):
        """Test password reset flow."""
        # Request password reset
        reset_request = {
            "email": test_user.email
        }
        response = await async_client.post(
            f"{settings.API_V1_STR}/password-recovery/{test_user.email}",
            json=reset_request
        )
        
        assert response.status_code == status.HTTP_202_ACCEPTED
        
        # In a real test, we would extract the reset token from the email
        # For testing, we'll create one directly
        reset_token = create_access_token(
            subject=test_user.email,
            expires_delta=settings.EMAIL_RESET_TOKEN_EXPIRE_MINUTES,
            token_type="reset"
        )
        
        # Reset the password
        new_password = "newsecurepassword123"
        reset_data = {
            "token": reset_token,
            "new_password": new_password
        }
        
        reset_response = await async_client.post(
            f"{settings.API_V1_STR}/reset-password/",
            json=reset_data
        )
        
        assert reset_response.status_code == status.HTTP_200_OK
        
        # Verify the password was actually changed
        db_user = await test_user.get(test_user.id)
        assert verify_password(new_password, db_user.hashed_password)

    async def test_register_user(
        self, async_client: AsyncClient, async_db: AsyncSession
    ):
        """Test user registration with proper transaction handling."""
        from fastapi import status
        from app.core.config import settings
        from app.models import User
        from sqlalchemy import select
        from app.core.security import verify_password
        import logging
        
        logger = logging.getLogger(__name__)
        
        # Generate unique test data
        unique_id = str(uuid.uuid4())[:8]
        test_email = f"testuser_{unique_id}@example.com"
        test_username = f"testuser_{unique_id}"
        test_password = "testpassword123"
        
        # Test data
        user_data = {
            "email": test_email,
            "username": test_username,
            "password": test_password
        }
        
        logger.info(f"Testing user registration with email: {test_email}")
        
        try:
            # Make the registration request using async_client
            logger.debug("Sending registration request...")
            response = await async_client.post(
                f"{settings.API_V1_STR}/auth/register",
                json=user_data
            )
            
            # Check response
            logger.debug(f"Response status: {response.status_code}")
            logger.debug(f"Response body: {response.text}")
            
            assert response.status_code == status.HTTP_201_CREATED, \
                f"Expected status code 201, got {response.status_code}. Response: {response.text}"
                
            data = response.json()
            assert data["email"] == user_data["email"]
            assert data["username"] == user_data["username"]
            assert "hashed_password" not in data
            
            # Verify user was created in the database
            logger.debug("Verifying user in database...")
            result = await async_db.execute(
                select(User).where(User.email == test_email)
            )
            db_user = result.scalars().first()
            
            assert db_user is not None, "User was not created in the database"
            assert db_user.email == test_email
            assert db_user.username == test_username
            assert verify_password(test_password, db_user.hashed_password), "Password was not hashed correctly"
            
            logger.info("User registration test passed successfully")
            
        except Exception as e:
            logger.error(f"Test failed: {str(e)}", exc_info=True)
            # The session will be rolled back by the fixture
            raise
