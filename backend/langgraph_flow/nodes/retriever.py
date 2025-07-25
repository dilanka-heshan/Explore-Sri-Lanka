"""
Enhanced Retriever Node for Travel Planning
Retrieves and ranks attractions using PEAR model and vector similarity search
"""

import asyncio
from typing import Dict, Any, List
import logging
import os
import sys

# Add the models directory to Python path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'models'))

try:
    from vector_db import QdrantVectorDB, MockVectorDB
    from pear_ranker import PEARRanker
except ImportError as e:
    logging.warning(f"Could not import custom modules: {e}")
    # Create mock classes
    class MockVectorDB:
        async def semantic_search(self, *args, **kwargs):
            return []
    class PEARRanker:
        def get_top_attractions(self, *args, **kwargs):
            return []

logger = logging.getLogger(__name__)

# Global instances (will be initialized once)
vector_db = None
pear_ranker = None

async def initialize_retriever_components():
    """Initialize vector DB and PEAR ranker components"""
    global vector_db, pear_ranker
    
    if vector_db is None:
        try:
            # Try to initialize Qdrant
            from config import settings
            vector_db = QdrantVectorDB(
                host=settings.QDRANT_HOST,
                port=settings.QDRANT_PORT,
                collection_name=settings.QDRANT_COLLECTION_NAME
            )
            await vector_db.initialize_collection()
        except Exception as e:
            logger.warning(f"Failed to initialize Qdrant, using mock: {e}")
            vector_db = MockVectorDB()
    
    if pear_ranker is None:
        try:
            pear_ranker = PEARRanker()
        except Exception as e:
            logger.warning(f"Failed to initialize PEAR ranker: {e}")
            pear_ranker = MockPEARRanker()

class MockPEARRanker:
    """Mock PEAR ranker for development"""
    def get_top_attractions(self, user_profile, attractions, top_k=50):
        return attractions[:top_k]

