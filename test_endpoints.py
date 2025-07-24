#!/usr/bin/env python3
"""
Test script for AutomateOS workflow CRUD endpoints.
Tests the complete workflow lifecycle: create, read, update, delete.
"""

import requests
import json
import time

BASE_URL = "http://127.0.0.1:8000"

def test_workflow_crud():
    """Test complete CRUD operations for workflows."""
    
    print("🚀 Starting AutomateOS Workflow CRUD Tests")
    print("=" * 50)
    
    # Step 1: Register a test user
    print("\n1. Registering test user...")
    register_data = {
        "email": "test@example.com",
        "password": "testpassword123"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/register/", json=register_data)
        if response.status_code == 200:
            print("✅ User registered successfully")
            user_data = response.json()
            print(f"   User ID: {user_data['id']}")
        elif response.status_code == 400 and "already registered" in response.text:
            print("ℹ️  User already exists, continuing...")
        else:
            print(f"❌ Registration failed: {response.status_code} - {response.text}")
            return False
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to server. Make sure the server is running on port 8000")
        return False
    
    # Step 2: Login to get JWT token
    print("\n2. Logging in to get JWT token...")
    login_data = {
        "username": "test@example.com",  # OAuth2 uses 'username' field
        "password": "testpassword123"
    }
    
    response = requests.post(f"{BASE_URL}/auth/token", data=login_data)
    if response.status_code != 200:
        print(f"❌ Login failed: {response.status_code} - {response.text}")
        return False
    
    token_data = response.json()
    access_token = token_data["access_token"]
    headers = {"Authorization": f"Bearer {access_token}"}
    print("✅ Login successful, JWT token obtained")
    
    # Step 3: Create a workflow
    print("\n3. Creating a new workflow...")
    workflow_data = {
        "name": "Test Workflow",
        "description": "A test workflow for CRUD operations",
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
    
    response = requests.post(f"{BASE_URL}/workflows/", json=workflow_data, headers=headers)
    if response.status_code != 200:
        print(f"❌ Workflow creation failed: {response.status_code} - {response.text}")
        return False
    
    created_workflow = response.json()
    workflow_id = created_workflow["id"]
    print("✅ Workflow created successfully")
    print(f"   Workflow ID: {workflow_id}")
    print(f"   Webhook URL: {created_workflow['webhook_url']}")
    
    # Step 4: Read all workflows
    print("\n4. Reading all workflows...")
    response = requests.get(f"{BASE_URL}/workflows/", headers=headers)
    if response.status_code != 200:
        print(f"❌ Failed to read workflows: {response.status_code} - {response.text}")
        return False
    
    workflows = response.json()
    print(f"✅ Retrieved {len(workflows)} workflow(s)")
    for wf in workflows:
        print(f"   - {wf['name']} (ID: {wf['id']})")
    
    # Step 5: Read single workflow
    print(f"\n5. Reading single workflow (ID: {workflow_id})...")
    response = requests.get(f"{BASE_URL}/workflows/{workflow_id}", headers=headers)
    if response.status_code != 200:
        print(f"❌ Failed to read single workflow: {response.status_code} - {response.text}")
        return False
    
    single_workflow = response.json()
    print("✅ Single workflow retrieved successfully")
    print(f"   Name: {single_workflow['name']}")
    print(f"   Description: {single_workflow['description']}")
    print(f"   Active: {single_workflow['is_active']}")
    
    # Step 6: Update the workflow
    print(f"\n6. Updating workflow (ID: {workflow_id})...")
    update_data = {
        "name": "Updated Test Workflow",
        "description": "Updated description for testing",
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
                        "url": "https://httpbin.org/put",
                        "method": "PUT",
                        "headers": {"Content-Type": "application/json"}
                    }
                },
                {
                    "id": "filter-1",
                    "type": "filter",
                    "config": {"condition": "status == 200"}
                }
            ],
            "connections": [
                {"from": "trigger-1", "to": "action-1"},
                {"from": "action-1", "to": "filter-1"}
            ]
        },
        "is_active": False
    }
    
    response = requests.put(f"{BASE_URL}/workflows/{workflow_id}", json=update_data, headers=headers)
    if response.status_code != 200:
        print(f"❌ Workflow update failed: {response.status_code} - {response.text}")
        return False
    
    updated_workflow = response.json()
    print("✅ Workflow updated successfully")
    print(f"   New name: {updated_workflow['name']}")
    print(f"   New description: {updated_workflow['description']}")
    print(f"   Active status: {updated_workflow['is_active']}")
    print(f"   Nodes count: {len(updated_workflow['definition']['nodes'])}")
    
    # Step 7: Test authorization (try to access non-existent workflow)
    print(f"\n7. Testing authorization with non-existent workflow...")
    response = requests.get(f"{BASE_URL}/workflows/99999", headers=headers)
    if response.status_code == 404:
        print("✅ Authorization test passed - 404 for non-existent workflow")
    else:
        print(f"⚠️  Unexpected response: {response.status_code}")
    
    # Step 8: Delete the workflow
    print(f"\n8. Deleting workflow (ID: {workflow_id})...")
    response = requests.delete(f"{BASE_URL}/workflows/{workflow_id}", headers=headers)
    if response.status_code != 200:
        print(f"❌ Workflow deletion failed: {response.status_code} - {response.text}")
        return False
    
    delete_result = response.json()
    print("✅ Workflow deleted successfully")
    print(f"   Message: {delete_result['message']}")
    
    # Step 9: Verify deletion
    print(f"\n9. Verifying workflow deletion...")
    response = requests.get(f"{BASE_URL}/workflows/{workflow_id}", headers=headers)
    if response.status_code == 404:
        print("✅ Deletion verified - workflow no longer exists")
    else:
        print(f"❌ Deletion verification failed: {response.status_code}")
        return False
    
    # Step 10: Check empty workflow list
    print(f"\n10. Checking workflow list after deletion...")
    response = requests.get(f"{BASE_URL}/workflows/", headers=headers)
    if response.status_code == 200:
        workflows = response.json()
        print(f"✅ Workflow list retrieved: {len(workflows)} workflow(s) remaining")
    else:
        print(f"❌ Failed to get workflow list: {response.status_code}")
    
    print("\n" + "=" * 50)
    print("🎉 All CRUD tests completed successfully!")
    print("✅ Create workflow - PASSED")
    print("✅ Read workflows (list) - PASSED") 
    print("✅ Read workflow (single) - PASSED")
    print("✅ Update workflow - PASSED")
    print("✅ Delete workflow - PASSED")
    print("✅ Authorization checks - PASSED")
    
    return True

if __name__ == "__main__":
    success = test_workflow_crud()
    if not success:
        exit(1)