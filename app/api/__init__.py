from fastapi import APIRouter
from app.api.endpoints import auth, user, verification

api_router = APIRouter()

api_router.include_router(auth.router, prefix="/auth", tags=["authentication"])
api_router.include_router(user.router, tags=["users"])
api_router.include_router(verification.router, tags=["verification"])