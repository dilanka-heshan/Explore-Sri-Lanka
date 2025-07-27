from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any, Union
from datetime import datetime, date, time
from enum import Enum

# Enums
class InterestType(str, Enum):
    CULTURAL = "cultural"
    NATURE = "nature"
    ADVENTURE = "adventure"
    BEACH = "beach"
    WILDLIFE = "wildlife"
    HISTORICAL = "historical"
    PHOTOGRAPHY = "photography"
    FOOD = "food"
    SPIRITUAL = "spiritual"
    SHOPPING = "shopping"

class TripType(str, Enum):
    SOLO = "solo"
    COUPLE = "couple"
    FAMILY = "family"
    GROUP = "group"

class BudgetLevel(str, Enum):
    BUDGET = "budget"
    MID_RANGE = "mid_range"
    LUXURY = "luxury"

class DifficultyLevel(str, Enum):
    EASY = "easy"
    MODERATE = "moderate"
    CHALLENGING = "challenging"

# User Profile Models
class UserProfile(BaseModel):
    interests: List[InterestType]
    trip_type: TripType
    budget_level: BudgetLevel
    age_group: Optional[str] = None
    mobility_requirements: Optional[str] = None
    preferred_pace: Optional[str] = "moderate"  # slow, moderate, fast
    cultural_interest_level: Optional[int] = Field(ge=1, le=5, default=3)
    adventure_level: Optional[int] = Field(ge=1, le=5, default=3)
    nature_appreciation: Optional[int] = Field(ge=1, le=5, default=3)

# Attraction/Destination Models
class Attraction(BaseModel):
    id: str
    name: str
    description: str
    category: InterestType
    latitude: float
    longitude: float
    rating: float = Field(ge=0, le=5)
    review_count: int = 0
    tags: List[str] = []
    entry_fee: Optional[float] = None
    opening_hours: Optional[Dict[str, str]] = None
    visit_duration_minutes: Optional[int] = None
    difficulty_level: DifficultyLevel = DifficultyLevel.EASY
    best_season: Optional[str] = None
    facilities: List[str] = []
    nearby_restaurants: List[str] = []
    nearby_hotels: List[str] = []
    pear_score: Optional[float] = None  # Computed by PEAR model

# Geographic Clustering Models
class GeoCluster(BaseModel):
    cluster_id: int
    center_lat: float
    center_lng: float
    attractions: List[Attraction]
    total_pear_score: float
    estimated_time_hours: float
    value_per_hour: float
    region_name: Optional[str] = None

# Route Optimization Models
class RouteSegment(BaseModel):
    from_attraction_id: str
    to_attraction_id: str
    distance_km: float
    travel_time_minutes: int
    transport_mode: str = "car"

class OptimizedRoute(BaseModel):
    attraction_order: List[str]
    total_distance_km: float
    total_travel_time_minutes: int
    segments: List[RouteSegment]

# Time Schedule Models
class ScheduleItem(BaseModel):
    attraction_id: str
    attraction_name: str
    start_time: time
    end_time: time
    visit_duration_minutes: int
    notes: Optional[str] = None

class DaySchedule(BaseModel):
    day: int
    date: date
    cluster_id: int
    cluster_name: str
    items: List[ScheduleItem]
    lunch_time: Optional[time] = None
    lunch_location: Optional[str] = None
    accommodation: Optional[str] = None
    total_attractions: int
    total_travel_time_minutes: int

# Request/Response Models
class TravelPlanRequest(BaseModel):
    user_profile: UserProfile
    duration_days: int = Field(ge=1, le=30)
    start_date: date
    daily_start_time: time = Field(default=time(9, 0))  # 9 AM
    daily_end_time: time = Field(default=time(18, 0))   # 6 PM
    max_travel_time_per_day_hours: float = Field(default=3.0)
    preferred_regions: Optional[List[str]] = None
    excluded_attractions: Optional[List[str]] = None
    special_requirements: Optional[str] = None

