"""
Destinations Router for managing Sri Lanka attractions and destinations
"""
from fastapi import APIRouter, HTTPException, Depends, Query
from sqlalchemy.orm import Session
from typing import List, Optional
import logging

from models.database import get_db, supabase_manager
from models.orm.destination import Destination

logger = logging.getLogger(__name__)

# Create router
router = APIRouter(prefix="/destinations", tags=["destinations"])

@router.get("/")
async def get_destinations(
    category: Optional[str] = Query(None, description="Filter by category"),
    district: Optional[str] = Query(None, description="Filter by district"),
    province: Optional[str] = Query(None, description="Filter by province"),
    limit: int = Query(50, description="Number of destinations to return"),
    offset: int = Query(0, description="Number of destinations to skip")
):
    """
    Get list of destinations with optional filtering
    """
    try:
        filters = {}
        if category:
            filters["category"] = category
        if district:
            filters["district"] = district
        if province:
            filters["province"] = province
        
        # Use Supabase to get destinations
        result = supabase_manager.select_data("destinations", filters)
        
        if result.data:
            # Apply pagination
            data = result.data[offset:offset + limit]
            return {
                "destinations": data,
                "total": len(result.data),
                "limit": limit,
                "offset": offset
            }
        else:
            return {"destinations": [], "total": 0, "limit": limit, "offset": offset}
            
    except Exception as e:
        logger.error(f"Error fetching destinations: {e}")
        raise HTTPException(status_code=500, detail="Error fetching destinations")

@router.get("/{destination_id}")
async def get_destination(destination_id: int):
    """
    Get a specific destination by ID
    """
    try:
        result = supabase_manager.select_data("destinations", {"id": destination_id})
        
        if result.data and len(result.data) > 0:
            return result.data[0]
        else:
            raise HTTPException(status_code=404, detail="Destination not found")
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching destination {destination_id}: {e}")
        raise HTTPException(status_code=500, detail="Error fetching destination")

@router.get("/search/{query}")
async def search_destinations(query: str):
    """
    Search destinations by name or description
    """
    try:
        # This is a basic implementation
        # In a real app, you'd want to use full-text search
        result = supabase_manager.select_data("destinations", {})
        
        if result.data:
            # Simple text search
            filtered_destinations = [
                dest for dest in result.data
                if query.lower() in dest.get("name", "").lower() or
                   query.lower() in dest.get("description", "").lower()
            ]
            return {"destinations": filtered_destinations, "query": query}
        else:
            return {"destinations": [], "query": query}
            
    except Exception as e:
        logger.error(f"Error searching destinations: {e}")
        raise HTTPException(status_code=500, detail="Error searching destinations")

@router.get("/categories/list")
async def get_categories():
    """
    Get list of all destination categories
    """
    try:
        result = supabase_manager.select_data("destinations", {}, "category")
        
        if result.data:
            categories = list(set([dest.get("category") for dest in result.data if dest.get("category")]))
            return {"categories": categories}
        else:
            return {"categories": []}
            
    except Exception as e:
        logger.error(f"Error fetching categories: {e}")
        raise HTTPException(status_code=500, detail="Error fetching categories")

@router.get("/health")
async def destinations_health():
    """Health check for destinations service"""
    return {"status": "healthy", "service": "destinations"}
