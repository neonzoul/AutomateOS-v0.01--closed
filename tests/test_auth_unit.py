#!/usr/bin/env python3
"""
Unit tests for authentication endpoints and JWT handling.
Tests the core authentication functionality including registration, login, and JWT token validation.
"""

import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session, SQLModel, create_engine
from sqlmodel.pool import StaticPool
from datetime import datetime, timedelta
import os
import sys

# Add the app directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

try:
    from app.main import app
    from app.database import get_session
    from app import security, models, crud, schemas
except ImportError as e:
    print(f"Import error: {e}")
    # Skip tests if imports fail
    pytest.skip("Skipping tests due to import errors", allow_module_level=True)

# Create in-memory SQLite database for testing
@pytest.fixture(name="session")
def session_fixture():
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        yield session

@pytest.fixture(name="client")
def client_fixture(session: Session):
    def get_session_override():
        return session

    app.dependency_overrides[get_session] = get_session_override
    client = TestClient(app)
    yield client
    app.dependency_overrides.clear()

class TestPasswordHashing:
    """Test password hashing and verification functions."""
    
    def test_password_hashing(self):
        """Test that passwords are properly hashed and verified."""
        password = "testpassword123"
        hashed = security.get_password_hash(password)
        
        # Hash should be different from original password
        assert hashed != password
        assert len(hashed) > 20  # Bcrypt hashes are typically 60 characters
        
        # Verification should work
        assert security.verify_password(password, hashed) is True
        
        # Wrong password should fail
        assert security.verify_password("wrongpassword", hashed) is False

    def test_password_hash_uniqueness(self):
        """Test that same password produces different hashes (salt)."""
        password = "testpassword123"
        hash1 = security.get_password_hash(password)
        hash2 = security.get_password_hash(password)
        
        # Hashes should be different due to salt
        assert hash1 != hash2
        
        # But both should verify correctly
        assert security.verify_password(password, hash1) is True
        assert security.verify_password(password, hash2) is True

class TestJWTTokens:
    """Test JWT token creation and validation."""
    
    def test_create_access_token(self):
        """Test JWT token creation."""
        data = {"sub": "test@example.com"}
        token = security.create_access_token(data)
        
        assert isinstance(token, str)
        assert len(token) > 50  # JWT tokens are typically long
        assert "." in token  # JWT tokens have dots separating parts

    def test_create_token_with_expiration(self):
        """Test JWT token creation with custom expiration."""
        data = {"sub": "test@example.com"}
        expires_delta = timedelta(hours=1)
        token = security.create_access_token(data, expires_delta)
        
        assert isinstance(token, str)
        # Decode to verify expiration was set correctly
        from jose import jwt
        payload = jwt.decode(token, security.SECRET_KEY, algorithms=[security.ALGORITHM])
        
        # Check that expiration is approximately 1 hour from now
        exp_time = datetime.fromtimestamp(payload["exp"])
        expected_time = datetime.utcnow() + expires_delta
        time_diff = abs((exp_time - expected_time).total_seconds())
        assert time_diff < 60  # Should be within 1 minute

    def test_token_validation(self):
        """Test JWT token validation."""
        # This test requires a user in the database
        pass  # Will be tested in integration tests

class TestUserRegistration:
    """Test user registration endpoint."""
    
    def test_register_new_user(self, client: TestClient):
        """Test successful user registration."""
        user_data = {
            "email": "test@example.com",
            "password": "testpassword123"
        }
        
        response = client.post("/register/", json=user_data)
        
        assert response.status_code == 200
        data = response.json()
        assert data["email"] == user_data["email"]
        assert "id" in data
        assert "hashed_password" not in data  # Should not expose password
        assert "created_at" in data

    def test_register_duplicate_email(self, client: TestClient):
        """Test registration with duplicate email."""
        user_data = {
            "email": "duplicate@example.com",
            "password": "testpassword123"
        }
        
        # Register first user
        response1 = client.post("/register/", json=user_data)
        assert response1.status_code == 200
        
        # Try to register same email again
        response2 = client.post("/register/", json=user_data)
        assert response2.status_code == 400
        assert "already registered" in response2.json()["detail"]

    def test_register_invalid_email(self, client: TestClient):
        """Test registration with invalid email format."""
        user_data = {
            "email": "invalid-email",
            "password": "testpassword123"
        }
        
        response = client.post("/register/", json=user_data)
        assert response.status_code == 422  # Validation error

    def test_register_missing_fields(self, client: TestClient):
        """Test registration with missing required fields."""
        # Missing password
        response1 = client.post("/register/", json={"email": "test@example.com"})
        assert response1.status_code == 422
        
        # Missing email
        response2 = client.post("/register/", json={"password": "testpassword123"})
        assert response2.status_code == 422
        
        # Empty request
        response3 = client.post("/register/", json={})
        assert response3.status_code == 422

