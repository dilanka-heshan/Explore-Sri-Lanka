"""
Story/Blog ORM Model for Supabase
"""
from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, JSON, ForeignKey
from sqlalchemy.sql import func
from models.database import Base

class Story(Base):
    """Story/Blog model for travel stories and guides"""
    __tablename__ = "stories"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Basic information
    title = Column(String(255), nullable=False, index=True)
    slug = Column(String(255), unique=True, index=True)  # URL-friendly version
    excerpt = Column(Text)  # Short summary
    content = Column(Text, nullable=False)  # Full content
    
    # Author information
    author_id = Column(Integer, ForeignKey("users.id"))  # If you have users table
    author_name = Column(String(255))
    author_email = Column(String(255))
    
    # Content classification
    category = Column(String(100), index=True)  # Travel Guide, Experience, Tips, etc.
    tags = Column(JSON)  # List of tags
    
    # Related destinations
    featured_destinations = Column(JSON)  # List of destination IDs
    
    # SEO and metadata
    meta_title = Column(String(255))
    meta_description = Column(Text)
    featured_image_url = Column(String(500))
    
    # Reading metrics
    read_time_minutes = Column(Integer)  # Estimated reading time
    view_count = Column(Integer, default=0)
    like_count = Column(Integer, default=0)
    
    # Publishing
    status = Column(String(20), default="draft")  # draft, published, archived
    published_at = Column(DateTime(timezone=True))
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Flags
    is_featured = Column(Boolean, default=False)
    is_trending = Column(Boolean, default=False)
    allow_comments = Column(Boolean, default=True)
    
    def __repr__(self):
        return f"<Story(id={self.id}, title='{self.title}', status='{self.status}')>"
    
    def to_dict(self):
        """Convert to dictionary for API responses"""
        return {
            "id": self.id,
            "title": self.title,
            "slug": self.slug,
            "excerpt": self.excerpt,
            "content": self.content,
            "author_id": self.author_id,
            "author_name": self.author_name,
            "author_email": self.author_email,
            "category": self.category,
            "tags": self.tags,
            "featured_destinations": self.featured_destinations,
            "meta_title": self.meta_title,
            "meta_description": self.meta_description,
            "featured_image_url": self.featured_image_url,
            "read_time_minutes": self.read_time_minutes,
            "view_count": self.view_count,
            "like_count": self.like_count,
            "status": self.status,
            "published_at": self.published_at.isoformat() if self.published_at else None,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "is_featured": self.is_featured,
            "is_trending": self.is_trending,
            "allow_comments": self.allow_comments
        }
