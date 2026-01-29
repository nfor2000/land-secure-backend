import os
from typing import Optional

class Settings():
    # Database
    DATABASE_URL: str = os.getenv("DATABASE_URL", "postgresql://postgres:mysecretpassword@localhost:5432/terraverify")
    # REGISTRY_DB_URL: str = os.getenv("REGISTRY_DB_URL", "postgresql://postgres:mysecretpassword@localhost:5432/land_registry")
    
    # JWT
    SECRET_KEY: str = os.getenv("SECRET_KEY", "your-secret-key-change-this")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 4320  # 3 days in minutes (24 * 60 * 3)
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7  # 7 days for refresh tokens
    
    # Session (for browser sessions)
    SESSION_EXPIRE_DAYS: int = 3  # 3 days for browser sessions
    
    # Ollama Configuration
    OLLAMA_BASE_URL: str = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
    OLLAMA_MODEL: str = os.getenv("OLLAMA_MODEL", "llama3.2:1b")
    
    # Verification Settings
    COORDINATES_OVERLAP_THRESHOLD: float = 0.95  # 95% overlap required
    MAX_COORDINATES_DISTANCE_METERS: float = 50.0
    
    # API
    API_V1_PREFIX: str = "/api/v1"  # Changed from API_V1_PREFIX for consistency
    PROJECT_NAME: str = "ChekyaPlot Land Verification API"
    PROJECT_VERSION: str = "1.0.0"
    
    # CORS
    BACKEND_CORS_ORIGINS: list = ["http://localhost:3000", "http://localhost:3001"]
    
    # Debug
    DEBUG: bool = os.getenv("DEBUG", "False").lower() == "true"
    
    class Config:
        env_file = ".env"

settings = Settings()