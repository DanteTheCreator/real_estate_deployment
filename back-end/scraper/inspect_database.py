#!/usr/bin/env python3
"""
Database schema inspector to check current structure and constraints.
"""

import sys
import os
sys.path.append('/app')

import logging
from sqlalchemy import create_engine, text, inspect
from database import engine

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def inspect_database_structure():
    """Inspect the current database structure."""
    try:
        inspector = inspect(engine)
        
        # Get all table names
        tables = inspector.get_table_names()
        logger.info(f"Available tables: {tables}")
        
        # Check each table's structure
        for table_name in tables:
            logger.info(f"\n=== Table: {table_name} ===")
            
            # Get columns
            columns = inspector.get_columns(table_name)
            logger.info(f"Columns: {[col['name'] for col in columns]}")
            
            # Get foreign keys
            foreign_keys = inspector.get_foreign_keys(table_name)
            if foreign_keys:
                logger.info(f"Foreign keys:")
                for fk in foreign_keys:
                    logger.info(f"  - {fk['name']}: {fk['constrained_columns']} -> {fk['referred_table']}.{fk['referred_columns']}")
                    logger.info(f"    Options: {fk.get('options', {})}")
            
            # Get indexes
            indexes = inspector.get_indexes(table_name)
            if indexes:
                logger.info(f"Indexes: {[idx['name'] for idx in indexes]}")
        
    except Exception as e:
        logger.error(f"Error inspecting database: {e}")


def check_constraint_details():
    """Check detailed constraint information from PostgreSQL system tables."""
    try:
        with engine.connect() as conn:
            # Query constraint details
            result = conn.execute(text("""
                SELECT 
                    tc.table_name,
                    tc.constraint_name,
                    tc.constraint_type,
                    kcu.column_name,
                    ccu.table_name AS foreign_table_name,
                    ccu.column_name AS foreign_column_name,
                    rc.delete_rule,
                    rc.update_rule
                FROM information_schema.table_constraints AS tc 
                JOIN information_schema.key_column_usage AS kcu
                    ON tc.constraint_name = kcu.constraint_name
                JOIN information_schema.constraint_column_usage AS ccu
                    ON ccu.constraint_name = tc.constraint_name
                LEFT JOIN information_schema.referential_constraints AS rc
                    ON tc.constraint_name = rc.constraint_name
                WHERE tc.constraint_type = 'FOREIGN KEY'
                    AND tc.table_schema = 'public'
                ORDER BY tc.table_name, tc.constraint_name;
            """))
            
            logger.info("\n=== Foreign Key Constraints Details ===")
            for row in result:
                logger.info(f"Table: {row.table_name}")
                logger.info(f"  Constraint: {row.constraint_name}")
                logger.info(f"  Column: {row.column_name} -> {row.foreign_table_name}.{row.foreign_column_name}")
                logger.info(f"  Delete Rule: {row.delete_rule}")
                logger.info(f"  Update Rule: {row.update_rule}")
                logger.info("")
        
    except Exception as e:
        logger.error(f"Error checking constraints: {e}")


def count_records():
    """Count records in each table to understand data volume."""
    try:
        inspector = inspect(engine)
        tables = inspector.get_table_names()
        
        logger.info("\n=== Record Counts ===")
        with engine.connect() as conn:
            for table in tables:
                try:
                    result = conn.execute(text(f"SELECT COUNT(*) FROM {table}"))
                    count = result.scalar()
                    logger.info(f"{table}: {count} records")
                except Exception as e:
                    logger.error(f"Error counting {table}: {e}")
    
    except Exception as e:
        logger.error(f"Error counting records: {e}")


def check_referential_integrity():
    """Check for referential integrity issues."""
    try:
        logger.info("\n=== Checking Referential Integrity ===")
        
        with engine.connect() as conn:
            # Check orphaned property_prices
            result = conn.execute(text("""
                SELECT COUNT(*) FROM property_prices pp
                LEFT JOIN properties p ON pp.property_id = p.id
                WHERE p.id IS NULL
            """))
            orphaned_prices = result.scalar()
            logger.info(f"Orphaned property_prices: {orphaned_prices}")
            
            # Check orphaned property_images
            result = conn.execute(text("""
                SELECT COUNT(*) FROM property_images pi
                LEFT JOIN properties p ON pi.property_id = p.id
                WHERE p.id IS NULL
            """))
            orphaned_images = result.scalar()
            logger.info(f"Orphaned property_images: {orphaned_images}")
            
            # Check orphaned property_parameters
            result = conn.execute(text("""
                SELECT COUNT(*) FROM property_parameters pp
                LEFT JOIN properties p ON pp.property_id = p.id
                WHERE p.id IS NULL
            """))
            orphaned_params = result.scalar()
            logger.info(f"Orphaned property_parameters: {orphaned_params}")
            
    except Exception as e:
        logger.error(f"Error checking referential integrity: {e}")


def main():
    """Main function."""
    logger.info("Starting database structure inspection...")
    
    try:
        # Inspect overall structure
        inspect_database_structure()
        
        # Check constraint details
        check_constraint_details()
        
        # Count records
        count_records()
        
        # Check referential integrity
        check_referential_integrity()
        
        logger.info("\nDatabase inspection completed successfully")
        
    except Exception as e:
        logger.error(f"Database inspection failed: {e}")
        return 1
    
    return 0


if __name__ == "__main__":
    exit(main())
