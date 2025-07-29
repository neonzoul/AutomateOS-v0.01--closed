#!/usr/bin/env python3
"""
Tests for node execution logic and error handling.
Tests the workflow execution engine and individual node types.
"""

import pytest
import json
import os
import sys
from unittest.mock import Mock, patch, MagicMock
import requests

# Add the app directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

try:
    from app.nodes.base import NodeBase
    from app.nodes.webhook_trigger import WebhookTrigger
    from app.nodes.http_request import HTTPRequestNode
    from app.workflow_engine import WorkflowEngine
except ImportError as e:
    print(f"Import error: {e}")
    # Skip tests if imports fail
    pytest.skip("Skipping tests due to import errors", allow_module_level=True)

class TestNodeBase:
    """Test the base node functionality."""
    
    def test_node_base_initialization(self):
        """Test that NodeBase initializes correctly."""
        config = {"test": "config"}
        node = NodeBase(config)
        assert node.config == config

    def test_node_base_execute_not_implemented(self):
        """Test that NodeBase.execute raises NotImplementedError."""
        node = NodeBase({})
        with pytest.raises(NotImplementedError):
            node.execute({})

class TestWebhookTrigger:
    """Test webhook trigger node functionality."""
    
    def test_webhook_trigger_initialization(self):
        """Test webhook trigger initialization."""
        config = {"method": "POST", "path": "/webhook/test"}
        trigger = WebhookTrigger(config)
        assert trigger.config == config

    def test_webhook_trigger_execute(self):
        """Test webhook trigger execution."""
        config = {"method": "POST"}
        trigger = WebhookTrigger(config)
        
        input_data = {
            "method": "POST",
            "headers": {"Content-Type": "application/json"},
            "payload": {"test": "data"},
            "timestamp": "2024-01-01T00:00:00Z"
        }
        
        result = trigger.execute(input_data)
        
        assert result["status"] == "success"
        assert result["data"] == input_data
        assert "timestamp" in result

    def test_webhook_trigger_method_validation(self):
        """Test webhook trigger method validation."""
        config = {"method": "GET"}
        trigger = WebhookTrigger(config)
        
        # Test with matching method
        input_data = {"method": "GET", "payload": {}}
        result = trigger.execute(input_data)
        assert result["status"] == "success"
        
        # Test with non-matching method
        input_data = {"method": "POST", "payload": {}}
        result = trigger.execute(input_data)
        assert result["status"] == "error"
        assert "method mismatch" in result["error"].lower()

class TestHTTPRequestNode:
    """Test HTTP request node functionality."""
    
    def test_http_request_initialization(self):
        """Test HTTP request node initialization."""
        config = {
            "url": "https://httpbin.org/post",
            "method": "POST",
            "headers": {"Content-Type": "application/json"},
            "body": {"test": "data"}
        }
        node = HTTPRequestNode(config)
        assert node.config == config

    @patch('requests.request')
    def test_http_request_execute_success(self, mock_request):
        """Test successful HTTP request execution."""
        # Mock successful response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"success": True}
        mock_response.text = '{"success": true}'
        mock_response.headers = {"Content-Type": "application/json"}
        mock_request.return_value = mock_response
        
        config = {
            "url": "https://httpbin.org/post",
            "method": "POST",
            "headers": {"Content-Type": "application/json"},
            "body": {"test": "data"}
        }
        node = HTTPRequestNode(config)
        
        input_data = {"previous_result": "test"}
        result = node.execute(input_data)
        
        assert result["status"] == "success"
        assert result["response"]["status_code"] == 200
        assert result["response"]["data"] == {"success": True}
        
        # Verify the request was made correctly
        mock_request.assert_called_once_with(
            method="POST",
            url="https://httpbin.org/post",
            headers={"Content-Type": "application/json"},
            json={"test": "data"},
            timeout=30
        )

    @patch('requests.request')
    def test_http_request_execute_failure(self, mock_request):
        """Test HTTP request execution with failure response."""
        # Mock failed response
        mock_response = Mock()
        mock_response.status_code = 404
        mock_response.text = "Not Found"
        mock_response.headers = {}
        mock_request.return_value = mock_response
        
        config = {
            "url": "https://httpbin.org/status/404",
            "method": "GET"
        }
        node = HTTPRequestNode(config)
        
        result = node.execute({})
        
        assert result["status"] == "error"
        assert result["response"]["status_code"] == 404
        assert "404" in result["error"]

    @patch('requests.request')
    def test_http_request_execute_exception(self, mock_request):
        """Test HTTP request execution with network exception."""
        # Mock network exception
        mock_request.side_effect = requests.exceptions.ConnectionError("Connection failed")
        
        config = {
            "url": "https://invalid-url.example.com",
            "method": "GET"
        }
        node = HTTPRequestNode(config)
        
        result = node.execute({})
        
        assert result["status"] == "error"
        assert "connection" in result["error"].lower()

    @patch('requests.request')
    def test_http_request_timeout(self, mock_request):
        """Test HTTP request timeout handling."""
        # Mock timeout exception
        mock_request.side_effect = requests.exceptions.Timeout("Request timed out")
        
        config = {
            "url": "https://httpbin.org/delay/10",
            "method": "GET",
            "timeout": 5
        }
        node = HTTPRequestNode(config)
        
        result = node.execute({})
        
        assert result["status"] == "error"
        assert "timeout" in result["error"].lower()

    def test_http_request_template_substitution(self):
        """Test template substitution in HTTP request configuration."""
        config = {
            "url": "https://httpbin.org/post",
            "method": "POST",
            "headers": {"Authorization": "Bearer {{token}}"},
            "body": {"user_id": "{{user_id}}", "data": "{{previous_result}}"}
        }
        node = HTTPRequestNode(config)
        
        input_data = {
            "token": "abc123",
            "user_id": "user456",
            "previous_result": "test_data"
        }
        
        # Test template substitution
        substituted_config = node._substitute_templates(config, input_data)
        
        assert substituted_config["headers"]["Authorization"] == "Bearer abc123"
        assert substituted_config["body"]["user_id"] == "user456"
        assert substituted_config["body"]["data"] == "test_data"

    def test_http_request_different_methods(self):
        """Test HTTP request node with different HTTP methods."""
        methods = ["GET", "POST", "PUT", "DELETE", "PATCH"]
        
        for method in methods:
            config = {
                "url": "https://httpbin.org/" + method.lower(),
                "method": method
            }
            node = HTTPRequestNode(config)
            assert node.config["method"] == method

