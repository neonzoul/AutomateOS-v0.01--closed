#!/usr/bin/env python3
"""
Basic functionality tests to verify the core system works.
This is a simplified test suite that focuses on essential functionality.
"""

import pytest
import requests
import time
import os
import sys
import subprocess
import threading

# Add the app directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

BASE_URL = "http://127.0.0.1:8000"

class TestBasicFunctionality:
    """Test basic system functionality."""
    
    @classmethod
    def setup_class(cls):
        """Set up test environment."""
        cls.server_process = None
        cls.start_server()
        time.sleep(3)  # Wait for server to start
    
    @classmethod
    def teardown_class(cls):
        """Clean up test environment."""
        if cls.server_process:
            cls.server_process.terminate()
            cls.server_process.wait()
    
    @classmethod
    def start_server(cls):
        """Start the FastAPI server for testing."""
        try:
            # Check if server is already running
            response = requests.get(f"{BASE_URL}/health", timeout=2)
            if response.status_code == 200:
                print("✅ Server already running")
                return
        except requests.exceptions.RequestException:
            pass
        
        print("🚀 Starting server for testing...")
        try:
            cls.server_process = subprocess.Popen(
                [sys.executable, "-m", "uvicorn", "app.main:app", "--host", "127.0.0.1", "--port", "8000"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
        except Exception as e:
            print(f"❌ Failed to start server: {e}")
    
    def test_health_endpoint(self):
        """Test that the health endpoint is working."""
        try:
            response = requests.get(f"{BASE_URL}/health", timeout=10)
            assert response.status_code == 200
            data = response.json()
            assert "status" in data
            print("✅ Health endpoint working")
        except Exception as e:
            pytest.fail(f"Health endpoint test failed: {e}")
    
    def test_root_endpoint(self):
        """Test that the root endpoint is working."""
        try:
            response = requests.get(f"{BASE_URL}/", timeout=10)
            assert response.status_code == 200
            data = response.json()
            assert "message" in data
            print("✅ Root endpoint working")
        except Exception as e:
            pytest.fail(f"Root endpoint test failed: {e}")
    
    def test_user_registration(self):
        """Test user registration functionality."""
        try:
            user_data = {
                "email": f"test_{int(time.time())}@example.com",
                "password": "testpassword123"
            }
            
            response = requests.post(f"{BASE_URL}/register/", json=user_data, timeout=10)
            
            # Should succeed or fail with "already registered"
            assert response.status_code in [200, 400]
            
            if response.status_code == 200:
                data = response.json()
                assert "email" in data
                assert "id" in data
                print("✅ User registration working")
            else:
                # Check if it's the expected "already registered" error
                assert "already registered" in response.text.lower()
                print("✅ User registration working (user already exists)")
                
        except Exception as e:
            pytest.fail(f"User registration test failed: {e}")
    
    def test_authentication_flow(self):
        """Test complete authentication flow."""
        try:
            # Register user
            user_email = f"auth_test_{int(time.time())}@example.com"
            user_data = {
                "email": user_email,
                "password": "testpassword123"
            }
            
            reg_response = requests.post(f"{BASE_URL}/register/", json=user_data, timeout=10)
            # Should succeed or user already exists
            assert reg_response.status_code in [200, 400]
            
            # Login
            login_data = {
                "username": user_email,
                "password": "testpassword123"
            }
            
            login_response = requests.post(f"{BASE_URL}/auth/token", data=login_data, timeout=10)
            assert login_response.status_code == 200
            
            token_data = login_response.json()
            assert "access_token" in token_data
            assert "token_type" in token_data
            
            # Test protected endpoint
            headers = {"Authorization": f"Bearer {token_data['access_token']}"}
            workflows_response = requests.get(f"{BASE_URL}/workflows/", headers=headers, timeout=10)
            assert workflows_response.status_code == 200
            
            workflows = workflows_response.json()
            assert isinstance(workflows, list)
            
            print("✅ Authentication flow working")
            
        except Exception as e:
            pytest.fail(f"Authentication flow test failed: {e}")
    
    def test_workflow_creation(self):
        """Test workflow creation functionality."""
        try:
            # First authenticate
            user_email = f"workflow_test_{int(time.time())}@example.com"
            user_data = {
                "email": user_email,
                "password": "testpassword123"
            }
            
            requests.post(f"{BASE_URL}/register/", json=user_data, timeout=10)
            
            login_data = {
                "username": user_email,
                "password": "testpassword123"
            }
            
            login_response = requests.post(f"{BASE_URL}/auth/token", data=login_data, timeout=10)
            token = login_response.json()["access_token"]
            headers = {"Authorization": f"Bearer {token}"}
            
            # Create workflow
            workflow_data = {
                "name": "Test Workflow",
                "description": "A test workflow",
                "definition": {
                    "nodes": [
                        {
                            "id": "trigger-1",
                            "type": "webhook",
                            "config": {"method": "POST"}
                        }
                    ],
                    "connections": []
                },
                "is_active": True
            }
            
            create_response = requests.post(f"{BASE_URL}/workflows/", json=workflow_data, headers=headers, timeout=10)
            assert create_response.status_code == 200
            
            workflow = create_response.json()
            assert "id" in workflow
            assert "webhook_url" in workflow
            assert workflow["name"] == "Test Workflow"
            
            # Test workflow retrieval
            get_response = requests.get(f"{BASE_URL}/workflows/{workflow['id']}", headers=headers, timeout=10)
            assert get_response.status_code == 200
            
            # Clean up - delete workflow
            delete_response = requests.delete(f"{BASE_URL}/workflows/{workflow['id']}", headers=headers, timeout=10)
            assert delete_response.status_code == 200
            
            print("✅ Workflow creation working")
            
        except Exception as e:
            pytest.fail(f"Workflow creation test failed: {e}")

def test_system_integration():
    """Test basic system integration without pytest class."""
    print("\n🧪 Running Basic System Integration Test")
    print("-" * 50)
    
    # Start server
    server_process = None
    try:
        # Check if server is running
        try:
            response = requests.get(f"{BASE_URL}/health", timeout=2)
            if response.status_code == 200:
                print("✅ Server already running")
            else:
                raise requests.exceptions.RequestException("Server not responding")
        except requests.exceptions.RequestException:
            print("🚀 Starting server...")
            server_process = subprocess.Popen(
                [sys.executable, "-m", "uvicorn", "app.main:app", "--host", "127.0.0.1", "--port", "8000"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            time.sleep(5)  # Wait for server to start
        
        # Test health endpoint
        response = requests.get(f"{BASE_URL}/health", timeout=10)
        assert response.status_code == 200, f"Health check failed: {response.status_code}"
        print("✅ Health endpoint working")
        
        # Test user registration and authentication
        user_email = f"integration_test_{int(time.time())}@example.com"
        user_data = {"email": user_email, "password": "testpassword123"}
        
        reg_response = requests.post(f"{BASE_URL}/register/", json=user_data, timeout=10)
        assert reg_response.status_code in [200, 400], f"Registration failed: {reg_response.status_code}"
        print("✅ User registration working")
        
        # Login
        login_data = {"username": user_email, "password": "testpassword123"}
        login_response = requests.post(f"{BASE_URL}/auth/token", data=login_data, timeout=10)
        assert login_response.status_code == 200, f"Login failed: {login_response.status_code}"
        
        token = login_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        print("✅ Authentication working")
        
        # Test workflow operations
        workflow_data = {
            "name": "Integration Test Workflow",
            "description": "Test workflow for integration testing",
            "definition": {"nodes": [{"id": "test", "type": "webhook", "config": {"method": "POST"}}]},
            "is_active": True
        }
        
        create_response = requests.post(f"{BASE_URL}/workflows/", json=workflow_data, headers=headers, timeout=10)
        assert create_response.status_code == 200, f"Workflow creation failed: {create_response.status_code}"
        
        workflow = create_response.json()
        workflow_id = workflow["id"]
        print("✅ Workflow creation working")
        
        # Test workflow listing
        list_response = requests.get(f"{BASE_URL}/workflows/", headers=headers, timeout=10)
        assert list_response.status_code == 200, f"Workflow listing failed: {list_response.status_code}"
        
        workflows = list_response.json()
        assert len(workflows) > 0, "No workflows found"
        print("✅ Workflow listing working")
        
        # Clean up
        delete_response = requests.delete(f"{BASE_URL}/workflows/{workflow_id}", headers=headers, timeout=10)
        assert delete_response.status_code == 200, f"Workflow deletion failed: {delete_response.status_code}"
        print("✅ Workflow deletion working")
        
        print("\n🎉 Basic system integration test PASSED!")
        return True
        
    except Exception as e:
        print(f"\n❌ Basic system integration test FAILED: {e}")
        return False
        
    finally:
        if server_process:
            server_process.terminate()
            server_process.wait()

if __name__ == "__main__":
    success = test_system_integration()
    if not success:
        exit(1)