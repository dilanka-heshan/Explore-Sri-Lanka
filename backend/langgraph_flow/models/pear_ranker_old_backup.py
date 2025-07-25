"""
PEAR (Personalized Attraction Ranking) Model Implementation
A neural ranking model that scores attractions based on user preferences
"""

import numpy as np
import torch
import torch.nn as nn
from typing import List, Dict, Any, Tuple
from dataclasses import dataclass
import logging
from sentence_transformers import SentenceTransformer

logger = logging.getLogger(__name__)

@dataclass
class AttractionFeatures:
    """Feature representation of an attraction"""
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
    """Feature representation of user preferences"""
    interests: List[str]
    trip_type: str
    budget_level: str
    cultural_interest: int
    adventure_level: int
    nature_appreciation: int
    age_group: str
    embedding: np.ndarray = None

class PEARModel(nn.Module):
    """
    PEAR Neural Ranking Model
    Takes user and attraction embeddings and outputs relevance score
    """
    
    def __init__(self, embedding_dim: int = 384, hidden_dims: List[int] = [256, 128, 64]):
        super(PEARModel, self).__init__()
        
        self.embedding_dim = embedding_dim
        
        # User preference encoder
        self.user_encoder = nn.Sequential(
            nn.Linear(embedding_dim + 10, hidden_dims[0]),  # +10 for categorical features
            nn.ReLU(),
            nn.Dropout(0.3),
            nn.Linear(hidden_dims[0], hidden_dims[1]),
            nn.ReLU(),
            nn.Dropout(0.2),
        )
        
        # Attraction encoder
        self.attraction_encoder = nn.Sequential(
            nn.Linear(embedding_dim + 8, hidden_dims[0]),  # +8 for categorical features
            nn.ReLU(),
            nn.Dropout(0.3),
            nn.Linear(hidden_dims[0], hidden_dims[1]),
            nn.ReLU(),
            nn.Dropout(0.2),
        )
        
        # Interaction layers
        self.interaction_layer = nn.Sequential(
            nn.Linear(hidden_dims[1] * 2, hidden_dims[2]),
            nn.ReLU(),
            nn.Dropout(0.2),
            nn.Linear(hidden_dims[2], 32),
            nn.ReLU(),
            nn.Linear(32, 1),
            nn.Sigmoid()
        )
        
    def forward(self, user_features: torch.Tensor, attraction_features: torch.Tensor) -> torch.Tensor:
        """
        Forward pass
        Args:
            user_features: [batch_size, embedding_dim + categorical_features]
            attraction_features: [batch_size, embedding_dim + categorical_features]
        Returns:
            relevance_scores: [batch_size, 1]
        """
        user_encoded = self.user_encoder(user_features)
        attraction_encoded = self.attraction_encoder(attraction_features)
        
        # Concatenate encoded features
        combined = torch.cat([user_encoded, attraction_encoded], dim=1)
        
        # Get relevance score
        relevance_score = self.interaction_layer(combined)
        
        return relevance_score

class PEARRanker:
    """
    Main PEAR ranking system that handles feature extraction and ranking
    """
    
    def __init__(self, model_path: str = None, embedding_model_name: str = "sentence-transformers/all-MiniLM-L6-v2"):
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.embedding_model = SentenceTransformer(embedding_model_name)
        self.embedding_dim = self.embedding_model.get_sentence_embedding_dimension()
        
        # Initialize PEAR model
        self.pear_model = PEARModel(embedding_dim=self.embedding_dim)
        
        if model_path:
            try:
                self.pear_model.load_state_dict(torch.load(model_path, map_location=self.device))
                logger.info(f"Loaded PEAR model from {model_path}")
            except Exception as e:
                logger.warning(f"Could not load PEAR model from {model_path}: {e}")
                logger.info("Using untrained model - will use rule-based fallback")
        
        self.pear_model.to(self.device)
        self.pear_model.eval()
        
        # Category mappings for encoding
        self.category_mapping = {
            'cultural': 0, 'nature': 1, 'adventure': 2, 'beach': 3,
            'wildlife': 4, 'historical': 5, 'photography': 6, 'food': 7,
            'spiritual': 8, 'shopping': 9
        }
        
        self.trip_type_mapping = {
            'solo': 0, 'couple': 1, 'family': 2, 'group': 3
        }
        
        self.budget_mapping = {
            'budget': 0, 'mid_range': 1, 'luxury': 2
        }
        
        self.difficulty_mapping = {
            'easy': 0, 'moderate': 1, 'challenging': 2
        }
    
    def extract_user_features(self, user_profile: Dict[str, Any]) -> UserFeatures:
        """Extract and encode user features"""
        
        # Create text representation for embedding
        interests_text = ", ".join(user_profile.get('interests', []))
        user_text = f"Traveler interested in {interests_text}, trip type: {user_profile.get('trip_type', '')}, budget: {user_profile.get('budget_level', '')}"
        
        # Get embedding
        embedding = self.embedding_model.encode(user_text)
        
        return UserFeatures(
            interests=user_profile.get('interests', []),
            trip_type=user_profile.get('trip_type', 'solo'),
            budget_level=user_profile.get('budget_level', 'mid_range'),
            cultural_interest=user_profile.get('cultural_interest_level', 3),
            adventure_level=user_profile.get('adventure_level', 3),
            nature_appreciation=user_profile.get('nature_appreciation', 3),
            age_group=user_profile.get('age_group', 'adult'),
            embedding=embedding
        )
    
    def extract_attraction_features(self, attraction: Dict[str, Any]) -> AttractionFeatures:
        """Extract and encode attraction features"""
        
        # Create text representation for embedding
        tags_text = ", ".join(attraction.get('tags', []))
        facilities_text = ", ".join(attraction.get('facilities', []))
        attraction_text = f"{attraction.get('name', '')} {attraction.get('description', '')} {tags_text} {facilities_text}"
        
        # Get embedding
        embedding = self.embedding_model.encode(attraction_text)
        
        return AttractionFeatures(
            id=attraction.get('id', ''),
            name=attraction.get('name', ''),
            category=attraction.get('category', 'cultural'),
            tags=attraction.get('tags', []),
            rating=float(attraction.get('rating', 0)),
            review_count=int(attraction.get('review_count', 0)),
            entry_fee=float(attraction.get('entry_fee', 0)),
            difficulty_level=attraction.get('difficulty_level', 'easy'),
            visit_duration_minutes=int(attraction.get('visit_duration_minutes', 120)),
            facilities=attraction.get('facilities', []),
            embedding=embedding
        )
    
    def encode_user_features_for_model(self, user_features: UserFeatures) -> np.ndarray:
        """Encode user features for neural model input"""
        
        # One-hot encode categorical features
        interests_vector = np.zeros(len(self.category_mapping))
        for interest in user_features.interests:
            if interest in self.category_mapping:
                interests_vector[self.category_mapping[interest]] = 1
        
        trip_type_vector = np.zeros(len(self.trip_type_mapping))
        if user_features.trip_type in self.trip_type_mapping:
            trip_type_vector[self.trip_type_mapping[user_features.trip_type]] = 1
        
        budget_vector = np.zeros(len(self.budget_mapping))
        if user_features.budget_level in self.budget_mapping:
            budget_vector[self.budget_mapping[user_features.budget_level]] = 1
        
        # Numerical features (normalized)
        numerical_features = np.array([
            user_features.cultural_interest / 5.0,
            user_features.adventure_level / 5.0,
            user_features.nature_appreciation / 5.0
        ])
        
        # Combine all features
        categorical_features = np.concatenate([
            interests_vector[:3],  # Top 3 interest categories
            trip_type_vector,
            budget_vector,
            numerical_features
        ])
        
        return np.concatenate([user_features.embedding, categorical_features])
    
    def encode_attraction_features_for_model(self, attraction_features: AttractionFeatures) -> np.ndarray:
        """Encode attraction features for neural model input"""
        
        # One-hot encode category
        category_vector = np.zeros(len(self.category_mapping))
        if attraction_features.category in self.category_mapping:
            category_vector[self.category_mapping[attraction_features.category]] = 1
        
        # One-hot encode difficulty
        difficulty_vector = np.zeros(len(self.difficulty_mapping))
        if attraction_features.difficulty_level in self.difficulty_mapping:
            difficulty_vector[self.difficulty_mapping[attraction_features.difficulty_level]] = 1
        
        # Numerical features (normalized)
        numerical_features = np.array([
            min(attraction_features.rating / 5.0, 1.0),
            min(attraction_features.review_count / 1000.0, 1.0),  # Normalize review count
            min(attraction_features.entry_fee / 100.0, 1.0),     # Normalize entry fee
            min(attraction_features.visit_duration_minutes / 480.0, 1.0)  # Normalize duration (max 8 hours)
        ])
        
        # Combine features
        categorical_features = np.concatenate([
            category_vector[:3],  # Top 3 categories
            difficulty_vector,
            numerical_features
        ])
        
        return np.concatenate([attraction_features.embedding, categorical_features])
    
    def rule_based_score(self, user_features: UserFeatures, attraction_features: AttractionFeatures) -> float:
        """Fallback rule-based scoring when neural model is not available"""
        
        score = 0.0
        
        # Interest match score
        interest_match = 0
        if attraction_features.category in user_features.interests:
            interest_match = 1.0
        else:
            # Partial match based on related categories
            related_interests = {
                'cultural': ['historical', 'spiritual'],
                'nature': ['wildlife', 'adventure'],
                'adventure': ['nature'],
                'beach': ['nature'],
                'wildlife': ['nature', 'adventure'],
                'historical': ['cultural'],
                'photography': ['nature', 'cultural'],
                'spiritual': ['cultural']
            }
            for interest in user_features.interests:
                if attraction_features.category in related_interests.get(interest, []):
                    interest_match = 0.5
                    break
        
        score += interest_match * 0.4
        
        # Rating score
        rating_score = attraction_features.rating / 5.0
        score += rating_score * 0.3
        
        # Budget compatibility
        budget_score = 1.0
        if user_features.budget_level == 'budget' and attraction_features.entry_fee > 50:
            budget_score = 0.5
        elif user_features.budget_level == 'luxury' and attraction_features.entry_fee < 10:
            budget_score = 0.8  # Luxury travelers might want premium experiences
        
        score += budget_score * 0.2
        
        # Difficulty compatibility
        difficulty_score = 1.0
        if user_features.adventure_level < 3 and attraction_features.difficulty_level == 'challenging':
            difficulty_score = 0.3
        elif user_features.adventure_level > 3 and attraction_features.difficulty_level == 'easy':
            difficulty_score = 0.7
        
        score += difficulty_score * 0.1
        
        return min(score, 1.0)
    
    def rank_attractions(self, user_profile: Dict[str, Any], attractions: List[Dict[str, Any]]) -> List[Tuple[str, float]]:
        """
        Rank attractions based on user preferences
        Returns list of (attraction_id, score) tuples sorted by score descending
        """
        
        if not attractions:
            return []
        
        try:
            # Extract features
            user_features = self.extract_user_features(user_profile)
            attraction_features_list = [self.extract_attraction_features(attr) for attr in attractions]
            
            scores = []
            
            # Use neural model if available, otherwise fallback to rules
            use_neural_model = True
            try:
                # Prepare batch for neural model
                user_tensor_features = self.encode_user_features_for_model(user_features)
                user_batch = np.tile(user_tensor_features, (len(attractions), 1))
                
                attraction_batch = np.array([
                    self.encode_attraction_features_for_model(attr_features)
                    for attr_features in attraction_features_list
                ])
                
                # Convert to tensors
                user_tensor = torch.FloatTensor(user_batch).to(self.device)
                attraction_tensor = torch.FloatTensor(attraction_batch).to(self.device)
                
                # Get predictions
                with torch.no_grad():
                    predictions = self.pear_model(user_tensor, attraction_tensor)
                    scores = predictions.cpu().numpy().flatten().tolist()
                
            except Exception as e:
                logger.warning(f"Neural model failed, using rule-based scoring: {e}")
                use_neural_model = False
            
            if not use_neural_model:
                scores = [
                    self.rule_based_score(user_features, attr_features)
                    for attr_features in attraction_features_list
                ]
                print("Using rule-based scoring for attractions")

            # Create ranked list
            ranked_attractions = [
                (attr_features.id, score)
                for attr_features, score in zip(attraction_features_list, scores)
            ]
            
            # Sort by score descending
            ranked_attractions.sort(key=lambda x: x[1], reverse=True)
            
            logger.info(f"Ranked {len(attractions)} attractions using {'neural' if use_neural_model else 'rule-based'} model")
            
            return ranked_attractions
            
        except Exception as e:
            logger.error(f"Error in ranking attractions: {e}")
            # Return attractions with equal scores as fallback
            return [(attr.get('id', str(i)), 0.5) for i, attr in enumerate(attractions)]

    def get_top_attractions(self, user_profile: Dict[str, Any], attractions: List[Dict[str, Any]], top_k: int = 50) -> List[Dict[str, Any]]:
        """Get top K attractions ranked by PEAR score"""
        
        ranked_attractions = self.rank_attractions(user_profile, attractions)
        top_attraction_ids = [attr_id for attr_id, _ in ranked_attractions[:top_k]]
        
        # Return attractions with their PEAR scores
        attraction_map = {attr.get('id'): attr for attr in attractions}
        score_map = dict(ranked_attractions)
        
        top_attractions = []
        for attr_id in top_attraction_ids:
            if attr_id in attraction_map:
                attraction = attraction_map[attr_id].copy()
                attraction['pear_score'] = score_map[attr_id]
                top_attractions.append(attraction)
        
        return top_attractions
