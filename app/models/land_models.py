from datetime import datetime
from typing import Optional, List, Dict
import uuid
from sqlmodel import Field, SQLModel, Column, JSON
from pydantic import BaseModel

# ============================================================================
# REGISTRY DATABASE (Existing - READ ONLY)
# ============================================================================

# class LandRegistry(SQLModel, table=True):
#     """Official land registry records"""
#     __tablename__ = "land_registry"
    
#     id: Optional[int] = Field(default=None, primary_key=True)
    
#     # Location ID (Primary Key)
#     town: str = Field(index=True)
#     layout: str = Field(index=True)
#     block_number: str = Field(index=True)
#     plot_number: str = Field(index=True)
    
#     # Official coordinates
#     coordinates: List[Dict] = Field(sa_column=Column(JSON))
    
#     # Ownership
#     owner_name: str
#     owner_phone: Optional[str] = None
    
#     # Land info
#     area_m2: float
#     certificate_url: Optional[str] = None
#     is_active: bool = Field(default=True)
    
#     # Index
#     location_hash: str = Field(index=True)

class LandRegistry(SQLModel, table=True):
    __tablename__ = "land_registry" 
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)    
    certificate_number: str = Field(index=True, unique=True) 
    certificate_pdf_url: str 
    town: str = Field(index=True) 
    layout: str = Field(index=True) 
    block_number: str = Field(index=True) 
    plot_number: str = Field(index=True) 
    coordinates: List[Dict] = Field(sa_column=Column(JSON)) 
    area_square_meters: Optional[float] = None 
    owner_name: str 
    owner_national_id: Optional[str] = None 
    owner_phone: Optional[str] = None 
    owner_email: Optional[str] = None 
    land_use: Optional[str] = None 
    acquisition_date: Optional[datetime] = None 
    registration_date: datetime = Field(default_factory=datetime.utcnow) 
    is_active: bool = Field(default=True) 
    notes: Optional[str] = None


class VerificationRequest(SQLModel, table=True):
    """Stores verification requests and results"""
    __tablename__ = "verification_requests"
    
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    user_id: int = Field(foreign_key="users.id", index=True)
    
    # Submitted data
    submitted_town: str
    submitted_layout: str
    submitted_block: str
    submitted_plot: str
    submitted_coords: List[Dict] = Field(sa_column=Column(JSON))
    
    # Verification results
    status: str = Field(default="pending")  # pending, verified, failed, fraudulent
    is_verified: bool = Field(default=False)
    message: Optional[str] = None
    
    # Match details (simple booleans)
    location_match: Optional[bool] = None
    coordinates_match: Optional[bool] = None
    
    # Scores (simple 0-1)
    overlap_score: Optional[float] = None
    distance_meters: Optional[float] = None
    
    # Fraud detection
    is_fraud: bool = Field(default=False)
    fraud_reason: Optional[str] = None
    
    # Official data (if verified)
    official_owner: Optional[str] = None
    official_coords: Optional[List[Dict]] = Field(sa_column=Column(JSON), default=None)
    official_area: Optional[float] = None
    
    # Timestamps
    requested_at: datetime = Field(default_factory=datetime.utcnow, index=True)
    verified_at: Optional[datetime] = None