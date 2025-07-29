"""
Database migration utilities for AutomateOS.

This module provides functions to create database tables and indexes
for optimal production performance.
"""

from sqlmodel import SQLModel, text
from sqlalchemy import Index
from .database import engine
from .models import User, Workflow, ExecutionLog


def create_database_indexes():
    """
    Create database indexes for optimal query performance.
    
    This function creates indexes on frequently queried columns
    to improve performance in production environments.
    """
    with engine.begin() as conn:
        # User table indexes
        try:
            conn.execute(text("CREATE INDEX IF NOT EXISTS idx_user_email ON user (email)"))
            print("✓ Created index on user.email")
        except Exception as e:
            print(f"Index on user.email already exists or failed: {e}")
        
        # Workflow table indexes
        try:
            conn.execute(text("CREATE INDEX IF NOT EXISTS idx_workflow_owner_id ON workflow (owner_id)"))
            print("✓ Created index on workflow.owner_id")
        except Exception as e:
            print(f"Index on workflow.owner_id already exists or failed: {e}")
            
        try:
            conn.execute(text("CREATE INDEX IF NOT EXISTS idx_workflow_webhook_url ON workflow (webhook_url)"))
            print("✓ Created index on workflow.webhook_url")
        except Exception as e:
            print(f"Index on workflow.webhook_url already exists or failed: {e}")
            
        try:
            conn.execute(text("CREATE INDEX IF NOT EXISTS idx_workflow_is_active ON workflow (is_active)"))
            print("✓ Created index on workflow.is_active")
        except Exception as e:
            print(f"Index on workflow.is_active already exists or failed: {e}")
        
        # ExecutionLog table indexes
        try:
            conn.execute(text("CREATE INDEX IF NOT EXISTS idx_execution_log_workflow_id ON executionlog (workflow_id)"))
            print("✓ Created index on executionlog.workflow_id")
        except Exception as e:
            print(f"Index on executionlog.workflow_id already exists or failed: {e}")
            
        try:
            conn.execute(text("CREATE INDEX IF NOT EXISTS idx_execution_log_status ON executionlog (status)"))
            print("✓ Created index on executionlog.status")
        except Exception as e:
            print(f"Index on executionlog.status already exists or failed: {e}")
            
        try:
            conn.execute(text("CREATE INDEX IF NOT EXISTS idx_execution_log_started_at ON executionlog (started_at)"))
            print("✓ Created index on executionlog.started_at")
        except Exception as e:
            print(f"Index on executionlog.started_at already exists or failed: {e}")
            
        # Composite indexes for common query patterns
        try:
            conn.execute(text("CREATE INDEX IF NOT EXISTS idx_execution_log_workflow_status ON executionlog (workflow_id, status)"))
            print("✓ Created composite index on executionlog.workflow_id, status")
        except Exception as e:
            print(f"Composite index on executionlog.workflow_id, status already exists or failed: {e}")
            
        try:
            conn.execute(text("CREATE INDEX IF NOT EXISTS idx_execution_log_workflow_started ON executionlog (workflow_id, started_at DESC)"))
            print("✓ Created composite index on executionlog.workflow_id, started_at")
        except Exception as e:
            print(f"Composite index on executionlog.workflow_id, started_at already exists or failed: {e}")


def run_migrations():
    """
    Run all database migrations including table creation and indexing.
    
    This function should be called during application startup to ensure
    the database schema is up to date.
    """
    print("Running database migrations...")
    
    # Create all tables
    print("Creating database tables...")
    SQLModel.metadata.create_all(engine)
    print("✓ Database tables created")
    
    # Create indexes
    print("Creating database indexes...")
    create_database_indexes()
    print("✓ Database indexes created")
    
    print("Database migrations completed successfully!")


if __name__ == "__main__":
    # Allow running migrations directly
    run_migrations()