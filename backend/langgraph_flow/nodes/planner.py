"""
Enhanced Planner Node for Travel Planning
Implements the complete 7-step travel planning process
"""

import asyncio
from typing import Dict, Any, List, Optional
from datetime import datetime, date, time, timedelta
import logging
import os
import sys

# Add the models directory to Python path  
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'models'))

try:
    from geo_clustering import GeographicClusterer, GeoCluster
    from route_optimizer import RouteOptimizer, TimeWindowOptimizer
    from vector_db import QdrantVectorDB, MockVectorDB
    import google.generativeai as genai
except ImportError as e:
    logging.warning(f"Could not import required modules: {e}")
    # Create mock classes for development
    class GeoCluster:
        def __init__(self):
            self.cluster_id = 0
            self.attractions = []
            self.region_name = ""
            self.estimated_time_hours = 0
    
    class GeographicClusterer:
        def cluster_attractions(self, *args, **kwargs):
            return []
        def rank_clusters_by_value(self, clusters):
            return clusters
    
    class RouteOptimizer:
        async def optimize_cluster_route(self, *args, **kwargs):
            return None
    
    class TimeWindowOptimizer:
        def create_time_schedule(self, *args, **kwargs):
            return []

logger = logging.getLogger(__name__)

# Global instances
geo_clusterer = None
route_optimizer = None
time_optimizer = None
llm = None

async def initialize_planner_components():
    """Initialize all planner components"""
    global geo_clusterer, route_optimizer, time_optimizer, llm
    
    if geo_clusterer is None:
        geo_clusterer = GeographicClusterer(cluster_radius_km=5.0)
    
    if route_optimizer is None:
        try:
            from config import settings
            route_optimizer = RouteOptimizer(settings.OPENROUTE_SERVICE_API_KEY)
        except:
            route_optimizer = RouteOptimizer()
    
    if time_optimizer is None:
        time_optimizer = TimeWindowOptimizer()
    
    if llm is None:
        try:
            from config import settings
            logger.info(f"Loading Gemini API key: {settings.GOOGLE_GEMINI_API_KEY[:10]}...")
            if settings.GOOGLE_GEMINI_API_KEY and not settings.GOOGLE_GEMINI_API_KEY.endswith("_TEMP"):
                genai.configure(api_key=settings.GOOGLE_GEMINI_API_KEY)
                llm = genai.GenerativeModel('gemini-2.0-flash-lite')
                logger.info("Gemini LLM initialized successfully")
            else:
                logger.warning("Invalid or temporary Gemini API key detected, skipping LLM initialization")
                llm = None
        except Exception as e:
            logger.error(f"Failed to initialize Gemini LLM: {e}")
            llm = None

