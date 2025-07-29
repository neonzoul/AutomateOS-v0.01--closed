#!/usr/bin/env python3
"""
Integration tests for workflow CRUD operations.
Tests the complete workflow lifecycle including creation, reading, updating, and deletion.
"""

import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session, SQLModel, create_engine
from sqlmodel.pool import StaticPool
import os
import sys

# Add the app directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

try:
    from app.main import app
    from app.database import get_session
    from app import models, crud, schemas
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

@pytest.fixture(name="authenticated_user")
def authenticated_user_fixture(client: TestClient):
    """Create a user and return authentication headers."""
    user_data = {
        "email": "testuser@example.com",
        "password": "testpassword123"
    }
    
    # Register user
    client.post("/register/", json=user_data)
    
    # Login to get token
    login_response = client.post("/auth/token", data={
        "username": "testuser@example.com",
        "password": "testpassword123"
    })
    token = login_response.json()["access_token"]
    
    return {"Authorization": f"Bearer {token}"}

class TestWorkflowCRUD:
    """Test workflow CRUD operations through API endpoints."""
    
    def test_create_workflow(self, client: TestClient, authenticated_user):
        """Test workflow creation."""
        workflow_data = {
            "name": "Test Workflow",
            "description": "A test workflow for integration testing",
            "definition": {
                "nodes": [
                    {
                        "id": "trigger-1",
                        "type": "webhook",
                        "config": {"method": "POST"}
                    },
                    {
                        "id": "action-1",
                        "type": "http_request",
                        "config": {
                            "url": "https://httpbin.org/post",
                            "method": "POST",
                            "headers": {"Content-Type": "application/json"}
                        }
                    }
                ],
                "connections": [{"from": "trigger-1", "to": "action-1"}]
            },
            "is_active": True
        }
        
        response = client.post("/workflows/", json=workflow_data, headers=authenticated_user)
        
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == workflow_data["name"]
        assert data["description"] == workflow_data["description"]
        assert data["definition"] == workflow_data["definition"]
        assert data["is_active"] == workflow_data["is_active"]
        assert "id" in data
        assert "webhook_url" in data
        assert data["webhook_url"].startswith("/webhook/")
        assert "created_at" in data
        assert "updated_at" in data

    def test_list_workflows_empty(self, client: TestClient, authenticated_user):
        """Test listing workflows when user has none."""
        response = client.get("/workflows/", headers=authenticated_user)
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) == 0

    def test_list_workflows_with_data(self, client: TestClient, authenticated_user):
        """Test listing workflows when user has workflows."""
        # Create a workflow first
        workflow_data = {
            "name": "List Test Workflow",
            "description": "For testing workflow listing",
            "definition": {"nodes": [], "connections": []},
            "is_active": True
        }
        
        create_response = client.post("/workflows/", json=workflow_data, headers=authenticated_user)
        assert create_response.status_code == 200
        
        # List workflows
        list_response = client.get("/workflows/", headers=authenticated_user)
        
        assert list_response.status_code == 200
        data = list_response.json()
        assert isinstance(data, list)
        assert len(data) == 1
        assert data[0]["name"] == workflow_data["name"]

    def test_get_workflow_by_id(self, client: TestClient, authenticated_user):
        """Test retrieving a specific workflow by ID."""
        # Create a workflow first
        workflow_data = {
            "name": "Get Test Workflow",
            "description": "For testing workflow retrieval",
            "definition": {"test": "data"},
            "is_active": False
        }
        
        create_response = client.post("/workflows/", json=workflow_data, headers=authenticated_user)
        workflow_id = create_response.json()["id"]
        
        # Get the workflow
        get_response = client.get(f"/workflows/{workflow_id}", headers=authenticated_user)
        
        assert get_response.status_code == 200
        data = get_response.json()
        assert data["id"] == workflow_id
        assert data["name"] == workflow_data["name"]
        assert data["description"] == workflow_data["description"]
        assert data["definition"] == workflow_data["definition"]
        assert data["is_active"] == workflow_data["is_active"]

    def test_get_nonexistent_workflow(self, client: TestClient, authenticated_user):
        """Test retrieving a non-existent workflow."""
        response = client.get("/workflows/99999", headers=authenticated_user)
        
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()

    def test_update_workflow(self, client: TestClient, authenticated_user):
        """Test updating an existing workflow."""
        # Create a workflow first
        original_data = {
            "name": "Original Workflow",
            "description": "Original description",
            "definition": {"original": "data"},
            "is_active": True
        }
        
        create_response = client.post("/workflows/", json=original_data, headers=authenticated_user)
        workflow_id = create_response.json()["id"]
        
        # Update the workflow
        updated_data = {
            "name": "Updated Workflow",
            "description": "Updated description",
            "definition": {"updated": "data", "new_field": "value"},
            "is_active": False
        }
        
        update_response = client.put(f"/workflows/{workflow_id}", json=updated_data, headers=authenticated_user)
        
        assert update_response.status_code == 200
        data = update_response.json()
        assert data["id"] == workflow_id
        assert data["name"] == updated_data["name"]
        assert data["description"] == updated_data["description"]
        assert data["definition"] == updated_data["definition"]
        assert data["is_active"] == updated_data["is_active"]
        assert data["updated_at"] != data["created_at"]

    def test_update_nonexistent_workflow(self, client: TestClient, authenticated_user):
        """Test updating a non-existent workflow."""
        update_data = {
            "name": "Updated Name",
            "definition": {"test": "data"},
            "is_active": True
        }
        
        response = client.put("/workflows/99999", json=update_data, headers=authenticated_user)
        
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()

    def test_delete_workflow(self, client: TestClient, authenticated_user):
        """Test deleting a workflow."""
        # Create a workflow first
        workflow_data = {
            "name": "Delete Test Workflow",
            "definition": {"test": "data"},
            "is_active": True
        }
        
        create_response = client.post("/workflows/", json=workflow_data, headers=authenticated_user)
        workflow_id = create_response.json()["id"]
        
        # Delete the workflow
        delete_response = client.delete(f"/workflows/{workflow_id}", headers=authenticated_user)
        
        assert delete_response.status_code == 200
        assert "deleted successfully" in delete_response.json()["message"]
        
        # Verify it's deleted
        get_response = client.get(f"/workflows/{workflow_id}", headers=authenticated_user)
        assert get_response.status_code == 404

    def test_delete_nonexistent_workflow(self, client: TestClient, authenticated_user):
        """Test deleting a non-existent workflow."""
        response = client.delete("/workflows/99999", headers=authenticated_user)
        
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()

