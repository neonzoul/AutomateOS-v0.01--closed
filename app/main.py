# AutomateOS main application file
from contextlib import asynccontextmanager
from fastapi import FastAPI

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

@app.get("/")
def read_root():
    return {"message": "Welcome to AutomateOS API"}