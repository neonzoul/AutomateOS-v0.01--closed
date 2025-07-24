"""
CRUD (Create, Read, Update, Delete) operations for database entities.

This module contains all database interaction logic, keeping it separate
from the API routing logic for better organization and testability.
"""

from typing import List
from sqlmodel import Session, select
from . import models, schemas, security

def create_user(session: Session, user: schemas.UserCreate) -> models.User:
    """Create a new user in the database with hashed password."""
    hashed_password = security.get_password_hash(user.password)
    db_user = models.User(
        email=user.email, 
        hashed_password=hashed_password
    )
    session.add(db_user)
    session.commit()
    session.refresh(db_user)
    return db_user

def get_user_by_email(session: Session, email: str) -> models.User | None:
    """Retrieve a user by their email address."""
    return session.exec(
        select(models.User).where(models.User.email == email)
    ).first()

def authenticate_user(session: Session, user_credentials: schemas.UserCreate) -> models.User | None:
    """
    Authenticate a user by email and password.
    
    Args:
        session: Database session
        user_credentials: UserCreate object containing email and password
        
    Returns:
        User object if authentication successful, None otherwise
    """
    user = get_user_by_email(session, email=user_credentials.email)
    if not user:
        return None
    if not security.verify_password(user_credentials.password, user.hashed_password):
        return None
    return user

def get_workflows_by_owner(session: Session, owner_id: int) -> List[models.Workflow]:
    """Retrieve all workflows for a specific owner."""
    return session.exec(select(models.Workflow).where(models.Workflow.owner_id == owner_id)).all()

def create_workflow(session: Session, workflow: schemas.WorkflowCreate, owner_id: int) -> models.Workflow:
    """Create a new workflow for a specific owner."""
    import uuid
    
    # Generate unique webhook URL
    webhook_url = f"/webhook/{str(uuid.uuid4())}"
    
    db_workflow = models.Workflow(
        name=workflow.name,
        description=workflow.description,
        definition=workflow.definition,
        webhook_url=webhook_url,
        is_active=workflow.is_active,
        owner_id=owner_id
    )
    session.add(db_workflow)
    session.commit()
    session.refresh(db_workflow)
    return db_workflow

def get_workflow_by_id(session: Session, workflow_id: int, owner_id: int) -> models.Workflow | None:
    """Retrieve a specific workflow by ID, ensuring it belongs to the owner."""
    return session.exec(
        select(models.Workflow).where(
            models.Workflow.id == workflow_id,
            models.Workflow.owner_id == owner_id
        )
    ).first()

def update_workflow(session: Session, workflow_id: int, workflow_update: schemas.WorkflowCreate, owner_id: int) -> models.Workflow | None:
    """Update an existing workflow."""
    db_workflow = get_workflow_by_id(session, workflow_id, owner_id)
    if not db_workflow:
        return None
    
    # Update fields
    db_workflow.name = workflow_update.name
    db_workflow.description = workflow_update.description
    db_workflow.definition = workflow_update.definition
    db_workflow.is_active = workflow_update.is_active
    db_workflow.updated_at = models.datetime.utcnow()
    
    session.add(db_workflow)
    session.commit()
    session.refresh(db_workflow)
    return db_workflow

def delete_workflow(session: Session, workflow_id: int, owner_id: int) -> bool:
    """Delete a workflow by ID, ensuring it belongs to the owner."""
    db_workflow = get_workflow_by_id(session, workflow_id, owner_id)
    if not db_workflow:
        return False
    
    session.delete(db_workflow)
    session.commit()
    return True