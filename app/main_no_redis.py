# AutomateOS main application file (No Redis version)
import os
from contextlib import asynccontextmanager
from datetime import timedelta
from typing import List, Dict, Any
from fastapi import FastAPI, Depends, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordRequestForm
from sqlmodel import Session, select

from . import crud, schemas, security, models
from .database import create_db_and_tables, get_session

# Check if we should use mock queue
USE_MOCK_QUEUE = os.getenv("USE_MOCK_QUEUE", "true").lower() == "true"

if USE_MOCK_QUEUE:
    from .mock_queue import (
        enqueue_workflow_execution_mock as enqueue_workflow_execution,
        get_job_status_mock as get_job_status,
        get_queue_info_mock as get_queue_info
    )
    print("Using mock queue system")
else:
    try:
        from .queue import enqueue_workflow_execution, get_job_status, get_queue_info
        print("Using Redis queue system")
    except Exception as e:
        print(f"Redis queue failed, falling back to mock queue: {e}")
        from .mock_queue import (
            enqueue_workflow_execution_mock as enqueue_workflow_execution,
            get_job_status_mock as get_job_status,
            get_queue_info_mock as get_queue_info
        )

@asynccontextmanager
async def lifespan(app: FastAPI):
    print("INFO:     Creating database and tables...")
    create_db_and_tables()
    yield
    print("INFO:     Application shutdown.")

app = FastAPI(
    title="AutomateOS",
    description="API for automating operating system tasks",
    version="0.1.0",
    lifespan=lifespan
)

# CORS Configuration
origins = [
    "http://localhost:5173",
    "http://localhost:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/register/", response_model=schemas.UserPublic)
def register_user(user: schemas.UserCreate, session: Session = Depends(get_session)):
    """Register a new user with email and password."""
    db_user = crud.get_user_by_email(session=session, email=user.email)
    if db_user:
        raise HTTPException(
            status_code=400, 
            detail="Email already registered"
        )
    
    new_user = crud.create_user(session=session, user=user)
    return new_user

@app.post("/auth/token", response_model=schemas.Token)
def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(), 
    session: Session = Depends(get_session)
):
    """Authenticate user and return a JWT access token."""
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
    
    access_token_expires = timedelta(minutes=security.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = security.create_access_token(
        data={"sub": user.email}, 
        expires_delta=access_token_expires
    )
    
    return {"access_token": access_token, "token_type": "bearer"}

@app.get("/")
def read_root():
    queue_type = "Mock Queue (No Redis)" if USE_MOCK_QUEUE else "Redis Queue"
    return {
        "message": "Welcome to AutomateOS API",
        "queue_system": queue_type,
        "status": "ready"
    }

@app.get("/workflows/", response_model=List[schemas.WorkflowPublic])
def read_user_workflows(
    session: Session = Depends(get_session),
    current_user: models.User = Depends(security.get_current_user)
):
    """Retrieve all workflows for the current authenticated user."""
    return crud.get_workflows_by_owner(session=session, owner_id=current_user.id)

@app.post("/workflows/", response_model=schemas.WorkflowPublic)
def create_workflow(
    workflow: schemas.WorkflowCreate,
    session: Session = Depends(get_session),
    current_user: models.User = Depends(security.get_current_user)
):
    """Create a new workflow for the current authenticated user."""
    return crud.create_workflow(session=session, workflow=workflow, owner_id=current_user.id)

@app.get("/workflows/{workflow_id}", response_model=schemas.WorkflowPublic)
def read_workflow(
    workflow_id: int,
    session: Session = Depends(get_session),
    current_user: models.User = Depends(security.get_current_user)
):
    """Retrieve a specific workflow by ID."""
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
    """Update an existing workflow."""
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
    """Delete a workflow by ID."""
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
    """Webhook endpoint to trigger workflow execution."""
    try:
        payload = await request.json()
    except:
        payload = {}
    
    from datetime import datetime
    payload.update({
        "method": request.method,
        "headers": dict(request.headers),
        "url": str(request.url),
        "timestamp": datetime.utcnow().isoformat()
    })
    
    workflow = crud.get_workflow_by_webhook_id(session=session, webhook_id=webhook_id)
    if not workflow:
        raise HTTPException(status_code=404, detail="Webhook not found")
    
    if not workflow.is_active:
        raise HTTPException(status_code=400, detail="Workflow is not active")
    
    job_id = enqueue_workflow_execution(workflow.id, payload)
    
    return {
        "message": "Workflow execution enqueued",
        "job_id": job_id,
        "workflow_id": workflow.id,
        "status": "accepted",
        "queue_type": "mock" if USE_MOCK_QUEUE else "redis"
    }

@app.get("/jobs/{job_id}/status")
def get_job_status_endpoint(job_id: str):
    """Get the status of a queued workflow execution job."""
    return get_job_status(job_id)

@app.get("/queue/info")
def get_queue_info_endpoint():
    """Get information about the workflow execution queue."""
    info = get_queue_info()
    info["type"] = "mock" if USE_MOCK_QUEUE else "redis"
    return info

@app.get("/workflows/{workflow_id}/logs", response_model=List[schemas.ExecutionLogSummary])
def get_workflow_execution_logs(
    workflow_id: int,
    status: str = None,
    limit: int = 50,
    offset: int = 0,
    session: Session = Depends(get_session),
    current_user: models.User = Depends(security.get_current_user)
):
    """Retrieve execution logs for a specific workflow."""
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
    """Retrieve detailed information for a specific execution log."""
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
    """Get the total count of execution logs for a workflow."""
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
    """Clean up execution logs older than the specified number of days."""
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
    from sqlmodel import select
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