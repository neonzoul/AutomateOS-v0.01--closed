"""
CRUD (Create, Read, Update, Delete) operations for database entities.

This module contains all database interaction logic, keeping it separate
from the API routing logic for better organization and testability.
"""

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