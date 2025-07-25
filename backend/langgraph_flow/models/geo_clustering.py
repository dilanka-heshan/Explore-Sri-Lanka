"""
Advanced Geographic Clustering Module
Clusters attractions based on OpenStreetMap routing and geographic proximity
Optimized for balanced daily itineraries with minimal travel distances
"""

import math
import numpy as np
from typing import List, Dict, Any, Tuple, Optional
from dataclasses import dataclass
from sklearn.cluster import DBSCAN, KMeans
import logging
import requests
import asyncio
import aiohttp
from itertools import combinations
import os
from dotenv import load_dotenv

load_dotenv()
logger = logging.getLogger(__name__)

@dataclass
class RouteInfo:
    """OpenStreetMap route information between two points"""
    distance_km: float
    duration_minutes: float
    route_geometry: Optional[str] = None
    
@dataclass
class GeoPoint:
    """Geographic point with latitude and longitude"""
    lat: float
    lng: float
    id: str
    name: str
    metadata: Dict[str, Any] = None

@dataclass
class GeoCluster:
    """A geographic cluster of attractions optimized for same-day visits"""
    cluster_id: int
    center_lat: float
    center_lng: float
    attractions: List[Dict[str, Any]]
    total_pear_score: float = 0.0
    estimated_time_hours: float = 0.0
    total_travel_time_minutes: float = 0.0
    value_per_hour: float = 0.0
    region_name: Optional[str] = None
    max_travel_distance_km: float = 0.0
    is_balanced: bool = True
    optimal_order: Optional[List[int]] = None  # Optimal visiting order indices
    
    def add_attraction(self, attraction: Dict[str, Any]):
        """Add an attraction to this cluster"""
        self.attractions.append(attraction)
        self.total_pear_score += attraction.get('pear_score', 0)
        self._recalculate_center()
        self._recalculate_metrics()
    
    def _recalculate_center(self):
        """Recalculate cluster center"""
        if self.attractions:
            total_lat = sum(attr.get('latitude', 0) for attr in self.attractions)
            total_lng = sum(attr.get('longitude', 0) for attr in self.attractions)
            self.center_lat = total_lat / len(self.attractions)
            self.center_lng = total_lng / len(self.attractions)
    
    def _recalculate_metrics(self):
        """Recalculate cluster metrics including travel optimization"""
        self.total_pear_score = sum(attr.get('pear_score', 0) for attr in self.attractions)
        self.estimated_time_hours = self._estimate_total_time()
        self.value_per_hour = self.total_pear_score / max(self.estimated_time_hours, 0.1)
        self._calculate_travel_metrics()
        self._check_balance()
    
    def _estimate_total_time(self) -> float:
        """Estimate total time needed for this cluster including optimized travel time"""
        if not self.attractions:
            return 0.0
        
        # Visit time for all attractions
        total_visit_time = 0
        for attraction in self.attractions:
            visit_time = attraction.get('visit_duration_minutes', 120)
            total_visit_time += visit_time
        
        # Add optimized travel time
        total_time_minutes = total_visit_time + self.total_travel_time_minutes
        return total_time_minutes / 60.0  # Convert to hours
    
    def _calculate_travel_metrics(self):
        """Calculate travel-related metrics for the cluster"""
        if len(self.attractions) <= 1:
            self.total_travel_time_minutes = 0
            self.max_travel_distance_km = 0
            return
        
        # Calculate maximum distance between any two attractions in cluster
        max_distance = 0
        total_distance = 0
        count = 0
        
        for i, attr1 in enumerate(self.attractions):
            for attr2 in self.attractions[i+1:]:
                dist = haversine_distance(
                    attr1.get('latitude', 0), attr1.get('longitude', 0),
                    attr2.get('latitude', 0), attr2.get('longitude', 0)
                )
                max_distance = max(max_distance, dist)
                total_distance += dist
                count += 1
        
        self.max_travel_distance_km = max_distance
        
        # Estimate travel time assuming 40 km/h average (considering traffic, stops)
        avg_distance = total_distance / max(count, 1)
        self.total_travel_time_minutes = (avg_distance / 40.0) * 60 * (len(self.attractions) - 1)
    
    def _check_balance(self):
        """Check if cluster is balanced for same-day visit"""
        # Criteria for balanced cluster:
        # 1. Max travel distance <= 50km between any two points
        # 2. Total time <= 10 hours
        # 3. At least 2 attractions but not more than 6
        # 4. Good value per hour ratio
        
        self.is_balanced = (
            self.max_travel_distance_km <= 50 and
            self.estimated_time_hours <= 14 and
            2 <= len(self.attractions) <= 6 and
            self.value_per_hour > 0.1
        )

