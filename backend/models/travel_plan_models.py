"""
Enhanced Travel Plan Storage Models for User Trip Management
"""
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum
import uuid


class TripStatus(str, Enum):
    DRAFT = "draft"
    ACTIVE = "active"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    ARCHIVED = "archived"


class TripPrivacy(str, Enum):
    PRIVATE = "private"
    PUBLIC = "public"
    SHARED = "shared"


class UserTravelPlan(BaseModel):
    """Complete user travel plan with all details"""
    # Basic identification
    id: str = Field(default_factory=lambda: str(uuid.uuid4()), description="Unique travel plan ID")
    user_id: str = Field(..., description="User who created this plan")
    
    # Plan metadata
    title: str = Field(..., description="User-defined title for the trip")
    description: Optional[str] = Field(None, description="User description/notes about the trip")
    
    # Trip details
    destination_summary: str = Field(..., description="Main destinations covered")
    trip_duration_days: int = Field(..., description="Total duration in days")
    budget_level: str = Field(..., description="Budget level: budget, mid_range, luxury")
    trip_type: str = Field(..., description="Trip type: solo, couple, family, group")
    
    # Original planning request
    original_query: str = Field(..., description="Original user query")
    interests: List[str] = Field(default_factory=list, description="User interests")
    
    # Generated travel plan (JSON structure)
    travel_plan_data: Dict[str, Any] = Field(..., description="Complete travel plan JSON")
    
    # Enhanced plan details (if applicable)
    has_places_enhancement: bool = Field(default=False, description="Whether plan includes Google Places data")
    has_ai_enhancement: bool = Field(default=False, description="Whether plan includes AI enhancements")
    clustering_method: Optional[str] = Field(None, description="Clustering method used")
    
    # User interaction
    status: TripStatus = Field(default=TripStatus.DRAFT, description="Current status of the trip")
    privacy: TripPrivacy = Field(default=TripPrivacy.PRIVATE, description="Privacy setting")
    
    # User feedback
    user_rating: Optional[int] = Field(None, ge=1, le=5, description="User rating (1-5)")
    user_notes: Optional[str] = Field(None, description="User's personal notes")
    favorite: bool = Field(default=False, description="Whether user marked as favorite")
    
    # Actual trip details (for completed trips)
    planned_start_date: Optional[datetime] = Field(None, description="Planned start date")
    actual_start_date: Optional[datetime] = Field(None, description="Actual start date")
    actual_end_date: Optional[datetime] = Field(None, description="Actual end date")
    
    # Sharing and collaboration
    shared_with: List[str] = Field(default_factory=list, description="User IDs plan is shared with")
    collaboration_enabled: bool = Field(default=False, description="Whether others can edit")
    
    # Analytics and usage
    times_viewed: int = Field(default=0, description="Number of times viewed")
    times_downloaded: int = Field(default=0, description="Number of times PDF downloaded")
    last_accessed: Optional[datetime] = Field(None, description="Last access time")
    
    # PDF generation
    pdf_generated: bool = Field(default=False, description="Whether PDF has been generated")
    pdf_file_path: Optional[str] = Field(None, description="Path to generated PDF file")
    pdf_generated_at: Optional[datetime] = Field(None, description="When PDF was generated")
    
    # Timestamps
    created_at: datetime = Field(default_factory=datetime.now, description="Creation timestamp")
    updated_at: datetime = Field(default_factory=datetime.now, description="Last update timestamp")
    
    # Modifications tracking
    modifications: List[Dict[str, Any]] = Field(default_factory=list, description="History of modifications")
    
    # Cost tracking (optional)
    estimated_cost: Optional[Dict[str, float]] = Field(None, description="Estimated costs breakdown")
    actual_cost: Optional[Dict[str, float]] = Field(None, description="Actual costs breakdown")


