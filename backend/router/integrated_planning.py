"""
Integrated Travel Planning Router
Combines clustering with modular enhancements (places, weather, transport, etc.)
Designed for extensible integration of additional services
"""

from fastapi import APIRouter, HTTPException, Query
from typing import Dict, Any, Optional, List
import logging
import time

from services.integrated_planning_service import (
    get_integrated_planning_service,
    IntegratedPlanningRequest,
    IntegratedPlanningResponse,
    EnhancementType,
    EnhancementConfig
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/integrated-planning", tags=["Integrated Planning"])

@router.post("/plan", response_model=IntegratedPlanningResponse)
async def create_integrated_travel_plan(request: IntegratedPlanningRequest):
    """
    Create integrated travel plan with clustering and configurable enhancements
    
    This endpoint combines:
    - Base clustering (attractions grouped geographically)
    - Places enhancement (restaurants, hotels via Google Places)
    - Weather enhancement (forecast and recommendations) [Coming Soon]
    - Transport enhancement (local transport options) [Coming Soon]
    
    **Modular Design**: Enable/disable enhancements as needed
    """
    
    try:
        planning_service = get_integrated_planning_service()
        
        logger.info(f"Creating integrated plan for query: {request.query}")
        
        # Validate request
        if not request.interests:
            raise HTTPException(
                status_code=400, 
                detail="At least one interest must be specified"
            )
        
        if request.trip_duration_days < 1 or request.trip_duration_days > 30:
            raise HTTPException(
                status_code=400,
                detail="Trip duration must be between 1 and 30 days"
            )
        
        # Create integrated plan
        integrated_plan = await planning_service.create_integrated_plan(request)
        
        logger.info(f"Successfully created integrated plan with {len(integrated_plan.enhancements_applied)} enhancements")
        
        return integrated_plan
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to create integrated plan: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to create integrated travel plan: {str(e)}"
        )

@router.post("/plan-with-places")
async def create_plan_with_places_only(
    query: str,
    interests: List[str],
    trip_duration_days: int,
    budget_level: str = "medium",
    daily_travel_preference: str = "balanced",
    max_attractions_per_day: int = 4,
    group_size: int = 2,
    
    # Places configuration
    places_search_radius_km: int = Query(5, description="Search radius for places", le=20),
    include_breakfast: bool = Query(True, description="Include breakfast recommendations"),
    include_lunch: bool = Query(True, description="Include lunch recommendations"),
    include_dinner: bool = Query(True, description="Include dinner recommendations"),
    include_accommodation: bool = Query(True, description="Include accommodation recommendations"),
    include_cafes: bool = Query(True, description="Include cafe recommendations")
):
    """
    Simplified endpoint for plan with places only
    Equivalent to the integrated endpoint with only places enhancement enabled
    """
    
    try:
        # Create request with only places enhancement enabled
        request = IntegratedPlanningRequest(
            query=query,
            interests=interests,
            trip_duration_days=trip_duration_days,
            budget_level=budget_level,
            daily_travel_preference=daily_travel_preference,
            max_attractions_per_day=max_attractions_per_day,
            group_size=group_size,
            enhancements={
                EnhancementType.PLACES: EnhancementConfig(
                    enabled=True,
                    priority=1,
                    config={
                        "search_radius_km": places_search_radius_km,
                        "include_breakfast": include_breakfast,
                        "include_lunch": include_lunch,
                        "include_dinner": include_dinner,
                        "include_accommodation": include_accommodation,
                        "include_cafes": include_cafes
                    }
                ),
                EnhancementType.WEATHER: EnhancementConfig(enabled=False),
                EnhancementType.TRANSPORT: EnhancementConfig(enabled=False)
            }
        )
        
        # Create plan
        integrated_plan = await create_integrated_travel_plan(request)
        
        # Return simplified response format
        return {
            "query": query,
            "total_days": integrated_plan.base_plan.get("total_days", 0),
            "total_attractions": integrated_plan.base_plan.get("total_attractions", 0),
            "daily_itineraries": integrated_plan.daily_itineraries,
            "places_stats": integrated_plan.stats.get("enhancements", {}).get("places", {}),
            "processing_time_ms": integrated_plan.total_processing_time_ms,
            "enhancements_applied": integrated_plan.enhancements_applied
        }
        
    except Exception as e:
        logger.error(f"Failed to create plan with places: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to create plan with places: {str(e)}"
        )

