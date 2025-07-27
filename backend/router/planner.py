"""
Enhanced Travel Planner API Router
Provides endpoints for sophisticated travel planning with multiple reasoning stages
"""

from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel, Field
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
import logging
import asyncio

# Import the enhanced planner
from langgraph_flow.planner_graph import compiled_graph, plan_trip_async, plan_trip_sync, validate_planning_input, format_itinerary_for_api

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/planning", tags=["Travel Planning"])

# Request/Response Models
class TravelPlanRequest(BaseModel):
    """Request model for travel planning"""
    message: str = Field(..., description="Natural language description of travel preferences", min_length=10, max_length=1000)
    user_preferences: Optional[Dict[str, Any]] = Field(default=None, description="Structured user preferences")
    duration_days: Optional[int] = Field(default=None, ge=1, le=30, description="Trip duration in days")
    budget_level: Optional[str] = Field(default=None, description="Budget level: budget, mid_range, luxury")
    trip_type: Optional[str] = Field(default=None, description="Trip type: solo, couple, family, group")
    start_date: Optional[str] = Field(default=None, description="Preferred start date (YYYY-MM-DD)")
    
    class Config:
        schema_extra = {
            "example": {
                "message": "I want to explore Sri Lanka for 7 days with my partner. We love nature, hiking, and cultural sites. We have a moderate budget and prefer adventure activities.",
                "duration_days": 7,
                "budget_level": "mid_range",
                "trip_type": "couple"
            }
        }

class TravelPlanResponse(BaseModel):
    """Response model for travel planning"""
    success: bool
    plan_id: Optional[str] = None
    summary: Optional[Dict[str, Any]] = None
    daily_schedules: Optional[List[Dict[str, Any]]] = None
    recommendations: Optional[Dict[str, Any]] = None
    travel_tips: Optional[Dict[str, Any]] = None
    emergency_contacts: Optional[List[str]] = None
    explanation: Optional[str] = None
    error: Optional[str] = None

class PlanningStatusResponse(BaseModel):
    """Response model for planning status"""
    steps_completed: int
    current_step: str
    user_profile: Dict[str, Any]
    attractions_found: int
    clusters_created: int
    days_planned: int

# In-memory storage for planning sessions (in production, use Redis or database)
planning_sessions: Dict[str, Dict[str, Any]] = {}

@router.post("/plan_trip", response_model=TravelPlanResponse)
async def plan_trip(request: TravelPlanRequest, background_tasks: BackgroundTasks):
    """
    Generate a comprehensive travel plan using advanced AI planning
    
    This endpoint implements a sophisticated 7-step planning process:
    1. PEAR ranking for personalized attraction scoring
    2. Geographic clustering of attractions  
    3. Cluster value-per-time optimization
    4. Time window filtering
    5. Route optimization with travel time calculation
    6. Gap filling with vector similarity search
    7. LLM reasoning for final enhancements
    """
    
    try:
        # Validate input
        validation = validate_planning_input(request.message)
        if not validation.get("valid"):
            raise HTTPException(status_code=400, detail=validation.get("error"))
        
        # Enhance message with structured preferences
        enhanced_message = enhance_message_with_preferences(request)
        
        logger.info(f"Starting travel planning for request: {request.message[:100]}...")
        
        # Plan trip using the enhanced async planner
        final_plan = await plan_trip_async(enhanced_message)
        
        # Format response
        if final_plan.get("error"):
            return TravelPlanResponse(
                success=False,
                error=final_plan.get("error"),
                explanation=final_plan.get("message", "Planning failed")
            )
        
        # Format successful response
        formatted_plan = format_itinerary_for_api(final_plan)
        
        # Store session for potential follow-up requests
        session_id = formatted_plan.get("plan_id", f"session_{datetime.now().strftime('%Y%m%d_%H%M%S')}")
        planning_sessions[session_id] = {
            "original_request": request.dict(),
            "final_plan": final_plan,
            "created_at": datetime.now()
        }
        
        logger.info(f"Successfully generated travel plan with ID: {session_id}")
        
        return TravelPlanResponse(**formatted_plan)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error in plan_trip: {e}")
        raise HTTPException(status_code=500, detail="Internal server error during planning")

@router.post("/plan_trip_sync", response_model=TravelPlanResponse)
def plan_trip_synchronous(request: TravelPlanRequest):
    """
    Synchronous version of travel planning (for backward compatibility)
    """
    
    try:
        # Validate input
        validation = validate_planning_input(request.message)
        if not validation.get("valid"):
            raise HTTPException(status_code=400, detail=validation.get("error"))
        
        # Enhance message with structured preferences
        enhanced_message = enhance_message_with_preferences(request)
        
        logger.info(f"Starting synchronous travel planning: {request.message[:100]}...")
        
        # Plan trip using synchronous planner
        final_plan = plan_trip_sync(enhanced_message)
        
        # Format response
        if final_plan.get("error"):
            return TravelPlanResponse(
                success=False,
                error=final_plan.get("error"),
                explanation=final_plan.get("message", "Planning failed")
            )
        
        # Format successful response
        formatted_plan = format_itinerary_for_api(final_plan)
        
        return TravelPlanResponse(**formatted_plan)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error in synchronous planning: {e}")
        raise HTTPException(status_code=500, detail="Internal server error during planning")

