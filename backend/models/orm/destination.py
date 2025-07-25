"""
Destination ORM Model for Supabase
"""
from sqlalchemy import Column, Integer, String, Text, Float, DateTime, Boolean, JSON
from sqlalchemy.sql import func
from models.database import Base

class Destination(Base):
    """Destination/Attraction model"""
    __tablename__ = "destinations"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False, index=True)
    description = Column(Text)
    category = Column(String(100), index=True)  # Cultural, Historical, Nature, Beach, etc.
    
    # Location information
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    address = Column(Text)
    district = Column(String(100), index=True)
    province = Column(String(100), index=True)
    
    # Visit information
    visit_time_minutes = Column(Integer, default=120)  # Average visit time
    best_time_to_visit = Column(String(255))  # Time of day/season
    accessibility_level = Column(String(50))  # Easy, Moderate, Difficult
    
    # Ratings and popularity
    popularity_score = Column(Float, default=0.0)
    user_rating = Column(Float, default=0.0)
    review_count = Column(Integer, default=0)
    
    # Practical information
    entry_fee = Column(Float, default=0.0)
    contact_info = Column(JSON)  # Phone, website, etc.
    facilities = Column(JSON)  # Parking, restrooms, food, etc.
    
    # Metadata
    image_urls = Column(JSON)  # List of image URLs
    tags = Column(JSON)  # Additional tags for filtering
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Status
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)
    
    def __repr__(self):
        return f"<Destination(id={self.id}, name='{self.name}', category='{self.category}')>"
    
    def to_dict(self):
        """Convert to dictionary for API responses"""
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "category": self.category,
            "latitude": self.latitude,
            "longitude": self.longitude,
            "address": self.address,
            "district": self.district,
            "province": self.province,
            "visit_time_minutes": self.visit_time_minutes,
            "best_time_to_visit": self.best_time_to_visit,
            "accessibility_level": self.accessibility_level,
            "popularity_score": self.popularity_score,
            "user_rating": self.user_rating,
            "review_count": self.review_count,
            "entry_fee": self.entry_fee,
            "contact_info": self.contact_info,
            "facilities": self.facilities,
            "image_urls": self.image_urls,
            "tags": self.tags,
            "is_active": self.is_active,
            "is_verified": self.is_verified,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }
