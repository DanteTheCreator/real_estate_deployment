#!/usr/bin/env python3
"""
PostgreSQL Database Setup Script for House Rental API

This script creates the PostgreSQL database and tables for the house rental application.
Make sure PostgreSQL is installed and running before executing this script.
"""

import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
import sys
import os
from sqlalchemy import create_engine
from database import Base
from config import settings

def create_database():
    """Create the PostgreSQL database if it doesn't exist"""
    # Parse database URL to get connection parameters
    db_url = settings.database_url
    if not db_url.startswith('postgresql://'):
        print("❌ DATABASE_URL must be a PostgreSQL URL")
        return False
    
    # Parse the database URL to extract connection parameters
    from urllib.parse import urlparse
    parsed = urlparse(db_url)
    
    db_name = parsed.path.lstrip('/')
    host = parsed.hostname or 'localhost'
    port = parsed.port or 5432
    user = parsed.username
    password = parsed.password or ''
    
    try:
        # Connect to PostgreSQL server (to default postgres database)
        print("🔗 Connecting to PostgreSQL server...")
        conn_params = {
            'host': host,
            'port': port,
            'user': user,
            'database': 'postgres'  # Connect to default postgres database
        }
        if password:
            conn_params['password'] = password
            
        conn = psycopg2.connect(**conn_params)
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cursor = conn.cursor()
        
        # Check if database exists
        cursor.execute("SELECT 1 FROM pg_catalog.pg_database WHERE datname = %s", (db_name,))
        exists = cursor.fetchone()
        
        if not exists:
            print(f"📊 Creating database '{db_name}'...")
            cursor.execute(f'CREATE DATABASE "{db_name}"')
            print(f"✅ Database '{db_name}' created successfully!")
        else:
            print(f"ℹ️  Database '{db_name}' already exists.")
        
        cursor.close()
        conn.close()
        return True
        
    except psycopg2.Error as e:
        print(f"❌ Error creating database: {e}")
        return False

def create_tables():
    """Create all tables using SQLAlchemy"""
    try:
        print("🔗 Connecting to the house rental database...")
        engine = create_engine(settings.database_url)
        
        print("📋 Creating tables...")
        Base.metadata.create_all(bind=engine)
        print("✅ All tables created successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Error creating tables: {e}")
        return False

def seed_initial_data():
    """Seed the database with initial amenities"""
    try:
        from database import SessionLocal, Amenity
        
        print("🌱 Seeding initial data...")
        db = SessionLocal()
        
        # Default amenities
        default_amenities = [
            {"name": "WiFi", "description": "High-speed internet access", "icon": "wifi", "category": "utilities"},
            {"name": "Parking", "description": "Dedicated parking space", "icon": "car", "category": "utilities"},
            {"name": "Air Conditioning", "description": "Central air conditioning", "icon": "snowflake", "category": "utilities"},
            {"name": "Heating", "description": "Central heating system", "icon": "fire", "category": "utilities"},
            {"name": "Washer/Dryer", "description": "In-unit laundry facilities", "icon": "tshirt", "category": "appliances"},
            {"name": "Dishwasher", "description": "Built-in dishwasher", "icon": "utensils", "category": "appliances"},
            {"name": "Microwave", "description": "Built-in microwave oven", "icon": "microwave", "category": "appliances"},
            {"name": "Refrigerator", "description": "Full-size refrigerator", "icon": "refrigerator", "category": "appliances"},
            {"name": "Swimming Pool", "description": "Access to swimming pool", "icon": "swimmer", "category": "recreation"},
            {"name": "Gym/Fitness Center", "description": "On-site fitness facilities", "icon": "dumbbell", "category": "recreation"},
            {"name": "Pet Friendly", "description": "Pets are welcome", "icon": "paw", "category": "policies"},
            {"name": "Balcony/Patio", "description": "Private outdoor space", "icon": "tree", "category": "features"},
            {"name": "Garden", "description": "Access to garden area", "icon": "leaf", "category": "features"},
            {"name": "Security System", "description": "24/7 security monitoring", "icon": "shield", "category": "security"},
            {"name": "Doorman", "description": "24/7 doorman service", "icon": "user-tie", "category": "security"},
            {"name": "Elevator", "description": "Elevator access", "icon": "elevator", "category": "features"},
            {"name": "Hardwood Floors", "description": "Beautiful hardwood flooring", "icon": "floor", "category": "features"},
            {"name": "Walk-in Closet", "description": "Spacious walk-in closet", "icon": "closet", "category": "features"},
        ]
        
        for amenity_data in default_amenities:
            existing = db.query(Amenity).filter(Amenity.name == amenity_data["name"]).first()
            if not existing:
                amenity = Amenity(**amenity_data)
                db.add(amenity)
        
        db.commit()
        db.close()
        print("✅ Initial amenities seeded successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Error seeding data: {e}")
        return False

def main():
    """Main setup function"""
    print("🏠 House Rental API - Database Setup")
    print("=" * 40)
    
    # Step 1: Create database
    if not create_database():
        print("❌ Failed to create database. Please check your PostgreSQL configuration.")
        sys.exit(1)
    
    # Step 2: Create tables
    if not create_tables():
        print("❌ Failed to create tables.")
        sys.exit(1)
    
    # Step 3: Seed initial data
    if not seed_initial_data():
        print("❌ Failed to seed initial data.")
        sys.exit(1)
    
    print("\n🎉 Database setup completed successfully!")
    print("📝 Next steps:")
    print("   1. Update your DATABASE_URL in the .env file with correct credentials")
    print("   2. Run: uvicorn app:app --reload")
    print("   3. Visit: http://localhost:8000/docs for API documentation")

if __name__ == "__main__":
    main()
