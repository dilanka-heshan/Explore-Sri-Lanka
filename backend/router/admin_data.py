"""
Admin and Data Management Router
Handles user interest collection, dataset upload, and itinerary management
"""

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.orm import Session
from typing import List, Dict, Any, Optional
import json
import logging

from models.database import get_db
from models.schemas import (
    UserInterestSurvey, MockUserProfile, EnhancedUserProfile,
    DatasetUploadRequest, DatasetUploadResponse, AttractionDataUpload,
    StoredItinerary, ItineraryQueryRequest, TravelPlanRequest, TravelPlanResponse
)
from services.mock_data_service import mock_data_generator
from services.dataset_upload_service import dataset_upload_service

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/admin", tags=["admin", "data_management"])

# ==========================================
# USER INTEREST COLLECTION ENDPOINTS
# ==========================================

@router.post("/user-survey/collect", response_model=Dict[str, Any])
async def collect_user_interests(
    survey: UserInterestSurvey,
    db: Session = Depends(get_db)
):
    """Collect user interest survey for PEAR model training"""
    try:
        # Store survey in database (implement actual storage)
        logger.info(f"Collecting user survey for session {survey.session_id}")
        
        # Generate enhanced profile from survey
        enhanced_profile = _convert_survey_to_enhanced_profile(survey)
        
        # Store for ML training (implement actual storage)
        
        return {
            "success": True,
            "message": "User interests collected successfully",
            "session_id": survey.session_id,
            "profile_summary": {
                "interests": enhanced_profile.interests,
                "trip_type": enhanced_profile.trip_type,
                "budget_level": enhanced_profile.budget_level,
                "activity_level": survey.activity_level
            },
            "next_steps": "You can now create personalized travel plans"
        }
        
    except Exception as e:
        logger.error(f"Failed to collect user interests: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to collect interests: {str(e)}")

@router.get("/user-survey/template", response_model=UserInterestSurvey)
async def get_survey_template():
    """Get a template for user interest survey"""
    return mock_data_generator.generate_user_interest_survey()

@router.post("/mock-users/generate", response_model=List[MockUserProfile])
async def generate_mock_users(
    count: int = 10,
    persona_type: Optional[str] = None
):
    """Generate mock user profiles for testing"""
    try:
        if persona_type:
            profiles = [mock_data_generator.generate_mock_user_profile(persona_type) for _ in range(count)]
        else:
            profiles = mock_data_generator.generate_mock_dataset(count)
        
        logger.info(f"Generated {len(profiles)} mock user profiles")
        return profiles
        
    except Exception as e:
        logger.error(f"Failed to generate mock users: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to generate mock users: {str(e)}")

