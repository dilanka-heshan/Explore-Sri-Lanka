"""
Advanced Clustered Recommendations API
Integrates PEAR ranking with OpenStreetMap-based geographic clustering
Uses Sri Lankan location database for accurate coordinates
"""

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field
from typing import Dict, Any, Optional, List
import logging
import asyncio
import time
from langgraph_flow.models.pear_ranker import create_pear_ranker
from langgraph_flow.models.geo_clustering import AdvancedGeographicClusterer, GeoCluster
# from langgraph_flow.models.geo_clustering_optimized import AdvancedGeographicClusterer, GeoCluster
from services.coordinate_service import get_coordinate_service, enrich_attraction_with_coordinates

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/clustered-recommendations", tags=["Clustered Recommendations"])

class ClusteredRecommendationRequest(BaseModel):
    """Request for clustered travel recommendations"""
    query: str = Field(..., description="What you want to do/see", 
                      example="I want to explore ancient temples and cultural sites in Sri Lanka")
    interests: List[str] = Field(..., description="Your interests", 
                                example=["culture", "temples", "history"])
    trip_duration_days: int = Field(..., description="Total trip duration", example=5)
    daily_travel_preference: str = Field("balanced", description="Travel preference", 
                                       enum=["minimal", "balanced", "extensive"])
    max_attractions_per_day: int = Field(4, description="Maximum attractions per day", example=4)
    budget_level: Optional[str] = Field("medium", description="Budget level")
    group_size: Optional[int] = Field(2, description="Group size")

class ClusterInfo(BaseModel):
    """Information about a geographic cluster"""
    cluster_id: int
    region_name: str
    center_lat: float
    center_lng: float
    total_attractions: int
    total_pear_score: float
    estimated_time_hours: float
    travel_time_minutes: float
    value_per_hour: float
    is_balanced: bool
    optimal_visiting_order: Optional[List[int]]

class AttractionInfo(BaseModel):
    """Attraction information"""
    id: str
    name: str
    category: str
    description: str
    region: str
    latitude: Optional[float]
    longitude: Optional[float]
    pear_score: float
    visit_order: Optional[int]

class DayItinerary(BaseModel):
    """Daily itinerary with clustered attractions"""
    day: int
    cluster_info: ClusterInfo
    attractions: List[AttractionInfo]
    total_travel_distance_km: float
    estimated_total_time_hours: float
    
class ClusteredRecommendationResponse(BaseModel):
    """Response with clustered recommendations organized by days"""
    query: str
    total_days: int
    total_attractions: int
    daily_itineraries: List[DayItinerary]
    overall_stats: Dict[str, Any]
    processing_time_ms: float

