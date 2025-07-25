"""
Enhanced Travel Recommendations API using Simplified PEAR Ranker
Direct integration with Qdrant vector database and new transformer-based approach
"""

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field
from typing import Dict, Any, Optional, List
import logging
import os
from langgraph_flow.models.pear_ranker import create_pear_ranker

logger = logging.getLogger(__name__)

# Load Qdrant configuration from environment
QDRANT_URL = os.getenv("QDRANT_HOST", "http://localhost:6333")
QDRANT_PORT = os.getenv("QDRANT_PORT", "6333")
QDRANT_API_KEY = os.getenv("QDRANT_API_KEY")
QDRANT_COLLECTION = os.getenv("QDRANT_COLLECTION_NAME", "exploresl")

# Construct full Qdrant URL
if not QDRANT_URL.startswith("http"):
    QDRANT_URL = f"https://{QDRANT_URL}:{QDRANT_PORT}"
elif ":" not in QDRANT_URL.split("://")[1]:
    QDRANT_URL = f"{QDRANT_URL}:{QDRANT_PORT}"

router = APIRouter(prefix="/recommendations", tags=["Enhanced Recommendations"])

# Global ranker instance
ranker = None

def get_ranker():
    """Get or initialize the PEAR ranker"""
    global ranker
    if ranker is None:
        try:
            ranker = create_pear_ranker(
                qdrant_url=QDRANT_URL,
                qdrant_api_key=QDRANT_API_KEY,
                collection_name=QDRANT_COLLECTION
            )
            logger.info("Successfully initialized PEAR ranker for recommendations API")
        except Exception as e:
            logger.error(f"Failed to initialize PEAR ranker: {e}")
            raise HTTPException(status_code=500, detail="Failed to initialize recommendation system")
    return ranker

class TravelPreferences(BaseModel):
    """User travel preferences for personalized recommendations"""
    interests: List[str] = Field(..., description="List of user interests", example=["culture", "beaches", "temples"])
    trip_type: Optional[str] = Field(None, description="Type of trip", example="cultural")
    budget: Optional[str] = Field(None, description="Budget level", example="medium")
    duration: Optional[int] = Field(None, description="Trip duration in days", example=7)
    group_size: Optional[int] = Field(None, description="Number of travelers", example=2)
    cultural_interest: Optional[int] = Field(None, description="Cultural interest level (1-10)", example=8)
    adventure_level: Optional[int] = Field(None, description="Adventure preference level (1-10)", example=5)
    nature_appreciation: Optional[int] = Field(None, description="Nature appreciation level (1-10)", example=7)

class RecommendationRequest(BaseModel):
    """Request model for travel recommendations"""
    query: str = Field(..., description="Natural language description of what user wants to do", 
                      example="I want to visit beautiful temples and beaches in Sri Lanka")
    preferences: TravelPreferences
    max_results: Optional[int] = Field(30, description="Maximum number of recommendations", example=30)

class PlaceRecommendation(BaseModel):
    """Recommendation response model"""
    id: str
    name: str
    category: str
    description: str
    region: str
    score: float = Field(..., description="Relevance score between 0 and 1")
    neural_score: Optional[float] = Field(None, description="Neural network ranking score")
    similarity_score: Optional[float] = Field(None, description="Vector similarity score")

class RecommendationResponse(BaseModel):
    """Response model for recommendations"""
    query: str
    total_results: int
    recommendations: List[PlaceRecommendation]
    processing_time_ms: float

@router.post("/places", response_model=RecommendationResponse)
async def get_travel_recommendations(request: RecommendationRequest):
    """
    Get personalized travel place recommendations using transformer-based ranking
    
    This endpoint uses the new simplified PEAR ranker that:
    1. Converts user query to embeddings
    2. Searches vector database for similar places
    3. Applies neural ranking for personalization
    4. Returns top-scored recommendations
    """
    import time
    start_time = time.time()
    
    try:
        # Get the ranker instance
        pear_ranker = get_ranker()
        
        # Convert preferences to user context
        user_context = {
            "interests": request.preferences.interests,
            "trip_type": request.preferences.trip_type,
            "budget": request.preferences.budget,
            "duration": request.preferences.duration,
            "group_size": request.preferences.group_size,
            "cultural_interest": request.preferences.cultural_interest,
            "adventure_level": request.preferences.adventure_level,
            "nature_appreciation": request.preferences.nature_appreciation
        }
        
        # Get recommendations from vector database
        recommendations = pear_ranker.get_recommendations_from_vector_db(
            user_query=request.query,
            user_context=user_context,
            top_k=request.max_results
        )
        
        # Convert to response format
        place_recommendations = []
        for rec in recommendations:
            place_rec = PlaceRecommendation(
                id=str(rec.get('id', '')),
                name=rec.get('name', 'Unknown'),
                category=rec.get('category', 'Unknown'),
                description=rec.get('description', ''),
                region=rec.get('region', 'Unknown'),
                score=rec.get('pear_score', 0.0),
                neural_score=rec.get('neural_score'),
                similarity_score=rec.get('similarity_score')
            )
            place_recommendations.append(place_rec)
        
        processing_time = (time.time() - start_time) * 1000
        
        logger.info(f"Generated {len(place_recommendations)} recommendations in {processing_time:.2f}ms")
        
        return RecommendationResponse(
            query=request.query,
            total_results=len(place_recommendations),
            recommendations=place_recommendations,
            processing_time_ms=processing_time
        )
        
    except Exception as e:
        logger.error(f"Error generating recommendations: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to generate recommendations: {str(e)}")

