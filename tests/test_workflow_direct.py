#!/usr/bin/env python3
"""
Direct workflow execution test (without queue).

This script tests workflow execution directly without using the queue system,
allowing us to verify the node execution logic works correctly.
"""

import json
from datetime import datetime
from app.database import create_db_and_tables, get_session
from app import crud, schemas, models
from app.workflow_engine import WorkflowEngine

def test_direct_workflow_execution():
    """Test direct workflow execution without queue."""
    print("Testing direct workflow execution...")
    
    # Create database tables
    create_db_and_tables()
    
    session = next(get_session())
    
    # Create test user
    test_user = schemas.UserCreate(
        email="direct@test.com",
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
    
    # Create test workflow with comprehensive node chain
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
                        "X-Test": "AutomateOS-Direct-Test"
                    },
                    "body": {
                        "webhook_payload": "{{trigger.payload}}",
                        "timestamp": "{{trigger.timestamp}}",
                        "test_info": {
                            "node_id": "api-call",
                            "test_type": "direct_execution"
                        }
                    }
                }
            },
            {
                "id": "status-filter",
                "type": "filter",
                "config": {
                    "condition": "{{response.status_code}} == 200",
                    "continue_on": True
                }
            }
        ],
        "connections": [
            {"from": "webhook-trigger", "to": "api-call"},
            {"from": "api-call", "to": "status-filter"}
        ]
    }
    
    test_workflow = schemas.WorkflowCreate(
        name="Direct Test Workflow",
        description="Test workflow for direct execution",
        definition=workflow_definition,
        is_active=True
    )
    
    workflow = crud.create_workflow(session, test_workflow, user.id)
    print(f"✓ Created test workflow: {workflow.name}")
    
    # Create test payload
    test_payload = {
        "payload": {
            "event": "direct_test",
            "user": {
                "id": 999,
                "name": "Direct Test User",
                "email": "direct@test.com"
            },
            "data": {
                "action": "test_direct_execution",
                "metadata": {
                    "test_run": True,
                    "execution_type": "direct"
                }
            }
        },
        "headers": {
            "Content-Type": "application/json",
            "User-Agent": "AutomateOS-Direct-Test/1.0"
        },
        "method": "POST",
        "url": f"http://localhost:8000{workflow.webhook_url}",
        "timestamp": datetime.utcnow().isoformat()
    }
    
    try:
        # Execute workflow directly
        engine = WorkflowEngine()
        result = engine.execute_workflow(workflow, test_payload)
        
        print("✓ Workflow executed successfully")
        print(f"  Status: {result['status']}")
        print(f"  Nodes executed: {len(result['node_results'])}")
        
        # Print detailed results
        for node_id, node_result in result['node_results'].items():
            node_status = node_result['status']
            print(f"    - {node_id}: {node_status}")
            
            if node_id == "api-call" and node_status == "success":
                node_data = node_result['data']
                response = node_data.get('response', {})
                print(f"      HTTP Status: {response.get('status_code', 'unknown')}")
                print(f"      Response URL: {response.get('url', 'unknown')}")
            
            elif node_id == "status-filter" and node_status == "success":
                node_data = node_result['data']
                print(f"      Filter result: {node_data.get('result', 'unknown')}")
                print(f"      Should continue: {node_data.get('should_continue', 'unknown')}")
        
        # Create execution log manually (since we're not using the queue)
        execution_log = models.ExecutionLog(
            workflow_id=workflow.id,
            status="success",
            payload=test_payload,
            result=result,
            started_at=datetime.fromisoformat(result['started_at'].replace('Z', '+00:00')),
            completed_at=datetime.fromisoformat(result['completed_at'].replace('Z', '+00:00'))
        )
        session.add(execution_log)
        session.commit()
        print(f"✓ Execution log created with ID: {execution_log.id}")
        
        session.close()
        return True
        
    except Exception as e:
        print(f"✗ Workflow execution failed: {e}")
        session.close()
        return False

