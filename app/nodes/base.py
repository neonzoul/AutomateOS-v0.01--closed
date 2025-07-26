"""
Base node class and common utilities for workflow node execution.

This module defines the abstract base class that all workflow nodes must inherit from,
along with common utilities and error handling for node execution.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class NodeExecutionError(Exception):
    """Exception raised when a node fails to execute."""
    
    def __init__(self, message: str, node_id: str, node_type: str, details: Optional[Dict[str, Any]] = None):
        self.message = message
        self.node_id = node_id
        self.node_type = node_type
        self.details = details or {}
        super().__init__(self.message)

class NodeBase(ABC):
    """
    Abstract base class for all workflow nodes.
    
    All node types must inherit from this class and implement the execute method.
    This ensures consistent behavior and error handling across all node types.
    """
    
    def __init__(self, node_id: str, config: Dict[str, Any]):
        """
        Initialize the node with configuration.
        
        Args:
            node_id: Unique identifier for this node instance
            config: Node-specific configuration dictionary
        """
        self.node_id = node_id
        self.config = config
        self.node_type = self.__class__.__name__.replace("Node", "").lower()
        
        # Validate configuration on initialization
        self.validate_config()
    
    @abstractmethod
    def execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute the node with the given input data.
        
        Args:
            input_data: Data passed from previous nodes or trigger
            
        Returns:
            Dict containing the node's output data
            
        Raises:
            NodeExecutionError: If the node fails to execute
        """
        pass
    
    def validate_config(self) -> None:
        """
        Validate the node configuration.
        
        Override this method in subclasses to implement node-specific validation.
        
        Raises:
            NodeExecutionError: If configuration is invalid
        """
        pass
    
    def log_execution(self, status: str, input_data: Dict[str, Any], output_data: Optional[Dict[str, Any]] = None, error: Optional[str] = None):
        """
        Log node execution details.
        
        Args:
            status: Execution status ("success", "failed", "skipped")
            input_data: Input data for the execution
            output_data: Output data from the execution
            error: Error message if execution failed
        """
        log_entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "node_id": self.node_id,
            "node_type": self.node_type,
            "status": status,
            "input_data": input_data,
            "output_data": output_data,
            "error": error
        }
        
        if status == "success":
            logger.info(f"Node {self.node_id} executed successfully", extra=log_entry)
        elif status == "failed":
            logger.error(f"Node {self.node_id} execution failed: {error}", extra=log_entry)
        else:
            logger.info(f"Node {self.node_id} execution {status}", extra=log_entry)
    
    def safe_execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute the node with error handling and logging.
        
        This method wraps the execute method with consistent error handling
        and logging across all node types.
        
        Args:
            input_data: Data passed from previous nodes or trigger
            
        Returns:
            Dict containing the node's output data and execution metadata
        """
        try:
            logger.info(f"Executing node {self.node_id} ({self.node_type})")
            
            # Execute the node
            output_data = self.execute(input_data)
            
            # Add execution metadata
            result = {
                "node_id": self.node_id,
                "node_type": self.node_type,
                "status": "success",
                "data": output_data,
                "executed_at": datetime.utcnow().isoformat()
            }
            
            self.log_execution("success", input_data, output_data)
            return result
            
        except NodeExecutionError as e:
            # Re-raise node execution errors with additional context
            self.log_execution("failed", input_data, error=str(e))
            raise e
            
        except Exception as e:
            # Wrap unexpected errors in NodeExecutionError
            error_msg = f"Unexpected error in node {self.node_id}: {str(e)}"
            self.log_execution("failed", input_data, error=error_msg)
            raise NodeExecutionError(
                message=error_msg,
                node_id=self.node_id,
                node_type=self.node_type,
                details={"original_error": str(e)}
            )
    
    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(id='{self.node_id}', type='{self.node_type}')"