class TravelPlanResponse(BaseModel):
    plan_id: str
    user_profile: UserProfile
    total_days: int
    total_attractions: int
    daily_schedules: List[DaySchedule]
    recommended_hotels: List[Dict[str, Any]]
    recommended_restaurants: List[Dict[str, Any]]
    total_estimated_cost: Optional[float] = None
    weather_considerations: Optional[str] = None
    packing_suggestions: List[str] = []
    local_tips: List[str] = []
    emergency_contacts: List[str] = []
    alternative_suggestions: Optional[List[str]] = None
    explanation: str  # LLM-generated explanation of choices

# Vector DB Models
class AttractionEmbedding(BaseModel):
    attraction_id: str
    embedding: List[float]
    metadata: Dict[str, Any]

class UserProfileEmbedding(BaseModel):
    profile_hash: str
    embedding: List[float]
    profile_data: UserProfile

# PEAR Model Prediction
class PEARPrediction(BaseModel):
    attraction_id: str
    user_profile_hash: str
    relevance_score: float
    confidence: float
    reasoning: Optional[str] = None

# Planning State (for LangGraph)
class PlanningState(BaseModel):
    user_input: str
    user_profile: Optional[UserProfile] = None
    duration_days: Optional[int] = None
    start_date: Optional[date] = None
    parsed_interests: List[str] = []
    candidate_attractions: List[Attraction] = []
    pear_ranked_attractions: List[Attraction] = []
    geo_clusters: List[GeoCluster] = []
    selected_clusters: List[GeoCluster] = []
    optimized_routes: Dict[int, OptimizedRoute] = {}  # cluster_id -> route
    daily_schedules: List[DaySchedule] = []
    final_plan: Optional[TravelPlanResponse] = None
    reasoning_log: List[str] = []

# Additional Models for External APIs
class OpenRouteServiceResponse(BaseModel):
    distance: float
    duration: float
    geometry: Optional[Dict[str, Any]] = None

class GooglePlacesResult(BaseModel):
    place_id: str
    name: str
    rating: Optional[float] = None
    price_level: Optional[int] = None
    types: List[str] = []
    vicinity: Optional[str] = None
    geometry: Dict[str, Any]

# Error Models
class PlanningError(BaseModel):
    error_type: str
    message: str
    suggestions: List[str] = []
    retry_possible: bool = True

# User Interest Collection Models
class UserInterestSurvey(BaseModel):
    user_id: Optional[str] = None
    session_id: str
    
    # Basic Demographics
    age_range: Optional[str] = Field(None, description="18-25, 26-35, 36-50, 50+")
    travel_experience: Optional[str] = Field(None, description="beginner, intermediate, expert")
    
    # Interest Preferences (1-5 scale)
    cultural_sites_interest: int = Field(ge=1, le=5, default=3)
    nature_wildlife_interest: int = Field(ge=1, le=5, default=3)
    adventure_sports_interest: int = Field(ge=1, le=5, default=3)
    beach_relaxation_interest: int = Field(ge=1, le=5, default=3)
    food_culinary_interest: int = Field(ge=1, le=5, default=3)
    historical_sites_interest: int = Field(ge=1, le=5, default=3)
    photography_interest: int = Field(ge=1, le=5, default=3)
    spiritual_religious_interest: int = Field(ge=1, le=5, default=3)
    shopping_interest: int = Field(ge=1, le=5, default=3)
    
    # Travel Style Preferences
    preferred_pace: str = Field(default="moderate", description="slow, moderate, fast")
    accommodation_preference: BudgetLevel = BudgetLevel.MID_RANGE
    activity_level: str = Field(default="moderate", description="low, moderate, high")
    
    # Group and Accessibility
    typical_group_size: int = Field(ge=1, le=20, default=2)
    mobility_requirements: Optional[str] = None
    dietary_restrictions: Optional[List[str]] = []
    
    # Previous Travel History (for PEAR model training)
    visited_places: List[str] = []
    favorite_destinations: List[str] = []
    least_favorite_destinations: List[str] = []
    
    # Feedback on recommendations (for learning)
    previous_recommendations_feedback: Optional[Dict[str, int]] = None  # attraction_id -> rating

