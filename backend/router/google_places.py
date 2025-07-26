"""
Google Places API Router
Standalone router for Google Places functionality
Provides restaurant, hotel, and place recommendations
"""

from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional
import logging
import time
from services.google_places_service import get_google_places_service
from models.enhanced_places_models import (
    PlaceSearchRequest,
    PlaceSearchResponse,
    PlaceType,
    MealType,
    PlaceRecommendation,
    DailyPlaceRecommendations
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/google-places", tags=["Google Places"])

@router.post("/search", response_model=PlaceSearchResponse)
async def search_places(request: PlaceSearchRequest):
    """Search for places using Google Places API"""
    
    start_time = time.time()
    
    try:
        places_service = get_google_places_service()
        
        places = await places_service.find_places_near_location(
            lat=request.latitude,
            lng=request.longitude,
            place_type=request.place_type,
            budget_level=request.budget_level,
            radius=request.radius,
            max_results=request.max_results,
            meal_type=request.meal_type
        )
        
        processing_time = (time.time() - start_time) * 1000
        
        return PlaceSearchResponse(
            search_location={"latitude": request.latitude, "longitude": request.longitude},
            place_type=request.place_type,
            budget_level=request.budget_level,
            radius_km=request.radius / 1000,
            results_count=len(places),
            places=places,
            search_time_ms=processing_time
        )
        
    except Exception as e:
        logger.error(f"Error searching places: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to search places: {str(e)}")

@router.get("/restaurants")
async def get_restaurants(
    lat: float = Query(..., description="Latitude"),
    lng: float = Query(..., description="Longitude"),
    budget_level: str = Query("medium", description="Budget level (budget/medium/luxury)"),
    meal_type: Optional[str] = Query(None, description="Meal type (breakfast/lunch/dinner)"),
    radius_km: float = Query(5.0, description="Search radius in kilometers", le=20),
    max_results: int = Query(5, description="Maximum results", le=20)
):
    """Get restaurant recommendations near coordinates"""
    
    try:
        places_service = get_google_places_service()
        
        # Convert meal type string to enum
        meal_type_enum = None
        if meal_type and meal_type.lower() in ["breakfast", "lunch", "dinner"]:
            meal_type_enum = MealType(meal_type.lower())
        
        restaurants = await places_service.find_places_near_location(
            lat=lat,
            lng=lng,
            place_type=PlaceType.RESTAURANT,
            budget_level=budget_level,
            radius=int(radius_km * 1000),
            max_results=max_results,
            meal_type=meal_type_enum
        )
        
        return {
            "location": {"latitude": lat, "longitude": lng},
            "search_params": {
                "meal_type": meal_type,
                "budget_level": budget_level,
                "radius_km": radius_km,
                "max_results": max_results
            },
            "restaurants": restaurants,
            "count": len(restaurants)
        }
        
    except Exception as e:
        logger.error(f"Error getting restaurants: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get restaurants: {str(e)}")

@router.get("/hotels")
async def get_hotels(
    lat: float = Query(..., description="Latitude"),
    lng: float = Query(..., description="Longitude"),
    budget_level: str = Query("medium", description="Budget level (budget/medium/luxury)"),
    radius_km: float = Query(10.0, description="Search radius in kilometers", le=30),
    max_results: int = Query(5, description="Maximum results", le=20)
):
    """Get hotel/accommodation recommendations near coordinates"""
    
    try:
        places_service = get_google_places_service()
        
        hotels = await places_service.find_places_near_location(
            lat=lat,
            lng=lng,
            place_type=PlaceType.LODGING,
            budget_level=budget_level,
            radius=int(radius_km * 1000),
            max_results=max_results
        )
        
        return {
            "location": {"latitude": lat, "longitude": lng},
            "search_params": {
                "budget_level": budget_level,
                "radius_km": radius_km,
                "max_results": max_results
            },
            "hotels": hotels,
            "count": len(hotels)
        }
        
    except Exception as e:
        logger.error(f"Error getting hotels: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get hotels: {str(e)}")

@router.get("/cafes")
async def get_cafes(
    lat: float = Query(..., description="Latitude"),
    lng: float = Query(..., description="Longitude"),
    budget_level: str = Query("medium", description="Budget level (budget/medium/luxury)"),
    radius_km: float = Query(3.0, description="Search radius in kilometers", le=10),
    max_results: int = Query(5, description="Maximum results", le=15)
):
    """Get cafe recommendations near coordinates"""
    
    try:
        places_service = get_google_places_service()
        
        cafes = await places_service.find_places_near_location(
            lat=lat,
            lng=lng,
            place_type=PlaceType.CAFE,
            budget_level=budget_level,
            radius=int(radius_km * 1000),
            max_results=max_results
        )
        
        return {
            "location": {"latitude": lat, "longitude": lng},
            "search_params": {
                "budget_level": budget_level,
                "radius_km": radius_km,
                "max_results": max_results
            },
            "cafes": cafes,
            "count": len(cafes)
        }
        
    except Exception as e:
        logger.error(f"Error getting cafes: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get cafes: {str(e)}")

@router.get("/daily-recommendations")
async def get_daily_recommendations(
    lat: float = Query(..., description="Latitude"),
    lng: float = Query(..., description="Longitude"),
    day: int = Query(1, description="Day number"),
    budget_level: str = Query("medium", description="Budget level (budget/medium/luxury)"),
    radius_km: float = Query(5.0, description="Search radius in kilometers", le=20)
):
    """Get complete daily place recommendations (breakfast, lunch, dinner, accommodation, cafes)"""
    
    try:
        places_service = get_google_places_service()
        
        daily_recs = await places_service.get_daily_recommendations(
            day=day,
            cluster_center_lat=lat,
            cluster_center_lng=lng,
            budget_level=budget_level,
            radius=int(radius_km * 1000)
        )
        
        return {
            "day": day,
            "location": {"latitude": lat, "longitude": lng},
            "search_params": {
                "budget_level": budget_level,
                "radius_km": radius_km
            },
            "recommendations": daily_recs,
            "summary": {
                "total_places": daily_recs.get_total_recommendations(),
                "breakfast_options": len(daily_recs.breakfast_places),
                "lunch_options": len(daily_recs.lunch_places),
                "dinner_options": len(daily_recs.dinner_places),
                "accommodation_options": len(daily_recs.accommodation),
                "cafe_options": len(daily_recs.cafes)
            }
        }
        
    except Exception as e:
        logger.error(f"Error getting daily recommendations: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get daily recommendations: {str(e)}")

@router.get("/place-details/{place_id}")
async def get_place_details(place_id: str):
    """Get detailed information about a specific place"""
    
    try:
        places_service = get_google_places_service()
        
        details = await places_service.get_place_details(place_id)
        
        if not details:
            raise HTTPException(status_code=404, detail="Place not found")
        
        return {
            "place_id": place_id,
            "details": details
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting place details: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get place details: {str(e)}")

@router.get("/test-connection")
async def test_google_places_connection():
    """Test Google Places API connection"""
    
    try:
        places_service = get_google_places_service()
        
        if not places_service.gmaps:
            return {
                "status": "error",
                "message": "Google Maps client not initialized",
                "suggestions": [
                    "Check GOOGLE_MAPS_API_KEY in environment variables",
                    "Verify API key has Places API enabled",
                    "Ensure billing is set up for the Google Cloud project"
                ]
            }
        
        # Test with a simple request (Kandy coordinates)
        test_places = await places_service.find_places_near_location(
            lat=7.2906,
            lng=80.6337,
            place_type=PlaceType.RESTAURANT,
            budget_level="medium",
            radius=2000,
            max_results=1
        )
        
        return {
            "status": "success",
            "message": "Google Places API connection successful",
            "test_results": f"Found {len(test_places)} test place(s)",
            "api_key_status": "Configured" if places_service.settings.GOOGLE_MAPS_API_KEY else "Missing"
        }
        
    except Exception as e:
        logger.error(f"Google Places API test failed: {e}")
        return {
            "status": "error",
            "message": f"Connection test failed: {str(e)}",
            "suggestions": [
                "Verify Google Maps API key is correct",
                "Check if Places API is enabled",
                "Ensure sufficient quota/credits"
            ]
        }
