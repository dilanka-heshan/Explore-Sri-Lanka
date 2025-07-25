"""
Qdrant Vector Database Interface
Handles vector storage and semantic similarity search for attractions
"""

from typing import List, Dict, Any, Optional, Tuple
import logging
from dataclasses import dataclass
import json

try:
    from qdrant_client import QdrantClient
    from qdrant_client.models import Distance, VectorParams, PointStruct, Filter, FieldCondition, Range, MatchValue
    from sentence_transformers import SentenceTransformer
    QDRANT_AVAILABLE = True
except ImportError:
    QDRANT_AVAILABLE = False
    logging.warning("Qdrant client not available. Vector search will use fallback methods.")

logger = logging.getLogger(__name__)

@dataclass
class SearchResult:
    """Represents a search result from vector database"""
    attraction_id: str
    score: float
    attraction_data: Dict[str, Any]

class QdrantVectorDB:
    """Interface to Qdrant vector database for attraction similarity search"""
    
    def __init__(self, host: str = "localhost", port: int = 6333, collection_name: str = "sri_lanka_attractions", embedding_model: str = "sentence-transformers/all-MiniLM-L6-v2"):
        self.host = host
        self.port = port
        self.collection_name = collection_name
        self.embedding_model_name = embedding_model
        
        if QDRANT_AVAILABLE:
            try:
                self.client = QdrantClient(host=host, port=port)
                self.embedding_model = SentenceTransformer(embedding_model)
                self.embedding_dim = self.embedding_model.get_sentence_embedding_dimension()
                logger.info(f"Connected to Qdrant at {host}:{port}")
            except Exception as e:
                logger.error(f"Failed to connect to Qdrant: {e}")
                self.client = None
                self.embedding_model = None
        else:
            self.client = None
            self.embedding_model = None
            logger.warning("Qdrant not available, using fallback search")
    
    async def initialize_collection(self):
        """Initialize the Qdrant collection if it doesn't exist"""
        
        if not self.client:
            return False
        
        try:
            # Check if collection exists
            collections = self.client.get_collections()
            collection_names = [col.name for col in collections.collections]
            
            if self.collection_name not in collection_names:
                # Create collection
                self.client.create_collection(
                    collection_name=self.collection_name,
                    vectors_config=VectorParams(size=self.embedding_dim, distance=Distance.COSINE)
                )
                logger.info(f"Created Qdrant collection: {self.collection_name}")
            else:
                logger.info(f"Collection {self.collection_name} already exists")
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize Qdrant collection: {e}")
            return False
    
    async def index_attractions(self, attractions: List[Dict[str, Any]]):
        """Index attractions in the vector database"""
        
        if not self.client or not self.embedding_model:
            logger.warning("Qdrant not available for indexing")
            return False
        
        try:
            points = []
            
            for attraction in attractions:
                # Create text representation for embedding
                text_content = self._create_attraction_text(attraction)
                
                # Generate embedding
                embedding = self.embedding_model.encode(text_content).tolist()
                
                # Create point
                point = PointStruct(
                    id=attraction.get('id', str(len(points))),
                    vector=embedding,
                    payload={
                        'id': attraction.get('id'),
                        'name': attraction.get('name'),
                        'category': attraction.get('category'),
                        'description': attraction.get('description', '')[:500],  # Truncate for storage
                        'tags': attraction.get('tags', []),
                        'rating': attraction.get('rating', 0),
                        'latitude': attraction.get('latitude'),
                        'longitude': attraction.get('longitude'),
                        'region': attraction.get('region'),
                        'entry_fee': attraction.get('entry_fee', 0),
                        'difficulty_level': attraction.get('difficulty_level', 'easy')
                    }
                )
                points.append(point)
            
            # Upload points to Qdrant
            self.client.upsert(
                collection_name=self.collection_name,
                points=points
            )
            
            logger.info(f"Indexed {len(points)} attractions in Qdrant")
            return True
            
        except Exception as e:
            logger.error(f"Failed to index attractions: {e}")
            return False
    
    def _create_attraction_text(self, attraction: Dict[str, Any]) -> str:
        """Create text representation of attraction for embedding"""
        
        parts = []
        
        # Basic info
        if attraction.get('name'):
            parts.append(f"Name: {attraction['name']}")
        
        if attraction.get('description'):
            parts.append(f"Description: {attraction['description']}")
        
        if attraction.get('category'):
            parts.append(f"Category: {attraction['category']}")
        
        # Tags and features
        if attraction.get('tags'):
            parts.append(f"Tags: {', '.join(attraction['tags'])}")
        
        if attraction.get('facilities'):
            parts.append(f"Facilities: {', '.join(attraction['facilities'])}")
        
        # Contextual info
        if attraction.get('region'):
            parts.append(f"Region: {attraction['region']}")
        
        if attraction.get('best_season'):
            parts.append(f"Best season: {attraction['best_season']}")
        
        return " | ".join(parts)
    
    async def semantic_search(self, query: str, user_profile: Dict[str, Any] = None, limit: int = 20, filters: Dict[str, Any] = None) -> List[SearchResult]:
        """
        Perform semantic similarity search
        
        Args:
            query: Search query (user interests, preferences)
            user_profile: User profile for additional context
            limit: Maximum number of results
            filters: Additional filters (category, region, etc.)
        
        Returns:
            List of search results
        """
        
        if not self.client or not self.embedding_model:
            return self._fallback_search(query, user_profile, limit, filters)
        
        try:
            # Enhance query with user profile
            enhanced_query = self._enhance_query_with_profile(query, user_profile)
            
            # Generate query embedding
            query_embedding = self.embedding_model.encode(enhanced_query).tolist()
            
            # Build filters
            search_filter = self._build_search_filter(filters)
            
            # Perform search
            search_results = self.client.search(
                collection_name=self.collection_name,
                query_vector=query_embedding,
                query_filter=search_filter,
                limit=limit,
                with_payload=True
            )
            
            # Convert to SearchResult objects
            results = []
            for result in search_results:
                search_result = SearchResult(
                    attraction_id=result.payload.get('id', str(result.id)),
                    score=result.score,
                    attraction_data=result.payload
                )
                results.append(search_result)
            
            logger.info(f"Found {len(results)} attractions with semantic search")
            return results
            
        except Exception as e:
            logger.error(f"Semantic search failed: {e}")
            return self._fallback_search(query, user_profile, limit, filters)
    
    def _enhance_query_with_profile(self, query: str, user_profile: Dict[str, Any]) -> str:
        """Enhance search query with user profile information"""
        
        if not user_profile:
            return query
        
        enhanced_parts = [query]
        
        # Add interests
        if user_profile.get('interests'):
            interests_text = f"interested in {', '.join(user_profile['interests'])}"
            enhanced_parts.append(interests_text)
        
        # Add trip type
        if user_profile.get('trip_type'):
            enhanced_parts.append(f"{user_profile['trip_type']} travel")
        
        # Add budget level
        if user_profile.get('budget_level'):
            enhanced_parts.append(f"{user_profile['budget_level']} budget")
        
        # Add preferences
        if user_profile.get('adventure_level', 0) > 3:
            enhanced_parts.append("adventurous activities")
        
        if user_profile.get('cultural_interest_level', 0) > 3:
            enhanced_parts.append("cultural experiences")
        
        if user_profile.get('nature_appreciation', 0) > 3:
            enhanced_parts.append("nature and wildlife")
        
        return " ".join(enhanced_parts)
    
    def _build_search_filter(self, filters: Dict[str, Any]) -> Optional[Filter]:
        """Build Qdrant filter from search criteria"""
        
        if not filters or not QDRANT_AVAILABLE:
            return None
        
        try:
            filter_conditions = []
            
            # Category filter
            if filters.get('category'):
                filter_conditions.append(
                    FieldCondition(key="category", match=MatchValue(value=filters['category']))
                )
            
            # Region filter
            if filters.get('region'):
                filter_conditions.append(
                    FieldCondition(key="region", match=MatchValue(value=filters['region']))
                )
            
            # Rating filter
            if filters.get('min_rating'):
                filter_conditions.append(
                    FieldCondition(key="rating", range=Range(gte=filters['min_rating']))
                )
            
            # Entry fee filter
            if filters.get('max_entry_fee'):
                filter_conditions.append(
                    FieldCondition(key="entry_fee", range=Range(lte=filters['max_entry_fee']))
                )
            
            # Difficulty filter
            if filters.get('difficulty_level'):
                filter_conditions.append(
                    FieldCondition(key="difficulty_level", match=MatchValue(value=filters['difficulty_level']))
                )
            
            if filter_conditions:
                return Filter(must=filter_conditions)
            
        except Exception as e:
            logger.error(f"Failed to build search filter: {e}")
        
        return None
    
    def _fallback_search(self, query: str, user_profile: Dict[str, Any], limit: int, filters: Dict[str, Any]) -> List[SearchResult]:
        """Fallback search when Qdrant is not available"""
        
        logger.info("Using fallback text-based search")
        
        # This would typically search a local database or file
        # For now, return empty results
        return []
    
    async def get_similar_attractions(self, attraction_id: str, limit: int = 10) -> List[SearchResult]:
        """Get attractions similar to a given attraction"""
        
        if not self.client:
            return []
        
        try:
            # Get the attraction vector
            attraction_data = self.client.retrieve(
                collection_name=self.collection_name,
                ids=[attraction_id],
                with_vectors=True
            )
            
            if not attraction_data:
                return []
            
            attraction_vector = attraction_data[0].vector
            
            # Search for similar attractions
            search_results = self.client.search(
                collection_name=self.collection_name,
                query_vector=attraction_vector,
                limit=limit + 1,  # +1 to exclude the attraction itself
                with_payload=True
            )
            
            # Filter out the original attraction and convert to SearchResult
            results = []
            for result in search_results:
                if result.payload.get('id') != attraction_id:
                    search_result = SearchResult(
                        attraction_id=result.payload.get('id', str(result.id)),
                        score=result.score,
                        attraction_data=result.payload
                    )
                    results.append(search_result)
            
            return results[:limit]
            
        except Exception as e:
            logger.error(f"Failed to get similar attractions: {e}")
            return []
    
    async def get_attractions_by_region(self, region: str, limit: int = 50) -> List[SearchResult]:
        """Get all attractions in a specific region"""
        
        if not self.client:
            return []
        
        try:
            filter_condition = Filter(
                must=[FieldCondition(key="region", match=MatchValue(value=region))]
            )
            
            # Use scroll to get all attractions in region
            scroll_result = self.client.scroll(
                collection_name=self.collection_name,
                scroll_filter=filter_condition,
                limit=limit,
                with_payload=True
            )
            
            results = []
            for point in scroll_result[0]:
                search_result = SearchResult(
                    attraction_id=point.payload.get('id', str(point.id)),
                    score=1.0,  # No relevance score for region-based search
                    attraction_data=point.payload
                )
                results.append(search_result)
            
            return results
            
        except Exception as e:
            logger.error(f"Failed to get attractions by region: {e}")
            return []

