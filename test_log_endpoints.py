"""
Simple test for execution log endpoints without workflow execution.

This test creates a mock execution log directly in the database
and tests the retrieval endpoints.
"""

import requests
import json
from datetime import datetime
from sqlmodel import Session, create_engine
from app.database import get_session
from app import models, crud, schemas

# Configuration
BASE_URL = "http://localhost:8000"
TEST_EMAIL = "test@example.com"
TEST_PASSWORD = "testpassword123"

def create_mock_execution_log():
    """Create a mock execution log directly in the database."""
    session = next(get_session())
    
    try:
        # Get the test user
        user = crud.get_user_by_email(session, TEST_EMAIL)
        if not user:
            print("Test user not found, creating...")
            user = crud.create_user(session, schemas.UserCreate(
                email=TEST_EMAIL,
                password=TEST_PASSWORD
            ))
        
        # Get or create a test workflow
        workflows = crud.get_workflows_by_owner(session, user.id)
        if workflows:
            workflow = workflows[0]
        else:
            print("Creating test workflow...")
            workflow = crud.create_workflow(session, schemas.WorkflowCreate(
                name="Test Workflow for Log Endpoints",
                description="A test workflow for testing log endpoints",
                definition={"nodes": [{"id": "test", "type": "webhook", "config": {}}]},
                is_active=True
            ), user.id)
        
        # Create mock execution logs
        print("Creating mock execution logs...")
        
        # Success log
        success_log = models.ExecutionLog(
            workflow_id=workflow.id,
            status="success",
            payload={"test": "success payload"},
            result={"status": "completed", "output": "success result"},
            started_at=datetime.utcnow(),
            completed_at=datetime.utcnow()
        )
        session.add(success_log)
        
        # Failed log
        failed_log = models.ExecutionLog(
            workflow_id=workflow.id,
            status="failed",
            payload={"test": "failed payload"},
            error_message="Test error message",
            started_at=datetime.utcnow(),
            completed_at=datetime.utcnow()
        )
        session.add(failed_log)
        
        # Running log
        running_log = models.ExecutionLog(
            workflow_id=workflow.id,
            status="running",
            payload={"test": "running payload"},
            started_at=datetime.utcnow()
        )
        session.add(running_log)
        
        session.commit()
        
        print(f"Created mock logs for workflow {workflow.id}")
        return workflow.id, user
        
    finally:
        session.close()

def test_log_endpoints():
    """Test the execution log endpoints."""
    
    print("Testing Execution Log Endpoints")
    print("=" * 40)
    
    # Create mock data
    workflow_id, user = create_mock_execution_log()
    
    # Login to get token
    print("1. Logging in...")
    login_response = requests.post(f"{BASE_URL}/auth/token", data={
        "username": TEST_EMAIL,
        "password": TEST_PASSWORD
    })
    
    if login_response.status_code != 200:
        print(f"   Login failed: {login_response.status_code}")
        return
    
    token = login_response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    print("   Login successful")
    
    # Test getting execution logs
    print("2. Testing execution log retrieval...")
    logs_response = requests.get(f"{BASE_URL}/workflows/{workflow_id}/logs", 
                                headers=headers)
    
    if logs_response.status_code != 200:
        print(f"   Failed to get logs: {logs_response.status_code}")
        print(f"   Response: {logs_response.text}")
        return
    
    logs = logs_response.json()
    print(f"   Found {len(logs)} execution logs")
    
    for log in logs:
        print(f"   - Log {log['id']}: {log['status']} (started: {log['started_at']})")
    
    # Test getting detailed log information
    if logs:
        print("3. Testing detailed log retrieval...")
        log_id = logs[0]['id']
        log_detail_response = requests.get(f"{BASE_URL}/logs/{log_id}", 
                                         headers=headers)
        
        if log_detail_response.status_code != 200:
            print(f"   Failed to get log details: {log_detail_response.status_code}")
        else:
            log_detail = log_detail_response.json()
            print(f"   Log detail retrieved successfully")
            print(f"   Status: {log_detail['status']}")
            print(f"   Payload keys: {list(log_detail['payload'].keys())}")
    
    # Test getting log count
    print("4. Testing log count...")
    count_response = requests.get(f"{BASE_URL}/workflows/{workflow_id}/logs/count", 
                                headers=headers)
    
    if count_response.status_code != 200:
        print(f"   Failed to get log count: {count_response.status_code}")
    else:
        count = count_response.json()["count"]
        print(f"   Total log count: {count}")
    
    # Test status filtering
    print("5. Testing status filtering...")
    for status in ["success", "failed", "running"]:
        status_logs_response = requests.get(
            f"{BASE_URL}/workflows/{workflow_id}/logs?status={status}", 
            headers=headers
        )
        
        if status_logs_response.status_code == 200:
            status_logs = status_logs_response.json()
            print(f"   {status} logs: {len(status_logs)}")
        else:
            print(f"   Failed to get {status} logs: {status_logs_response.status_code}")
    
    # Test pagination
    print("6. Testing pagination...")
    paginated_response = requests.get(
        f"{BASE_URL}/workflows/{workflow_id}/logs?limit=2&offset=0", 
        headers=headers
    )
    
    if paginated_response.status_code == 200:
        paginated_logs = paginated_response.json()
        print(f"   Paginated logs (limit=2): {len(paginated_logs)}")
    else:
        print(f"   Pagination test failed: {paginated_response.status_code}")
    
    # Test log cleanup
    print("7. Testing log cleanup...")
    cleanup_response = requests.delete(f"{BASE_URL}/logs/cleanup?days_to_keep=0", 
                                     headers=headers)
    
    if cleanup_response.status_code == 200:
        cleanup_result = cleanup_response.json()
        print(f"   Cleanup completed: {cleanup_result['deleted_count']} logs deleted")
    else:
        print(f"   Cleanup test failed: {cleanup_response.status_code}")
    
    print("\n✅ Execution log endpoint tests completed!")

if __name__ == "__main__":
    test_log_endpoints()