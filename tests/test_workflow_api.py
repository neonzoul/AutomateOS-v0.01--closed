#!/usr/bin/env python3
"""
Test script for the Workflow API endpoints.

This script tests the complete workflow CRUD functionality:
1. User registration
2. User authentication 
3. Workflow creation
4. Workflow listing
5. Workflow retrieval
6. Workflow update
7. Workflow deletion
"""

import requests
import json
import time
import subprocess
import threading
import sys

BASE_URL = "http://127.0.0.1:8000"

def start_server():
    """Start the FastAPI server in background."""
    subprocess.run(['python', '-m', 'uvicorn', 'app.main:app', '--host', '127.0.0.1', '--port', '8000'], 
                   capture_output=True)

def test_workflow_api():
    """Test the complete workflow API functionality."""
    
    print("🚀 Starting Workflow API Test")
    print("=" * 50)
    
    # Start server
    print("Starting server...")
    server_thread = threading.Thread(target=start_server, daemon=True)
    server_thread.start()
    time.sleep(3)  # Wait for server to start
    
    try:
        # Test 1: Register a test user
        print("\n1. Testing user registration...")
        import random
        test_email = f"test{random.randint(1000, 9999)}@example.com"
        register_data = {
            "email": test_email,
            "password": "testpassword123"
        }
        
        response = requests.post(f"{BASE_URL}/register/", json=register_data)
        if response.status_code == 200:
            print("✅ User registration successful")
            user_data = response.json()
            print(f"   User ID: {user_data['id']}, Email: {user_data['email']}")
        else:
            print(f"❌ User registration failed: {response.status_code} - {response.text}")
            return
        
        # Test 2: Login and get token
        print("\n2. Testing user authentication...")
        login_data = {
            "username": test_email,  # OAuth2 uses 'username' field
            "password": "testpassword123"
        }
        
        response = requests.post(f"{BASE_URL}/auth/token", data=login_data)
        if response.status_code == 200:
            print("✅ User authentication successful")
            token_data = response.json()
            access_token = token_data["access_token"]
            print(f"   Token type: {token_data['token_type']}")
        else:
            print(f"❌ User authentication failed: {response.status_code} - {response.text}")
            return
        
        # Set up headers for authenticated requests
        headers = {"Authorization": f"Bearer {access_token}"}
        
        # Test 3: List workflows (should be empty initially)
        print("\n3. Testing workflow listing (empty state)...")
        response = requests.get(f"{BASE_URL}/workflows/", headers=headers)
        if response.status_code == 200:
            workflows = response.json()
            print(f"✅ Workflow listing successful - Found {len(workflows)} workflows")
            if len(workflows) == 0:
                print("   ✅ Empty state correct - no workflows yet")
        else:
            print(f"❌ Workflow listing failed: {response.status_code} - {response.text}")
            return
        
        # Test 4: Create a workflow
        print("\n4. Testing workflow creation...")
        workflow_data = {
            "name": "Test Workflow",
            "description": "A test workflow for API testing",
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
                            "method": "POST"
                        }
                    }
                ],
                "connections": [{"from": "trigger-1", "to": "action-1"}]
            },
            "is_active": True
        }
        
        response = requests.post(f"{BASE_URL}/workflows/", json=workflow_data, headers=headers)
        if response.status_code == 200:
            print("✅ Workflow creation successful")
            created_workflow = response.json()
            workflow_id = created_workflow["id"]
            print(f"   Workflow ID: {workflow_id}")
            print(f"   Webhook URL: {created_workflow['webhook_url']}")
        else:
            print(f"❌ Workflow creation failed: {response.status_code} - {response.text}")
            return
        
        # Test 5: List workflows (should now have 1 workflow)
        print("\n5. Testing workflow listing (with data)...")
        response = requests.get(f"{BASE_URL}/workflows/", headers=headers)
        if response.status_code == 200:
            workflows = response.json()
            print(f"✅ Workflow listing successful - Found {len(workflows)} workflows")
            if len(workflows) == 1:
                print("   ✅ Correct number of workflows returned")
                print(f"   Workflow: {workflows[0]['name']}")
        else:
            print(f"❌ Workflow listing failed: {response.status_code} - {response.text}")
            return
        
        # Test 6: Get specific workflow
        print("\n6. Testing workflow retrieval...")
        response = requests.get(f"{BASE_URL}/workflows/{workflow_id}", headers=headers)
        if response.status_code == 200:
            workflow = response.json()
            print("✅ Workflow retrieval successful")
            print(f"   Name: {workflow['name']}")
            print(f"   Description: {workflow['description']}")
        else:
            print(f"❌ Workflow retrieval failed: {response.status_code} - {response.text}")
            return
        
        # Test 7: Update workflow
        print("\n7. Testing workflow update...")
        updated_workflow_data = {
            "name": "Updated Test Workflow",
            "description": "An updated test workflow",
            "definition": workflow_data["definition"],  # Keep same definition
            "is_active": False  # Change active status
        }
        
        response = requests.put(f"{BASE_URL}/workflows/{workflow_id}", json=updated_workflow_data, headers=headers)
        if response.status_code == 200:
            updated_workflow = response.json()
            print("✅ Workflow update successful")
            print(f"   New name: {updated_workflow['name']}")
            print(f"   Active status: {updated_workflow['is_active']}")
        else:
            print(f"❌ Workflow update failed: {response.status_code} - {response.text}")
            return
        
        # Test 8: Delete workflow
        print("\n8. Testing workflow deletion...")
        response = requests.delete(f"{BASE_URL}/workflows/{workflow_id}", headers=headers)
        if response.status_code == 200:
            print("✅ Workflow deletion successful")
            result = response.json()
            print(f"   Message: {result['message']}")
        else:
            print(f"❌ Workflow deletion failed: {response.status_code} - {response.text}")
            return
        
        # Test 9: Verify workflow is deleted
        print("\n9. Verifying workflow deletion...")
        response = requests.get(f"{BASE_URL}/workflows/", headers=headers)
        if response.status_code == 200:
            workflows = response.json()
            print(f"✅ Final workflow listing - Found {len(workflows)} workflows")
            if len(workflows) == 0:
                print("   ✅ Workflow successfully deleted")
        else:
            print(f"❌ Final workflow listing failed: {response.status_code} - {response.text}")
            return
        
        print("\n" + "=" * 50)
        print("🎉 ALL TESTS PASSED! Workflow API is working correctly.")
        print("=" * 50)
        
    except Exception as e:
        print(f"\n❌ Test failed with exception: {e}")
        return

if __name__ == "__main__":
    test_workflow_api()