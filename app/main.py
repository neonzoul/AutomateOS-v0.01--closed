# AutomateOS main application file
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .database import create_db_and_tables

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

@app.get("/")
def read_root():
    return {"message": "Welcome to AutomateOS API"}