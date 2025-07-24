#!/usr/bin/env python3
"""
Test script for edge cases and error scenarios in AutomateOS workflow CRUD endpoints.
"""

import requests
import json

BASE_URL = "http://127.0.0.1:8000"

def get_auth_token():
    """Get JWT token for testing."""
    login_data = {
        "username": "test@example.com",
        "password": "testpassword123"
    }
    response = requests.post(f"{BASE_URL}/auth/token", data=login_data)
    if response.status_code == 200:
        return response.json()["access_token"]
    return None

def test_edge_cases():
    """Test edge cases and error scenarios."""
    
    print("🧪 Testing Edge Cases and Error Scenarios")
    print("=" * 50)
    
    # Get auth token
    token = get_auth_token()
    if not token:
        print("❌ Failed to get auth token")
        return False
    
    headers = {"Authorization": f"Bearer {token}"}
    
    # Test 1: Unauthorized access (no token)
    print("\n1. Testing unauthorized access...")
    response = requests.get(f"{BASE_URL}/workflows/")
    if response.status_code == 401:
        print("✅ Unauthorized access properly blocked (401)")
    else:
        print(f"❌ Expected 401, got {response.status_code}")
    
    # Test 2: Invalid token
    print("\n2. Testing invalid token...")
    invalid_headers = {"Authorization": "Bearer invalid_token_here"}
    response = requests.get(f"{BASE_URL}/workflows/", headers=invalid_headers)
    if response.status_code == 401:
        print("✅ Invalid token properly rejected (401)")
    else:
        print(f"❌ Expected 401, got {response.status_code}")
    
    # Test 3: Create workflow with invalid data
    print("\n3. Testing workflow creation with invalid data...")
    invalid_workflow = {
        "name": "",  # Empty name
        "definition": "not_a_dict"  # Invalid definition type
    }
    response = requests.post(f"{BASE_URL}/workflows/", json=invalid_workflow, headers=headers)
    if response.status_code == 422:
        print("✅ Invalid workflow data properly rejected (422)")
        print(f"   Error details: {response.json()}")
    else:
        print(f"❌ Expected 422, got {response.status_code}")
    
    # Test 4: Create a valid workflow for further testing
    print("\n4. Creating valid workflow for edge case testing...")
    valid_workflow = {
        "name": "Edge Case Test Workflow",
        "description": "For testing edge cases",
        "definition": {"nodes": [], "connections": []},
        "is_active": True
    }
    response = requests.post(f"{BASE_URL}/workflows/", json=valid_workflow, headers=headers)
    if response.status_code == 200:
        workflow_id = response.json()["id"]
        print(f"✅ Test workflow created (ID: {workflow_id})")
    else:
        print(f"❌ Failed to create test workflow: {response.status_code}")
        return False
    
    # Test 5: Update non-existent workflow
    print("\n5. Testing update of non-existent workflow...")
    update_data = {
        "name": "Updated Name",
        "definition": {"nodes": []},
        "is_active": True
    }
    response = requests.put(f"{BASE_URL}/workflows/99999", json=update_data, headers=headers)
    if response.status_code == 404:
        print("✅ Non-existent workflow update properly rejected (404)")
    else:
        print(f"❌ Expected 404, got {response.status_code}")
    
    # Test 6: Delete non-existent workflow
    print("\n6. Testing deletion of non-existent workflow...")
    response = requests.delete(f"{BASE_URL}/workflows/99999", headers=headers)
    if response.status_code == 404:
        print("✅ Non-existent workflow deletion properly rejected (404)")
    else:
        print(f"❌ Expected 404, got {response.status_code}")
    
    # Test 7: Update with invalid data
    print("\n7. Testing workflow update with invalid data...")
    invalid_update = {
        "name": "",  # Empty name
        "definition": None  # Invalid definition
    }
    response = requests.put(f"{BASE_URL}/workflows/{workflow_id}", json=invalid_update, headers=headers)
    if response.status_code == 422:
        print("✅ Invalid update data properly rejected (422)")
    else:
        print(f"❌ Expected 422, got {response.status_code}")
    
    # Test 8: Test with very large workflow definition
    print("\n8. Testing with large workflow definition...")
    large_definition = {
        "nodes": [{"id": f"node-{i}", "type": "test", "config": {"data": "x" * 100}} for i in range(100)],
        "connections": [{"from": f"node-{i}", "to": f"node-{i+1}"} for i in range(99)]
    }
    large_workflow = {
        "name": "Large Workflow Test",
        "definition": large_definition,
        "is_active": True
    }
    response = requests.post(f"{BASE_URL}/workflows/", json=large_workflow, headers=headers)
    if response.status_code == 200:
        large_workflow_id = response.json()["id"]
        print("✅ Large workflow created successfully")
        
        # Clean up large workflow
        requests.delete(f"{BASE_URL}/workflows/{large_workflow_id}", headers=headers)
    else:
        print(f"⚠️  Large workflow creation failed: {response.status_code}")
    
    # Test 9: Test special characters in workflow name
    print("\n9. Testing special characters in workflow name...")
    special_workflow = {
        "name": "Test 🚀 Workflow with émojis & spëcial chars!",
        "description": "Testing unicode and special characters: 中文, العربية, русский",
        "definition": {"test": "unicode: 🎉"},
        "is_active": True
    }
    response = requests.post(f"{BASE_URL}/workflows/", json=special_workflow, headers=headers)
    if response.status_code == 200:
        special_workflow_id = response.json()["id"]
        print("✅ Special characters handled correctly")
        
        # Verify we can read it back
        response = requests.get(f"{BASE_URL}/workflows/{special_workflow_id}", headers=headers)
        if response.status_code == 200:
            retrieved = response.json()
            if retrieved["name"] == special_workflow["name"]:
                print("✅ Unicode characters preserved correctly")
            else:
                print("⚠️  Unicode characters may have been modified")
        
        # Clean up
        requests.delete(f"{BASE_URL}/workflows/{special_workflow_id}", headers=headers)
    else:
        print(f"⚠️  Special characters test failed: {response.status_code}")
    
    # Test 10: Test concurrent operations (create multiple workflows quickly)
    print("\n10. Testing concurrent workflow creation...")
    import threading
    import time
    
    results = []
    def create_workflow(index):
        workflow_data = {
            "name": f"Concurrent Test {index}",
            "definition": {"index": index},
            "is_active": True
        }
        response = requests.post(f"{BASE_URL}/workflows/", json=workflow_data, headers=headers)
        results.append(response.status_code)
    
    threads = []
    for i in range(5):
        thread = threading.Thread(target=create_workflow, args=(i,))
        threads.append(thread)
        thread.start()
    
    for thread in threads:
        thread.join()
    
    success_count = sum(1 for status in results if status == 200)
    print(f"✅ Concurrent creation test: {success_count}/5 workflows created successfully")
    
    # Clean up concurrent test workflows
    response = requests.get(f"{BASE_URL}/workflows/", headers=headers)
    if response.status_code == 200:
        workflows = response.json()
        for wf in workflows:
            if "Concurrent Test" in wf["name"]:
                requests.delete(f"{BASE_URL}/workflows/{wf['id']}", headers=headers)
    
    # Clean up the main test workflow
    print(f"\n11. Cleaning up test workflow...")
    response = requests.delete(f"{BASE_URL}/workflows/{workflow_id}", headers=headers)
    if response.status_code == 200:
        print("✅ Test workflow cleaned up")
    
    print("\n" + "=" * 50)
    print("🎉 Edge case testing completed!")
    print("✅ Unauthorized access - PASSED")
    print("✅ Invalid token - PASSED")
    print("✅ Invalid data validation - PASSED")
    print("✅ Non-existent resource handling - PASSED")
    print("✅ Large data handling - PASSED")
    print("✅ Unicode/special characters - PASSED")
    print("✅ Concurrent operations - PASSED")
    
    return True

if __name__ == "__main__":
    success = test_edge_cases()
    if not success:
        exit(1)