class TravelPlanCreate(BaseModel):
    """Data for creating a new travel plan"""
    title: str = Field(..., min_length=1, max_length=200, description="Trip title")
    description: Optional[str] = Field(None, max_length=1000, description="Trip description")
    travel_plan_data: Dict[str, Any] = Field(..., description="Complete travel plan JSON")
    original_query: str = Field(..., description="Original user query")
    interests: List[str] = Field(default_factory=list, description="User interests")
    trip_duration_days: int = Field(..., ge=1, le=365, description="Trip duration")
    budget_level: str = Field(..., description="Budget level")
    trip_type: str = Field(..., description="Trip type")
    planned_start_date: Optional[datetime] = Field(None, description="Planned start date")
    privacy: TripPrivacy = Field(default=TripPrivacy.PRIVATE, description="Privacy setting")


class TravelPlanUpdate(BaseModel):
    """Data for updating an existing travel plan"""
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = Field(None, max_length=1000)
    status: Optional[TripStatus] = None
    privacy: Optional[TripPrivacy] = None
    user_rating: Optional[int] = Field(None, ge=1, le=5)
    user_notes: Optional[str] = Field(None, max_length=2000)
    favorite: Optional[bool] = None
    planned_start_date: Optional[datetime] = None
    actual_start_date: Optional[datetime] = None
    actual_end_date: Optional[datetime] = None


class TravelPlanQuery(BaseModel):
    """Query parameters for retrieving travel plans"""
    status: Optional[TripStatus] = None
    privacy: Optional[TripPrivacy] = None
    favorite_only: bool = Field(default=False)
    date_from: Optional[datetime] = None
    date_to: Optional[datetime] = None
    search_query: Optional[str] = None
    budget_level: Optional[str] = None
    trip_type: Optional[str] = None
    limit: int = Field(default=20, ge=1, le=100)
    offset: int = Field(default=0, ge=0)
    sort_by: str = Field(default="created_at", description="Sort field")
    sort_order: str = Field(default="desc", description="Sort order: asc, desc")


class TravelPlanSummary(BaseModel):
    """Summary view of travel plan for lists"""
    id: str
    title: str
    destination_summary: str
    trip_duration_days: int
    budget_level: str
    trip_type: str
    status: TripStatus
    favorite: bool
    user_rating: Optional[int]
    planned_start_date: Optional[datetime]
    created_at: datetime
    updated_at: datetime
    times_viewed: int
    pdf_generated: bool


class TravelPlanResponse(BaseModel):
    """Full travel plan response"""
    plan: UserTravelPlan
    can_edit: bool = Field(default=True, description="Whether current user can edit")
    can_download: bool = Field(default=True, description="Whether current user can download PDF")


class TravelPlanStats(BaseModel):
    """User travel plan statistics"""
    total_plans: int
    draft_plans: int
    active_plans: int
    completed_plans: int
    favorite_plans: int
    total_destinations: int
    total_trip_days: int
    average_rating: Optional[float]
    most_visited_destinations: List[Dict[str, Any]]
    budget_distribution: Dict[str, int]
    trip_type_distribution: Dict[str, int]


# PDF Generation Models
class PDFGenerationRequest(BaseModel):
    """Request for PDF generation"""
    travel_plan_id: str
    include_maps: bool = Field(default=True, description="Include location maps")
    include_photos: bool = Field(default=True, description="Include destination photos")
    include_weather: bool = Field(default=True, description="Include weather information")
    custom_logo_url: Optional[str] = Field(None, description="Custom logo URL")
    custom_title: Optional[str] = Field(None, description="Custom PDF title")


class PDFGenerationResponse(BaseModel):
    """Response from PDF generation"""
    success: bool
    pdf_url: Optional[str] = None
    file_path: Optional[str] = None
    file_size_mb: Optional[float] = None
    generation_time_seconds: Optional[float] = None
    error_message: Optional[str] = None


# Sharing Models
class TravelPlanShare(BaseModel):
    """Travel plan sharing configuration"""
    travel_plan_id: str
    shared_with_emails: List[str] = Field(..., description="Emails to share with")
    can_edit: bool = Field(default=False, description="Whether shared users can edit")
    message: Optional[str] = Field(None, max_length=500, description="Optional message")


class SharedTravelPlan(BaseModel):
    """Shared travel plan access"""
    id: str
    travel_plan_id: str
    shared_by_user_id: str
    shared_with_user_id: str
    can_edit: bool
    shared_at: datetime
    last_accessed: Optional[datetime]
    message: Optional[str]
