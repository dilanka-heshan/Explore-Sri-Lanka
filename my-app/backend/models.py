from pydantic import BaseModel, EmailStr, Field
from typing import List, Optional, Dict, Any
from datetime import datetime, date
from enum import Enum

# Enums
class DestinationType(str, Enum):
    CULTURAL = "Cultural"
    BEACH = "Beach"
    NATURE = "Nature"
    WILDLIFE = "Wildlife"
    HISTORICAL = "Historical"
    ADVENTURE = "Adventure"

class RegionType(str, Enum):
    CENTRAL = "Central"
    SOUTHERN = "Southern"
    NORTHERN = "Northern"
    EASTERN = "Eastern"
    WESTERN = "Western"
    NORTH_CENTRAL = "North Central"
    NORTH_WESTERN = "North Western"
    SABARAGAMUWA = "Sabaragamuwa"
    UVA = "Uva"

class TripType(str, Enum):
    SOLO = "solo"
    COUPLE = "couple"
    FAMILY = "family"
    PHOTOGRAPHY = "photography"
    ADVENTURE = "adventure"
    CULTURAL = "cultural"

class BookingStatus(str, Enum):
    PENDING = "pending"
    CONFIRMED = "confirmed"
    CANCELLED = "cancelled"
    COMPLETED = "completed"

# Base models
class BaseResponse(BaseModel):
    id: str
    created_at: datetime
    updated_at: Optional[datetime] = None

# Destination models
class DestinationBase(BaseModel):
    name: str
    slug: str
    description: Optional[str] = None
    long_description: Optional[str] = None
    image_url: Optional[str] = None
    gallery_images: Optional[List[str]] = []
    region: RegionType
    destination_type: DestinationType
    best_season: Optional[str] = None
    highlights: Optional[List[str]] = []
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    entry_fee: Optional[float] = None
    opening_hours: Optional[Dict[str, Any]] = None
    facilities: Optional[List[str]] = []
    nearby_attractions: Optional[List[str]] = []

class DestinationCreate(DestinationBase):
    pass

class DestinationResponse(DestinationBase, BaseResponse):
    rating: Optional[float] = 0.0
    review_count: Optional[int] = 0

class DestinationDetailResponse(DestinationResponse):
    experiences: Optional[List['ExperienceResponse']] = []
    recent_reviews: Optional[List['ReviewResponse']] = []

# Experience models
class ExperienceBase(BaseModel):
    title: str
    slug: str
    description: Optional[str] = None
    image_url: Optional[str] = None
    category: Optional[str] = None
    duration: Optional[str] = None
    difficulty_level: Optional[str] = None
    price_from: Optional[float] = None
    includes: Optional[List[str]] = []
    requirements: Optional[List[str]] = []
    destination_id: Optional[str] = None

class ExperienceCreate(ExperienceBase):
    pass

class ExperienceResponse(ExperienceBase, BaseResponse):
    destination: Optional[DestinationResponse] = None

class ExperienceDetailResponse(ExperienceResponse):
    pass

# Review models
class ReviewBase(BaseModel):
    user_name: str
    user_email: Optional[EmailStr] = None
    rating: int = Field(..., ge=1, le=5)
    title: Optional[str] = None
    content: Optional[str] = None

class ReviewCreate(ReviewBase):
    pass

class ReviewResponse(ReviewBase, BaseResponse):
    destination_id: str
    helpful_count: Optional[int] = 0

# Itinerary models
class ItineraryBase(BaseModel):
    title: str
    slug: str
    description: Optional[str] = None
    duration_days: int
    price: Optional[float] = None
    image_url: Optional[str] = None
    highlights: Optional[List[str]] = []
    best_for: Optional[List[str]] = []
    trip_type: Optional[TripType] = None
    day_by_day: Optional[Dict[str, Any]] = None
    includes: Optional[List[str]] = []
    excludes: Optional[List[str]] = []

class ItineraryCreate(ItineraryBase):
    pass

class ItineraryResponse(ItineraryBase, BaseResponse):
    pass

class ItineraryDetailResponse(ItineraryResponse):
    pass

# Blog models
class BlogPostBase(BaseModel):
    title: str
    slug: str
    excerpt: Optional[str] = None
    content: Optional[str] = None
    image_url: Optional[str] = None
    author_name: Optional[str] = None
    author_avatar: Optional[str] = None
    category: Optional[str] = None
    tags: Optional[List[str]] = []
    published: bool = False
    published_at: Optional[datetime] = None

class BlogPostCreate(BlogPostBase):
    pass

class BlogPostResponse(BlogPostBase, BaseResponse):
    pass

class BlogPostDetailResponse(BlogPostResponse):
    pass

# Booking models
class BookingBase(BaseModel):
    itinerary_id: str
    customer_name: str
    customer_email: EmailStr
    customer_phone: Optional[str] = None
    travel_date: Optional[date] = None
    number_of_travelers: int = Field(..., ge=1)
    special_requests: Optional[str] = None
    total_price: Optional[float] = None

class BookingCreate(BookingBase):
    pass

class BookingResponse(BookingBase, BaseResponse):
    status: BookingStatus = BookingStatus.PENDING
    itinerary: Optional[ItineraryResponse] = None

# Newsletter models
class NewsletterSubscription(BaseModel):
    email: EmailStr

# Contact models
class ContactMessage(BaseModel):
    name: str
    email: EmailStr
    subject: Optional[str] = None
    message: str

# Media models
class MediaBase(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    image_url: str
    thumbnail_url: Optional[str] = None
    category: Optional[str] = None
    destination_id: Optional[str] = None
    photographer: Optional[str] = None
    tags: Optional[List[str]] = []
    featured: bool = False

class MediaCreate(MediaBase):
    pass

class MediaResponse(MediaBase, BaseResponse):
    destination: Optional[DestinationResponse] = None

# Search models
class SearchResult(BaseModel):
    type: str  # destination, experience, blog
    id: str
    title: str
    description: Optional[str] = None
    image_url: Optional[str] = None
    slug: str
    relevance_score: Optional[float] = None

class SearchResponse(BaseModel):
    query: str
    total_results: int
    results: List[SearchResult]

# Update forward references
DestinationDetailResponse.model_rebuild()
ExperienceResponse.model_rebuild()
BookingResponse.model_rebuild()
MediaResponse.model_rebuild()
