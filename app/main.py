# AutomateOS main application file
from contextlib import asynccontextmanager
from datetime import timedelta
from typing import List, Dict, Any
from fastapi import FastAPI, Depends, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.staticfiles import StaticFiles
from sqlmodel import Session, select
import os

from . import crud, schemas, security, models
from .database import create_db_and_tables, get_session
from .queue import enqueue_workflow_execution, get_job_status, get_queue_info
from .config import settings

@asynccontextmanager
# Use lifespan context manager for database initialization
async def lifespan(app: FastAPI):
    # Code to run on startup
    print("INFO:     Creating database and tables...")
    if settings.is_production:
        # Run full migrations in production
        from .migrations import run_migrations
        run_migrations()
    else:
        # Simple table creation in development
        create_db_and_tables()
    yield
    # Code to run on shutdown (if any)
    print("INFO:     Application shutdown.")

app = FastAPI(
    title="AutomateOS API",
    description="""
    **AutomateOS** is a workflow automation platform that enables users to create and manage automated workflows using a trigger-action model.

    ## Features

    * **User Authentication**: Secure JWT-based authentication system
    * **Workflow Management**: Create, read, update, and delete automation workflows
    * **Webhook Triggers**: External services can trigger workflows via HTTP webhooks
    * **Asynchronous Execution**: Background processing with Redis queue
    * **Execution Monitoring**: Comprehensive logging and status tracking

    ## Authentication

    Most endpoints require authentication using JWT tokens. To authenticate:

    1. Register a new account using `/register/`
    2. Login using `/auth/token` to get an access token
    3. Include the token in the Authorization header: `Bearer <your_token>`

    ## Workflow Structure

    Workflows are defined as JSON objects containing:
    - **nodes**: Array of workflow steps (webhook triggers, HTTP requests, filters)
    - **connections**: How nodes are linked together
    - **configuration**: Node-specific settings and parameters

    ## Rate Limits

    API endpoints are subject to reasonable rate limits to ensure system stability.
    """,
    version="1.0.0",
    lifespan=lifespan,
    contact={
        "name": "AutomateOS Support",
        "email": "support@automateos.dev",
    },
    license_info={
        "name": "MIT License",
        "url": "https://opensource.org/licenses/MIT",
    },
    servers=[
        {
            "url": "http://localhost:8000",
            "description": "Development server"
        },
        {
            "url": "https://your-production-domain.com",
            "description": "Production server"
        }
    ]
)

# Mount static files for production (React frontend)
if settings.is_production and os.path.exists("static"):
    app.mount("/static", StaticFiles(directory="static"), name="static")
    print("✓ Static files mounted for production")

# Configuration already imported above

# CORS Configuration
# Cross-Origin Resource Sharing (CORS) allows web applications running at one origin
# (domain, protocol, or port) to access resources from a different origin.
# This is essential for our architecture where the React frontend and FastAPI backend
# run on different ports during development.
origins = settings.allowed_origins

# Add the CORS middleware to the FastAPI application
# - allow_origins: List of allowed origins (frontend URLs)
# - allow_credentials: Allow cookies and authentication headers
# - allow_methods: Allow all HTTP methods (GET, POST, PUT, DELETE, etc.)
# - allow_headers: Allow all request headers
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/register/", 
          response_model=schemas.UserPublic,
          tags=["Authentication"],
          summary="Register a new user",
          description="Create a new user account with email and password. The password will be securely hashed before storage.")
def register_user(user: schemas.UserCreate, session: Session = Depends(get_session)):
    """
    Register a new user account.
    
    **Parameters:**
    - **email**: User's email address (must be unique and valid)
    - **password**: User's password (minimum 8 characters, will be securely hashed)
    
    **Returns:**
    - User's public information (ID, email, creation timestamp)
    
    **Errors:**
    - **400**: Email already registered
    - **422**: Invalid email format or password too short
    """
    # Check if user already exists
    db_user = crud.get_user_by_email(session=session, email=user.email)
    if db_user:
        raise HTTPException(
            status_code=400, 
            detail="Email already registered"
        )
    
    # Create new user
    new_user = crud.create_user(session=session, user=user)
    return new_user

@app.post("/auth/token", 
          response_model=schemas.Token,
          tags=["Authentication"],
          summary="Login and get access token",
          description="Authenticate with email and password to receive a JWT access token for API access.")
