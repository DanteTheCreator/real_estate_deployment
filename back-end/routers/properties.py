from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import and_, or_
from typing import List, Optional
from database import get_db, Property, User, Amenity, PropertyImage, property_amenities, saved_properties
from schemas import (
    PropertyCreate, PropertyUpdate, PropertyResponse, PropertyListResponse,
    AmenityResponse, PropertySearchFilters, MessageResponse,
    PropertyImageCreate, PropertyImageResponse, PropertyImageUpdate,
    PropertyType
)
from auth import get_current_active_user, require_landlord

router = APIRouter(prefix="/properties", tags=["Properties"])

@router.get("/", response_model=List[PropertyListResponse])
async def get_properties(
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    city: Optional[str] = None,
    state: Optional[str] = None,
    property_type: Optional[str] = None,
    min_rent: Optional[float] = Query(None, ge=0),
    max_rent: Optional[float] = Query(None, ge=0),
    min_bedrooms: Optional[int] = Query(None, ge=0),
    max_bedrooms: Optional[int] = Query(None, ge=0),
    pets_allowed: Optional[bool] = None,
    is_furnished: Optional[bool] = None,
    db: Session = Depends(get_db)
):
    """Get all available properties with filtering"""
    query = db.query(Property).options(joinedload(Property.images)).filter(Property.is_available == True)
    
    # Apply filters
    if city:
        query = query.filter(Property.city.ilike(f"%{city}%"))
    if state:
        query = query.filter(Property.state.ilike(f"%{state}%"))
    if property_type:
        query = query.filter(Property.property_type == property_type)
    if min_rent is not None:
        query = query.filter(Property.rent_amount >= min_rent)
    if max_rent is not None:
        query = query.filter(Property.rent_amount <= max_rent)
    if min_bedrooms is not None:
        query = query.filter(Property.bedrooms >= min_bedrooms)
    if max_bedrooms is not None:
        query = query.filter(Property.bedrooms <= max_bedrooms)
    if pets_allowed is not None:
        query = query.filter(Property.pets_allowed == pets_allowed)
    if is_furnished is not None:
        query = query.filter(Property.is_furnished == is_furnished)
    
    properties = query.offset(skip).limit(limit).all()
    return [PropertyListResponse.model_validate(prop) for prop in properties]

