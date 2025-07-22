# AutomateOS main application file
from contextlib import asynccontextmanager
from datetime import timedelta
from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordRequestForm
from sqlmodel import Session

from . import crud, schemas, security
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