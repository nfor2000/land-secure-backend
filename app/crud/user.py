# app/crud/user.py
from datetime import datetime
from typing import Optional, List
from sqlmodel import Session, select
from fastapi import HTTPException, status
from app.models.user import User
from app.schemas.user import UserCreate, UserUpdate
from app.schemas.auth import GoogleAuthPayload
from app.core.security import hash_password, verify_password

class UserCRUD:
    @staticmethod
    def get_user_by_email(session: Session, email: str) -> Optional[User]:
        statement = select(User).where(User.email == email)
        return session.exec(statement).first()
    
    @staticmethod
    def get_user_by_google_id(session: Session, google_id: str) -> Optional[User]:
        statement = select(User).where(User.google_id == google_id)
        return session.exec(statement).first()
    
    @staticmethod
    def get_user_by_id(session: Session, user_id: int) -> Optional[User]:
        return session.get(User, user_id)
    
    @staticmethod
    def create_user(session: Session, user_data: UserCreate) -> User:
        # Check if user already exists
        existing_user = UserCRUD.get_user_by_email(session, user_data.email)
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )
        
        # Hash password
        password_hash = hash_password(user_data.password)
        
        # Create user
        user = User(
            name=user_data.name,
            email=user_data.email,
            password_hash=password_hash,
            is_verified=False,  # Email verification needed for regular users
        )
        
        session.add(user)
        session.commit()
        session.refresh(user)
        return user
    
    @staticmethod
    def create_or_update_google_user(
        session: Session, 
        google_data: GoogleAuthPayload
    ) -> User:
        """
        Create a new user from Google OAuth or update existing user
        """
        # Check if user exists by email or google_id
        user = UserCRUD.get_user_by_email(session, google_data.email)
        
        if not user:
            user = UserCRUD.get_user_by_google_id(session, google_data.google_id)
        
        if user:
            # Update existing user
            user.name = google_data.name
            user.image = google_data.image
            user.is_verified = True  # Google users are auto-verified
            
            # Link google_id if not already linked
            if not user.google_id:
                user.google_id = google_data.google_id
            
            user.updated_at = datetime.utcnow()
        else:
            # Create new user
            user = User(
                name=google_data.name,
                email=google_data.email,
                google_id=google_data.google_id,
                image=google_data.image,
                is_verified=True,  # Google users are pre-verified
                password_hash=None,  # No password for OAuth users
            )
            session.add(user)
        
        session.commit()
        session.refresh(user)
        return user
    
    @staticmethod
    def authenticate_user(session: Session, email: str, password: str) -> Optional[User]:
        user = UserCRUD.get_user_by_email(session, email)
        if not user:
            return None
        
        # Check if user has a password (not OAuth-only user)
        if not user.password_hash:
            return None
            
        if not verify_password(password, user.password_hash):
            return None
        return user
    
    @staticmethod
    def update_user(session: Session, user_id: int, user_data: UserUpdate) -> Optional[User]:
        user = UserCRUD.get_user_by_id(session, user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        # Update fields
        update_data = user_data.model_dump(exclude_unset=True)
        
        for field, value in update_data.items():
            if field == "password" and value:
                user.password_hash = hash_password(value)
            elif field == "email" and value:
                # Check if email is already taken
                existing_user = UserCRUD.get_user_by_email(session, value)
                if existing_user and existing_user.id != user_id:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="Email already in use"
                    )
                user.email = value
            elif field != "password":
                setattr(user, field, value)
        
        user.updated_at = datetime.utcnow()
        session.add(user)
        session.commit()
        session.refresh(user)
        return user
    
    @staticmethod
    def delete_user(session: Session, user_id: int) -> bool:
        user = UserCRUD.get_user_by_id(session, user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        session.delete(user)
        session.commit()
        return True
    
    @staticmethod
    def get_all_users(session: Session, skip: int = 0, limit: int = 100) -> List[User]:
        statement = select(User).offset(skip).limit(limit)
        return list(session.exec(statement).all())