class OpenStreetMapRouter:
    """Handles routing queries to OpenStreetMap/OpenRouteService"""
    
    def __init__(self):
        self.api_key = os.getenv("OPENROUTE_SERVICE_API_KEY")
        self.base_url = "https://api.openrouteservice.org/v2"
        self.session = None
    
    async def get_route_info(self, start_lat: float, start_lng: float, 
                           end_lat: float, end_lng: float) -> RouteInfo:
        """Get route information between two points"""
        
        if not self.api_key:
            # Fallback to haversine distance estimation
            distance = haversine_distance(start_lat, start_lng, end_lat, end_lng)
            duration = (distance / 40.0) * 60  # Assume 40 km/h average speed
            return RouteInfo(distance_km=distance, duration_minutes=duration)
        
        try:
            url = f"{self.base_url}/directions/driving-car"
            
            headers = {
                'Authorization': self.api_key,
                'Content-Type': 'application/json'
            }
            
            data = {
                'coordinates': [[start_lng, start_lat], [end_lng, end_lat]],
                'format': 'json'
            }
            
            if not self.session:
                self.session = aiohttp.ClientSession()
            
            async with self.session.post(url, json=data, headers=headers) as response:
                if response.status == 200:
                    result = await response.json()
                    route = result['routes'][0]
                    
                    distance_km = route['summary']['distance'] / 1000  # Convert m to km
                    duration_minutes = route['summary']['duration'] / 60  # Convert s to minutes
                    
                    return RouteInfo(
                        distance_km=distance_km,
                        duration_minutes=duration_minutes,
                        route_geometry=route.get('geometry')
                    )
                else:
                    # Fallback to haversine
                    distance = haversine_distance(start_lat, start_lng, end_lat, end_lng)
                    duration = (distance / 40.0) * 60
                    return RouteInfo(distance_km=distance, duration_minutes=duration)
                    
        except Exception as e:
            logger.warning(f"OpenRouteService API failed: {e}, using haversine fallback")
            distance = haversine_distance(start_lat, start_lng, end_lat, end_lng)
            duration = (distance / 40.0) * 60
            return RouteInfo(distance_km=distance, duration_minutes=duration)
    
    async def get_distance_matrix(self, locations: List[Tuple[float, float]]) -> np.ndarray:
        """Get distance matrix between multiple locations"""
        
        n = len(locations)
        matrix = np.zeros((n, n))
        
        # Get all pairwise distances
        for i in range(n):
            for j in range(i + 1, n):
                route_info = await self.get_route_info(
                    locations[i][0], locations[i][1],
                    locations[j][0], locations[j][1]
                )
                matrix[i][j] = route_info.distance_km
                matrix[j][i] = route_info.distance_km
        
        return matrix
    
    async def close(self):
        """Close the aiohttp session"""
        if self.session:
            await self.session.close()