@router.get("/search", response_model=List[PropertyListResponse])
async def search_properties(
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    query: Optional[str] = Query(None, description="General search query"),
    city: Optional[str] = Query(None, description="City filter"),
    state: Optional[str] = Query(None, description="State filter"),
    property_type: Optional[str] = Query(None, description="Property type filter"),
    listing_type: Optional[str] = Query(None, description="Listing type filter (rent, sale, lease, daily, mortgage)"),
    min_bedrooms: Optional[int] = Query(None, ge=0, description="Minimum bedrooms"),
    max_bedrooms: Optional[int] = Query(None, ge=0, description="Maximum bedrooms"),
    min_bathrooms: Optional[float] = Query(None, ge=0, description="Minimum bathrooms"),
    max_bathrooms: Optional[float] = Query(None, ge=0, description="Maximum bathrooms"),
    min_rent: Optional[float] = Query(None, ge=0, description="Minimum rent"),
    max_rent: Optional[float] = Query(None, ge=0, description="Maximum rent"),
    min_square_feet: Optional[int] = Query(None, ge=0, description="Minimum square feet"),
    max_square_feet: Optional[int] = Query(None, ge=0, description="Maximum square feet"),
    pets_allowed: Optional[bool] = Query(None, description="Pets allowed filter"),
    is_furnished: Optional[bool] = Query(None, description="Furnished filter"),
    smoking_allowed: Optional[bool] = Query(None, description="Smoking allowed filter"),
    year_built_min: Optional[int] = Query(None, ge=1800, le=2030, description="Minimum year built"),
    year_built_max: Optional[int] = Query(None, ge=1800, le=2030, description="Maximum year built"),
    parking_spaces_min: Optional[int] = Query(None, ge=0, description="Minimum parking spaces"),
    currency: Optional[str] = Query("GEL", description="Currency for price filtering (GEL or USD)"),
    sort_by: Optional[str] = Query("date", description="Sort by field"),
    sort_order: Optional[str] = Query("desc", description="Sort order (asc/desc)"),
    db: Session = Depends(get_db)
):
    """Search properties with advanced filters"""
    query_obj = db.query(Property).options(joinedload(Property.images)).filter(Property.is_available == True)
    
    # General search query (search in title, description, address)
    if query:
        search_filter = or_(
            Property.title.ilike(f"%{query}%"),
            Property.description.ilike(f"%{query}%"),
            Property.address.ilike(f"%{query}%"),
            Property.city.ilike(f"%{query}%"),
            Property.state.ilike(f"%{query}%")
        )
        query_obj = query_obj.filter(search_filter)
    
    # Location filters
    if city:
        query_obj = query_obj.filter(Property.city.ilike(f"%{city}%"))
    if state:
        query_obj = query_obj.filter(Property.state.ilike(f"%{state}%"))
    
    # Property type filter
    if property_type:
        query_obj = query_obj.filter(Property.property_type == property_type)
    
    # Listing type filter
    if listing_type:
        query_obj = query_obj.filter(Property.listing_type == listing_type)
    
    # Bedroom filters
    if min_bedrooms is not None:
        query_obj = query_obj.filter(Property.bedrooms >= min_bedrooms)
    if max_bedrooms is not None:
        query_obj = query_obj.filter(Property.bedrooms <= max_bedrooms)
    
    # Bathroom filters
    if min_bathrooms is not None:
        query_obj = query_obj.filter(Property.bathrooms >= min_bathrooms)
    if max_bathrooms is not None:
        query_obj = query_obj.filter(Property.bathrooms <= max_bathrooms)
    
    # Price filters
    if min_rent is not None:
        query_obj = query_obj.filter(Property.rent_amount >= min_rent)
    if max_rent is not None:
        query_obj = query_obj.filter(Property.rent_amount <= max_rent)
    
    # Area filters
    if min_square_feet is not None:
        query_obj = query_obj.filter(Property.square_feet >= min_square_feet)
    if max_square_feet is not None:
        query_obj = query_obj.filter(Property.square_feet <= max_square_feet)
    
    # Feature filters
    if pets_allowed is not None:
        query_obj = query_obj.filter(Property.pets_allowed == pets_allowed)
    if is_furnished is not None:
        query_obj = query_obj.filter(Property.is_furnished == is_furnished)
    if smoking_allowed is not None:
        query_obj = query_obj.filter(Property.smoking_allowed == smoking_allowed)
    
    # Year built filters
    if year_built_min is not None:
        query_obj = query_obj.filter(Property.year_built >= year_built_min)
    if year_built_max is not None:
        query_obj = query_obj.filter(Property.year_built <= year_built_max)
    
    # Parking filter
    if parking_spaces_min is not None:
        query_obj = query_obj.filter(Property.parking_spaces >= parking_spaces_min)
    
    # Sorting
    if sort_by == "price":
        order_field = Property.rent_amount
    elif sort_by == "area":
        order_field = Property.square_feet
    elif sort_by == "bedrooms":
        order_field = Property.bedrooms
    else:  # default to date
        order_field = Property.created_at
    
    if sort_order == "asc":
        query_obj = query_obj.order_by(order_field.asc())
    else:
        query_obj = query_obj.order_by(order_field.desc())
    
    properties = query_obj.offset(skip).limit(limit).all()
    return [PropertyListResponse.model_validate(prop) for prop in properties]

