# Manual Verification Guide - Task 3.1

## 🚀 Starting the Server

Run this command to start the server:
```bash
python start_server.py
```

Or directly:
```bash
python -m uvicorn app.main:app --host 127.0.0.1 --port 8002 --reload
```

The server will be available at: **http://127.0.0.1:8002**

## 📚 API Documentation

Visit: **http://127.0.0.1:8002/docs**

This will open the interactive Swagger UI where you can test all endpoints.

## ✅ Verification Checklist

### Step 1: Register a Test User

1. In the API docs, find the `POST /register/` endpoint
2. Click "Try it out"
3. Use this JSON body:
```json
{
  "email": "test@example.com",
  "password": "testpassword123"
}
```
4. Click "Execute"
5. **Expected Result**: 200 OK with user details

### Step 2: Get Authentication Token

1. Find the `POST /auth/token` endpoint
2. Click "Try it out"
3. Enter:
   - **username**: `test@example.com`
   - **password**: `testpassword123`
4. Click "Execute"
5. **Expected Result**: 200 OK with access token
6. **Copy the access_token value** for next steps

### Step 3: Authorize in Swagger UI

1. Click the **"Authorize"** button at the top of the page
2. Enter: `Bearer YOUR_ACCESS_TOKEN_HERE`
3. Click "Authorize"
4. You should now see a lock icon next to protected endpoints

### Step 4: Test Workflow Creation ✅

1. Find the `POST /workflows/` endpoint
2. Click "Try it out"
3. Use this JSON body:
```json
{
  "name": "My Test Workflow",
  "description": "A test.",
  "definition": { "nodes": [] }
}
```
4. Click "Execute"
5. **Expected Result**: 200 OK with:
   - Workflow `id`
   - Unique `webhook_url`
   - All provided fields returned

### Step 5: Test Workflow Listing ✅

1. Find the `GET /workflows/` endpoint
2. Click "Try it out"
3. Click "Execute"
4. **Expected Result**: 200 OK with array containing your workflow

### Step 6: Test Route Protection ✅

1. Click the **"Authorize"** button again
2. Click **"Logout"** to clear your token
3. Try the `GET /workflows/` endpoint again
4. **Expected Result**: 401 Unauthorized
5. Try the `POST /workflows/` endpoint
6. **Expected Result**: 401 Unauthorized

## 🎯 Success Criteria

All of the following should work:

- ✅ **Successful Workflow Creation**: POST returns 200 with id and webhook_url
- ✅ **Correct Workflow Listing**: GET returns 200 with user's workflows
- ✅ **Route Protection**: Unauthorized requests return 401

## 🔧 Troubleshooting

If you encounter issues:

1. **Port already in use**: Try a different port (8003, 8004, etc.)
2. **Database errors**: Delete `database.db` file and restart
3. **Token issues**: Make sure to include "Bearer " prefix in authorization

## 📝 Test Data Templates

### User Registration:
```json
{
  "email": "test@example.com",
  "password": "testpassword123"
}
```

### Workflow Creation:
```json
{
  "name": "My Test Workflow",
  "description": "A test.",
  "definition": { "nodes": [] }
}
```

### More Complex Workflow:
```json
{
  "name": "Advanced Test Workflow",
  "description": "A more complex test workflow",
  "definition": {
    "nodes": [
      {
        "id": "trigger-1",
        "type": "webhook",
        "config": {"method": "POST"}
      },
      {
        "id": "action-1", 
        "type": "http_request",
        "config": {
          "url": "https://httpbin.org/post",
          "method": "POST"
        }
      }
    ],
    "connections": [{"from": "trigger-1", "to": "action-1"}]
  },
  "is_active": true
}
```