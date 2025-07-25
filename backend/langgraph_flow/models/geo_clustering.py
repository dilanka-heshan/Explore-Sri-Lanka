"""
Geographic Clustering Module
Clusters attractions based on geographic proximity using Haversine distance
"""

import math
import numpy as np
from typing import List, Dict, Any, Tuple, Optional
from dataclasses import dataclass
from sklearn.cluster import DBSCAN
import logging

logger = logging.getLogger(__name__)

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
    """A geographic cluster of attractions"""
    cluster_id: int
    center_lat: float
    center_lng: float
    attractions: List[Dict[str, Any]]
    total_pear_score: float = 0.0
    estimated_time_hours: float = 0.0
    value_per_hour: float = 0.0
    region_name: Optional[str] = None
    
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
        """Recalculate cluster metrics"""
        self.total_pear_score = sum(attr.get('pear_score', 0) for attr in self.attractions)
        self.estimated_time_hours = self._estimate_total_time()
        self.value_per_hour = self.total_pear_score / max(self.estimated_time_hours, 0.1)
    
    def _estimate_total_time(self) -> float:
        """Estimate total time needed for this cluster including travel time"""
        if not self.attractions:
            return 0.0
        
        # Visit time for all attractions
        total_visit_time = 0
        for attraction in self.attractions:
            visit_time = attraction.get('visit_duration_minutes', 120)
            total_visit_time += visit_time
        
        # Internal travel time between attractions in cluster
        internal_travel_time = 0
        if len(self.attractions) > 1:
            # Estimate internal travel time based on cluster radius
            max_distance = 0
            for i, attr1 in enumerate(self.attractions):
                for attr2 in self.attractions[i+1:]:
                    dist = haversine_distance(
                        attr1.get('latitude', 0), attr1.get('longitude', 0),
                        attr2.get('latitude', 0), attr2.get('longitude', 0)
                    )
                    max_distance = max(max_distance, dist)
            
            # Assume 30 km/h average speed within cluster
            avg_internal_travel_time = (max_distance / 30.0) * 60  # minutes
            internal_travel_time = avg_internal_travel_time * (len(self.attractions) - 1)
        
        total_time_minutes = total_visit_time + internal_travel_time
        return total_time_minutes / 60.0  # Convert to hours

class GeographicClusterer:
    """Handles geographic clustering of attractions"""
    
    def __init__(self, cluster_radius_km: float = 5.0, min_attractions_per_cluster: int = 2):
        self.cluster_radius_km = cluster_radius_km
        self.min_attractions_per_cluster = min_attractions_per_cluster
        
        # Convert km to degrees (approximate)
        # 1 degree ≈ 111 km at equator
        self.eps_degrees = cluster_radius_km / 111.0
    
    def cluster_attractions(self, attractions: List[Dict[str, Any]], algorithm: str = "DBSCAN") -> List[GeoCluster]:
        """
        Cluster attractions geographically
        
        Args:
            attractions: List of attractions with latitude/longitude
            algorithm: Clustering algorithm to use ("DBSCAN" or "distance_based")
        
        Returns:
            List of GeoCluster objects
        """
        
        if not attractions:
            return []
        
        # Filter attractions with valid coordinates
        valid_attractions = [
            attr for attr in attractions 
            if attr.get('latitude') is not None and attr.get('longitude') is not None
        ]
        
        if len(valid_attractions) < self.min_attractions_per_cluster:
            # If too few attractions, create a single cluster
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
