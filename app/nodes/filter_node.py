"""
Filter node implementation.

This module implements the filter node that applies conditional logic
to determine whether workflow execution should continue.
"""

import re
import json
from typing import Dict, Any, Union
from .base import NodeBase, NodeExecutionError

class FilterNode(NodeBase):
    """
    Filter node that applies conditional logic to workflow data.
    
    This node evaluates conditions and determines whether the workflow
    should continue execution or terminate based on the result.
    """
    
    def validate_config(self) -> None:
        """
        Validate filter node configuration.
        
        Raises:
            NodeExecutionError: If configuration is invalid
        """
        required_fields = ["condition"]
        
        for field in required_fields:
            if field not in self.config:
                raise NodeExecutionError(
                    message=f"Missing required field: {field}",
                    node_id=self.node_id,
                    node_type=self.node_type,
                    details={"missing_field": field}
                )
        
        # Validate condition format
        condition = self.config["condition"]
        if not isinstance(condition, str) or not condition.strip():
            raise NodeExecutionError(
                message="Condition must be a non-empty string",
                node_id=self.node_id,
                node_type=self.node_type,
                details={"invalid_condition": condition}
            )
    
    def execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute the filter node.
        
        Args:
            input_data: Data from previous nodes for condition evaluation
            
        Returns:
            Dict containing filter result and processed data
            
        Raises:
            NodeExecutionError: If condition evaluation fails or condition is not met
        """
        condition = self.config["condition"]
        continue_on_true = self.config.get("continue_on", True)
        
        try:
            # Substitute templates in condition
            processed_condition = self._substitute_templates(condition, input_data)
            
            # Evaluate the condition
            result = self._evaluate_condition(processed_condition, input_data)
            
            # Determine if workflow should continue
            should_continue = result if continue_on_true else not result
            
            filter_result = {
                "condition": condition,
                "processed_condition": processed_condition,
                "result": result,
                "continue_on": continue_on_true,
                "should_continue": should_continue,
                "input_data": input_data
            }
            
            if not should_continue:
                raise NodeExecutionError(
                    message=f"Filter condition not met: {processed_condition} = {result}",
                    node_id=self.node_id,
                    node_type=self.node_type,
                    details=filter_result
                )
            
            return filter_result
            
        except NodeExecutionError:
            # Re-raise filter-specific errors
            raise
            
        except Exception as e:
            raise NodeExecutionError(
                message=f"Error evaluating filter condition: {str(e)}",
                node_id=self.node_id,
                node_type=self.node_type,
                details={"condition": condition, "error": str(e)}
            )
    
    def _substitute_templates(self, template: str, data: Dict[str, Any]) -> str:
        """
        Substitute template variables in condition strings.
        
        Args:
            template: String with template variables
            data: Data dictionary for substitution
            
        Returns:
            str: String with variables substituted
        """
        if not isinstance(template, str):
            return str(template)
        
        # Find all template variables
        pattern = r'\{\{([^}]+)\}\}'
        matches = re.findall(pattern, template)
        
        result = template
        for match in matches:
            # Parse the variable path
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
                    # Convert value to string for condition evaluation
                    if isinstance(value, str):
                        # Quote string values for condition evaluation
                        str_value = f'"{value}"'
                    else:
                        str_value = str(value)
                    
                    result = result.replace(f"{{{{{match}}}}}", str_value)
                
            except (KeyError, TypeError):
                # If template variable can't be resolved, leave it as is
                pass
        
        return result
    
    def _evaluate_condition(self, condition: str, data: Dict[str, Any]) -> bool:
        """
        Evaluate a condition string and return boolean result.
        
        Supports basic comparison operators: ==, !=, <, >, <=, >=
        Supports logical operators: and, or, not
        Supports membership operators: in, not in
        
        Args:
            condition: Processed condition string
            data: Input data for context
            
        Returns:
            bool: Result of condition evaluation
        """
        # Simple condition evaluation using safe eval with restricted globals
        # This is a basic implementation - in production, consider using a proper expression parser
        
        # Define safe globals for evaluation
        safe_globals = {
            "__builtins__": {},
            "True": True,
            "False": False,
            "None": None,
            "len": len,
            "str": str,
            "int": int,
            "float": float,
            "bool": bool
        }
        
        # Define safe locals with common comparison functions
        safe_locals = {
            "data": data
        }
        
        try:
            # Basic safety check - only allow certain characters and operators
            allowed_chars = set("abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789 ._()[]{}\"'<>=!&|+-*/,%:")
            if not all(c in allowed_chars for c in condition):
                raise ValueError("Condition contains unsafe characters")
            
            # Replace common operators with Python equivalents
            condition = condition.replace(" and ", " and ")
            condition = condition.replace(" or ", " or ")
            condition = condition.replace(" not ", " not ")
            
            # Evaluate the condition
            result = eval(condition, safe_globals, safe_locals)
            
            # Ensure result is boolean
            return bool(result)
            
        except Exception as e:
            # If evaluation fails, try simple string comparisons
            return self._simple_condition_evaluation(condition, data)
    
    def _simple_condition_evaluation(self, condition: str, data: Dict[str, Any]) -> bool:
        """
        Fallback simple condition evaluation for basic comparisons.
        
        Args:
            condition: Condition string
            data: Input data
            
        Returns:
            bool: Result of simple condition evaluation
        """
        # Remove extra whitespace
        condition = condition.strip()
        
        # Handle simple equality checks
        if " == " in condition:
            left, right = condition.split(" == ", 1)
            return self._get_value(left.strip(), data) == self._get_value(right.strip(), data)
        
        elif " != " in condition:
            left, right = condition.split(" != ", 1)
            return self._get_value(left.strip(), data) != self._get_value(right.strip(), data)
        
        elif " > " in condition:
            left, right = condition.split(" > ", 1)
            return float(self._get_value(left.strip(), data)) > float(self._get_value(right.strip(), data))
        
        elif " < " in condition:
            left, right = condition.split(" < ", 1)
            return float(self._get_value(left.strip(), data)) < float(self._get_value(right.strip(), data))
        
        elif " >= " in condition:
            left, right = condition.split(" >= ", 1)
            return float(self._get_value(left.strip(), data)) >= float(self._get_value(right.strip(), data))
        
        elif " <= " in condition:
            left, right = condition.split(" <= ", 1)
            return float(self._get_value(left.strip(), data)) <= float(self._get_value(right.strip(), data))
        
        # If no operators found, treat as boolean value
        value = self._get_value(condition, data)
        return bool(value)
    
    def _get_value(self, expression: str, data: Dict[str, Any]) -> Any:
        """
        Extract value from expression or data.
        
        Args:
            expression: Value expression (literal or data path)
            data: Input data
            
        Returns:
            Any: Extracted value
        """
        expression = expression.strip()
        
        # Handle quoted strings
        if (expression.startswith('"') and expression.endswith('"')) or \
           (expression.startswith("'") and expression.endswith("'")):
            return expression[1:-1]
        
        # Handle numbers
        try:
            if '.' in expression:
                return float(expression)
            else:
                return int(expression)
        except ValueError:
            pass
        
        # Handle boolean values
        if expression.lower() == "true":
            return True
        elif expression.lower() == "false":
            return False
        elif expression.lower() == "none":
            return None
        
        # Handle data path (e.g., "response.status_code")
        if '.' in expression:
            path_parts = expression.split('.')
            value = data
            
            for part in path_parts:
                if isinstance(value, dict):
                    value = value.get(part)
                else:
                    return None
            
            return value
        
        # Handle simple key lookup
        return data.get(expression)
    
    def test_condition(self, test_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Test the filter condition with sample data.
        
        Args:
            test_data: Sample data to test condition against
            
        Returns:
            Dict containing test results
        """
        try:
            result = self.execute(test_data)
            return {
                "success": True,
                "result": result,
                "error": None
            }
        except NodeExecutionError as e:
            return {
                "success": False,
                "result": None,
                "error": {
                    "message": e.message,
                    "details": e.details
                }
            }