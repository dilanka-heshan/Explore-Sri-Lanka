"""
Enhanced Travel Recommendations API using Simplifi    try:
        # Initialize the ranker
        ranker = create_travel_ranke        t    try:
        ranker = create_travel_ranker(
            qdrant_url=QDRANT_URL,
            qdrant_api_key=QDRANT_API_KEY,
            colle    try:
        # Test Qdrant connection
        ranker = create_travel_ranker(
            qdrant_url=QDRANT_URL,
            qdrant_api_key=QDRANT_API_KEY,
            collection_name=QDRANT_COLLECTION
        )name=QDRANT_COLLECTION
        )        ranker = create_travel_ranker(
            qdrant_url=QDRANT_URL,
            qdrant_api_key=QDRANT_API_KEY,
            collection_name=QDRANT_COLLECTION
        )
        ranker = create_travel_ranker(
            qdrant_url=QDRANT_URL,
            qdrant_api_key=QDRANT_API_KEY,
            collection_name=QDRANT_COLLECTION
        )           qdrant_url=QDRANT_URL,
            qdrant_api_key=QDRANT_API_KEY,
            collection_name=QDRANT_COLLECTION
        )R Ranker
Direct integration with Qdrant vector database
"""

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field
from typing import Dict, Any, Optional, List
import logging
import os
from langgraph_flow.models.simplified_pear_ranker import create_travel_ranker

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

router = APIRouter(prefix="/api/recommendations", tags=["Enhanced Recommendations"])

class RecommendationRequest(BaseModel):
    """Request model for travel recommendations"""
    user_query: str = Field(..., description="Natural language description of travel preferences", min_length=10, max_length=500)
    trip_type: Optional[str] = Field(default="solo", description="Trip type: solo, couple, family, group")
    budget: Optional[str] = Field(default="moderate", description="Budget level: budget, moderate, luxury")
    interests: Optional[List[str]] = Field(default=[], description="List of user interests")
    duration: Optional[int] = Field(default=7, description="Trip duration in days")
    group_size: Optional[int] = Field(default=1, description="Number of travelers")

class RecommendationResponse(BaseModel):
    """Response model for recommendations"""
    success: bool
    total_results: int
    recommendations: List[Dict[str, Any]]
    query_info: Dict[str, Any]

@router.post("/places", response_model=RecommendationResponse)
async def get_place_recommendations(request: RecommendationRequest):
    """
    Get travel place recommendations using transformer-based approach
    
    This endpoint implements your vision:
    1. User Query → Embedding
    2. Vector DB Similarity Search (Qdrant)
    3. Neural Ranking
    4. Top 30 Results
    """
    try:
        # Initialize the ranker
        ranker = create_travel_ranker(
            qdrant_url="https://50ab27b1-fac6-42dc-88af-ef70408179e6.us-east-1-0.aws.cloud.qdrant.io",  # Update with your Qdrant URL
            collection_name="exploresl"      # Update with your collection name
        )
        
        # Prepare user context
        user_context = {
            "trip_type": request.trip_type,
            "budget": request.budget,
            "interests": request.interests,
            "duration": request.duration,
            "group_size": request.group_size
        }
        
        # Get recommendations
        recommendations = ranker.get_recommendations(
            user_query=request.user_query,
            user_context=user_context,
            top_k=30,
            vector_search_limit=100
        )
        
        if not recommendations:
            return RecommendationResponse(
                success=True,
                total_results=0,
                recommendations=[],
                query_info={
                    "user_query": request.user_query,
                    "user_context": user_context,
                    "message": "No matching places found"
                }
            )
        
        # Format recommendations
        formatted_recommendations = []
        for rec in recommendations:
            formatted_rec = {
                "place_id": rec["id"],
                "neural_score": round(rec["neural_score"], 3),
                "similarity_score": round(rec["similarity_score"], 3),
                "combined_score": round(rec["combined_score"], 3),
                "place_info": rec["payload"]
            }
            formatted_recommendations.append(formatted_rec)
        
        return RecommendationResponse(
            success=True,
            total_results=len(recommendations),
            recommendations=formatted_recommendations,
            query_info={
                "user_query": request.user_query,
                "user_context": user_context,
                "ranking_method": "transformer_neural_ranking"
            }
        )
        
    except Exception as e:
        logger.error(f"Error in get_place_recommendations: {e}")
        raise HTTPException(status_code=500, detail=f"Recommendation error: {str(e)}")

