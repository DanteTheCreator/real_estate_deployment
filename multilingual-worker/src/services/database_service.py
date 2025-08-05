"""
Database service for the multilingual worker.
"""
import logging
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import selectinload
from sqlalchemy import select, text
from sqlalchemy.exc import SQLAlchemyError

from ..models.property_data import PropertyData
from ..core.config import MultilingualConfig


class DatabaseService:
    """Handles database operations for the multilingual worker."""
    
    def __init__(self, config: MultilingualConfig):
        """Initialize database service."""
        self.config = config
        self.logger = logging.getLogger(self.__class__.__name__)
        
        # Create async engine with connection pooling
        self.engine = create_async_engine(
            config.DATABASE_URL,
            pool_size=5,
            max_overflow=10,
            pool_pre_ping=True,
            echo=config.DEBUG_MODE,
        )
        
        # Create session factory
        self.async_session = async_sessionmaker(
            self.engine,
            class_=AsyncSession,
            expire_on_commit=False
        )
    
    async def get_properties_for_multilingual_processing(self, limit: int = 100) -> List[PropertyData]:
        """Get properties that need multilingual processing."""
        try:
            async with self.async_session() as session:
                # Query for properties that don't have English or Russian translations
                query = text("""
                    SELECT id, external_id, title, description, 
                           title_en, title_ru, description_en, description_ru,
                           created_at, updated_at, property_type, deal_type,
                           price, currency, area, bedrooms, bathrooms, floor,
                           total_floors, address, city, district, latitude, longitude,
                           contact_name, phone, images, features, status_id
                    FROM properties 
                    WHERE (title_en IS NULL OR title_ru IS NULL OR 
                           description_en IS NULL OR description_ru IS NULL)
                    AND external_id IS NOT NULL 
                    AND title IS NOT NULL
                    ORDER BY created_at DESC 
                    LIMIT :limit
                """)
                
                result = await session.execute(query, {"limit": limit})
                rows = result.fetchall()
                
                properties = []
                for row in rows:
                    # Convert row to PropertyData object
                    property_data = PropertyData(
                        id=row.id,
                        external_id=row.external_id,
                        title=row.title,
                        description=row.description,
                        title_en=row.title_en,
                        title_ru=row.title_ru,
                        description_en=row.description_en,
                        description_ru=row.description_ru,
                        property_type=row.property_type,
                        deal_type=row.deal_type,
                        price=row.price,
                        currency=row.currency,
                        area=row.area,
                        bedrooms=row.bedrooms,
                        bathrooms=row.bathrooms,
                        floor=row.floor,
                        total_floors=row.total_floors,
                        address=row.address,
                        city=row.city,
                        district=row.district,
                        latitude=row.latitude,
                        longitude=row.longitude,
                        contact_name=row.contact_name,
                        phone=row.phone,
                        images=row.images,
                        features=row.features,
                        status_id=row.status_id,
                        created_at=row.created_at,
                        updated_at=row.updated_at
                    )
                    properties.append(property_data)
                
                self.logger.info(f"Retrieved {len(properties)} properties for multilingual processing")
                return properties
                
        except SQLAlchemyError as e:
            self.logger.error(f"Database error getting properties for multilingual processing: {e}")
            return []
        except Exception as e:
            self.logger.error(f"Unexpected error getting properties for multilingual processing: {e}")
            return []
    
    async def update_property_multilingual_content(self, property_data: PropertyData) -> bool:
        """Update property with multilingual content."""
        try:
            async with self.async_session() as session:
                # Update the property with multilingual content
                update_query = text("""
                    UPDATE properties 
                    SET title_en = :title_en,
                        title_ru = :title_ru,
                        description_en = :description_en,
                        description_ru = :description_ru,
                        updated_at = NOW()
                    WHERE id = :property_id
                """)
                
                await session.execute(update_query, {
                    "title_en": property_data.title_en,
                    "title_ru": property_data.title_ru,
                    "description_en": property_data.description_en,
                    "description_ru": property_data.description_ru,
                    "property_id": property_data.id
                })
                
                await session.commit()
                
                self.logger.info(f"Updated multilingual content for property {property_data.external_id}")
                return True
                
        except SQLAlchemyError as e:
            self.logger.error(f"Database error updating property {property_data.external_id}: {e}")
            await session.rollback()
            return False
        except Exception as e:
            self.logger.error(f"Unexpected error updating property {property_data.external_id}: {e}")
            return False
    
    async def get_total_properties_pending_translation(self) -> int:
        """Get count of properties that need multilingual processing."""
        try:
            async with self.async_session() as session:
                query = text("""
                    SELECT COUNT(*) as count
                    FROM properties 
                    WHERE (title_en IS NULL OR title_ru IS NULL OR 
                           description_en IS NULL OR description_ru IS NULL)
                    AND external_id IS NOT NULL 
                    AND title IS NOT NULL
                """)
                
                result = await session.execute(query)
                row = result.fetchone()
                count = row.count if row else 0
                
                self.logger.info(f"Total properties pending translation: {count}")
                return count
                
        except SQLAlchemyError as e:
            self.logger.error(f"Database error getting pending translation count: {e}")
            return 0
        except Exception as e:
            self.logger.error(f"Unexpected error getting pending translation count: {e}")
            return 0
    
    async def close(self):
        """Close database connections."""
        try:
            await self.engine.dispose()
            self.logger.info("Database connections closed")
        except Exception as e:
            self.logger.error(f"Error closing database connections: {e}")