@router.get("/enhancement-modules")
async def get_available_enhancement_modules():
    """Get list of available enhancement modules and their configurations"""
    
    return {
        "available_modules": [
            {
                "type": "places",
                "name": "Google Places Integration",
                "description": "Adds restaurant and accommodation recommendations",
                "status": "active",
                "config_options": {
                    "search_radius_km": "Search radius in kilometers (1-20)",
                    "include_breakfast": "Include breakfast recommendations",
                    "include_lunch": "Include lunch recommendations", 
                    "include_dinner": "Include dinner recommendations",
                    "include_accommodation": "Include accommodation recommendations",
                    "include_cafes": "Include cafe recommendations"
                }
            },
            {
                "type": "weather",
                "name": "Weather Forecast Integration",
                "description": "Adds weather forecasts and recommendations",
                "status": "coming_soon",
                "config_options": {
                    "forecast_days": "Number of days to forecast (1-14)"
                }
            },
            {
                "type": "transport",
                "name": "Transport Information",
                "description": "Adds local transport options and routes",
                "status": "coming_soon",
                "config_options": {
                    "include_local_transport": "Include local transport recommendations"
                }
            },
            {
                "type": "events",
                "name": "Local Events Integration",
                "description": "Adds local events and festivals",
                "status": "planned",
                "config_options": {}
            },
            {
                "type": "budget",
                "name": "Budget Optimization",
                "description": "Optimizes plan based on budget constraints",
                "status": "planned",
                "config_options": {}
            }
        ],
        "usage_examples": {
            "places_only": {
                "endpoint": "/integrated-planning/plan-with-places",
                "description": "Simple endpoint for clustering + places"
            },
            "full_integration": {
                "endpoint": "/integrated-planning/plan",
                "description": "Full modular endpoint with all enhancement options"
            }
        }
    }

@router.get("/test-enhancements")
async def test_enhancement_modules():
    """Test connectivity of all enhancement modules"""
    
    try:
        planning_service = get_integrated_planning_service()
        
        results = {}
        
        # Test Places module
        try:
            places_module = planning_service.enhancement_modules[EnhancementType.PLACES]
            # Simple test - check if Google Places service is initialized
            if hasattr(places_module.places_service, 'gmaps') and places_module.places_service.gmaps:
                results["places"] = {
                    "status": "available",
                    "message": "Google Places API connected"
                }
            else:
                results["places"] = {
                    "status": "error", 
                    "message": "Google Places API not initialized"
                }
        except Exception as e:
            results["places"] = {
                "status": "error",
                "message": f"Places module error: {str(e)}"
            }
        
        # Test Weather module (placeholder)
        results["weather"] = {
            "status": "placeholder",
            "message": "Weather module ready for implementation"
        }
        
        # Test Transport module (placeholder)
        results["transport"] = {
            "status": "placeholder", 
            "message": "Transport module ready for implementation"
        }
        
        return {
            "test_results": results,
            "overall_status": "operational" if results["places"]["status"] == "available" else "partial",
            "recommendations": [
                "Places enhancement is ready to use",
                "Weather and transport modules are prepared for future implementation",
                "Use /integrated-planning/plan-with-places for immediate clustering + places functionality"
            ]
        }
        
    except Exception as e:
        logger.error(f"Enhancement test failed: {e}")
        return {
            "test_results": {},
            "overall_status": "error",
            "error": str(e)
        }

@router.post("/validate-request")
async def validate_planning_request(request: IntegratedPlanningRequest):
    """Validate a planning request without executing it"""
    
    try:
        validation_results = {
            "valid": True,
            "issues": [],
            "warnings": [],
            "estimated_processing_time_ms": 0
        }
        
        # Validate basic parameters
        if not request.interests:
            validation_results["valid"] = False
            validation_results["issues"].append("At least one interest must be specified")
        
        if request.trip_duration_days < 1 or request.trip_duration_days > 30:
            validation_results["valid"] = False
            validation_results["issues"].append("Trip duration must be between 1 and 30 days")
        
        if len(request.query.strip()) < 10:
            validation_results["warnings"].append("Query is quite short - consider adding more details")
        
        # Validate enhancement configurations
        enabled_enhancements = [
            enhancement_type for enhancement_type, config in request.enhancements.items()
            if config.enabled
        ]
        
        if not enabled_enhancements:
            validation_results["warnings"].append("No enhancements enabled - you'll get base clustering only")
        
        # Estimate processing time
        base_time = 1000  # Base clustering time
        places_time = 2000 if EnhancementType.PLACES in enabled_enhancements else 0
        weather_time = 500 if EnhancementType.WEATHER in enabled_enhancements else 0
        transport_time = 300 if EnhancementType.TRANSPORT in enabled_enhancements else 0
        
        validation_results["estimated_processing_time_ms"] = base_time + places_time + weather_time + transport_time
        
        # Add recommendations
        validation_results["recommendations"] = []
        
        if EnhancementType.PLACES not in enabled_enhancements:
            validation_results["recommendations"].append("Consider enabling places enhancement for restaurant and accommodation suggestions")
        
        if request.trip_duration_days > 7 and not request.async_processing:
            validation_results["recommendations"].append("For trips longer than 7 days, consider enabling async_processing for better performance")
        
        return validation_results
        
    except Exception as e:
        logger.error(f"Request validation failed: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to validate request: {str(e)}"
        )
