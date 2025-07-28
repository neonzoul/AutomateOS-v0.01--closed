from sqlmodel import SQLModel
from datetime import datetime
from typing import Optional

# Schema for creating a new user (input)
class UserCreate(SQLModel):
    email: str
    password: str

# Schema for reading user data (output)
class UserPublic(SQLModel):
    id: int
    email: str
    created_at: datetime

# Schema for JWT token response
class Token(SQLModel):
    access_token: str
    token_type: str = "bearer"

# Schema for creating a new workflow (input)
class WorkflowCreate(SQLModel):
    name: str
    description: Optional[str] = None
    definition: dict
    is_active: bool = True

# Schema for reading workflow data (output)
class WorkflowPublic(SQLModel):
    id: int
    name: str
    description: Optional[str]
    definition: dict
    webhook_url: str
    is_active: bool
    owner_id: int
    created_at: datetime
    updated_at: datetime

# Schema for reading execution log data (output)
class ExecutionLogPublic(SQLModel):
    id: int
    workflow_id: int
    status: str
    payload: dict
    result: Optional[dict]
    error_message: Optional[str]
    started_at: datetime
    completed_at: Optional[datetime]

# Schema for execution log summary (for list views)
class ExecutionLogSummary(SQLModel):
    id: int
    workflow_id: int
    status: str
    started_at: datetime
    completed_at: Optional[datetime]
    error_message: Optional[str]