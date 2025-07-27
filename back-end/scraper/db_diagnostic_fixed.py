#!/usr/bin/env python3
"""
Simple database diagnostic script with correct Docker authentication.
"""

import sys
import os
import logging
from sqlalchemy import create_engine, text, inspect
import psycopg2

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Database connection settings from Docker Compose
DB_HOST = 'comfyrent-postgres'
DB_PORT = '5432'
DB_NAME = 'comfyrent_production'
DB_USER = 'comfyrent_user'
# Password from the secret file
DB_PASSWORD = 'oS05j2bk7uM7iBUGwHpJdOn8zMDncnMrpXJWfDAjtd0='


def check_database_connection():
    """Check basic database connectivity."""
    try:
        # Try direct psycopg2 connection first
        conn = psycopg2.connect(
            host=DB_HOST,
            port=DB_PORT,
            database=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD
        )
        logger.info("✅ Direct database connection successful")
        conn.close()
        return True
    except Exception as e:
        logger.error(f"❌ Database connection failed: {e}")
        return False


def list_all_tables():
    """List all tables in the database."""
    try:
        engine = create_engine(
            f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
        )
        
        with engine.connect() as conn:
            # Get all tables
            result = conn.execute(text("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public'
                ORDER BY table_name;
            """))
            
            tables = [row[0] for row in result]
            logger.info(f"📋 All tables: {tables}")
            return tables
            
    except Exception as e:
        logger.error(f"❌ Error listing tables: {e}")
        return []


def check_foreign_keys_detailed():
    """Check all foreign key constraints in detail."""
    try:
        engine = create_engine(
            f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
        )
        
        with engine.connect() as conn:
            result = conn.execute(text("""
                SELECT 
                    tc.table_name,
                    tc.constraint_name,
                    kcu.column_name,
                    ccu.table_name AS foreign_table_name,
                    ccu.column_name AS foreign_column_name,
                    rc.delete_rule,
                    rc.update_rule
                FROM information_schema.table_constraints AS tc
                JOIN information_schema.key_column_usage AS kcu
                    ON tc.constraint_name = kcu.constraint_name
                    AND tc.table_schema = kcu.table_schema
                JOIN information_schema.constraint_column_usage AS ccu
                    ON ccu.constraint_name = tc.constraint_name
                    AND ccu.table_schema = tc.table_schema
                LEFT JOIN information_schema.referential_constraints AS rc
                    ON tc.constraint_name = rc.constraint_name
                WHERE tc.constraint_type = 'FOREIGN KEY'
                ORDER BY tc.table_name, tc.constraint_name;
            """))
            
            logger.info("🔗 Foreign Key Constraints:")
            for row in result:
                table, constraint, column, ref_table, ref_column, delete_rule, update_rule = row
                logger.info(f"   {table}.{column} -> {ref_table}.{ref_column}")
                logger.info(f"      DELETE: {delete_rule}, UPDATE: {update_rule}")
            
            return True
            
    except Exception as e:
        logger.error(f"❌ Error checking foreign keys: {e}")
        return False


def count_records():
    """Count records in key tables."""
    try:
        engine = create_engine(
            f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
        )
        
        key_tables = ['properties', 'property_prices', 'property_images', 'property_parameters']
        
        with engine.connect() as conn:
            for table in key_tables:
                try:
                    result = conn.execute(text(f"SELECT COUNT(*) FROM {table};"))
                    count = result.scalar()
                    logger.info(f"📊 Table '{table}': {count} records")
                except Exception as e:
                    logger.warning(f"⚠️  Could not count records in '{table}': {e}")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Error counting records: {e}")
        return False


def test_cascade_delete():
    """Test if we can fix the cascade delete issue."""
    try:
        engine = create_engine(
            f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
        )
        
        with engine.connect() as conn:
            logger.info("🔧 Attempting to fix foreign key constraints...")
            
            trans = conn.begin()
            try:
                # Drop and recreate constraints with CASCADE
                logger.info("   Dropping existing constraints...")
                
                # Property prices
                conn.execute(text("""
                    ALTER TABLE property_prices 
                    DROP CONSTRAINT IF EXISTS property_prices_property_id_fkey;
                """))
                
                # Property images
                conn.execute(text("""
                    ALTER TABLE property_images 
                    DROP CONSTRAINT IF EXISTS property_images_property_id_fkey;
                """))
                
                # Property parameters
                conn.execute(text("""
                    ALTER TABLE property_parameters 
                    DROP CONSTRAINT IF EXISTS property_parameters_property_id_fkey;
                """))
                
                logger.info("   Adding CASCADE constraints...")
                
                # Property prices with CASCADE
                conn.execute(text("""
                    ALTER TABLE property_prices 
                    ADD CONSTRAINT property_prices_property_id_fkey 
                    FOREIGN KEY (property_id) REFERENCES properties(id) 
                    ON DELETE CASCADE;
                """))
                
                # Property images with CASCADE
                conn.execute(text("""
                    ALTER TABLE property_images 
                    ADD CONSTRAINT property_images_property_id_fkey 
                    FOREIGN KEY (property_id) REFERENCES properties(id) 
                    ON DELETE CASCADE;
                """))
                
                # Property parameters with CASCADE
                conn.execute(text("""
                    ALTER TABLE property_parameters 
                    ADD CONSTRAINT property_parameters_property_id_fkey 
                    FOREIGN KEY (property_id) REFERENCES properties(id) 
                    ON DELETE CASCADE;
                """))
                
                trans.commit()
                logger.info("✅ Foreign key constraints updated successfully!")
                return True
                
            except Exception as e:
                trans.rollback()
                logger.error(f"❌ Error updating constraints: {e}")
                return False
                
    except Exception as e:
        logger.error(f"❌ Error in cascade delete fix: {e}")
        return False


def main():
    """Main diagnostic function."""
    logger.info("🔍 Starting database diagnostic with correct credentials...")
    
    # Basic connectivity
    if not check_database_connection():
        return 1
    
    # List tables
    tables = list_all_tables()
    if not tables:
        logger.error("❌ No tables found or unable to list tables")
        return 1
    
    # Check foreign keys
    check_foreign_keys_detailed()
    
    # Count records
    count_records()
    
    # Try to fix cascade delete
    if test_cascade_delete():
        logger.info("✅ Database issues fixed!")
        
        # Verify the fix
        logger.info("🧪 Verifying the fix...")
        check_foreign_keys_detailed()
    else:
        logger.error("❌ Could not fix database issues")
        return 1
    
    logger.info("✅ Database diagnostic and fix completed successfully!")
    return 0


if __name__ == "__main__":
    exit(main())
