"""Tests for authentication API endpoints."""

import logging
import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import sessionmaker
from app.core.security import get_password_hash, verify_password
from app.core.config import settings
from app.models import User, Base
from app.db.session import Base, get_db
from app.main import app
from app.crud.user import user as crud_user
from tests.utils.utils import random_email, random_lower_string

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Test database setup
from app.db.session import engine

# Override settings for testing
settings.DATABASE_URL = "sqlite:///:memory:"
settings.TESTING = True

# Create test database tables
Base.metadata.create_all(bind=engine)

# Create a test session
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


# Override get_db dependency
def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


# Override the database dependency in the app
app.dependency_overrides[get_db] = override_get_db

# Test client
client = TestClient(app)


# Fixture to clean up database after each test
@pytest.fixture(autouse=True)
def cleanup():
    # Clear all data after each test
    with TestingSessionLocal() as db:
        for table in reversed(Base.metadata.sorted_tables):
            db.execute(table.delete())
        db.commit()


@pytest.fixture
def test_user() -> User:
    """Create a test user."""
    db = TestingSessionLocal()
    email = random_email()
    password = random_lower_string()

    # Use the same hashing method as in the application
    hashed_password = get_password_hash(password)
    logger.debug(f"Creating test user with email: {email}, password: {password}, hashed: {hashed_password}")

    user = User(
        email=email,
        hashed_password=hashed_password,
        username=email.split("@")[0],
        full_name="Test User",
        is_active=True,
    )

    db.add(user)
    db.commit()
    db.refresh(user)

    # Verify the password can be verified
    assert verify_password(password, user.hashed_password), "Password verification failed after user creation"

    # Store the password in plaintext for testing
    user.plain_password = password
    return user


def test_authenticate_directly(test_user: User) -> None:
    """Test authentication directly with the CRUD method."""
    db = TestingSessionLocal()
    try:
        # Test with correct credentials
        user = crud_user.authenticate(db, email=test_user.email, password=test_user.plain_password)
        assert user is not None, "Authentication with correct credentials failed"
        assert user.email == test_user.email, "Authenticated user email doesn't match"

        # Test with incorrect password
        user = crud_user.authenticate(db, email=test_user.email, password="wrongpassword")
        assert user is None, "Authentication with wrong password should fail"

    finally:
        db.close()


def test_login_access_token(client: TestClient, db_session) -> None:
    """Test login for access token."""
    try:
        # Create a test user with all required fields
        email = random_email()
        password = random_lower_string()
        username = email.split("@")[0]  # Use part before @ as username

        # Use the same password hashing as the application
        hashed_password = get_password_hash(password)

        logger.debug(f"Creating test user with email: {email}, username: {username}")

        test_user = User(
            username=username,
            email=email,
            hashed_password=hashed_password,
            full_name="Test User",
            is_active=True,
            is_superuser=False,
        )

        db_session.add(test_user)
        db_session.commit()
        db_session.refresh(test_user)

        # Store the plain password for testing
        test_user.plain_password = password
        logger.debug(f"Created user with ID: {test_user.id}")

        # Verify the user is in the database
        user_in_db = db_session.query(User).filter(User.id == test_user.id).first()
        assert user_in_db is not None, "Test user was not created in the database"
        logger.debug(f"User in DB: ID={user_in_db.id}, Email={user_in_db.email}, Active={user_in_db.is_active}")

        # Verify the password
        is_password_correct = verify_password(test_user.plain_password, user_in_db.hashed_password)
        logger.debug(f"Password verification: {is_password_correct}")
        assert is_password_correct, "Password verification failed for test user"

        # Now test the API endpoint
        login_data = {
            "username": test_user.email,
            "password": test_user.plain_password,
            "grant_type": "password",
        }

        logger.debug(f"Testing login with data: {login_data}")

        # Make the API request
        r = client.post(
            f"{settings.API_V1_STR}/auth/login",
            data=login_data,
            headers={"Content-Type": "application/x-www-form-urlencoded"},
        )

        logger.debug(f"Login response: {r.status_code}, {r.text}")

        if r.status_code != 200:
            # If login failed, check the database state
            users = db_session.query(User).all()
            logger.error(f"Users in database after failed login: {[u.email for u in users]}")

            # Try to authenticate directly to verify the password
            auth_user = crud_user.authenticate(db_session, email=test_user.email, password=test_user.plain_password)
            logger.error(f"Direct authentication result: {auth_user}")

            # Check if the password hash is what we expect
            user = db_session.query(User).filter(User.email == test_user.email).first()
            if user:
                logger.error(f"Stored password hash: {user.hashed_password}")
                logger.error(f"Expected to verify with: {test_user.plain_password}")
                logger.error(f"Verify result: {verify_password(test_user.plain_password, user.hashed_password)}")

        assert r.status_code == 200, f"Login failed with status {r.status_code}: {r.text}"

        tokens = r.json()
        assert "access_token" in tokens, "No access token in response"
        assert "token_type" in tokens, "No token type in response"
        assert tokens["token_type"].lower() == "bearer", f"Unexpected token type: {tokens['token_type']}"
        assert len(tokens["access_token"]) > 0, "Access token is empty"

    except Exception as e:
        logger.error(f"Test failed with error: {str(e)}", exc_info=True)
        raise
    finally:
        # Clean up
        try:
            if "test_user" in locals() and hasattr(test_user, "id"):
                db_session.query(User).filter(User.id == test_user.id).delete()
                db_session.commit()
        except Exception as e:
            logger.error(f"Error cleaning up test user: {e}")
            db_session.rollback()