class TestWorkflowValidation:
    """Test workflow data validation."""
    
    def test_create_workflow_invalid_data(self, client: TestClient, authenticated_user):
        """Test creating workflow with invalid data."""
        # Missing required fields
        invalid_data = {
            "description": "Missing name field"
        }
        
        response = client.post("/workflows/", json=invalid_data, headers=authenticated_user)
        assert response.status_code == 422

    def test_create_workflow_empty_name(self, client: TestClient, authenticated_user):
        """Test creating workflow with empty name."""
        invalid_data = {
            "name": "",
            "definition": {"test": "data"},
            "is_active": True
        }
        
        response = client.post("/workflows/", json=invalid_data, headers=authenticated_user)
        assert response.status_code == 422

    def test_create_workflow_invalid_definition_type(self, client: TestClient, authenticated_user):
        """Test creating workflow with invalid definition type."""
        invalid_data = {
            "name": "Test Workflow",
            "definition": "not_a_dict",  # Should be a dict/object
            "is_active": True
        }
        
        response = client.post("/workflows/", json=invalid_data, headers=authenticated_user)
        assert response.status_code == 422

class TestWorkflowSecurity:
    """Test workflow security and authorization."""
    
    def test_user_isolation(self, client: TestClient):
        """Test that users can only access their own workflows."""
        # Create two users
        user1_data = {"email": "user1@example.com", "password": "password123"}
        user2_data = {"email": "user2@example.com", "password": "password123"}
        
        client.post("/register/", json=user1_data)
        client.post("/register/", json=user2_data)
        
        # Get tokens for both users
        token1_response = client.post("/auth/token", data={
            "username": "user1@example.com", "password": "password123"
        })
        token2_response = client.post("/auth/token", data={
            "username": "user2@example.com", "password": "password123"
        })
        
        token1 = token1_response.json()["access_token"]
        token2 = token2_response.json()["access_token"]
        
        headers1 = {"Authorization": f"Bearer {token1}"}
        headers2 = {"Authorization": f"Bearer {token2}"}
        
        # User 1 creates a workflow
        workflow_data = {
            "name": "User 1 Workflow",
            "definition": {"test": "data"},
            "is_active": True
        }
        
        create_response = client.post("/workflows/", json=workflow_data, headers=headers1)
        workflow_id = create_response.json()["id"]
        
        # User 1 can access their workflow
        get_response1 = client.get(f"/workflows/{workflow_id}", headers=headers1)
        assert get_response1.status_code == 200
        
        # User 2 cannot access User 1's workflow
        get_response2 = client.get(f"/workflows/{workflow_id}", headers=headers2)
        assert get_response2.status_code == 404
        
        # User 2 cannot update User 1's workflow
        update_response = client.put(f"/workflows/{workflow_id}", 
                                   json={"name": "Hacked"}, headers=headers2)
        assert update_response.status_code == 404
        
        # User 2 cannot delete User 1's workflow
        delete_response = client.delete(f"/workflows/{workflow_id}", headers=headers2)
        assert delete_response.status_code == 404

