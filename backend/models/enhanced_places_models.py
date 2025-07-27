"""
Enhanced models for clustered recommendations with Google Places integration
Extends existing models to include restaurant, accommodation, and place recommendations
"""

from pydantic import BaseModel, Field
from typing import Dict, Any, Optional, List
from enum import Enum

class PlaceType(str, Enum):
    RESTAURANT = "restaurant"
    LODGING = "lodging"
    CAFE = "cafe"
    TOURIST_ATTRACTION = "tourist_attraction"

class MealType(str, Enum):
    BREAKFAST = "breakfast"
    LUNCH = "lunch"
    DINNER = "dinner"

class PlaceRecommendation(BaseModel):
    """Single place recommendation from Google Places"""
    name: str = Field(..., description="Name of the place")
    rating: float = Field(0.0, description="Google rating (0-5)")
    price_level: Optional[int] = Field(None, description="Price level (0-4, where 0=free, 4=very expensive)")
    place_id: str = Field(..., description="Google Places ID")
    latitude: float = Field(..., description="Latitude")
    longitude: float = Field(..., description="Longitude")
    types: List[str] = Field(default_factory=list, description="Place types from Google")
    address: str = Field("", description="Address or vicinity")
    phone: Optional[str] = Field(None, description="Phone number")
    website: Optional[str] = Field(None, description="Website URL")
    opening_hours: Optional[Dict[str, Any]] = Field(None, description="Opening hours information")
    photos: List[str] = Field(default_factory=list, description="Photo URLs")
    distance_km: Optional[float] = Field(None, description="Distance from cluster center in km")
    
    def get_price_indicator(self) -> str:
        """Get user-friendly price indicator"""
        if self.price_level is None:
            return "💲 Price not available"
        indicators = ["💲 Free", "💲 Budget", "💲💲 Moderate", "💲💲💲 Expensive", "💲💲💲💲 Very Expensive"]
        return indicators[min(self.price_level, 4)]
    
    def get_rating_stars(self) -> str:
        """Get star rating display"""
        if self.rating == 0:
            return "⭐ Not rated"
        full_stars = int(self.rating)
        half_star = "½" if self.rating - full_stars >= 0.5 else ""
        return "⭐" * full_stars + half_star + f" ({self.rating})"

class DailyPlaceRecommendations(BaseModel):
    """Place recommendations for a single day/cluster"""
    day: int = Field(..., description="Day number")
    cluster_center_lat: float = Field(..., description="Cluster center latitude")
    cluster_center_lng: float = Field(..., description="Cluster center longitude")
    breakfast_places: List[PlaceRecommendation] = Field(default_factory=list, description="Breakfast recommendations")
    lunch_places: List[PlaceRecommendation] = Field(default_factory=list, description="Lunch recommendations") 
    dinner_places: List[PlaceRecommendation] = Field(default_factory=list, description="Dinner recommendations")
    accommodation: List[PlaceRecommendation] = Field(default_factory=list, description="Hotel/accommodation recommendations")
    cafes: List[PlaceRecommendation] = Field(default_factory=list, description="Cafe recommendations for breaks")
    
    def get_total_recommendations(self) -> int:
        """Get total number of place recommendations for this day"""
        return (len(self.breakfast_places) + len(self.lunch_places) + 
                len(self.dinner_places) + len(self.accommodation) + len(self.cafes))

class EnhancedDayItinerary(BaseModel):
    """Enhanced daily itinerary with clustered attractions and place recommendations"""
    day: int = Field(..., description="Day number")
    cluster_info: Dict[str, Any] = Field(..., description="Cluster information")
    attractions: List[Dict[str, Any]] = Field(..., description="Attraction information") 
    total_travel_distance_km: float = Field(..., description="Total travel distance for the day")
    estimated_total_time_hours: float = Field(..., description="Estimated total time for the day")
    place_recommendations: Optional[DailyPlaceRecommendations] = Field(None, description="Restaurant and accommodation recommendations")
    
    def get_day_summary(self) -> str:
        """Get a summary of the day's plan"""
        attraction_count = len(self.attractions)
        place_count = self.place_recommendations.get_total_recommendations() if self.place_recommendations else 0
        
        return f"Day {self.day}: {attraction_count} attractions, {place_count} dining/accommodation options, {self.total_travel_distance_km}km travel"

class EnhancedClusteredRecommendationResponse(BaseModel):
    """Enhanced response with clustered recommendations and place suggestions"""
    query: str = Field(..., description="Original user query")
    total_days: int = Field(..., description="Total number of days planned")
    total_attractions: int = Field(..., description="Total number of attractions")
    daily_itineraries: List[EnhancedDayItinerary] = Field(..., description="Day-by-day itineraries with places")
    overall_stats: Dict[str, Any] = Field(..., description="Overall statistics")
    processing_time_ms: float = Field(..., description="Processing time in milliseconds")
    place_recommendations_included: bool = Field(True, description="Whether place recommendations are included")
    budget_level: str = Field("medium", description="Budget level used for place recommendations")
    
    def get_summary(self) -> Dict[str, Any]:
        """Get a comprehensive summary of the travel plan"""
        total_restaurants = sum(
            len(day.place_recommendations.breakfast_places) + 
            len(day.place_recommendations.lunch_places) + 
            len(day.place_recommendations.dinner_places)
            for day in self.daily_itineraries 
            if day.place_recommendations
        )
        
        total_accommodation = sum(
            len(day.place_recommendations.accommodation)
            for day in self.daily_itineraries
            if day.place_recommendations
        )
        
        total_distance = sum(day.total_travel_distance_km for day in self.daily_itineraries)
        
        return {
            "total_days": self.total_days,
            "total_attractions": self.total_attractions,
            "total_restaurants": total_restaurants,
            "total_accommodation_options": total_accommodation,
            "total_travel_distance_km": round(total_distance, 2),
            "budget_level": self.budget_level,
            "processing_time_ms": self.processing_time_ms
        }

class PlaceSearchRequest(BaseModel):
    """Request for searching places near a location"""
    latitude: float = Field(..., description="Latitude of search center")
    longitude: float = Field(..., description="Longitude of search center")
    place_type: PlaceType = Field(..., description="Type of place to search for")
    budget_level: str = Field("medium", description="Budget level (budget/medium/luxury)")
    radius: int = Field(5000, description="Search radius in meters", le=50000)
    max_results: int = Field(5, description="Maximum number of results", le=20)
    meal_type: Optional[MealType] = Field(None, description="Meal type for restaurant searches")

class PlaceSearchResponse(BaseModel):
    """Response for place search"""
    search_location: Dict[str, float] = Field(..., description="Search center coordinates")
    place_type: PlaceType = Field(..., description="Type of places searched")
    budget_level: str = Field(..., description="Budget level used")
    radius_km: float = Field(..., description="Search radius in kilometers") 
    results_count: int = Field(..., description="Number of results found")
    places: List[PlaceRecommendation] = Field(..., description="Found places")
    search_time_ms: float = Field(..., description="Search time in milliseconds")
