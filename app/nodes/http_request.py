"""
HTTP request node implementation.

This module implements the HTTP request node that makes HTTP calls to external APIs
as part of workflow execution.
"""

import requests
from typing import Dict, Any, Optional
from urllib.parse import urlparse
import json
import re
from .base import NodeBase, NodeExecutionError

class HTTPRequestNode(NodeBase):
    """
    HTTP request node that makes HTTP calls to external APIs.
    
    This node can make GET, POST, PUT, DELETE, and PATCH requests with
    configurable headers, body, and URL parameters.
    """
    
    def validate_config(self) -> None:
        """
        Validate HTTP request configuration.
        
        Raises:
            NodeExecutionError: If configuration is invalid
        """
        required_fields = ["url", "method"]
        
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
        
        # Validate URL format
        url = self.config["url"]
        try:
            parsed = urlparse(url)
            if not parsed.scheme or not parsed.netloc:
                raise ValueError("Invalid URL format")
        except Exception:
            raise NodeExecutionError(
                message=f"Invalid URL format: {url}",
                node_id=self.node_id,
                node_type=self.node_type,
                details={"invalid_url": url}
            )
    
    def execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute the HTTP request node.
        
        Args:
            input_data: Data from previous nodes, used for template substitution
            
        Returns:
            Dict containing HTTP response data
        """
        # Process configuration with template substitution
        url = self._substitute_templates(self.config["url"], input_data)
        method = self.config["method"].upper()
        headers = self._process_headers(input_data)
        body = self._process_body(input_data)
        timeout = self.config.get("timeout", 30)
        
        try:
            # Make the HTTP request
            response = requests.request(
                method=method,
                url=url,
                headers=headers,
                data=body if isinstance(body, (str, bytes)) else None,
                json=body if isinstance(body, dict) else None,
                timeout=timeout
            )
            
            # Process response
            response_data = self._process_response(response)
            
            return {
                "request": {
                    "url": url,
                    "method": method,
                    "headers": headers,
                    "body": body
                },
                "response": response_data,
                "status_code": response.status_code,
                "success": response.ok
            }
            
        except requests.exceptions.Timeout:
            raise NodeExecutionError(
                message=f"HTTP request timed out after {timeout} seconds",
                node_id=self.node_id,
                node_type=self.node_type,
                details={"url": url, "timeout": timeout}
            )
            
        except requests.exceptions.ConnectionError as e:
            raise NodeExecutionError(
                message=f"Connection error: {str(e)}",
                node_id=self.node_id,
                node_type=self.node_type,
                details={"url": url, "error": str(e)}
            )
            
        except requests.exceptions.RequestException as e:
            raise NodeExecutionError(
                message=f"HTTP request failed: {str(e)}",
                node_id=self.node_id,
                node_type=self.node_type,
                details={"url": url, "error": str(e)}
            )
    
    def _substitute_templates(self, template: str, data: Dict[str, Any]) -> str:
        """
        Substitute template variables in strings.
        
        Supports templates like {{trigger.payload.field}} or {{previous_node.data.value}}
        
        Args:
            template: String with template variables
            data: Data dictionary for substitution
            
        Returns:
            str: String with variables substituted
        """
        if not isinstance(template, str):
            return template
        
        # Find all template variables
        pattern = r'\{\{([^}]+)\}\}'
        matches = re.findall(pattern, template)
        
        result = template
        for match in matches:
            # Parse the variable path (e.g., "trigger.payload.field")
            path_parts = match.strip().split('.')
            value = data
            
            try:
                for part in path_parts:
                    if isinstance(value, dict):
                        value = value.get(part)
                    else:
                        value = None
                        break
                
                if value is not None:
                    # Replace the template variable with the actual value
                    result = result.replace(f"{{{{{match}}}}}", str(value))
                
            except (KeyError, TypeError):
                # If template variable can't be resolved, leave it as is
                pass
        
        return result
    
    def _process_headers(self, input_data: Dict[str, Any]) -> Dict[str, str]:
        """
        Process and substitute templates in headers.
        
        Args:
            input_data: Data for template substitution
            
        Returns:
            Dict of processed headers
        """
        headers = self.config.get("headers", {})
        processed_headers = {}
        
        for key, value in headers.items():
            processed_key = self._substitute_templates(key, input_data)
            processed_value = self._substitute_templates(value, input_data)
            processed_headers[processed_key] = processed_value
        
        # Set default Content-Type if not specified and we have a body
        if "body" in self.config and "Content-Type" not in processed_headers:
            body = self.config["body"]
            if isinstance(body, dict) or (isinstance(body, str) and body.strip().startswith('{')):
                processed_headers["Content-Type"] = "application/json"
        
        return processed_headers
    
    def _process_body(self, input_data: Dict[str, Any]) -> Optional[Any]:
        """
        Process and substitute templates in request body.
        
        Args:
            input_data: Data for template substitution
            
        Returns:
            Processed body data
        """
        if "body" not in self.config:
            return None
        
        body = self.config["body"]
        
        if isinstance(body, str):
            # String body - substitute templates
            processed_body = self._substitute_templates(body, input_data)
            
            # Try to parse as JSON if it looks like JSON
            if processed_body.strip().startswith('{') or processed_body.strip().startswith('['):
                try:
                    return json.loads(processed_body)
                except json.JSONDecodeError:
                    return processed_body
            
            return processed_body
            
        elif isinstance(body, dict):
            # Dictionary body - recursively substitute templates
            return self._substitute_dict_templates(body, input_data)
        
        return body
    
    def _substitute_dict_templates(self, data: Dict[str, Any], input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Recursively substitute templates in dictionary values.
        
        Args:
            data: Dictionary to process
            input_data: Data for template substitution
            
        Returns:
            Dictionary with templates substituted
        """
        result = {}
        
        for key, value in data.items():
            processed_key = self._substitute_templates(key, input_data)
            
            if isinstance(value, str):
                processed_value = self._substitute_templates(value, input_data)
            elif isinstance(value, dict):
                processed_value = self._substitute_dict_templates(value, input_data)
            elif isinstance(value, list):
                processed_value = [
                    self._substitute_templates(item, input_data) if isinstance(item, str)
                    else self._substitute_dict_templates(item, input_data) if isinstance(item, dict)
                    else item
                    for item in value
                ]
            else:
                processed_value = value
            
            result[processed_key] = processed_value
        
        return result
    
    def _process_response(self, response: requests.Response) -> Dict[str, Any]:
        """
        Process HTTP response into structured data.
        
        Args:
            response: requests.Response object
            
        Returns:
            Dict containing response data
        """
        # Try to parse JSON response
        try:
            json_data = response.json()
        except (json.JSONDecodeError, ValueError):
            json_data = None
        
        return {
            "status_code": response.status_code,
            "headers": dict(response.headers),
            "text": response.text,
            "json": json_data,
            "ok": response.ok,
            "url": response.url
        }