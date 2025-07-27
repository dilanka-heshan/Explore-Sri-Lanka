"""
Integrated Travel Planning Service
Combines clustering, places, and extensible enhancement modules
Designed for modular integration of weather, transport, and other services
"""

from typing import Dict, Any, List, Optional, Union
import logging
import time
from pydantic import BaseModel, Field
from enum import Enum

from services.coordinate_service import get_coordinate_service
from services.google_places_service import get_google_places_service
from services.places_enhancement_service import get_places_enhancement_service
from models.enhanced_places_models import DailyPlaceRecommendations

logger = logging.getLogger(__name__)

class EnhancementType(str, Enum):
    """Types of enhancements available"""
    PLACES = "places"
    WEATHER = "weather"
    TRANSPORT = "transport"
    EVENTS = "events"
    BUDGET = "budget"

class EnhancementConfig(BaseModel):
    """Configuration for individual enhancement modules"""
    enabled: bool = Field(True, description="Whether this enhancement is enabled")
    priority: int = Field(1, description="Processing priority (1=highest)")
    config: Dict[str, Any] = Field(default_factory=dict, description="Module-specific configuration")

class IntegratedPlanningRequest(BaseModel):
    """Request for integrated travel planning with enhancements"""
    
    # Core clustering parameters
    query: str = Field(..., description="What you want to do/see")
    interests: List[str] = Field(..., description="Your interests")
    trip_duration_days: int = Field(..., description="Total trip duration")
    daily_travel_preference: str = Field("balanced", description="Travel preference")
    max_attractions_per_day: int = Field(4, description="Maximum attractions per day")
    budget_level: str = Field("medium", description="Budget level")
    group_size: int = Field(2, description="Group size")
    
    # Enhancement configurations
    enhancements: Dict[EnhancementType, EnhancementConfig] = Field(
        default_factory=lambda: {
            EnhancementType.PLACES: EnhancementConfig(
                enabled=True,
                priority=1,
                config={
                    "search_radius_km": 5,
                    "include_breakfast": True,
                    "include_lunch": True,
                    "include_dinner": True,
                    "include_accommodation": True,
                    "include_cafes": True
                }
            ),
            EnhancementType.WEATHER: EnhancementConfig(
                enabled=False,
                priority=2,
                config={"forecast_days": 7}
            ),
            EnhancementType.TRANSPORT: EnhancementConfig(
                enabled=False,
                priority=3,
                config={"include_local_transport": True}
            )
        },
        description="Configuration for enhancement modules"
    )
    
    # Performance options
    async_processing: bool = Field(True, description="Enable asynchronous enhancement processing")
    cache_results: bool = Field(True, description="Cache results for similar requests")

class EnhancementResult(BaseModel):
    """Result from an enhancement module"""
    type: EnhancementType
    success: bool
    data: Dict[str, Any] = Field(default_factory=dict)
    processing_time_ms: float
    error_message: Optional[str] = None

class IntegratedPlanningResponse(BaseModel):
    """Response for integrated travel planning"""
    
    # Core plan
    base_plan: Dict[str, Any] = Field(..., description="Base clustered plan")
    
    # Enhancement results
    enhancements: Dict[EnhancementType, EnhancementResult] = Field(
        default_factory=dict,
        description="Results from enhancement modules"
    )
    
    # Integrated data
    daily_itineraries: List[Dict[str, Any]] = Field(..., description="Enhanced daily itineraries")
    
    # Metadata
    total_processing_time_ms: float = Field(..., description="Total processing time")
    enhancements_applied: List[EnhancementType] = Field(..., description="Successfully applied enhancements")
    
    # Stats
    stats: Dict[str, Any] = Field(default_factory=dict, description="Planning statistics")

class BaseEnhancementModule:
    """Base class for enhancement modules"""
    
    def __init__(self, module_type: EnhancementType):
        self.module_type = module_type
        self.logger = logging.getLogger(f"enhancement.{module_type.value}")
    
    async def enhance(
        self, 
        base_plan: Dict[str, Any], 
        config: EnhancementConfig,
        request: IntegratedPlanningRequest
    ) -> EnhancementResult:
        """Enhance the base plan with module-specific data"""
        raise NotImplementedError("Enhancement modules must implement enhance method")
    
    def validate_config(self, config: EnhancementConfig) -> bool:
        """Validate module configuration"""
        return True