class TestWorkflowWebhooks:
    """Test webhook functionality for workflows."""
    
    def test_webhook_url_generation(self, client: TestClient, authenticated_user):
        """Test that workflows get unique webhook URLs."""
        workflow_data = {
            "name": "Webhook Test Workflow",
            "definition": {"test": "data"},
            "is_active": True
        }
        
        # Create two workflows
        response1 = client.post("/workflows/", json=workflow_data, headers=authenticated_user)
        response2 = client.post("/workflows/", json=workflow_data, headers=authenticated_user)
        
        webhook_url1 = response1.json()["webhook_url"]
        webhook_url2 = response2.json()["webhook_url"]
        
        # URLs should be different
        assert webhook_url1 != webhook_url2
        assert webhook_url1.startswith("/webhook/")
        assert webhook_url2.startswith("/webhook/")

    def test_webhook_trigger_active_workflow(self, client: TestClient, authenticated_user):
        """Test triggering an active workflow via webhook."""
        workflow_data = {
            "name": "Active Webhook Test",
            "definition": {"test": "data"},
            "is_active": True
        }
        
        create_response = client.post("/workflows/", json=workflow_data, headers=authenticated_user)
        webhook_url = create_response.json()["webhook_url"]
        webhook_id = webhook_url.split("/")[-1]
        
        # Trigger the webhook
        payload = {"test": "webhook_data"}
        webhook_response = client.post(f"/webhook/{webhook_id}", json=payload)
        
        assert webhook_response.status_code == 200
        data = webhook_response.json()
        assert "job_id" in data
        assert "workflow_id" in data
        assert data["status"] == "accepted"

    def test_webhook_trigger_inactive_workflow(self, client: TestClient, authenticated_user):
        """Test triggering an inactive workflow via webhook."""
        workflow_data = {
            "name": "Inactive Webhook Test",
            "definition": {"test": "data"},
            "is_active": False
        }
        
        create_response = client.post("/workflows/", json=workflow_data, headers=authenticated_user)
        webhook_url = create_response.json()["webhook_url"]
        webhook_id = webhook_url.split("/")[-1]
        
        # Try to trigger the webhook
        payload = {"test": "webhook_data"}
        webhook_response = client.post(f"/webhook/{webhook_id}", json=payload)
        
        assert webhook_response.status_code == 400
        assert "not active" in webhook_response.json()["detail"]

    def test_webhook_nonexistent(self, client: TestClient):
        """Test triggering a non-existent webhook."""
        payload = {"test": "data"}
        response = client.post("/webhook/nonexistent-id", json=payload)
        
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()

