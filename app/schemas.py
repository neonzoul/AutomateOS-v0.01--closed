from sqlmodel import SQLModel
from datetime import datetime

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