@router.post("/plan", response_model=ClusteredRecommendationResponse)
async def get_clustered_travel_plan(request: ClusteredRecommendationRequest):
    """
    Create a complete travel plan with geographically clustered attractions
    
    This endpoint:
    1. Gets top 30 attractions using PEAR ranking
    2. Creates geographic clusters using OpenStreetMap routing
    3. Organizes clusters into daily itineraries
    4. Optimizes visiting order within each cluster
    5. Returns balanced daily plans
    """
    import time
    start_time = time.time()
    
    try:
        # Step 1: Get top attractions using PEAR ranking
        logger.info(f"Getting recommendations for query: '{request.query}'")
        
        pear_ranker = create_pear_ranker()
        
        user_context = {
            "interests": request.interests,
            "trip_type": "cultural" if "culture" in request.interests else "mixed",
            "budget": request.budget_level,
            "duration": request.trip_duration_days,
            "group_size": request.group_size
        }
        
        # Get top 30 recommendations
        top_attractions = pear_ranker.get_recommendations_from_vector_db(
            user_query=request.query,
            user_context=user_context,
            top_k=30
        )
        
        if not top_attractions:
            raise HTTPException(status_code=404, detail="No attractions found for your preferences")
        
        logger.info(f"Found {len(top_attractions)} top attractions")
        
        # Step 2: Apply advanced geographic clustering
        travel_time_mapping = {
            "minimal": 2.0,    # Max 2 hours travel per day
            "balanced": 3.0,   # Max 3 hours travel per day  
            "extensive": 4.5   # Max 4.5 hours travel per day
        }
        
        max_daily_travel = travel_time_mapping.get(request.daily_travel_preference, 3.0)
        
        clusterer = AdvancedGeographicClusterer(
            max_cluster_radius_km=40.0,
            max_daily_travel_time_hours=max_daily_travel,
            min_attractions_per_cluster=2,
            max_attractions_per_cluster=request.max_attractions_per_day,
            target_clusters=request.trip_duration_days
        )
        
        # Convert recommendations to expected format for clustering with coordinate enrichment
        coordinate_service = get_coordinate_service()
        attractions_for_clustering = []
        
        for rec in top_attractions:
            payload = rec.get('payload', {})
            attraction = {
                'id': str(rec.get('id', '')),
                'name': payload.get('name', 'Unknown'),
                'category': payload.get('category', 'Unknown'),
                'description': payload.get('description', ''),
                'region': payload.get('region', 'Unknown'),
                'pear_score': rec.get('pear_score', 0.0),
                'visit_duration_minutes': payload.get('visit_duration_minutes', 120)
            }
            
            # Enrich with accurate coordinates from Sri Lankan locations database
            attraction = enrich_attraction_with_coordinates(attraction)
            
            # Only include attractions with valid coordinates for clustering
            if attraction.get('latitude') is not None and attraction.get('longitude') is not None:
                attractions_for_clustering.append(attraction)
                logger.debug(f"Added {attraction['name']} with coordinates ({attraction['latitude']}, {attraction['longitude']})")
            else:
                logger.warning(f"Skipped {attraction['name']} - no coordinates available")
        
        logger.info(f"Prepared {len(attractions_for_clustering)} attractions with coordinates for clustering")
        
        # Create balanced clusters
        clusters = await clusterer.create_balanced_clusters(
            attractions_for_clustering,
            algorithm="smart_clustering"
        )
        
        logger.info(f"Created {len(clusters)} geographic clusters")
        
        # Step 3: Rank clusters and assign to days
        ranked_clusters = clusterer.rank_clusters_by_value(clusters)
        
        # Limit to trip duration
        selected_clusters = ranked_clusters[:request.trip_duration_days]
        
        # Step 4: Create daily itineraries
        daily_itineraries = []
        total_travel_distance = 0
        
        for day, cluster in enumerate(selected_clusters, 1):
            # Create cluster info
            cluster_info = ClusterInfo(
                cluster_id=cluster.cluster_id,
                region_name=cluster.region_name or "Unknown Region",
                center_lat=cluster.center_lat,
                center_lng=cluster.center_lng,
                total_attractions=len(cluster.attractions),
                total_pear_score=cluster.total_pear_score,
                estimated_time_hours=cluster.estimated_time_hours,
                travel_time_minutes=cluster.total_travel_time_minutes,
                value_per_hour=cluster.value_per_hour,
                is_balanced=cluster.is_balanced,
                optimal_visiting_order=cluster.optimal_order
            )
            
            # Create attraction list in optimal order
            attractions_info = []
            ordered_attractions = cluster.attractions
            
            if cluster.optimal_order:
                ordered_attractions = [cluster.attractions[i] for i in cluster.optimal_order]
            
            for order, attraction in enumerate(ordered_attractions):
                attraction_info = AttractionInfo(
                    id=attraction.get('id', ''),
                    name=attraction.get('name', 'Unknown'),
                    category=attraction.get('category', 'Unknown'),
                    description=attraction.get('description', ''),
                    region=attraction.get('region', 'Unknown'),
                    latitude=attraction.get('latitude'),
                    longitude=attraction.get('longitude'),
                    pear_score=attraction.get('pear_score', 0.0),
                    visit_order=order + 1
                )
                attractions_info.append(attraction_info)
            
            # Calculate cluster travel distance
            cluster_travel_distance = cluster.max_travel_distance_km
            total_travel_distance += cluster_travel_distance
            
            day_itinerary = DayItinerary(
                day=day,
                cluster_info=cluster_info,
                attractions=attractions_info,
                total_travel_distance_km=cluster_travel_distance,
                estimated_total_time_hours=cluster.estimated_time_hours
            )
            
            daily_itineraries.append(day_itinerary)
        
        # Step 5: Calculate overall statistics
        total_attractions_planned = sum(len(day.attractions) for day in daily_itineraries)
        avg_value_per_hour = sum(day.cluster_info.value_per_hour for day in daily_itineraries) / len(daily_itineraries)
        
        overall_stats = {
            "total_attractions": total_attractions_planned,
            "total_travel_distance_km": round(total_travel_distance, 2),
            "average_value_per_hour": round(avg_value_per_hour, 3),
            "balanced_clusters": sum(1 for day in daily_itineraries if day.cluster_info.is_balanced),
            "travel_optimization": "OpenStreetMap routing used",
            "clustering_algorithm": "Smart clustering with PEAR ranking"
        }
        
        processing_time = (time.time() - start_time) * 1000
        
        # Clean up resources
        await clusterer.close()
        
        logger.info(f"Generated {request.trip_duration_days}-day clustered plan in {processing_time:.2f}ms")
        
        return ClusteredRecommendationResponse(
            query=request.query,
            total_days=len(daily_itineraries),
            total_attractions=total_attractions_planned,
            daily_itineraries=daily_itineraries,
            overall_stats=overall_stats,
            processing_time_ms=processing_time
        )
        
    except Exception as e:
        logger.error(f"Error generating clustered recommendations: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to generate travel plan: {str(e)}")

