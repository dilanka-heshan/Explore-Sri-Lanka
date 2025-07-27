"""
Google Places Service for enhanced travel recommendations
Provides restaurants, hotels, and accommodation suggestions for each cluster/day
"""

import googlemaps
import logging
from typing import List, Dict, Any, Optional, Tuple
from config import Settings
from models.enhanced_places_models import (
    PlaceType, 
    MealType, 
    PlaceRecommendation, 
    DailyPlaceRecommendations
)

logger = logging.getLogger(__name__)

class GooglePlacesService:
    """Service for finding nearby places using Google Places API"""
    
    def __init__(self):
        self.settings = Settings()
        try:
            self.gmaps = googlemaps.Client(key=self.settings.GOOGLE_MAPS_API_KEY)
            logger.info("Google Maps client initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize Google Maps client: {e}")
            self.gmaps = None
    
    def _get_budget_price_range(self, budget_level: str) -> Tuple[int, int]:
        """Map budget level to Google Places price range (0-4)"""
        budget_mapping = {
            "budget": (0, 2),      # Free to moderate
            "low": (0, 2),
            "medium": (1, 3),      # Moderate to expensive  
            "mid_range": (1, 3),
            "high": (2, 4),        # Expensive to very expensive
            "luxury": (3, 4)       # Very expensive only
        }
        return budget_mapping.get(budget_level.lower(), (1, 3))
    
    def _get_meal_keywords(self, meal_type: MealType) -> List[str]:
        """Get search keywords for different meal types"""
        meal_keywords = {
            MealType.BREAKFAST: ["breakfast", "cafe", "bakery", "tea"],
            MealType.LUNCH: ["lunch", "restaurant", "local food", "rice and curry"],
            MealType.DINNER: ["dinner", "restaurant", "fine dining", "seafood"]
        }
        return meal_keywords.get(meal_type, ["restaurant"])
    
    async def find_places_near_location(
        self,
        lat: float,
        lng: float,
        place_type: PlaceType,
        budget_level: str = "medium",
        radius: int = 5000,
        max_results: int = 5,
        meal_type: Optional[MealType] = None
    ) -> List[PlaceRecommendation]:
        """Find places near a specific location"""
        
        if not self.gmaps:
            logger.warning("Google Maps client not available, returning empty results")
            return []
        
        try:
            min_price, max_price = self._get_budget_price_range(budget_level)
            
            # Handle both enum and string inputs for place_type
            place_type_str = place_type.value if hasattr(place_type, 'value') else str(place_type)
            
            # Build search parameters
            search_params = {
                "location": (lat, lng),
                "radius": radius,
                "type": place_type_str,
                "min_price": min_price,
                "max_price": max_price,
                "open_now": False  # Don't restrict to currently open places
            }
            
            # Add meal-specific keywords for restaurants
            if (place_type == PlaceType.RESTAURANT or place_type_str == "restaurant") and meal_type:
                # Handle both enum and string inputs for meal_type
                meal_type_obj = meal_type if hasattr(meal_type, 'value') else MealType(meal_type) if meal_type in [e.value for e in MealType] else None
                if meal_type_obj:
                    keywords = self._get_meal_keywords(meal_type_obj)
                    search_params["keyword"] = " ".join(keywords)
            
            # Perform search
            response = self.gmaps.places_nearby(**search_params)
            
            if not response or 'results' not in response:
                logger.warning(f"No results found for {place_type} near ({lat}, {lng})")
                return []
            
            recommendations = []
            for place in response['results'][:max_results]:
                try:
                    recommendation = self._parse_place_result(place, lat, lng)
                    if recommendation:
                        recommendations.append(recommendation)
                except Exception as e:
                    logger.warning(f"Error parsing place result: {e}")
                    continue
            
            logger.info(f"Found {len(recommendations)} {place_type} recommendations near ({lat}, {lng})")
            return recommendations
            
        except Exception as e:
            logger.error(f"Error finding places near ({lat}, {lng}): {e}")
            return []
    
    def _parse_place_result(
        self, 
        place: Dict[str, Any], 
        origin_lat: float, 
        origin_lng: float
    ) -> Optional[PlaceRecommendation]:
        """Parse a single place result from Google Places API"""
        
        try:
            geometry = place.get('geometry', {})
            location = geometry.get('location', {})
            
            if not location:
                return None
            
            # Calculate distance
            distance_km = self._calculate_distance(
                origin_lat, origin_lng,
                location['lat'], location['lng']
            )
            
            # Extract photos
            photos = []
            if 'photos' in place:
                for photo in place['photos'][:3]:  # Limit to 3 photos
                    photo_ref = photo.get('photo_reference')
                    if photo_ref:
                        photo_url = f"https://maps.googleapis.com/maps/api/place/photo?maxwidth=400&photoreference={photo_ref}&key={self.settings.GOOGLE_MAPS_API_KEY}"
                        photos.append(photo_url)
            
            return PlaceRecommendation(
                name=place.get('name', 'Unknown'),
                rating=place.get('rating', 0.0),
                price_level=place.get('price_level'),
                place_id=place.get('place_id', ''),
                latitude=location['lat'],
                longitude=location['lng'],
                types=place.get('types', []),
                address=place.get('vicinity', ''),
                photos=photos,
                distance_km=distance_km
            )
            
        except Exception as e:
            logger.error(f"Error parsing place result: {e}")
            return None
    
    def _calculate_distance(self, lat1: float, lng1: float, lat2: float, lng2: float) -> float:
        """Calculate distance between two points using Haversine formula"""
        from math import radians, cos, sin, asin, sqrt
        
        # Convert decimal degrees to radians
        lat1, lng1, lat2, lng2 = map(radians, [lat1, lng1, lat2, lng2])
        
        # Haversine formula
        dlng = lng2 - lng1
        dlat = lat2 - lat1
        a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlng/2)**2
        c = 2 * asin(sqrt(a))
        r = 6371  # Radius of earth in kilometers
        
        return round(c * r, 2)
    
    async def get_place_details(self, place_id: str) -> Optional[Dict[str, Any]]:
        """Get detailed information about a specific place"""
        
        if not self.gmaps:
            return None
        
        try:
            fields = [
                'name', 'rating', 'price_level', 'formatted_address',
                'international_phone_number', 'website', 'opening_hours',
                'photos', 'geometry', 'types', 'reviews'
            ]
            
            response = self.gmaps.place(place_id=place_id, fields=fields)
            return response.get('result')
            
        except Exception as e:
            logger.error(f"Error getting place details for {place_id}: {e}")
            return None
    
    async def get_daily_recommendations(
        self,
        day: int,
        cluster_center_lat: float,
        cluster_center_lng: float,
        budget_level: str = "medium",
        radius: int = 5000
    ) -> DailyPlaceRecommendations:
        """Get comprehensive place recommendations for a single day"""
        
        logger.info(f"Getting daily recommendations for day {day} at ({cluster_center_lat}, {cluster_center_lng})")
        
        # Get breakfast places
        breakfast_places = await self.find_places_near_location(
            cluster_center_lat, cluster_center_lng,
            PlaceType.RESTAURANT, budget_level, radius, 3,
            MealType.BREAKFAST
        )
        
        # Get lunch places
        lunch_places = await self.find_places_near_location(
            cluster_center_lat, cluster_center_lng,
            PlaceType.RESTAURANT, budget_level, radius, 4,
            MealType.LUNCH
        )
        
        # Get dinner places
        dinner_places = await self.find_places_near_location(
            cluster_center_lat, cluster_center_lng,
            PlaceType.RESTAURANT, budget_level, radius, 4,
            MealType.DINNER
        )
        
        # Get accommodation
        accommodation = await self.find_places_near_location(
            cluster_center_lat, cluster_center_lng,
            PlaceType.LODGING, budget_level, radius * 2, 3  # Wider radius for hotels
        )
        
        # Get cafes for breaks
        cafes = await self.find_places_near_location(
            cluster_center_lat, cluster_center_lng,
            PlaceType.CAFE, budget_level, radius, 3
        )
        
        return DailyPlaceRecommendations(
            day=day,
            cluster_center_lat=cluster_center_lat,
            cluster_center_lng=cluster_center_lng,
            breakfast_places=breakfast_places,
            lunch_places=lunch_places,
            dinner_places=dinner_places,
            accommodation=accommodation,
            cafes=cafes
        )
    
    async def get_multi_day_recommendations(
        self,
        daily_clusters: List[Dict[str, Any]],
        budget_level: str = "medium"
    ) -> List[DailyPlaceRecommendations]:
        """Get place recommendations for multiple days/clusters"""
        
        recommendations = []
        
        for i, cluster in enumerate(daily_clusters, 1):
            center_lat = cluster.get('center_lat')
            center_lng = cluster.get('center_lng')
            
            if center_lat is None or center_lng is None:
                logger.warning(f"Missing coordinates for day {i} cluster")
                continue
            
            daily_recs = await self.get_daily_recommendations(
                day=i,
                cluster_center_lat=center_lat,
                cluster_center_lng=center_lng,
                budget_level=budget_level
            )
            
            recommendations.append(daily_recs)
        
        return recommendations

# Global instance
_google_places_service = None

def get_google_places_service() -> GooglePlacesService:
    """Get or create Google Places service instance"""
    global _google_places_service
    if _google_places_service is None:
        _google_places_service = GooglePlacesService()
    return _google_places_service
