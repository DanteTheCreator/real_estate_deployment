from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from database import get_db, RentalApplication, Property, User
from schemas import (
    RentalApplicationCreate, RentalApplicationUpdate, RentalApplicationResponse,
    MessageResponse, ApplicationStatus
)
from auth import get_current_active_user, require_landlord

router = APIRouter(prefix="/applications", tags=["Rental Applications"])

@router.post("/", response_model=RentalApplicationResponse, status_code=status.HTTP_201_CREATED)
async def create_application(
    application_data: RentalApplicationCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Create a new rental application"""
    # Check if property exists and is available
    property_obj = db.query(Property).filter(Property.id == application_data.property_id).first()
    if not property_obj:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Property not found"
        )
    
    if not property_obj.is_available:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Property is not available for rent"
        )
    
    # Check if user already has an application for this property
    existing_app = db.query(RentalApplication).filter(
        RentalApplication.property_id == application_data.property_id,
        RentalApplication.tenant_id == current_user.id
    ).first()
    
    if existing_app:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You already have an application for this property"
        )
    
    # Create application
    application_dict = application_data.model_dump()
    db_application = RentalApplication(**application_dict, tenant_id=current_user.id)
    
    db.add(db_application)
    db.commit()
    db.refresh(db_application)
    
    return RentalApplicationResponse.model_validate(db_application)

@router.get("/my-applications", response_model=List[RentalApplicationResponse])
async def get_my_applications(
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    status_filter: Optional[ApplicationStatus] = None,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get current user's rental applications"""
    query = db.query(RentalApplication).filter(RentalApplication.tenant_id == current_user.id)
    
    if status_filter:
        query = query.filter(RentalApplication.status == status_filter.value)
    
    applications = query.offset(skip).limit(limit).all()
    return [RentalApplicationResponse.model_validate(app) for app in applications]

@router.get("/property/{property_id}", response_model=List[RentalApplicationResponse])
async def get_property_applications(
    property_id: int,
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    status_filter: Optional[ApplicationStatus] = None,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get applications for a specific property (property owner or admin only)"""
    # Check if property exists
    property_obj = db.query(Property).filter(Property.id == property_id).first()
    if not property_obj:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Property not found"
        )
    
    # Check permissions
    if property_obj.owner_id != current_user.id and current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to view applications for this property"
        )
    
    query = db.query(RentalApplication).filter(RentalApplication.property_id == property_id)
    
    if status_filter:
        query = query.filter(RentalApplication.status == status_filter.value)
    
    applications = query.offset(skip).limit(limit).all()
    return [RentalApplicationResponse.model_validate(app) for app in applications]

@router.get("/{application_id}", response_model=RentalApplicationResponse)
async def get_application(
    application_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get a specific application (applicant or property owner only)"""
    application = db.query(RentalApplication).filter(RentalApplication.id == application_id).first()
    if not application:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Application not found"
        )
    
    # Check permissions
    if (application.tenant_id != current_user.id and 
        application.property.owner_id != current_user.id and 
        current_user.role != "admin"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to view this application"
        )
    
    return RentalApplicationResponse.model_validate(application)

@router.put("/{application_id}/status", response_model=RentalApplicationResponse)
async def update_application_status(
    application_id: int,
    status_update: ApplicationStatus,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Update application status (property owner or admin only)"""
    application = db.query(RentalApplication).filter(RentalApplication.id == application_id).first()
    if not application:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Application not found"
        )
    
    # Check permissions
    if (application.property.owner_id != current_user.id and current_user.role != "admin"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to update this application"
        )
    
    # Update status
    application.status = status_update.value
    
    # If approved, mark property as unavailable and reject other pending applications
    if status_update == ApplicationStatus.APPROVED:
        application.property.is_available = False
        
        # Reject other pending applications for this property
        other_applications = db.query(RentalApplication).filter(
            RentalApplication.property_id == application.property_id,
            RentalApplication.id != application_id,
            RentalApplication.status == "pending"
        ).all()
        
        for other_app in other_applications:
            other_app.status = "rejected"
    
    db.commit()
    db.refresh(application)
    
    return RentalApplicationResponse.model_validate(application)

@router.delete("/{application_id}", response_model=MessageResponse)
async def delete_application(
    application_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Delete an application (applicant only, and only if pending)"""
    application = db.query(RentalApplication).filter(RentalApplication.id == application_id).first()
    if not application:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Application not found"
        )
    
    # Check permissions
    if application.tenant_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to delete this application"
        )
    
    # Can only delete pending applications
    if application.status != "pending":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Can only delete pending applications"
        )
    
    db.delete(application)
    db.commit()
    
    return {"message": "Application deleted successfully"}
