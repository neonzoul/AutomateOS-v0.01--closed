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
    title="AutomateOS",
    description="API for automating operating system tasks",
    version="0.1.0",
    lifespan=lifespan
)

# Mount static files for production (React frontend)
if settings.is_production and os.path.exists("static"):
    app.mount("/static", StaticFiles(directory="static"), name="static")
    print("✓ Static files mounted for production")

# Import configuration
from .config import settings

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

@app.post("/register/", response_model=schemas.UserPublic)
def register_user(user: schemas.UserCreate, session: Session = Depends(get_session)):
    """
    Register a new user with email and password.
    
    - **email**: User's email address (must be unique)
    - **password**: User's password (will be securely hashed)
    
    Returns the newly created user's public information.
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

@app.post("/auth/token", response_model=schemas.Token)
def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(), 
    session: Session = Depends(get_session)
):
    """
    Authenticate user and return a JWT access token.
    
    - **username**: User's email address (OAuth2 standard uses 'username' field)
    - **password**: User's password
    
    Returns a JWT access token that can be used for authenticated requests.
    The token expires after the configured time period (default: 30 minutes).
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

@app.get("/")
def read_root():
    return {"message": "Welcome to AutomateOS API"}

@app.get("/health")
def health_check():
    """
    Health check endpoint for monitoring and load balancers.
    
    Returns basic system status and service availability.
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

@app.get("/workflows/", response_model=List[schemas.WorkflowPublic])
def read_user_workflows(
    session: Session = Depends(get_session),
    current_user: models.User = Depends(security.get_current_user)
):
    """
    Retrieve all workflows for the current authenticated user.
    
    Returns a list of workflows owned by the authenticated user.
    Requires valid JWT token in Authorization header.
    """
    return crud.get_workflows_by_owner(session=session, owner_id=current_user.id)

@app.post("/workflows/", response_model=schemas.WorkflowPublic)
def create_workflow(
    workflow: schemas.WorkflowCreate,
    session: Session = Depends(get_session),
    current_user: models.User = Depends(security.get_current_user)
):
    """
    Create a new workflow for the current authenticated user.
    
    - **name**: Workflow name
    - **description**: Optional workflow description  
    - **definition**: Workflow configuration as JSON
    - **is_active**: Whether the workflow is active (default: true)
    
    Returns the created workflow with generated webhook URL.
    """
    return crud.create_workflow(session=session, workflow=workflow, owner_id=current_user.id)

@app.get("/workflows/{workflow_id}", response_model=schemas.WorkflowPublic)
def read_workflow(
    workflow_id: int,
    session: Session = Depends(get_session),
    current_user: models.User = Depends(security.get_current_user)
):
    """
    Retrieve a specific workflow by ID.
    
    Returns the workflow if it exists and belongs to the authenticated user.
    """
    workflow = crud.get_workflow_by_id(session=session, workflow_id=workflow_id, owner_id=current_user.id)
    if not workflow:
        raise HTTPException(status_code=404, detail="Workflow not found")
    return workflow

@app.put("/workflows/{workflow_id}", response_model=schemas.WorkflowPublic)
def update_workflow(
    workflow_id: int,
    workflow_update: schemas.WorkflowCreate,
    session: Session = Depends(get_session),
    current_user: models.User = Depends(security.get_current_user)
):
    """
    Update an existing workflow.
    
    Updates the workflow if it exists and belongs to the authenticated user.
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

@app.delete("/workflows/{workflow_id}")
def delete_workflow(
    workflow_id: int,
    session: Session = Depends(get_session),
    current_user: models.User = Depends(security.get_current_user)
):
    """
    Delete a workflow by ID.
    
    Deletes the workflow if it exists and belongs to the authenticated user.
    """
    success = crud.delete_workflow(session=session, workflow_id=workflow_id, owner_id=current_user.id)
    if not success:
        raise HTTPException(status_code=404, detail="Workflow not found")
    return {"message": "Workflow deleted successfully"}

@app.post("/webhook/{webhook_id}")
async def trigger_workflow_webhook(
    webhook_id: str,
    request: Request,
    session: Session = Depends(get_session)
):
    """
    Webhook endpoint to trigger workflow execution.
    
    This endpoint receives HTTP requests from external services and enqueues
    the corresponding workflow for asynchronous execution.
    
    Args:
        webhook_id: Unique webhook identifier from the URL
        request: HTTP request containing the payload
        
    Returns:
        Dict with job ID and status information
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

@app.get("/jobs/{job_id}/status")
def get_job_status_endpoint(job_id: str):
    """
    Get the status of a queued workflow execution job.
    
    Args:
        job_id: ID of the job to check
        
    Returns:
        Dict containing job status and execution information
    """
    return get_job_status(job_id)

@app.get("/queue/info")
def get_queue_info_endpoint():
    """
    Get information about the workflow execution queue.
    
    Returns queue statistics including job counts and status.
    """
    return get_queue_info()

@app.get("/workflows/{workflow_id}/logs", response_model=List[schemas.ExecutionLogSummary])
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
    
    Args:
        workflow_id: ID of the workflow
        status: Optional status filter ("success", "failed", "running")
        limit: Maximum number of logs to return (default: 50, max: 100)
        offset: Number of logs to skip for pagination (default: 0)
        
    Returns:
        List of execution log summaries ordered by most recent first
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

@app.get("/logs/{log_id}", response_model=schemas.ExecutionLogPublic)
def get_execution_log_detail(
    log_id: int,
    session: Session = Depends(get_session),
    current_user: models.User = Depends(security.get_current_user)
):
    """
    Retrieve detailed information for a specific execution log.
    
    Args:
        log_id: ID of the execution log
        
    Returns:
        Complete execution log with payload, result, and error details
    """
    log = crud.get_execution_log_by_id(
        session=session,
        log_id=log_id,
        owner_id=current_user.id
    )
    
    if not log:
        raise HTTPException(status_code=404, detail="Execution log not found")
    
    return log

@app.get("/workflows/{workflow_id}/logs/count")
def get_workflow_logs_count(
    workflow_id: int,
    status: str = None,
    session: Session = Depends(get_session),
    current_user: models.User = Depends(security.get_current_user)
):
    """
    Get the total count of execution logs for a workflow.
    
    Args:
        workflow_id: ID of the workflow
        status: Optional status filter ("success", "failed", "running")
        
    Returns:
        Dict containing the total count of logs
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

@app.delete("/logs/cleanup")
def cleanup_old_logs(
    days_to_keep: int = 30,
    session: Session = Depends(get_session),
    current_user: models.User = Depends(security.get_current_user)
):
    """
    Clean up execution logs older than the specified number of days.
    
    This endpoint is available to all authenticated users but only affects
    logs from workflows they own (through the database relationships).
    
    Args:
        days_to_keep: Number of days to keep logs (default: 30, min: 1, max: 365)
        
    Returns:
        Dict containing the number of logs deleted
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