@router.get("/test-clustering")
async def test_clustering_algorithm():
    """Test endpoint to verify clustering algorithm works"""
    
    try:
        # Sample attractions for testing
        sample_attractions = [
            {
                'id': 'sigiriya',
                'name': 'Sigiriya Rock Fortress',
                'category': 'Historical',
                'description': 'Ancient rock fortress',
                'region': 'Central',
                'latitude': 7.9568,
                'longitude': 80.7604,
                'pear_score': 0.9,
                'visit_duration_minutes': 180
            },
            {
                'id': 'dambulla',
                'name': 'Dambulla Cave Temple',
                'category': 'Religious',
                'description': 'Ancient cave temple',
                'region': 'Central',
                'latitude': 7.8567,
                'longitude': 80.6492,
                'pear_score': 0.85,
                'visit_duration_minutes': 120
            },
            {
                'id': 'kandy_temple',
                'name': 'Temple of the Sacred Tooth',
                'category': 'Religious',
                'description': 'Sacred Buddhist temple',
                'region': 'Central',
                'latitude': 7.2936,
                'longitude': 80.6350,
                'pear_score': 0.88,
                'visit_duration_minutes': 90
            }
        ]
        
        clusterer = AdvancedGeographicClusterer(target_clusters=2)
        clusters = await clusterer.create_balanced_clusters(sample_attractions)
        
        await clusterer.close()
        
        result = {
            "status": "success",
            "clusters_created": len(clusters),
            "clusters": [
                {
                    "cluster_id": cluster.cluster_id,
                    "attractions_count": len(cluster.attractions),
                    "region": cluster.region_name,
                    "is_balanced": cluster.is_balanced,
                    "value_per_hour": cluster.value_per_hour
                }
                for cluster in clusters
            ]
        }
        
        return result
        
    except Exception as e:
        logger.error(f"Error testing clustering: {e}")
        return {"status": "error", "message": str(e)}
