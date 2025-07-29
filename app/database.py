"""
Database connection utilities for the AutomateOS application.

This module provides the SQLModel engine setup and database initialization functions.
"""

from sqlmodel import create_engine, SQLModel, Session
from .config import settings

# Create database engine with configuration-based URL and echo settings
engine = create_engine(
    settings.database_url, 
    echo=settings.database_echo,
    # PostgreSQL-specific connection arguments
    connect_args={} if settings.database_url.startswith("postgresql") else {"check_same_thread": False}
)

def create_db_and_tables():
    """Creates the database file and all tables based on SQLModel metadata."""
    SQLModel.metadata.create_all(engine)

# Dependency to get a database session
def get_session():
    """Provides a database session for API endpoints."""
    with Session(engine) as session:
        yield session