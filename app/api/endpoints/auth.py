# app/api/routes/auth.py
from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlmodel import Session
from app.core.database import get_session
from app.core.config import settings
from app.core.security import create_access_token
from app.crud.user import UserCRUD
from app.schemas.user import Token, UserCreate, UserRead
from app.schemas.auth import GoogleAuthPayload, AuthResponse
from app.api.deps import get_current_user

router = APIRouter(tags=["authentication"])

@router.post("/register", response_model=UserRead, status_code=status.HTTP_201_CREATED)
def register(
    user_data: UserCreate,
    session: Session = Depends(get_session)
):
    """
    Register a new user
    """
    return UserCRUD.create_user(session, user_data)

@router.post("/login", response_model=AuthResponse)
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    session: Session = Depends(get_session)
):
    """
    Login and get access token
    """
    user = UserCRUD.authenticate_user(session, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account is inactive"
        )
    
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.email, "role": user.role}, 
        expires_delta=access_token_expires
    )
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user_id": user.id,
        "role": user.role
    }

@router.post("/google", response_model=AuthResponse)
def google_auth(
    google_data: GoogleAuthPayload,
    session: Session = Depends(get_session)
):
    """
    Authenticate or register user via Google OAuth
    """
    # Create or update user
    user = UserCRUD.create_or_update_google_user(session, google_data)
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account is inactive"
        )
    
    # Generate access token
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.email, "role": user.role},
        expires_delta=access_token_expires
    )
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user_id": user.id,
        "role": user.role
    }

@router.get("/me", response_model=UserRead)
def read_users_me(current_user: UserRead = Depends(get_current_user)):
    """
    Get current user information
    """
    return current_user

@router.get("/verify-token")
def verify_token_endpoint(token: str):
    """
    Verify if a token is valid
    """
    from app.core.security import verify_token
    payload = verify_token(token)
    if payload:
        return {"valid": True, "email": payload.get("sub")}
    return {"valid": False}