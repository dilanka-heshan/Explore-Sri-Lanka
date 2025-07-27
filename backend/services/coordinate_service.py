"""
Coordinate Service for Sri Lankan Travel Locations
Provides latitude/longitude lookup for attractions stored in Qdrant
"""
import json
import os
from typing import Dict, Optional, Tuple, List
import logging
from fuzzywuzzy import fuzz

logger = logging.getLogger(__name__)

class CoordinateService:
    """Service to map attraction names to geographic coordinates"""
    
    def __init__(self, locations_file_path: str = None):
        if locations_file_path is None:
            # Default path to sri_lanka_locations.json
            current_dir = os.path.dirname(os.path.abspath(__file__))
            backend_dir = os.path.dirname(current_dir)
            locations_file_path = os.path.join(backend_dir, "data", "sri_lanka_locations.json")
        
        self.locations_file_path = locations_file_path
        self.locations_data: Dict[str, Dict] = {}
        self.name_to_coords: Dict[str, Tuple[float, float]] = {}
        self.category_mapping: Dict[str, List[str]] = {}
        
        # Load the coordinate data
        self._load_locations_data()
        
    def _load_locations_data(self):
        """Load and process the Sri Lanka locations JSON file"""
        try:
            with open(self.locations_file_path, 'r', encoding='utf-8') as file:
                data = json.load(file)
                
            locations = data.get('sri_lanka_travel_locations', [])
            logger.info(f"Loading {len(locations)} Sri Lankan travel locations")
            
            for location in locations:
                name = location.get('name', '').strip()
                latitude = location.get('latitude')
                longitude = location.get('longitude')
                category = location.get('category', 'Unknown')
                
                if name and latitude is not None and longitude is not None:
                    # Store full location data
                    self.locations_data[name.lower()] = location
                    
                    # Store name-to-coordinates mapping
                    self.name_to_coords[name.lower()] = (latitude, longitude)
                    
                    # Build category mapping
                    if category not in self.category_mapping:
                        self.category_mapping[category] = []
                    self.category_mapping[category].append(name)
                    
            logger.info(f"Successfully loaded {len(self.name_to_coords)} locations with coordinates")
            logger.info(f"Categories available: {list(self.category_mapping.keys())}")
            
        except FileNotFoundError:
            logger.error(f"Locations file not found: {self.locations_file_path}")
            raise
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON in locations file: {e}")
            raise
        except Exception as e:
            logger.error(f"Error loading locations data: {e}")
            raise
    
    def get_coordinates(self, attraction_name: str) -> Optional[Tuple[float, float]]:
        """
        Get latitude and longitude for an attraction name
        
        Args:
            attraction_name: Name of the attraction
            
        Returns:
            Tuple of (latitude, longitude) or None if not found
        """
        if not attraction_name:
            return None
            
        # Direct exact match (case insensitive)
        exact_match = self.name_to_coords.get(attraction_name.lower())
        if exact_match:
            return exact_match
        
        # Fuzzy matching for partial names
        best_match = self._fuzzy_search_coordinates(attraction_name)
        if best_match:
            return best_match
            
        logger.warning(f"No coordinates found for attraction: {attraction_name}")
        return None
    
    def _fuzzy_search_coordinates(self, attraction_name: str, threshold: int = 80) -> Optional[Tuple[float, float]]:
        """
        Find coordinates using fuzzy string matching
        
        Args:
            attraction_name: Name to search for
            threshold: Minimum similarity score (0-100)
            
        Returns:
            Tuple of (latitude, longitude) or None
        """
        best_score = 0
        best_match = None
        
        for stored_name, coords in self.name_to_coords.items():
            # Calculate similarity score
            score = fuzz.partial_ratio(attraction_name.lower(), stored_name)
            
            if score > best_score and score >= threshold:
                best_score = score
                best_match = coords
                
        if best_match:
            logger.info(f"Fuzzy match for '{attraction_name}': score {best_score}")
            
        return best_match
    
    def get_location_info(self, attraction_name: str) -> Optional[Dict]:
        """
        Get complete location information for an attraction
        
        Args:
            attraction_name: Name of the attraction
            
        Returns:
            Dictionary with full location data or None
        """
        if not attraction_name:
            return None
            
        # Direct exact match
        exact_match = self.locations_data.get(attraction_name.lower())
        if exact_match:
            return exact_match
            
        # Fuzzy matching
        best_match = self._fuzzy_search_location_info(attraction_name)
        return best_match
    
    def _fuzzy_search_location_info(self, attraction_name: str, threshold: int = 80) -> Optional[Dict]:
        """Fuzzy search for complete location information"""
        best_score = 0
        best_match = None
        
        for stored_name, location_data in self.locations_data.items():
            score = fuzz.partial_ratio(attraction_name.lower(), stored_name)
            
            if score > best_score and score >= threshold:
                best_score = score
                best_match = location_data
                
        return best_match
    
    def get_attractions_by_category(self, category: str) -> List[Dict]:
        """Get all attractions in a specific category"""
        attractions = []
        
        for location_data in self.locations_data.values():
            if location_data.get('category', '').lower() == category.lower():
                attractions.append(location_data)
                
        return attractions
    
    def get_nearby_attractions(self, latitude: float, longitude: float, max_distance_km: float = 50) -> List[Dict]:
        """
        Find attractions within a certain distance of a point
        
        Args:
            latitude: Center point latitude
            longitude: Center point longitude
            max_distance_km: Maximum distance in kilometers
            
        Returns:
            List of nearby attractions with distance information
        """
        from langgraph_flow.models.geo_clustering import haversine_distance
        
        nearby = []
        
        for location_data in self.locations_data.values():
            attr_lat = location_data.get('latitude')
            attr_lng = location_data.get('longitude')
            
            if attr_lat is not None and attr_lng is not None:
                distance = haversine_distance(latitude, longitude, attr_lat, attr_lng)
                
                if distance <= max_distance_km:
                    location_with_distance = location_data.copy()
                    location_with_distance['distance_km'] = round(distance, 2)
                    nearby.append(location_with_distance)
        
        # Sort by distance
        nearby.sort(key=lambda x: x['distance_km'])
        return nearby
    
    def get_statistics(self) -> Dict:
        """Get statistics about the loaded location data"""
        category_counts = {}
        for category, attractions in self.category_mapping.items():
            category_counts[category] = len(attractions)
            
        return {
            "total_locations": len(self.locations_data),
            "categories": category_counts,
            "locations_with_coordinates": len(self.name_to_coords),
            "coverage_percentage": (len(self.name_to_coords) / len(self.locations_data)) * 100 if self.locations_data else 0
        }

