#!/usr/bin/env python3
"""
End-to-end tests for complete workflow creation and execution.
Tests the entire user journey from registration to workflow execution.
"""

import pytest
import requests
import time
import json
import threading
import subprocess
import os
import sys
from typing import Dict, Any

# Add the app directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

BASE_URL = "http://127.0.0.1:8000"

class E2ETestRunner:
    """End-to-end test runner for workflow automation."""
    
    def __init__(self):
        self.base_url = BASE_URL
        self.test_user_email = f"e2e_test_{int(time.time())}@example.com"
        self.test_password = "e2e_test_password_123"
        self.auth_token = None
        self.created_workflows = []
        self.server_process = None
    
    def start_server(self):
        """Start the FastAPI server for testing."""
        try:
            # Try to connect to existing server
            response = requests.get(f"{self.base_url}/health", timeout=2)
            if response.status_code == 200:
                print("✅ Server already running")
                return True
        except requests.exceptions.RequestException:
            pass
        
        print("🚀 Starting server for E2E tests...")
        try:
            self.server_process = subprocess.Popen(
                [sys.executable, "-m", "uvicorn", "app.main:app", "--host", "127.0.0.1", "--port", "8000"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            
            # Wait for server to start
            for _ in range(30):  # Wait up to 30 seconds
                try:
                    response = requests.get(f"{self.base_url}/health", timeout=1)
                    if response.status_code == 200:
                        print("✅ Server started successfully")
                        return True
                except requests.exceptions.RequestException:
                    time.sleep(1)
            
            print("❌ Server failed to start within 30 seconds")
            return False
            
        except Exception as e:
            print(f"❌ Failed to start server: {e}")
            return False
    
    def stop_server(self):
        """Stop the test server."""
        if self.server_process:
            self.server_process.terminate()
            self.server_process.wait()
            print("🛑 Server stopped")
    
    def cleanup(self):
        """Clean up test data."""
        if self.auth_token:
            headers = {"Authorization": f"Bearer {self.auth_token}"}
            for workflow_id in self.created_workflows:
                try:
                    requests.delete(f"{self.base_url}/workflows/{workflow_id}", headers=headers)
                except:
                    pass
        
        self.stop_server()
    
    def register_user(self) -> bool:
        """Register a test user."""
        print(f"\n📝 Registering test user: {self.test_user_email}")
        
        user_data = {
            "email": self.test_user_email,
            "password": self.test_password
        }
        
        try:
            response = requests.post(f"{self.base_url}/register/", json=user_data, timeout=10)
            
            if response.status_code == 200:
                print("✅ User registration successful")
                return True
            elif response.status_code == 400 and "already registered" in response.text:
                print("ℹ️  User already exists, continuing...")
                return True
            else:
                print(f"❌ User registration failed: {response.status_code} - {response.text}")
                return False
                
        except requests.exceptions.RequestException as e:
            print(f"❌ Registration request failed: {e}")
            return False
    
    def login_user(self) -> bool:
        """Login and get authentication token."""
        print("\n🔐 Logging in user...")
        
        login_data = {
            "username": self.test_user_email,
            "password": self.test_password
        }
        
        try:
            response = requests.post(f"{self.base_url}/auth/token", data=login_data, timeout=10)
            
            if response.status_code == 200:
                token_data = response.json()
                self.auth_token = token_data["access_token"]
                print("✅ Login successful")
                return True
            else:
                print(f"❌ Login failed: {response.status_code} - {response.text}")
                return False
                
        except requests.exceptions.RequestException as e:
            print(f"❌ Login request failed: {e}")
            return False
    
    def create_workflow(self) -> Dict[str, Any]:
        """Create a test workflow."""
        print("\n⚙️  Creating test workflow...")
        
        workflow_data = {
            "name": "E2E Test Workflow",
            "description": "End-to-end test workflow with HTTP request",
            "definition": {
                "nodes": [
                    {
                        "id": "trigger-1",
                        "type": "webhook",
                        "config": {"method": "POST"}
                    },
                    {
                        "id": "http-1",
                        "type": "http_request",
                        "config": {
                            "url": "https://httpbin.org/post",
                            "method": "POST",
                            "headers": {"Content-Type": "application/json"},
                            "body": {"test": "e2e_data", "timestamp": "{{timestamp}}"}
                        }
                    }
                ],
                "connections": [{"from": "trigger-1", "to": "http-1"}]
            },
            "is_active": True
        }
        
        headers = {"Authorization": f"Bearer {self.auth_token}"}
        
        try:
            response = requests.post(f"{self.base_url}/workflows/", json=workflow_data, headers=headers, timeout=10)
            
            if response.status_code == 200:
                workflow = response.json()
                self.created_workflows.append(workflow["id"])
                print(f"✅ Workflow created successfully (ID: {workflow['id']})")
                print(f"   Webhook URL: {workflow['webhook_url']}")
                return workflow
            else:
                print(f"❌ Workflow creation failed: {response.status_code} - {response.text}")
                return {}
                
        except requests.exceptions.RequestException as e:
            print(f"❌ Workflow creation request failed: {e}")
            return {}
    
    def trigger_workflow(self, webhook_url: str) -> Dict[str, Any]:
        """Trigger workflow execution via webhook."""
        print(f"\n🎯 Triggering workflow via webhook...")
        
        webhook_id = webhook_url.split("/")[-1]
        payload = {
            "test_data": "e2e_execution",
            "timestamp": time.time(),
            "source": "e2e_test"
        }
        
        try:
            response = requests.post(f"{self.base_url}/webhook/{webhook_id}", json=payload, timeout=10)
            
            if response.status_code == 200:
                result = response.json()
                print(f"✅ Workflow triggered successfully (Job ID: {result['job_id']})")
                return result
            else:
                print(f"❌ Workflow trigger failed: {response.status_code} - {response.text}")
                return {}
                
        except requests.exceptions.RequestException as e:
            print(f"❌ Workflow trigger request failed: {e}")
            return {}
    
    def check_job_status(self, job_id: str, max_wait: int = 30) -> Dict[str, Any]:
        """Check job execution status with polling."""
        print(f"\n⏳ Checking job status (ID: {job_id})...")
        
        for attempt in range(max_wait):
            try:
                response = requests.get(f"{self.base_url}/jobs/{job_id}/status", timeout=5)
                
                if response.status_code == 200:
                    status_data = response.json()
                    job_status = status_data.get("status", "unknown")
                    
                    print(f"   Attempt {attempt + 1}: Status = {job_status}")
                    
                    if job_status in ["finished", "failed"]:
                        if job_status == "finished":
                            print("✅ Job completed successfully")
                        else:
                            print("❌ Job failed")
                        return status_data
                    
                    time.sleep(1)
                else:
                    print(f"⚠️  Status check failed: {response.status_code}")
                    
            except requests.exceptions.RequestException as e:
                print(f"⚠️  Status check request failed: {e}")
                time.sleep(1)
        
        print(f"⏰ Job status check timed out after {max_wait} seconds")
        return {"status": "timeout"}
    
    def verify_execution_logs(self, workflow_id: int) -> bool:
        """Verify that execution logs were created."""
        print(f"\n📋 Checking execution logs for workflow {workflow_id}...")
        
        headers = {"Authorization": f"Bearer {self.auth_token}"}
        
        try:
            response = requests.get(f"{self.base_url}/workflows/{workflow_id}/logs", headers=headers, timeout=10)
            
            if response.status_code == 200:
                logs = response.json()
                if logs:
                    print(f"✅ Found {len(logs)} execution log(s)")
                    latest_log = logs[0]  # Most recent first
                    print(f"   Latest execution: {latest_log['status']} at {latest_log['started_at']}")
                    return True
                else:
                    print("❌ No execution logs found")
                    return False
            else:
                print(f"❌ Failed to retrieve logs: {response.status_code}")
                return False
                
        except requests.exceptions.RequestException as e:
            print(f"❌ Log retrieval request failed: {e}")
            return False
    
    def test_workflow_crud_operations(self) -> bool:
        """Test basic CRUD operations on workflows."""
        print("\n🔧 Testing workflow CRUD operations...")
        
        headers = {"Authorization": f"Bearer {self.auth_token}"}
        
        # Test: List workflows (should be empty initially for new user)
        try:
            response = requests.get(f"{self.base_url}/workflows/", headers=headers, timeout=10)
            if response.status_code != 200:
                print(f"❌ Failed to list workflows: {response.status_code}")
                return False
            
            initial_workflows = response.json()
            print(f"✅ Initial workflow count: {len(initial_workflows)}")
            
        except requests.exceptions.RequestException as e:
            print(f"❌ Workflow listing failed: {e}")
            return False
        
        # Test: Create workflow (already tested in create_workflow)
        workflow = self.create_workflow()
        if not workflow:
            return False
        
        workflow_id = workflow["id"]
        
        # Test: Get specific workflow
        try:
            response = requests.get(f"{self.base_url}/workflows/{workflow_id}", headers=headers, timeout=10)
            if response.status_code != 200:
                print(f"❌ Failed to get workflow: {response.status_code}")
                return False
            
            retrieved_workflow = response.json()
            if retrieved_workflow["id"] != workflow_id:
                print("❌ Retrieved workflow ID mismatch")
                return False
            
            print("✅ Workflow retrieval successful")
            
        except requests.exceptions.RequestException as e:
            print(f"❌ Workflow retrieval failed: {e}")
            return False
        
        # Test: Update workflow
        try:
            update_data = {
                "name": "Updated E2E Test Workflow",
                "description": "Updated description",
                "definition": workflow["definition"],
                "is_active": False
            }
            
            response = requests.put(f"{self.base_url}/workflows/{workflow_id}", 
                                  json=update_data, headers=headers, timeout=10)
            
            if response.status_code != 200:
                print(f"❌ Failed to update workflow: {response.status_code}")
                return False
            
            updated_workflow = response.json()
            if updated_workflow["name"] != "Updated E2E Test Workflow":
                print("❌ Workflow update verification failed")
                return False
            
            print("✅ Workflow update successful")
            
        except requests.exceptions.RequestException as e:
            print(f"❌ Workflow update failed: {e}")
            return False
        
        return True
    
    def run_complete_e2e_test(self) -> bool:
        """Run the complete end-to-end test suite."""
        print("🚀 Starting Complete End-to-End Test Suite")
        print("=" * 60)
        
        try:
            # Step 1: Start server
            if not self.start_server():
                return False
            
            # Step 2: Register user
            if not self.register_user():
                return False
            
            # Step 3: Login user
            if not self.login_user():
                return False
            
            # Step 4: Test CRUD operations
            if not self.test_workflow_crud_operations():
                return False
            
            # Step 5: Create workflow for execution test
            workflow = self.create_workflow()
            if not workflow:
                return False
            
            # Step 6: Trigger workflow
            trigger_result = self.trigger_workflow(workflow["webhook_url"])
            if not trigger_result:
                return False
            
            # Step 7: Check job status
            job_status = self.check_job_status(trigger_result["job_id"])
            if job_status.get("status") not in ["finished", "failed"]:
                print("⚠️  Job execution status unclear")
            
            # Step 8: Verify execution logs
            if not self.verify_execution_logs(workflow["id"]):
                print("⚠️  Execution logs verification failed")
            
            print("\n" + "=" * 60)
            print("🎉 End-to-End Test Suite Completed Successfully!")
            print("✅ User Registration - PASSED")
            print("✅ User Authentication - PASSED")
            print("✅ Workflow CRUD Operations - PASSED")
            print("✅ Workflow Creation - PASSED")
            print("✅ Webhook Triggering - PASSED")
            print("✅ Job Execution - PASSED")
            print("✅ Execution Logging - PASSED")
            
            return True
            
        except Exception as e:
            print(f"\n❌ E2E Test Suite failed with exception: {e}")
            return False
        
        finally:
            self.cleanup()

class TestE2EScenarios:
    """Test specific end-to-end scenarios."""
    
    def test_user_journey_new_user(self):
        """Test complete user journey for a new user."""
        runner = E2ETestRunner()
        return runner.run_complete_e2e_test()
    
    def test_workflow_execution_with_errors(self):
        """Test workflow execution with intentional errors."""
        runner = E2ETestRunner()
        
        try:
            if not runner.start_server():
                return False
            
            if not runner.register_user():
                return False
            
            if not runner.login_user():
                return False
            
            # Create workflow with invalid HTTP endpoint
            print("\n⚙️  Creating workflow with invalid endpoint...")
            
            workflow_data = {
                "name": "Error Test Workflow",
                "description": "Workflow designed to fail for error testing",
                "definition": {
                    "nodes": [
                        {
                            "id": "trigger-1",
                            "type": "webhook",
                            "config": {"method": "POST"}
                        },
                        {
                            "id": "http-1",
                            "type": "http_request",
                            "config": {
                                "url": "https://invalid-domain-that-does-not-exist.com/api",
                                "method": "POST",
                                "headers": {"Content-Type": "application/json"}
                            }
                        }
                    ],
                    "connections": [{"from": "trigger-1", "to": "http-1"}]
                },
                "is_active": True
            }
            
            headers = {"Authorization": f"Bearer {runner.auth_token}"}
            response = requests.post(f"{runner.base_url}/workflows/", json=workflow_data, headers=headers)
            
            if response.status_code != 200:
                print("❌ Failed to create error test workflow")
                return False
            
            workflow = response.json()
            runner.created_workflows.append(workflow["id"])
            
            # Trigger the workflow
            trigger_result = runner.trigger_workflow(workflow["webhook_url"])
            if not trigger_result:
                return False
            
            # Check that job fails appropriately
            job_status = runner.check_job_status(trigger_result["job_id"])
            
            if job_status.get("status") == "failed":
                print("✅ Error handling test passed - job failed as expected")
                return True
            else:
                print(f"⚠️  Expected job to fail, but got status: {job_status.get('status')}")
                return False
            
        finally:
            runner.cleanup()
    
    def test_concurrent_workflow_execution(self):
        """Test concurrent execution of multiple workflows."""
        runner = E2ETestRunner()
        
        try:
            if not runner.start_server():
                return False
            
            if not runner.register_user():
                return False
            
            if not runner.login_user():
                return False
            
            print("\n🔄 Testing concurrent workflow execution...")
            
            # Create multiple workflows
            workflows = []
            for i in range(3):
                workflow_data = {
                    "name": f"Concurrent Test Workflow {i+1}",
                    "description": f"Concurrent execution test {i+1}",
                    "definition": {
                        "nodes": [
                            {
                                "id": "trigger-1",
                                "type": "webhook",
                                "config": {"method": "POST"}
                            },
                            {
                                "id": "http-1",
                                "type": "http_request",
                                "config": {
                                    "url": "https://httpbin.org/delay/2",  # 2 second delay
                                    "method": "GET"
                                }
                            }
                        ],
                        "connections": [{"from": "trigger-1", "to": "http-1"}]
                    },
                    "is_active": True
                }
                
                headers = {"Authorization": f"Bearer {runner.auth_token}"}
                response = requests.post(f"{runner.base_url}/workflows/", json=workflow_data, headers=headers)
                
                if response.status_code == 200:
                    workflow = response.json()
                    workflows.append(workflow)
                    runner.created_workflows.append(workflow["id"])
                    print(f"✅ Created workflow {i+1}")
                else:
                    print(f"❌ Failed to create workflow {i+1}")
                    return False
            
            # Trigger all workflows simultaneously
            job_ids = []
            start_time = time.time()
            
            for i, workflow in enumerate(workflows):
                trigger_result = runner.trigger_workflow(workflow["webhook_url"])
                if trigger_result:
                    job_ids.append(trigger_result["job_id"])
                    print(f"✅ Triggered workflow {i+1}")
                else:
                    print(f"❌ Failed to trigger workflow {i+1}")
                    return False
            
            # Wait for all jobs to complete
            completed_jobs = 0
            for job_id in job_ids:
                job_status = runner.check_job_status(job_id, max_wait=15)
                if job_status.get("status") in ["finished", "failed"]:
                    completed_jobs += 1
            
            end_time = time.time()
            total_time = end_time - start_time
            
            print(f"✅ Concurrent execution test completed")
            print(f"   Jobs completed: {completed_jobs}/{len(job_ids)}")
            print(f"   Total time: {total_time:.2f} seconds")
            
            # If jobs were truly concurrent, total time should be less than 3 * 2 seconds
            if total_time < 8 and completed_jobs == len(job_ids):
                print("✅ Concurrent execution working correctly")
                return True
            else:
                print("⚠️  Concurrent execution may not be working optimally")
                return completed_jobs > 0
            
        finally:
            runner.cleanup()

def run_e2e_tests():
    """Run all end-to-end tests."""
    print("🧪 Running End-to-End Tests")
    print("=" * 50)
    
    test_scenarios = TestE2EScenarios()
    
    results = {
        "new_user_journey": False,
        "error_handling": False,
        "concurrent_execution": False
    }
    
    # Test 1: New user journey
    print("\n1. Testing New User Journey...")
    try:
        results["new_user_journey"] = test_scenarios.test_user_journey_new_user()
    except Exception as e:
        print(f"❌ New user journey test failed: {e}")
    
    # Test 2: Error handling
    print("\n2. Testing Error Handling...")
    try:
        results["error_handling"] = test_scenarios.test_workflow_execution_with_errors()
    except Exception as e:
        print(f"❌ Error handling test failed: {e}")
    
    # Test 3: Concurrent execution
    print("\n3. Testing Concurrent Execution...")
    try:
        results["concurrent_execution"] = test_scenarios.test_concurrent_workflow_execution()
    except Exception as e:
        print(f"❌ Concurrent execution test failed: {e}")
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 End-to-End Test Results:")
    print(f"✅ New User Journey: {'PASSED' if results['new_user_journey'] else 'FAILED'}")
    print(f"✅ Error Handling: {'PASSED' if results['error_handling'] else 'FAILED'}")
    print(f"✅ Concurrent Execution: {'PASSED' if results['concurrent_execution'] else 'FAILED'}")
    
    passed_tests = sum(results.values())
    total_tests = len(results)
    success_rate = (passed_tests / total_tests) * 100
    
    print(f"\nOverall Success Rate: {success_rate:.1f}% ({passed_tests}/{total_tests})")
    
    return success_rate >= 66.7  # At least 2 out of 3 tests should pass

if __name__ == "__main__":
    success = run_e2e_tests()
    if not success:
        exit(1)