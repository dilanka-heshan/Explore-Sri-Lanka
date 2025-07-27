"""
Route Optimization Module
Optimizes travel routes between attractions using distance and time calculations
"""

import asyncio
import aiohttp
import math
from typing import List, Dict, Any, Tuple, Optional
from dataclasses import dataclass
import logging
from itertools import permutations

logger = logging.getLogger(__name__)

@dataclass
class RouteSegment:
    """Represents a segment between two attractions"""
    from_attraction_id: str
    to_attraction_id: str
    distance_km: float
    travel_time_minutes: int
    transport_mode: str = "car"

@dataclass
class OptimizedRoute:
    """Represents an optimized route through attractions"""
    attraction_order: List[str]
    total_distance_km: float
    total_travel_time_minutes: int
    segments: List[RouteSegment]

class OpenRouteServiceAPI:
    """Interface to OpenRouteService API for route calculation"""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://api.openrouteservice.org"
        
    async def get_distance_matrix(self, coordinates: List[Tuple[float, float]], profile: str = "driving-car") -> Dict[str, Any]:
        """
        Get distance matrix from OpenRouteService
        
        Args:
            coordinates: List of (longitude, latitude) tuples
            profile: Transport profile (driving-car, foot-walking, cycling-regular)
        
        Returns:
            Distance matrix response
        """
        
        url = f"{self.base_url}/v2/matrix/{profile}"
        
        headers = {
            'Authorization': self.api_key,
            'Content-Type': 'application/json'
        }
        
        # Format coordinates for ORS (longitude, latitude)
        locations = [[coord[1], coord[0]] for coord in coordinates]  # ORS expects [lng, lat]
        
        payload = {
            "locations": locations,
            "metrics": ["distance", "duration"],
            "units": "km"
        }
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(url, json=payload, headers=headers) as response:
                    if response.status == 200:
                        return await response.json()
                    else:
                        error_text = await response.text()
                        logger.error(f"OpenRouteService API error: {response.status} - {error_text}")
                        return None
        except Exception as e:
            logger.error(f"Error calling OpenRouteService API: {e}")
            return None
    
    async def get_route(self, start_coord: Tuple[float, float], end_coord: Tuple[float, float], profile: str = "driving-car") -> Dict[str, Any]:
        """
        Get detailed route between two points
        
        Args:
            start_coord: (latitude, longitude) of start point
            end_coord: (latitude, longitude) of end point
            profile: Transport profile
        
        Returns:
            Route response with geometry and instructions
        """
        
        url = f"{self.base_url}/v2/directions/{profile}"
        
        headers = {
            'Authorization': self.api_key,
            'Content-Type': 'application/json'
        }
        
        # Format coordinates for ORS (longitude, latitude)
        coordinates = [[start_coord[1], start_coord[0]], [end_coord[1], end_coord[0]]]
        
        payload = {
            "coordinates": coordinates,
            "format": "json",
            "instructions": "true",
            "geometry": "true",
            "preference": "fastest"
        }
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(url, json=payload, headers=headers) as response:
                    if response.status == 200:
                        return await response.json()
                    else:
                        error_text = await response.text()
                        logger.error(f"OpenRouteService route API error: {response.status} - {error_text}")
                        return None
        except Exception as e:
            logger.error(f"Error calling OpenRouteService route API: {e}")
            return None

