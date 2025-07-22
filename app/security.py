import os
from datetime import datetime, timedelta, timezone
from typing import Optional
from jose import JWTError, jwt
from dotenv import load_dotenv
from passlib.context import CryptContext

load_dotenv()  # Load environment variables from .env file

# --- JWT Settings ---
SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES"))

# Use bcrypt for hashing passwords
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verifies a plain password against a hashed one."""
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    """Hashes a plain password."""
    return pwd_context.hash(password)


# Creates a new JWT access token for user authentication.
"""
Args:
    data: Dictionary containing user information (typically {'sub': user_email})
    expires_delta: Optional custom expiration time. If None, defaults to 15 minutes

Returns:
    str: Encoded JWT token that can be used for API authentication
    
Example:
    token = create_access_token({"sub": "user@example.com"})
    # or with custom expiration
    token = create_access_token(
        {"sub": "user@example.com"}, 
        expires_delta=timedelta(hours=1)
    )
"""
def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        # Default to 15 minutes if no custom expiration provided
        expire = datetime.now(timezone.utc) + timedelta(minutes=15)
    
    # Add expiration claim to the token payload
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt