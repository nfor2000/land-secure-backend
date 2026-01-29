import uuid
from app.models.user import User
from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session
from app.core.database import get_session
from app.api.deps import get_current_user
from app.models.land_models import  VerificationRequest
from app.schemas.land_schemas import (
    VerificationRequestCreate,
    VerificationResult,
    VerificationHistory
)
from app.services.verification_service import verifier

router = APIRouter(prefix="/verification", tags=["verification"])

@router.post("/verify", response_model=VerificationResult)
async def verify_land(
    request: VerificationRequestCreate,
    current_user: User = Depends(get_current_user),  # This injects the user
    db: Session = Depends(get_session)
):
    """
    Verify land ownership using coordinates and location data.
    
    This endpoint compares submitted land data against official registry records.
    
    **Authentication Required**: User must be logged in.
    
    **Verification Process**:
    1. Exact match on location (town/layout/block/plot)
    2. Approximate match on coordinates (≥2 of 3 checks must pass)
    3. Fraud detection for suspicious mismatches
    
    **Returns**:
    - Verification result with match details
    - Official ownership data (if verified)
    - Fraud detection flags (if applicable)
    """
    try:
        # The user is automatically injected by FastAPI
        vr = verifier.verify_land(db, current_user.id, request)
        
        return VerificationResult(
            verification_id=vr.id,
            status=vr.status,
            is_verified=vr.is_verified,
            message=vr.message or '',
            location_match=vr.location_match,
            coordinates_match=vr.coordinates_match,
            overlap_percent=vr.overlap_score,
            distance_meters=vr.distance_meters,
            is_fraud=vr.is_fraud,
            fraud_reason=vr.fraud_reason,
            official_owner=vr.official_owner,
            official_area=vr.official_area
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/history", response_model=list[VerificationHistory])
async def get_verification_history(
    current_user: User = Depends(get_current_user),  # User dependency
    db: Session = Depends(get_session),
    limit: int = 20
):
    """
    Get verification history for the authenticated user.
    
    **Authentication Required**: User must be logged in.
    
    **Parameters**:
    - `limit`: Maximum number of records to return (default: 20, max: 100)
    
    **Returns**: List of verification requests with basic information
    """
    history = verifier.get_history(db, current_user.id, limit)
    
    return [
        VerificationHistory(
            id=vr.id,
            status=vr.status,
            town=vr.submitted_town,
            layout=vr.submitted_layout,
            block=vr.submitted_block,
            plot=vr.submitted_plot,
            is_verified=vr.is_verified,
            is_fraud=vr.is_fraud,
            requested_at=vr.requested_at
        )
        for vr in history
    ]

@router.get("/{verification_id}")
async def get_verification_details(
    verification_id: uuid.UUID,
    current_user: User = Depends(get_current_user),  # User dependency
    db: Session = Depends(get_session)
):
    """
    Get detailed information about a specific verification request.
    
    **Authentication Required**: User must be logged in.
    
    **Security**: Users can only access their own verification requests.
    
    **Parameters**:
    - `verification_id`: ID of the verification request
    
    **Returns**: Complete verification details including submitted and official data
    """
    from sqlmodel import select
    
    stmt = select(VerificationRequest).where(
        VerificationRequest.id == verification_id,
        VerificationRequest.user_id == current_user.id  # Security check
    )
    vr = db.exec(stmt).first()
    
    if not vr:
        raise HTTPException(status_code=404, detail="Verification not found")
    
    return {
        'id': vr.id,
        'status': vr.status,
        'is_verified': vr.is_verified,
        'is_fraud': vr.is_fraud,
        'requested_at': vr.requested_at,
        'verified_at': vr.verified_at,
        
        'submitted_data': {
            'town': vr.submitted_town,
            'layout': vr.submitted_layout,
            'block': vr.submitted_block,
            'plot': vr.submitted_plot,
            'coordinates': vr.submitted_coords
        },
        
        'match_details': {
            'location_match': vr.location_match,
            'coordinates_match': vr.coordinates_match,
            'overlap_score': vr.overlap_score,
            'distance_meters': vr.distance_meters
        },
        
        'official_data': {
            'owner': vr.official_owner,
            'area': vr.official_area,
            'coordinates': vr.official_coords
        } 
    }