class RouteOptimizer:
    """Optimizes routes within clusters of attractions"""
    
    def __init__(self, openroute_api_key: str = None):
        self.openroute_api = OpenRouteServiceAPI(openroute_api_key) if openroute_api_key else None
        
    async def optimize_cluster_route(self, cluster_attractions: List[Dict[str, Any]], start_point: Optional[Dict[str, Any]] = None) -> OptimizedRoute:
        """
        Optimize route within a cluster of attractions
        
        Args:
            cluster_attractions: List of attractions in the cluster
            start_point: Optional starting point (e.g., hotel)
        
        Returns:
            Optimized route
        """
        
        if len(cluster_attractions) <= 1:
            return self._create_single_attraction_route(cluster_attractions)
        
        # Get distance matrix
        distance_matrix = await self._get_distance_matrix(cluster_attractions, start_point)
        
        if distance_matrix is None:
            # Fallback to Haversine distance
            logger.warning("Using Haversine distance fallback for route optimization")
            distance_matrix = self._calculate_haversine_matrix(cluster_attractions, start_point)
        
        # Solve TSP (Traveling Salesman Problem)
        optimal_route = self._solve_tsp(distance_matrix, cluster_attractions, start_point)
        
        return optimal_route
    
    async def _get_distance_matrix(self, attractions: List[Dict[str, Any]], start_point: Optional[Dict[str, Any]] = None) -> Optional[Dict[str, List[List[float]]]]:
        """Get distance matrix from OpenRouteService"""
        
        if not self.openroute_api:
            return None
        
        # Prepare coordinates
        coordinates = []
        
        if start_point:
            coordinates.append((start_point.get('latitude', 0), start_point.get('longitude', 0)))
        
        for attraction in attractions:
            coordinates.append((attraction.get('latitude', 0), attraction.get('longitude', 0)))
        
        # Get matrix from API
        response = await self.openroute_api.get_distance_matrix(coordinates)
        
        if response and 'distances' in response and 'durations' in response:
            return {
                'distances': response['distances'],  # km
                'durations': response['durations']   # seconds
            }
        
        return None
    
    def _calculate_haversine_matrix(self, attractions: List[Dict[str, Any]], start_point: Optional[Dict[str, Any]] = None) -> Dict[str, List[List[float]]]:
        """Calculate distance matrix using Haversine formula"""
        
        coordinates = []
        
        if start_point:
            coordinates.append((start_point.get('latitude', 0), start_point.get('longitude', 0)))
        
        for attraction in attractions:
            coordinates.append((attraction.get('latitude', 0), attraction.get('longitude', 0)))
        
        n = len(coordinates)
        distances = [[0.0 for _ in range(n)] for _ in range(n)]
        durations = [[0.0 for _ in range(n)] for _ in range(n)]
        
        for i in range(n):
            for j in range(n):
                if i != j:
                    dist_km = self._haversine_distance(
                        coordinates[i][0], coordinates[i][1],
                        coordinates[j][0], coordinates[j][1]
                    )
                    distances[i][j] = dist_km
                    # Estimate duration: assume 40 km/h average speed
                    durations[i][j] = (dist_km / 40.0) * 3600  # seconds
        
        return {
            'distances': distances,
            'durations': durations
        }
    
    def _haversine_distance(self, lat1: float, lng1: float, lat2: float, lng2: float) -> float:
        """Calculate Haversine distance between two points"""
        
        # Convert decimal degrees to radians
        lat1, lng1, lat2, lng2 = map(math.radians, [lat1, lng1, lat2, lng2])
        
        # Haversine formula
        dlat = lat2 - lat1
        dlng = lng2 - lng1
        a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlng/2)**2
        c = 2 * math.asin(math.sqrt(a))
        
        # Radius of Earth in kilometers
        r = 6371
        
        return r * c
    
    def _solve_tsp(self, distance_matrix: Dict[str, List[List[float]]], attractions: List[Dict[str, Any]], start_point: Optional[Dict[str, Any]] = None) -> OptimizedRoute:
        """
        Solve Traveling Salesman Problem for optimal route
        Uses nearest neighbor heuristic for larger problems, brute force for smaller ones
        """
        
        distances = distance_matrix['distances']
        durations = distance_matrix['durations']
        
        n_points = len(distances)
        start_idx = 0 if start_point else 0
        
        # For small problems (≤ 8 attractions), use brute force
        if len(attractions) <= 8:
            optimal_route = self._brute_force_tsp(distances, durations, attractions, start_point)
        else:
            # For larger problems, use nearest neighbor heuristic
            optimal_route = self._nearest_neighbor_tsp(distances, durations, attractions, start_point)
        
        return optimal_route
    
    def _brute_force_tsp(self, distances: List[List[float]], durations: List[List[float]], attractions: List[Dict[str, Any]], start_point: Optional[Dict[str, Any]] = None) -> OptimizedRoute:
        """Brute force TSP solution for small problems"""
        
        n = len(attractions)
        attraction_indices = list(range(1 if start_point else 0, len(distances)))
        
        best_distance = float('inf')
        best_time = float('inf')
        best_route = []
        
        # Try all permutations
        for perm in permutations(attraction_indices):
            if start_point:
                route = [0] + list(perm)
            else:
                route = list(perm)
            
            total_distance, total_time = self._calculate_route_cost(route, distances, durations)
            
            if total_distance < best_distance:
                best_distance = total_distance
                best_time = total_time
                best_route = route
        
        return self._create_optimized_route(best_route, best_distance, best_time, distances, durations, attractions, start_point)
    
    def _nearest_neighbor_tsp(self, distances: List[List[float]], durations: List[List[float]], attractions: List[Dict[str, Any]], start_point: Optional[Dict[str, Any]] = None) -> OptimizedRoute:
        """Nearest neighbor heuristic for TSP"""
        
        n = len(distances)
        start_idx = 0 if start_point else 0
        
        unvisited = set(range(n))
        current = start_idx
        route = [current]
        unvisited.remove(current)
        
        total_distance = 0.0
        total_time = 0.0
        
        while unvisited:
            nearest = min(unvisited, key=lambda x: distances[current][x])
            total_distance += distances[current][nearest]
            total_time += durations[current][nearest]
            
            route.append(nearest)
            unvisited.remove(nearest)
            current = nearest
        
        return self._create_optimized_route(route, total_distance, total_time, distances, durations, attractions, start_point)
    
    def _calculate_route_cost(self, route: List[int], distances: List[List[float]], durations: List[List[float]]) -> Tuple[float, float]:
        """Calculate total distance and time for a route"""
        
        total_distance = 0.0
        total_time = 0.0
        
        for i in range(len(route) - 1):
            total_distance += distances[route[i]][route[i + 1]]
            total_time += durations[route[i]][route[i + 1]]
        
        return total_distance, total_time
    
    def _create_optimized_route(self, route_indices: List[int], total_distance: float, total_time: float, distances: List[List[float]], durations: List[List[float]], attractions: List[Dict[str, Any]], start_point: Optional[Dict[str, Any]] = None) -> OptimizedRoute:
        """Create OptimizedRoute object from solution"""
        
        # Map indices back to attraction IDs
        all_points = []
        if start_point:
            all_points.append(start_point)
        all_points.extend(attractions)
        
        attraction_order = []
        segments = []
        
        for i, idx in enumerate(route_indices):
            if idx == 0 and start_point:
                continue  # Skip start point in attraction order
            
            attraction_idx = idx - (1 if start_point else 0)
            if 0 <= attraction_idx < len(attractions):
                attraction_order.append(attractions[attraction_idx].get('id', str(attraction_idx)))
        
        # Create segments
        for i in range(len(route_indices) - 1):
            from_idx = route_indices[i]
            to_idx = route_indices[i + 1]
            
            from_point = all_points[from_idx]
            to_point = all_points[to_idx]
            
            segment = RouteSegment(
                from_attraction_id=from_point.get('id', str(from_idx)),
                to_attraction_id=to_point.get('id', str(to_idx)),
                distance_km=distances[from_idx][to_idx],
                travel_time_minutes=int(durations[from_idx][to_idx] / 60)  # Convert to minutes
            )
            segments.append(segment)
        
        return OptimizedRoute(
            attraction_order=attraction_order,
            total_distance_km=total_distance,
            total_travel_time_minutes=int(total_time / 60),  # Convert to minutes
            segments=segments
        )
    
    def _create_single_attraction_route(self, attractions: List[Dict[str, Any]]) -> OptimizedRoute:
        """Create route for single attraction"""
        
        if not attractions:
            return OptimizedRoute([], 0.0, 0, [])
        
        return OptimizedRoute(
            attraction_order=[attractions[0].get('id', '0')],
            total_distance_km=0.0,
            total_travel_time_minutes=0,
            segments=[]
        )

