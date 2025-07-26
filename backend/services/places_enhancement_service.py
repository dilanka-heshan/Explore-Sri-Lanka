"""
Places Enhancement Service
Takes existing cluster results and adds Google Places recommendations when requested
Works as a separate service without modifying the main clustering logic
"""

from typing import Dict, List, Any, Optional
import logging
from pydantic import BaseModel, Field
from services.google_places_service import get_google_places_service
from models.enhanced_places_models import DailyPlaceRecommendations, PlaceRecommendation, PlaceType, MealType

logger = logging.getLogger(__name__)

class ClusterPlacesRequest(BaseModel):
    """Request to add places to existing cluster results"""
    cluster_results: Dict[str, Any] = Field(..., description="Original cluster results from /clustered-recommendations/plan")
    budget_level: str = Field("medium", description="Budget level (budget/medium/luxury)")
    place_search_radius_km: int = Field(5, description="Search radius for places in kilometers", le=20)
    include_breakfast: bool = Field(True, description="Include breakfast recommendations")
    include_lunch: bool = Field(True, description="Include lunch recommendations") 
    include_dinner: bool = Field(True, description="Include dinner recommendations")
    include_accommodation: bool = Field(True, description="Include accommodation recommendations")
    include_cafes: bool = Field(True, description="Include cafe recommendations")

class EnhancedClusterWithPlaces(BaseModel):
    """Enhanced cluster results with place recommendations"""
    original_plan: Dict[str, Any] = Field(..., description="Original cluster plan")
    place_recommendations: List[DailyPlaceRecommendations] = Field(..., description="Daily place recommendations")
    enhancement_stats: Dict[str, Any] = Field(..., description="Statistics about added places")
    processing_time_ms: float = Field(..., description="Time taken to enhance with places")

