#!/usr/bin/env python3
"""
Integration test for complete workflow execution.

This script tests the end-to-end workflow execution including
database integration, queue processing, and node execution.
"""

import time
import json
from datetime import datetime
from app.database import create_db_and_tables, get_session
from app import crud, schemas, models
from app.queue import enqueue_workflow_execution, get_job_status

def setup_test_workflow():
    """Create a test workflow with multiple nodes."""
    print("Setting up test workflow...")
    
    # Create database tables
    create_db_and_tables()
    
    session = next(get_session())
    
    # Create test user
    test_user = schemas.UserCreate(
        email="integration@test.com",
        password="testpassword123"
    )
    
    # Check if user already exists
    existing_user = crud.get_user_by_email(session, test_user.email)
    if not existing_user:
        user = crud.create_user(session, test_user)
        print(f"✓ Created test user: {user.email}")
    else:
        user = existing_user
        print(f"✓ Using existing test user: {user.email}")
    
    # Create comprehensive test workflow
    workflow_definition = {
        "nodes": [
            {
                "id": "webhook-trigger",
                "type": "webhook",
                "config": {
                    "method": "POST"
                }
            },
            {
                "id": "api-call",
                "type": "http_request",
                "config": {
                    "url": "https://httpbin.org/post",
                    "method": "POST",
                    "headers": {
                        "Content-Type": "application/json",
                        "X-Source": "AutomateOS-Integration-Test"
                    },
                    "body": {
                        "original_payload": "{{trigger.payload}}",
                        "processed_at": "{{trigger.timestamp}}",
                        "test_data": {
                            "workflow_name": "Integration Test Workflow",
                            "node_id": "api-call"
                        }
                    }
                }
            },
            {
                "id": "success-filter",
                "type": "filter",
                "config": {
                    "condition": "{{response.status_code}} == 200",
                    "continue_on": True
                }
            }
        ],
        "connections": [
            {"from": "webhook-trigger", "to": "api-call"},
            {"from": "api-call", "to": "success-filter"}
        ]
    }
    
    test_workflow = schemas.WorkflowCreate(
        name="Integration Test Workflow",
        description="Comprehensive test workflow for integration testing",
        definition=workflow_definition,
        is_active=True
    )
    
    workflow = crud.create_workflow(session, test_workflow, user.id)
    print(f"✓ Created test workflow: {workflow.name}")
    print(f"✓ Webhook URL: {workflow.webhook_url}")
    
    session.close()
    return workflow

def test_workflow_execution(workflow):
    """Test complete workflow execution through the queue system."""
    print(f"\nTesting workflow execution...")
    
    # Create test payload
    test_payload = {
        "payload": {
            "event": "integration_test",
            "user": {
                "id": 12345,
                "name": "Integration Test User",
                "email": "test@integration.com"
            },
            "data": {
                "action": "test_workflow_execution",
                "timestamp": datetime.utcnow().isoformat(),
                "metadata": {
                    "test_run": True,
                    "version": "1.0.0"
                }
            }
        },
        "headers": {
            "Content-Type": "application/json",
            "User-Agent": "AutomateOS-Integration-Test/1.0"
        },
        "method": "POST",
        "url": f"http://localhost:8000{workflow.webhook_url}",
        "timestamp": datetime.utcnow().isoformat()
    }
    
    try:
        # Enqueue workflow execution
        job_id = enqueue_workflow_execution(workflow.id, test_payload)
        print(f"✓ Workflow execution enqueued with job ID: {job_id}")
        
        # Wait for job to complete (with timeout)
        max_wait = 30  # 30 seconds timeout
        wait_time = 0
        
        while wait_time < max_wait:
            job_status = get_job_status(job_id)
            status = job_status.get("status", "unknown")
            
            print(f"  Job status: {status} (waited {wait_time}s)")
            
            if status == "finished":
                print("✓ Job completed successfully")
                result = job_status.get("result", {})
                
                # Print execution results
                if isinstance(result, dict):
                    print(f"  Workflow status: {result.get('status', 'unknown')}")
                    print(f"  Nodes executed: {len(result.get('node_results', {}))}")
                    
                    # Print node results
                    for node_id, node_result in result.get('node_results', {}).items():
                        node_status = node_result.get('status', 'unknown')
                        print(f"    - {node_id}: {node_status}")
                        
                        # Show HTTP response details for API call
                        if node_id == "api-call" and node_status == "success":
                            node_data = node_result.get('data', {})
                            response_data = node_data.get('response', {})
                            print(f"      HTTP Status: {response_data.get('status_code', 'unknown')}")
                
                return True
                
            elif status == "failed":
                print("✗ Job failed")
                error_info = job_status.get("exc_info", "No error details available")
                print(f"  Error: {error_info}")
                return False
                
            elif status in ["queued", "started"]:
                # Job is still processing
                time.sleep(1)
                wait_time += 1
                
            else:
                print(f"✗ Unexpected job status: {status}")
                return False
        
        print(f"✗ Job timed out after {max_wait} seconds")
        return False
        
    except Exception as e:
        print(f"✗ Workflow execution test failed: {e}")
        return False

