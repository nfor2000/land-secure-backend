from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session
from app.core.database import get_session
from app.crud.user import UserCRUD
from app.schemas.user import UserRead, UserUpdate
from app.api.deps import get_current_active_user, get_current_admin_user
from app.models.user import User

router = APIRouter(prefix="/users", tags=["users"])

@router.get("/", response_model=List[UserRead])
def get_all_users(
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_admin_user),
    session: Session = Depends(get_session)
):
    """
    Get all users (Admin only)
    """
    return UserCRUD.get_all_users(session, skip, limit)

@router.get("/{user_id}", response_model=UserRead)
def get_user(
    user_id: int,
    current_user: User = Depends(get_current_admin_user),
    session: Session = Depends(get_session)
):
    """
    Get user by ID (Admin only)
    """
    user = UserCRUD.get_user_by_id(session, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    return user

@router.put("/{user_id}", response_model=UserRead)
def update_user(
    user_id: int,
    user_data: UserUpdate,
    current_user: User = Depends(get_current_admin_user),
    session: Session = Depends(get_session)
):
    """
    Update user by ID (Admin only)
    """
    return UserCRUD.update_user(session, user_id, user_data)

@router.delete("/{user_id}")
def delete_user(
    user_id: int,
    current_user: User = Depends(get_current_admin_user),
    session: Session = Depends(get_session)
):
    """
    Delete user (Admin only)
    """
    success = UserCRUD.delete_user(session, user_id)
    if success:
        return {"message": "User deleted successfully"}
    
    raise HTTPException(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        detail="Failed to delete user"
    )