class AdvancedGeographicClusterer:
    """Advanced geographic clustering with OpenStreetMap routing and balanced clusters"""
    
    def __init__(self, 
                 max_cluster_radius_km: float = 30.0,
                 max_daily_travel_time_hours: float = 3.0,
                 min_attractions_per_cluster: int = 2,
                 max_attractions_per_cluster: int = 6,
                 target_clusters: int = 5):
        
        self.max_cluster_radius_km = max_cluster_radius_km
        self.max_daily_travel_time_hours = max_daily_travel_time_hours
        self.min_attractions_per_cluster = min_attractions_per_cluster
        self.max_attractions_per_cluster = max_attractions_per_cluster
        self.target_clusters = target_clusters
        self.router = OpenStreetMapRouter()
    
    async def create_balanced_clusters(self, 
                                     top_attractions: List[Dict[str, Any]],
                                     algorithm: str = "smart_clustering") -> List[GeoCluster]:
        """
        Create balanced clusters from top 30 attractions for optimal daily itineraries
        
        Args:
            top_attractions: List of top-ranked attractions (up to 30)
            algorithm: Clustering algorithm ("smart_clustering", "kmeans_routing", "dbscan_routing")
        
        Returns:
            List of balanced GeoCluster objects optimized for same-day visits
        """
        
        if not top_attractions:
            return []
        
        # Limit to top 30 as requested
        attractions = top_attractions[:30]
        
        # Filter attractions with valid coordinates
        valid_attractions = [
            attr for attr in attractions 
            if attr.get('latitude') is not None and attr.get('longitude') is not None
        ]
        
        if len(valid_attractions) < self.min_attractions_per_cluster:
            return self._create_single_cluster(valid_attractions)
        
        logger.info(f"Creating balanced clusters from {len(valid_attractions)} top attractions")
        
        if algorithm == "smart_clustering":
            return await self._smart_clustering(valid_attractions)
        elif algorithm == "kmeans_routing":
            return await self._kmeans_with_routing(valid_attractions)
        elif algorithm == "dbscan_routing":
            return await self._dbscan_with_routing(valid_attractions)
        else:
            return await self._smart_clustering(valid_attractions)
    
    async def _smart_clustering(self, attractions: List[Dict[str, Any]]) -> List[GeoCluster]:
        """
        Smart clustering algorithm that considers:
        1. Geographic proximity
        2. PEAR scores
        3. Travel time optimization
        4. Balanced daily itineraries
        """
        
        # Step 1: Get location coordinates
        locations = [(attr.get('latitude', 0), attr.get('longitude', 0)) for attr in attractions]
        
        # Step 2: Get distance matrix using OpenStreetMap routing
        distance_matrix = await self.router.get_distance_matrix(locations)
        
        # Step 3: Apply initial clustering based on distance and PEAR scores
        initial_clusters = await self._weighted_clustering(attractions, distance_matrix)
        
        # Step 4: Optimize clusters for balance
        balanced_clusters = self._optimize_cluster_balance(initial_clusters)
        
        # Step 5: Calculate optimal visiting order within each cluster
        final_clusters = await self._optimize_visiting_order(balanced_clusters)
        
        logger.info(f"Smart clustering created {len(final_clusters)} balanced clusters")
        return final_clusters
    
    async def _weighted_clustering(self, attractions: List[Dict[str, Any]], 
                                 distance_matrix: np.ndarray) -> List[GeoCluster]:
        """Clustering that considers both distance and PEAR scores"""
        
        n = len(attractions)
        
        # Create weighted similarity matrix
        # Combine distance (negative) and PEAR score similarity (positive)
        similarity_matrix = np.zeros((n, n))
        
        for i in range(n):
            for j in range(n):
                if i != j:
                    # Distance penalty (normalized)
                    max_dist = np.max(distance_matrix)
                    dist_penalty = distance_matrix[i][j] / max_dist
                    
                    # PEAR score similarity bonus
                    score_i = attractions[i].get('pear_score', 0)
                    score_j = attractions[j].get('pear_score', 0)
                    score_similarity = 1 - abs(score_i - score_j)
                    
                    # Combined similarity (higher is better)
                    similarity_matrix[i][j] = score_similarity - (0.7 * dist_penalty)
        
        # Apply clustering based on similarity
        # Convert similarity to distance for clustering algorithms
        distance_for_clustering = 1 - similarity_matrix
        np.fill_diagonal(distance_for_clustering, 0)
        
        # Use KMeans with custom distance metric
        n_clusters = min(self.target_clusters, len(attractions) // self.min_attractions_per_cluster)
        n_clusters = max(1, n_clusters)
        
        # Apply KMeans clustering
        kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
        cluster_labels = kmeans.fit_predict(distance_for_clustering)
        
        # Group attractions by cluster
        clusters_dict = {}
        for i, label in enumerate(cluster_labels):
            if label not in clusters_dict:
                clusters_dict[label] = []
            clusters_dict[label].append(attractions[i])
        
        # Create GeoCluster objects
        clusters = []
        for cluster_id, cluster_attractions in clusters_dict.items():
            cluster = self._create_cluster(cluster_id, cluster_attractions)
            clusters.append(cluster)
        
        return clusters
    
    def _optimize_cluster_balance(self, clusters: List[GeoCluster]) -> List[GeoCluster]:
        """Optimize clusters for balanced daily itineraries"""
        
        balanced_clusters = []
        redistributed_attractions = []
        
        for cluster in clusters:
            if cluster.is_balanced:
                balanced_clusters.append(cluster)
            else:
                # Cluster is not balanced, need to redistribute
                if len(cluster.attractions) > self.max_attractions_per_cluster:
                    # Split large cluster
                    split_clusters = self._split_cluster(cluster)
                    balanced_clusters.extend(split_clusters)
                elif cluster.max_travel_distance_km > self.max_cluster_radius_km:
                    # Cluster too spread out, redistribute attractions
                    redistributed_attractions.extend(cluster.attractions)
                else:
                    # Keep cluster but mark for potential merging
                    balanced_clusters.append(cluster)
        
        # Redistribute unbalanced attractions
        if redistributed_attractions:
            for attraction in redistributed_attractions:
                # Find best cluster to add this attraction
                best_cluster = self._find_best_cluster_for_attraction(attraction, balanced_clusters)
                if best_cluster and self._can_add_to_cluster(attraction, best_cluster):
                    best_cluster.add_attraction(attraction)
                else:
                    # Create new cluster for orphaned attractions
                    new_cluster = self._create_cluster(len(balanced_clusters), [attraction])
                    balanced_clusters.append(new_cluster)
        
        return balanced_clusters
    
    async def _optimize_visiting_order(self, clusters: List[GeoCluster]) -> List[GeoCluster]:
        """Calculate optimal visiting order within each cluster to minimize travel time"""
        
        optimized_clusters = []
        
        for cluster in clusters:
            if len(cluster.attractions) <= 2:
                cluster.optimal_order = list(range(len(cluster.attractions)))
                optimized_clusters.append(cluster)
                continue
            
            # Get distance matrix for attractions in this cluster
            locations = [(attr.get('latitude', 0), attr.get('longitude', 0)) 
                        for attr in cluster.attractions]
            
            distance_matrix = await self.router.get_distance_matrix(locations)
            
            # Solve TSP (Traveling Salesman Problem) for optimal order
            optimal_order = self._solve_tsp_greedy(distance_matrix)
            cluster.optimal_order = optimal_order
            
            # Recalculate travel time based on optimal order
            total_distance = 0
            for i in range(len(optimal_order) - 1):
                total_distance += distance_matrix[optimal_order[i]][optimal_order[i + 1]]
            
            cluster.total_travel_time_minutes = (total_distance / 40.0) * 60  # 40 km/h average
            cluster._recalculate_metrics()
            
            optimized_clusters.append(cluster)
        
        return optimized_clusters
    
    def _solve_tsp_greedy(self, distance_matrix: np.ndarray) -> List[int]:
        """Solve TSP using greedy nearest neighbor algorithm"""
        
        n = distance_matrix.shape[0]
        if n <= 2:
            return list(range(n))
        
        unvisited = set(range(1, n))
        tour = [0]  # Start from first attraction
        current = 0
        
        while unvisited:
            nearest = min(unvisited, key=lambda x: distance_matrix[current][x])
            tour.append(nearest)
            unvisited.remove(nearest)
            current = nearest
        
        return tour
    
    def _split_cluster(self, cluster: GeoCluster) -> List[GeoCluster]:
        """Split a large cluster into smaller balanced clusters"""
        
        attractions = cluster.attractions
        n_splits = (len(attractions) + self.max_attractions_per_cluster - 1) // self.max_attractions_per_cluster
        
        # Sort attractions by PEAR score to distribute high-value attractions evenly
        sorted_attractions = sorted(attractions, key=lambda x: x.get('pear_score', 0), reverse=True)
        
        split_clusters = []
        for i in range(n_splits):
            split_attractions = []
            # Distribute attractions in round-robin fashion to balance scores
            for j in range(i, len(sorted_attractions), n_splits):
                split_attractions.append(sorted_attractions[j])
            
            if split_attractions:
                split_cluster = self._create_cluster(len(split_clusters), split_attractions)
                split_clusters.append(split_cluster)
        
        return split_clusters
    
    def _find_best_cluster_for_attraction(self, attraction: Dict[str, Any], 
                                        clusters: List[GeoCluster]) -> Optional[GeoCluster]:
        """Find the best cluster to add an attraction to"""
        
        if not clusters:
            return None
        
        best_cluster = None
        best_score = -float('inf')
        
        attr_lat = attraction.get('latitude', 0)
        attr_lng = attraction.get('longitude', 0)
        
        for cluster in clusters:
            if len(cluster.attractions) >= self.max_attractions_per_cluster:
                continue
            
            # Calculate distance to cluster center
            distance = haversine_distance(attr_lat, attr_lng, cluster.center_lat, cluster.center_lng)
            
            if distance > self.max_cluster_radius_km:
                continue
            
            # Score based on distance (closer is better) and cluster value
            distance_score = 1 / (1 + distance)  # Closer = higher score
            value_score = cluster.value_per_hour
            
            combined_score = distance_score + 0.3 * value_score
            
            if combined_score > best_score:
                best_score = combined_score
                best_cluster = cluster
        
        return best_cluster
    
    def _can_add_to_cluster(self, attraction: Dict[str, Any], cluster: GeoCluster) -> bool:
        """Check if an attraction can be added to a cluster while maintaining balance"""
        
        # Check cluster size limit
        if len(cluster.attractions) >= self.max_attractions_per_cluster:
            return False
        
        # Check distance to cluster center
        attr_lat = attraction.get('latitude', 0)
        attr_lng = attraction.get('longitude', 0)
        distance = haversine_distance(attr_lat, attr_lng, cluster.center_lat, cluster.center_lng)
        
        if distance > self.max_cluster_radius_km:
            return False
        
        # Check if adding this attraction would exceed max travel distance within cluster
        max_distance_after_adding = distance
        for existing_attr in cluster.attractions:
            dist_to_existing = haversine_distance(
                attr_lat, attr_lng,
                existing_attr.get('latitude', 0), existing_attr.get('longitude', 0)
            )
            max_distance_after_adding = max(max_distance_after_adding, dist_to_existing)
        
        return max_distance_after_adding <= self.max_cluster_radius_km
    
    async def _kmeans_with_routing(self, attractions: List[Dict[str, Any]]) -> List[GeoCluster]:
        """KMeans clustering enhanced with OpenStreetMap routing"""
        
        locations = [(attr.get('latitude', 0), attr.get('longitude', 0)) for attr in attractions]
        distance_matrix = await self.router.get_distance_matrix(locations)
        
        # Use distance matrix for KMeans clustering
        n_clusters = min(self.target_clusters, len(attractions) // self.min_attractions_per_cluster)
        n_clusters = max(1, n_clusters)
        
        kmeans = KMeans(n_clusters=n_clusters, random_state=42)
        cluster_labels = kmeans.fit_predict(distance_matrix)
        
        # Group attractions by cluster
        clusters_dict = {}
        for i, label in enumerate(cluster_labels):
            if label not in clusters_dict:
                clusters_dict[label] = []
            clusters_dict[label].append(attractions[i])
        
        clusters = []
        for cluster_id, cluster_attractions in clusters_dict.items():
            cluster = self._create_cluster(cluster_id, cluster_attractions)
            clusters.append(cluster)
        
        return clusters
    
    async def _dbscan_with_routing(self, attractions: List[Dict[str, Any]]) -> List[GeoCluster]:
        """DBSCAN clustering enhanced with OpenStreetMap routing"""
        
        locations = [(attr.get('latitude', 0), attr.get('longitude', 0)) for attr in attractions]
        distance_matrix = await self.router.get_distance_matrix(locations)
        
        # Use distance matrix for DBSCAN
        eps = self.max_cluster_radius_km  # Maximum distance for clustering
        db = DBSCAN(eps=eps, min_samples=self.min_attractions_per_cluster, metric='precomputed')
        cluster_labels = db.fit_predict(distance_matrix)
        
        # Group attractions by cluster
        clusters_dict = {}
        noise_attractions = []
        
        for i, label in enumerate(cluster_labels):
            if label == -1:  # Noise point
                noise_attractions.append(attractions[i])
            else:
                if label not in clusters_dict:
                    clusters_dict[label] = []
                clusters_dict[label].append(attractions[i])
        
        clusters = []
        for cluster_id, cluster_attractions in clusters_dict.items():
            cluster = self._create_cluster(cluster_id, cluster_attractions)
            clusters.append(cluster)
        
        # Handle noise attractions
        for attraction in noise_attractions:
            # Create individual cluster or add to nearest suitable cluster
            best_cluster = self._find_best_cluster_for_attraction(attraction, clusters)
            if best_cluster and self._can_add_to_cluster(attraction, best_cluster):
                best_cluster.add_attraction(attraction)
            else:
                individual_cluster = self._create_cluster(len(clusters), [attraction])
                clusters.append(individual_cluster)
        
        return clusters
    
    def _create_cluster(self, cluster_id: int, attractions: List[Dict[str, Any]]) -> GeoCluster:
        """Create a GeoCluster from a list of attractions"""
        
        if not attractions:
            return GeoCluster(cluster_id, 0, 0, [])
        
        # Calculate center
        center_lat = sum(attr.get('latitude', 0) for attr in attractions) / len(attractions)
        center_lng = sum(attr.get('longitude', 0) for attr in attractions) / len(attractions)
        
        # Determine region name
        region_name = self._get_region_name(center_lat, center_lng)
        
        cluster = GeoCluster(
            cluster_id=cluster_id,
            center_lat=center_lat,
            center_lng=center_lng,
            attractions=attractions,
            region_name=region_name
        )
        
        cluster._recalculate_metrics()
        return cluster
    
    def _create_single_cluster(self, attractions: List[Dict[str, Any]]) -> List[GeoCluster]:
        """Create a single cluster when there are too few attractions"""
        if not attractions:
            return []
        
        cluster = self._create_cluster(0, attractions)
        return [cluster]
    
    def _get_region_name(self, lat: float, lng: float) -> str:
        """Determine region name based on coordinates (Sri Lanka specific)"""
        
        # Enhanced region mapping for Sri Lanka
        if lat > 9.0:  # Northern region
            return "Northern Province"
        elif lat > 8.0 and lng < 80.0:  # North Western
            return "North Western Province"
        elif lat > 7.5 and lng < 80.5:  # Western region
            return "Western Province"
        elif lat > 7.5 and lng > 81.0:  # Eastern region
            return "Eastern Province"
        elif lat > 6.8 and 80.2 < lng < 81.2:  # Central region
            return "Central Province"
        elif lat > 6.0 and lng < 80.5:  # Southern region
            return "Southern Province"
        elif lng > 81.0:  # Eastern/Uva
            return "Uva Province"
        else:  # Sabaragamuwa
            return "Sabaragamuwa Province"
    
    def rank_clusters_by_value(self, clusters: List[GeoCluster]) -> List[GeoCluster]:
        """Rank clusters by value per hour and balance score"""
        
        def cluster_score(cluster):
            # Combine value per hour with balance factors
            base_score = cluster.value_per_hour
            
            # Bonus for balanced clusters
            balance_bonus = 1.2 if cluster.is_balanced else 1.0
            
            # Penalty for clusters with excessive travel time
            travel_penalty = 1.0
            if cluster.total_travel_time_minutes > 180:  # More than 3 hours travel
                travel_penalty = 0.7
            
            # Bonus for optimal cluster size
            size_bonus = 1.0
            if self.min_attractions_per_cluster <= len(cluster.attractions) <= self.max_attractions_per_cluster:
                size_bonus = 1.1
            
            return base_score * balance_bonus * travel_penalty * size_bonus
        
        ranked_clusters = sorted(clusters, key=cluster_score, reverse=True)
        
        logger.info(f"Ranked {len(clusters)} clusters by balanced value score")
        for i, cluster in enumerate(ranked_clusters[:3]):  # Log top 3
            logger.info(f"Cluster {i+1}: {cluster.region_name}, "
                       f"Value/Hour: {cluster.value_per_hour:.2f}, "
                       f"Attractions: {len(cluster.attractions)}, "
                       f"Balanced: {cluster.is_balanced}, "
                       f"Travel Time: {cluster.total_travel_time_minutes:.1f}min")
        
        return ranked_clusters
    
    async def close(self):
        """Clean up resources"""
        await self.router.close()

# Legacy class for backward compatibility
class GeographicClusterer:
    """Legacy geographic clusterer - use AdvancedGeographicClusterer for new features"""
    
    def __init__(self, cluster_radius_km: float = 5.0, min_attractions_per_cluster: int = 2):
        self.cluster_radius_km = cluster_radius_km
        self.min_attractions_per_cluster = min_attractions_per_cluster
        self.eps_degrees = cluster_radius_km / 111.0
        logger.warning("Using legacy GeographicClusterer. Consider upgrading to AdvancedGeographicClusterer")
    
    def cluster_attractions(self, attractions: List[Dict[str, Any]], algorithm: str = "DBSCAN") -> List[GeoCluster]:
        """
        Legacy clustering method - basic geographic clustering
        """
        
        if not attractions:
            return []
        
        # Filter attractions with valid coordinates
        valid_attractions = [
            attr for attr in attractions 
            if attr.get('latitude') is not None and attr.get('longitude') is not None
        ]
        
        if len(valid_attractions) < self.min_attractions_per_cluster:
            return self._create_single_cluster(valid_attractions)
        
        if algorithm == "DBSCAN":
            return self._dbscan_clustering(valid_attractions)
        else:
            return self._distance_based_clustering(valid_attractions)
    
    def _dbscan_clustering(self, attractions: List[Dict[str, Any]]) -> List[GeoCluster]:
        """Use DBSCAN for clustering"""
        
        try:
            # Prepare coordinates for clustering
            coordinates = np.array([
                [attr.get('latitude', 0), attr.get('longitude', 0)]
                for attr in attractions
            ])
            
            # Apply DBSCAN
            db = DBSCAN(eps=self.eps_degrees, min_samples=self.min_attractions_per_cluster, metric='haversine')
            cluster_labels = db.fit_predict(np.radians(coordinates))
            
            # Group attractions by cluster
            clusters = {}
            noise_attractions = []
            
            for i, label in enumerate(cluster_labels):
                if label == -1:  # Noise point
                    noise_attractions.append(attractions[i])
                else:
                    if label not in clusters:
                        clusters[label] = []
                    clusters[label].append(attractions[i])
            
            # Create GeoCluster objects
            geo_clusters = []
            
            for cluster_id, cluster_attractions in clusters.items():
                if len(cluster_attractions) >= self.min_attractions_per_cluster:
                    cluster = self._create_cluster(cluster_id, cluster_attractions)
                    geo_clusters.append(cluster)
                else:
                    noise_attractions.extend(cluster_attractions)
            
            # Handle noise attractions - create individual clusters or merge with nearest
            if noise_attractions:
                for attraction in noise_attractions:
                    # Find nearest cluster
                    nearest_cluster = self._find_nearest_cluster(attraction, geo_clusters)
                    if nearest_cluster:
                        nearest_cluster.add_attraction(attraction)
                    else:
                        # Create individual cluster
                        individual_cluster = self._create_cluster(len(geo_clusters), [attraction])
                        geo_clusters.append(individual_cluster)
            
            logger.info(f"DBSCAN clustering created {len(geo_clusters)} clusters from {len(attractions)} attractions")
            return geo_clusters
            
        except Exception as e:
            logger.error(f"DBSCAN clustering failed: {e}")
            return self._distance_based_clustering(attractions)
    
    def _distance_based_clustering(self, attractions: List[Dict[str, Any]]) -> List[GeoCluster]:
        """Simple distance-based clustering"""
        
        clusters = []
        remaining_attractions = attractions.copy()
        cluster_id = 0
        
        while remaining_attractions:
            # Start new cluster with first remaining attraction
            seed_attraction = remaining_attractions.pop(0)
            cluster_attractions = [seed_attraction]
            
            # Find nearby attractions
            i = 0
            while i < len(remaining_attractions):
                attraction = remaining_attractions[i]
                
                # Check if attraction is close to any attraction in current cluster
                is_close = False
                for cluster_attr in cluster_attractions:
                    distance = haversine_distance(
                        cluster_attr.get('latitude', 0), cluster_attr.get('longitude', 0),
                        attraction.get('latitude', 0), attraction.get('longitude', 0)
                    )
                    
                    if distance <= self.cluster_radius_km:
                        is_close = True
                        break
                
                if is_close:
                    cluster_attractions.append(remaining_attractions.pop(i))
                else:
                    i += 1
            
            # Create cluster
            cluster = self._create_cluster(cluster_id, cluster_attractions)
            clusters.append(cluster)
            cluster_id += 1
        
        logger.info(f"Distance-based clustering created {len(clusters)} clusters from {len(attractions)} attractions")
        return clusters
    
    def _create_cluster(self, cluster_id: int, attractions: List[Dict[str, Any]]) -> GeoCluster:
        """Create a GeoCluster from a list of attractions"""
        
        if not attractions:
            return GeoCluster(cluster_id, 0, 0, [])
        
        # Calculate center
        center_lat = sum(attr.get('latitude', 0) for attr in attractions) / len(attractions)
        center_lng = sum(attr.get('longitude', 0) for attr in attractions) / len(attractions)
        
        # Determine region name based on center coordinates
        region_name = self._get_region_name(center_lat, center_lng)
        
        cluster = GeoCluster(
            cluster_id=cluster_id,
            center_lat=center_lat,
            center_lng=center_lng,
            attractions=attractions,
            region_name=region_name
        )
        
        cluster._recalculate_metrics()
        return cluster
    
    def _create_single_cluster(self, attractions: List[Dict[str, Any]]) -> List[GeoCluster]:
        """Create a single cluster when there are too few attractions"""
        if not attractions:
            return []
        
        cluster = self._create_cluster(0, attractions)
        return [cluster]
    
    def _find_nearest_cluster(self, attraction: Dict[str, Any], clusters: List[GeoCluster]) -> Optional[GeoCluster]:
        """Find the nearest cluster to an attraction"""
        
        if not clusters:
            return None
        
        min_distance = float('inf')
        nearest_cluster = None
        
        attr_lat = attraction.get('latitude', 0)
        attr_lng = attraction.get('longitude', 0)
        
        for cluster in clusters:
            distance = haversine_distance(attr_lat, attr_lng, cluster.center_lat, cluster.center_lng)
            
            if distance < min_distance and distance <= self.cluster_radius_km * 1.5:  # Allow 50% buffer
                min_distance = distance
                nearest_cluster = cluster
        
        return nearest_cluster
    
    def _get_region_name(self, lat: float, lng: float) -> str:
        """Determine region name based on coordinates (Sri Lanka specific)"""
        
        # Basic region mapping for Sri Lanka
        # This is a simplified version - in production, use proper geographic boundaries
        
        if lat > 8.5:  # Northern region
            return "Northern Province"
        elif lat > 7.5 and lng < 80.5:  # Western region
            return "Western Province"
        elif lat > 7.0 and lng > 81.0:  # Eastern region
            return "Eastern Province"
        elif lat > 6.5:  # Central region
            return "Central Province"
        else:  # Southern region
            return "Southern Province"
    
    def rank_clusters_by_value(self, clusters: List[GeoCluster]) -> List[GeoCluster]:
        """Rank clusters by value per hour ratio"""
        
        ranked_clusters = sorted(clusters, key=lambda c: c.value_per_hour, reverse=True)
        
        logger.info(f"Ranked {len(clusters)} clusters by value per hour")
        for i, cluster in enumerate(ranked_clusters[:5]):  # Log top 5
            logger.info(f"Cluster {i+1}: {cluster.region_name}, Value/Hour: {cluster.value_per_hour:.2f}, Attractions: {len(cluster.attractions)}")
        
        return ranked_clusters

def haversine_distance(lat1: float, lng1: float, lat2: float, lng2: float) -> float:
    """
    Calculate the Haversine distance between two points on Earth
    
    Returns:
        Distance in kilometers
    """
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

def calculate_cluster_bounds(cluster: GeoCluster) -> Dict[str, float]:
    """Calculate bounding box for a cluster"""
    
    if not cluster.attractions:
        return {'min_lat': 0, 'max_lat': 0, 'min_lng': 0, 'max_lng': 0}
    
    latitudes = [attr.get('latitude', 0) for attr in cluster.attractions]
    longitudes = [attr.get('longitude', 0) for attr in cluster.attractions]
    
    return {
        'min_lat': min(latitudes),
        'max_lat': max(latitudes),
        'min_lng': min(longitudes),
        'max_lng': max(longitudes)
    }
