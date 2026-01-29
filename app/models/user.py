# app/models/user.py
from datetime import datetime
from enum import Enum
from typing import Optional
from sqlmodel import Field, SQLModel

class UserRole(str, Enum):
    USER = "user"
    ADMIN = "admin"

class User(SQLModel, table=True):
    
    __tablename__ = "users"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(index=True, max_length=100)
    email: str = Field(unique=True, index=True, max_length=255)
    password_hash: Optional[str] = Field(default=None, max_length=255)  # Optional for OAuth users
    google_id: Optional[str] = Field(default=None, unique=True, index=True, max_length=255)
    image: Optional[str] = Field(default=None, max_length=500)
    is_verified: bool = Field(default=False)  # Google users auto-verified
    role: UserRole = Field(default=UserRole.USER)
    is_active: bool = Field(default=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = Field(default=None)