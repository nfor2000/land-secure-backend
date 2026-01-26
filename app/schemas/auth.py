# app/schemas/auth.py
from typing import Optional
from pydantic import BaseModel, EmailStr

class GoogleAuthPayload(BaseModel):
    email: EmailStr
    name: str
    google_id: str
    image: Optional[str] = None

class AuthResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user_id: int
    role: str