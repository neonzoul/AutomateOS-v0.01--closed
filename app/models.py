"""
Database models for the Automate-OS MVP application.

This module defines the core SQLModel classes that represent the database schema
for user management, workflow definitions, and execution tracking.
"""

from typing import List, Optional
from datetime import datetime
from sqlmodel import Field, Relationship, SQLModel, Column, JSON

class User(SQLModel, table=True):
    """
    User model for authentication and workflow ownership.
    
    Represents registered users who can create and manage workflows.
    Each user can own multiple workflows and has secure password storage.
    """
    id: Optional[int] = Field(default=None, primary_key=True)
    email: str = Field(unique=True, index=True)  # Unique email for login
    hashed_password: str  # Securely hashed password (never store plain text)
    created_at: datetime = Field(default_factory=datetime.utcnow)
   
    # Relationship: One user can have many workflows
    workflows: List["Workflow"] = Relationship(back_populates="owner")


class Workflow(SQLModel, table=True):
    """
    Workflow model for storing automation definitions.
    
    Contains the workflow configuration, webhook endpoint, and metadata.
    The definition field stores the complete workflow logic as JSON.
    """
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str  # Human-readable workflow name
    description: Optional[str] = None  # Optional workflow description
    definition: dict = Field(sa_column=Column(JSON))  # Workflow steps and logic
    webhook_url: str = Field(unique=True)  # Unique webhook endpoint for triggering
    is_active: bool = True  # Enable/disable workflow execution
    owner_id: int = Field(foreign_key="user.id")  # Links to User table
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    # Relationship: Each workflow belongs to one user
    owner: "User" = Relationship(back_populates="workflows")


class ExecutionLog(SQLModel, table=True):
    """
    Execution log model for tracking workflow runs.
    
    Records every workflow execution with payload, results, timing, and status.
    Provides audit trail and debugging information for workflow runs.
    """
    id: Optional[int] = Field(default=None, primary_key=True)
    workflow_id: int = Field(foreign_key="workflow.id")  # Links to Workflow table
    status: str  # Execution status: "success", "failed", "running"
    payload: dict = Field(sa_column=Column(JSON))  # Input data that triggered workflow
    result: Optional[dict] = Field(sa_column=Column(JSON))  # Workflow output/results
    error_message: Optional[str] = None  # Error details if execution failed
    started_at: datetime = Field(default_factory=datetime.utcnow)  # Execution start time
    completed_at: Optional[datetime] = None  # Execution completion time (if finished)