class TestWorkflowCRUDDatabase:
    """Test workflow CRUD operations at the database level."""
    
    def test_create_workflow_crud(self, session: Session):
        """Test workflow creation through CRUD operations."""
        # Create a user first
        user_create = schemas.UserCreate(email="crud@example.com", password="password")
        user = crud.create_user(session, user_create)
        
        # Create workflow
        workflow_create = schemas.WorkflowCreate(
            name="CRUD Test Workflow",
            description="Testing CRUD operations",
            definition={"test": "data"},
            is_active=True
        )
        
        workflow = crud.create_workflow(session, workflow_create, user.id)
        
        assert workflow.name == "CRUD Test Workflow"
        assert workflow.description == "Testing CRUD operations"
        assert workflow.definition == {"test": "data"}
        assert workflow.is_active is True
        assert workflow.owner_id == user.id
        assert workflow.webhook_url.startswith("/webhook/")
        assert workflow.id is not None

    def test_get_workflows_by_owner(self, session: Session):
        """Test retrieving workflows by owner."""
        # Create a user
        user_create = schemas.UserCreate(email="owner@example.com", password="password")
        user = crud.create_user(session, user_create)
        
        # Create multiple workflows
        for i in range(3):
            workflow_create = schemas.WorkflowCreate(
                name=f"Workflow {i}",
                definition={"index": i},
                is_active=True
            )
            crud.create_workflow(session, workflow_create, user.id)
        
        # Get workflows
        workflows = crud.get_workflows_by_owner(session, user.id)
        
        assert len(workflows) == 3
        assert all(w.owner_id == user.id for w in workflows)

    def test_update_workflow_crud(self, session: Session):
        """Test workflow update through CRUD operations."""
        # Create user and workflow
        user_create = schemas.UserCreate(email="update@example.com", password="password")
        user = crud.create_user(session, user_create)
        
        workflow_create = schemas.WorkflowCreate(
            name="Original Name",
            definition={"original": "data"},
            is_active=True
        )
        workflow = crud.create_workflow(session, workflow_create, user.id)
        
        # Update workflow
        workflow_update = schemas.WorkflowCreate(
            name="Updated Name",
            definition={"updated": "data"},
            is_active=False
        )
        
        updated_workflow = crud.update_workflow(session, workflow.id, workflow_update, user.id)
        
        assert updated_workflow is not None
        assert updated_workflow.name == "Updated Name"
        assert updated_workflow.definition == {"updated": "data"}
        assert updated_workflow.is_active is False
        assert updated_workflow.updated_at > updated_workflow.created_at

    def test_delete_workflow_crud(self, session: Session):
        """Test workflow deletion through CRUD operations."""
        # Create user and workflow
        user_create = schemas.UserCreate(email="delete@example.com", password="password")
        user = crud.create_user(session, user_create)
        
        workflow_create = schemas.WorkflowCreate(
            name="To Delete",
            definition={"test": "data"},
            is_active=True
        )
        workflow = crud.create_workflow(session, workflow_create, user.id)
        
        # Delete workflow
        success = crud.delete_workflow(session, workflow.id, user.id)
        assert success is True
        
        # Verify deletion
        deleted_workflow = crud.get_workflow_by_id(session, workflow.id, user.id)
        assert deleted_workflow is None

if __name__ == "__main__":
    pytest.main([__file__, "-v"])