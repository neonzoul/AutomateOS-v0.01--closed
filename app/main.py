# AutomateOS main application file
from contextlib import asynccontextmanager
from datetime import timedelta
from typing import List
from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordRequestForm
from sqlmodel import Session

from . import crud, schemas, security, models
from .database import create_db_and_tables, get_session

@asynccontextmanager
# Use lifespan context manager for database initialization
async def lifespan(app: FastAPI):
    # Code to run on startup
    print("INFO:     Creating database and tables...")
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

# CORS Configuration
# Cross-Origin Resource Sharing (CORS) allows web applications running at one origin
# (domain, protocol, or port) to access resources from a different origin.
# This is essential for our architecture where the React frontend and FastAPI backend
# run on different ports during development.
origins = [
    "http://localhost:5173",  # The default port for Vite React dev server
    "http://localhost:3000",  # A common alternative for React dev servers
]

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