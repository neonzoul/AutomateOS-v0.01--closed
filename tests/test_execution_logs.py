"""
Test script for execution log functionality.

This script tests the new execution log endpoints and CRUD operations.
"""

import requests
import json
from datetime import datetime

# Configuration
BASE_URL = "http://localhost:8000"
TEST_EMAIL = "test@example.com"
TEST_PASSWORD = "testpassword123"

def test_execution_logs():
    """Test the execution log functionality."""
    
    print("Testing Execution Log Functionality")
    print("=" * 50)
    
    # Step 1: Register and login
    print("1. Registering test user...")
    register_response = requests.post(f"{BASE_URL}/register/", json={
        "email": TEST_EMAIL,
        "password": TEST_PASSWORD
    })
    
    if register_response.status_code == 400:
        print("   User already exists, continuing...")
    elif register_response.status_code == 200:
        print("   User registered successfully")
    else:
        print(f"   Registration failed: {register_response.status_code}")
        return
    
    print("2. Logging in...")
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
    
    # Step 2: Create a test workflow
    print("3. Creating test workflow...")
    workflow_data = {
        "name": "Test Workflow for Logs",
        "description": "A test workflow to generate execution logs",
        "definition": {
            "nodes": [
                {
                    "id": "trigger-1",
                    "type": "webhook",
                    "config": {}
                },
                {
                    "id": "http-1",
                    "type": "http_request",
                    "config": {
                        "url": "https://httpbin.org/post",
                        "method": "POST",
                        "headers": {"Content-Type": "application/json"},
                        "body": {"test": "data"}
                    }
                }
            ],
            "connections": [
                {"from": "trigger-1", "to": "http-1"}
            ]
        },
        "is_active": True
    }
    
    workflow_response = requests.post(f"{BASE_URL}/workflows/", 
                                    json=workflow_data, 
                                    headers=headers)
    
    if workflow_response.status_code != 200:
        print(f"   Workflow creation failed: {workflow_response.status_code}")
        print(f"   Response: {workflow_response.text}")
        return
    
    workflow = workflow_response.json()
    workflow_id = workflow["id"]
    webhook_url = workflow["webhook_url"]
    print(f"   Workflow created with ID: {workflow_id}")
    
    # Step 3: Trigger the workflow to create execution logs
    print("4. Triggering workflow execution...")
    webhook_id = webhook_url.split("/")[-1]
    trigger_response = requests.post(f"{BASE_URL}/webhook/{webhook_id}", json={
        "test_payload": "execution log test",
        "timestamp": datetime.utcnow().isoformat()
    })
    
    if trigger_response.status_code != 200:
        print(f"   Workflow trigger failed: {trigger_response.status_code}")
        print(f"   Response: {trigger_response.text}")
        return
    
    print("   Workflow triggered successfully")
    
    # Wait a moment for execution to complete
    import time
    print("   Waiting for execution to complete...")
    time.sleep(3)
    
    # Step 4: Test execution log endpoints
    print("5. Testing execution log endpoints...")
    
    # Test getting execution logs for the workflow
    print("   5.1 Getting execution logs...")
    logs_response = requests.get(f"{BASE_URL}/workflows/{workflow_id}/logs", 
                                headers=headers)
    
    if logs_response.status_code != 200:
        print(f"   Failed to get logs: {logs_response.status_code}")
        print(f"   Response: {logs_response.text}")
        return
    
    logs = logs_response.json()
    print(f"   Found {len(logs)} execution logs")
    
    if logs:
        log = logs[0]
        print(f"   Latest log status: {log['status']}")
        print(f"   Latest log started at: {log['started_at']}")
        
        # Test getting detailed log information
        print("   5.2 Getting detailed log information...")
        log_detail_response = requests.get(f"{BASE_URL}/logs/{log['id']}", 
                                         headers=headers)
        
        if log_detail_response.status_code != 200:
            print(f"   Failed to get log details: {log_detail_response.status_code}")
        else:
            log_detail = log_detail_response.json()
            print(f"   Log detail retrieved successfully")
            print(f"   Payload keys: {list(log_detail['payload'].keys())}")
            if log_detail['result']:
                print(f"   Result available: {bool(log_detail['result'])}")
    
    # Test getting log count
    print("   5.3 Getting log count...")
    count_response = requests.get(f"{BASE_URL}/workflows/{workflow_id}/logs/count", 
                                headers=headers)
    
    if count_response.status_code != 200:
        print(f"   Failed to get log count: {count_response.status_code}")
    else:
        count = count_response.json()["count"]
        print(f"   Total log count: {count}")
    
    # Test status filtering
    print("   5.4 Testing status filtering...")
    for status in ["success", "failed", "running"]:
        status_logs_response = requests.get(
            f"{BASE_URL}/workflows/{workflow_id}/logs?status={status}", 
            headers=headers
        )
        
        if status_logs_response.status_code == 200:
            status_logs = status_logs_response.json()
            print(f"   {status} logs: {len(status_logs)}")
    
    # Test pagination
    print("   5.5 Testing pagination...")
    paginated_response = requests.get(
        f"{BASE_URL}/workflows/{workflow_id}/logs?limit=1&offset=0", 
        headers=headers
    )
    
    if paginated_response.status_code == 200:
        paginated_logs = paginated_response.json()
        print(f"   Paginated logs (limit=1): {len(paginated_logs)}")
    
    print("\n✅ Execution log functionality test completed successfully!")

if __name__ == "__main__":
    test_execution_logs()