@router.get("/places/category/{category}")
async def get_recommendations_by_category(
    category: str,
    query: str = Query(..., description="User query"),
    interests: str = Query("", description="Comma-separated interests"),
    budget: Optional[str] = Query(None, description="Budget level"),
    max_results: int = Query(20, description="Maximum results")
):
    """Get recommendations filtered by category"""
    try:
        pear_ranker = get_ranker()
        
        # Parse interests
        interest_list = [i.strip() for i in interests.split(",") if i.strip()] if interests else []
        
        user_context = {
            "interests": interest_list,
            "budget": budget
        }
        
        # Use the ranker's category search
        recommendations = pear_ranker.search_by_category(
            user_query=query,
            user_context=user_context,
            category_filter=category,
            top_k=max_results
        )
        
        # Format response
        formatted_recommendations = []
        for rec in recommendations:
            payload = rec.get('payload', {})
            formatted_rec = {
                "id": str(rec.get('id', '')),
                "name": payload.get('name', 'Unknown'),
                "category": payload.get('category', category),
                "description": payload.get('description', ''),
                "region": payload.get('region', 'Unknown'),
                "score": rec.get('combined_score', 0.0)
            }
            formatted_recommendations.append(formatted_rec)
        
        return {
            "category": category,
            "query": query,
            "total_results": len(formatted_recommendations),
            "recommendations": formatted_recommendations
        }
        
    except Exception as e:
        logger.error(f"Error getting category recommendations: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get recommendations: {str(e)}")

@router.get("/places/region/{region}")
async def get_recommendations_by_region(
    region: str,
    query: str = Query(..., description="User query"),
    interests: str = Query("", description="Comma-separated interests"),
    budget: Optional[str] = Query(None, description="Budget level"),
    max_results: int = Query(20, description="Maximum results")
):
    """Get recommendations filtered by region"""
    try:
        pear_ranker = get_ranker()
        
        # Parse interests
        interest_list = [i.strip() for i in interests.split(",") if i.strip()] if interests else []
        
        user_context = {
            "interests": interest_list,
            "budget": budget
        }
        
        # Use the ranker's region search
        recommendations = pear_ranker.search_by_region(
            user_query=query,
            user_context=user_context,
            region_filter=region,
            top_k=max_results
        )
        
        # Format response
        formatted_recommendations = []
        for rec in recommendations:
            payload = rec.get('payload', {})
            formatted_rec = {
                "id": str(rec.get('id', '')),
                "name": payload.get('name', 'Unknown'),
                "category": payload.get('category', 'Unknown'),
                "description": payload.get('description', ''),
                "region": payload.get('region', region),
                "score": rec.get('combined_score', 0.0)
            }
            formatted_recommendations.append(formatted_rec)
        
        return {
            "region": region,
            "query": query,
            "total_results": len(formatted_recommendations),
            "recommendations": formatted_recommendations
        }
        
    except Exception as e:
        logger.error(f"Error getting region recommendations: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get recommendations: {str(e)}")

@router.get("/similar/{place_id}")
async def get_similar_places(
    place_id: str,
    max_results: int = Query(10, description="Maximum number of similar places")
):
    """Get places similar to a given place"""
    try:
        pear_ranker = get_ranker()
        
        similar_places = pear_ranker.get_similar_places(
            place_id=place_id,
            top_k=max_results
        )
        
        # Format response
        formatted_places = []
        for place in similar_places:
            payload = place.get('payload', {})
            formatted_place = {
                "id": str(place.get('id', '')),
                "name": payload.get('name', 'Unknown'),
                "category": payload.get('category', 'Unknown'),
                "description": payload.get('description', ''),
                "region": payload.get('region', 'Unknown'),
                "similarity_score": place.get('similarity_score', 0.0)
            }
            formatted_places.append(formatted_place)
        
        return {
            "reference_place_id": place_id,
            "total_results": len(formatted_places),
            "similar_places": formatted_places
        }
        
    except Exception as e:
        logger.error(f"Error getting similar places: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get similar places: {str(e)}")

@router.get("/health")
async def health_check():
    """Health check endpoint for the recommendation system"""
    try:
        pear_ranker = get_ranker()
        return {
            "status": "healthy",
            "system": "Enhanced Recommendations API",
            "ranker_type": "Simplified PEAR (Transformer-based)",
            "vector_database": "Qdrant Cloud",
            "collection": QDRANT_COLLECTION
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "error": str(e)
        }
