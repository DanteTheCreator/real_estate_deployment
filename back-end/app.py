from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from database import Base, engine, SessionLocal
from config import settings
from routers import auth, properties, applications, upload

async def seed_initial_data():
    """Seed the database with initial amenities"""
    from database import Amenity
    
    db = SessionLocal()
    try:
        # Create default amenities if they don't exist
        default_amenities = [
            {"name": "WiFi", "description": "High-speed internet access", "icon": "wifi", "category": "utilities"},
            {"name": "Parking", "description": "Dedicated parking space", "icon": "car", "category": "utilities"},
            {"name": "Air Conditioning", "description": "Central air conditioning", "icon": "snowflake", "category": "utilities"},
            {"name": "Heating", "description": "Central heating system", "icon": "fire", "category": "utilities"},
            {"name": "Washer/Dryer", "description": "In-unit laundry facilities", "icon": "tshirt", "category": "appliances"},
            {"name": "Dishwasher", "description": "Built-in dishwasher", "icon": "utensils", "category": "appliances"},
            {"name": "Swimming Pool", "description": "Access to swimming pool", "icon": "swimmer", "category": "recreation"},
            {"name": "Gym/Fitness Center", "description": "On-site fitness facilities", "icon": "dumbbell", "category": "recreation"},
            {"name": "Pet Friendly", "description": "Pets are welcome", "icon": "paw", "category": "policies"},
            {"name": "Balcony/Patio", "description": "Private outdoor space", "icon": "tree", "category": "features"},
            {"name": "Garden", "description": "Access to garden area", "icon": "leaf", "category": "features"},
            {"name": "Security System", "description": "24/7 security monitoring", "icon": "shield", "category": "security"},
        ]
        
        for amenity_data in default_amenities:
            existing = db.query(Amenity).filter(Amenity.name == amenity_data["name"]).first()
            if not existing:
                amenity = Amenity(**amenity_data)
                db.add(amenity)
        
        db.commit()
        print("✅ Initial amenities seeded successfully")
        
    except Exception as e:
        print(f"❌ Error seeding amenities: {e}")
        db.rollback()
    finally:
        db.close()

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager for startup and shutdown events"""
    # Startup
    try:
        # Create database tables
        Base.metadata.create_all(bind=engine)
        print("✅ Database tables created successfully")
        
        # Seed initial data
        await seed_initial_data()
        
    except Exception as e:
        print(f"❌ Error during startup: {e}")
    
    yield
    
    # Shutdown (if needed)
    print("🔄 Application shutting down...")

# Create FastAPI app
app = FastAPI(
    title=settings.app_name,
    version=settings.version,
    description="A comprehensive house rental management API",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.get_cors_origins(),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router, prefix="/api")
app.include_router(properties.router, prefix="/api")
app.include_router(applications.router, prefix="/api")
app.include_router(upload.router, prefix="/api")

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "House Rental API",
        "version": settings.version,
        "docs": "/docs"
    }

# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "message": "House Rental API is running"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.debug
    )