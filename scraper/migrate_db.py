#!/usr/bin/env python3
"""
Migration script to add scraper-specific columns to the properties table
Run this before using the scraper database integration
"""

import sys
from pathlib import Path
from sqlalchemy import create_engine, text, Column, String, Float, Integer, DateTime
from sqlalchemy.exc import SQLAlchemyError
import logging

# Add backend directory to path
backend_path = Path(__file__).parent.parent / "back-end"
sys.path.append(str(backend_path))

from config import settings

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def run_migration():
    """Add new columns to properties table for scraper integration"""
    
    engine = create_engine(settings.database_url)
    
    # List of new columns to add
    new_columns = [
        "ALTER TABLE properties ADD COLUMN IF NOT EXISTS district VARCHAR(100);",
        "ALTER TABLE properties ADD COLUMN IF NOT EXISTS urban_area VARCHAR(100);",
        "ALTER TABLE properties ADD COLUMN IF NOT EXISTS latitude FLOAT;",
        "ALTER TABLE properties ADD COLUMN IF NOT EXISTS longitude FLOAT;",
        "ALTER TABLE properties ADD COLUMN IF NOT EXISTS floor_number INTEGER;",
        "ALTER TABLE properties ADD COLUMN IF NOT EXISTS total_floors INTEGER;",
        "ALTER TABLE properties ADD COLUMN IF NOT EXISTS external_id VARCHAR(50);",
        "ALTER TABLE properties ADD COLUMN IF NOT EXISTS source VARCHAR(50);",
        "ALTER TABLE properties ADD COLUMN IF NOT EXISTS user_type VARCHAR(50);",
        "ALTER TABLE properties ADD COLUMN IF NOT EXISTS last_scraped TIMESTAMP WITH TIME ZONE;",
        
        # Create index on external_id for faster lookups
        "CREATE INDEX IF NOT EXISTS idx_properties_external_id ON properties(external_id);",
        "CREATE INDEX IF NOT EXISTS idx_properties_source ON properties(source);",
        "CREATE INDEX IF NOT EXISTS idx_properties_location ON properties(latitude, longitude);",
    ]
    
    try:
        with engine.connect() as conn:
            for sql in new_columns:
                try:
                    conn.execute(text(sql))
                    conn.commit()
                    logger.info(f"Executed: {sql}")
                except SQLAlchemyError as e:
                    logger.warning(f"Failed to execute {sql}: {e}")
                    
        logger.info("Migration completed successfully!")
        return True
        
    except Exception as e:
        logger.error(f"Migration failed: {e}")
        return False

if __name__ == "__main__":
    if run_migration():
        print("✅ Database migration completed successfully!")
    else:
        print("❌ Database migration failed!")
        sys.exit(1)