async def retrieve_places(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Enhanced retriever that finds relevant attractions using multiple methods:
    1. Vector similarity search based on user interests
    2. PEAR neural ranking for personalization
    3. Fallback rule-based filtering
    
    Args:
        state: Current planning state with user profile and preferences
    
    Returns:
        Updated state with candidate attractions and PEAR-ranked results
    """
    
    try:
        # Initialize components if needed
        await initialize_retriever_components()
        
        user_profile = state.get("user_profile", {})
        interests = state.get("parsed_interests", ["cultural", "nature"])
        preferred_regions = state.get("preferred_regions", [])
        excluded_attractions = state.get("excluded_attractions", [])
        
        # Step 1: Get candidate attractions from multiple sources
        candidate_attractions = await get_candidate_attractions(
            user_profile, interests, preferred_regions, excluded_attractions
        )
        
        logger.info(f"Found {len(candidate_attractions)} candidate attractions")
        
        # Step 2: Apply PEAR ranking for personalization
        if candidate_attractions:
            pear_ranked_attractions = pear_ranker.get_top_attractions(
                user_profile=user_profile,
                attractions=candidate_attractions,
                top_k=50  # Top 50 for further processing
            )
        else:
            pear_ranked_attractions = []
        
        logger.info(f"PEAR ranking selected {len(pear_ranked_attractions)} top attractions")
        
        # Update state
        state.update({
            "candidate_attractions": candidate_attractions,
            "pear_ranked_attractions": pear_ranked_attractions,
            "reasoning_log": state.get("reasoning_log", []) + [
                f"Retrieved {len(candidate_attractions)} candidates, ranked to {len(pear_ranked_attractions)} top attractions"
            ]
        })
        
        return state
        
    except Exception as e:
        logger.error(f"Error in retrieve_places: {e}")
        # Fallback to mock data
        mock_attractions = create_mock_attractions()
        state.update({
            "candidate_attractions": mock_attractions,
            "pear_ranked_attractions": mock_attractions[:20],
            "reasoning_log": state.get("reasoning_log", []) + [
                f"Used fallback attractions due to error: {e}"
            ]
        })
        return state

async def get_candidate_attractions(user_profile: Dict[str, Any], interests: List[str], preferred_regions: List[str], excluded_attractions: List[str]) -> List[Dict[str, Any]]:
    """Get candidate attractions from multiple sources"""
    
    all_attractions = []
    
    # Method 1: Vector similarity search
    vector_attractions = await get_attractions_from_vector_search(user_profile, interests)
    all_attractions.extend(vector_attractions)
    
    # Method 2: Region-based search
    if preferred_regions:
        region_attractions = await get_attractions_by_regions(preferred_regions)
        all_attractions.extend(region_attractions)
    
    # Method 3: Interest-based fallback
    interest_attractions = await get_attractions_by_interests(interests)
    all_attractions.extend(interest_attractions)
    
    # Remove duplicates and excluded attractions
    unique_attractions = remove_duplicates_and_excluded(all_attractions, excluded_attractions)
    
    # Add mock data if no attractions found
    if not unique_attractions:
        unique_attractions = create_mock_attractions()
    
    return unique_attractions

async def get_attractions_from_vector_search(user_profile: Dict[str, Any], interests: List[str]) -> List[Dict[str, Any]]:
    """Get attractions using vector similarity search"""
    
    try:
        # Create search query from interests and profile
        query = create_search_query(user_profile, interests)
        
        # Search in vector database
        search_results = await vector_db.semantic_search(
            query=query,
            user_profile=user_profile,
            limit=30
        )
        
        # Convert search results to attraction format
        attractions = []
        for result in search_results:
            attraction = result.attraction_data.copy()
            attraction['vector_score'] = result.score
            attractions.append(attraction)
        
        return attractions
        
    except Exception as e:
        logger.error(f"Vector search failed: {e}")
        return []

def create_search_query(user_profile: Dict[str, Any], interests: List[str]) -> str:
    """Create search query from user profile and interests"""
    
    query_parts = []
    
    # Add interests
    query_parts.append(f"Interested in {', '.join(interests)}")
    
    # Add trip type context
    trip_type = user_profile.get('trip_type', 'couple')
    query_parts.append(f"{trip_type} travel")
    
    # Add budget context
    budget = user_profile.get('budget_level', 'mid_range')
    if budget == 'budget':
        query_parts.append("affordable attractions")
    elif budget == 'luxury':
        query_parts.append("premium experiences")
    
    # Add activity level context
    adventure_level = user_profile.get('adventure_level', 3)
    if adventure_level >= 4:
        query_parts.append("adventurous activities")
    elif adventure_level <= 2:
        query_parts.append("relaxed activities")
    
    return " ".join(query_parts)

async def get_attractions_by_regions(regions: List[str]) -> List[Dict[str, Any]]:
    """Get attractions from specific regions"""
    
    try:
        attractions = []
        for region in regions:
            region_results = await vector_db.get_attractions_by_region(region, limit=20)
            for result in region_results:
                attraction = result.attraction_data.copy()
                attraction['source'] = 'region_search'
                attractions.append(attraction)
        return attractions
        
    except Exception as e:
        logger.error(f"Region search failed: {e}")
        return []

async def get_attractions_by_interests(interests: List[str]) -> List[Dict[str, Any]]:
    """Fallback method to get attractions by interests"""
    
    # This would typically query a database
    # For now, return mock data based on interests
    mock_data = create_mock_attractions()
    
    # Filter mock data by interests
    filtered_attractions = []
    for attraction in mock_data:
        attraction_category = attraction.get('category', '').lower()
        if any(interest.lower() in attraction_category for interest in interests):
            filtered_attractions.append(attraction)
    
    return filtered_attractions

def remove_duplicates_and_excluded(attractions: List[Dict[str, Any]], excluded: List[str]) -> List[Dict[str, Any]]:
    """Remove duplicate attractions and excluded items"""
    
    seen_ids = set()
    unique_attractions = []
    
    for attraction in attractions:
        attraction_id = attraction.get('id')
        attraction_name = attraction.get('name', '').lower()
        
        # Skip if already seen or excluded
        if attraction_id in seen_ids:
            continue
        
        if any(exc.lower() in attraction_name for exc in excluded):
            continue
        
        seen_ids.add(attraction_id)
        unique_attractions.append(attraction)
    
    return unique_attractions

def create_mock_attractions() -> List[Dict[str, Any]]:
    """Create mock attraction data for development/testing"""
    
    return [
        {
            'id': 'sigiriya_rock',
            'name': 'Sigiriya Rock Fortress',
            'description': 'Ancient rock fortress and palace ruins with stunning frescoes',
            'category': 'historical',
            'latitude': 7.9570,
            'longitude': 80.7603,
            'rating': 4.6,
            'review_count': 15000,
            'tags': ['UNESCO', 'historical', 'climbing', 'views'],
            'entry_fee': 30.0,
            'visit_duration_minutes': 180,
            'difficulty_level': 'moderate',
            'region': 'North Central',
            'facilities': ['parking', 'restrooms', 'guide_service']
        },
        {
            'id': 'temple_of_tooth',
            'name': 'Temple of the Sacred Tooth Relic',
            'description': 'Sacred Buddhist temple housing tooth relic of Buddha',
            'category': 'cultural',
            'latitude': 7.2936,
            'longitude': 80.6410,
            'rating': 4.5,
            'review_count': 12000,
            'tags': ['Buddhist', 'cultural', 'sacred', 'Kandy'],
            'entry_fee': 10.0,
            'visit_duration_minutes': 120,
            'difficulty_level': 'easy',
            'region': 'Central',
            'facilities': ['parking', 'restrooms', 'museum']
        },
        {
            'id': 'yala_national_park',
            'name': 'Yala National Park',
            'description': 'Premier wildlife sanctuary famous for leopards',
            'category': 'wildlife',
            'latitude': 6.3725,
            'longitude': 81.5185,
            'rating': 4.4,
            'review_count': 8000,
            'tags': ['wildlife', 'safari', 'leopards', 'elephants'],
            'entry_fee': 25.0,
            'visit_duration_minutes': 240,
            'difficulty_level': 'easy',
            'region': 'Southern',
            'facilities': ['safari_vehicles', 'restrooms', 'restaurant']
        },
        {
            'id': 'galle_fort',
            'name': 'Galle Dutch Fort',
            'description': 'Historic Dutch colonial fortification by the sea',
            'category': 'historical',
            'latitude': 6.0329,
            'longitude': 80.2168,
            'rating': 4.3,
            'review_count': 10000,
            'tags': ['colonial', 'Dutch', 'fort', 'UNESCO'],
            'entry_fee': 0.0,
            'visit_duration_minutes': 150,
            'difficulty_level': 'easy',
            'region': 'Southern',
            'facilities': ['parking', 'restaurants', 'shops']
        },
        {
            'id': 'ella_nine_arch',
            'name': 'Nine Arch Bridge Ella',
            'description': 'Iconic railway bridge surrounded by lush greenery',
            'category': 'nature',
            'latitude': 6.8729,
            'longitude': 81.0456,
            'rating': 4.2,
            'review_count': 6000,
            'tags': ['bridge', 'railway', 'nature', 'photography'],
            'entry_fee': 0.0,
            'visit_duration_minutes': 90,
            'difficulty_level': 'easy',
            'region': 'Uva',
            'facilities': ['parking', 'viewpoints']
        },
        {
            'id': 'adams_peak',
            'name': "Adam's Peak (Sri Pada)",
            'description': 'Sacred mountain with pilgrimage trail and sunrise views',
            'category': 'adventure',
            'latitude': 6.8095,
            'longitude': 80.4989,
            'rating': 4.7,
            'review_count': 7500,
            'tags': ['mountain', 'pilgrimage', 'hiking', 'sunrise'],
            'entry_fee': 0.0,
            'visit_duration_minutes': 360,
            'difficulty_level': 'challenging',
            'region': 'Central',
            'facilities': ['rest_stops', 'basic_food']
        },
        {
            'id': 'mirissa_beach',
            'name': 'Mirissa Beach',
            'description': 'Beautiful beach famous for whale watching and surfing',
            'category': 'beach',
            'latitude': 5.9487,
            'longitude': 80.4565,
            'rating': 4.1,
            'review_count': 5500,
            'tags': ['beach', 'whale_watching', 'surfing', 'sunset'],
            'entry_fee': 0.0,
            'visit_duration_minutes': 180,
            'difficulty_level': 'easy',
            'region': 'Southern',
            'facilities': ['restaurants', 'water_sports', 'parking']
        },
        {
            'id': 'polonnaruwa',
            'name': 'Ancient City of Polonnaruwa',
            'description': 'Medieval capital with well-preserved ruins and sculptures',
            'category': 'historical',
            'latitude': 7.9403,
            'longitude': 81.0188,
            'rating': 4.4,
            'review_count': 4500,
            'tags': ['ancient', 'ruins', 'UNESCO', 'cycling'],
            'entry_fee': 25.0,
            'visit_duration_minutes': 240,
            'difficulty_level': 'moderate',
            'region': 'North Central',
            'facilities': ['bicycle_rental', 'museum', 'restrooms']
        }
    ]
