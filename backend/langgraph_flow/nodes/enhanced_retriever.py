"""
Enhanced Retriever using Simplified PEAR Ranker
Integrates with Qdrant vector database for travel place recommendations
"""

from typing import Dict, Any, List
import logging
from ..models.simplified_pear_ranker import SimplifiedPEARRanker, create_travel_ranker

logger = logging.getLogger(__name__)

def retrieve_places(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Enhanced place retrieval using vector database and neural ranking
    
    This function implements your vision:
    1. User query → Embedding
    2. Vector DB similarity search
    3. Neural ranking
    4. Return top 30 places
    """
    
    try:
        # Get user input and profile from state
        user_input = state.get("user_input", "")
        user_profile = state.get("user_profile", {})
        
        if not user_input:
            logger.warning("No user input provided for place retrieval")
            return {**state, "pear_ranked_attractions": []}
        
        # Initialize the simplified PEAR ranker
        try:
            ranker = create_travel_ranker(
                qdrant_url="http://localhost:6333",  # Update with your Qdrant URL
                collection_name="travel_places",     # Update with your collection name
                model_path=None  # Add path if you have a trained model
            )
        except Exception as e:
            logger.error(f"Failed to initialize PEAR ranker: {e}")
            return {**state, "pear_ranked_attractions": []}
        
        # Prepare user context from profile
        user_context = {
            "trip_type": user_profile.get("trip_type", "solo"),
            "budget": user_profile.get("budget_level", "moderate"),
            "interests": user_profile.get("interests", []),
            "duration": user_profile.get("duration_days", 7),
            "group_size": user_profile.get("group_size", 1)
        }
        
        # Get recommendations using the simplified approach
        recommendations = ranker.get_recommendations(
            user_query=user_input,
            user_context=user_context,
            top_k=30,  # Get top 30 as requested
            vector_search_limit=100  # Search through more candidates first
        )
        
        if not recommendations:
            logger.warning("No recommendations found")
            return {**state, "pear_ranked_attractions": []}
        
        # Convert to the format expected by the rest of the pipeline
        pear_ranked_attractions = []
        for rec in recommendations:
            place_data = {
                "id": rec["id"],
                "pear_score": rec["neural_score"],
                "similarity_score": rec["similarity_score"],
                "combined_score": rec["combined_score"],
                **rec["payload"]  # Include all the place metadata from Qdrant
            }
            pear_ranked_attractions.append(place_data)
        
        logger.info(f"Successfully retrieved and ranked {len(pear_ranked_attractions)} places")
        
        # Add reasoning log
        reasoning_entry = {
            "step": "PEAR_RANKING",
            "description": f"Retrieved {len(pear_ranked_attractions)} places using transformer-based similarity search and neural ranking",
            "details": {
                "user_query": user_input,
                "user_context": user_context,
                "top_score": pear_ranked_attractions[0]["combined_score"] if pear_ranked_attractions else 0,
                "ranking_method": "neural_network"
            }
        }
        
        return {
            **state,
            "pear_ranked_attractions": pear_ranked_attractions,
            "candidate_attractions": pear_ranked_attractions,  # For backward compatibility
            "reasoning_log": state.get("reasoning_log", []) + [reasoning_entry]
        }
        
    except Exception as e:
        logger.error(f"Error in retrieve_places: {e}")
        return {
            **state,
            "pear_ranked_attractions": [],
            "reasoning_log": state.get("reasoning_log", []) + [{
                "step": "PEAR_RANKING_ERROR",
                "description": f"Failed to retrieve places: {str(e)}",
                "details": {"error": str(e)}
            }]
        }

def retrieve_places_by_category(state: Dict[str, Any], category: str) -> Dict[str, Any]:
    """
    Retrieve places filtered by specific category
    """
    try:
        user_input = state.get("user_input", "")
        user_profile = state.get("user_profile", {})
        
        ranker = create_travel_ranker()
        
        user_context = {
            "trip_type": user_profile.get("trip_type", "solo"),
            "budget": user_profile.get("budget_level", "moderate"),
            "interests": user_profile.get("interests", []),
            "duration": user_profile.get("duration_days", 7)
        }
        
        recommendations = ranker.search_by_category(
            user_query=user_input,
            user_context=user_context,
            category_filter=category,
            top_k=20
        )
        
        # Convert to expected format
        category_attractions = []
        for rec in recommendations:
            place_data = {
                "id": rec["id"],
                "pear_score": rec["neural_score"],
                "similarity_score": rec["similarity_score"],
                "category": category,
                **rec["payload"]
            }
            category_attractions.append(place_data)
        
        return {
            **state,
            f"{category}_attractions": category_attractions
        }
        
    except Exception as e:
        logger.error(f"Error in retrieve_places_by_category: {e}")
        return state

def retrieve_places_by_region(state: Dict[str, Any], region: str) -> Dict[str, Any]:
    """
    Retrieve places filtered by specific region
    """
    try:
        user_input = state.get("user_input", "")
        user_profile = state.get("user_profile", {})
        
        ranker = create_travel_ranker()
        
        user_context = {
            "trip_type": user_profile.get("trip_type", "solo"),
            "budget": user_profile.get("budget_level", "moderate"),
            "interests": user_profile.get("interests", []),
            "duration": user_profile.get("duration_days", 7)
        }
        
        recommendations = ranker.search_by_region(
            user_query=user_input,
            user_context=user_context,
            region_filter=region,
            top_k=20
        )
        
        # Convert to expected format
        regional_attractions = []
        for rec in recommendations:
            place_data = {
                "id": rec["id"],
                "pear_score": rec["neural_score"],
                "similarity_score": rec["similarity_score"],
                "region": region,
                **rec["payload"]
            }
            regional_attractions.append(place_data)
        
        return {
            **state,
            f"{region}_attractions": regional_attractions
        }
        
    except Exception as e:
        logger.error(f"Error in retrieve_places_by_region: {e}")
        return state

def get_similar_attractions(place_id: str, top_k: int = 10) -> List[Dict[str, Any]]:
    """
    Standalone function to get similar attractions
    """
    try:
        ranker = create_travel_ranker()
        similar_places = ranker.get_similar_places(place_id, top_k)
        
        return [
            {
                "id": place["id"],
                "similarity_score": place["similarity_score"],
                **place["payload"]
            }
            for place in similar_places
        ]
        
    except Exception as e:
        logger.error(f"Error in get_similar_attractions: {e}")
        return []