class MockVectorDB:
    """Mock vector database for development/testing when Qdrant is not available"""
    
    def __init__(self):
        self.attractions_data = []
        logger.info("Using mock vector database")
    
    async def initialize_collection(self):
        return True
    
    async def index_attractions(self, attractions: List[Dict[str, Any]]):
        self.attractions_data = attractions
        logger.info(f"Mock indexed {len(attractions)} attractions")
        return True
    
    async def semantic_search(self, query: str, user_profile: Dict[str, Any] = None, limit: int = 20, filters: Dict[str, Any] = None) -> List[SearchResult]:
        """Simple text-based search for mock implementation"""
        
        query_lower = query.lower()
        results = []
        
        for attraction in self.attractions_data:
            score = 0.0
            
            # Simple text matching
            name = attraction.get('name', '').lower()
            description = attraction.get('description', '').lower()
            tags = ' '.join(attraction.get('tags', [])).lower()
            
            if query_lower in name:
                score += 0.8
            elif query_lower in description:
                score += 0.6
            elif query_lower in tags:
                score += 0.4
            
            # User profile matching
            if user_profile and user_profile.get('interests'):
                for interest in user_profile['interests']:
                    if interest.lower() in (name + ' ' + description + ' ' + tags):
                        score += 0.3
            
            if score > 0:
                results.append(SearchResult(
                    attraction_id=attraction.get('id', ''),
                    score=score,
                    attraction_data=attraction
                ))
        
        # Sort by score and return top results
        results.sort(key=lambda x: x.score, reverse=True)
        return results[:limit]
    
    async def get_similar_attractions(self, attraction_id: str, limit: int = 10) -> List[SearchResult]:
        # Simple implementation: return random attractions
        results = []
        count = 0
        for attraction in self.attractions_data:
            if attraction.get('id') != attraction_id and count < limit:
                results.append(SearchResult(
                    attraction_id=attraction.get('id', ''),
                    score=0.5,
                    attraction_data=attraction
                ))
                count += 1
        return results
    
    async def get_attractions_by_region(self, region: str, limit: int = 50) -> List[SearchResult]:
        results = []
        for attraction in self.attractions_data:
            if attraction.get('region', '').lower() == region.lower():
                results.append(SearchResult(
                    attraction_id=attraction.get('id', ''),
                    score=1.0,
                    attraction_data=attraction
                ))
        return results[:limit]