def test_login_invalid_credentials(client: TestClient, db_session) -> None:
    """Test login with invalid credentials."""
    # Create a test user
    email = random_email()
    password = random_lower_string()
    hashed_password = get_password_hash(password)

    test_user = User(
        email=email,
        username=email.split("@")[0],
        hashed_password=hashed_password,
        full_name="Test User",
        is_active=True,
    )
    db_session.add(test_user)
    db_session.commit()

    try:
        # Test with wrong password
        response = client.post(
            f"{settings.API_V1_STR}/auth/login",
            data={
                "username": email,
                "password": "wrongpassword",
                "grant_type": "password",
            },
            headers={"Content-Type": "application/x-www-form-urlencoded"},
        )
        assert response.status_code == 400
        assert "Incorrect email or password" in response.json()["detail"]

    finally:
        # Cleanup
        db_session.delete(test_user)
        db_session.commit()


def test_login_inactive_user(client: TestClient, db_session) -> None:
    """Test login with an inactive user account."""
    # Create an inactive test user
    from app.core.security import get_password_hash
    from app.models import User

    email = "inactive@example.com"
    password = "inactive123"

    # Delete any existing test user
    db_session.query(User).filter(User.email == email).delete()

    # Create a new test user that's inactive
    test_user = User(
        email=email,
        username="inactive_user",
        full_name="Inactive User",
        hashed_password=get_password_hash(password),
        is_active=False,
    )
    db_session.add(test_user)
    db_session.commit()
    db_session.refresh(test_user)

    try:
        # Attempt to login with inactive user
        response = client.post(
            f"{settings.API_V1_STR}/auth/login",
            data={"username": email, "password": password, "grant_type": "password"},
            headers={"Content-Type": "application/x-www-form-urlencoded"},
        )

        # The API returns 400 for both incorrect password and inactive user
        # to avoid user enumeration
        assert response.status_code == 400
        assert "Incorrect email or password" in response.json()["detail"]

        # Verify the user exists and is inactive
        user = db_session.query(User).filter(User.email == email).first()
        assert user is not None
        assert not user.is_active

    finally:
        # Cleanup
        db_session.delete(test_user)
        db_session.commit()


def test_login_nonexistent_user(client: TestClient) -> None:
    """Test login with a non-existent user."""
    response = client.post(
        f"{settings.API_V1_STR}/auth/login",
        data={
            "username": "nonexistent@example.com",
            "password": "password123",
            "grant_type": "password",
        },
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )
    assert response.status_code == 400
    assert "Incorrect email or password" in response.json()["detail"]