# Global instance for easy access
_coordinate_service = None

def get_coordinate_service() -> CoordinateService:
    """Get a singleton instance of the coordinate service"""
    global _coordinate_service
    if _coordinate_service is None:
        _coordinate_service = CoordinateService()
    return _coordinate_service

def get_attraction_coordinates(attraction_name: str) -> Optional[Tuple[float, float]]:
    """Convenience function to get coordinates for an attraction"""
    service = get_coordinate_service()
    return service.get_coordinates(attraction_name)

def enrich_attraction_with_coordinates(attraction_data: Dict) -> Dict:
    """
    Add latitude/longitude to attraction data if missing
    
    Args:
        attraction_data: Dictionary containing attraction info
        
    Returns:
        Enhanced attraction data with coordinates
    """
    enhanced = attraction_data.copy()
    
    # Check if coordinates already exist
    if enhanced.get('latitude') is not None and enhanced.get('longitude') is not None:
        return enhanced
    
    # Try to get coordinates from the service
    attraction_name = enhanced.get('name', '')
    coordinates = get_attraction_coordinates(attraction_name)
    
    if coordinates:
        enhanced['latitude'], enhanced['longitude'] = coordinates
        enhanced['coordinate_source'] = 'sri_lanka_locations_db'
    else:
        # Fallback coordinates for unknown locations (center of Sri Lanka)
        enhanced['latitude'] = 7.8731  # Center of Sri Lanka
        enhanced['longitude'] = 80.7718
        enhanced['coordinate_source'] = 'fallback_center'
        
    return enhanced

if __name__ == "__main__":
    # Test the coordinate service
    service = CoordinateService()
    
    print("Coordinate Service Statistics:")
    stats = service.get_statistics()
    for key, value in stats.items():
        print(f"  {key}: {value}")
    
    # Test coordinate lookup
    test_attractions = [
        "Sigiriya Rock Fortress",
        "Dambulla Cave Temple", 
        "Tangalle Beach",
        "Gangaramaya Temple",
        "Unknown Attraction"
    ]
    
    print("\nCoordinate Lookup Tests:")
    for attraction in test_attractions:
        coords = service.get_coordinates(attraction)
        if coords:
            print(f"  ✅ {attraction}: {coords}")
        else:
            print(f"  ❌ {attraction}: Not found")