@router.get("/count")
async def get_properties_count(
    city: Optional[str] = None,
    state: Optional[str] = None,
    property_type: Optional[str] = None,
    min_rent: Optional[float] = Query(None, ge=0),
    max_rent: Optional[float] = Query(None, ge=0),
    min_bedrooms: Optional[int] = Query(None, ge=0),
    max_bedrooms: Optional[int] = Query(None, ge=0),
    pets_allowed: Optional[bool] = None,
    is_furnished: Optional[bool] = None,
    currency: Optional[str] = Query("GEL", description="Currency for price filtering (GEL or USD)"),
    db: Session = Depends(get_db)
):
    """Get count of available properties with filtering"""
    query = db.query(Property).filter(Property.is_available == True)
    
    # Apply same filters as get_properties
    if city:
        query = query.filter(Property.city.ilike(f"%{city}%"))
    if state:
        query = query.filter(Property.state.ilike(f"%{state}%"))
    if property_type:
        query = query.filter(Property.property_type == property_type)
    
    # Price filters - handle currency selection
    if min_rent is not None or max_rent is not None:
        if currency and currency.upper() == "USD":
            # Filter by USD amount
            if min_rent is not None:
                query = query.filter(
                    or_(
                        Property.rent_amount_usd >= min_rent,
                        and_(Property.rent_amount_usd.is_(None), Property.rent_amount >= min_rent * 2.7)
                    )
                )
            if max_rent is not None:
                query = query.filter(
                    or_(
                        Property.rent_amount_usd <= max_rent,
                        and_(Property.rent_amount_usd.is_(None), Property.rent_amount <= max_rent * 2.7)
                    )
                )
        else:
            # Filter by GEL amount (default)
            if min_rent is not None:
                query = query.filter(Property.rent_amount >= min_rent)
            if max_rent is not None:
                query = query.filter(Property.rent_amount <= max_rent)
    
    if min_bedrooms is not None:
        query = query.filter(Property.bedrooms >= min_bedrooms)
    if max_bedrooms is not None:
        query = query.filter(Property.bedrooms <= max_bedrooms)
    if pets_allowed is not None:
        query = query.filter(Property.pets_allowed == pets_allowed)
    if is_furnished is not None:
        query = query.filter(Property.is_furnished == is_furnished)
    
    total_count = query.count()
    return {"total_count": total_count}

@router.get("/search/count")
async def get_search_count(
    query: Optional[str] = Query(None, description="General search query"),
    city: Optional[str] = Query(None, description="City filter"),
    state: Optional[str] = Query(None, description="State filter"),
    property_type: Optional[str] = Query(None, description="Property type filter"),
    listing_type: Optional[str] = Query(None, description="Listing type filter (rent, sale, lease, daily, mortgage)"),
    min_bedrooms: Optional[int] = Query(None, ge=0, description="Minimum bedrooms"),
    max_bedrooms: Optional[int] = Query(None, ge=0, description="Maximum bedrooms"),
    min_bathrooms: Optional[float] = Query(None, ge=0, description="Minimum bathrooms"),
    max_bathrooms: Optional[float] = Query(None, ge=0, description="Maximum bathrooms"),
    min_rent: Optional[float] = Query(None, ge=0, description="Minimum rent"),
    max_rent: Optional[float] = Query(None, ge=0, description="Maximum rent"),
    min_square_feet: Optional[int] = Query(None, ge=0, description="Minimum square feet"),
    max_square_feet: Optional[int] = Query(None, ge=0, description="Maximum square feet"),
    pets_allowed: Optional[bool] = Query(None, description="Pets allowed filter"),
    is_furnished: Optional[bool] = Query(None, description="Furnished filter"),
    smoking_allowed: Optional[bool] = Query(None, description="Smoking allowed filter"),
    year_built_min: Optional[int] = Query(None, ge=1800, le=2030, description="Minimum year built"),
    year_built_max: Optional[int] = Query(None, ge=1800, le=2030, description="Maximum year built"),
    parking_spaces_min: Optional[int] = Query(None, ge=0, description="Minimum parking spaces"),
    currency: Optional[str] = Query("GEL", description="Currency for price filtering (GEL or USD)"),
    db: Session = Depends(get_db)
):
    """Get count of search results with advanced filters"""
    query_obj = db.query(Property).filter(Property.is_available == True)
    
    # Apply same filters as search_properties
    if query:
        search_filter = or_(
            Property.title.ilike(f"%{query}%"),
            Property.description.ilike(f"%{query}%"),
            Property.address.ilike(f"%{query}%"),
            Property.city.ilike(f"%{query}%"),
            Property.state.ilike(f"%{query}%")
        )
        query_obj = query_obj.filter(search_filter)
    
    if city:
        query_obj = query_obj.filter(Property.city.ilike(f"%{city}%"))
    if state:
        query_obj = query_obj.filter(Property.state.ilike(f"%{state}%"))
    if property_type:
        query_obj = query_obj.filter(Property.property_type == property_type)
    if listing_type:
        query_obj = query_obj.filter(Property.listing_type == listing_type)
    if min_bedrooms is not None:
        query_obj = query_obj.filter(Property.bedrooms >= min_bedrooms)
    if max_bedrooms is not None:
        query_obj = query_obj.filter(Property.bedrooms <= max_bedrooms)
    if min_bathrooms is not None:
        query_obj = query_obj.filter(Property.bathrooms >= min_bathrooms)
    if max_bathrooms is not None:
        query_obj = query_obj.filter(Property.bathrooms <= max_bathrooms)
    
    # Price filters - handle currency selection
    if min_rent is not None or max_rent is not None:
        if currency and currency.upper() == "USD":
            # Filter by USD amount
            if min_rent is not None:
                query_obj = query_obj.filter(
                    or_(
                        Property.rent_amount_usd >= min_rent,
                        and_(Property.rent_amount_usd.is_(None), Property.rent_amount >= min_rent * 2.7)
                    )
                )
            if max_rent is not None:
                query_obj = query_obj.filter(
                    or_(
                        Property.rent_amount_usd <= max_rent,
                        and_(Property.rent_amount_usd.is_(None), Property.rent_amount <= max_rent * 2.7)
                    )
                )
        else:
            # Filter by GEL amount (default)
            if min_rent is not None:
                query_obj = query_obj.filter(Property.rent_amount >= min_rent)
            if max_rent is not None:
                query_obj = query_obj.filter(Property.rent_amount <= max_rent)
    if min_square_feet is not None:
        query_obj = query_obj.filter(Property.square_feet >= min_square_feet)
    if max_square_feet is not None:
        query_obj = query_obj.filter(Property.square_feet <= max_square_feet)
    if pets_allowed is not None:
        query_obj = query_obj.filter(Property.pets_allowed == pets_allowed)
    if is_furnished is not None:
        query_obj = query_obj.filter(Property.is_furnished == is_furnished)
    if smoking_allowed is not None:
        query_obj = query_obj.filter(Property.smoking_allowed == smoking_allowed)
    if year_built_min is not None:
        query_obj = query_obj.filter(Property.year_built >= year_built_min)
    if year_built_max is not None:
        query_obj = query_obj.filter(Property.year_built <= year_built_max)
    if parking_spaces_min is not None:
        query_obj = query_obj.filter(Property.parking_spaces >= parking_spaces_min)
    
    total_count = query_obj.count()
    return {"total_count": total_count}

