# AutomateOS Manual Testing Guide

This guide covers comprehensive manual testing of the AutomateOS system including the new node execution capabilities.

## 🚀 Setup Instructions

### Prerequisites
- Python 3.8+
- Redis server
- Node.js (for frontend testing)

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Start Redis Server
```bash
# Windows (if installed via installer)
redis-server

# Or if using WSL/Linux
sudo service redis-server start
```

### 3. Start the Backend Server
```bash
python start_server.py
```
Server will be available at: **http://localhost:8000**

### 4. Start the Background Worker
```bash
# In a separate terminal
python start_worker.py
```

### 5. Start Frontend (Optional)
```bash
cd frontend
npm install
npm run dev
```
Frontend will be available at: **http://localhost:5173**

## 📚 API Documentation

Visit: **http://localhost:8000/docs** for interactive Swagger UI

## ✅ Manual Testing Scenarios

### Scenario 1: Basic Authentication & Workflow Management

#### Step 1: Register a User
**Endpoint**: `POST /register/`
```json
{
  "email": "test@example.com",
  "password": "testpassword123"
}
```
**Expected**: 200 OK with user details

#### Step 2: Login and Get Token
**Endpoint**: `POST /auth/token`
- **username**: `test@example.com`
- **password**: `testpassword123`

**Expected**: 200 OK with access token
**Action**: Copy the `access_token` for authorization

#### Step 3: Authorize in Swagger
1. Click "Authorize" button
2. Enter: `Bearer YOUR_ACCESS_TOKEN`
3. Click "Authorize"

#### Step 4: Create a Simple Workflow
**Endpoint**: `POST /workflows/`
```json
{
  "name": "Test Webhook Workflow",
  "description": "Simple webhook test",
  "definition": {
    "nodes": [
      {
        "id": "webhook-trigger",
        "type": "webhook",
        "config": {
          "method": "POST"
        }
      }
    ]
  },
  "is_active": true
}
```
**Expected**: 200 OK with workflow details including `webhook_url`
**Action**: Copy the `webhook_url` for testing

### Scenario 2: Advanced Workflow with HTTP Request and Filter

#### Step 1: Create Advanced Workflow
**Endpoint**: `POST /workflows/`
```json
{
  "name": "HTTP Request with Filter",
  "description": "Workflow that makes HTTP request and filters response",
  "definition": {
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
            "X-Test": "AutomateOS-Manual-Test"
          },
          "body": {
            "original_payload": "{{trigger.payload}}",
            "timestamp": "{{trigger.timestamp}}",
            "test_data": {
              "workflow_name": "HTTP Request with Filter",
              "manual_test": true
            }
          }
        }
      },
      {
        "id": "success-filter",
        "type": "filter",
        "config": {
          "condition": "{{response.status_code}} == 200",
          "continue_on": true
        }
      }
    ],
    "connections": [
      {"from": "webhook-trigger", "to": "api-call"},
      {"from": "api-call", "to": "success-filter"}
    ]
  },
  "is_active": true
}
```
**Expected**: 200 OK with workflow details
**Action**: Copy the `webhook_url`

### Scenario 3: Webhook Execution Testing

#### Step 1: Trigger Simple Webhook
**Method**: POST to the webhook URL from Step 1
**URL**: `http://localhost:8000/webhook/{webhook_id}`
**Body**:
```json
{
  "test": true,
  "message": "Manual webhook test",
  "user": {
    "id": 123,
    "name": "Test User"
  }
}
```
**Expected**: 202 Accepted with job information

#### Step 2: Check Job Status
**Endpoint**: `GET /jobs/{job_id}/status`
**Expected**: Job status information (queued → finished)

#### Step 3: Trigger Advanced Webhook
**Method**: POST to the webhook URL from Step 2
**URL**: `http://localhost:8000/webhook/{webhook_id}`
**Body**:
```json
{
  "event": "manual_test",
  "data": {
    "action": "test_advanced_workflow",
    "priority": "high"
  },
  "metadata": {
    "source": "manual_testing",
    "version": "1.0"
  }
}
```
**Expected**: 202 Accepted with job information

### Scenario 4: Queue and Execution Monitoring

#### Step 1: Check Queue Information
**Endpoint**: `GET /queue/info`
**Expected**: Queue statistics (length, job counts)