@router.get("/places/category/{category}")
async def get_recommendations_by_category(
    category: str,
    user_query: str = Query(..., description="User travel query"),
    trip_type: str = Query("solo", description="Trip type"),
    budget: str = Query("moderate", description="Budget level"),
    interests: Optional[str] = Query(None, description="Comma-separated interests"),
    top_k: int = Query(20, le=50, description="Number of recommendations")
):
    """Get recommendations filtered by category"""
    try:
        ranker = create_travel_ranker(
            qdrant_url="https://50ab27b1-fac6-42dc-88af-ef70408179e6.us-east-1-0.aws.cloud.qdrant.io",
            collection_name="exploresl"
        )
        
        user_context = {
            "trip_type": trip_type,
            "budget": budget,
            "interests": interests.split(",") if interests else [],
        }
        
        recommendations = ranker.search_by_category(
            user_query=user_query,
            user_context=user_context,
            category_filter=category,
            top_k=top_k
        )
        
        return {
            "success": True,
            "category": category,
            "total_results": len(recommendations),
            "recommendations": recommendations
        }
        
    except Exception as e:
        logger.error(f"Error in category recommendations: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/places/region/{region}")
async def get_recommendations_by_region(
    region: str,
    user_query: str = Query(..., description="User travel query"),
    trip_type: str = Query("solo", description="Trip type"),
    budget: str = Query("moderate", description="Budget level"),
    interests: Optional[str] = Query(None, description="Comma-separated interests"),
    top_k: int = Query(20, le=50, description="Number of recommendations")
):
    """Get recommendations filtered by region"""
    try:
        ranker = create_travel_ranker(
            qdrant_url="https://50ab27b1-fac6-42dc-88af-ef70408179e6.us-east-1-0.aws.cloud.qdrant.io",
            collection_name="exploresl"
        )
        
        user_context = {
            "trip_type": trip_type,
            "budget": budget,
            "interests": interests.split(",") if interests else [],
        }
        
        recommendations = ranker.search_by_region(
            user_query=user_query,
            user_context=user_context,
            region_filter=region,
            top_k=top_k
        )
        
        return {
            "success": True,
            "region": region,
            "total_results": len(recommendations),
            "recommendations": recommendations
        }
        
    except Exception as e:
        logger.error(f"Error in region recommendations: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/places/{place_id}/similar")
async def get_similar_places(
    place_id: str,
    top_k: int = Query(10, le=20, description="Number of similar places")
):
    """Get places similar to a specific place"""
    try:
        ranker = create_travel_ranker(
            qdrant_url="https://50ab27b1-fac6-42dc-88af-ef70408179e6.us-east-1-0.aws.cloud.qdrant.io",
            collection_name="exploresl"
        )
        similar_places = ranker.get_similar_places(place_id, top_k)
        
        return {
            "success": True,
            "base_place_id": place_id,
            "total_results": len(similar_places),
            "similar_places": similar_places
        }
        
    except Exception as e:
        logger.error(f"Error in similar places: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/quick-search")
async def quick_search(
    query: str = Query(..., description="Quick search query"),
    top_k: int = Query(10, le=30, description="Number of results")
):
    """
    Quick search endpoint for simple queries
    """
    try:
        ranker = create_travel_ranker(
            qdrant_url="https://50ab27b1-fac6-42dc-88af-ef70408179e6.us-east-1-0.aws.cloud.qdrant.io",
            collection_name="exploresl"
        )
        
        # Simple user context for quick search
        user_context = {
            "trip_type": "solo",
            "budget": "moderate",
            "interests": []
        }
        
        recommendations = ranker.get_recommendations(
            user_query=query,
            user_context=user_context,
            top_k=top_k,
            vector_search_limit=50
        )
        
        return {
            "success": True,
            "query": query,
            "total_results": len(recommendations),
            "places": [
                {
                    "id": rec["id"],
                    "score": rec["combined_score"],
                    **rec["payload"]
                }
                for rec in recommendations
            ]
        }
        
    except Exception as e:
        logger.error(f"Error in quick search: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/health")
async def health_check():
    """Health check for the recommendation service"""
    try:
        # Test Qdrant connection
        ranker = create_travel_ranker(
            qdrant_url="https://50ab27b1-fac6-42dc-88af-ef70408179e6.us-east-1-0.aws.cloud.qdrant.io",
            collection_name="exploresl"
        )
        
        return {
            "status": "healthy",
            "service": "Enhanced Travel Recommendations",
            "features": [
                "Transformer-based embeddings",
                "Qdrant vector database",
                "Neural ranking",
                "Real-time recommendations"
            ],
            "database": "connected"
        }
        
    except Exception as e:
        return {
            "status": "unhealthy",
            "error": str(e),
            "database": "disconnected"
        }
