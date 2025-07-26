#!/usr/bin/env python3
"""
Test script for node execution logic.

This script tests individual nodes and the workflow execution engine
to ensure proper functionality of the node execution system.
"""

import json
from app.nodes import create_node, NodeExecutionError
from app.workflow_engine import WorkflowEngine, WorkflowExecutionError
from app.models import Workflow
from datetime import datetime

def test_webhook_trigger_node():
    """Test webhook trigger node execution."""
    print("Testing WebhookTriggerNode...")
    
    try:
        # Create webhook trigger node
        config = {
            "method": "POST",
            "webhook_url": "/webhook/test-123"
        }
        
        node = create_node("webhook", config)
        node.node_id = "trigger-1"
        
        # Test input data
        input_data = {
            "payload": {
                "user_id": 123,
                "action": "user_created",
                "data": {"name": "John Doe", "email": "john@example.com"}
            },
            "headers": {"Content-Type": "application/json"},
            "method": "POST",
            "url": "http://localhost:8000/webhook/test-123",
            "timestamp": datetime.utcnow().isoformat()
        }
        
        # Execute node
        result = node.safe_execute(input_data)
        
        print("✓ WebhookTriggerNode executed successfully")
        print(f"  Result: {json.dumps(result, indent=2)}")
        return True
        
    except Exception as e:
        print(f"✗ WebhookTriggerNode failed: {e}")
        return False

def test_http_request_node():
    """Test HTTP request node execution."""
    print("\nTesting HTTPRequestNode...")
    
    try:
        # Create HTTP request node
        config = {
            "url": "https://httpbin.org/post",
            "method": "POST",
            "headers": {
                "Content-Type": "application/json",
                "User-Agent": "AutomateOS/1.0"
            },
            "body": {
                "message": "Test from AutomateOS",
                "user_data": "{{trigger.payload.data}}",
                "timestamp": "{{trigger.timestamp}}"
            }
        }
        
        node = create_node("http_request", config)
        node.node_id = "http-1"
        
        # Test input data with template variables
        input_data = {
            "trigger": {
                "payload": {
                    "data": {"name": "John Doe", "email": "john@example.com"}
                },
                "timestamp": datetime.utcnow().isoformat()
            }
        }
        
        # Execute node
        result = node.safe_execute(input_data)
        
        print("✓ HTTPRequestNode executed successfully")
        print(f"  Status Code: {result['data']['status_code']}")
        print(f"  Success: {result['data']['success']}")
        return True
        
    except Exception as e:
        print(f"✗ HTTPRequestNode failed: {e}")
        return False

def test_filter_node():
    """Test filter node execution."""
    print("\nTesting FilterNode...")
    
    try:
        # Test 1: Condition that should pass
        config = {
            "condition": "{{response.status_code}} == 200",
            "continue_on": True
        }
        
        node = create_node("filter", config)
        node.node_id = "filter-1"
        
        # Test input data
        input_data = {
            "response": {
                "status_code": 200,
                "json": {"success": True}
            }
        }
        
        # Execute node
        result = node.safe_execute(input_data)
        
        print("✓ FilterNode (passing condition) executed successfully")
        print(f"  Should continue: {result['data']['should_continue']}")
        
        # Test 2: Condition that should fail
        config_fail = {
            "condition": "{{response.status_code}} == 404",
            "continue_on": True
        }
        
        node_fail = create_node("filter", config_fail)
        node_fail.node_id = "filter-2"
        
        try:
            result_fail = node_fail.safe_execute(input_data)
            print("✗ FilterNode should have failed but didn't")
            return False
        except NodeExecutionError as e:
            print("✓ FilterNode correctly failed on condition not met")
            print(f"  Error: {e.message}")
        
        return True
        
    except Exception as e:
        print(f"✗ FilterNode failed: {e}")
        return False