class TimeWindowOptimizer:
    """Optimizes schedules within time windows and opening hours"""
    
    def __init__(self):
        pass
    
    def create_time_schedule(self, optimized_route: OptimizedRoute, attractions: List[Dict[str, Any]], start_time: str = "09:00", end_time: str = "18:00") -> List[Dict[str, Any]]:
        """
        Create time schedule for optimized route
        
        Args:
            optimized_route: The optimized route
            attractions: List of attraction details
            start_time: Daily start time (HH:MM)
            end_time: Daily end time (HH:MM)
        
        Returns:
            List of scheduled activities with times
        """
        
        schedule = []
        attraction_map = {attr.get('id'): attr for attr in attractions}
        
        current_time = self._parse_time(start_time)
        max_time = self._parse_time(end_time)
        
        for i, attraction_id in enumerate(optimized_route.attraction_order):
            attraction = attraction_map.get(attraction_id)
            if not attraction:
                continue
            
            # Check if we have time for this attraction
            visit_duration = attraction.get('visit_duration_minutes', 120)
            travel_time = 0
            
            if i < len(optimized_route.segments):
                travel_time = optimized_route.segments[i].travel_time_minutes
            
            total_time_needed = visit_duration + travel_time
            
            if current_time + total_time_needed > max_time:
                logger.warning(f"Not enough time for attraction {attraction.get('name')} on current day")
                break
            
            # Add travel time
            if travel_time > 0:
                current_time += travel_time
            
            # Schedule attraction visit
            start_visit = self._time_to_string(current_time)
            current_time += visit_duration
            end_visit = self._time_to_string(current_time)
            
            schedule_item = {
                'attraction_id': attraction_id,
                'attraction_name': attraction.get('name', ''),
                'start_time': start_visit,
                'end_time': end_visit,
                'visit_duration_minutes': visit_duration,
                'travel_time_minutes': travel_time
            }
            
            schedule.append(schedule_item)
            
            # Add buffer time
            current_time += 15  # 15 minute buffer between attractions
        
        return schedule
    
    def _parse_time(self, time_str: str) -> int:
        """Parse time string to minutes since midnight"""
        hours, minutes = map(int, time_str.split(':'))
        return hours * 60 + minutes
    
    def _time_to_string(self, minutes: int) -> str:
        """Convert minutes since midnight to time string"""
        hours = minutes // 60
        mins = minutes % 60
        return f"{hours:02d}:{mins:02d}"
