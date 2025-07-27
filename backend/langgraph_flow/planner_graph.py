"""
Enhanced Travel Planning Graph using LangGraph
Implements a sophisticated 7-step travel planning workflow
"""

from langgraph.graph import StateGraph, END
from typing import Dict, Any, TypedDict
import logging

# Import enhanced nodes
from .nodes.parser import parse_user_input
from .nodes.retriever import retrieve_places  
from .nodes.planner import generate_itinerary

logger = logging.getLogger(__name__)

class PlanningState(TypedDict):
    """Enhanced state for travel planning workflow"""
    
    # Input
    user_input: str
    
    # Parsed information
    user_profile: Dict[str, Any]
    duration_days: int
    start_date: str
    parsed_interests: list
    excluded_attractions: list
    preferred_regions: list
    special_requirements: str
    
    # Retrieved data
    candidate_attractions: list
    pear_ranked_attractions: list
    
    # Planning results
    geo_clusters: list
    selected_clusters: list
    optimized_routes: Dict[int, Any]
    daily_schedules: list
    final_plan: Dict[str, Any]
    
    # Output
    itinerary: Dict[str, Any]
    
    # Workflow tracking
    reasoning_log: list

def should_continue_to_retriever(state: PlanningState) -> str:
    """Conditional logic to determine if we should proceed to retrieval"""
    
    user_profile = state.get("user_profile")
    if not user_profile or not user_profile.get("interests"):
        logger.warning("No valid user profile found, using defaults")
    
    return "retrieve"

def should_continue_to_planner(state: PlanningState) -> str:
    """Conditional logic to determine if we should proceed to planning"""
    
    attractions = state.get("pear_ranked_attractions", [])
    if len(attractions) < 3:
        logger.warning(f"Only {len(attractions)} attractions found, may result in limited itinerary")
    
    return "plan"

def create_planning_graph() -> StateGraph:
    """Create the enhanced travel planning graph"""
    
    # Initialize graph with enhanced state
    graph = StateGraph(PlanningState)
    
    # Add nodes
    graph.add_node("parse", parse_user_input)
    graph.add_node("retrieve", retrieve_places)
    graph.add_node("plan", generate_itinerary)
    
    # Set entry point
    graph.set_entry_point("parse")
    
    # Add edges with conditional logic
    graph.add_conditional_edges(
        "parse",
        should_continue_to_retriever,
        {"retrieve": "retrieve"}
    )
    
    graph.add_conditional_edges(
        "retrieve", 
        should_continue_to_planner,
        {"plan": "plan"}
    )
    
    # End after planning
    graph.add_edge("plan", END)
    
    return graph

# Create and compile the graph
graph = create_planning_graph()
compiled_graph = graph.compile()

async def plan_trip_async(user_input: str) -> Dict[str, Any]:
    """
    Asynchronous trip planning function
    
    Args:
        user_input: Natural language description of travel preferences
        
    Returns:
        Complete travel plan with itinerary and recommendations
    """
    
    try:
        # Initialize state
        initial_state = {
            "user_input": user_input,
            "reasoning_log": []
        }
        
        # Run the planning workflow
        result = await compiled_graph.ainvoke(initial_state)
        
        # Extract final plan
        final_plan = result.get("final_plan", result.get("itinerary", {}))
        
        logger.info("Trip planning completed successfully")
        return final_plan
        
    except Exception as e:
        logger.error(f"Trip planning failed: {e}")
        
        # Return fallback plan
        return {
            "error": str(e),
            "message": "Trip planning encountered an error. Please try again with different preferences.",
            "fallback_suggestions": [
                "Visit Sigiriya Rock Fortress",
                "Explore Kandy and Temple of the Tooth",
                "Relax at Mirissa Beach"
            ]
        }

def plan_trip_sync(user_input: str) -> Dict[str, Any]:
    """
    Synchronous trip planning function for backward compatibility
    
    Args:
        user_input: Natural language description of travel preferences
        
    Returns:
        Complete travel plan with itinerary and recommendations
    """
    
    try:
        # Initialize state
        initial_state = {
            "user_input": user_input,
            "reasoning_log": []
        }
        
        # Run the planning workflow synchronously
        result = compiled_graph.invoke(initial_state)
        
        # Extract final plan
        final_plan = result.get("final_plan", result.get("itinerary", {}))
        
        logger.info("Trip planning completed successfully")
        return final_plan
        
    except Exception as e:
        logger.error(f"Trip planning failed: {e}")
        
        # Return fallback plan
        return {
            "error": str(e),
            "message": "Trip planning encountered an error. Please try again with different preferences.",
            "fallback_suggestions": [
                "Visit Sigiriya Rock Fortress",
                "Explore Kandy and Temple of the Tooth", 
                "Relax at Mirissa Beach"
            ]
        }

# Helper functions for external API integration

def get_planning_status(state: PlanningState) -> Dict[str, Any]:
    """Get current status of planning workflow"""
    
    reasoning_log = state.get("reasoning_log", [])
    
    status = {
        "steps_completed": len(reasoning_log),
        "current_step": reasoning_log[-1] if reasoning_log else "Starting planning",
        "user_profile": state.get("user_profile", {}),
        "attractions_found": len(state.get("pear_ranked_attractions", [])),
        "clusters_created": len(state.get("geo_clusters", [])),
        "days_planned": len(state.get("daily_schedules", []))
    }
    
    return status

def validate_planning_input(user_input: str) -> Dict[str, Any]:
    """Validate user input before planning"""
    
    if not user_input or len(user_input.strip()) < 10:
        return {
            "valid": False,
            "error": "Please provide more details about your travel preferences"
        }
    
    if len(user_input) > 1000:
        return {
            "valid": False,
            "error": "Please keep your request under 1000 characters"
        }
    
    return {"valid": True}

def format_itinerary_for_api(final_plan: Dict[str, Any]) -> Dict[str, Any]:
    """Format the final plan for API response"""
    
    if not final_plan:
        return {"error": "No itinerary generated"}
    
    # Format for consistent API response
    formatted = {
        "success": True,
        "plan_id": final_plan.get("plan_id", ""),
        "summary": {
            "total_days": final_plan.get("total_days", 0),
            "total_attractions": final_plan.get("total_attractions", 0),
            "estimated_cost": final_plan.get("total_estimated_cost", 0)
        },
        "daily_schedules": final_plan.get("daily_schedules", []),
        "recommendations": {
            "hotels": final_plan.get("recommended_hotels", []),
            "restaurants": final_plan.get("recommended_restaurants", [])
        },
        "travel_tips": {
            "weather": final_plan.get("weather_considerations", ""),
            "packing": final_plan.get("packing_suggestions", []),
            "local_tips": final_plan.get("local_tips", [])
        },
        "emergency_contacts": final_plan.get("emergency_contacts", []),
        "explanation": final_plan.get("explanation", "")
    }
    
    return formatted