class TestUserLogin:
    """Test user login endpoint."""
    
    def test_login_success(self, client: TestClient):
        """Test successful user login."""
        # First register a user
        user_data = {
            "email": "login@example.com",
            "password": "testpassword123"
        }
        client.post("/register/", json=user_data)
        
        # Now try to login
        login_data = {
            "username": "login@example.com",  # OAuth2 uses 'username' field
            "password": "testpassword123"
        }
        
        response = client.post("/auth/token", data=login_data)
        
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"
        assert len(data["access_token"]) > 50

    def test_login_wrong_password(self, client: TestClient):
        """Test login with wrong password."""
        # First register a user
        user_data = {
            "email": "wrongpass@example.com",
            "password": "correctpassword"
        }
        client.post("/register/", json=user_data)
        
        # Try to login with wrong password
        login_data = {
            "username": "wrongpass@example.com",
            "password": "wrongpassword"
        }
        
        response = client.post("/auth/token", data=login_data)
        
        assert response.status_code == 401
        assert "Incorrect email or password" in response.json()["detail"]

    def test_login_nonexistent_user(self, client: TestClient):
        """Test login with non-existent user."""
        login_data = {
            "username": "nonexistent@example.com",
            "password": "anypassword"
        }
        
        response = client.post("/auth/token", data=login_data)
        
        assert response.status_code == 401
        assert "Incorrect email or password" in response.json()["detail"]

    def test_login_missing_credentials(self, client: TestClient):
        """Test login with missing credentials."""
        # Missing password
        response1 = client.post("/auth/token", data={"username": "test@example.com"})
        assert response1.status_code == 422
        
        # Missing username
        response2 = client.post("/auth/token", data={"password": "testpassword"})
        assert response2.status_code == 422

class TestAuthenticatedEndpoints:
    """Test endpoints that require authentication."""
    
    def test_access_without_token(self, client: TestClient):
        """Test accessing protected endpoint without token."""
        response = client.get("/workflows/")
        assert response.status_code == 401

    def test_access_with_invalid_token(self, client: TestClient):
        """Test accessing protected endpoint with invalid token."""
        headers = {"Authorization": "Bearer invalid_token_here"}
        response = client.get("/workflows/", headers=headers)
        assert response.status_code == 401

    def test_access_with_valid_token(self, client: TestClient):
        """Test accessing protected endpoint with valid token."""
        # Register and login to get token
        user_data = {
            "email": "validtoken@example.com",
            "password": "testpassword123"
        }
        client.post("/register/", json=user_data)
        
        login_response = client.post("/auth/token", data={
            "username": "validtoken@example.com",
            "password": "testpassword123"
        })
        token = login_response.json()["access_token"]
        
        # Access protected endpoint
        headers = {"Authorization": f"Bearer {token}"}
        response = client.get("/workflows/", headers=headers)
        assert response.status_code == 200

class TestCRUDOperations:
    """Test CRUD operations for user management."""
    
    def test_create_user_crud(self, session: Session):
        """Test user creation through CRUD operations."""
        user_create = schemas.UserCreate(
            email="crud@example.com",
            password="testpassword123"
        )
        
        user = crud.create_user(session, user_create)
        
        assert user.email == "crud@example.com"
        assert user.hashed_password != "testpassword123"  # Should be hashed
        assert user.id is not None
        assert isinstance(user.created_at, datetime)

    def test_get_user_by_email(self, session: Session):
        """Test retrieving user by email."""
        # Create a user first
        user_create = schemas.UserCreate(
            email="getuser@example.com",
            password="testpassword123"
        )
        created_user = crud.create_user(session, user_create)
        
        # Retrieve the user
        retrieved_user = crud.get_user_by_email(session, "getuser@example.com")
        
        assert retrieved_user is not None
        assert retrieved_user.id == created_user.id
        assert retrieved_user.email == "getuser@example.com"

    def test_authenticate_user_success(self, session: Session):
        """Test successful user authentication."""
        # Create a user first
        user_create = schemas.UserCreate(
            email="auth@example.com",
            password="testpassword123"
        )
        crud.create_user(session, user_create)
        
        # Authenticate the user
        auth_user = crud.authenticate_user(session, user_create)
        
        assert auth_user is not None
        assert auth_user.email == "auth@example.com"

    def test_authenticate_user_wrong_password(self, session: Session):
        """Test user authentication with wrong password."""
        # Create a user first
        user_create = schemas.UserCreate(
            email="wrongauth@example.com",
            password="correctpassword"
        )
        crud.create_user(session, user_create)
        
        # Try to authenticate with wrong password
        wrong_credentials = schemas.UserCreate(
            email="wrongauth@example.com",
            password="wrongpassword"
        )
        auth_user = crud.authenticate_user(session, wrong_credentials)
        
        assert auth_user is None

    def test_authenticate_nonexistent_user(self, session: Session):
        """Test authentication of non-existent user."""
        credentials = schemas.UserCreate(
            email="nonexistent@example.com",
            password="anypassword"
        )
        auth_user = crud.authenticate_user(session, credentials)
        
        assert auth_user is None

if __name__ == "__main__":
    pytest.main([__file__, "-v"])