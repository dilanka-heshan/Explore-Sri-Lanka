"""
Subscriber/Newsletter ORM Model for Supabase
"""
from sqlalchemy import Column, Integer, String, DateTime, Boolean, JSON
from sqlalchemy.sql import func
from models.database import Base

class Subscriber(Base):
    """Newsletter subscriber model"""
    __tablename__ = "subscribers"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Contact information
    email = Column(String(255), unique=True, nullable=False, index=True)
    first_name = Column(String(100))
    last_name = Column(String(100))
    
    # Subscription preferences
    subscription_type = Column(String(50), default="newsletter")  # newsletter, updates, promotions
    frequency = Column(String(20), default="weekly")  # daily, weekly, monthly
    interests = Column(JSON)  # List of interests/categories
    
    # Status
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)
    verification_token = Column(String(255))
    
    # Tracking
    subscription_source = Column(String(100))  # website, social, referral
    utm_source = Column(String(100))
    utm_medium = Column(String(100))
    utm_campaign = Column(String(100))
    
    # Timestamps
    subscribed_at = Column(DateTime(timezone=True), server_default=func.now())
    verified_at = Column(DateTime(timezone=True))
    unsubscribed_at = Column(DateTime(timezone=True))
    last_email_sent = Column(DateTime(timezone=True))
    
    # Metadata
    user_agent = Column(String(500))
    ip_address = Column(String(45))  # IPv4/IPv6
    
    def __repr__(self):
        return f"<Subscriber(id={self.id}, email='{self.email}', is_active={self.is_active})>"
    
    def to_dict(self):
        """Convert to dictionary for API responses"""
        return {
            "id": self.id,
            "email": self.email,
            "first_name": self.first_name,
            "last_name": self.last_name,
            "subscription_type": self.subscription_type,
            "frequency": self.frequency,
            "interests": self.interests,
            "is_active": self.is_active,
            "is_verified": self.is_verified,
            "subscription_source": self.subscription_source,
            "utm_source": self.utm_source,
            "utm_medium": self.utm_medium,
            "utm_campaign": self.utm_campaign,
            "subscribed_at": self.subscribed_at.isoformat() if self.subscribed_at else None,
            "verified_at": self.verified_at.isoformat() if self.verified_at else None,
            "unsubscribed_at": self.unsubscribed_at.isoformat() if self.unsubscribed_at else None,
            "last_email_sent": self.last_email_sent.isoformat() if self.last_email_sent else None
        }
