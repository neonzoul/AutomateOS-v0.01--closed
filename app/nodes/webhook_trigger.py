"""
Webhook trigger node implementation.

This module implements the webhook trigger node that serves as the entry point
for workflows triggered by external HTTP requests.
"""

from typing import Dict, Any
from .base import NodeBase, NodeExecutionError

class WebhookTriggerNode(NodeBase):
    """
    Webhook trigger node that processes incoming HTTP requests.
    
    This node serves as the starting point for workflows triggered by webhooks.
    It processes the incoming request payload and makes it available to subsequent nodes.
    """
    
    def validate_config(self) -> None:
        """
        Validate webhook trigger configuration.
        
        Raises:
            NodeExecutionError: If configuration is invalid
        """
        required_fields = ["method"]
        
        for field in required_fields:
            if field not in self.config:
                raise NodeExecutionError(
                    message=f"Missing required field: {field}",
                    node_id=self.node_id,
                    node_type=self.node_type,
                    details={"missing_field": field}
                )
        
        # Validate HTTP method
        allowed_methods = ["GET", "POST", "PUT", "DELETE", "PATCH"]
        method = self.config["method"].upper()
        
        if method not in allowed_methods:
            raise NodeExecutionError(
                message=f"Invalid HTTP method: {method}",
                node_id=self.node_id,
                node_type=self.node_type,
                details={"invalid_method": method, "allowed_methods": allowed_methods}
            )
    
    def execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute the webhook trigger node.
        
        For webhook triggers, the execution simply processes and validates
        the incoming request data, making it available to subsequent nodes.
        
        Args:
            input_data: Request payload from the webhook endpoint
            
        Returns:
            Dict containing processed webhook data
        """
        # Extract webhook payload
        payload = input_data.get("payload", {})
        headers = input_data.get("headers", {})
        method = input_data.get("method", "POST")
        url = input_data.get("url", "")
        timestamp = input_data.get("timestamp", "")
        
        # Process and structure the webhook data
        webhook_data = {
            "trigger": {
                "type": "webhook",
                "method": method,
                "url": url,
                "timestamp": timestamp,
                "payload": payload,
                "headers": dict(headers) if headers else {}
            },
            "raw_payload": payload
        }
        
        # Validate that we have some data to work with
        if not payload and method in ["POST", "PUT", "PATCH"]:
            # For methods that typically have payloads, warn if empty
            # but don't fail - some webhooks might have empty payloads
            pass
        
        return webhook_data
    
    def get_webhook_url(self) -> str:
        """
        Get the webhook URL for this trigger.
        
        Returns:
            str: The webhook URL path
        """
        return self.config.get("webhook_url", f"/webhook/{self.node_id}")
    
    def supports_method(self, method: str) -> bool:
        """
        Check if this webhook trigger supports the given HTTP method.
        
        Args:
            method: HTTP method to check
            
        Returns:
            bool: True if method is supported
        """
        configured_method = self.config.get("method", "POST").upper()
        return method.upper() == configured_method