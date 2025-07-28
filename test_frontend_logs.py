"""
Test script for frontend execution log functionality.

This script tests the frontend log visualization by creating test data
and verifying the API endpoints work correctly.
"""

import requests
import json
from datetime import datetime

# Configuration
BASE_URL = "http://localhost:8000"
FRONTEND_URL = "http://localhost:5173"
TEST_EMAIL = "frontend_test@example.com"
TEST_PASSWORD = "testpassword123"

def test_frontend_log_integration():
    """Test the frontend log integration with backend APIs."""
    
    print("Testing Frontend Log Integration")
    print("=" * 50)
    
    # Step 1: Register and login
    print("1. Setting up test user...")
    try:
        register_response = requests.post(f"{BASE_URL}/register/", json={
            "email": TEST_EMAIL,
            "password": TEST_PASSWORD
        })
        if register_response.status_code == 400:
            print("   User already exists, continuing...")
        else:
            print("   User registered successfully")
    except Exception as e:
        print(f"   Registration error: {e}")
    
    # Login
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
    print("2. Creating test workflow...")
    workflow_data = {
        "name": "Frontend Log Test Workflow",
        "description": "A test workflow for frontend log visualization",
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
                        "body": {"test": "frontend_data"}
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
        return
    
    workflow = workflow_response.json()
    workflow_id = workflow["id"]
    print(f"   Workflow created with ID: {workflow_id}")
    
    # Step 3: Create some test execution logs by triggering the workflow
    print("3. Creating test execution logs...")
    webhook_id = workflow["webhook_url"].split("/")[-1]
    
    # Create multiple executions with different outcomes
    test_payloads = [
        {"test": "success_case", "data": "test1"},
        {"test": "another_success", "data": "test2"},
        {"test": "third_execution", "data": "test3"}
    ]
    
    for i, payload in enumerate(test_payloads):
        trigger_response = requests.post(f"{BASE_URL}/webhook/{webhook_id}", json=payload)
        if trigger_response.status_code == 200:
            print(f"   Execution {i+1} triggered successfully")
        else:
            print(f"   Execution {i+1} failed: {trigger_response.status_code}")
    
    # Wait for executions to complete
    import time
    print("   Waiting for executions to complete...")
    time.sleep(5)
    
    # Step 4: Test the log API endpoints
    print("4. Testing log API endpoints...")
    
    # Test getting execution logs
    logs_response = requests.get(f"{BASE_URL}/workflows/{workflow_id}/logs", 
                                headers=headers)
    
    if logs_response.status_code != 200:
        print(f"   Failed to get logs: {logs_response.status_code}")
        return
    
    logs = logs_response.json()
    print(f"   Retrieved {len(logs)} execution logs")
    
    # Test getting log count
    count_response = requests.get(f"{BASE_URL}/workflows/{workflow_id}/logs/count", 
                                headers=headers)
    
    if count_response.status_code == 200:
        count = count_response.json()["count"]
        print(f"   Total log count: {count}")
    
    # Test getting detailed log information
    if logs:
        log_id = logs[0]["id"]
        detail_response = requests.get(f"{BASE_URL}/logs/{log_id}", 
                                     headers=headers)
        
        if detail_response.status_code == 200:
            print(f"   Log detail retrieved for log {log_id}")
        else:
            print(f"   Failed to get log detail: {detail_response.status_code}")
    
    # Step 5: Test filtering
    print("5. Testing log filtering...")
    for status in ["success", "failed", "running"]:
        filtered_response = requests.get(
            f"{BASE_URL}/workflows/{workflow_id}/logs?status={status}", 
            headers=headers
        )
        
        if filtered_response.status_code == 200:
            filtered_logs = filtered_response.json()
            print(f"   {status} logs: {len(filtered_logs)}")
    
    # Step 6: Display frontend access information
    print("6. Frontend access information:")
    print(f"   Frontend URL: {FRONTEND_URL}")
    print(f"   Workflow ID: {workflow_id}")
    print(f"   Direct logs URL: {FRONTEND_URL}/workflows/{workflow_id}/logs")
    print(f"   Edit workflow URL: {FRONTEND_URL}/workflows/{workflow_id}/edit")
    
    print("\n✅ Frontend log integration test completed!")
    print("\nNext steps:")
    print("1. Open the frontend in your browser")
    print("2. Login with the test credentials:")
    print(f"   Email: {TEST_EMAIL}")
    print(f"   Password: {TEST_PASSWORD}")
    print("3. Navigate to the workflow and check the execution logs")

if __name__ == "__main__":
    test_frontend_log_integration()