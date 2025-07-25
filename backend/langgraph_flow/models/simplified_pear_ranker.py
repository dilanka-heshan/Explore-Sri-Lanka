"""
Simplified PEAR Ranker for Travel Place Recommendations
Pure transformer-based approach with vector database integration
"""

import torch
import torch.nn as nn
from sentence_transformers import SentenceTransformer
import numpy as np
from typing import List, Dict, Any, Optional
import logging
from qdrant_client import QdrantClient
from qdrant_client.http import models
from qdrant_client.http.models import Distance, VectorParams

logger = logging.getLogger(__name__)

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

class SimplifiedPEARRanker:
    """
    Simplified PEAR ranking system following your vision:
    1. User Query → Embedding
    2. Vector DB Similarity Search  
    3. Neural Ranking
    4. Top K Results
    """
    
    def __init__(
        self,
        qdrant_url: str = "https://50ab27b1-fac6-42dc-88af-ef70408179e6.us-east-1-0.aws.cloud.qdrant.io",
        qdrant_api_key: Optional[str] = None,
        collection_name: str = "travel_places",
        embedding_model_name: str = "all-MiniLM-L6-v2",
        model_path: Optional[str] = None
    ):
        # Initialize embedding model
        self.embedding_model = SentenceTransformer(embedding_model_name)
        self.embedding_dim = self.embedding_model.get_sentence_embedding_dimension()
        
        # Initialize Qdrant client with API key for cloud instances
        if qdrant_api_key:
            self.qdrant_client = QdrantClient(
                url=qdrant_url,
                api_key=qdrant_api_key
            )
            logger.info("Initialized Qdrant client with API key authentication")
        else:
            self.qdrant_client = QdrantClient(url=qdrant_url)
            logger.info("Initialized Qdrant client without authentication")
            
        self.collection_name = collection_name
        
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
        
        # Verify vector database connection
        self._verify_collection()
    
    def _verify_collection(self):
        """Verify that the collection exists in Qdrant"""
        try:
            collection_info = self.qdrant_client.get_collection(self.collection_name)
            logger.info(f"Connected to Qdrant collection '{self.collection_name}' with {collection_info.points_count} places")
        except Exception as e:
            logger.error(f"Failed to connect to Qdrant collection '{self.collection_name}': {e}")
            raise
    
    def _create_user_context_embedding(self, user_context: Dict[str, Any]) -> np.ndarray:
        """Create embedding from user context information"""
        context_parts = []
        
        if user_context.get('trip_type'):
            context_parts.append(f"Trip type: {user_context['trip_type']}")
        
        if user_context.get('budget'):
            context_parts.append(f"Budget: {user_context['budget']}")
        
        if user_context.get('interests'):
            interests = ', '.join(user_context['interests'])
            context_parts.append(f"Interests: {interests}")
        
        if user_context.get('duration'):
            context_parts.append(f"Duration: {user_context['duration']} days")
        
        if user_context.get('group_size'):
            context_parts.append(f"Group size: {user_context['group_size']}")
        
        context_text = ". ".join(context_parts) if context_parts else "General travel preferences"
        return self.embedding_model.encode(context_text)
    
    def get_recommendations(
        self,
        user_query: str,
        user_context: Dict[str, Any],
        top_k: int = 30,
        vector_search_limit: int = 100
    ) -> List[Dict[str, Any]]:
        """
        Get travel place recommendations based on user query and context
        
        Args:
            user_query: Natural language description of what user wants
            user_context: Dictionary with trip_type, budget, interests, etc.
            top_k: Number of final recommendations to return
            vector_search_limit: Number of candidates to retrieve from vector DB
            
        Returns:
            List of recommended places with scores
        """
        try:
            # Step 1: Convert user query to embedding
            user_query_embed = self.embedding_model.encode(user_query)
            
            # Step 2: Create user context embedding
            user_context_embed = self._create_user_context_embedding(user_context)
            
            # Step 3: Vector database similarity search
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
            
            # Step 4: Neural ranking of retrieved candidates
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
                        'combined_score': (neural_score * 0.7) + (result.score * 0.3)  # Weighted combination
                    }
                    
                    ranked_places.append(place_info)
            
            # Step 5: Sort by neural ranking score and return top K
            ranked_places.sort(key=lambda x: x['combined_score'], reverse=True)
            
            logger.info(f"Returning top {top_k} recommendations")
            return ranked_places[:top_k]
            
        except Exception as e:
            logger.error(f"Error in get_recommendations: {e}")
            return []
    
    def search_by_category(
        self,
        user_query: str,
        user_context: Dict[str, Any],
        category_filter: str,
        top_k: int = 20
    ) -> List[Dict[str, Any]]:
        """
        Search for places with category filtering
        """
        try:
            user_query_embed = self.embedding_model.encode(user_query)
            
            # Search with category filter
            search_result = self.qdrant_client.search(
                collection_name=self.collection_name,
                query_vector=user_query_embed.tolist(),
                query_filter=models.Filter(
                    must=[
                        models.FieldCondition(
                            key="category",
                            match=models.MatchValue(value=category_filter)
                        )
                    ]
                ),
                limit=top_k * 2,  # Get more candidates for ranking
                with_payload=True,
                with_vectors=True
            )
            
            # Apply neural ranking
            return self._rank_search_results(user_query, user_context, search_result, top_k)
            
        except Exception as e:
            logger.error(f"Error in search_by_category: {e}")
            return []
    
    def search_by_region(
        self,
        user_query: str,
        user_context: Dict[str, Any],
        region_filter: str,
        top_k: int = 20
    ) -> List[Dict[str, Any]]:
        """
        Search for places with region filtering
        """
        try:
            user_query_embed = self.embedding_model.encode(user_query)
            
            # Search with region filter
            search_result = self.qdrant_client.search(
                collection_name=self.collection_name,
                query_vector=user_query_embed.tolist(),
                query_filter=models.Filter(
                    must=[
                        models.FieldCondition(
                            key="region",
                            match=models.MatchValue(value=region_filter)
                        )
                    ]
                ),
                limit=top_k * 2,
                with_payload=True,
                with_vectors=True
            )
            
            # Apply neural ranking
            return self._rank_search_results(user_query, user_context, search_result, top_k)
            
        except Exception as e:
            logger.error(f"Error in search_by_region: {e}")
            return []
    
    def _rank_search_results(
        self,
        user_query: str,
        user_context: Dict[str, Any],
        search_results: List,
        top_k: int
    ) -> List[Dict[str, Any]]:
        """Helper method to rank search results with neural network"""
        user_query_embed = self.embedding_model.encode(user_query)
        user_context_embed = self._create_user_context_embedding(user_context)
        
        user_query_tensor = torch.tensor(user_query_embed, dtype=torch.float32).unsqueeze(0)
        user_context_tensor = torch.tensor(user_context_embed, dtype=torch.float32).unsqueeze(0)
        
        ranked_places = []
        
        with torch.no_grad():
            for result in search_results:
                place_embed = np.array(result.vector)
                place_embed_tensor = torch.tensor(place_embed, dtype=torch.float32).unsqueeze(0)
                
                neural_score = self.neural_ranker(
                    user_query_tensor, 
                    user_context_tensor, 
                    place_embed_tensor
                ).item()
                
                place_info = {
                    'id': result.id,
                    'payload': result.payload,
                    'neural_score': neural_score,
                    'similarity_score': result.score,
                    'combined_score': (neural_score * 0.7) + (result.score * 0.3)
                }
                
                ranked_places.append(place_info)
        
        ranked_places.sort(key=lambda x: x['combined_score'], reverse=True)
        return ranked_places[:top_k]
    
    def get_similar_places(self, place_id: str, top_k: int = 10) -> List[Dict[str, Any]]:
        """
        Find places similar to a given place
        """
        try:
            # Get the place vector
            place_data = self.qdrant_client.retrieve(
                collection_name=self.collection_name,
                ids=[place_id],
                with_vectors=True
            )
            
            if not place_data:
                logger.warning(f"Place with id {place_id} not found")
                return []
            
            place_vector = place_data[0].vector
            
            # Search for similar places
            search_result = self.qdrant_client.search(
                collection_name=self.collection_name,
                query_vector=place_vector,
                limit=top_k + 1,  # +1 to exclude the original place
                with_payload=True
            )
            
            # Filter out the original place
            similar_places = [
                {
                    'id': result.id,
                    'payload': result.payload,
                    'similarity_score': result.score
                }
                for result in search_result
                if result.id != place_id
            ]
            
            return similar_places[:top_k]
            
        except Exception as e:
            logger.error(f"Error in get_similar_places: {e}")
            return []

# Factory function for easy initialization
def create_travel_ranker(
    qdrant_url: str = "http://localhost:6333",
    qdrant_api_key: Optional[str] = None,
    collection_name: str = "travel_places",
    model_path: Optional[str] = None
) -> SimplifiedPEARRanker:
    """
    Factory function to create a SimplifiedPEARRanker instance
    """
    # Load API key from environment if not provided
    if qdrant_api_key is None:
        import os
        qdrant_api_key = os.getenv("QDRANT_API_KEY")
        
    return SimplifiedPEARRanker(
        qdrant_url=qdrant_url,
        qdrant_api_key=qdrant_api_key,
        collection_name=collection_name,
        model_path=model_path
    )