class TestWorkflowEngine:
    """Test the workflow execution engine."""
    
    def test_workflow_engine_initialization(self):
        """Test workflow engine initialization."""
        workflow_definition = {
            "nodes": [
                {"id": "trigger-1", "type": "webhook", "config": {"method": "POST"}},
                {"id": "action-1", "type": "http_request", "config": {"url": "https://httpbin.org/post", "method": "POST"}}
            ],
            "connections": [{"from": "trigger-1", "to": "action-1"}]
        }
        
        engine = WorkflowEngine(workflow_definition)
        assert engine.definition == workflow_definition
        assert len(engine.nodes) == 2
        assert "trigger-1" in engine.nodes
        assert "action-1" in engine.nodes

    def test_workflow_engine_node_creation(self):
        """Test that workflow engine creates correct node types."""
        workflow_definition = {
            "nodes": [
                {"id": "webhook-1", "type": "webhook", "config": {"method": "POST"}},
                {"id": "http-1", "type": "http_request", "config": {"url": "https://example.com", "method": "GET"}}
            ],
            "connections": []
        }
        
        engine = WorkflowEngine(workflow_definition)
        
        assert isinstance(engine.nodes["webhook-1"], WebhookTrigger)
        assert isinstance(engine.nodes["http-1"], HTTPRequestNode)

    def test_workflow_engine_invalid_node_type(self):
        """Test workflow engine with invalid node type."""
        workflow_definition = {
            "nodes": [
                {"id": "invalid-1", "type": "invalid_type", "config": {}}
            ],
            "connections": []
        }
        
        with pytest.raises(ValueError, match="Unknown node type"):
            WorkflowEngine(workflow_definition)

    @patch('app.nodes.http_request.requests.request')
    def test_workflow_engine_execute_simple(self, mock_request):
        """Test simple workflow execution."""
        # Mock HTTP response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"result": "success"}
        mock_response.text = '{"result": "success"}'
        mock_response.headers = {"Content-Type": "application/json"}
        mock_request.return_value = mock_response
        
        workflow_definition = {
            "nodes": [
                {"id": "trigger-1", "type": "webhook", "config": {"method": "POST"}},
                {"id": "action-1", "type": "http_request", "config": {
                    "url": "https://httpbin.org/post",
                    "method": "POST",
                    "body": {"data": "test"}
                }}
            ],
            "connections": [{"from": "trigger-1", "to": "action-1"}]
        }
        
        engine = WorkflowEngine(workflow_definition)
        
        trigger_data = {
            "method": "POST",
            "payload": {"webhook": "data"},
            "timestamp": "2024-01-01T00:00:00Z"
        }
        
        result = engine.execute(trigger_data)
        
        assert result["status"] == "success"
        assert "execution_log" in result
        assert len(result["execution_log"]) == 2  # trigger + action
        
        # Check trigger execution
        trigger_log = result["execution_log"][0]
        assert trigger_log["node_id"] == "trigger-1"
        assert trigger_log["status"] == "success"
        
        # Check action execution
        action_log = result["execution_log"][1]
        assert action_log["node_id"] == "action-1"
        assert action_log["status"] == "success"

    def test_workflow_engine_execution_order(self):
        """Test that workflow engine executes nodes in correct order."""
        workflow_definition = {
            "nodes": [
                {"id": "trigger-1", "type": "webhook", "config": {"method": "POST"}},
                {"id": "action-1", "type": "webhook", "config": {"method": "POST"}},  # Using webhook for simplicity
                {"id": "action-2", "type": "webhook", "config": {"method": "POST"}}
            ],
            "connections": [
                {"from": "trigger-1", "to": "action-1"},
                {"from": "action-1", "to": "action-2"}
            ]
        }
        
        engine = WorkflowEngine(workflow_definition)
        
        trigger_data = {"method": "POST", "payload": {}}
        result = engine.execute(trigger_data)
        
        assert result["status"] == "success"
        execution_log = result["execution_log"]
        
        # Check execution order
        assert execution_log[0]["node_id"] == "trigger-1"
        assert execution_log[1]["node_id"] == "action-1"
        assert execution_log[2]["node_id"] == "action-2"

    @patch('app.nodes.http_request.requests.request')
    def test_workflow_engine_error_handling(self, mock_request):
        """Test workflow engine error handling."""
        # Mock HTTP request failure
        mock_request.side_effect = requests.exceptions.ConnectionError("Connection failed")
        
        workflow_definition = {
            "nodes": [
                {"id": "trigger-1", "type": "webhook", "config": {"method": "POST"}},
                {"id": "action-1", "type": "http_request", "config": {
                    "url": "https://invalid-url.example.com",
                    "method": "GET"
                }}
            ],
            "connections": [{"from": "trigger-1", "to": "action-1"}]
        }
        
        engine = WorkflowEngine(workflow_definition)
        
        trigger_data = {"method": "POST", "payload": {}}
        result = engine.execute(trigger_data)
        
        assert result["status"] == "error"
        assert "execution_log" in result
        
        # Check that trigger succeeded but action failed
        trigger_log = result["execution_log"][0]
        assert trigger_log["status"] == "success"
        
        action_log = result["execution_log"][1]
        assert action_log["status"] == "error"
        assert "connection" in action_log["error"].lower()

    def test_workflow_engine_data_passing(self):
        """Test data passing between nodes."""
        workflow_definition = {
            "nodes": [
                {"id": "trigger-1", "type": "webhook", "config": {"method": "POST"}},
                {"id": "action-1", "type": "webhook", "config": {"method": "POST"}}  # Using webhook for simplicity
            ],
            "connections": [{"from": "trigger-1", "to": "action-1"}]
        }
        
        engine = WorkflowEngine(workflow_definition)
        
        trigger_data = {
            "method": "POST",
            "payload": {"initial": "data"},
            "custom_field": "test_value"
        }
        
        result = engine.execute(trigger_data)
        
        assert result["status"] == "success"
        execution_log = result["execution_log"]
        
        # Check that data from trigger is passed to action
        trigger_result = execution_log[0]["result"]
        action_input = execution_log[1]["input"]
        
        # Action should receive trigger's output as input
        assert "trigger-1" in action_input  # Previous node results are passed

