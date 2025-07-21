# Week 3 Logbook

## Day 1 - Monday, July 20, 2025

### Summary
Set up project foundation including frontend boilerplate and backend infrastructure with FastAPI.

### Completed Tasks

#### Frontend Setup
- [✓] Imported and edited boilerplate from previous project
  - Updated package.json with correct dependencies and scripts
  - Fixed tsconfig.json for Vite instead of Next.js
  - Created proper vite.config.ts and tsconfig.node.json
  - Updated scripts (dev, build, preview) for Vite workflow
  - Configured TypeScript for modern React development with proper paths
  - Set up Chakra UI integration
  - Maintained existing folder structure in src/ for components, contexts, hooks, services
- [✓] Committed initial "hello world" version

#### Development Environment
- [✓] Set up AI assistants (NotebookLM, Gemini 2.5 Pro)
- [✓] Created and activated Python virtual environment
  - Command: `source venv/Scripts/activate` (ensures packages install to project venv, not globally)

#### Backend Foundation
- [✓] Installed core dependencies
  ```bash
  pip install fastapi "uvicorn[standard]" sqlmodel
  ```
- [✓] Created initial project structure
  ```
  AutomateOS/
  ├── app/
  │   ├── __init__.py
  │   └── main.py
  └── requirements.txt 
  ```
- [✓] Implemented basic health check endpoint
  - Created FastAPI application in `app/main.py`
  - Added endpoint returning JSON message
- [✓] Successfully ran development server
  ```bash
  uvicorn app.main:app --reload
  ```
  - Verified health check at http://127.0.0.1:8000
  - Tested FastAPI's interactive docs at http://127.0.0.1:8000/docs

#### Database Setup
- [✓] Defined core data models with SQLModel
  - Created User, Workflow, and ExecutionLog models
- [✓] Implemented database connection utilities
  - Created `database.py` with SQLite connection
  - Set up engine and table creation function
- [✓] Configured database initialization on application startup
  - Used FastAPI's lifespan context manager for proper startup/shutdown

### Pending Tasks
- [ ] Set up React project with Vite and Chakra UI
- [✅] Configure CORS middleware for local development

### Implementation Notes

#### Database Connection Setup
Created `database.py` with the following code:
```python
from sqlmodel import create_engine, SQLModel

# The database file will be named "database.db"
DATABASE_URL = "sqlite:///database.db"

# The engine is the main point of contact with the database
engine = create_engine(DATABASE_URL, echo=True)

def create_db_and_tables():
    """
    Creates the database file and all tables based on SQLModel metadata.
    """
    SQLModel.metadata.create_all(engine)
```

#### FastAPI Application Setup
Updated `main.py` to initialize database on startup:
```python
# AutomateOS main application file
from contextlib import asynccontextmanager
from fastapi import FastAPI
from .database import create_db_and_tables

@asynccontextmanager
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

@app.get("/")
def read_root():
    return {"message": "Welcome to AutomateOS API"}
```

#### Next Steps: CORS Configuration
Need to add CORS middleware to allow frontend-backend communication:
```python
from fastapi.middleware.cors import CORSMiddleware

# CORS configuration
origins = [
    "http://localhost:5173",  # Default port for Vite React dev server
    "http://localhost:3000",  # Common alternative for React dev servers
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```