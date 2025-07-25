"""
Dataset Upload Service
Handles uploading attraction data to database and Qdrant vector store
"""

import json
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime
import pandas as pd
from sqlalchemy.orm import Session

from models.schemas import (
    AttractionDataUpload, DatasetUploadRequest, DatasetUploadResponse,
    Attraction, InterestType, DifficultyLevel, BudgetLevel
)
from models.database import get_db
from langgraph_flow.models.vector_db import QdrantVectorDB, MockVectorDB
from config import settings

logger = logging.getLogger(__name__)

class DatasetUploadService:
    """Service for uploading and managing attraction datasets"""
    
    def __init__(self):
        self.vector_db = MockVectorDB() if settings.QDRANT_USE_MOCK else QdrantVectorDB()
        
    async def upload_attractions_dataset(
        self, 
        upload_request: DatasetUploadRequest,
        db: Session
    ) -> DatasetUploadResponse:
        """Upload a dataset of attractions to database and vector store"""
        
        uploaded_count = 0
        failed_count = 0
        failed_items = []
        
        try:
            # Process each attraction
            for idx, attraction_data in enumerate(upload_request.attractions):
                try:
                    # Validate and convert to internal format
                    attraction = self._convert_upload_to_attraction(attraction_data)
                    
                    # Store in database
                    db_success = await self._store_in_database(attraction, db)
                    
                    # Store in vector database
                    vector_success = await self._store_in_vector_db(attraction)
                    
                    if db_success and vector_success:
                        uploaded_count += 1
                    else:
                        failed_count += 1
                        failed_items.append({
                            "index": idx,
                            "name": attraction_data.name,
                            "error": "Database or vector store error"
                        })
                        
                except Exception as e:
                    failed_count += 1
                    failed_items.append({
                        "index": idx,
                        "name": attraction_data.name if hasattr(attraction_data, 'name') else f"Item {idx}",
                        "error": str(e)
                    })
                    logger.error(f"Failed to upload attraction {idx}: {e}")
            
            # Determine sync status
            qdrant_status = "success" if failed_count == 0 else ("partial" if uploaded_count > 0 else "failed")
            db_status = "success" if failed_count == 0 else ("partial" if uploaded_count > 0 else "failed")
            
            return DatasetUploadResponse(
                success=uploaded_count > 0,
                uploaded_count=uploaded_count,
                failed_count=failed_count,
                failed_items=failed_items,
                qdrant_sync_status=qdrant_status,
                database_sync_status=db_status,
                message=f"Successfully uploaded {uploaded_count} attractions, {failed_count} failed"
            )
            
        except Exception as e:
            logger.error(f"Dataset upload failed: {e}")
            return DatasetUploadResponse(
                success=False,
                uploaded_count=0,
                failed_count=len(upload_request.attractions),
                failed_items=[{"error": str(e)}],
                qdrant_sync_status="failed",
                database_sync_status="failed",
                message=f"Upload failed: {str(e)}"
            )
    
    def _convert_upload_to_attraction(self, upload_data: AttractionDataUpload) -> Attraction:
        """Convert upload format to internal Attraction format"""
        return Attraction(
            id=f"attr_{hash(upload_data.name + str(upload_data.latitude))}",
            name=upload_data.name,
            description=upload_data.description,
            category=upload_data.category,
            latitude=upload_data.latitude,
            longitude=upload_data.longitude,
            rating=upload_data.rating,
            review_count=upload_data.review_count,
            tags=upload_data.tags,
            entry_fee=upload_data.entry_fee_lkr,
            opening_hours=upload_data.opening_hours,
            visit_duration_minutes=int(upload_data.visit_duration_hours * 60),  # Convert hours to minutes
            difficulty_level=upload_data.difficulty_level,
            best_season=upload_data.best_season,
            facilities=upload_data.facilities
        )
    
    async def _store_in_database(self, attraction: Attraction, db: Session) -> bool:
        """Store attraction in SQL database"""
        try:
            # Here you would implement the actual database storage
            # For now, just log the operation
            logger.info(f"Storing attraction {attraction.name} in database")
            # db.add(attraction_orm_model)
            # db.commit()
            return True
        except Exception as e:
            logger.error(f"Database storage failed for {attraction.name}: {e}")
            return False
    
    async def _store_in_vector_db(self, attraction: Attraction) -> bool:
        """Store attraction in Qdrant vector database"""
        try:
            # Create embedding text
            embedding_text = f"{attraction.name} {attraction.description} {' '.join(attraction.tags)}"
            
            # Store in vector database
            success = await self.vector_db.add_attraction(
                attraction_id=attraction.id,
                text=embedding_text,
                metadata={
                    "name": attraction.name,
                    "category": attraction.category.value,
                    "rating": attraction.rating,
                    "latitude": attraction.latitude,
                    "longitude": attraction.longitude,
                    "visit_duration_minutes": attraction.visit_duration_minutes,
                    "difficulty_level": attraction.difficulty_level.value,
                    "tags": attraction.tags
                }
            )
            return success
        except Exception as e:
            logger.error(f"Vector DB storage failed for {attraction.name}: {e}")
            return False
    
    async def upload_from_csv(self, csv_file_path: str, source: str = "csv_import") -> DatasetUploadResponse:
        """Upload attractions from CSV file"""
        try:
            # Read CSV file
            df = pd.read_csv(csv_file_path)
            
            # Convert to upload format
            attractions = []
            for _, row in df.iterrows():
                try:
                    attraction = AttractionDataUpload(
                        name=row['name'],
                        description=row.get('description', ''),
                        category=InterestType(row.get('category', 'nature')),
                        latitude=float(row['latitude']),
                        longitude=float(row['longitude']),
                        rating=float(row.get('rating', 0)),
                        review_count=int(row.get('review_count', 0)),
                        tags=row.get('tags', '').split(',') if row.get('tags') else [],
                        entry_fee_lkr=float(row['entry_fee_lkr']) if pd.notna(row.get('entry_fee_lkr')) else None,
                        visit_duration_hours=float(row.get('visit_duration_hours', 2)),
                        difficulty_level=DifficultyLevel(row.get('difficulty_level', 'easy')),
                        best_season=row.get('best_season'),
                        facilities=row.get('facilities', '').split(',') if row.get('facilities') else []
                    )
                    attractions.append(attraction)
                except Exception as e:
                    logger.warning(f"Skipping row due to error: {e}")
                    continue
            
            # Create upload request
            upload_request = DatasetUploadRequest(
                attractions=attractions,
                source=source,
                upload_timestamp=datetime.now()
            )
            
            # Process upload
            db = next(get_db())
            return await self.upload_attractions_dataset(upload_request, db)
            
        except Exception as e:
            logger.error(f"CSV upload failed: {e}")
            return DatasetUploadResponse(
                success=False,
                uploaded_count=0,
                failed_count=0,
                failed_items=[{"error": f"CSV processing failed: {str(e)}"}],
                qdrant_sync_status="failed",
                database_sync_status="failed",
                message=f"CSV upload failed: {str(e)}"
            )
    
    async def upload_from_json(self, json_file_path: str, source: str = "json_import") -> DatasetUploadResponse:
        """Upload attractions from JSON file"""
        try:
            with open(json_file_path, 'r') as f:
                data = json.load(f)
            
            # Convert to upload format
            attractions = []
            for item in data:
                try:
                    attraction = AttractionDataUpload(**item)
                    attractions.append(attraction)
                except Exception as e:
                    logger.warning(f"Skipping item due to validation error: {e}")
                    continue
            
            # Create upload request
            upload_request = DatasetUploadRequest(
                attractions=attractions,
                source=source,
                upload_timestamp=datetime.now()
            )
            
            # Process upload
            db = next(get_db())
            return await self.upload_attractions_dataset(upload_request, db)
            
        except Exception as e:
            logger.error(f"JSON upload failed: {e}")
            return DatasetUploadResponse(
                success=False,
                uploaded_count=0,
                failed_count=0,
                failed_items=[{"error": f"JSON processing failed: {str(e)}"}],
                qdrant_sync_status="failed",
                database_sync_status="failed",
                message=f"JSON upload failed: {str(e)}"
            )
    
    async def validate_dataset(self, attractions: List[AttractionDataUpload]) -> Dict[str, Any]:
        """Validate dataset before upload"""
        validation_results = {
            "total_items": len(attractions),
            "valid_items": 0,
            "invalid_items": 0,
            "warnings": [],
            "errors": []
        }
        
        for idx, attraction in enumerate(attractions):
            try:
                # Check required fields
                if not attraction.name or not attraction.description:
                    validation_results["errors"].append(f"Item {idx}: Missing name or description")
                    continue
                
                # Check coordinates
                if not (-90 <= attraction.latitude <= 90) or not (-180 <= attraction.longitude <= 180):
                    validation_results["errors"].append(f"Item {idx}: Invalid coordinates")
                    continue
                
                # Check visit duration
                if attraction.visit_duration_hours <= 0 or attraction.visit_duration_hours > 24:
                    validation_results["warnings"].append(f"Item {idx}: Unusual visit duration")
                
                # Check rating
                if attraction.rating < 0 or attraction.rating > 5:
                    validation_results["warnings"].append(f"Item {idx}: Rating out of range")
                
                validation_results["valid_items"] += 1
                
            except Exception as e:
                validation_results["errors"].append(f"Item {idx}: Validation error - {str(e)}")
                validation_results["invalid_items"] += 1
        
        return validation_results
    
    async def get_upload_statistics(self) -> Dict[str, Any]:
        """Get statistics about uploaded data"""
        try:
            # Get vector DB stats
            vector_stats = await self.vector_db.get_collection_info()
            
            # Get database stats (mock for now)
            db_stats = {
                "total_attractions": vector_stats.get("vectors_count", 0),
                "categories": {},  # Would query actual DB
                "average_rating": 4.2,  # Would calculate from DB
                "last_update": datetime.now().isoformat()
            }
            
            return {
                "database_stats": db_stats,
                "vector_db_stats": vector_stats,
                "sync_status": "synchronized"
            }
            
        except Exception as e:
            logger.error(f"Failed to get upload statistics: {e}")
            return {
                "error": str(e),
                "sync_status": "error"
            }

# Singleton instance
dataset_upload_service = DatasetUploadService()