def test_error_workflow():
    """Test workflow with intentional error."""
    print("\nTesting error handling in workflow...")
    
    session = next(get_session())
    
    # Get existing user
    user = crud.get_user_by_email(session, "direct@test.com")
    if not user:
        print("✗ Test user not found")
        return False
    
    # Create workflow with invalid HTTP request
    error_workflow_definition = {
        "nodes": [
            {
                "id": "webhook-trigger",
                "type": "webhook",
                "config": {"method": "POST"}
            },
            {
                "id": "bad-request",
                "type": "http_request",
                "config": {
                    "url": "https://invalid-domain-12345.com/api",
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
    print(f"✓ Created error test workflow: {workflow.name}")
    
    # Test payload
    test_payload = {
        "payload": {"test": "error_handling"},
        "method": "POST",
        "timestamp": datetime.utcnow().isoformat()
    }
    
    try:
        # Execute workflow directly (should fail)
        engine = WorkflowEngine()
        result = engine.execute_workflow(workflow, test_payload)
        
        print("✗ Workflow should have failed but didn't")
        session.close()
        return False
        
    except Exception as e:
        print("✓ Workflow correctly failed as expected")
        print(f"  Error type: {type(e).__name__}")
        print(f"  Error message: {str(e)}")
        
        session.close()
        return True

def test_filter_conditions():
    """Test various filter conditions."""
    print("\nTesting filter conditions...")
    
    session = next(get_session())
    
    # Get existing user
    user = crud.get_user_by_email(session, "direct@test.com")
    if not user:
        print("✗ Test user not found")
        return False
    
    # Test different filter conditions
    filter_tests = [
        {
            "name": "Equality check (should pass)",
            "condition": "{{test_value}} == 42",
            "test_data": {"test_value": 42},
            "should_pass": True
        },
        {
            "name": "String comparison (should pass)",
            "condition": "{{status}} == \"success\"",
            "test_data": {"status": "success"},
            "should_pass": True
        },
        {
            "name": "Numeric comparison (should fail)",
            "condition": "{{score}} > 100",
            "test_data": {"score": 85},
            "should_pass": False
        }
    ]
    
    all_passed = True
    
    for i, test in enumerate(filter_tests, 1):
        print(f"  Test {i}: {test['name']}")
        
        # Create workflow with filter
        filter_workflow_definition = {
            "nodes": [
                {
                    "id": "webhook-trigger",
                    "type": "webhook",
                    "config": {"method": "POST"}
                },
                {
                    "id": "test-filter",
                    "type": "filter",
                    "config": {
                        "condition": test["condition"],
                        "continue_on": True
                    }
                }
            ]
        }
        
        filter_workflow = schemas.WorkflowCreate(
            name=f"Filter Test {i}",
            description=f"Test filter: {test['name']}",
            definition=filter_workflow_definition,
            is_active=True
        )
        
        workflow = crud.create_workflow(session, filter_workflow, user.id)
        
        # Test payload with test data
        test_payload = {
            "payload": test["test_data"],
            "method": "POST",
            "timestamp": datetime.utcnow().isoformat()
        }
        
        try:
            engine = WorkflowEngine()
            result = engine.execute_workflow(workflow, test_payload)
            
            if test["should_pass"]:
                print(f"    ✓ Filter passed as expected")
            else:
                print(f"    ✗ Filter should have failed but passed")
                all_passed = False
                
        except Exception as e:
            if not test["should_pass"]:
                print(f"    ✓ Filter correctly failed as expected")
            else:
                print(f"    ✗ Filter should have passed but failed: {e}")
                all_passed = False
    
    session.close()
    return all_passed

def main():
    """Run direct workflow execution tests."""
    print("AutomateOS Direct Workflow Execution Test")
    print("=" * 42)
    
    tests = [
        test_direct_workflow_execution,
        test_error_workflow,
        test_filter_conditions
    ]
    
    passed = 0
    for test in tests:
        if test():
            passed += 1
    
    print(f"\nDirect Test Results: {passed}/{len(tests)} passed")
    
    if passed == len(tests):
        print("✓ All direct execution tests passed! Node execution logic is working correctly.")
    else:
        print("✗ Some tests failed. Check the node implementation.")

if __name__ == "__main__":
    main()