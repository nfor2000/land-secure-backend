import os
from typing import Optional


class Settings():
    # Database
    DATABASE_URL: str = "postgresql://postgres:mysecretpassword@localhost:5432/terraverify"
    
    # JWT
    SECRET_KEY: str = os.getenv("SECRET_KEY", "your-secret-key-change-this-in-production")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # API
    API_V1_PREFIX: str = "/api/v1"
    PROJECT_NAME: str = "User Authentication API"
    PROJECT_VERSION: str = "1.0.0"
    
    class Config:
        env_file = ".env"

settings = Settings()