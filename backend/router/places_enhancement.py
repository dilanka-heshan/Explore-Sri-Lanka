"""
Places Enhancement Router
Provides endpoints to enhance existing cluster results with Google Places recommendations
Works independently from the main clustering endpoint
"""

from fastapi import APIRouter, HTTPException, Query
from typing import Dict, Any, Optional
import logging
import time
from services.places_enhancement_service import (
    get_places_enhancement_service,
    ClusterPlacesRequest,
    EnhancedClusterWithPlaces
)
from services.google_places_service import get_google_places_service
from models.enhanced_places_models import DailyPlaceRecommendations

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/places-enhancement", tags=["Places Enhancement"])

@router.post("/enhance-cluster", response_model=EnhancedClusterWithPlaces)
async def enhance_cluster_with_places(request: ClusterPlacesRequest):
    """
    Enhance existing cluster results with Google Places recommendations
    
    Takes the output from /clustered-recommendations/plan and adds place suggestions
    Only adds places when explicitly requested by the user
    """
    try:
        enhancement_service = get_places_enhancement_service()
        
        # Build meal preferences from request
        meal_preferences = {
            "breakfast": request.include_breakfast,
            "lunch": request.include_lunch,
            "dinner": request.include_dinner,
            "accommodation": request.include_accommodation,
            "cafes": request.include_cafes
        }
        
        enhanced_results = await enhancement_service.enhance_cluster_with_places(
            cluster_results=request.cluster_results,
            budget_level=request.budget_level,
            place_search_radius_km=request.place_search_radius_km,
            meal_preferences=meal_preferences
        )
        
        logger.info(f"Enhanced cluster plan with {enhanced_results.enhancement_stats['total_places_added']} places")
        
        return enhanced_results
        
    except Exception as e:
        logger.error(f"Error enhancing cluster with places: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to enhance cluster: {str(e)}")

@router.post("/add-places-to-day")
async def add_places_to_specific_day(
    day: int,
    center_lat: float,
    center_lng: float,
    budget_level: str = Query("medium", description="Budget level"),
    radius_km: int = Query(5, description="Search radius in kilometers"),
    include_breakfast: bool = Query(True, description="Include breakfast places"),
    include_lunch: bool = Query(True, description="Include lunch places"),
    include_dinner: bool = Query(True, description="Include dinner places"),
    include_accommodation: bool = Query(True, description="Include accommodation"),
    include_cafes: bool = Query(True, description="Include cafes")
):
    """
    Add places to a specific day/cluster
    
    Useful for adding places to individual days of an existing plan
    """
    try:
        enhancement_service = get_places_enhancement_service()
        
        meal_preferences = {
            "breakfast": include_breakfast,
            "lunch": include_lunch,
            "dinner": include_dinner,
            "accommodation": include_accommodation,
            "cafes": include_cafes
        }
        
        daily_places = await enhancement_service._get_selective_daily_recommendations(
            day=day,
            center_lat=center_lat,
            center_lng=center_lng,
            budget_level=budget_level,
            radius_km=radius_km,
            meal_preferences=meal_preferences
        )
        
        return {
            "day": day,
            "location": {"latitude": center_lat, "longitude": center_lng},
            "search_params": {
                "budget_level": budget_level,
                "radius_km": radius_km,
                "meal_preferences": meal_preferences
            },
            "places": daily_places,
            "summary": {
                "total_places": daily_places.get_total_recommendations(),
                "breakfast_options": len(daily_places.breakfast_places),
                "lunch_options": len(daily_places.lunch_places),
                "dinner_options": len(daily_places.dinner_places),
                "accommodation_options": len(daily_places.accommodation),
                "cafe_options": len(daily_places.cafes)
            }
        }
        
    except Exception as e:
        logger.error(f"Error adding places to day {day}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to add places to day: {str(e)}")

@router.get("/places-for-coordinates/{lat}/{lng}")
async def get_places_for_coordinates(
    lat: float,
    lng: float,
    budget_level: str = Query("medium", description="Budget level"),
    radius_km: int = Query(5, description="Search radius in kilometers"),
    place_types: str = Query("all", description="Comma-separated place types (restaurant,lodging,cafe) or 'all'"),
    max_results_per_type: int = Query(5, description="Maximum results per place type")
):
    """
    Get places for specific coordinates
    
    Useful for testing or getting places for custom locations
    """
    try:
        places_service = get_google_places_service()
        
        # Parse place types
        if place_types.lower() == "all":
            types_to_search = ["restaurant", "lodging", "cafe"]
        else:
            types_to_search = [t.strip() for t in place_types.split(",")]
        
        results = {}
        total_places = 0
        
        for place_type in types_to_search:
            try:
                places = await places_service.find_places_near_location(
                    lat=lat,
                    lng=lng,
                    place_type=place_type,
                    budget_level=budget_level,
                    radius=radius_km * 1000,
                    max_results=max_results_per_type
                )
                results[place_type] = places
                total_places += len(places)
                
            except Exception as e:
                logger.warning(f"Error getting {place_type} places: {e}")
                results[place_type] = []
        
        return {
            "location": {"latitude": lat, "longitude": lng},
            "search_params": {
                "budget_level": budget_level,
                "radius_km": radius_km,
                "place_types": types_to_search,
                "max_results_per_type": max_results_per_type
            },
            "places_by_type": results,
            "summary": {
                "total_places": total_places,
                "types_searched": len(types_to_search)
            }
        }
        
    except Exception as e:
        logger.error(f"Error getting places for coordinates: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get places: {str(e)}")

