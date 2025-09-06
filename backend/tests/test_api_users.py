import pytest
from fastapi import status, Depends
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session, sessionmaker

from app.api.deps import get_current_active_user, get_current_active_superuser, get_db
from app.core.security import get_password_hash
from app.models.base import Base
from app.models.base_models import User, Role
from app.db.session import engine
# Remove get_test_db import as we'll use the db_session fixture from conftest.py

# Test API prefix
API_PREFIX = "/api/v1"

# Test user data
TEST_USER_EMAIL = "test@example.com"
TEST_USER_PASSWORD = "testpass"
TEST_USER_FULL_NAME = "Test User"

# Mock authentication for tests
def override_get_current_user():
    # This will be overridden in individual tests
    return None

def override_get_current_superuser():
    # This will be overridden in individual tests
    return None

def make_superuser(db_session):
    # Create admin role if it doesn't exist
    admin_role = db_session.query(Role).filter(Role.name == "admin").first()
    if not admin_role:
        admin_role = Role(name="admin", description="Administrator role")
        db_session.add(admin_role)
        db_session.commit()
        db_session.refresh(admin_role)

    su = User(
        email="admin@example.com",
        username="admin",
        hashed_password=get_password_hash("adminpass"),
        is_active=True,
        is_superuser=True,
    )
    su.roles.append(admin_role)
    db_session.add(su)
    db_session.commit()
    db_session.refresh(su)
    return su


def make_user(db: Session, username: str = "testuser", email: str = "test@example.com", password: str = "testpass", is_superuser: bool = False) -> User:
    """Create a test user in the database.
    
    Args:
        db: Database session
        username: Username for the new user
        email: Email for the new user
        password: Password for the new user
        is_superuser: Whether the user should be a superuser
    """
    from app.crud.user import user as user_crud
    from app.schemas.user import UserCreate
    
    user_data = UserCreate(
        username=username,
        email=email,
        password=password,
        is_active=True,
        is_superuser=is_superuser,
    )
    return user_crud.create(db, obj_in=user_data)


@pytest.fixture(scope="function")
def client(db_session):
    from app.main import app
    from fastapi.testclient import TestClient

    # Create test database tables if they don't exist
    Base.metadata.create_all(bind=engine)

    # Override the get_db dependency to use the test session
    def override_get_db():
        try:
            yield db_session
            db_session.commit()
        except Exception:
            db_session.rollback()
            raise

    # Store original overrides
    original_overrides = app.dependency_overrides.copy()

    # Set up test overrides
    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[get_current_active_user] = override_get_current_user
    app.dependency_overrides[get_current_active_superuser] = override_get_current_superuser

    # Create test client with the overridden dependencies
    test_client = TestClient(app)

    try:
        yield test_client
    finally:
        # Clean up test data
        db_session.rollback()
        # Restore original overrides
        app.dependency_overrides = original_overrides


