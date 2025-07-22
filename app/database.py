"""
Database connection utilities for the AutomateOS application.

This module provides the SQLModel engine setup and database initialization functions.
"""

from sqlmodel import create_engine, SQLModel, Session

# The database file will be named "database.db"
DATABASE_URL = "sqlite:///database.db"

# The engine is the main point of contact with the database
# echo=True enables SQL statement logging for debugging
engine = create_engine(DATABASE_URL, echo=True)

def create_db_and_tables():
    """Creates the database file and all tables based on SQLModel metadata."""
    SQLModel.metadata.create_all(engine)

# Dependency to get a database session
def get_session():
    """Provides a database session for API endpoints."""
    with Session(engine) as session:
        yield session