async def generate_itinerary(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Enhanced planner implementing the complete 7-step process:
    1. PEAR ranking (already done in retriever)
    2. Geographic clustering
    3. Cluster scoring (value-per-time)
    4. Time window filtering  
    5. Route optimization
    6. Fill gaps with vector DB suggestions
    7. LLM reasoning for final adjustments
    """
    
    try:
        # Initialize components
        await initialize_planner_components()
        
        pear_ranked_attractions = state.get("pear_ranked_attractions", [])
        user_profile = state.get("user_profile", {})
        duration_days = state.get("duration_days", 3)
        start_date = state.get("start_date", date.today())
        
        if not pear_ranked_attractions:
            logger.warning("No attractions to plan with")
            return create_fallback_itinerary(state)
        
        logger.info(f"Starting planning with {len(pear_ranked_attractions)} attractions for {duration_days} days")
        
        # Step 2: Geographic Clustering
        geo_clusters = geo_clusterer.cluster_attractions(pear_ranked_attractions)
        logger.info(f"Created {len(geo_clusters)} geographic clusters")
        
        # Step 3: Cluster Scoring (Value-per-Time)
        ranked_clusters = geo_clusterer.rank_clusters_by_value(geo_clusters)
        logger.info(f"Ranked clusters by value per hour")
        
        # Step 4: Time Window Filtering
        selected_clusters = select_clusters_for_timeframe(
            ranked_clusters, duration_days, user_profile
        )
        logger.info(f"Selected {len(selected_clusters)} clusters for {duration_days} days")
        
        # Step 5: Route Optimization
        optimized_routes = {}
        for cluster in selected_clusters:
            route = await route_optimizer.optimize_cluster_route(cluster.attractions)
            optimized_routes[cluster.cluster_id] = route
        
        # Step 6: Create Daily Schedules
        daily_schedules = create_daily_schedules(
            selected_clusters, optimized_routes, start_date, user_profile
        )
        
        # Step 7: Fill gaps and LLM enhancement
        enhanced_schedules = await enhance_with_gap_filling_and_llm(
            daily_schedules, user_profile, state
        )
        
        # Create final travel plan
        final_plan = create_final_travel_plan(
            enhanced_schedules, user_profile, duration_days, selected_clusters
        )
        
        # Update state
        state.update({
            "geo_clusters": geo_clusters,
            "selected_clusters": selected_clusters,
            "optimized_routes": optimized_routes,
            "daily_schedules": enhanced_schedules,
            "final_plan": final_plan,
            "itinerary": final_plan,  # For backward compatibility
            "reasoning_log": state.get("reasoning_log", []) + [
                f"Generated {len(enhanced_schedules)}-day itinerary with {sum(len(day['items']) for day in enhanced_schedules)} activities"
            ]
        })
        
        logger.info(f"Successfully generated complete travel plan")
        return state
        
    except Exception as e:
        logger.error(f"Error in generate_itinerary: {e}")
        return create_fallback_itinerary(state)

def select_clusters_for_timeframe(clusters: List[GeoCluster], duration_days: int, user_profile: Dict[str, Any]) -> List[GeoCluster]:
    """Select clusters that fit within the available time budget"""
    
    # Calculate available time
    daily_hours = 9  # 9 AM to 6 PM
    total_available_hours = duration_days * daily_hours
    
    # Account for buffer time (travel between clusters, meals, rest)
    buffer_factor = 0.8  # Use 80% of available time
    usable_hours = total_available_hours * buffer_factor
    
    selected_clusters = []
    used_hours = 0
    
    for cluster in clusters:
        # Add inter-cluster travel time estimate
        inter_cluster_travel = 2.0  # 2 hours travel between clusters
        if selected_clusters:
            cluster_time_needed = cluster.estimated_time_hours + inter_cluster_travel
        else:
            cluster_time_needed = cluster.estimated_time_hours
        
        if used_hours + cluster_time_needed <= usable_hours:
            selected_clusters.append(cluster)
            used_hours += cluster_time_needed
        else:
            break
    
    # Ensure we have at least one cluster per day if possible
    if len(selected_clusters) < duration_days and len(clusters) >= duration_days:
        # Select top clusters, one per day
        selected_clusters = clusters[:duration_days]
    
    return selected_clusters

def create_daily_schedules(clusters: List[GeoCluster], routes: Dict[int, Any], start_date: date, user_profile: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Create detailed daily schedules"""
    
    daily_schedules = []
    current_date = start_date
    
    for day_num, cluster in enumerate(clusters, 1):
        route = routes.get(cluster.cluster_id)
        
        # Create time schedule for this cluster
        schedule_items = []
        if route and route.attraction_order:
            schedule_items = time_optimizer.create_time_schedule(
                route, cluster.attractions, "09:00", "18:00"
            )
        
        # Create day schedule
        day_schedule = {
            "day": day_num,
            "date": current_date.isoformat(),
            "cluster_id": cluster.cluster_id,
            "cluster_name": cluster.region_name or f"Cluster {cluster.cluster_id}",
            "items": schedule_items,
            "lunch_time": "12:30",
            "lunch_location": find_lunch_location(cluster),
            "accommodation": find_accommodation(cluster, user_profile),
            "total_attractions": len(schedule_items),
            "total_travel_time_minutes": route.total_travel_time_minutes if route else 0
        }
        
        daily_schedules.append(day_schedule)
        current_date += timedelta(days=1)
    
    return daily_schedules

def find_lunch_location(cluster: GeoCluster) -> str:
    """Find suitable lunch location for the cluster"""
    
    # Simple implementation - would typically use Google Places API
    if cluster.region_name:
        return f"Local restaurant in {cluster.region_name}"
    else:
        return "Local restaurant"

def find_accommodation(cluster: GeoCluster, user_profile: Dict[str, Any]) -> str:
    """Find accommodation recommendation for the cluster"""
    
    budget = user_profile.get('budget_level', 'mid_range')
    
    if budget == 'luxury':
        accommodation_type = "Luxury resort"
    elif budget == 'budget':
        accommodation_type = "Budget guesthouse"
    else:
        accommodation_type = "Mid-range hotel"
    
    region = cluster.region_name or "the area"
    return f"{accommodation_type} in {region}"

async def enhance_with_gap_filling_and_llm(schedules: List[Dict[str, Any]], user_profile: Dict[str, Any], state: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Step 6 & 7: Fill gaps and enhance with LLM reasoning"""
    
    enhanced_schedules = []
    
    for schedule in schedules:
        enhanced_schedule = schedule.copy()
        
        # Check for time gaps and fill them
        enhanced_schedule = await fill_time_gaps(enhanced_schedule, user_profile, state)
        
        enhanced_schedules.append(enhanced_schedule)
    
    # Apply LLM reasoning for final adjustments
    if llm:
        enhanced_schedules = await apply_llm_reasoning(enhanced_schedules, user_profile, state)
    
    return enhanced_schedules

async def fill_time_gaps(schedule: Dict[str, Any], user_profile: Dict[str, Any], state: Dict[str, Any]) -> Dict[str, Any]:
    """Fill time gaps with additional suggestions"""
    
    # Calculate total scheduled time
    total_scheduled_minutes = sum(
        item.get('visit_duration_minutes', 0) + item.get('travel_time_minutes', 0)
        for item in schedule['items']
    )
    
    # Check if we have significant gaps (more than 2 hours)
    daily_minutes = 9 * 60  # 9 hours
    free_time = daily_minutes - total_scheduled_minutes
    
    if free_time > 120:  # More than 2 hours free
        # Look for additional suggestions using vector DB
        try:
            vector_db = state.get('vector_db')
            if vector_db:
                # Search for nearby attractions
                cluster_region = schedule.get('cluster_name', '')
                additional_suggestions = await vector_db.semantic_search(
                    query=f"attractions near {cluster_region}",
                    user_profile=user_profile,
                    limit=3
                )
                
                # Add suggestions to schedule notes
                if additional_suggestions:
                    schedule['additional_suggestions'] = [
                        {
                            'name': result.attraction_data.get('name', ''),
                            'description': result.attraction_data.get('description', ''),
                            'suggestion_type': 'gap_filler'
                        }
                        for result in additional_suggestions
                    ]
        except Exception as e:
            logger.warning(f"Could not add gap fillers: {e}")
    
    return schedule

async def apply_llm_reasoning(schedules: List[Dict[str, Any]], user_profile: Dict[str, Any], state: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Apply LLM reasoning for final plan adjustments"""
    
    if not llm:
        logger.info("LLM not available, skipping LLM reasoning")
        return schedules
    
    try:
        # Create prompt for LLM
        prompt = create_llm_prompt(schedules, user_profile, state)
        
        # Get LLM suggestions
        response = llm.generate_content(prompt)
        
        # Parse and apply suggestions
        enhanced_schedules = parse_llm_suggestions(schedules, response.text)
        
        logger.info("LLM reasoning completed successfully")
        return enhanced_schedules
        
    except Exception as e:
        logger.error(f"LLM reasoning failed: {e}")
        # If LLM fails, return original schedules without enhancement
        logger.info("Continuing without LLM enhancement")
        return schedules

def create_llm_prompt(schedules: List[Dict[str, Any]], user_profile: Dict[str, Any], state: Dict[str, Any]) -> str:
    """Create prompt for LLM to review and enhance the itinerary"""
    
    prompt_parts = [
        "You are a Sri Lankan travel expert. Please review this travel itinerary and suggest improvements.",
        "",
        f"Traveler Profile:",
        f"- Interests: {', '.join(user_profile.get('interests', []))}",
        f"- Trip type: {user_profile.get('trip_type', 'couple')}",
        f"- Budget: {user_profile.get('budget_level', 'mid_range')}",
        f"- Adventure level: {user_profile.get('adventure_level', 3)}/5",
        "",
        "Current Itinerary:"
    ]
    
    for schedule in schedules:
        prompt_parts.append(f"\nDay {schedule['day']} - {schedule['cluster_name']}:")
        for item in schedule['items']:
            prompt_parts.append(f"  - {item['start_time']}-{item['end_time']}: {item['attraction_name']}")
    
    prompt_parts.extend([
        "",
        "Please provide:",
        "1. Overall assessment of the itinerary balance",
        "2. Specific suggestions for improvements",
        "3. Weather and seasonal considerations",
        "4. Local tips and cultural insights",
        "5. Packing suggestions",
        "",
        "Keep suggestions practical and specific to Sri Lanka."
    ])
    
    return "\n".join(prompt_parts)

def parse_llm_suggestions(schedules: List[Dict[str, Any]], llm_response: str) -> List[Dict[str, Any]]:
    """Parse LLM response and apply suggestions to schedules"""
    
    # For now, just add the LLM response as a general recommendation
    # In a full implementation, you would parse specific suggestions and apply them
    
    enhanced_schedules = []
    for schedule in schedules:
        enhanced_schedule = schedule.copy()
        if not enhanced_schedule.get('llm_insights'):
            enhanced_schedule['llm_insights'] = llm_response
        enhanced_schedules.append(enhanced_schedule)
    
    return enhanced_schedules

def create_final_travel_plan(schedules: List[Dict[str, Any]], user_profile: Dict[str, Any], duration_days: int, clusters: List[GeoCluster]) -> Dict[str, Any]:
    """Create the final comprehensive travel plan"""
    
    # Calculate totals
    total_attractions = sum(schedule['total_attractions'] for schedule in schedules)
    
    # Generate recommendations
    hotel_recommendations = generate_hotel_recommendations(clusters, user_profile)
    restaurant_recommendations = generate_restaurant_recommendations(clusters, user_profile)
    
    # Estimate costs
    estimated_cost = estimate_total_cost(schedules, user_profile)
    
    # Create final plan
    final_plan = {
        "plan_id": f"plan_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
        "user_profile": user_profile,
        "total_days": duration_days,
        "total_attractions": total_attractions,
        "daily_schedules": schedules,
        "recommended_hotels": hotel_recommendations,
        "recommended_restaurants": restaurant_recommendations,
        "total_estimated_cost": estimated_cost,
        "weather_considerations": get_weather_considerations(),
        "packing_suggestions": generate_packing_suggestions(user_profile),
        "local_tips": generate_local_tips(),
        "emergency_contacts": get_emergency_contacts(),
        "explanation": generate_plan_explanation(schedules, user_profile)
    }
    
    return final_plan

def generate_hotel_recommendations(clusters: List[GeoCluster], user_profile: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Generate hotel recommendations based on clusters and budget"""
    
    budget = user_profile.get('budget_level', 'mid_range')
    recommendations = []
    
    for cluster in clusters:
        if budget == 'luxury':
            hotel = {
                "name": f"Luxury Resort in {cluster.region_name}",
                "type": "5-star resort",
                "price_range": "$150-300/night",
                "features": ["pool", "spa", "fine_dining"]
            }
        elif budget == 'budget':
            hotel = {
                "name": f"Guesthouse in {cluster.region_name}",
                "type": "Budget accommodation",
                "price_range": "$20-50/night",
                "features": ["clean_rooms", "basic_amenities"]
            }
        else:
            hotel = {
                "name": f"Mid-range Hotel in {cluster.region_name}",
                "type": "3-4 star hotel",
                "price_range": "$60-120/night",
                "features": ["restaurant", "wifi", "ac"]
            }
        
        recommendations.append(hotel)
    
    return recommendations

def generate_restaurant_recommendations(clusters: List[GeoCluster], user_profile: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Generate restaurant recommendations"""
    
    recommendations = [
        {
            "name": "Local Sri Lankan Restaurant",
            "cuisine": "Traditional Sri Lankan",
            "specialties": ["Rice and curry", "Hoppers", "Kottu"]
        },
        {
            "name": "Seafood Restaurant", 
            "cuisine": "Fresh seafood",
            "specialties": ["Fish curry", "Crab curry", "Prawn dishes"]
        }
    ]
    
    return recommendations

def estimate_total_cost(schedules: List[Dict[str, Any]], user_profile: Dict[str, Any]) -> float:
    """Estimate total trip cost"""
    
    budget = user_profile.get('budget_level', 'mid_range')
    
    base_costs = {
        'budget': 30,
        'mid_range': 60,
        'luxury': 150
    }
    
    daily_cost = base_costs.get(budget, 60)
    total_days = len(schedules)
    
    return daily_cost * total_days

def get_weather_considerations() -> str:
    """Get weather considerations for Sri Lanka"""
    
    return "Sri Lanka has a tropical climate. Dry season (Dec-Mar) is best for west/south coasts. East coast is best Apr-Sep. Bring light, breathable clothing and rain gear."

def generate_packing_suggestions(user_profile: Dict[str, Any]) -> List[str]:
    """Generate packing suggestions"""
    
    suggestions = [
        "Light, breathable clothing",
        "Comfortable walking shoes",
        "Sun hat and sunscreen",
        "Insect repellent",
        "Light rain jacket"
    ]
    
    if user_profile.get('adventure_level', 0) > 3:
        suggestions.extend(["Hiking boots", "Quick-dry clothing"])
    
    if any(interest in ['cultural', 'spiritual'] for interest in user_profile.get('interests', [])):
        suggestions.append("Modest clothing for temples")
    
    return suggestions

def generate_local_tips() -> List[str]:
    """Generate local tips for Sri Lanka"""
    
    return [
        "Remove shoes before entering temples",
        "Dress modestly when visiting religious sites",
        "Try local street food but choose busy stalls",
        "Bargain politely in markets",
        "Learn basic Sinhala phrases like 'Ayubowan' (hello)",
        "Tip 10% in restaurants if service charge not included"
    ]

def get_emergency_contacts() -> List[str]:
    """Get emergency contact information"""
    
    return [
        "Police: 119",
        "Tourist Police: 1912",
        "Fire & Rescue: 110",
        "Sri Lanka Tourism Hotline: +94 11 2426900"
    ]

def generate_plan_explanation(schedules: List[Dict[str, Any]], user_profile: Dict[str, Any]) -> str:
    """Generate explanation of the travel plan"""
    
    interests = user_profile.get('interests', [])
    trip_type = user_profile.get('trip_type', 'couple')
    
    explanation = f"This {len(schedules)}-day itinerary is designed for {trip_type} travelers interested in {', '.join(interests)}. "
    explanation += f"The plan balances must-see attractions with your personal interests, optimizing travel time and ensuring a memorable experience. "
    explanation += f"Each day focuses on a specific region to minimize travel fatigue while maximizing your enjoyment."
    
    return explanation

def create_fallback_itinerary(state: Dict[str, Any]) -> Dict[str, Any]:
    """Create a fallback itinerary when main planning fails"""
    
    logger.warning("Creating fallback itinerary")
    
    fallback_plan = {
        "plan_id": "fallback_plan",
        "daily_schedules": [
            {
                "day": 1,
                "date": (date.today() + timedelta(days=30)).isoformat(),
                "cluster_name": "Colombo & Surroundings",
                "items": [
                    {
                        "attraction_name": "National Museum",
                        "start_time": "09:00",
                        "end_time": "11:00"
                    },
                    {
                        "attraction_name": "Gangaramaya Temple",
                        "start_time": "11:30",
                        "end_time": "12:30"
                    }
                ],
                "total_attractions": 2
            }
        ],
        "explanation": "This is a basic fallback itinerary. Please try again with more specific preferences."
    }
    
    state.update({
        "final_plan": fallback_plan,
        "itinerary": fallback_plan,
        "reasoning_log": state.get("reasoning_log", []) + [
            "Used fallback itinerary due to planning errors"
        ]
    })
    
    return state