class PlacesEnhancementService:
    """Service to enhance existing cluster results with Google Places"""
    
    def __init__(self):
        self.places_service = get_google_places_service()
    
    async def enhance_cluster_with_places(
        self, 
        cluster_results: Dict[str, Any],
        budget_level: str = "medium",
        place_search_radius_km: int = 5,
        meal_preferences: Dict[str, bool] = None
    ) -> EnhancedClusterWithPlaces:
        """
        Enhance existing cluster results with Google Places recommendations
        
        Args:
            cluster_results: Output from /clustered-recommendations/plan endpoint
            budget_level: Budget level for place filtering
            place_search_radius_km: Search radius for places
            meal_preferences: Dict specifying which meal types to include
        """
        import time
        start_time = time.time()
        
        if meal_preferences is None:
            meal_preferences = {
                "breakfast": True,
                "lunch": True, 
                "dinner": True,
                "accommodation": True,
                "cafes": True
            }
        
        try:
            daily_itineraries = cluster_results.get('daily_itineraries', [])
            place_recommendations = []
            
            total_places_added = 0
            
            for day_plan in daily_itineraries:
                day = day_plan['day']
                cluster_info = day_plan['cluster_info']
                
                # Extract cluster center coordinates
                center_lat = cluster_info['center_lat']
                center_lng = cluster_info['center_lng']
                
                logger.info(f"Getting place recommendations for Day {day} at ({center_lat}, {center_lng})")
                
                # Get places for this day's cluster
                daily_places = await self._get_selective_daily_recommendations(
                    day=day,
                    center_lat=center_lat,
                    center_lng=center_lng,
                    budget_level=budget_level,
                    radius_km=place_search_radius_km,
                    meal_preferences=meal_preferences
                )
                
                place_recommendations.append(daily_places)
                total_places_added += daily_places.get_total_recommendations()
                
                logger.info(f"Added {daily_places.get_total_recommendations()} places for Day {day}")
            
            processing_time = (time.time() - start_time) * 1000
            
            # Calculate enhancement statistics
            enhancement_stats = {
                "total_days_enhanced": len(place_recommendations),
                "total_places_added": total_places_added,
                "average_places_per_day": round(total_places_added / len(place_recommendations), 1) if place_recommendations else 0,
                "budget_level_used": budget_level,
                "search_radius_km": place_search_radius_km,
                "meal_preferences": meal_preferences,
                "google_places_api_used": True
            }
            
            return EnhancedClusterWithPlaces(
                original_plan=cluster_results,
                place_recommendations=place_recommendations,
                enhancement_stats=enhancement_stats,
                processing_time_ms=processing_time
            )
            
        except Exception as e:
            logger.error(f"Error enhancing cluster with places: {e}")
            raise
    
    async def _get_selective_daily_recommendations(
        self,
        day: int,
        center_lat: float,
        center_lng: float,
        budget_level: str,
        radius_km: int,
        meal_preferences: Dict[str, bool]
    ) -> DailyPlaceRecommendations:
        """Get daily recommendations based on user preferences"""
        
        radius_meters = radius_km * 1000
        
        # Initialize empty lists
        breakfast_places = []
        lunch_places = []
        dinner_places = []
        accommodation = []
        cafes = []
        
        # Get breakfast places if requested
        if meal_preferences.get("breakfast", True):
            breakfast_places = await self.places_service.find_places_near_location(
                lat=center_lat,
                lng=center_lng,
                place_type=PlaceType.RESTAURANT,  # Use enum instead of string
                budget_level=budget_level,
                radius=radius_meters,
                max_results=3,
                meal_type=MealType.BREAKFAST  # Use enum instead of string
            )
        
        # Get lunch places if requested
        if meal_preferences.get("lunch", True):
            lunch_places = await self.places_service.find_places_near_location(
                lat=center_lat,
                lng=center_lng,
                place_type=PlaceType.RESTAURANT,  # Use enum instead of string
                budget_level=budget_level,
                radius=radius_meters,
                max_results=4,
                meal_type=MealType.LUNCH  # Use enum instead of string
            )
        
        # Get dinner places if requested
        if meal_preferences.get("dinner", True):
            dinner_places = await self.places_service.find_places_near_location(
                lat=center_lat,
                lng=center_lng,
                place_type=PlaceType.RESTAURANT,  # Use enum instead of string
                budget_level=budget_level,
                radius=radius_meters,
                max_results=4,
                meal_type=MealType.DINNER  # Use enum instead of string
            )
        
        # Get accommodation if requested
        if meal_preferences.get("accommodation", True):
            accommodation = await self.places_service.find_places_near_location(
                lat=center_lat,
                lng=center_lng,
                place_type=PlaceType.LODGING,  # Use enum instead of string
                budget_level=budget_level,
                radius=radius_meters * 2,  # Wider radius for hotels
                max_results=3
            )
        
        # Get cafes if requested
        if meal_preferences.get("cafes", True):
            cafes = await self.places_service.find_places_near_location(
                lat=center_lat,
                lng=center_lng,
                place_type=PlaceType.CAFE,  # Use enum instead of string
                budget_level=budget_level,
                radius=radius_meters,
                max_results=3
            )
        
        return DailyPlaceRecommendations(
            day=day,
            cluster_center_lat=center_lat,
            cluster_center_lng=center_lng,
            breakfast_places=breakfast_places,
            lunch_places=lunch_places,
            dinner_places=dinner_places,
            accommodation=accommodation,
            cafes=cafes
        )
    
    async def get_places_for_single_day(
        self,
        day: int,
        center_lat: float,
        center_lng: float,
        budget_level: str = "medium",
        radius_km: int = 5
    ) -> DailyPlaceRecommendations:
        """Get places for a single day/cluster"""
        
        return await self.places_service.get_daily_recommendations(
            day=day,
            cluster_center_lat=center_lat,
            cluster_center_lng=center_lng,
            budget_level=budget_level,
            radius=radius_km * 1000
        )

# Global service instance
_places_enhancement_service = None

def get_places_enhancement_service() -> PlacesEnhancementService:
    """Get or create places enhancement service instance"""
    global _places_enhancement_service
    if _places_enhancement_service is None:
        _places_enhancement_service = PlacesEnhancementService()
    return _places_enhancement_service
