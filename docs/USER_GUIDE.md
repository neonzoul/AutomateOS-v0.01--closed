# AutomateOS User Guide

Welcome to AutomateOS! This guide will help you get started with creating and managing automated workflows.

## Table of Contents

1. [Getting Started](#getting-started)
2. [Creating Your First Workflow](#creating-your-first-workflow)
3. [Understanding Workflow Nodes](#understanding-workflow-nodes)
4. [Managing Workflows](#managing-workflows)
5. [Monitoring Executions](#monitoring-executions)
6. [Troubleshooting](#troubleshooting)
7. [Best Practices](#best-practices)

## Getting Started

### Account Registration

1. Navigate to the AutomateOS application
2. Click "Register" to create a new account
3. Enter your email address and a secure password (minimum 8 characters)
4. Click "Create Account"

### Logging In

1. Enter your email and password on the login page
2. Click "Sign In"
3. You'll be redirected to your workflow dashboard

## Creating Your First Workflow

### Step 1: Access the Workflow Editor

1. From your dashboard, click "Create New Workflow"
2. Enter a name for your workflow (e.g., "Welcome Email Automation")
3. Optionally add a description
4. Click "Create Workflow"

### Step 2: Configure the Webhook Trigger

Every workflow starts with a webhook trigger that allows external services to initiate your automation.

1. The webhook trigger is automatically added to new workflows
2. Copy the webhook URL displayed - you'll use this to trigger the workflow
3. The webhook accepts any JSON payload via POST requests

### Step 3: Add Action Nodes

#### Adding an HTTP Request Node

1. Click "Add Node" and select "HTTP Request"
2. Configure the request:
   - **Method**: Choose GET, POST, PUT, or DELETE
   - **URL**: Enter the target API endpoint
   - **Headers**: Add any required headers (e.g., Authorization, Content-Type)
   - **Body**: For POST/PUT requests, enter the JSON payload

**Example Configuration:**
```json
{
  "method": "POST",
  "url": "https://api.sendgrid.com/v3/mail/send",
  "headers": {
    "Authorization": "Bearer YOUR_API_KEY",
    "Content-Type": "application/json"
  },
  "body": {
    "personalizations": [{"to": [{"email": "{{webhook.payload.email}}"}]}],
    "from": {"email": "noreply@yourapp.com"},
    "subject": "Welcome!",
    "content": [{"type": "text/plain", "value": "Welcome to our service!"}]
  }
}
```

#### Adding a Filter Node

Filter nodes allow you to add conditional logic to your workflows.

1. Click "Add Node" and select "Filter"
2. Configure the condition:
   - **Field**: The data field to evaluate (e.g., `webhook.payload.event_type`)
   - **Operator**: Choose from equals, not equals, contains, etc.
   - **Value**: The value to compare against

**Example:** Only proceed if the webhook payload contains `"event_type": "user_signup"`

### Step 4: Connect Your Nodes

1. Nodes are automatically connected in the order you add them
2. Data flows from the webhook trigger through each subsequent node
3. Each node can access data from previous nodes using template syntax: `{{node_id.field}}`

### Step 5: Save and Test

1. Click "Save Workflow" to store your configuration
2. Your workflow is now active and ready to receive webhook requests
3. Test by sending a POST request to your webhook URL

## Understanding Workflow Nodes

### Webhook Trigger Node

- **Purpose**: Receives HTTP requests from external services
- **Configuration**: Automatically configured with a unique URL
- **Data Output**: Provides the incoming request payload and metadata
- **Usage**: `{{webhook.payload.field_name}}` to access webhook data

### HTTP Request Node

- **Purpose**: Makes HTTP calls to external APIs
- **Supported Methods**: GET, POST, PUT, DELETE
- **Features**: 
  - Custom headers and authentication
  - JSON request bodies
  - Template variables for dynamic content
- **Data Output**: Response status, headers, and body
- **Usage**: `{{http_request_1.response.data}}` to access response data

### Filter Node

- **Purpose**: Conditional logic to control workflow execution
- **Operators**: 
  - `equals` / `not_equals`
  - `contains` / `not_contains`
  - `greater_than` / `less_than`
  - `exists` / `not_exists`
- **Behavior**: Stops workflow execution if condition is not met
- **Usage**: Essential for creating dynamic, intelligent workflows

## Managing Workflows

### Viewing Your Workflows

Your dashboard displays all your workflows with:
- Workflow name and description
- Active/inactive status
- Creation and last modified dates
- Quick action buttons

### Editing Workflows

1. Click the "Edit" button on any workflow card
2. Modify nodes, connections, or settings as needed
3. Click "Save Workflow" to apply changes
4. Changes take effect immediately for new executions

### Activating/Deactivating Workflows

- **Active workflows**: Can be triggered via webhook and will execute
- **Inactive workflows**: Webhook requests return an error, no execution occurs
- Toggle status using the switch on each workflow card

### Deleting Workflows

1. Click the "Delete" button on the workflow card
2. Confirm the deletion in the popup dialog
3. **Warning**: This permanently deletes the workflow and all execution logs

## Monitoring Executions

### Viewing Execution History

1. Click "View Logs" on any workflow card
2. See a chronological list of all executions
3. Each entry shows:
   - Execution timestamp
   - Status (Success, Failed, Running)
   - Duration
   - Error message (if failed)

### Detailed Execution Logs

1. Click on any execution entry to view details
2. See the complete execution trace:
   - Original webhook payload
   - Output from each node
   - Error details and stack traces
   - Timing information

### Execution Status Meanings

- **Success**: Workflow completed without errors
- **Failed**: An error occurred during execution
- **Running**: Workflow is currently executing (rare to see, as most workflows complete quickly)

## Troubleshooting

### Common Issues

#### Webhook Not Triggering

1. **Check the webhook URL**: Ensure you're using the correct URL from your workflow
2. **Verify HTTP method**: Webhooks only accept POST requests
3. **Check workflow status**: Ensure the workflow is active
4. **Review payload format**: Send valid JSON in the request body

#### HTTP Request Failures

1. **Verify the target URL**: Ensure the API endpoint is correct and accessible
2. **Check authentication**: Verify API keys and authentication headers
3. **Review request format**: Ensure headers and body match API requirements
4. **Check rate limits**: Some APIs have rate limiting that may cause failures

#### Filter Conditions Not Working

1. **Verify field paths**: Use the correct path to access nested data (e.g., `payload.user.email`)
2. **Check data types**: Ensure you're comparing compatible data types
3. **Review operator logic**: Make sure you're using the correct comparison operator

### Getting Help

1. **Execution Logs**: Always check the detailed execution logs for error messages
2. **API Documentation**: Review the `/docs` endpoint for complete API reference
3. **Test Incrementally**: Build workflows step by step, testing each node individually

## Best Practices

### Workflow Design

1. **Start Simple**: Begin with basic workflows and add complexity gradually
2. **Use Descriptive Names**: Give your workflows and nodes clear, descriptive names
3. **Add Documentation**: Use the description field to document workflow purpose and logic
4. **Test Thoroughly**: Test workflows with various input scenarios

### Security

1. **Protect API Keys**: Never expose API keys in webhook URLs or logs
2. **Use Environment Variables**: Store sensitive data securely, not in workflow definitions
3. **Validate Input**: Use filter nodes to validate incoming webhook data
4. **Monitor Access**: Regularly review execution logs for suspicious activity

### Performance

1. **Minimize HTTP Requests**: Combine API calls when possible to reduce latency
2. **Use Filters Early**: Place filter conditions early in workflows to avoid unnecessary processing
3. **Handle Errors Gracefully**: Design workflows to handle API failures appropriately
4. **Clean Up Logs**: Regularly clean up old execution logs to maintain performance

### Maintenance

1. **Regular Testing**: Periodically test your workflows to ensure they still work
2. **Update API Endpoints**: Keep track of changes to external APIs you integrate with
3. **Monitor Execution Rates**: Watch for unusual patterns in execution frequency
4. **Backup Important Workflows**: Export or document critical workflow configurations

## Advanced Features

### Template Variables

Use template syntax to access data from previous nodes:

```json
{
  "webhook_data": "{{webhook.payload.user_id}}",
  "api_response": "{{http_request_1.response.data.id}}",
  "combined": "User {{webhook.payload.name}} has ID {{api_response.user_id}}"
}
```

### Error Handling

- Failed nodes stop workflow execution
- Error details are logged for debugging
- Use filter nodes to handle expected error conditions
- Design workflows with fallback logic when possible

### Webhook Security

- Webhook URLs are unique and difficult to guess
- Consider implementing webhook signature verification for sensitive workflows
- Monitor execution logs for unauthorized access attempts

---

**Need more help?** Check the API documentation at `/docs` or review the execution logs for detailed error information.