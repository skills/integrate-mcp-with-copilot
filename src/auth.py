"""
Authentication and authorization utilities for the Mergington High School API.
"""

from datetime import datetime, timedelta
from typing import Optional
from enum import Enum
from pydantic import BaseModel
import jwt
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthCredentials

# Configuration
SECRET_KEY = "your-secret-key-change-this-in-production"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
security = HTTPBearer()


class Role(str, Enum):
    """User roles in the system"""
    STUDENT = "student"
    ORGANIZER = "organizer"
    ADMIN = "admin"


class TokenData(BaseModel):
    """JWT token payload"""
    email: str
    role: Role


class User(BaseModel):
    """User model"""
    email: str
    role: Role
    hashed_password: str


class LoginRequest(BaseModel):
    """Login request model"""
    email: str
    password: str


class TokenResponse(BaseModel):
    """Token response after login"""
    access_token: str
    token_type: str
    role: str


# In-memory user database (replace with real database later)
users_db: dict[str, User] = {
    "student@mergington.edu": User(
        email="student@mergington.edu",
        role=Role.STUDENT,
        hashed_password=pwd_context.hash("student_password")
    ),
    "organizer@mergington.edu": User(
        email="organizer@mergington.edu",
        role=Role.ORGANIZER,
        hashed_password=pwd_context.hash("organizer_password")
    ),
    "admin@mergington.edu": User(
        email="admin@mergington.edu",
        role=Role.ADMIN,
        hashed_password=pwd_context.hash("admin_password")
    ),
    "emma@mergington.edu": User(
        email="emma@mergington.edu",
        role=Role.STUDENT,
        hashed_password=pwd_context.hash("emma_password")
    ),
    "john@mergington.edu": User(
        email="john@mergington.edu",
        role=Role.STUDENT,
        hashed_password=pwd_context.hash("john_password")
    ),
}


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash"""
    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(email: str, role: Role, expires_delta: Optional[timedelta] = None) -> str:
    """Create a JWT access token"""
    if expires_delta is None:
        expires_delta = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    expire = datetime.utcnow() + expires_delta
    payload = {
        "email": email,
        "role": role.value,
        "exp": expire,
        "iat": datetime.utcnow()
    }
    
    encoded_jwt = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def decode_token(token: str) -> TokenData:
    """Decode a JWT token and return token data"""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("email")
        role: str = payload.get("role")
        
        if email is None or role is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        return TokenData(email=email, role=Role(role))
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except jwt.InvalidTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
            headers={"WWW-Authenticate": "Bearer"},
        )


async def get_current_user(credentials: HTTPAuthCredentials = Depends(security)) -> TokenData:
    """
    Dependency to get the current authenticated user from the token.
    Returns 401 if not authenticated.
    """
    token = credentials.credentials
    return decode_token(token)


async def require_student(current_user: TokenData = Depends(get_current_user)) -> TokenData:
    """Require the user to be a student or higher role"""
    if current_user.role not in [Role.STUDENT, Role.ORGANIZER, Role.ADMIN]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Student access required"
        )
    return current_user


async def require_organizer(current_user: TokenData = Depends(get_current_user)) -> TokenData:
    """Require the user to be an organizer or admin"""
    if current_user.role not in [Role.ORGANIZER, Role.ADMIN]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Organizer access required"
        )
    return current_user


async def require_admin(current_user: TokenData = Depends(get_current_user)) -> TokenData:
    """Require the user to have admin role"""
    if current_user.role != Role.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    return current_user
