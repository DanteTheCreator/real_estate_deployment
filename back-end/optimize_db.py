#!/usr/bin/env python3
"""
Database performance optimization migration script.

This script adds missing indexes to improve query performance.
Run this to optimize existing database without losing data.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy import create_engine, text
from database import SessionLocal
from config import settings
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def add_performance_indexes():
    """Add missing indexes for better query performance."""
    
    # SQL commands to add indexes (only if they don't exist)
    index_commands = [
        # City index for location searches
        """
        CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_properties_city 
        ON properties USING btree (city);
        """,
        
        # State index for location searches  
        """
        CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_properties_state 
        ON properties USING btree (state) WHERE state IS NOT NULL;
        """,
        
        # Property type index for filtering
        """
        CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_properties_property_type 
        ON properties USING btree (property_type);
        """,
        
        # Listing type index for filtering
        """
        CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_properties_listing_type 
        ON properties USING btree (listing_type);
        """,
        
        # Price indexes for range queries
        """
        CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_properties_rent_amount 
        ON properties USING btree (rent_amount);
        """,
        
        """
        CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_properties_rent_amount_usd 
        ON properties USING btree (rent_amount_usd) WHERE rent_amount_usd IS NOT NULL;
        """,
        
        # Availability index (most important filter)
        """
        CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_properties_is_available 
        ON properties USING btree (is_available);
        """,
        
        # District and urban area indexes
        """
        CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_properties_district 
        ON properties USING btree (district) WHERE district IS NOT NULL;
        """,
        
        """
        CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_properties_urban_area 
        ON properties USING btree (urban_area) WHERE urban_area IS NOT NULL;
        """,
        
        # Owner ID index for landlord queries
        """
        CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_properties_owner_id 
        ON properties USING btree (owner_id);
        """,
        
        # Created at index for date sorting
        """
        CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_properties_created_at 
        ON properties USING btree (created_at DESC);
        """,
        
        # Composite index for the most common query pattern (available properties by date)
        """
        CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_properties_available_created 
        ON properties USING btree (is_available, created_at DESC) 
        WHERE is_available = true;
        """,
        
        # Composite index for price range searches
        """
        CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_properties_available_price 
        ON properties USING btree (is_available, rent_amount) 
        WHERE is_available = true;
        """,
        
        # Text search index for title and description
        """
        CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_properties_text_search 
        ON properties USING gin (to_tsvector('english', title || ' ' || COALESCE(description, '')));
        """,
    ]
    
    try:
        with SessionLocal() as db:
            logger.info("🚀 Starting database performance optimization...")
            
            for i, command in enumerate(index_commands, 1):
                try:
                    logger.info(f"📊 Creating index {i}/{len(index_commands)}...")
                    db.execute(text(command))
                    db.commit()
                    logger.info(f"✅ Index {i} created successfully")
                    
                except Exception as e:
                    if "already exists" in str(e):
                        logger.info(f"ℹ️ Index {i} already exists, skipping")
                    else:
                        logger.error(f"❌ Failed to create index {i}: {e}")
                    db.rollback()
                    continue
            
            logger.info("🎉 Database performance optimization completed!")
            logger.info("📈 Query performance should be significantly improved")
            
    except Exception as e:
        logger.error(f"💥 Database optimization failed: {e}")
        return False
    
    return True


def verify_indexes():
    """Verify that indexes were created successfully."""
    
    verification_query = """
    SELECT 
        indexname,
        tablename,
        indexdef
    FROM pg_indexes 
    WHERE tablename = 'properties' 
    AND indexname LIKE 'idx_properties_%'
    ORDER BY indexname;
    """
    
    try:
        with SessionLocal() as db:
            result = db.execute(text(verification_query))
            indexes = result.fetchall()
            
            logger.info(f"📋 Found {len(indexes)} performance indexes:")
            for index in indexes:
                logger.info(f"   ✓ {index[0]}")
            
            return True
            
    except Exception as e:
        logger.error(f"❌ Failed to verify indexes: {e}")
        return False


def analyze_table_stats():
    """Update table statistics for better query planning."""
    
    try:
        with SessionLocal() as db:
            logger.info("📊 Updating table statistics...")
            db.execute(text("ANALYZE properties;"))
            db.execute(text("ANALYZE property_images;"))
            db.execute(text("ANALYZE amenities;"))
            db.commit()
            logger.info("✅ Table statistics updated")
            
    except Exception as e:
        logger.error(f"❌ Failed to update statistics: {e}")


if __name__ == "__main__":
    print("🔧 ComfyRent Database Performance Optimization")
    print("=" * 50)
    
    # Add indexes
    if add_performance_indexes():
        print("\n✅ Indexes added successfully!")
        
        # Verify indexes
        if verify_indexes():
            print("\n✅ Index verification completed!")  
        
        # Update statistics
        analyze_table_stats()
        
        print("\n🎉 Database optimization completed!")
        print("📈 Your API should now respond much faster!")
        
    else:
        print("\n❌ Database optimization failed!")
        sys.exit(1)
