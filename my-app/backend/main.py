from fastapi import FastAPI, HTTPException, Depends, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from typing import List, Optional
import os
from datetime import datetime
import uvicorn

# Changed from relative imports to absolute imports
from database import get_supabase_client
from models import *
from services import *

app = FastAPI(
    title="Explore Sri Lanka API",
    description="Backend API for Sri Lanka Tourism Website",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "https://your-domain.com"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Dependency to get Supabase client
def get_db():
    return get_supabase_client()

# Health check endpoint
@app.get("/health")
async def health_check():
    return {"status": "healthy", "timestamp": datetime.now()}

# Destinations endpoints
@app.get("/api/destinations", response_model=List[DestinationResponse])
async def get_destinations(
    region: Optional[str] = Query(None),
    destination_type: Optional[str] = Query(None),
    search: Optional[str] = Query(None),
    limit: int = Query(20, le=100),
    offset: int = Query(0, ge=0),
    db=Depends(get_db)
):
    """Get all destinations with optional filtering"""
    try:
        service = DestinationService(db)
        destinations = await service.get_destinations(
            region=region,
            destination_type=destination_type,
            search=search,
            limit=limit,
            offset=offset
        )
        return destinations
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/destinations/{slug}", response_model=DestinationDetailResponse)
async def get_destination_by_slug(slug: str, db=Depends(get_db)):
    """Get destination details by slug"""
    try:
        service = DestinationService(db)
        destination = await service.get_destination_by_slug(slug)
        if not destination:
            raise HTTPException(status_code=404, detail="Destination not found")
        return destination
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/destinations/{destination_id}/reviews", response_model=List[ReviewResponse])
async def get_destination_reviews(
    destination_id: str,
    limit: int = Query(10, le=50),
    offset: int = Query(0, ge=0),
    db=Depends(get_db)
):
    """Get reviews for a specific destination"""
    try:
        service = ReviewService(db)
        reviews = await service.get_destination_reviews(destination_id, limit, offset)
        return reviews
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/destinations/{destination_id}/reviews", response_model=ReviewResponse)
async def create_review(
    destination_id: str,
    review: ReviewCreate,
    db=Depends(get_db)
):
    """Create a new review for a destination"""
    try:
        service = ReviewService(db)
        new_review = await service.create_review(destination_id, review)
        return new_review
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Experiences endpoints
@app.get("/api/experiences", response_model=List[ExperienceResponse])
async def get_experiences(
    category: Optional[str] = Query(None),
    destination_id: Optional[str] = Query(None),
    limit: int = Query(20, le=100),
    offset: int = Query(0, ge=0),
    db=Depends(get_db)
):
    """Get all experiences with optional filtering"""
    try:
        service = ExperienceService(db)
        experiences = await service.get_experiences(
            category=category,
            destination_id=destination_id,
            limit=limit,
            offset=offset
        )
        return experiences
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/experiences/{slug}", response_model=ExperienceDetailResponse)
async def get_experience_by_slug(slug: str, db=Depends(get_db)):
    """Get experience details by slug"""
    try:
        service = ExperienceService(db)
        experience = await service.get_experience_by_slug(slug)
        if not experience:
            raise HTTPException(status_code=404, detail="Experience not found")
        return experience
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Itineraries endpoints
@app.get("/api/itineraries", response_model=List[ItineraryResponse])
async def get_itineraries(
    trip_type: Optional[str] = Query(None),
    duration_min: Optional[int] = Query(None),
    duration_max: Optional[int] = Query(None),
    price_min: Optional[float] = Query(None),
    price_max: Optional[float] = Query(None),
    limit: int = Query(20, le=100),
    offset: int = Query(0, ge=0),
    db=Depends(get_db)
):
    """Get all itineraries with optional filtering"""
    try:
        service = ItineraryService(db)
        itineraries = await service.get_itineraries(
            trip_type=trip_type,
            duration_min=duration_min,
            duration_max=duration_max,
            price_min=price_min,
            price_max=price_max,
            limit=limit,
            offset=offset
        )
        return itineraries
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/itineraries/{slug}", response_model=ItineraryDetailResponse)
async def get_itinerary_by_slug(slug: str, db=Depends(get_db)):
    """Get itinerary details by slug"""
    try:
        service = ItineraryService(db)
        itinerary = await service.get_itinerary_by_slug(slug)
        if not itinerary:
            raise HTTPException(status_code=404, detail="Itinerary not found")
        return itinerary
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Blog endpoints
@app.get("/api/blog", response_model=List[BlogPostResponse])
async def get_blog_posts(
    category: Optional[str] = Query(None),
    tag: Optional[str] = Query(None),
    search: Optional[str] = Query(None),
    published_only: bool = Query(True),
    limit: int = Query(20, le=100),
    offset: int = Query(0, ge=0),
    db=Depends(get_db)
):
    """Get all blog posts with optional filtering"""
    try:
        service = BlogService(db)
        posts = await service.get_blog_posts(
            category=category,
            tag=tag,
            search=search,
            published_only=published_only,
            limit=limit,
            offset=offset
        )
        return posts
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/blog/{slug}", response_model=BlogPostDetailResponse)
async def get_blog_post_by_slug(slug: str, db=Depends(get_db)):
    """Get blog post details by slug"""
    try:
        service = BlogService(db)
        post = await service.get_blog_post_by_slug(slug)
        if not post:
            raise HTTPException(status_code=404, detail="Blog post not found")
        return post
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Booking endpoints
@app.post("/api/bookings", response_model=BookingResponse)
async def create_booking(booking: BookingCreate, db=Depends(get_db)):
    """Create a new booking"""
    try:
        service = BookingService(db)
        new_booking = await service.create_booking(booking)
        return new_booking
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/bookings/{booking_id}", response_model=BookingResponse)
async def get_booking(booking_id: str, db=Depends(get_db)):
    """Get booking details by ID"""
    try:
        service = BookingService(db)
        booking = await service.get_booking(booking_id)
        if not booking:
            raise HTTPException(status_code=404, detail="Booking not found")
        return booking
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Newsletter endpoints
@app.post("/api/newsletter/subscribe")
async def subscribe_newsletter(subscription: NewsletterSubscription, db=Depends(get_db)):
    """Subscribe to newsletter"""
    try:
        service = NewsletterService(db)
        result = await service.subscribe(subscription.email)
        return {"message": "Successfully subscribed to newsletter", "success": True}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Contact endpoints
@app.post("/api/contact")
async def submit_contact_message(message: ContactMessage, db=Depends(get_db)):
    """Submit a contact message"""
    try:
        service = ContactService(db)
        result = await service.create_message(message)
        return {"message": "Message sent successfully", "success": True}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Media gallery endpoints
@app.get("/api/media", response_model=List[MediaResponse])
async def get_media_gallery(
    category: Optional[str] = Query(None),
    destination_id: Optional[str] = Query(None),
    featured_only: bool = Query(False),
    limit: int = Query(20, le=100),
    offset: int = Query(0, ge=0),
    db=Depends(get_db)
):
    """Get media gallery items"""
    try:
        service = MediaService(db)
        media_items = await service.get_media_items(
            category=category,
            destination_id=destination_id,
            featured_only=featured_only,
            limit=limit,
            offset=offset
        )
        return media_items
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Search endpoint
@app.get("/api/search")
async def search_content(
    q: str = Query(..., min_length=2),
    type: Optional[str] = Query(None),  # destinations, experiences, blog
    limit: int = Query(10, le=50),
    db=Depends(get_db)
):
    """Global search across destinations, experiences, and blog posts"""
    try:
        service = SearchService(db)
        results = await service.search_content(q, type, limit)
        return results
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)