def test_use_access_token(client: TestClient, db_session) -> None:
    """Test using an access token for authentication."""
    # Create a test user directly in the test
    from app.models import User as UserModel
    from app.core.security import get_password_hash

    # Create a test user with a known password
    email = "test_user@example.com"
    password = "testpassword123"
    hashed_password = get_password_hash(password)

    # Delete any existing test user
    db_session.query(UserModel).filter(UserModel.email == email).delete()

    # Create a new test user
    test_user = UserModel(
        email=email,
        username="testuser",
        full_name="Test User",
        hashed_password=hashed_password,
        is_active=True,
    )
    db_session.add(test_user)
    db_session.commit()
    db_session.refresh(test_user)

    # Verify the user was created
    db_user = db_session.query(UserModel).filter(UserModel.id == test_user.id).first()
    assert db_user is not None, "Test user not found in database"

    # Debug: Print test user details
    logger.debug(f"Test user email: {db_user.email}")
    logger.debug(f"Test user ID: {db_user.id}")
    logger.debug(f"Test user active: {db_user.is_active}")

    # Login to get a token
    login_data = {"username": email, "password": password, "grant_type": "password"}

    # Test login with form data
    login_response = client.post(
        f"{settings.API_V1_STR}/auth/login",
        data=login_data,
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )

    # Debug output if login fails
    if login_response.status_code != 200:
        logger.error(f"Login failed: {login_response.status_code} - {login_response.text}")
        # Check if user exists and is active
        user = db_session.query(type(test_user)).filter(type(test_user).email == test_user.email).first()
        logger.error(f"User in DB: {user}")
        if user:
            logger.error(f"User active: {user.is_active}")
            logger.error(f"Password matches: {verify_password(password, user.hashed_password)}")

    assert login_response.status_code == 200, f"Login failed: {login_response.text}"

    tokens = login_response.json()
    assert "access_token" in tokens, "No access token in response"
    assert "token_type" in tokens, "No token type in response"
    assert tokens["token_type"].lower() == "bearer", f"Unexpected token type: {tokens['token_type']}"

    # Use the token to access a protected endpoint
    response = client.get(
        f"{settings.API_V1_STR}/users/me",
        headers={"Authorization": f"Bearer {tokens['access_token']}"},
    )
    assert response.status_code == 200, f"Failed to access protected endpoint: {response.text}"
    user_data = response.json()
    assert "email" in user_data, "Email not in user data"
    assert isinstance(user_data["email"], str), "Email should be a string"
    assert "id" in user_data, "User ID not in response"
    assert isinstance(user_data["id"], int), "User ID should be an integer"


def test_login_incorrect_credentials(client: TestClient, test_user: User) -> None:
    """Test login with incorrect credentials."""
    login_data = {
        "username": test_user.email,
        "password": "incorrect_password",
        "grant_type": "password",
        "scope": "",
    }
    r = client.post(
        f"{settings.API_V1_STR}/auth/login",
        data=login_data,
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )
    assert r.status_code == 400
    response_data = r.json()
    assert "detail" in response_data
    assert "Incorrect email or password" in response_data["detail"]


def test_login_inactive_user(client: TestClient) -> None:
    """Test login with an inactive user."""
    db = TestingSessionLocal()
    email = random_email()
    password = random_lower_string()
    hashed_password = get_password_hash(password)

    # Create inactive user
    user = User(
        email=email,
        hashed_password=hashed_password,
        username=email.split("@")[0],
        full_name="Inactive User",
        is_active=False,
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    # Try to login
    login_data = {
        "username": email,
        "password": password,
        "grant_type": "password",
        "scope": "",
    }
    r = client.post(
        f"{settings.API_V1_STR}/auth/login",
        data=login_data,
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )

    assert r.status_code == 400, f"Expected status code 400, got {r.status_code}: {r.text}"
    response_data = r.json()
    assert "detail" in response_data, f"No 'detail' in response: {response_data}"
    # The API should return a generic error message for inactive users to prevent user enumeration
    assert (
        "Incorrect email or password" in response_data["detail"]
    ), f"Unexpected error message: {response_data['detail']}"


def test_login_nonexistent_user(client: TestClient) -> None:
    """Test login with a non-existent user."""
    login_data = {
        "username": "nonexistent@example.com",
        "password": "password123",
        "grant_type": "password",
        "scope": "",
    }
    r = client.post(
        f"{settings.API_V1_STR}/auth/login",
        data=login_data,
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )
    assert r.status_code == 400
    response_data = r.json()
    assert "detail" in response_data
    assert "Incorrect email or password" in response_data["detail"]
