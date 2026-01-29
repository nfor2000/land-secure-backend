from datetime import datetime
from typing import List, Dict, Optional
import uuid
from pydantic import BaseModel, Field, validator

class Coordinate(BaseModel):
    lat: float = Field(..., ge=-90, le=90)
    lng: float = Field(..., ge=-180, le=180)

class VerificationRequestCreate(BaseModel):
    """Simple request schema"""
    town: str
    layout: str
    block_number: str
    plot_number: str
    coordinates: List[Coordinate] = Field(..., min_items=3)
    
    @validator('coordinates')
    def validate_coords(cls, v):
        """Ensure polygon is closed"""
        if len(v) < 3:
            raise ValueError('Need at least 3 points for polygon')
        return v

class VerificationResult(BaseModel):
    """Simple response schema"""
    verification_id: uuid.UUID
    status: str
    is_verified: bool
    message: str
    
    # Match details
    location_match: Optional[bool] = None
    coordinates_match: Optional[bool] = None
    overlap_percent: Optional[float] = None
    distance_meters: Optional[float] = None
    
    # Fraud
    is_fraud: bool = False
    fraud_reason: Optional[str] = None
    
    # Official data (if verified)
    official_owner: Optional[str] = None
    official_area: Optional[float] = None

class VerificationHistory(BaseModel):
    """History item"""
    id: uuid.UUID
    status: str
    town: str
    layout: str
    block: str
    plot: str
    is_verified: bool
    is_fraud: bool
    requested_at: datetime