@router.post("/bulk-enhance-clusters")
async def bulk_enhance_multiple_clusters(
    cluster_plans: list[Dict[str, Any]],
    budget_level: str = Query("medium", description="Budget level"),
    radius_km: int = Query(5, description="Search radius in kilometers")
):
    """
    Enhance multiple cluster plans with places in one request
    
    Useful for batch processing multiple travel plans
    """
    try:
        enhancement_service = get_places_enhancement_service()
        
        enhanced_plans = []
        total_processing_time = 0
        
        for i, cluster_plan in enumerate(cluster_plans):
            start_time = time.time()
            
            enhanced_plan = await enhancement_service.enhance_cluster_with_places(
                cluster_results=cluster_plan,
                budget_level=budget_level,
                place_search_radius_km=radius_km
            )
            
            processing_time = (time.time() - start_time) * 1000
            total_processing_time += processing_time
            
            enhanced_plans.append({
                "plan_index": i,
                "enhanced_plan": enhanced_plan,
                "processing_time_ms": processing_time
            })
        
        return {
            "enhanced_plans": enhanced_plans,
            "summary": {
                "total_plans_processed": len(cluster_plans),
                "total_processing_time_ms": total_processing_time,
                "average_processing_time_ms": total_processing_time / len(cluster_plans) if cluster_plans else 0
            }
        }
        
    except Exception as e:
        logger.error(f"Error bulk enhancing clusters: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to bulk enhance: {str(e)}")

@router.get("/enhancement-stats/{cluster_id}")
async def get_enhancement_stats(cluster_id: str):
    """
    Get statistics about places that would be added to a cluster
    
    Returns counts and estimates without actually fetching the places
    """
    try:
        # This is a placeholder for getting cluster details by ID
        # In a real implementation, you'd fetch cluster details from your database
        
        return {
            "cluster_id": cluster_id,
            "estimated_places": {
                "restaurants_per_day": "3-12 depending on budget and location",
                "hotels_per_day": "3-8 depending on budget and area",
                "cafes_per_day": "2-5 depending on urban/rural setting"
            },
            "factors_affecting_results": [
                "Budget level (budget/medium/luxury)",
                "Search radius (larger radius = more options)",
                "Location density (urban vs rural)",
                "Google Places API data availability for Sri Lanka"
            ],
            "recommendations": {
                "urban_areas": "Use 3-5km radius for good variety",
                "rural_areas": "Use 10-15km radius for sufficient options",
                "budget_filtering": "Adjust price_level based on budget constraints"
            }
        }
        
    except Exception as e:
        logger.error(f"Error getting enhancement stats: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get stats: {str(e)}")

@router.get("/test-places-api")
async def test_google_places_api():
    """
    Test Google Places API connectivity and functionality
    
    Runs a simple test to verify the API is working
    """
    try:
        places_service = get_google_places_service()
        
        if not places_service.gmaps:
            return {
                "status": "error",
                "message": "Google Maps client not initialized",
                "suggestions": [
                    "Check GOOGLE_MAPS_API_KEY environment variable",
                    "Verify API key has Places API enabled",
                    "Ensure billing is configured"
                ]
            }
        
        # Test with Kandy coordinates
        test_lat, test_lng = 7.2906, 80.6337
        
        test_restaurants = await places_service.find_places_near_location(
            lat=test_lat,
            lng=test_lng,
            place_type="restaurant",
            budget_level="medium",
            radius=2000,
            max_results=2
        )
        
        return {
            "status": "success",
            "message": "Google Places API is working",
            "test_location": {"latitude": test_lat, "longitude": test_lng, "name": "Kandy"},
            "test_results": {
                "restaurants_found": len(test_restaurants),
                "sample_restaurant": test_restaurants[0].name if test_restaurants else None
            },
            "api_capabilities": [
                "Place search by type and location",
                "Budget-based filtering", 
                "Radius-based search",
                "Restaurant, hotel, and cafe discovery"
            ]
        }
        
    except Exception as e:
        logger.error(f"Places API test failed: {e}")
        return {
            "status": "error",
            "message": f"API test failed: {str(e)}",
            "troubleshooting": [
                "Verify Google Maps API key is correct",
                "Check if Places API is enabled in Google Cloud Console",
                "Ensure sufficient API quota/credits",
                "Check internet connectivity"
            ]
        }