@router.get("/saved", response_model=List[PropertyListResponse])
async def get_saved_properties(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get user's saved properties"""
    saved_props = db.query(Property).join(
        saved_properties,
        Property.id == saved_properties.c.property_id
    ).filter(
        saved_properties.c.user_id == current_user.id
    ).options(joinedload(Property.images)).all()
    
    return [
        PropertyListResponse(
            id=prop.id,
            title=prop.title,
            address=prop.address,
            city=prop.city,
            state=prop.state,
            zip_code=prop.zip_code,
            property_type=PropertyType(prop.property_type),
            bedrooms=prop.bedrooms,
            bathrooms=prop.bathrooms,
            rent_amount=prop.rent_amount,
            is_available=prop.is_available,
            images=[
                PropertyImageResponse(
                    id=img.id,
                    property_id=img.property_id,
                    image_url=img.image_url,
                    caption=img.caption,
                    is_primary=img.is_primary,
                    created_at=img.created_at
                ) for img in prop.images
            ],
            created_at=prop.created_at
        ) for prop in saved_props
    ]

@router.get("/{property_id}", response_model=PropertyResponse)
async def get_property(property_id: int, db: Session = Depends(get_db)):
    """Get a specific property by ID"""
    property_obj = db.query(Property).options(
        joinedload(Property.images),
        joinedload(Property.amenities)
    ).filter(Property.id == property_id).first()
    if not property_obj:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Property not found"
        )
    return PropertyResponse.model_validate(property_obj)