class PlacesEnhancementModule(BaseEnhancementModule):
    """Google Places enhancement module"""
    
    def __init__(self):
        super().__init__(EnhancementType.PLACES)
        self.places_service = get_google_places_service()
        self.enhancement_service = get_places_enhancement_service()
    
    async def enhance(
        self, 
        base_plan: Dict[str, Any], 
        config: EnhancementConfig,
        request: IntegratedPlanningRequest
    ) -> EnhancementResult:
        """Add Google Places recommendations to the plan"""
        
        start_time = time.time()
        
        try:
            # Extract configuration
            places_config = config.config
            
            # Build meal preferences
            meal_preferences = {
                "breakfast": places_config.get("include_breakfast", True),
                "lunch": places_config.get("include_lunch", True),
                "dinner": places_config.get("include_dinner", True),
                "accommodation": places_config.get("include_accommodation", True),
                "cafes": places_config.get("include_cafes", True)
            }
            
            # Enhance with places
            enhanced_results = await self.enhancement_service.enhance_cluster_with_places(
                cluster_results=base_plan,
                budget_level=request.budget_level,
                place_search_radius_km=places_config.get("search_radius_km", 5),
                meal_preferences=meal_preferences
            )
            
            processing_time = (time.time() - start_time) * 1000
            
            return EnhancementResult(
                type=EnhancementType.PLACES,
                success=True,
                data={
                    "place_recommendations": enhanced_results.place_recommendations,
                    "enhancement_stats": enhanced_results.enhancement_stats
                },
                processing_time_ms=processing_time
            )
            
        except Exception as e:
            processing_time = (time.time() - start_time) * 1000
            self.logger.error(f"Places enhancement failed: {e}")
            
            return EnhancementResult(
                type=EnhancementType.PLACES,
                success=False,
                processing_time_ms=processing_time,
                error_message=str(e)
            )

class WeatherEnhancementModule(BaseEnhancementModule):
    """Weather information enhancement module (placeholder for future implementation)"""
    
    def __init__(self):
        super().__init__(EnhancementType.WEATHER)
    
    async def enhance(
        self, 
        base_plan: Dict[str, Any], 
        config: EnhancementConfig,
        request: IntegratedPlanningRequest
    ) -> EnhancementResult:
        """Add weather information to the plan"""
        
        start_time = time.time()
        
        try:
            # TODO: Implement weather API integration
            # For now, return placeholder data
            
            weather_data = {
                "forecast": "Weather integration coming soon",
                "recommendations": [
                    "Check weather conditions before traveling",
                    "Pack appropriate clothing for the season"
                ]
            }
            
            processing_time = (time.time() - start_time) * 1000
            
            return EnhancementResult(
                type=EnhancementType.WEATHER,
                success=True,
                data=weather_data,
                processing_time_ms=processing_time
            )
            
        except Exception as e:
            processing_time = (time.time() - start_time) * 1000
            self.logger.error(f"Weather enhancement failed: {e}")
            
            return EnhancementResult(
                type=EnhancementType.WEATHER,
                success=False,
                processing_time_ms=processing_time,
                error_message=str(e)
            )

class TransportEnhancementModule(BaseEnhancementModule):
    """Transport information enhancement module (placeholder for future implementation)"""
    
    def __init__(self):
        super().__init__(EnhancementType.TRANSPORT)
    
    async def enhance(
        self, 
        base_plan: Dict[str, Any], 
        config: EnhancementConfig,
        request: IntegratedPlanningRequest
    ) -> EnhancementResult:
        """Add transport information to the plan"""
        
        start_time = time.time()
        
        try:
            # TODO: Implement transport API integration
            
            transport_data = {
                "recommendations": "Transport integration coming soon",
                "local_options": [
                    "Tuk-tuk for short distances",
                    "Train for scenic routes",
                    "Bus for budget travel"
                ]
            }
            
            processing_time = (time.time() - start_time) * 1000
            
            return EnhancementResult(
                type=EnhancementType.TRANSPORT,
                success=True,
                data=transport_data,
                processing_time_ms=processing_time
            )
            
        except Exception as e:
            processing_time = (time.time() - start_time) * 1000
            self.logger.error(f"Transport enhancement failed: {e}")
            
            return EnhancementResult(
                type=EnhancementType.TRANSPORT,
                success=False,
                processing_time_ms=processing_time,
                error_message=str(e)
            )

class IntegratedTravelPlanningService:
    """Main service for integrated travel planning with modular enhancements"""
    
    def __init__(self):
        self.logger = logging.getLogger("integrated_planning")
        
        # Initialize enhancement modules
        self.enhancement_modules = {
            EnhancementType.PLACES: PlacesEnhancementModule(),
            EnhancementType.WEATHER: WeatherEnhancementModule(),
            EnhancementType.TRANSPORT: TransportEnhancementModule()
        }
    
    async def create_integrated_plan(
        self, 
        request: IntegratedPlanningRequest
    ) -> IntegratedPlanningResponse:
        """Create integrated travel plan with requested enhancements"""
        
        total_start_time = time.time()
        
        try:
            # Step 1: Generate base clustered plan
            self.logger.info("Generating base clustered plan...")
            base_plan = await self._generate_base_plan(request)
            
            # Step 2: Apply enhancements based on configuration
            self.logger.info("Applying enhancements...")
            enhancement_results = await self._apply_enhancements(base_plan, request)
            
            # Step 3: Integrate all results
            self.logger.info("Integrating results...")
            integrated_itineraries = await self._integrate_results(
                base_plan, enhancement_results, request
            )
            
            total_processing_time = (time.time() - total_start_time) * 1000
            
            # Collect successful enhancements
            successful_enhancements = [
                enhancement_type for enhancement_type, result in enhancement_results.items()
                if result.success
            ]
            
            # Generate stats
            stats = self._generate_stats(base_plan, enhancement_results, request)
            
            return IntegratedPlanningResponse(
                base_plan=base_plan,
                enhancements=enhancement_results,
                daily_itineraries=integrated_itineraries,
                total_processing_time_ms=total_processing_time,
                enhancements_applied=successful_enhancements,
                stats=stats
            )
            
        except Exception as e:
            self.logger.error(f"Integrated planning failed: {e}")
            raise Exception(f"Failed to create integrated plan: {str(e)}")
    
    async def _generate_base_plan(self, request: IntegratedPlanningRequest) -> Dict[str, Any]:
        """Generate base clustered plan"""
        
        # Import the clustering router function
        from router.clustered_recommendations import get_clustered_travel_plan, ClusteredRecommendationRequest
        
        # Create clustering request using the proper model
        cluster_request = ClusteredRecommendationRequest(
            query=request.query,
            interests=request.interests,
            trip_duration_days=request.trip_duration_days,
            daily_travel_preference=request.daily_travel_preference,
            max_attractions_per_day=request.max_attractions_per_day,
            budget_level=request.budget_level,
            group_size=request.group_size
        )
        
        # Generate base plan using existing clustering logic
        base_plan = await get_clustered_travel_plan(cluster_request)
        
        # Convert Pydantic response to dict for easier processing
        if hasattr(base_plan, 'dict'):
            base_plan = base_plan.dict()
        
        return base_plan
    
    async def _apply_enhancements(
        self, 
        base_plan: Dict[str, Any], 
        request: IntegratedPlanningRequest
    ) -> Dict[EnhancementType, EnhancementResult]:
        """Apply requested enhancements to base plan"""
        
        enhancement_results = {}
        
        # Sort enhancements by priority
        enabled_enhancements = [
            (enhancement_type, config) 
            for enhancement_type, config in request.enhancements.items()
            if config.enabled and enhancement_type in self.enhancement_modules
        ]
        
        enabled_enhancements.sort(key=lambda x: x[1].priority)
        
        # Apply enhancements
        if request.async_processing:
            # Apply enhancements in parallel for better performance
            import asyncio
            tasks = []
            
            for enhancement_type, config in enabled_enhancements:
                module = self.enhancement_modules[enhancement_type]
                task = module.enhance(base_plan, config, request)
                tasks.append((enhancement_type, task))
            
            # Wait for all enhancements to complete
            for enhancement_type, task in tasks:
                try:
                    result = await task
                    enhancement_results[enhancement_type] = result
                except Exception as e:
                    self.logger.error(f"Enhancement {enhancement_type} failed: {e}")
                    enhancement_results[enhancement_type] = EnhancementResult(
                        type=enhancement_type,
                        success=False,
                        processing_time_ms=0,
                        error_message=str(e)
                    )
        else:
            # Apply enhancements sequentially
            for enhancement_type, config in enabled_enhancements:
                try:
                    module = self.enhancement_modules[enhancement_type]
                    result = await module.enhance(base_plan, config, request)
                    enhancement_results[enhancement_type] = result
                except Exception as e:
                    self.logger.error(f"Enhancement {enhancement_type} failed: {e}")
                    enhancement_results[enhancement_type] = EnhancementResult(
                        type=enhancement_type,
                        success=False,
                        processing_time_ms=0,
                        error_message=str(e)
                    )
        
        return enhancement_results
    
    async def _integrate_results(
        self, 
        base_plan: Dict[str, Any], 
        enhancement_results: Dict[EnhancementType, EnhancementResult],
        request: IntegratedPlanningRequest
    ) -> List[Dict[str, Any]]:
        """Integrate all enhancement results into daily itineraries"""
        
        # Start with base daily itineraries
        daily_itineraries = base_plan.get("daily_itineraries", [])
        
        # Integrate places if available
        if (EnhancementType.PLACES in enhancement_results and 
            enhancement_results[EnhancementType.PLACES].success):
            
            places_data = enhancement_results[EnhancementType.PLACES].data
            place_recommendations = places_data.get("place_recommendations", [])
            
            # Add places to each day
            for i, day_plan in enumerate(daily_itineraries):
                if i < len(place_recommendations):
                    day_plan["place_recommendations"] = place_recommendations[i]
        
        # Integrate weather if available
        if (EnhancementType.WEATHER in enhancement_results and 
            enhancement_results[EnhancementType.WEATHER].success):
            
            weather_data = enhancement_results[EnhancementType.WEATHER].data
            
            # Add weather to each day
            for day_plan in daily_itineraries:
                day_plan["weather_info"] = weather_data
        
        # Integrate transport if available
        if (EnhancementType.TRANSPORT in enhancement_results and 
            enhancement_results[EnhancementType.TRANSPORT].success):
            
            transport_data = enhancement_results[EnhancementType.TRANSPORT].data
            
            # Add transport to each day
            for day_plan in daily_itineraries:
                day_plan["transport_info"] = transport_data
        
        return daily_itineraries
    
    def _generate_stats(
        self, 
        base_plan: Dict[str, Any], 
        enhancement_results: Dict[EnhancementType, EnhancementResult],
        request: IntegratedPlanningRequest
    ) -> Dict[str, Any]:
        """Generate comprehensive statistics"""
        
        stats = {
            "base_plan": {
                "total_attractions": base_plan.get("total_attractions", 0),
                "total_days": base_plan.get("total_days", 0),
                "total_distance_km": base_plan.get("overall_stats", {}).get("total_distance_km", 0)
            },
            "enhancements": {}
        }
        
        # Add enhancement stats
        for enhancement_type, result in enhancement_results.items():
            stats["enhancements"][enhancement_type.value] = {
                "success": result.success,
                "processing_time_ms": result.processing_time_ms,
                "data_added": len(result.data) if result.success else 0
            }
            
            # Special handling for places stats
            if enhancement_type == EnhancementType.PLACES and result.success:
                enhancement_stats = result.data.get("enhancement_stats", {})
                stats["enhancements"]["places"]["total_places_added"] = enhancement_stats.get("total_places_added", 0)
                stats["enhancements"]["places"]["restaurants"] = enhancement_stats.get("total_restaurants", 0)
                stats["enhancements"]["places"]["accommodations"] = enhancement_stats.get("total_accommodations", 0)
        
        return stats

# Singleton service instance
_integrated_service = None

def get_integrated_planning_service() -> IntegratedTravelPlanningService:
    """Get singleton instance of integrated planning service"""
    global _integrated_service
    if _integrated_service is None:
        _integrated_service = IntegratedTravelPlanningService()
    return _integrated_service
