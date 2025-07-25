"""
Newsletter Router for managing email subscriptions
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, EmailStr
from typing import Optional
import logging

from models.database import supabase_manager

logger = logging.getLogger(__name__)

# Create router
router = APIRouter(prefix="/newsletter", tags=["newsletter"])

class SubscriberCreate(BaseModel):
    email: EmailStr
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    interests: Optional[list] = None

class SubscriberResponse(BaseModel):
    message: str
    success: bool

@router.post("/subscribe", response_model=SubscriberResponse)
async def subscribe_to_newsletter(subscriber: SubscriberCreate):
    """
    Subscribe to newsletter
    """
    try:
        # Check if email already exists
        existing = supabase_manager.select_data("subscribers", {"email": subscriber.email})
        
        if existing.data and len(existing.data) > 0:
            return SubscriberResponse(
                message="Email already subscribed to newsletter",
                success=False
            )
        
        # Create new subscriber
        subscriber_data = {
            "email": subscriber.email,
            "first_name": subscriber.first_name,
            "last_name": subscriber.last_name,
            "interests": subscriber.interests or [],
            "is_active": True,
            "subscription_source": "website"
        }
        
        result = supabase_manager.insert_data("subscribers", subscriber_data)
        
        if result:
            return SubscriberResponse(
                message="Successfully subscribed to newsletter",
                success=True
            )
        else:
            raise HTTPException(status_code=500, detail="Failed to subscribe")
            
    except Exception as e:
        logger.error(f"Error subscribing to newsletter: {e}")
        raise HTTPException(status_code=500, detail="Error processing subscription")

@router.post("/unsubscribe")
async def unsubscribe_from_newsletter(email: EmailStr):
    """
    Unsubscribe from newsletter
    """
    try:
        result = supabase_manager.update_data(
            "subscribers",
            {"is_active": False, "unsubscribed_at": "NOW()"},
            {"email": email}
        )
        
        if result:
            return {"message": "Successfully unsubscribed from newsletter", "success": True}
        else:
            raise HTTPException(status_code=404, detail="Email not found")
            
    except Exception as e:
        logger.error(f"Error unsubscribing from newsletter: {e}")
        raise HTTPException(status_code=500, detail="Error processing unsubscription")

@router.get("/health")
async def newsletter_health():
    """Health check for newsletter service"""
    return {"status": "healthy", "service": "newsletter"}