# Dataset Upload Models
class AttractionDataUpload(BaseModel):
    name: str
    description: str
    category: InterestType
    latitude: float = Field(ge=-90, le=90)
    longitude: float = Field(ge=-180, le=180)
    rating: float = Field(ge=0, le=5, default=0)
    review_count: int = Field(ge=0, default=0)
    tags: List[str] = []
    entry_fee_lkr: Optional[float] = None
    opening_hours: Optional[Dict[str, str]] = None
    visit_duration_hours: float = Field(gt=0, le=24, description="Hours to spend at attraction")
    difficulty_level: DifficultyLevel = DifficultyLevel.EASY
    best_season: Optional[str] = None
    facilities: List[str] = []
    contact_info: Optional[Dict[str, str]] = None
    website: Optional[str] = None
    images: List[str] = []
    
    # Additional metadata for ML models
    popularity_score: Optional[float] = Field(ge=0, le=1, default=0.5)
    accessibility_features: List[str] = []
    recommended_for: List[TripType] = []
    suitable_for_budget: List[BudgetLevel] = []

class DatasetUploadRequest(BaseModel):
    attractions: List[AttractionDataUpload]
    source: str = Field(description="Source of the data (e.g., 'manual_entry', 'csv_import', 'api_sync')")
    upload_timestamp: datetime = Field(default_factory=datetime.now)
    uploader_id: Optional[str] = None
    validation_settings: Optional[Dict[str, Any]] = None

class DatasetUploadResponse(BaseModel):
    success: bool
    uploaded_count: int
    failed_count: int
    failed_items: List[Dict[str, Any]] = []
    qdrant_sync_status: str  # "success", "partial", "failed"
    database_sync_status: str
    message: str

# Stored Itinerary Models
class StoredItinerary(BaseModel):
    id: str = Field(description="Unique itinerary ID")
    user_id: Optional[str] = None
    session_id: str
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    
    # Original request
    original_request: TravelPlanRequest
    
    # Generated plan
    travel_plan: TravelPlanResponse
    
    # User feedback and modifications
    user_rating: Optional[int] = Field(ge=1, le=5, default=None)
    user_feedback: Optional[str] = None
    modifications_made: List[str] = []
    
    # Usage tracking
    times_accessed: int = 0
    shared_count: int = 0
    is_public: bool = False
    
    # Status
    status: str = Field(default="active", description="active, archived, deleted")

class ItineraryQueryRequest(BaseModel):
    user_id: Optional[str] = None
    session_id: Optional[str] = None
    date_range: Optional[Dict[str, date]] = None
    status: Optional[str] = None
    limit: int = Field(ge=1, le=100, default=10)
    offset: int = Field(ge=0, default=0)

# Mock User Data Models (for testing)
class MockUserProfile(BaseModel):
    user_id: str
    name: str
    age_range: str
    interests: List[InterestType]
    trip_history: List[Dict[str, Any]]
    preference_scores: Dict[str, float]
    budget_range: BudgetLevel
    travel_style: Dict[str, Any]
    
    class Config:
        schema_extra = {
            "example": {
                "user_id": "user_001",
                "name": "Adventure Seeker",
                "age_range": "26-35",
                "interests": ["adventure", "nature", "photography"],
                "trip_history": [
                    {"destination": "Ella", "rating": 5, "activities": ["hiking", "train_ride"]},
                    {"destination": "Sigiriya", "rating": 4, "activities": ["historical_sites", "photography"]}
                ],
                "preference_scores": {
                    "adventure_level": 0.9,
                    "cultural_interest": 0.6,
                    "nature_appreciation": 0.8,
                    "budget_consciousness": 0.4
                },
                "budget_range": "mid_range",
                "travel_style": {
                    "pace": "moderate",
                    "group_preference": "couple",
                    "accommodation": "boutique_hotels"
                }
            }
        }

# Enhanced User Profile with ML Features
class EnhancedUserProfile(UserProfile):
    # Additional fields for ML model
    profile_embedding: Optional[List[float]] = None
    interaction_history: List[Dict[str, Any]] = []
    seasonal_preferences: Optional[Dict[str, float]] = None
    time_of_day_preferences: Optional[Dict[str, float]] = None
    
    # Learning from feedback
    recommendation_feedback_history: List[Dict[str, Any]] = []
    preference_evolution: Optional[Dict[str, List[float]]] = None  # Track how preferences change over time