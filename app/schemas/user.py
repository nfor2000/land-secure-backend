from datetime import datetime
from typing import Optional
from pydantic import BaseModel, EmailStr, Field
from app.models.user import UserRole

# Base schemas
class UserBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    email: EmailStr = Field(..., max_length=255)

# Request schemas
class UserCreate(UserBase):
    password: str = Field(..., min_length=8, max_length=100)
    role: Optional[UserRole] = UserRole.USER

class UserUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    email: Optional[EmailStr] = Field(None, max_length=255)
    password: Optional[str] = Field(None, min_length=8, max_length=100)
    is_active: Optional[bool] = None

class UserLogin(BaseModel):
    email: EmailStr
    password: str

# Response schemas
class UserRead(UserBase):
    id: int
    role: UserRole
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime]
    
    class Config:
        from_attributes = True

class UserInDB(UserRead):
    password_hash: str

# Token schemas
class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    email: Optional[str] = None
    role: Optional[str] = None

from datetime import datetime
from enum import Enum
from typing import Optional
from sqlmodel import Field, SQLModel