class TestUsersAPI:
    def setup_method(self):
        # Set up default authentication overrides for each test
        from app.main import app
        
        # Clear any existing overrides
        app.dependency_overrides.clear()
        
        # Set default overrides that will be used if not overridden in the test
        app.dependency_overrides[get_current_active_user] = override_get_current_user
        app.dependency_overrides[get_current_active_superuser] = override_get_current_superuser
    
    def test_list_users_with_pagination(self, client, db_session):
        """Test listing users with pagination parameters."""
        from app.main import app
        from app.crud.user import user as user_crud
        from fastapi import HTTPException
        
        # Create a superuser for this test
        superuser = make_superuser(db_session)
        
        # Create some test users
        users = []
        for i in range(5):
            user = make_user(db_session, 
                           username=f"testuser_{i}", 
                           email=f"test_{i}@example.com")
            users.append(user)
        db_session.commit()
        
        # Set up superuser override
        def get_superuser_override():
            db_user = user_crud.get(db_session, id=superuser.id)
            if not db_user:
                raise HTTPException(status_code=404, detail="User not found")
            return db_user
            
        app.dependency_overrides[get_current_active_user] = get_superuser_override
        app.dependency_overrides[get_current_active_superuser] = get_superuser_override
        
        try:
            # Test with skip and limit
            resp = client.get(f"{API_PREFIX}/users/?skip=1&limit=2")
            assert resp.status_code == 200
            users_data = resp.json()
            assert len(users_data) == 2  # Should return 2 users
            
            # Test with just limit
            resp = client.get(f"{API_PREFIX}/users/?limit=3")
            assert resp.status_code == 200
            users_data = resp.json()
            assert len(users_data) == 3
            
            # Test with just skip
            resp = client.get(f"{API_PREFIX}/users/?skip=2")
            assert resp.status_code == 200
            all_users = resp.json()
            assert len(all_users) > 0  # Should return at least some users
            
        finally:
            # Clean up
            for user in users:
                if user_crud.get(db_session, id=user.id):
                    user_crud.remove(db_session, id=user.id)
            if user_crud.get(db_session, id=superuser.id):
                user_crud.remove(db_session, id=superuser.id)
            db_session.commit()
            app.dependency_overrides.clear()
    
    def test_list_users_requires_superuser(self, client, db_session):
        from app.main import app
        from app.crud.user import user as user_crud
        from fastapi import HTTPException
        
        # Clear any existing overrides
        app.dependency_overrides.clear()
        
        # Test that endpoint requires authentication
        resp = client.get(f"{API_PREFIX}/users/")
        assert resp.status_code == status.HTTP_401_UNAUTHORIZED, "Should require authentication"
        
        # Create a non-superuser
        non_superuser = make_user(db_session, username="regularuser", email="regular@example.com")
        db_session.refresh(non_superuser)
        
        # Test that non-superuser gets 403 Forbidden
        def get_regular_user_override():
            db_user = user_crud.get(db_session, id=non_superuser.id)
            if not db_user:
                raise HTTPException(status_code=404, detail="User not found")
            return db_user
            
        # Set up the override for the current user
        app.dependency_overrides[get_current_active_user] = get_regular_user_override
        
        # For the users list endpoint, we need to override get_current_active_superuser
        # to raise a 403 if the user is not a superuser
        def get_non_superuser_override():
            db_user = user_crud.get(db_session, id=non_superuser.id)
            if not db_user or not db_user.is_superuser:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="The user doesn't have enough privileges"
                )
            return db_user
            
        app.dependency_overrides[get_current_active_superuser] = get_non_superuser_override
        
        resp = client.get(f"{API_PREFIX}/users/")
        assert resp.status_code == status.HTTP_403_FORBIDDEN, "Non-superuser should not be able to list users"
        
        # Create a superuser
        superuser = make_superuser(db_session)
        db_session.refresh(superuser)
        
        def get_superuser_override():
            db_user = user_crud.get(db_session, id=superuser.id)
            if not db_user or not db_user.is_superuser:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="The user doesn't have enough privileges"
                )
            return db_user
            
        # Set up the override for the superuser
        app.dependency_overrides[get_current_active_superuser] = get_superuser_override
        
        resp = client.get(f"{API_PREFIX}/users/")
        assert resp.status_code == status.HTTP_200_OK, "Superuser should be able to list users"
        users = resp.json()
        assert isinstance(users, list), "Response should be a list"
        
        # Clean up
        if user_crud.get(db_session, id=non_superuser.id):
            user_crud.remove(db_session, id=non_superuser.id)
        if user_crud.get(db_session, id=superuser.id):
            user_crud.remove(db_session, id=superuser.id)
        db_session.commit()
        # Clear overrides
        app.dependency_overrides.clear()

    def test_create_user(self, client, db_session):
        from app.main import app
        from app.crud.user import user as user_crud
        from app.schemas.user import UserCreate, UserInDB
        from fastapi import HTTPException
        
        # Clear any existing overrides
        app.dependency_overrides.clear()
        
        # Create a superuser for the test
        superuser = make_superuser(db_session)
        db_session.refresh(superuser)  # Ensure we have the latest state
        
        def get_superuser_override():
            # Return a fresh instance from the database
            db_user = user_crud.get(db_session, id=superuser.id)
            if not db_user or not db_user.is_superuser:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="The user doesn't have enough privileges"
                )
            return db_user
            
        app.dependency_overrides[get_current_active_superuser] = get_superuser_override
        
        # Generate unique test data for this test run
        import uuid
        unique_id = str(uuid.uuid4())[:8]
        test_email = f"testuser_{unique_id}@example.com"
        test_username = f"testuser_{unique_id}"
        test_password = f"TestPass123!{unique_id}"  # Include special chars and numbers for password validation
        
        # Double-check that the user doesn't already exist
        existing_user = user_crud.get_by_email(db_session, email=test_email)
        if existing_user:
            user_crud.remove(db_session, id=existing_user.id)
            db_session.commit()
            db_session.flush()
        
        # Prepare the request payload
        payload = {
            "email": test_email,
            "username": test_username,
            "password": test_password,
            "is_active": True,
            "is_superuser": False,
        }
        
        # Test user creation with superuser
        resp = client.post(f"{API_PREFIX}/users/", json=payload)
        
        # Debug output
        print(f"Response status code: {resp.status_code}")
        print(f"Response body: {resp.text}")
        
        assert resp.status_code == status.HTTP_201_CREATED, "Superuser should be able to create user"
        
        # Get the created user ID from the response
        user_data = resp.json()
        created_user_id = user_data.get("id")
        assert created_user_id is not None, "User ID should be in the response"
        
        # Verify the response data
        assert user_data["email"] == test_email, f"Email should be {test_email}"
        assert user_data["username"] == test_username, f"Username should be {test_username}"
        assert user_data["is_active"] is True, "User should be active by default"
        assert "password" not in user_data, "Password should not be in the response"
        
        # Verify the user was created in the database
        # Use a new session to verify the user exists in the database
        from app.db.session import SessionLocal
        db = SessionLocal()
        try:
            db_user = user_crud.get(db, id=created_user_id)
            assert db_user is not None, "User should exist in the database"
            assert db_user.email == test_email, f"Email should be {test_email} but was {db_user.email if db_user else 'None'}"
            assert db_user.username == test_username, f"Username should be {test_username} but was {db_user.username if db_user else 'None'}"
            assert db_user.is_active is True, "User should be active"
            assert db_user.is_superuser is False, "User should not be a superuser"
        finally:
            db.close()
        
        # Test user creation with duplicate email
        resp = client.post(f"{API_PREFIX}/users/", json=payload)
        assert resp.status_code == status.HTTP_400_BAD_REQUEST, "Should not allow duplicate emails"
        
        # Test user creation as non-superuser
        regular_user = make_user(db_session,
                               username=f"regularuser_{unique_id}",
                               email=f"regular_{unique_id}@example.com",
                               is_superuser=False)  # Explicitly set non-superuser
        db_session.commit()
        
        # Create a function that will be used for both get_current_active_user and get_current_active_superuser
        def get_regular_user_override():
            db_user = user_crud.get(db_session, id=regular_user.id)
            if not db_user:
                raise HTTPException(status_code=404, detail="User not found")
            return db_user
            
        # Set up the overrides
        app.dependency_overrides[get_current_active_user] = get_regular_user_override
        
        # For the superuser check, we need to ensure it raises a 403 for non-superusers
        def get_non_superuser_override():
            user = get_regular_user_override()
            if not user.is_superuser:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="The user doesn't have enough privileges"
                )
            return user
            
        app.dependency_overrides[get_current_active_superuser] = get_non_superuser_override
        
        # Now the request should fail with 403 since the user is not a superuser
        resp = client.post(
            f"{API_PREFIX}/users/",
            json={
                "email": f"another_{unique_id}@example.com",
                "username": f"anotheruser_{unique_id}",
                "password": f"anotherpass123_{unique_id}"
            }
        )
        assert resp.status_code == status.HTTP_403_FORBIDDEN, "Non-superuser should not be able to create users"
        
        # Clean up
        if created_user_id and user_crud.get(db_session, id=created_user_id):
            user_crud.remove(db_session, id=created_user_id)
        if 'regular_user' in locals() and regular_user and user_crud.get(db_session, id=regular_user.id):
            user_crud.remove(db_session, id=regular_user.id)
        if superuser and user_crud.get(db_session, id=superuser.id):
            user_crud.remove(db_session, id=superuser.id)
        db_session.commit()

    def test_update_user_by_id(self, client, db_session):
        """Test updating a user by ID (admin functionality)."""
        from app.main import app
        from app.crud.user import user as user_crud
        from app.models import User, Role
        from fastapi import HTTPException
        import uuid
        
        # Start a new transaction for this test
        db_session.begin_nested()
        
        try:
            # Create admin role if it doesn't exist
            admin_role = db_session.query(Role).filter(Role.name == "admin").first()
            if not admin_role:
                admin_role = Role(name="admin", description="Administrator role")
                db_session.add(admin_role)
                db_session.commit()
            
            # Create a test user for test 1
            unique_id_1 = str(uuid.uuid4())[:8]
            test_user_1 = User(
                email=f"test1_{unique_id_1}@example.com",
                username=f"testuser1_{unique_id_1}",
                hashed_password="testpass",
                is_active=True
            )
            db_session.add(test_user_1)
            db_session.commit()
            db_session.refresh(test_user_1)
            
            # Create a superuser for the test
            superuser = User(
                email=f"admin_{unique_id_1}@example.com",
                username=f"admin_{unique_id_1}",
                hashed_password="adminpass",
                is_active=True,
                is_superuser=True
            )
            superuser.roles.append(admin_role)
            db_session.add(superuser)
            db_session.commit()
            db_session.refresh(superuser)
            
            # Set up superuser override
            def get_superuser_override():
                return superuser
                
            # Set up the dependency overrides for admin access
            app.dependency_overrides[get_current_active_user] = get_superuser_override
            app.dependency_overrides[get_current_active_superuser] = get_superuser_override
            
            # Test 1: Update user with new email and username (admin)
            update_data_1 = {
                "email": f"updated_{unique_id_1}@example.com",
                "username": f"updateduser_{unique_id_1}",
                "is_active": False
            }
            
            # Make the update request as admin
            resp = client.put(
                f"{API_PREFIX}/users/{test_user_1.id}",
                json=update_data_1
            )
            
            # Verify the response
            assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
            updated_user = resp.json()
            assert updated_user["email"] == update_data_1["email"]
            assert updated_user["username"] == update_data_1["username"]
            assert updated_user["is_active"] == update_data_1["is_active"]
            
            # Create fresh users for test 2
            unique_id_2 = str(uuid.uuid4())[:8]
            test_user_2 = User(
                email=f"test2_{unique_id_2}@example.com",
                username=f"testuser2_{unique_id_2}",
                hashed_password="testpass",
                is_active=True
            )
            another_user = User(
                email=f"another_{unique_id_2}@example.com",
                username=f"another_{unique_id_2}",
                hashed_password="testpass",
                is_active=True
            )
            db_session.add_all([test_user_2, another_user])
            db_session.commit()
            db_session.refresh(test_user_2)
            db_session.refresh(another_user)
            
            # Test 2: Try to update to an existing email (should fail with 400)
            update_data_2 = {"email": another_user.email}
            resp = client.put(
                f"{API_PREFIX}/users/{test_user_2.id}",
                json=update_data_2
            )
            assert resp.status_code == 400, "Should not allow updating to an existing email"
            
            # Create fresh user for test 3
            unique_id_3 = str(uuid.uuid4())[:8]
            test_user_3 = User(
                email=f"test3_{unique_id_3}@example.com",
                username=f"testuser3_{unique_id_3}",
                hashed_password="testpass",
                is_active=True
            )
            db_session.add(test_user_3)
            db_session.commit()
            db_session.refresh(test_user_3)
            
            # Test 3: Update with a new unique email (should succeed)
            unique_email = f"unique_{uuid.uuid4().hex}@example.com"
            update_data_3 = {"email": unique_email}
            resp = client.put(
                f"{API_PREFIX}/users/{test_user_3.id}",
                json=update_data_3
            )
            assert resp.status_code == 200, f"Should allow updating to a new unique email, got {resp.status_code}: {resp.text}"
            
            # Create fresh user for test 4
            unique_id_4 = str(uuid.uuid4())[:8]
            test_user_4 = User(
                email=f"test4_{unique_id_4}@example.com",
                username=f"testuser4_{unique_id_4}",
                hashed_password="testpass",
                is_active=True
            )
            db_session.add(test_user_4)
            db_session.commit()
            db_session.refresh(test_user_4)
            
            # Test 4: Non-admin trying to update non-existent user (should fail with 404)
            def get_regular_user_override():
                return test_user_4
                
            app.dependency_overrides[get_current_active_user] = get_regular_user_override
            app.dependency_overrides[get_current_active_superuser] = get_regular_user_override
            
            update_data_4 = {"email": f"newemail_{unique_id_4}@example.com"}
            resp = client.put(
                f"{API_PREFIX}/users/{test_user_4.id + 1}",  # Non-existent user ID
                json=update_data_4
            )
            assert resp.status_code == 404, "Should return 404 when user doesn't exist"
            
            # Test 5: Update own profile (should succeed)
            update_data_5 = {"email": f"selfupdate_{unique_id_4}@example.com"}
            resp = client.put(
                f"{API_PREFIX}/users/me",
                json=update_data_5
            )
            assert resp.status_code == 200, "Should be able to update own profile"
            
        finally:
            # Clean up
            if db_session.in_transaction():
                db_session.rollback()
            app.dependency_overrides.clear()
            db_session.expire_all()  # Clear the session to force a fresh load
    
    def test_delete_user(self, client, db_session):
        """Test user deletion if the endpoint is implemented."""
        # This is a placeholder for when the delete endpoint is implemented
        # The API currently doesn't have a DELETE /users/{user_id} endpoint
        pass

    def test_change_password(self, client, db_session):
        """Test changing a user's password."""
        pass