@router.post("/", response_model=PropertyResponse, status_code=status.HTTP_201_CREATED)
async def create_property(
    property_data: PropertyCreate,
    current_user: User = Depends(require_landlord),
    db: Session = Depends(get_db)
):
    """Create a new property (any authenticated user)"""
    # Create property
    property_dict = property_data.dict(exclude={"amenity_ids"})
    db_property = Property(**property_dict, owner_id=current_user.id)
    
    db.add(db_property)
    db.commit()
    db.refresh(db_property)
    
    # Add amenities if provided
    if property_data.amenity_ids:
        for amenity_id in property_data.amenity_ids:
            amenity = db.query(Amenity).filter(Amenity.id == amenity_id).first()
            if amenity:
                db_property.amenities.append(amenity)
        db.commit()
        db.refresh(db_property)
    
    return PropertyResponse.model_validate(db_property)

@router.put("/{property_id}", response_model=PropertyResponse)
async def update_property(
    property_id: int,
    property_update: PropertyUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Update a property (owner or admin only)"""
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
            detail="Not authorized to update this property"
        )
    
    # Update property
    update_data = property_update.dict(exclude_unset=True, exclude={"amenity_ids"})
    for field, value in update_data.items():
        setattr(property_obj, field, value)
    
    # Update amenities if provided
    if property_update.amenity_ids is not None:
        property_obj.amenities.clear()
        for amenity_id in property_update.amenity_ids:
            amenity = db.query(Amenity).filter(Amenity.id == amenity_id).first()
            if amenity:
                property_obj.amenities.append(amenity)
    
    db.commit()
    db.refresh(property_obj)
    
    return PropertyResponse.model_validate(property_obj)

@router.delete("/{property_id}", response_model=MessageResponse)
async def delete_property(
    property_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Delete a property (owner or admin only)"""
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
            detail="Not authorized to delete this property"
        )
    
    db.delete(property_obj)
    db.commit()
    
    return {"message": "Property deleted successfully"}

@router.get("/my-properties/", response_model=List[PropertyListResponse])
async def get_my_properties(
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    current_user: User = Depends(require_landlord),
    db: Session = Depends(get_db)
):
    """Get current user's properties"""
    properties = db.query(Property).options(joinedload(Property.images)).filter(
        Property.owner_id == current_user.id
    ).offset(skip).limit(limit).all()
    
    return [PropertyListResponse.model_validate(prop) for prop in properties]

@router.get("/amenities/", response_model=List[AmenityResponse])
async def get_amenities(db: Session = Depends(get_db)):
    """Get all available amenities"""
    amenities = db.query(Amenity).all()
    return [AmenityResponse.model_validate(amenity) for amenity in amenities]

# Property Image endpoints
@router.post("/{property_id}/images", response_model=PropertyImageResponse, status_code=status.HTTP_201_CREATED)
async def add_property_image(
    property_id: int,
    image_data: PropertyImageCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Add an image to a property (owner or admin only)"""
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
            detail="Not authorized to add images to this property"
        )
    
    # If this is marked as primary, unset other primary images
    if image_data.is_primary:
        db.query(PropertyImage).filter(
            PropertyImage.property_id == property_id,
            PropertyImage.is_primary == True
        ).update({"is_primary": False})
    
    # Create image
    db_image = PropertyImage(**image_data.dict(), property_id=property_id)
    db.add(db_image)
    db.commit()
    db.refresh(db_image)
    
    return PropertyImageResponse.model_validate(db_image)

@router.get("/{property_id}/images", response_model=List[PropertyImageResponse])
async def get_property_images(property_id: int, db: Session = Depends(get_db)):
    """Get all images for a property"""
    property_obj = db.query(Property).filter(Property.id == property_id).first()
    if not property_obj:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Property not found"
        )
    
    images = db.query(PropertyImage).filter(
        PropertyImage.property_id == property_id
    ).order_by(PropertyImage.is_primary.desc(), PropertyImage.order_index).all()
    
    return [PropertyImageResponse.model_validate(img) for img in images]

@router.put("/{property_id}/images/{image_id}", response_model=PropertyImageResponse)
async def update_property_image(
    property_id: int,
    image_id: int,
    image_update: PropertyImageUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Update a property image (owner or admin only)"""
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
            detail="Not authorized to update images for this property"
        )
    
    image_obj = db.query(PropertyImage).filter(
        PropertyImage.id == image_id,
        PropertyImage.property_id == property_id
    ).first()
    if not image_obj:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Image not found"
        )
    
    # If setting as primary, unset other primary images
    if image_update.is_primary:
        db.query(PropertyImage).filter(
            PropertyImage.property_id == property_id,
            PropertyImage.is_primary == True,
            PropertyImage.id != image_id
        ).update({"is_primary": False})
    
    # Update image
    update_data = image_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(image_obj, field, value)
    
    db.commit()
    db.refresh(image_obj)
    
    return PropertyImageResponse.model_validate(image_obj)

