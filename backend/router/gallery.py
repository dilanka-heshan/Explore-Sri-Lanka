"""
Gallery Router for managing destination images and media
"""
from fastapi import APIRouter, HTTPException, Query
from typing import Optional
import logging

from models.database import supabase_manager

logger = logging.getLogger(__name__)

# Create router
router = APIRouter(prefix="/gallery", tags=["gallery"])

@router.get("/")
async def get_gallery_images(
    destination_id: Optional[int] = Query(None, description="Filter by destination ID"),
    image_type: Optional[str] = Query(None, description="Filter by image type"),
    limit: int = Query(20, description="Number of images to return"),
    offset: int = Query(0, description="Number of images to skip")
):
    """
    Get gallery images with optional filtering
    """
    try:
        filters = {}
        if destination_id:
            filters["destination_id"] = destination_id
        if image_type:
            filters["image_type"] = image_type
        
        result = supabase_manager.select_data("gallery", filters)
        
        if result.data:
            # Apply pagination
            data = result.data[offset:offset + limit]
            return {
                "images": data,
                "total": len(result.data),
                "limit": limit,
                "offset": offset
            }
        else:
            return {"images": [], "total": 0, "limit": limit, "offset": offset}
            
    except Exception as e:
        logger.error(f"Error fetching gallery images: {e}")
        raise HTTPException(status_code=500, detail="Error fetching gallery images")

@router.get("/destination/{destination_id}")
async def get_destination_gallery(destination_id: int):
    """
    Get all gallery images for a specific destination
    """
    try:
        result = supabase_manager.select_data("gallery", {"destination_id": destination_id})
        
        if result.data:
            return {"destination_id": destination_id, "images": result.data}
        else:
            return {"destination_id": destination_id, "images": []}
            
    except Exception as e:
        logger.error(f"Error fetching gallery for destination {destination_id}: {e}")
        raise HTTPException(status_code=500, detail="Error fetching destination gallery")

@router.get("/featured")
async def get_featured_images():
    """
    Get featured gallery images
    """
    try:
        result = supabase_manager.select_data("gallery", {"is_featured": True})
        
        if result.data:
            return {"featured_images": result.data}
        else:
            return {"featured_images": []}
            
    except Exception as e:
        logger.error(f"Error fetching featured images: {e}")
        raise HTTPException(status_code=500, detail="Error fetching featured images")

@router.get("/health")
async def gallery_health():
    """Health check for gallery service"""
    return {"status": "healthy", "service": "gallery"}
