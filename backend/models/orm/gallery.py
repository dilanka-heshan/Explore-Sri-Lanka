"""
Gallery ORM Model for Supabase
"""
from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from models.database import Base

class Gallery(Base):
    """Gallery/Image model for destinations"""
    __tablename__ = "gallery"
    
    id = Column(Integer, primary_key=True, index=True)
    destination_id = Column(Integer, ForeignKey("destinations.id"), nullable=False, index=True)
    
    # Image information
    image_url = Column(String(500), nullable=False)
    thumbnail_url = Column(String(500))
    alt_text = Column(String(255))
    caption = Column(Text)
    
    # Image metadata
    file_name = Column(String(255))
    file_size = Column(Integer)  # in bytes
    width = Column(Integer)
    height = Column(Integer)
    format = Column(String(10))  # jpg, png, webp, etc.
    
    # Classification
    image_type = Column(String(50))  # main, interior, exterior, aerial, food, activity
    is_featured = Column(Boolean, default=False)
    display_order = Column(Integer, default=0)
    
    # Attribution
    photographer = Column(String(255))
    license_type = Column(String(100))  # Creative Commons, Commercial, etc.
    source = Column(String(255))  # Where the image came from
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Status
    is_active = Column(Boolean, default=True)
    is_approved = Column(Boolean, default=False)
    
    def __repr__(self):
        return f"<Gallery(id={self.id}, destination_id={self.destination_id}, image_type='{self.image_type}')>"
    
    def to_dict(self):
        """Convert to dictionary for API responses"""
        return {
            "id": self.id,
            "destination_id": self.destination_id,
            "image_url": self.image_url,
            "thumbnail_url": self.thumbnail_url,
            "alt_text": self.alt_text,
            "caption": self.caption,
            "file_name": self.file_name,
            "file_size": self.file_size,
            "width": self.width,
            "height": self.height,
            "format": self.format,
            "image_type": self.image_type,
            "is_featured": self.is_featured,
            "display_order": self.display_order,
            "photographer": self.photographer,
            "license_type": self.license_type,
            "source": self.source,
            "is_active": self.is_active,
            "is_approved": self.is_approved,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }
