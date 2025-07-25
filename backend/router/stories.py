"""
Stories Router for managing travel blogs and stories
"""
from fastapi import APIRouter, HTTPException, Query
from typing import Optional
import logging

from models.database import supabase_manager

logger = logging.getLogger(__name__)

# Create router
router = APIRouter(prefix="/stories", tags=["stories"])

@router.get("/")
async def get_stories(
    category: Optional[str] = Query(None, description="Filter by category"),
    status: str = Query("published", description="Filter by status"),
    limit: int = Query(10, description="Number of stories to return"),
    offset: int = Query(0, description="Number of stories to skip")
):
    """
    Get list of stories with optional filtering
    """
    try:
        filters = {"status": status}
        if category:
            filters["category"] = category
        
        result = supabase_manager.select_data("stories", filters)
        
        if result.data:
            # Apply pagination
            data = result.data[offset:offset + limit]
            return {
                "stories": data,
                "total": len(result.data),
                "limit": limit,
                "offset": offset
            }
        else:
            return {"stories": [], "total": 0, "limit": limit, "offset": offset}
            
    except Exception as e:
        logger.error(f"Error fetching stories: {e}")
        raise HTTPException(status_code=500, detail="Error fetching stories")

@router.get("/featured")
async def get_featured_stories():
    """
    Get featured stories
    """
    try:
        result = supabase_manager.select_data("stories", {"is_featured": True, "status": "published"})
        
        if result.data:
            return {"featured_stories": result.data}
        else:
            return {"featured_stories": []}
            
    except Exception as e:
        logger.error(f"Error fetching featured stories: {e}")
        raise HTTPException(status_code=500, detail="Error fetching featured stories")

@router.get("/trending")
async def get_trending_stories():
    """
    Get trending stories
    """
    try:
        result = supabase_manager.select_data("stories", {"is_trending": True, "status": "published"})
        
        if result.data:
            return {"trending_stories": result.data}
        else:
            return {"trending_stories": []}
            
    except Exception as e:
        logger.error(f"Error fetching trending stories: {e}")
        raise HTTPException(status_code=500, detail="Error fetching trending stories")

@router.get("/{slug}")
async def get_story_by_slug(slug: str):
    """
    Get a specific story by slug
    """
    try:
        result = supabase_manager.select_data("stories", {"slug": slug, "status": "published"})
        
        if result.data and len(result.data) > 0:
            return result.data[0]
        else:
            raise HTTPException(status_code=404, detail="Story not found")
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching story {slug}: {e}")
        raise HTTPException(status_code=500, detail="Error fetching story")

@router.get("/health")
async def stories_health():
    """Health check for stories service"""
    return {"status": "healthy", "service": "stories"}
