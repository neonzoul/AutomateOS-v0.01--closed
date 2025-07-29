# AutomateOS Node Execution System

This document describes the node execution system implemented for AutomateOS workflow processing.

## Overview

The node execution system provides a modular, extensible framework for processing workflow steps. Each node type implements specific functionality (HTTP requests, filtering, etc.) while sharing common execution patterns and error handling.

## Architecture

### Core Components

1. **NodeBase** - Abstract base class for all nodes
2. **Node Implementations** - Specific node types (WebhookTrigger, HTTPRequest, Filter)
3. **WorkflowEngine** - Orchestrates node execution in workflows
4. **Node Registry** - Factory system for creating node instances

### Node Types

#### 1. WebhookTriggerNode
- **Purpose**: Entry point for webhook-triggered workflows
- **Configuration**: HTTP method validation
- **Execution**: Processes incoming request payload and metadata
- **Output**: Structured webhook data for subsequent nodes

```python
config = {
    "method": "POST"  # Required: HTTP method
}
```

#### 2. HTTPRequestNode
- **Purpose**: Makes HTTP calls to external APIs
- **Configuration**: URL, method, headers, body, timeout
- **Execution**: Template substitution, HTTP request, response processing
- **Output**: Request details and response data

```python
config = {
    "url": "https://api.example.com/data",
    "method": "POST",
    "headers": {"Content-Type": "application/json"},
    "body": {"data": "{{trigger.payload}}"},
    "timeout": 30
}
```

#### 3. FilterNode
- **Purpose**: Conditional logic for workflow flow control
- **Configuration**: Condition expression and continuation behavior
- **Execution**: Template substitution, condition evaluation
- **Output**: Filter result and continuation decision

```python
config = {
    "condition": "{{response.status_code}} == 200",
    "continue_on": True  # Continue if condition is True
}
```

## Template System

### Template Variables

Nodes support template variable substitution using `{{variable.path}}` syntax:

- `{{trigger.payload.field}}` - Access webhook payload data
- `{{node_id.output.field}}` - Access output from specific node
- `{{response.status_code}}` - Access HTTP response data
- `{{payload.field}}` - Direct access to payload fields

### Template Processing

Templates are processed recursively in:
- HTTP request URLs, headers, and body
- Filter condition expressions
- Any string configuration values

## Workflow Execution Flow

### 1. Workflow Initialization
```python
engine = WorkflowEngine()
result = engine.execute_workflow(workflow, trigger_payload)
```

### 2. Node Execution Sequence
1. Parse workflow definition (nodes and connections)
2. Execute nodes in definition order
3. Pass data between nodes via merged context
4. Handle errors and termination conditions

### 3. Data Flow
```
Trigger Payload → Node 1 → Merged Data → Node 2 → Final Result
```

Each node receives:
- Original trigger payload
- Outputs from all previous nodes
- Merged data context for template resolution

## Error Handling

### Node-Level Errors

**NodeExecutionError**: Raised for node-specific failures
- Configuration validation errors
- HTTP request failures
- Filter condition failures

```python
try:
    result = node.safe_execute(input_data)
except NodeExecutionError as e:
    print(f"Node {e.node_id} failed: {e.message}")
    print(f"Details: {e.details}")
```

### Workflow-Level Errors

**WorkflowExecutionError**: Raised for workflow failures
- Node execution failures
- Invalid workflow definitions
- System errors

### Error Recovery

- Individual node failures terminate the workflow
- Detailed error information is logged and stored
- Failed workflows can be retried or debugged

## Configuration Validation

### Automatic Validation

All nodes validate their configuration on initialization:

```python
class HTTPRequestNode(NodeBase):
    def validate_config(self):
        # Check required fields
        if "url" not in self.config:
            raise NodeExecutionError("Missing required field: url")
        
        # Validate URL format
        if not self._is_valid_url(self.config["url"]):
            raise NodeExecutionError("Invalid URL format")
```

### Workflow Validation

The WorkflowEngine provides workflow-level validation:

```python
engine = WorkflowEngine()
validation = engine.validate_workflow_definition(definition)

if not validation["valid"]:
    print("Validation errors:", validation["errors"])
```

## Execution Logging

### Node-Level Logging

Each node logs its execution:
- Input data received
- Processing steps
- Output data generated
- Errors encountered

### Workflow-Level Logging

The workflow engine logs:
- Workflow start/completion
- Node execution sequence
- Data flow between nodes
- Final results or errors

## Testing

### Unit Tests

Individual nodes can be tested in isolation:

```python
node = create_node("http_request", config)
node.node_id = "test-node"
result = node.safe_execute(test_data)
```

### Integration Tests

Complete workflows can be tested:

```python
engine = WorkflowEngine()
result = engine.execute_workflow(workflow, test_payload)
```

### Test Utilities

- `test_node_execution.py` - Individual node tests
- `test_workflow_direct.py` - Direct workflow execution tests
- `test_integration.py` - End-to-end integration tests

## Performance Considerations

### Template Processing

- Templates are processed on-demand during execution
- Complex nested templates may impact performance
- Consider caching for frequently used templates

### HTTP Requests

- Configurable timeouts prevent hanging requests
- Connection pooling handled by requests library
- Consider rate limiting for external APIs

### Memory Usage

- Node outputs are kept in memory during workflow execution
- Large payloads may impact memory usage
- Consider streaming for large data processing

## Extension Points

### Adding New Node Types

1. Create new node class inheriting from `NodeBase`
2. Implement `execute()` and `validate_config()` methods
3. Register in `NODE_REGISTRY`
4. Add tests and documentation

```python
class CustomNode(NodeBase):
    def validate_config(self):
        # Validate configuration
        pass
    
    def execute(self, input_data):
        # Implement node logic
        return {"result": "custom_output"}

# Register the node
NODE_REGISTRY["custom"] = CustomNode
```

### Custom Template Functions

Template processing can be extended with custom functions:

```python
def custom_template_function(value):
    return value.upper()

# Use in templates: {{custom_function(field)}}
```

## Security Considerations

### Template Injection

- Template variables are processed safely
- No arbitrary code execution in templates
- Input validation prevents malicious templates

### HTTP Requests

- URL validation prevents SSRF attacks
- Configurable timeouts prevent DoS
- Header validation prevents injection

### Filter Conditions

- Safe evaluation using restricted globals
- No access to system functions
- Fallback to simple string comparison

## Requirements Satisfied

This implementation satisfies the following requirements:

- **5.1**: WebhookTrigger node execution logic ✅
- **5.2**: HTTPRequestNode with configurable HTTP client ✅
- **5.3**: FilterNode with condition evaluation engine ✅
- **5.4**: Data passing between nodes in workflow chain ✅
- **5.5**: Error handling and workflow termination logic ✅
- **7.4**: Execution logging with detailed status tracking ✅
- **7.5**: Template system for dynamic data processing ✅

## Future Enhancements

1. **Parallel Execution**: Execute independent nodes concurrently
2. **Conditional Branching**: Support for if/else workflow paths
3. **Loop Support**: Iterate over arrays or repeat conditions
4. **Custom Functions**: User-defined template functions
5. **Node Versioning**: Support for multiple node versions
6. **Performance Metrics**: Detailed execution timing and statistics