@router.delete("/{property_id}/images/{image_id}", response_model=MessageResponse)
async def delete_property_image(
    property_id: int,
    image_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Delete a property image (owner or admin only)"""
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
            detail="Not authorized to delete images from this property"
        )
    
    image_obj = db.query(PropertyImage).filter(
        PropertyImage.id == image_id,
        PropertyImage.property_id == property_id
    ).first()
    if not image_obj:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Image not found"
        )
    
    db.delete(image_obj)
    db.commit()
    
    return {"message": "Image deleted successfully"}

@router.post("/{property_id}/save", response_model=MessageResponse)
async def save_property(
    property_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Save a property to user's favorites"""
    property_obj = db.query(Property).filter(Property.id == property_id).first()
    if not property_obj:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Property not found"
        )
    
    # Check if already saved
    existing_save = db.query(saved_properties).filter(
        and_(
            saved_properties.c.user_id == current_user.id,
            saved_properties.c.property_id == property_id
        )
    ).first()
    
    if existing_save:
        return {"message": "Property already saved"}
    
    # Add to saved properties
    insert_stmt = saved_properties.insert().values(
        user_id=current_user.id,
        property_id=property_id
    )
    db.execute(insert_stmt)
    db.commit()
    
    return {"message": "Property saved successfully"}


@router.post("/{property_id}/toggle-save", response_model=MessageResponse)
async def toggle_save_property(
    property_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Toggle save status of a property"""
    property_obj = db.query(Property).filter(Property.id == property_id).first()
    if not property_obj:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Property not found"
        )
    
    # Check if already saved
    existing_save = db.query(saved_properties).filter(
        and_(
            saved_properties.c.user_id == current_user.id,
            saved_properties.c.property_id == property_id
        )
    ).first()
    
    if existing_save:
        # Remove from saved properties
        delete_stmt = saved_properties.delete().where(
            and_(
                saved_properties.c.user_id == current_user.id,
                saved_properties.c.property_id == property_id
            )
        )
        db.execute(delete_stmt)
        db.commit()
        return {"message": "Property removed from saved list"}
    else:
        # Add to saved properties
        insert_stmt = saved_properties.insert().values(
            user_id=current_user.id,
            property_id=property_id
        )
        db.execute(insert_stmt)
        db.commit()
        return {"message": "Property saved successfully"}


@router.get("/{property_id}/is-saved", response_model=dict)
async def check_if_property_saved(
    property_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Check if a property is saved by the current user"""
    property_obj = db.query(Property).filter(Property.id == property_id).first()
    if not property_obj:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Property not found"
        )
    
    # Check if saved
    existing_save = db.query(saved_properties).filter(
        and_(
            saved_properties.c.user_id == current_user.id,
            saved_properties.c.property_id == property_id
        )
    ).first()
    
    return {"is_saved": existing_save is not None}

@router.delete("/{property_id}/save", response_model=MessageResponse)
async def unsave_property(
    property_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Remove a property from user's favorites"""
    property_obj = db.query(Property).filter(Property.id == property_id).first()
    if not property_obj:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Property not found"
        )
    
    # Check if property is saved
    existing_save = db.query(saved_properties).filter(
        and_(
            saved_properties.c.user_id == current_user.id,
            saved_properties.c.property_id == property_id
        )
    ).first()
    
    if not existing_save:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Property not in saved list"
        )
    
    # Remove from saved properties
    delete_stmt = saved_properties.delete().where(
        and_(
            saved_properties.c.user_id == current_user.id,
            saved_properties.c.property_id == property_id
        )
    )
    db.execute(delete_stmt)
    db.commit()
    
    return {"message": "Property removed from saved list"}