def test_workflow_engine():
    """Test complete workflow execution."""
    print("\nTesting WorkflowEngine...")
    
    try:
        # Create a test workflow definition
        workflow_definition = {
            "nodes": [
                {
                    "id": "trigger-1",
                    "type": "webhook",
                    "config": {
                        "method": "POST"
                    }
                },
                {
                    "id": "http-1",
                    "type": "http_request",
                    "config": {
                        "url": "https://httpbin.org/post",
                        "method": "POST",
                        "headers": {
                            "Content-Type": "application/json"
                        },
                        "body": {
                            "webhook_data": "{{trigger.payload}}",
                            "processed_at": "{{trigger.timestamp}}"
                        }
                    }
                },
                {
                    "id": "filter-1",
                    "type": "filter",
                    "config": {
                        "condition": "{{response.status_code}} == 200",
                        "continue_on": True
                    }
                }
            ],
            "connections": [
                {"from": "trigger-1", "to": "http-1"},
                {"from": "http-1", "to": "filter-1"}
            ]
        }
        
        # Create mock workflow object
        class MockWorkflow:
            def __init__(self):
                self.id = 1
                self.name = "Test Workflow"
                self.definition = workflow_definition
        
        workflow = MockWorkflow()
        
        # Test trigger payload
        trigger_payload = {
            "payload": {
                "test": True,
                "message": "Test workflow execution",
                "user": {"id": 123, "name": "Test User"}
            },
            "headers": {"Content-Type": "application/json"},
            "method": "POST",
            "timestamp": datetime.utcnow().isoformat()
        }
        
        # Execute workflow
        engine = WorkflowEngine()
        result = engine.execute_workflow(workflow, trigger_payload)
        
        print("✓ WorkflowEngine executed successfully")
        print(f"  Status: {result['status']}")
        print(f"  Nodes executed: {len(result['node_results'])}")
        
        # Print node results
        for node_id, node_result in result['node_results'].items():
            print(f"  - {node_id}: {node_result['status']}")
        
        return True
        
    except Exception as e:
        print(f"✗ WorkflowEngine failed: {e}")
        return False

def test_workflow_validation():
    """Test workflow definition validation."""
    print("\nTesting workflow validation...")
    
    try:
        engine = WorkflowEngine()
        
        # Test valid workflow
        valid_definition = {
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
                        "url": "https://api.example.com/data",
                        "method": "GET"
                    }
                }
            ]
        }
        
        validation_result = engine.validate_workflow_definition(valid_definition)
        
        if validation_result["valid"]:
            print("✓ Valid workflow definition passed validation")
        else:
            print(f"✗ Valid workflow failed validation: {validation_result['errors']}")
            return False
        
        # Test invalid workflow
        invalid_definition = {
            "nodes": [
                {
                    "id": "trigger-1",
                    "type": "webhook"
                    # Missing config
                },
                {
                    # Missing id and type
                    "config": {"url": "https://api.example.com"}
                }
            ]
        }
        
        validation_result = engine.validate_workflow_definition(invalid_definition)
        
        if not validation_result["valid"]:
            print("✓ Invalid workflow definition correctly failed validation")
            print(f"  Errors: {validation_result['errors']}")
        else:
            print("✗ Invalid workflow should have failed validation")
            return False
        
        return True
        
    except Exception as e:
        print(f"✗ Workflow validation failed: {e}")
        return False

def main():
    """Run all node execution tests."""
    print("AutomateOS Node Execution Test")
    print("=" * 35)
    
    tests = [
        test_webhook_trigger_node,
        test_http_request_node,
        test_filter_node,
        test_workflow_engine,
        test_workflow_validation
    ]
    
    passed = 0
    for test in tests:
        if test():
            passed += 1
    
    print(f"\nTest Results: {passed}/{len(tests)} passed")
    
    if passed == len(tests):
        print("✓ All tests passed! Node execution logic is working.")
    else:
        print("✗ Some tests failed. Check the implementation.")

if __name__ == "__main__":
    main()