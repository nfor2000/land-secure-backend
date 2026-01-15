from fastapi import APIRouter
from app.api.endpoints import auth, user

api_router = APIRouter()

api_router.include_router(auth.router, prefix="/auth", tags=["authentication"])
api_router.include_router(user.router, tags=["users"])