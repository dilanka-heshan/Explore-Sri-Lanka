"""
Simplified PEAR (Personalized Attraction Ranking) Model Implementation
Pure transformer-based approach with vector database integration
"""

import numpy as np
import torch
import torch.nn as nn
from typing import List, Dict, Any, Tuple, Optional
from dataclasses import dataclass
import logging
from sentence_transformers import SentenceTransformer
from qdrant_client import QdrantClient
from qdrant_client.http import models
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

logger = logging.getLogger(__name__)

@dataclass
class AttractionFeatures:
    """Feature representation of an attraction (kept for compatibility)"""
    id: str
    name: str
    category: str
    tags: List[str]
    rating: float
    review_count: int
    entry_fee: float
    difficulty_level: str
    visit_duration_minutes: int
    facilities: List[str]
    embedding: np.ndarray = None

@dataclass
class UserFeatures:
    """Feature representation of user preferences (kept for compatibility)"""
    interests: List[str]
    trip_type: str
    budget_level: str
    cultural_interest: int
    adventure_level: int
    nature_appreciation: int
    age_group: str
    embedding: np.ndarray = None

class TravelPlaceRanker(nn.Module):
    """
    Lightweight neural ranker for travel places
    Takes: user_query_embedding + user_context_embedding + place_embedding
    Returns: relevance score between 0-1
    """
    def __init__(self, embedding_dim: int, hidden_dim: int = 256):
        super().__init__()
        self.ranker = nn.Sequential(
            nn.Linear(embedding_dim * 3, hidden_dim),  # user_query + user_context + place
            nn.ReLU(),
            nn.Dropout(0.2),
            nn.Linear(hidden_dim, hidden_dim // 2),
            nn.ReLU(), 
            nn.Linear(hidden_dim // 2, 1),  # single relevance score
            nn.Sigmoid()  # score between 0-1
        )
    
    def forward(self, user_query_embed, user_context_embed, place_embed):
        """Forward pass through the ranker"""
        combined = torch.cat([user_query_embed, user_context_embed, place_embed], dim=-1)
        return self.ranker(combined)

class PEARRanker:
    """
    Simplified PEAR ranking system using transformers and vector database
    Replaces the old rule-based complex implementation
    """
    
    def __init__(
        self,
        qdrant_url: Optional[str] = None,
        qdrant_api_key: Optional[str] = None,
        collection_name: str = "exploresl",
        embedding_model_name: str = "all-MiniLM-L6-v2",
        model_path: Optional[str] = None
    ):
        """Initialize the simplified PEAR ranker"""
        
        # Load configuration from environment if not provided
        self.qdrant_url = qdrant_url or os.getenv("QDRANT_HOST", "https://50ab27b1-fac6-42dc-88af-ef70408179e6.us-east-1-0.aws.cloud.qdrant.io")
        self.qdrant_api_key = qdrant_api_key or os.getenv("QDRANT_API_KEY")
        self.collection_name = collection_name or os.getenv("QDRANT_COLLECTION_NAME", "exploresl")
        
        # Initialize embedding model
        self.embedding_model = SentenceTransformer(embedding_model_name)
        self.embedding_dim = self.embedding_model.get_sentence_embedding_dimension()
        
        # Initialize Qdrant client
        if self.qdrant_api_key:
            self.qdrant_client = QdrantClient(
                url=self.qdrant_url,
                api_key=self.qdrant_api_key
            )
            logger.info("Initialized Qdrant client with API key authentication")
        else:
            self.qdrant_client = QdrantClient(url=self.qdrant_url)
            logger.info("Initialized Qdrant client without authentication")
        
        # Initialize neural ranker
        self.neural_ranker = TravelPlaceRanker(embedding_dim=self.embedding_dim)
        
        # Load pre-trained model if available
        if model_path:
            try:
                self.neural_ranker.load_state_dict(torch.load(model_path, map_location="cpu"))
                logger.info(f"Loaded pre-trained ranker from {model_path}")
            except Exception as e:
                logger.warning(f"Could not load model from {model_path}: {e}")
                logger.info("Using randomly initialized ranker")
        
        self.neural_ranker.eval()
        
        # Verify connection
        self._verify_collection()
    
    def _verify_collection(self):
        """Verify that the collection exists in Qdrant"""
        try:
            collection_info = self.qdrant_client.get_collection(self.collection_name)
            logger.info(f"Connected to Qdrant collection '{self.collection_name}' with {collection_info.points_count} places")
        except Exception as e:
            logger.warning(f"Could not connect to Qdrant collection '{self.collection_name}': {e}")
    
    def _create_user_context_from_profile(self, user_profile: Dict[str, Any]) -> str:
        """Convert user profile to context string for embedding"""
        context_parts = []
        
        # Extract interests
        if user_profile.get('interests'):
            interests = ', '.join(user_profile['interests'])
            context_parts.append(f"Interests: {interests}")
        
        # Extract trip type
        if user_profile.get('trip_type'):
            context_parts.append(f"Trip type: {user_profile['trip_type']}")
        
        # Extract budget
        if user_profile.get('budget') or user_profile.get('budget_level'):
            budget = user_profile.get('budget') or user_profile.get('budget_level')
            context_parts.append(f"Budget: {budget}")
        
        # Extract duration
        if user_profile.get('duration'):
            context_parts.append(f"Duration: {user_profile['duration']} days")
        
        # Extract group size
        if user_profile.get('group_size'):
            context_parts.append(f"Group size: {user_profile['group_size']}")
        
        # Extract cultural interest level
        if user_profile.get('cultural_interest'):
            level = user_profile['cultural_interest']
            if level > 7:
                context_parts.append("High cultural interest")
            elif level > 4:
                context_parts.append("Moderate cultural interest")
        
        # Extract adventure level
        if user_profile.get('adventure_level'):
            level = user_profile['adventure_level']
            if level > 7:
                context_parts.append("High adventure preference")
            elif level > 4:
                context_parts.append("Moderate adventure preference")
        
        # Extract nature appreciation
        if user_profile.get('nature_appreciation'):
            level = user_profile['nature_appreciation']
            if level > 7:
                context_parts.append("High nature appreciation")
            elif level > 4:
                context_parts.append("Moderate nature appreciation")
        
        return ". ".join(context_parts) if context_parts else "General travel preferences"
    
    def _create_user_query_from_interests(self, interests: List[str]) -> str:
        """Create a search query from user interests"""
        if not interests:
            return "interesting places to visit in Sri Lanka"
        
        interest_text = " ".join(interests)
        return f"I want to visit places related to {interest_text} in Sri Lanka"
    
    def rank_attractions(self, user_profile: Dict[str, Any], attractions: List[Dict[str, Any]]) -> List[Tuple[str, float]]:
        """
        Rank attractions using the simplified transformer-based approach
        
        Args:
            user_profile: User preferences and profile information
            attractions: List of candidate attractions
            
        Returns:
            List of (attraction_id, score) tuples sorted by score
        """
        try:
            if not attractions:
                return []
            
            # Create user context and query
            user_context_text = self._create_user_context_from_profile(user_profile)
            user_interests = user_profile.get('interests', [])
            user_query_text = self._create_user_query_from_interests(user_interests)
            
            # Create embeddings
            user_query_embed = self.embedding_model.encode(user_query_text)
            user_context_embed = self.embedding_model.encode(user_context_text)
            
            # Convert to tensors
            user_query_tensor = torch.tensor(user_query_embed, dtype=torch.float32).unsqueeze(0)
            user_context_tensor = torch.tensor(user_context_embed, dtype=torch.float32).unsqueeze(0)
            
            ranked_attractions = []
            
            with torch.no_grad():
                for attraction in attractions:
                    try:
                        # Create attraction text for embedding
                        attraction_text = self._create_attraction_text(attraction)
                        attraction_embed = self.embedding_model.encode(attraction_text)
                        attraction_tensor = torch.tensor(attraction_embed, dtype=torch.float32).unsqueeze(0)
                        
                        # Get neural ranking score
                        neural_score = self.neural_ranker(
                            user_query_tensor,
                            user_context_tensor,
                            attraction_tensor
                        ).item()
                        
                        # Use attraction ID or name as identifier
                        attraction_id = attraction.get('id') or attraction.get('name', str(len(ranked_attractions)))
                        
                        ranked_attractions.append((attraction_id, neural_score))
                        
                    except Exception as e:
                        logger.warning(f"Error ranking attraction {attraction.get('name', 'Unknown')}: {e}")
                        # Add with default score
                        attraction_id = attraction.get('id') or attraction.get('name', str(len(ranked_attractions)))
                        ranked_attractions.append((attraction_id, 0.5))
            
            # Sort by score (descending)
            ranked_attractions.sort(key=lambda x: x[1], reverse=True)
            
            logger.info(f"Successfully ranked {len(ranked_attractions)} attractions")
            return ranked_attractions
            
        except Exception as e:
            logger.error(f"Error in ranking attractions: {e}")
            # Return attractions with equal scores as fallback
            return [(attr.get('id', str(i)), 0.5) for i, attr in enumerate(attractions)]
    
    def _create_attraction_text(self, attraction: Dict[str, Any]) -> str:
        """Create text representation of an attraction for embedding"""
        text_parts = []
        
        # Name
        if attraction.get('name'):
            text_parts.append(f"Name: {attraction['name']}")
        
        # Category
        if attraction.get('category'):
            text_parts.append(f"Category: {attraction['category']}")
        
        # Description
        if attraction.get('description'):
            text_parts.append(f"Description: {attraction['description']}")
        
        # Tags
        if attraction.get('tags'):
            tags = ', '.join(attraction['tags']) if isinstance(attraction['tags'], list) else attraction['tags']
            text_parts.append(f"Tags: {tags}")
        
        # Location/Region
        if attraction.get('region'):
            text_parts.append(f"Region: {attraction['region']}")
        
        # Facilities
        if attraction.get('facilities'):
            facilities = ', '.join(attraction['facilities']) if isinstance(attraction['facilities'], list) else attraction['facilities']
            text_parts.append(f"Facilities: {facilities}")
        
        return ". ".join(text_parts) if text_parts else attraction.get('name', 'Unknown attraction')
    
    def get_top_attractions(self, user_profile: Dict[str, Any], attractions: List[Dict[str, Any]], top_k: int = 50) -> List[Dict[str, Any]]:
        """
        Get top K attractions ranked by simplified PEAR score
        
        This method maintains compatibility with the existing API
        """
        try:
            ranked_attractions = self.rank_attractions(user_profile, attractions)
            top_attraction_ids = [attr_id for attr_id, _ in ranked_attractions[:top_k]]
            
            # Return attractions with their PEAR scores
            attraction_map = {attr.get('id', attr.get('name')): attr for attr in attractions}
            score_map = dict(ranked_attractions)
            
            top_attractions = []
            for attr_id in top_attraction_ids:
                if attr_id in attraction_map:
                    attraction = attraction_map[attr_id].copy()
                    attraction['pear_score'] = score_map[attr_id]
                    top_attractions.append(attraction)
                else:
                    # Try to find by name if ID doesn't match
                    for attr in attractions:
                        if attr.get('name') == attr_id or attr.get('id') == attr_id:
                            attraction = attr.copy()
                            attraction['pear_score'] = score_map[attr_id]
                            top_attractions.append(attraction)
                            break
            
            logger.info(f"Returning {len(top_attractions)} top attractions")
            return top_attractions
            
        except Exception as e:
            logger.error(f"Error in get_top_attractions: {e}")
            # Return original attractions with default scores as fallback
            return [dict(attr, pear_score=0.5) for attr in attractions[:top_k]]
    
    def get_recommendations_from_vector_db(
        self,
        user_query: str,
        user_context: Dict[str, Any],
        top_k: int = 30,
        vector_search_limit: int = 100
    ) -> List[Dict[str, Any]]:
        """
        Get recommendations directly from vector database (new functionality)
        This bypasses the traditional candidate attraction filtering
        """
        try:
            # Convert user query to embedding
            user_query_embed = self.embedding_model.encode(user_query)
            
            # Vector database similarity search
            search_result = self.qdrant_client.search(
                collection_name=self.collection_name,
                query_vector=user_query_embed.tolist(),
                limit=vector_search_limit,
                with_payload=True,
                with_vectors=True
            )
            
            if not search_result:
                logger.warning("No results found in vector search")
                return []
            
            logger.info(f"Retrieved {len(search_result)} candidates from vector database")
            
            # Apply neural ranking
            user_context_text = self._create_user_context_from_profile(user_context)
            user_context_embed = self.embedding_model.encode(user_context_text)
            
            user_query_tensor = torch.tensor(user_query_embed, dtype=torch.float32).unsqueeze(0)
            user_context_tensor = torch.tensor(user_context_embed, dtype=torch.float32).unsqueeze(0)
            
            ranked_places = []
            
            with torch.no_grad():
                for result in search_result:
                    # Get place embedding from vector search result
                    place_embed = np.array(result.vector)
                    place_embed_tensor = torch.tensor(place_embed, dtype=torch.float32).unsqueeze(0)
                    
                    # Get neural ranking score
                    neural_score = self.neural_ranker(
                        user_query_tensor, 
                        user_context_tensor, 
                        place_embed_tensor
                    ).item()
                    
                    # Combine with place information
                    place_info = {
                        'id': result.id,
                        'payload': result.payload,
                        'neural_score': neural_score,
                        'similarity_score': result.score,
                        'pear_score': (neural_score * 0.7) + (result.score * 0.3),  # Combined score
                        'name': result.payload.get('name', 'Unknown') if result.payload else 'Unknown',
                        'category': result.payload.get('category', 'Unknown') if result.payload else 'Unknown',
                        'description': result.payload.get('description', '') if result.payload else '',
                        'region': result.payload.get('region', 'Unknown') if result.payload else 'Unknown'
                    }
                    
                    ranked_places.append(place_info)
            
            # Sort by combined score and return top K
            ranked_places.sort(key=lambda x: x['pear_score'], reverse=True)
            
            logger.info(f"Returning top {top_k} recommendations from vector database")
            return ranked_places[:top_k]
            
        except Exception as e:
            logger.error(f"Error in get_recommendations_from_vector_db: {e}")
            return []

# Legacy class for compatibility (will be removed in future versions)
class PEARModel(nn.Module):
    """Legacy PEAR model - deprecated, use TravelPlaceRanker instead"""
    def __init__(self, *args, **kwargs):
        super().__init__()
        logger.warning("PEARModel is deprecated. Use TravelPlaceRanker instead.")
        
    def forward(self, x):
        return torch.zeros(x.shape[0], 1)

# Factory function for easy initialization
def create_pear_ranker(**kwargs) -> PEARRanker:
    """Factory function to create a PEARRanker instance"""
    return PEARRanker(**kwargs)