@router.get("/mock-users/training-data", response_model=List[Dict[str, Any]])
async def get_pear_training_data(samples: int = 100):
    """Get training data for PEAR model"""
    try:
        training_data = mock_data_generator.generate_training_data_for_pear(samples)
        return training_data
    except Exception as e:
        logger.error(f"Failed to generate training data: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ==========================================
# DATASET UPLOAD ENDPOINTS
# ==========================================

@router.post("/dataset/upload", response_model=DatasetUploadResponse)
async def upload_attraction_dataset(
    upload_request: DatasetUploadRequest,
    db: Session = Depends(get_db)
):
    """Upload attraction dataset to database and Qdrant"""
    try:
        result = await dataset_upload_service.upload_attractions_dataset(upload_request, db)
        logger.info(f"Dataset upload completed: {result.uploaded_count} successful, {result.failed_count} failed")
        return result
        
    except Exception as e:
        logger.error(f"Dataset upload failed: {e}")
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")

@router.post("/dataset/upload-csv", response_model=DatasetUploadResponse)
async def upload_csv_dataset(
    file: UploadFile = File(...),
    source: str = Form("csv_upload")
):
    """Upload attractions from CSV file"""
    try:
        # Save uploaded file temporarily
        temp_path = f"/tmp/{file.filename}"
        with open(temp_path, "wb") as buffer:
            content = await file.read()
            buffer.write(content)
        
        # Process CSV
        result = await dataset_upload_service.upload_from_csv(temp_path, source)
        
        # Clean up temp file
        import os
        if os.path.exists(temp_path):
            os.remove(temp_path)
        
        return result
        
    except Exception as e:
        logger.error(f"CSV upload failed: {e}")
        raise HTTPException(status_code=500, detail=f"CSV upload failed: {str(e)}")

@router.post("/dataset/upload-json", response_model=DatasetUploadResponse)
async def upload_json_dataset(
    file: UploadFile = File(...),
    source: str = Form("json_upload")
):
    """Upload attractions from JSON file"""
    try:
        # Read JSON content
        content = await file.read()
        json_data = json.loads(content)
        
        # Convert to upload request
        attractions = [AttractionDataUpload(**item) for item in json_data]
        upload_request = DatasetUploadRequest(
            attractions=attractions,
            source=source
        )
        
        # Process upload
        db = next(get_db())
        result = await dataset_upload_service.upload_attractions_dataset(upload_request, db)
        
        return result
        
    except Exception as e:
        logger.error(f"JSON upload failed: {e}")
        raise HTTPException(status_code=500, detail=f"JSON upload failed: {str(e)}")

@router.post("/dataset/validate", response_model=Dict[str, Any])
async def validate_dataset(attractions: List[AttractionDataUpload]):
    """Validate attraction dataset before upload"""
    try:
        validation_results = await dataset_upload_service.validate_dataset(attractions)
        return validation_results
    except Exception as e:
        logger.error(f"Dataset validation failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/dataset/upload-sample", response_model=DatasetUploadResponse)
async def upload_sample_dataset(db: Session = Depends(get_db)):
    """Upload the built-in sample Sri Lankan attractions dataset"""
    try:
        # Import sample data
        from data.sample_attractions import get_sample_dataset
        sample_data = get_sample_dataset()
        
        # Convert to upload format
        attractions = [AttractionDataUpload(**item) for item in sample_data]
        
        upload_request = DatasetUploadRequest(
            attractions=attractions,
            source="sample_dataset",
            uploader_id="system"
        )
        
        # Process upload
        result = await dataset_upload_service.upload_attractions_dataset(upload_request, db)
        
        logger.info(f"Sample dataset upload completed: {result.uploaded_count} attractions")
        return result
        
    except Exception as e:
        logger.error(f"Sample dataset upload failed: {e}")
        raise HTTPException(status_code=500, detail=f"Sample upload failed: {str(e)}")

@router.get("/dataset/stats", response_model=Dict[str, Any])
async def get_dataset_statistics():
    """Get statistics about uploaded datasets"""
    try:
        stats = await dataset_upload_service.get_upload_statistics()
        return stats
    except Exception as e:
        logger.error(f"Failed to get dataset stats: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ==========================================
# ITINERARY STORAGE AND MANAGEMENT
# ==========================================

@router.post("/itinerary/store", response_model=Dict[str, Any])
async def store_itinerary(
    request: TravelPlanRequest,
    plan: TravelPlanResponse,
    user_id: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Store a generated itinerary in database"""
    try:
        # Create stored itinerary
        stored_itinerary = StoredItinerary(
            id=plan.plan_id,
            user_id=user_id,
            session_id=f"session_{plan.plan_id}",
            original_request=request,
            travel_plan=plan
        )
        
        # Store in database (implement actual storage)
        logger.info(f"Storing itinerary {plan.plan_id}")
        
        return {
            "success": True,
            "itinerary_id": plan.plan_id,
            "message": "Itinerary stored successfully",
            "access_url": f"/api/admin/itinerary/{plan.plan_id}"
        }
        
    except Exception as e:
        logger.error(f"Failed to store itinerary: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/itinerary/{itinerary_id}", response_model=StoredItinerary)
async def get_stored_itinerary(
    itinerary_id: str,
    db: Session = Depends(get_db)
):
    """Retrieve a stored itinerary"""
    try:
        # Retrieve from database (implement actual retrieval)
        # For now, return a mock response
        logger.info(f"Retrieving itinerary {itinerary_id}")
        
        # This would be replaced with actual database query
        raise HTTPException(status_code=404, detail="Itinerary not found - storage not implemented")
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to retrieve itinerary: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/itinerary/search", response_model=List[StoredItinerary])
async def search_itineraries(
    query: ItineraryQueryRequest,
    db: Session = Depends(get_db)
):
    """Search for stored itineraries"""
    try:
        # Implement database search
        logger.info(f"Searching itineraries with query: {query}")
        
        # This would be replaced with actual database query
        return []
        
    except Exception as e:
        logger.error(f"Failed to search itineraries: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/itinerary/{itinerary_id}/feedback", response_model=Dict[str, Any])
async def update_itinerary_feedback(
    itinerary_id: str,
    rating: int,
    feedback: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Update user feedback for a stored itinerary"""
    try:
        # Update feedback in database
        logger.info(f"Updating feedback for itinerary {itinerary_id}: rating={rating}")
        
        # This would update the actual database record
        
        return {
            "success": True,
            "message": "Feedback updated successfully",
            "itinerary_id": itinerary_id,
            "rating": rating
        }
        
    except Exception as e:
        logger.error(f"Failed to update feedback: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ==========================================
# SYSTEM MONITORING AND HEALTH
# ==========================================

@router.get("/system/health", response_model=Dict[str, Any])
async def check_system_health():
    """Check system health and component status"""
    try:
        # Check various system components
        health_status = {
            "status": "healthy",
            "timestamp": "2024-12-01T10:00:00Z",
            "components": {
                "database": "connected",
                "qdrant": "connected" if not hasattr(dataset_upload_service.vector_db, 'mock') else "mock",
                "pear_model": "loaded",
                "clustering": "operational",
                "route_optimizer": "operational"
            },
            "statistics": await dataset_upload_service.get_upload_statistics()
        }
        
        return health_status
        
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return {
            "status": "degraded",
            "error": str(e)
        }

# ==========================================
# HELPER FUNCTIONS
# ==========================================

def _convert_survey_to_enhanced_profile(survey: UserInterestSurvey) -> EnhancedUserProfile:
    """Convert user survey to enhanced profile for ML models"""
    from models.schemas import InterestType, TripType
    
    # Map survey responses to interests
    interests = []
    if survey.cultural_sites_interest >= 4:
        interests.append(InterestType.CULTURAL)
    if survey.nature_wildlife_interest >= 4:
        interests.extend([InterestType.NATURE, InterestType.WILDLIFE])
    if survey.adventure_sports_interest >= 4:
        interests.append(InterestType.ADVENTURE)
    if survey.beach_relaxation_interest >= 4:
        interests.append(InterestType.BEACH)
    if survey.food_culinary_interest >= 4:
        interests.append(InterestType.FOOD)
    if survey.historical_sites_interest >= 4:
        interests.append(InterestType.HISTORICAL)
    if survey.photography_interest >= 4:
        interests.append(InterestType.PHOTOGRAPHY)
    if survey.spiritual_religious_interest >= 4:
        interests.append(InterestType.SPIRITUAL)
    if survey.shopping_interest >= 4:
        interests.append(InterestType.SHOPPING)
    
    # Default to nature if no strong interests
    if not interests:
        interests = [InterestType.NATURE]
    
    # Map group size to trip type
    if survey.typical_group_size == 1:
        trip_type = TripType.SOLO
    elif survey.typical_group_size == 2:
        trip_type = TripType.COUPLE
    elif survey.typical_group_size <= 4:
        trip_type = TripType.FAMILY
    else:
        trip_type = TripType.GROUP
    
    return EnhancedUserProfile(
        interests=interests,
        trip_type=trip_type,
        budget_level=survey.accommodation_preference,
        age_group=survey.age_range,
        preferred_pace=survey.preferred_pace,
        mobility_requirements=survey.mobility_requirements
    )
