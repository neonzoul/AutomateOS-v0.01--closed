"""
Workflow execution engine for AutomateOS.

This module contains the core workflow execution logic that orchestrates
the execution of nodes in a workflow definition.
"""

from typing import Dict, Any, List, Optional
from datetime import datetime
import logging

from .nodes import create_node, NodeExecutionError
from .models import Workflow

logger = logging.getLogger(__name__)

class WorkflowExecutionError(Exception):
    """Exception raised when workflow execution fails."""
    
    def __init__(self, message: str, workflow_id: int, details: Optional[Dict[str, Any]] = None):
        self.message = message
        self.workflow_id = workflow_id
        self.details = details or {}
        super().__init__(self.message)

class WorkflowEngine:
    """
    Workflow execution engine that processes workflow definitions.
    
    This engine takes a workflow definition and executes its nodes in sequence,
    handling data flow between nodes and error conditions.
    """
    
    def __init__(self):
        self.execution_context = {}
    
    def execute_workflow(self, workflow: Workflow, trigger_payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute a complete workflow.
        
        Args:
            workflow: Workflow model instance
            trigger_payload: Data from the webhook trigger
            
        Returns:
            Dict containing workflow execution results
            
        Raises:
            WorkflowExecutionError: If workflow execution fails
        """
        logger.info(f"Starting workflow execution: {workflow.id} - {workflow.name}")
        
        try:
            # Initialize execution context
            self.execution_context = {
                "workflow_id": workflow.id,
                "workflow_name": workflow.name,
                "started_at": datetime.utcnow().isoformat(),
                "trigger_payload": trigger_payload,
                "node_results": {},
                "current_data": trigger_payload
            }
            
            # Parse workflow definition
            definition = workflow.definition
            nodes = definition.get("nodes", [])
            connections = definition.get("connections", [])
            
            if not nodes:
                raise WorkflowExecutionError(
                    message="Workflow has no nodes defined",
                    workflow_id=workflow.id,
                    details={"definition": definition}
                )
            
            # Execute nodes in sequence
            execution_results = self._execute_nodes(nodes, connections, trigger_payload)
            
            # Compile final results
            result = {
                "workflow_id": workflow.id,
                "workflow_name": workflow.name,
                "status": "success",
                "started_at": self.execution_context["started_at"],
                "completed_at": datetime.utcnow().isoformat(),
                "trigger_payload": trigger_payload,
                "node_results": execution_results,
                "final_data": self.execution_context["current_data"]
            }
            
            logger.info(f"Workflow execution completed successfully: {workflow.id}")
            return result
            
        except NodeExecutionError as e:
            # Handle node execution errors
            error_result = {
                "workflow_id": workflow.id,
                "workflow_name": workflow.name,
                "status": "failed",
                "started_at": self.execution_context.get("started_at"),
                "failed_at": datetime.utcnow().isoformat(),
                "error": {
                    "type": "node_execution_error",
                    "message": e.message,
                    "node_id": e.node_id,
                    "node_type": e.node_type,
                    "details": e.details
                },
                "node_results": self.execution_context.get("node_results", {}),
                "trigger_payload": trigger_payload
            }
            
            logger.error(f"Workflow execution failed at node {e.node_id}: {e.message}")
            raise WorkflowExecutionError(
                message=f"Node execution failed: {e.message}",
                workflow_id=workflow.id,
                details=error_result
            )
            
        except Exception as e:
            # Handle unexpected errors
            error_result = {
                "workflow_id": workflow.id,
                "workflow_name": workflow.name,
                "status": "failed",
                "started_at": self.execution_context.get("started_at"),
                "failed_at": datetime.utcnow().isoformat(),
                "error": {
                    "type": "workflow_execution_error",
                    "message": str(e),
                    "details": {}
                },
                "node_results": self.execution_context.get("node_results", {}),
                "trigger_payload": trigger_payload
            }
            
            logger.error(f"Workflow execution failed with unexpected error: {str(e)}")
            raise WorkflowExecutionError(
                message=f"Workflow execution failed: {str(e)}",
                workflow_id=workflow.id,
                details=error_result
            )
    
    def _execute_nodes(self, nodes: List[Dict[str, Any]], connections: List[Dict[str, Any]], initial_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute workflow nodes in sequence.
        
        Args:
            nodes: List of node definitions
            connections: List of node connections (for future use)
            initial_data: Initial data from trigger
            
        Returns:
            Dict containing results from all executed nodes
        """
        node_results = {}
        current_data = initial_data
        
        # For MVP, execute nodes in the order they appear in the definition
        # Future versions can use connections for more complex flow control
        for node_def in nodes:
            node_id = node_def.get("id")
            node_type = node_def.get("type")
            node_config = node_def.get("config", {})
            
            if not node_id or not node_type:
                raise WorkflowExecutionError(
                    message="Node missing required id or type",
                    workflow_id=self.execution_context["workflow_id"],
                    details={"node_definition": node_def}
                )
            
            logger.info(f"Executing node: {node_id} ({node_type})")
            
            try:
                # Create and execute node
                node = create_node(node_type, node_config)
                node.node_id = node_id  # Set the node ID from definition
                
                # Execute node with current data
                node_result = node.safe_execute(current_data)
                
                # Store node result
                node_results[node_id] = node_result
                
                # Update current data with node output
                # This makes the node's output available to subsequent nodes
                current_data = self._merge_data(current_data, node_result["data"], node_id)
                
                # Update execution context
                self.execution_context["node_results"][node_id] = node_result
                self.execution_context["current_data"] = current_data
                
                logger.info(f"Node {node_id} executed successfully")
                
            except NodeExecutionError as e:
                # Add node context and re-raise
                logger.error(f"Node {node_id} execution failed: {e.message}")
                raise e
            
            except Exception as e:
                # Wrap unexpected errors
                logger.error(f"Unexpected error in node {node_id}: {str(e)}")
                raise NodeExecutionError(
                    message=f"Unexpected error in node {node_id}: {str(e)}",
                    node_id=node_id,
                    node_type=node_type,
                    details={"original_error": str(e)}
                )
        
        return node_results
    
    def _merge_data(self, current_data: Dict[str, Any], node_output: Dict[str, Any], node_id: str) -> Dict[str, Any]:
        """
        Merge node output into current workflow data.
        
        Args:
            current_data: Current workflow data
            node_output: Output from executed node
            node_id: ID of the executed node
            
        Returns:
            Dict containing merged data
        """
        # Create a new data dictionary with node output accessible by node ID
        merged_data = current_data.copy()
        merged_data[node_id] = node_output
        
        # For convenience, also merge top-level keys from node output
        # This allows templates like {{response.status_code}} instead of {{http_node.response.status_code}}
        if isinstance(node_output, dict):
            for key, value in node_output.items():
                if key not in merged_data:  # Don't overwrite existing keys
                    merged_data[key] = value
        
        # Also make payload data directly accessible for filter conditions
        if "payload" in current_data:
            payload = current_data["payload"]
            if isinstance(payload, dict):
                for key, value in payload.items():
                    if key not in merged_data:
                        merged_data[key] = value
        
        return merged_data
    
    def validate_workflow_definition(self, definition: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate a workflow definition without executing it.
        
        Args:
            definition: Workflow definition to validate
            
        Returns:
            Dict containing validation results
        """
        validation_result = {
            "valid": True,
            "errors": [],
            "warnings": [],
            "node_validations": {}
        }
        
        try:
            nodes = definition.get("nodes", [])
            connections = definition.get("connections", [])
            
            if not nodes:
                validation_result["errors"].append("Workflow must have at least one node")
                validation_result["valid"] = False
                return validation_result
            
            # Validate each node
            for node_def in nodes:
                node_id = node_def.get("id")
                node_type = node_def.get("type")
                node_config = node_def.get("config", {})
                
                node_validation = {
                    "valid": True,
                    "errors": [],
                    "warnings": []
                }
                
                if not node_id:
                    node_validation["errors"].append("Node missing required 'id' field")
                    node_validation["valid"] = False
                
                if not node_type:
                    node_validation["errors"].append("Node missing required 'type' field")
                    node_validation["valid"] = False
                
                if node_type and node_id:
                    try:
                        # Try to create node to validate configuration
                        node = create_node(node_type, node_config)
                        node.node_id = node_id
                        # Configuration validation happens in node constructor
                        
                    except ValueError as e:
                        node_validation["errors"].append(f"Unsupported node type: {node_type}")
                        node_validation["valid"] = False
                        
                    except NodeExecutionError as e:
                        node_validation["errors"].append(f"Configuration error: {e.message}")
                        node_validation["valid"] = False
                
                validation_result["node_validations"][node_id or "unknown"] = node_validation
                
                if not node_validation["valid"]:
                    validation_result["valid"] = False
                    validation_result["errors"].extend([
                        f"Node {node_id}: {error}" for error in node_validation["errors"]
                    ])
            
            # Check for trigger node
            trigger_nodes = [node for node in nodes if node.get("type") == "webhook"]
            if not trigger_nodes:
                validation_result["warnings"].append("Workflow has no webhook trigger node")
            elif len(trigger_nodes) > 1:
                validation_result["warnings"].append("Workflow has multiple trigger nodes")
            
            return validation_result
            
        except Exception as e:
            validation_result["valid"] = False
            validation_result["errors"].append(f"Validation error: {str(e)}")
            return validation_result