def test_execution_logging(workflow):
    """Test that execution logs are properly created."""
    print(f"\nTesting execution logging...")
    
    try:
        session = next(get_session())
        
        # Get execution logs for the workflow
        logs = session.query(models.ExecutionLog).filter(
            models.ExecutionLog.workflow_id == workflow.id
        ).order_by(models.ExecutionLog.started_at.desc()).all()
        
        if not logs:
            print("✗ No execution logs found")
            return False
        
        latest_log = logs[0]
        print(f"✓ Found {len(logs)} execution log(s)")
        print(f"  Latest execution:")
        print(f"    Status: {latest_log.status}")
        print(f"    Started: {latest_log.started_at}")
        print(f"    Completed: {latest_log.completed_at}")
        
        if latest_log.status == "success":
            print(f"    Result keys: {list(latest_log.result.keys()) if latest_log.result else 'None'}")
        elif latest_log.status == "failed":
            print(f"    Error: {latest_log.error_message}")
        
        session.close()
        return True
        
    except Exception as e:
        print(f"✗ Execution logging test failed: {e}")
        return False

def test_error_handling():
    """Test error handling with invalid workflow."""
    print(f"\nTesting error handling...")
    
    try:
        # Create workflow with invalid HTTP URL
        session = next(get_session())
        
        # Get existing user
        user = crud.get_user_by_email(session, "integration@test.com")
        if not user:
            print("✗ Test user not found")
            return False
        
        # Create workflow with invalid configuration
        error_workflow_definition = {
            "nodes": [
                {
                    "id": "webhook-trigger",
                    "type": "webhook",
                    "config": {"method": "POST"}
                },
                {
                    "id": "bad-api-call",
                    "type": "http_request",
                    "config": {
                        "url": "https://invalid-domain-that-does-not-exist.com/api",
                        "method": "GET",
                        "timeout": 5
                    }
                }
            ]
        }
        
        error_workflow = schemas.WorkflowCreate(
            name="Error Test Workflow",
            description="Workflow designed to test error handling",
            definition=error_workflow_definition,
            is_active=True
        )
        
        workflow = crud.create_workflow(session, error_workflow, user.id)
        session.close()
        
        # Test payload
        test_payload = {
            "payload": {"test": "error_handling"},
            "method": "POST",
            "timestamp": datetime.utcnow().isoformat()
        }
        
        # Enqueue workflow execution
        job_id = enqueue_workflow_execution(workflow.id, test_payload)
        print(f"✓ Error test workflow enqueued with job ID: {job_id}")
        
        # Wait for job to fail
        max_wait = 15
        wait_time = 0
        
        while wait_time < max_wait:
            job_status = get_job_status(job_id)
            status = job_status.get("status", "unknown")
            
            if status == "failed":
                print("✓ Job correctly failed as expected")
                print(f"  Error handled gracefully")
                return True
                
            elif status in ["queued", "started"]:
                time.sleep(1)
                wait_time += 1
                
            else:
                print(f"  Job status: {status} (waited {wait_time}s)")
                time.sleep(1)
                wait_time += 1
        
        print("✗ Job should have failed but didn't within timeout")
        return False
        
    except Exception as e:
        print(f"✗ Error handling test failed: {e}")
        return False

def main():
    """Run integration tests."""
    print("AutomateOS Integration Test")
    print("=" * 30)
    
    # Setup test workflow
    workflow = setup_test_workflow()
    
    # Run tests
    tests = [
        lambda: test_workflow_execution(workflow),
        lambda: test_execution_logging(workflow),
        test_error_handling
    ]
    
    passed = 0
    for i, test in enumerate(tests, 1):
        print(f"\n--- Test {i}/{len(tests)} ---")
        if test():
            passed += 1
    
    print(f"\nIntegration Test Results: {passed}/{len(tests)} passed")
    
    if passed == len(tests):
        print("✓ All integration tests passed! The system is working end-to-end.")
    else:
        print("✗ Some integration tests failed.")
        print("Note: Make sure Redis is running and the worker is started for full functionality.")

if __name__ == "__main__":
    main()