from sqlmodel import create_engine, SQLModel, Session
from app.core.config import settings
import os

def get_engine():
    """Create database engine based on URL"""
    # Check if it's SQLite or PostgreSQL
    if settings.DATABASE_URL.startswith("sqlite"):
        # SQLite connection
        return create_engine(
            settings.DATABASE_URL, 
            echo=True,
            connect_args={"check_same_thread": False}  # Only for SQLite
        )
    else:
        # PostgreSQL or other databases
        return create_engine(
            settings.DATABASE_URL, 
            echo=True
            # No connect_args for PostgreSQL!
        )

# def get_registry_engine():
#     """Create registry database engine"""
#     if settings.REGISTRY_DB_URL.startswith("sqlite"):
#         return create_engine(
#             settings.REGISTRY_DB_URL,
#             echo=False,
#             connect_args={"check_same_thread": False}
#         )
#     else:
#         return create_engine(
#             settings.REGISTRY_DB_URL,
#             echo=False
#         )

# Create engines
engine = get_engine()
# registry_engine = get_registry_engine()

def create_db_and_tables():
    """Create verification database tables only (not registry)"""
    SQLModel.metadata.create_all(engine)

def get_session():
    with Session(engine) as session:
        yield session

# def get_registry_session():
#     with Session(registry_engine) as session:
#         yield session