def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(), 
    session: Session = Depends(get_session)
):
    """
    Authenticate user and return a JWT access token.
    
    **Parameters:**
    - **username**: User's email address (OAuth2 standard uses 'username' field)
    - **password**: User's password
    
    **Returns:**
    - **access_token**: JWT token for authenticated requests
    - **token_type**: Always "bearer"
    
    **Token Usage:**
    Include the token in the Authorization header: `Bearer <access_token>`
    
    **Token Expiration:**
    Tokens expire after 30 minutes. You'll need to login again to get a new token.
    
    **Errors:**
    - **401**: Invalid email or password
    """
    # Authenticate user using email (username field) and password
    user = crud.authenticate_user(
        session=session, 
        user_credentials=schemas.UserCreate(
            email=form_data.username, 
            password=form_data.password
        )
    )
    
    if not user:
        raise HTTPException(
            status_code=401,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Create access token with user's email as subject
    access_token_expires = timedelta(minutes=security.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = security.create_access_token(
        data={"sub": user.email}, 
        expires_delta=access_token_expires
    )
    
    return {"access_token": access_token, "token_type": "bearer"}

@app.get("/", 
         tags=["System"],
         summary="API root endpoint",
         description="Welcome message and basic API information.")
def read_root():
    """
    API root endpoint providing welcome message and basic information.
    
    **Returns:**
    - Welcome message and API version information
    """
    return {
        "message": "Welcome to AutomateOS API",
        "version": "1.0.0",
        "documentation": "/docs",
        "status": "operational"
    }

@app.get("/health",
         tags=["System"],
         summary="System health check",
         description="Check the health status of the API and its dependencies (database, Redis).")
def health_check():
    """
    System health check endpoint for monitoring and load balancers.
    
    **Returns:**
    - **status**: Overall system status (healthy/degraded)
    - **version**: API version
    - **environment**: Current environment (development/production)
    - **services**: Status of individual services (database, Redis)
    
    **Status Values:**
    - **healthy**: All services are operational
    - **degraded**: One or more services are experiencing issues
    """
    try:
        # Test database connection
        with next(get_session()) as session:
            session.exec(select(models.User).limit(1))
        db_status = "healthy"
    except Exception as e:
        db_status = f"unhealthy: {str(e)}"
    
    try:
        # Test Redis connection
        from .queue import get_redis_connection
        redis_conn = get_redis_connection()
        redis_conn.ping()
        redis_status = "healthy"
    except Exception as e:
        redis_status = f"unhealthy: {str(e)}"
    
    return {
        "status": "healthy" if db_status == "healthy" and redis_status == "healthy" else "degraded",
        "version": "0.1.0",
        "environment": settings.environment,
        "services": {
            "database": db_status,
            "redis": redis_status
        }
    }

@app.get("/workflows/", 
         response_model=List[schemas.WorkflowPublic],
         tags=["Workflows"],
         summary="List user workflows",
         description="Retrieve all workflows owned by the authenticated user.")
def read_user_workflows(
    session: Session = Depends(get_session),
    current_user: models.User = Depends(security.get_current_user)
):
    """
    Retrieve all workflows for the current authenticated user.
    
    **Authentication Required:** Yes (JWT token)
    
    **Returns:**
    - List of workflow objects with basic information
    - Each workflow includes: ID, name, description, webhook URL, active status
    
    **Empty Response:**
    Returns empty array `[]` if user has no workflows
    """
    return crud.get_workflows_by_owner(session=session, owner_id=current_user.id)

@app.post("/workflows/", 
          response_model=schemas.WorkflowPublic,
          tags=["Workflows"],
          summary="Create new workflow",
          description="Create a new automation workflow with nodes and connections.")
def create_workflow(
    workflow: schemas.WorkflowCreate,
    session: Session = Depends(get_session),
    current_user: models.User = Depends(security.get_current_user)
):
    """
    Create a new workflow for the current authenticated user.
    
    **Authentication Required:** Yes (JWT token)
    
    **Parameters:**
    - **name**: Workflow name (required, max 255 characters)
    - **description**: Optional workflow description
    - **definition**: Workflow configuration as JSON object containing nodes and connections
    - **is_active**: Whether the workflow is active and can be triggered (default: true)
    
    **Returns:**
    - Created workflow object with auto-generated webhook URL
    - Unique webhook URL can be used to trigger the workflow externally
    
    **Example Definition:**
    ```json
    {
      "nodes": [
        {"id": "trigger-1", "type": "webhook", "config": {}},
        {"id": "action-1", "type": "http_request", "config": {"url": "https://api.example.com"}}
      ],
      "connections": [{"from": "trigger-1", "to": "action-1"}]
    }
    ```
    """
    return crud.create_workflow(session=session, workflow=workflow, owner_id=current_user.id)

@app.get("/workflows/{workflow_id}", 
         response_model=schemas.WorkflowPublic,
         tags=["Workflows"],
         summary="Get workflow by ID",
         description="Retrieve detailed information for a specific workflow.")
def read_workflow(
    workflow_id: int,
    session: Session = Depends(get_session),
    current_user: models.User = Depends(security.get_current_user)
):
    """
    Retrieve a specific workflow by ID.
    
    **Authentication Required:** Yes (JWT token)
    
    **Returns:**
    - Complete workflow information including definition, webhook URL, and metadata
    
    **Errors:**
    - **404**: Workflow not found or not owned by user
    """
    workflow = crud.get_workflow_by_id(session=session, workflow_id=workflow_id, owner_id=current_user.id)
    if not workflow:
        raise HTTPException(status_code=404, detail="Workflow not found")
    return workflow

@app.put("/workflows/{workflow_id}", 
         response_model=schemas.WorkflowPublic,
         tags=["Workflows"],
         summary="Update workflow",
         description="Update an existing workflow's configuration, name, or status.")
def update_workflow(
    workflow_id: int,
    workflow_update: schemas.WorkflowCreate,
    session: Session = Depends(get_session),
    current_user: models.User = Depends(security.get_current_user)
):
    """
    Update an existing workflow.
    
    **Authentication Required:** Yes (JWT token)
    
    **Parameters:**
    - **workflow_id**: ID of workflow to update
    - **workflow_update**: Updated workflow data (same format as create)
    
    **Returns:**
    - Updated workflow object with new configuration
    
    **Errors:**
    - **404**: Workflow not found or not owned by user
    """
    workflow = crud.update_workflow(
        session=session, 
        workflow_id=workflow_id, 
        workflow_update=workflow_update, 
        owner_id=current_user.id
    )
    if not workflow:
        raise HTTPException(status_code=404, detail="Workflow not found")
    return workflow

@app.delete("/workflows/{workflow_id}",
           tags=["Workflows"],
           summary="Delete workflow",
           description="Permanently delete a workflow and all its execution logs.")
def delete_workflow(
    workflow_id: int,
    session: Session = Depends(get_session),
    current_user: models.User = Depends(security.get_current_user)
):
    """
    Delete a workflow by ID.
    
    **Authentication Required:** Yes (JWT token)
    
    **Warning:** This action is permanent and will also delete all execution logs for this workflow.
    
    **Parameters:**
    - **workflow_id**: ID of workflow to delete
    
    **Returns:**
    - Confirmation message
    
    **Errors:**
    - **404**: Workflow not found or not owned by user
    """
    success = crud.delete_workflow(session=session, workflow_id=workflow_id, owner_id=current_user.id)
    if not success:
        raise HTTPException(status_code=404, detail="Workflow not found")
    return {"message": "Workflow deleted successfully"}

@app.post("/webhook/{webhook_id}",
          tags=["Webhooks"],
          summary="Trigger workflow via webhook",
          description="External endpoint to trigger workflow execution. Accepts any JSON payload and processes asynchronously.")
async def trigger_workflow_webhook(
    webhook_id: str,
    request: Request,
    session: Session = Depends(get_session)
):
    """
    Webhook endpoint to trigger workflow execution.
    
    **Authentication Required:** No (public webhook endpoint)
    
    **Parameters:**
    - **webhook_id**: Unique webhook identifier from the URL path
    - **request body**: Any JSON payload (optional)
    
    **Processing:**
    - Request is immediately accepted and queued for background processing
    - Workflow executes asynchronously without blocking the response
    - Request metadata (headers, timestamp, etc.) is automatically added to payload
    
    **Returns:**
    - **message**: Confirmation message
    - **job_id**: Unique identifier for tracking execution status
    - **workflow_id**: ID of the triggered workflow
    - **status**: Always "accepted" for successful requests
    
    **Errors:**
    - **404**: Webhook ID not found or workflow doesn't exist
    - **400**: Workflow is not active
    
    **Usage Example:**
    ```bash
    curl -X POST https://your-domain.com/webhook/abc123 \\
         -H "Content-Type: application/json" \\
         -d '{"event": "user_signup", "user_id": 12345}'
    ```
    """
    # Get request payload
    try:
        payload = await request.json()
    except:
        payload = {}
    
    # Add request metadata to payload
    from datetime import datetime
    payload.update({
        "method": request.method,
        "headers": dict(request.headers),
        "url": str(request.url),
        "timestamp": datetime.utcnow().isoformat()
    })
    
    # Find workflow by webhook URL
    workflow = crud.get_workflow_by_webhook_id(session=session, webhook_id=webhook_id)
    if not workflow:
        raise HTTPException(status_code=404, detail="Webhook not found")
    
    if not workflow.is_active:
        raise HTTPException(status_code=400, detail="Workflow is not active")
    
    # Enqueue workflow execution
    job_id = enqueue_workflow_execution(workflow.id, payload)
    
    return {
        "message": "Workflow execution enqueued",
        "job_id": job_id,
        "workflow_id": workflow.id,
        "status": "accepted"
    }

@app.get("/jobs/{job_id}/status",
         tags=["Job Status"],
         summary="Get job execution status",
         description="Check the current status of a workflow execution job.")
def get_job_status_endpoint(job_id: str):
    """
    Get the status of a queued workflow execution job.
    
    **Authentication Required:** No
    
    **Parameters:**
    - **job_id**: Unique job identifier returned from webhook trigger
    
    **Returns:**
    - **status**: Job status (queued, running, completed, failed)
    - **result**: Execution result (if completed)
    - **error**: Error details (if failed)
    
    **Job Status Values:**
    - **queued**: Job is waiting to be processed
    - **running**: Job is currently executing
    - **completed**: Job finished successfully
    - **failed**: Job encountered an error
    """
    return get_job_status(job_id)

@app.get("/queue/info",
         tags=["System"],
         summary="Get queue information",
         description="Retrieve statistics about the workflow execution queue.")
def get_queue_info_endpoint():
    """
    Get information about the workflow execution queue.
    
    **Authentication Required:** No
    
    **Returns:**
    - Queue statistics including job counts by status
    - Worker information and queue health
    
    **Useful for:**
    - Monitoring system load
    - Debugging execution delays
    - System health checks
    """
    return get_queue_info()

@app.get("/workflows/{workflow_id}/logs", 
         response_model=List[schemas.ExecutionLogSummary],
         tags=["Execution Logs"],
         summary="Get workflow execution logs",
         description="Retrieve execution history for a specific workflow with optional filtering and pagination.")
def get_workflow_execution_logs(
    workflow_id: int,
    status: str = None,
    limit: int = 50,
    offset: int = 0,
    session: Session = Depends(get_session),
    current_user: models.User = Depends(security.get_current_user)
):
    """
    Retrieve execution logs for a specific workflow.
    
    **Authentication Required:** Yes (JWT token)
    
    **Parameters:**
    - **workflow_id**: ID of the workflow (must be owned by authenticated user)
    - **status**: Optional status filter - "success", "failed", or "running"
    - **limit**: Maximum logs to return (default: 50, max: 100)
    - **offset**: Number of logs to skip for pagination (default: 0)
    
    **Returns:**
    - List of execution log summaries ordered by most recent first
    - Each log includes: ID, status, start/completion times, error message (if any)
    
    **Pagination:**
    Use `limit` and `offset` parameters for pagination:
    - Page 1: `offset=0&limit=50`
    - Page 2: `offset=50&limit=50`
    
    **Errors:**
    - **400**: Invalid status filter
    - **404**: Workflow not found or not owned by user
    """
    # Validate parameters
    if limit > 100:
        limit = 100
    if limit < 1:
        limit = 1
    if offset < 0:
        offset = 0
    
    # Validate status filter
    valid_statuses = ["success", "failed", "running"]
    if status and status not in valid_statuses:
        raise HTTPException(
            status_code=400, 
            detail=f"Invalid status filter. Must be one of: {', '.join(valid_statuses)}"
        )
    
    # Get execution logs
    logs = crud.get_execution_logs_by_workflow(
        session=session,
        workflow_id=workflow_id,
        owner_id=current_user.id,
        status_filter=status,
        limit=limit,
        offset=offset
    )
    
    # Convert to summary format
    return [
        schemas.ExecutionLogSummary(
            id=log.id,
            workflow_id=log.workflow_id,
            status=log.status,
            started_at=log.started_at,
            completed_at=log.completed_at,
            error_message=log.error_message
        )
        for log in logs
    ]

@app.get("/logs/{log_id}", 
         response_model=schemas.ExecutionLogPublic,
         tags=["Execution Logs"],
         summary="Get detailed execution log",
         description="Retrieve complete details for a specific workflow execution including payload and results.")
def get_execution_log_detail(
    log_id: int,
    session: Session = Depends(get_session),
    current_user: models.User = Depends(security.get_current_user)
):
    """
    Retrieve detailed information for a specific execution log.
    
    **Authentication Required:** Yes (JWT token)
    
    **Parameters:**
    - **log_id**: ID of the execution log
    
    **Returns:**
    - Complete execution log including:
      - Original webhook payload
      - Execution results from each node
      - Error details and stack traces (if failed)
      - Timing information
    
    **Errors:**
    - **404**: Log not found or not owned by user
    """
    log = crud.get_execution_log_by_id(
        session=session,
        log_id=log_id,
        owner_id=current_user.id
    )
    
    if not log:
        raise HTTPException(status_code=404, detail="Execution log not found")
    
    return log

@app.get("/workflows/{workflow_id}/logs/count",
         tags=["Execution Logs"],
         summary="Get workflow logs count",
         description="Get the total number of execution logs for a workflow, optionally filtered by status.")
def get_workflow_logs_count(
    workflow_id: int,
    status: str = None,
    session: Session = Depends(get_session),
    current_user: models.User = Depends(security.get_current_user)
):
    """
    Get the total count of execution logs for a workflow.
    
    **Authentication Required:** Yes (JWT token)
    
    **Parameters:**
    - **workflow_id**: ID of the workflow
    - **status**: Optional status filter ("success", "failed", "running")
    
    **Returns:**
    - **count**: Total number of matching logs
    
    **Useful for:**
    - Pagination calculations
    - Workflow usage statistics
    - Performance monitoring
    """
    # Validate status filter
    valid_statuses = ["success", "failed", "running"]
    if status and status not in valid_statuses:
        raise HTTPException(
            status_code=400, 
            detail=f"Invalid status filter. Must be one of: {', '.join(valid_statuses)}"
        )
    
    count = crud.get_execution_logs_count_by_workflow(
        session=session,
        workflow_id=workflow_id,
        owner_id=current_user.id,
        status_filter=status
    )
    
    return {"count": count}

@app.delete("/logs/cleanup",
           tags=["Execution Logs"],
           summary="Clean up old logs",
           description="Delete execution logs older than the specified number of days to free up storage space.")
def cleanup_old_logs(
    days_to_keep: int = 30,
    session: Session = Depends(get_session),
    current_user: models.User = Depends(security.get_current_user)
):
    """
    Clean up execution logs older than the specified number of days.
    
    **Authentication Required:** Yes (JWT token)
    
    **Security:** Only affects logs from workflows owned by the authenticated user.
    
    **Parameters:**
    - **days_to_keep**: Number of days to retain logs (default: 30, min: 1, max: 365)
    
    **Returns:**
    - **deleted_count**: Number of logs that were deleted
    
    **Use Cases:**
    - Regular maintenance to prevent database bloat
    - Compliance with data retention policies
    - Storage cost optimization
    
    **Warning:** This action is permanent and cannot be undone.
    """
    # Validate days_to_keep parameter
    if days_to_keep < 1:
        days_to_keep = 1
    elif days_to_keep > 365:
        days_to_keep = 365
    
    # For security, we'll only clean up logs for workflows owned by the current user
    # First get all workflow IDs owned by the user
    user_workflows = crud.get_workflows_by_owner(session=session, owner_id=current_user.id)
    workflow_ids = [w.id for w in user_workflows]
    
    if not workflow_ids:
        return {"deleted_count": 0}
    
    # Clean up logs for user's workflows only
    from datetime import datetime, timedelta
    cutoff_date = datetime.utcnow() - timedelta(days=days_to_keep)
    
    logs_to_delete = session.exec(
        select(models.ExecutionLog).where(
            models.ExecutionLog.workflow_id.in_(workflow_ids),
            models.ExecutionLog.started_at < cutoff_date
        )
    ).all()
    
    # Delete the logs
    for log in logs_to_delete:
        session.delete(log)
    
    session.commit()
    
    return {"deleted_count": len(logs_to_delete)}

# Serve React app for all non-API routes (production only)
if settings.is_production and os.path.exists("static/index.html"):
    from fastapi.responses import FileResponse
    
    @app.get("/{full_path:path}")
    async def serve_react_app(full_path: str):
        """
        Serve the React app for all routes that don't match API endpoints.
        This enables client-side routing to work properly in production.
        """
        # Don't serve React app for API routes
        if full_path.startswith("api/") or full_path.startswith("docs") or full_path.startswith("redoc"):
            raise HTTPException(status_code=404, detail="Not found")
        
        # Serve index.html for all other routes
        return FileResponse("static/index.html")