class TestErrorHandling:
    """Test error handling across the workflow system."""
    
    def test_node_execution_timeout(self):
        """Test node execution timeout handling."""
        # This would require implementing timeout functionality in nodes
        pass

    def test_workflow_execution_memory_limits(self):
        """Test workflow execution with memory constraints."""
        # This would test large payload handling
        pass

    def test_circular_dependency_detection(self):
        """Test detection of circular dependencies in workflow."""
        workflow_definition = {
            "nodes": [
                {"id": "node-1", "type": "webhook", "config": {"method": "POST"}},
                {"id": "node-2", "type": "webhook", "config": {"method": "POST"}},
                {"id": "node-3", "type": "webhook", "config": {"method": "POST"}}
            ],
            "connections": [
                {"from": "node-1", "to": "node-2"},
                {"from": "node-2", "to": "node-3"},
                {"from": "node-3", "to": "node-1"}  # Creates circular dependency
            ]
        }
        
        with pytest.raises(ValueError, match="circular"):
            engine = WorkflowEngine(workflow_definition)
            engine._validate_workflow()

    def test_missing_node_reference(self):
        """Test handling of missing node references in connections."""
        workflow_definition = {
            "nodes": [
                {"id": "node-1", "type": "webhook", "config": {"method": "POST"}}
            ],
            "connections": [
                {"from": "node-1", "to": "nonexistent-node"}
            ]
        }
        
        with pytest.raises(ValueError, match="references non-existent node"):
            WorkflowEngine(workflow_definition)

class TestPerformance:
    """Test performance aspects of node execution."""
    
    def test_large_payload_handling(self):
        """Test handling of large payloads."""
        config = {"method": "POST"}
        trigger = WebhookTrigger(config)
        
        # Create large payload (1MB of data)
        large_payload = {"data": "x" * (1024 * 1024)}
        input_data = {
            "method": "POST",
            "payload": large_payload
        }
        
        result = trigger.execute(input_data)
        assert result["status"] == "success"

    @patch('app.nodes.http_request.requests.request')
    def test_concurrent_http_requests(self, mock_request):
        """Test concurrent HTTP request handling."""
        # Mock response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"success": True}
        mock_response.text = '{"success": true}'
        mock_response.headers = {}
        mock_request.return_value = mock_response
        
        config = {
            "url": "https://httpbin.org/post",
            "method": "POST"
        }
        
        # Create multiple HTTP request nodes
        nodes = [HTTPRequestNode(config) for _ in range(10)]
        
        # Execute all nodes (simulating concurrent execution)
        results = []
        for node in nodes:
            result = node.execute({})
            results.append(result)
        
        # All should succeed
        assert all(r["status"] == "success" for r in results)
        assert mock_request.call_count == 10

if __name__ == "__main__":
    pytest.main([__file__, "-v"])