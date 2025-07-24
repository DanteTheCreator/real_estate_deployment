from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException, Request, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy import text
from database import Base, engine, SessionLocal
from config import settings
from routers import auth, properties, applications, upload
import time
import psutil
import logging
from datetime import datetime

# Configure logging for production
if settings.is_production():
    logging.basicConfig(
        level=getattr(logging, settings.log_level),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('/app/logs/app.log'),
            logging.StreamHandler()
        ]
    )
else:
    logging.basicConfig(level=logging.DEBUG)

logger = logging.getLogger(__name__)

# Import security middleware for production
if settings.is_production():
    try:
        from security import SecurityMiddleware, limiter, rate_limit_handler
        from slowapi.errors import RateLimitExceeded
        SECURITY_ENABLED = True
    except ImportError:
        logger.warning("Security middleware not available")
        SECURITY_ENABLED = False
else:
    SECURITY_ENABLED = False

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

# Create FastAPI app with production settings
app = FastAPI(
    title=settings.app_name,
    version=settings.version,
    description="A comprehensive house rental management API - Production Ready",
    lifespan=lifespan,
    docs_url="/docs" if not settings.is_production() else None,  # Disable docs in production
    redoc_url="/redoc" if not settings.is_production() else None,
    openapi_url="/openapi.json" if not settings.is_production() else None
)

# Add security middleware for production
if SECURITY_ENABLED:
    app.add_middleware(SecurityMiddleware)
    app.state.limiter = limiter
    app.add_exception_handler(RateLimitExceeded, rate_limit_handler)

# Add CORS middleware with restricted origins for production
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.get_cors_origins(),
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"] if settings.is_production() else ["*"],
    allow_headers=["Authorization", "Content-Type", "X-Requested-With"] if settings.is_production() else ["*"],
    expose_headers=["X-Total-Count"] if settings.is_production() else []
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

# Enhanced health check endpoint for production
@app.get("/health")
async def health_check():
    """Comprehensive health check endpoint"""
    try:
        health_status = {
            "status": "healthy",
            "timestamp": datetime.utcnow().isoformat(),
            "version": settings.version,
            "environment": settings.environment
        }
        
        # Check database connection
        try:
            db = SessionLocal()
            db.execute(text("SELECT 1"))
            db.close()
            health_status["database"] = "connected"
        except Exception as e:
            health_status["database"] = "disconnected"
            health_status["database_error"] = str(e)
            health_status["status"] = "unhealthy"
        
        # Check system resources (only in production monitoring)
        if settings.monitoring_enabled:
            try:
                health_status["system"] = {
                    "cpu_percent": psutil.cpu_percent(interval=1),
                    "memory_percent": psutil.virtual_memory().percent,
                    "disk_percent": psutil.disk_usage('/').percent
                }
            except Exception:
                pass  # System metrics not critical
        
        # Return appropriate status code
        status_code = 200 if health_status["status"] == "healthy" else 503
        return JSONResponse(content=health_status, status_code=status_code)
        
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return JSONResponse(
            content={
                "status": "unhealthy",
                "timestamp": datetime.utcnow().isoformat(),
                "error": "Health check failed"
            },
            status_code=503
        )

# Startup check endpoint (for container orchestration)
@app.get("/ready")
async def readiness_check():
    """Readiness check for container orchestration"""
    try:
        # Check if app is ready to serve requests
        db = SessionLocal()
        db.execute(text("SELECT 1"))
        db.close()
        return {"status": "ready", "timestamp": datetime.utcnow().isoformat()}
    except Exception:
        return JSONResponse(
            content={"status": "not ready", "timestamp": datetime.utcnow().isoformat()},
            status_code=503
        )

# Metrics endpoint (protected in production)
@app.get("/metrics")
async def metrics():
    """Basic metrics endpoint"""
    if settings.is_production():
        # In production, this should be protected or use proper monitoring tools
        return {"message": "Metrics available through monitoring tools"}
    
    try:
        return {
            "timestamp": datetime.utcnow().isoformat(),
            "uptime": time.time() - app.state.start_time if hasattr(app.state, 'start_time') else 0,
            "requests_count": getattr(app.state, 'requests_count', 0),
            "system": {
                "cpu_percent": psutil.cpu_percent(),
                "memory_percent": psutil.virtual_memory().percent,
                "disk_percent": psutil.disk_usage('/').percent
            }
        }
    except Exception:
        return {"error": "Metrics not available"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.debug
    )