#### Step 2: Monitor Job Execution
**Endpoint**: `GET /jobs/{job_id}/status`
**Expected**: Detailed job status with execution results

### Scenario 5: Error Handling Testing

#### Step 1: Create Workflow with Invalid HTTP Request
```json
{
  "name": "Error Test Workflow",
  "description": "Test error handling",
  "definition": {
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
  },
  "is_active": true
}
```

#### Step 2: Trigger Error Workflow
**Method**: POST to webhook URL
**Body**: `{"test": "error_handling"}`
**Expected**: 202 Accepted, but job should fail

#### Step 3: Check Failed Job Status
**Endpoint**: `GET /jobs/{job_id}/status`
**Expected**: Job status "failed" with error details

### Scenario 6: Filter Condition Testing

#### Step 1: Create Filter Test Workflow
```json
{
  "name": "Filter Condition Test",
  "description": "Test different filter conditions",
  "definition": {
    "nodes": [
      {
        "id": "webhook-trigger",
        "type": "webhook",
        "config": {"method": "POST"}
      },
      {
        "id": "number-filter",
        "type": "filter",
        "config": {
          "condition": "{{score}} > 50",
          "continue_on": true
        }
      }
    ]
  },
  "is_active": true
}
```

#### Step 2: Test Passing Condition
**Body**: `{"score": 75}`
**Expected**: Workflow completes successfully

#### Step 3: Test Failing Condition
**Body**: `{"score": 25}`
**Expected**: Workflow fails at filter node

## 🧪 Frontend Testing (If Available)

### 1. Access Dashboard
**URL**: `http://localhost:5173`
**Expected**: Login page or dashboard

### 2. Test Authentication
- Register new user
- Login with credentials
- Access protected pages

### 3. Test Workflow Management
- View workflow list
- Create new workflow
- Edit existing workflow
- Delete workflow

### 4. Test Workflow Editor
- Add nodes to workflow
- Configure node settings
- Save workflow configuration

## 🔧 Troubleshooting

### Common Issues

1. **Redis Connection Error**
   - Ensure Redis server is running
   - Check Redis URL in environment variables

2. **Worker Not Processing Jobs**
   - Verify worker is running (`python start_worker.py`)
   - Check Redis connection
   - Look for worker logs

3. **Webhook 404 Errors**
   - Verify webhook URL format: `/webhook/{uuid}`
   - Check workflow is active
   - Ensure workflow exists in database

4. **Template Substitution Issues**
   - Verify template syntax: `{{variable.path}}`
   - Check data availability in workflow context
   - Review node execution logs

### Debug Commands

```bash
# Test queue infrastructure
python test_queue.py

# Test node execution
python test_node_execution.py

# Test direct workflow execution
python test_workflow_direct.py

# Test webhook setup
python test_webhook.py
```

## 📊 Success Criteria

### ✅ Basic Functionality
- [ ] User registration and authentication
- [ ] Workflow CRUD operations
- [ ] Webhook URL generation
- [ ] API documentation accessible

### ✅ Advanced Functionality
- [ ] Webhook triggers execute workflows
- [ ] HTTP requests work with template substitution
- [ ] Filter conditions evaluate correctly
- [ ] Background job processing
- [ ] Error handling and logging

### ✅ System Integration
- [ ] Queue system processes jobs
- [ ] Database stores execution logs
- [ ] Real-time job status tracking
- [ ] Frontend integrates with backend (if available)

## 📝 Test Data Templates

### Simple Webhook Payload
```json
{
  "test": true,
  "message": "Hello AutomateOS",
  "timestamp": "2025-01-26T12:00:00Z"
}
```

### Complex Webhook Payload
```json
{
  "event": "user_signup",
  "user": {
    "id": 12345,
    "email": "user@example.com",
    "name": "John Doe"
  },
  "metadata": {
    "source": "web_app",
    "ip": "192.168.1.1",
    "user_agent": "Mozilla/5.0..."
  },
  "data": {
    "plan": "premium",
    "trial_days": 14
  }
}
```

### Filter Test Payloads
```json
// Should pass (score > 50)
{"score": 85, "status": "active"}

// Should fail (score <= 50)
{"score": 30, "status": "inactive"}

// String comparison
{"status": "success", "code": 200}
```

This guide provides comprehensive manual testing coverage for all implemented features. The system is fully testable and ready for production validation!