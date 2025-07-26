"""
Authentication and User Management Models
"""
from pydantic import BaseModel, EmailStr, validator
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum

class UserRole(str, Enum):
    USER = "user"
    ADMIN = "admin"
    MODERATOR = "moderator"

class TravelStyle(str, Enum):
    SOLO = "solo"
    COUPLE = "couple"
    FAMILY = "family"
    GROUP = "group"

class BudgetLevel(str, Enum):
    BUDGET = "budget"
    MID_RANGE = "mid_range"
    LUXURY = "luxury"

# Base Models
class UserBase(BaseModel):
    email: EmailStr
    full_name: str
    avatar_url: Optional[str] = None
    phone: Optional[str] = None
    date_of_birth: Optional[datetime] = None
    nationality: Optional[str] = None
    location: Optional[str] = None
    bio: Optional[str] = None

class UserCreate(UserBase):
    password: str
    confirm_password: str
    
    @validator('confirm_password')
    def passwords_match(cls, v, values, **kwargs):
        if 'password' in values and v != values['password']:
            raise ValueError('Passwords do not match')
        return v

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserUpdate(BaseModel):
    full_name: Optional[str] = None
    avatar_url: Optional[str] = None
    phone: Optional[str] = None
    date_of_birth: Optional[datetime] = None
    nationality: Optional[str] = None
    location: Optional[str] = None
    bio: Optional[str] = None

class PasswordUpdate(BaseModel):
    current_password: str
    new_password: str
    confirm_password: str
    
    @validator('confirm_password')
    def passwords_match(cls, v, values, **kwargs):
        if 'new_password' in values and v != values['new_password']:
            raise ValueError('Passwords do not match')
        return v

# Travel Preferences
class TravelPreferences(BaseModel):
    interests: List[str] = []
    preferred_destinations: List[str] = []
    travel_style: Optional[TravelStyle] = None
    budget_level: BudgetLevel = BudgetLevel.MID_RANGE
    adventure_level: int = 3  # 1-5 scale
    accessibility_needs: Optional[str] = None
    dietary_restrictions: List[str] = []
    accommodation_preferences: List[str] = []
    transportation_preferences: List[str] = []
    activity_preferences: List[str] = []
    
    @validator('adventure_level')
    def validate_adventure_level(cls, v):
        if not (1 <= v <= 5):
            raise ValueError('Adventure level must be between 1 and 5')
        return v

class UserPreferencesUpdate(BaseModel):
    travel_preferences: Optional[TravelPreferences] = None

# Response Models
class UserResponse(UserBase):
    id: str
    role: UserRole = UserRole.USER
    email_verified: bool = False
    is_active: bool = True
    created_at: datetime
    updated_at: Optional[datetime] = None
    last_login: Optional[datetime] = None
    
    class Config:
        from_attributes = True

class UserProfileResponse(UserResponse):
    travel_preferences: Optional[TravelPreferences] = None
    total_reviews: int = 0
    total_bookings: int = 0
    favorite_destinations: List[str] = []

# Authentication Response Models
class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int

class TokenData(BaseModel):
    email: Optional[str] = None
    user_id: Optional[str] = None
    role: Optional[UserRole] = None

class AuthResponse(BaseModel):
    user: UserResponse
    token: Token

# Password Reset Models
class PasswordResetRequest(BaseModel):
    email: EmailStr

class PasswordReset(BaseModel):
    token: str
    new_password: str
    confirm_password: str
    
    @validator('confirm_password')
    def passwords_match(cls, v, values, **kwargs):
        if 'new_password' in values and v != values['new_password']:
            raise ValueError('Passwords do not match')
        return v

# Email Verification Models
class EmailVerificationRequest(BaseModel):
    email: EmailStr

class EmailVerification(BaseModel):
    token: str

# Saved Items Models
class SavedDestination(BaseModel):
    destination_id: str
    saved_at: datetime

class SavedItinerary(BaseModel):
    itinerary_id: str
    saved_at: datetime

class UserSavedItems(BaseModel):
    destinations: List[SavedDestination] = []
    itineraries: List[SavedItinerary] = []

# Trip History Models
class TripHistoryItem(BaseModel):
    id: str
    destination_name: str
    visit_date: datetime
    duration_days: int
    rating: Optional[int] = None
    review_id: Optional[str] = None

class UserTripHistory(BaseModel):
    trips: List[TripHistoryItem] = []
    total_countries_visited: int = 0
    total_destinations_visited: int = 0