@router.get("/plan/{plan_id}", response_model=TravelPlanResponse)
def get_plan(plan_id: str):
    """
    Retrieve a previously generated travel plan
    """
    
    if plan_id not in planning_sessions:
        raise HTTPException(status_code=404, detail="Travel plan not found")
    
    session = planning_sessions[plan_id]
    final_plan = session["final_plan"]
    formatted_plan = format_itinerary_for_api(final_plan)
    
    return TravelPlanResponse(**formatted_plan)

@router.post("/refine_plan/{plan_id}")
async def refine_plan(plan_id: str, refinement_request: Dict[str, Any]):
    """
    Refine an existing travel plan based on user feedback
    """
    
    if plan_id not in planning_sessions:
        raise HTTPException(status_code=404, detail="Travel plan not found")
    
    try:
        # Get original session
        session = planning_sessions[plan_id]
        original_request = session["original_request"]
        
        # Create refined request
        refined_message = f"{original_request['message']} Additionally: {refinement_request.get('additional_requirements', '')}"
        
        # Re-plan with refined requirements
        final_plan = await plan_trip_async(refined_message)
        
        # Update session
        session["final_plan"] = final_plan
        session["refined_at"] = datetime.now()
        session["refinement_history"] = session.get("refinement_history", []) + [refinement_request]
        
        # Format response
        formatted_plan = format_itinerary_for_api(final_plan)
        return TravelPlanResponse(**formatted_plan)
        
    except Exception as e:
        logger.error(f"Error refining plan {plan_id}: {e}")
        raise HTTPException(status_code=500, detail="Error refining travel plan")

@router.get("/status/{plan_id}", response_model=PlanningStatusResponse)
def get_planning_status(plan_id: str):
    """
    Get the status of an ongoing planning session
    (For future use with real-time planning updates)
    """
    
    if plan_id not in planning_sessions:
        raise HTTPException(status_code=404, detail="Planning session not found")
    
    # For now, return completed status
    # In a real implementation, this would track ongoing planning progress
    return PlanningStatusResponse(
        steps_completed=7,
        current_step="Planning completed",
        user_profile={},
        attractions_found=0,
        clusters_created=0,
        days_planned=0
    )

@router.get("/recommendations/similar/{plan_id}")
async def get_similar_recommendations(plan_id: str, limit: int = 5):
    """
    Get similar attraction recommendations based on the planned itinerary
    """
    
    if plan_id not in planning_sessions:
        raise HTTPException(status_code=404, detail="Travel plan not found")
    
    try:
        session = planning_sessions[plan_id]
        final_plan = session["final_plan"]
        
        # Extract planned attractions
        planned_attractions = []
        for schedule in final_plan.get("daily_schedules", []):
            for item in schedule.get("items", []):
                planned_attractions.append(item.get("attraction_name", ""))
        
        # This would typically use the vector DB to find similar attractions
        # For now, return mock similar recommendations
        similar_recommendations = [
            {
                "name": "Alternative Cultural Site",
                "reason": "Similar to your cultural interests",
                "category": "cultural"
            },
            {
                "name": "Nearby Nature Spot", 
                "reason": "Complements your nature activities",
                "category": "nature"
            }
        ]
        
        return {
            "plan_id": plan_id,
            "similar_attractions": similar_recommendations[:limit],
            "based_on": planned_attractions
        }
        
    except Exception as e:
        logger.error(f"Error getting similar recommendations: {e}")
        raise HTTPException(status_code=500, detail="Error finding similar recommendations")

@router.delete("/plan/{plan_id}")
def delete_plan(plan_id: str):
    """
    Delete a travel plan from storage
    """
    
    if plan_id not in planning_sessions:
        raise HTTPException(status_code=404, detail="Travel plan not found")
    
    del planning_sessions[plan_id]
    
    return {"message": f"Travel plan {plan_id} deleted successfully"}

@router.get("/health")
def health_check():
    """
    Health check endpoint for the planning service
    """
    
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "active_sessions": len(planning_sessions),
        "service": "Enhanced Travel Planner",
        "features": [
            "PEAR ranking",
            "Geographic clustering", 
            "Route optimization",
            "Vector similarity search",
            "LLM reasoning"
        ]
    }

# Helper functions

def enhance_message_with_preferences(request: TravelPlanRequest) -> str:
    """Enhance the natural language message with structured preferences"""
    
    enhanced_parts = [request.message]
    
    if request.duration_days:
        enhanced_parts.append(f"Duration: {request.duration_days} days")
    
    if request.budget_level:
        enhanced_parts.append(f"Budget: {request.budget_level}")
    
    if request.trip_type:
        enhanced_parts.append(f"Trip type: {request.trip_type}")
    
    if request.start_date:
        enhanced_parts.append(f"Start date: {request.start_date}")
    
    if request.user_preferences:
        prefs = request.user_preferences
        if prefs.get("interests"):
            enhanced_parts.append(f"Specific interests: {', '.join(prefs['interests'])}")
        if prefs.get("excluded_activities"):
            enhanced_parts.append(f"Avoid: {', '.join(prefs['excluded_activities'])}")
    
    return " | ".join(enhanced_parts)

# Background task for cleanup
async def cleanup_old_sessions():
    """Clean up old planning sessions (run periodically)"""
    
    cutoff_time = datetime.now() - timedelta(hours=24)  # Keep sessions for 24 hours
    
    sessions_to_delete = [
        session_id for session_id, session in planning_sessions.items()
        if session.get("created_at", datetime.now()) < cutoff_time
    ]
    
    for session_id in sessions_to_delete:
        del planning_sessions[session_id]
    
    logger.info(f"Cleaned up {len(sessions_to_delete)} old planning sessions")
