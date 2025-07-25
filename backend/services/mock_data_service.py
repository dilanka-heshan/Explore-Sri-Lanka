"""
Mock Data Generation Service for Testing
Generates realistic user profiles and travel preferences for testing PEAR model
"""

import random
import uuid
from typing import List, Dict, Any
from datetime import datetime, timedelta
from models.schemas import (
    MockUserProfile, UserInterestSurvey, EnhancedUserProfile,
    InterestType, TripType, BudgetLevel, DifficultyLevel
)

class MockDataGenerator:
    """Generate mock user data for testing and model training"""
    
    def __init__(self):
        self.user_personas = {
            "adventure_seeker": {
                "name_templates": ["Adventure Alex", "Hiking Hannah", "Extreme Eddie"],
                "interests": [InterestType.ADVENTURE, InterestType.NATURE, InterestType.PHOTOGRAPHY],
                "budget_preference": [BudgetLevel.MID_RANGE, BudgetLevel.LUXURY],
                "trip_types": [TripType.SOLO, TripType.COUPLE, TripType.GROUP],
                "preference_scores": {
                    "adventure_level": (0.7, 1.0),
                    "cultural_interest": (0.3, 0.6),
                    "nature_appreciation": (0.8, 1.0),
                    "budget_consciousness": (0.2, 0.7)
                }
            },
            "cultural_explorer": {
                "name_templates": ["Cultural Clara", "History Hunter", "Temple Tom"],
                "interests": [InterestType.CULTURAL, InterestType.HISTORICAL, InterestType.SPIRITUAL],
                "budget_preference": [BudgetLevel.MID_RANGE, BudgetLevel.LUXURY],
                "trip_types": [TripType.COUPLE, TripType.FAMILY],
                "preference_scores": {
                    "adventure_level": (0.2, 0.5),
                    "cultural_interest": (0.8, 1.0),
                    "nature_appreciation": (0.4, 0.7),
                    "budget_consciousness": (0.3, 0.8)
                }
            },
            "beach_lover": {
                "name_templates": ["Beach Bob", "Coastal Kate", "Surf Sam"],
                "interests": [InterestType.BEACH, InterestType.NATURE, InterestType.PHOTOGRAPHY],
                "budget_preference": [BudgetLevel.BUDGET, BudgetLevel.MID_RANGE],
                "trip_types": [TripType.COUPLE, TripType.FAMILY, TripType.GROUP],
                "preference_scores": {
                    "adventure_level": (0.3, 0.6),
                    "cultural_interest": (0.2, 0.5),
                    "nature_appreciation": (0.6, 0.9),
                    "budget_consciousness": (0.4, 0.9)
                }
            },
            "family_traveler": {
                "name_templates": ["Family Fred", "Parent Patty", "Kids & Co"],
                "interests": [InterestType.NATURE, InterestType.CULTURAL, InterestType.BEACH],
                "budget_preference": [BudgetLevel.BUDGET, BudgetLevel.MID_RANGE],
                "trip_types": [TripType.FAMILY],
                "preference_scores": {
                    "adventure_level": (0.2, 0.5),
                    "cultural_interest": (0.5, 0.8),
                    "nature_appreciation": (0.6, 0.9),
                    "budget_consciousness": (0.6, 1.0)
                }
            },
            "luxury_traveler": {
                "name_templates": ["Luxury Lisa", "Premium Pete", "Elite Emma"],
                "interests": [InterestType.CULTURAL, InterestType.FOOD, InterestType.SHOPPING],
                "budget_preference": [BudgetLevel.LUXURY],
                "trip_types": [TripType.COUPLE, TripType.SOLO],
                "preference_scores": {
                    "adventure_level": (0.1, 0.4),
                    "cultural_interest": (0.6, 0.9),
                    "nature_appreciation": (0.3, 0.6),
                    "budget_consciousness": (0.0, 0.3)
                }
            },
            "wildlife_enthusiast": {
                "name_templates": ["Wildlife Will", "Safari Sarah", "Nature Nick"],
                "interests": [InterestType.WILDLIFE, InterestType.NATURE, InterestType.PHOTOGRAPHY],
                "budget_preference": [BudgetLevel.MID_RANGE, BudgetLevel.LUXURY],
                "trip_types": [TripType.SOLO, TripType.COUPLE, TripType.GROUP],
                "preference_scores": {
                    "adventure_level": (0.6, 0.9),
                    "cultural_interest": (0.3, 0.6),
                    "nature_appreciation": (0.9, 1.0),
                    "budget_consciousness": (0.2, 0.6)
                }
            }
        }
        
        self.sri_lanka_destinations = [
            "Sigiriya", "Kandy", "Ella", "Galle", "Anuradhapura", "Polonnaruwa",
            "Nuwara Eliya", "Mirissa", "Yala National Park", "Udawalawe",
            "Dambulla", "Negombo", "Bentota", "Hikkaduwa", "Trincomalee",
            "Arugam Bay", "Pinnawala", "Horton Plains", "Adam's Peak", "Colombo"
        ]
        
        self.activities = [
            "hiking", "temple_visits", "wildlife_safari", "beach_relaxation",
            "train_ride", "historical_sites", "photography", "water_sports",
            "cultural_shows", "food_tours", "shopping", "meditation",
            "rock_climbing", "whale_watching", "surfing", "tea_plantation_tours"
        ]

    def generate_mock_user_profile(self, persona_type: str = None) -> MockUserProfile:
        """Generate a single mock user profile"""
        if persona_type is None:
            persona_type = random.choice(list(self.user_personas.keys()))
        
        persona = self.user_personas[persona_type]
        user_id = f"mock_user_{uuid.uuid4().hex[:8]}"
        
        # Generate trip history
        trip_history = []
        num_trips = random.randint(2, 8)
        for _ in range(num_trips):
            destination = random.choice(self.sri_lanka_destinations)
            rating = random.randint(3, 5) if random.random() > 0.2 else random.randint(1, 2)
            activities = random.sample(self.activities, random.randint(1, 4))
            
            trip_history.append({
                "destination": destination,
                "rating": rating,
                "activities": activities,
                "duration_days": random.randint(1, 7),
                "budget_spent": random.randint(100, 1500),
                "travel_date": (datetime.now() - timedelta(days=random.randint(30, 730))).date().isoformat()
            })
        
        # Generate preference scores
        preference_scores = {}
        for pref, (min_val, max_val) in persona["preference_scores"].items():
            preference_scores[pref] = round(random.uniform(min_val, max_val), 2)
        
        return MockUserProfile(
            user_id=user_id,
            name=random.choice(persona["name_templates"]),
            age_range=random.choice(["18-25", "26-35", "36-50", "50+"]),
            interests=persona["interests"],
            trip_history=trip_history,
            preference_scores=preference_scores,
            budget_range=random.choice(persona["budget_preference"]),
            travel_style={
                "pace": random.choice(["slow", "moderate", "fast"]),
                "group_preference": random.choice(persona["trip_types"]).value,
                "accommodation": random.choice(["hostels", "hotels", "boutique_hotels", "resorts"]),
                "food_adventurousness": round(random.uniform(0.3, 1.0), 2),
                "planning_style": random.choice(["spontaneous", "planned", "semi_planned"])
            }
        )

    def generate_user_interest_survey(self, user_id: str = None) -> UserInterestSurvey:
        """Generate a mock user interest survey response"""
        if user_id is None:
            user_id = f"survey_user_{uuid.uuid4().hex[:8]}"
        
        # Generate realistic survey responses with some correlation
        adventure_interest = random.randint(1, 5)
        nature_interest = max(1, min(5, adventure_interest + random.randint(-2, 2)))
        cultural_interest = random.randint(1, 5)
        
        return UserInterestSurvey(
            user_id=user_id,
            session_id=f"session_{uuid.uuid4().hex[:12]}",
            age_range=random.choice(["18-25", "26-35", "36-50", "50+"]),
            travel_experience=random.choice(["beginner", "intermediate", "expert"]),
            
            # Interest ratings (with some logical correlation)
            cultural_sites_interest=cultural_interest,
            nature_wildlife_interest=nature_interest,
            adventure_sports_interest=adventure_interest,
            beach_relaxation_interest=random.randint(2, 5),
            food_culinary_interest=random.randint(2, 5),
            historical_sites_interest=max(1, min(5, cultural_interest + random.randint(-1, 1))),
            photography_interest=max(1, min(5, nature_interest + random.randint(-1, 2))),
            spiritual_religious_interest=max(1, min(5, cultural_interest + random.randint(-2, 1))),
            shopping_interest=random.randint(1, 4),
            
            # Travel style
            preferred_pace=random.choice(["slow", "moderate", "fast"]),
            accommodation_preference=random.choice(list(BudgetLevel)),
            activity_level=random.choice(["low", "moderate", "high"]),
            
            # Group info
            typical_group_size=random.randint(1, 6),
            mobility_requirements=random.choice([None, "wheelchair_accessible", "limited_walking"]) if random.random() < 0.1 else None,
            dietary_restrictions=random.choice([[], ["vegetarian"], ["halal"], ["gluten_free"]]),
            
            # Travel history
            visited_places=random.sample(self.sri_lanka_destinations, random.randint(1, 5)),
            favorite_destinations=random.sample(self.sri_lanka_destinations, random.randint(0, 3)),
            least_favorite_destinations=random.sample(self.sri_lanka_destinations, random.randint(0, 2))
        )

    def generate_enhanced_user_profile(self, base_profile: MockUserProfile = None) -> EnhancedUserProfile:
        """Generate an enhanced user profile with ML features"""
        if base_profile is None:
            base_profile = self.generate_mock_user_profile()
        
        # Convert MockUserProfile to EnhancedUserProfile
        enhanced = EnhancedUserProfile(
            interests=base_profile.interests,
            trip_type=TripType(base_profile.travel_style["group_preference"]),
            budget_level=base_profile.budget_range,
            age_group=base_profile.age_range,
            preferred_pace=base_profile.travel_style["pace"]
        )
        
        # Add ML-specific features
        enhanced.profile_embedding = [random.uniform(-1, 1) for _ in range(384)]  # Mock embedding
        enhanced.interaction_history = [
            {
                "attraction_id": f"attr_{i}",
                "interaction_type": random.choice(["view", "save", "book", "rate"]),
                "timestamp": (datetime.now() - timedelta(days=random.randint(1, 365))).isoformat(),
                "value": random.randint(1, 5) if random.random() > 0.5 else None
            }
            for i in range(random.randint(10, 50))
        ]
        
        # Seasonal preferences
        enhanced.seasonal_preferences = {
            "dry_season": random.uniform(0.6, 1.0),
            "wet_season": random.uniform(0.2, 0.6),
            "festival_season": random.uniform(0.3, 0.9)
        }
        
        # Time preferences
        enhanced.time_of_day_preferences = {
            "early_morning": random.uniform(0.3, 0.8),
            "morning": random.uniform(0.7, 1.0),
            "afternoon": random.uniform(0.5, 0.9),
            "evening": random.uniform(0.4, 0.8)
        }
        
        return enhanced

    def generate_mock_dataset(self, num_users: int = 50) -> List[MockUserProfile]:
        """Generate a dataset of mock users for training/testing"""
        profiles = []
        
        # Ensure we have representation from all personas
        personas = list(self.user_personas.keys())
        for i in range(num_users):
            persona = personas[i % len(personas)]  # Cycle through personas
            profile = self.generate_mock_user_profile(persona)
            profiles.append(profile)
        
        return profiles

    def generate_training_data_for_pear(self, num_samples: int = 1000) -> List[Dict[str, Any]]:
        """Generate training data specifically for PEAR model"""
        training_data = []
        
        for _ in range(num_samples):
            user_profile = self.generate_enhanced_user_profile()
            
            # Generate mock interactions with attractions
            for interaction in user_profile.interaction_history:
                if interaction.get("value") is not None:  # Has rating
                    training_data.append({
                        "user_id": f"user_{len(training_data)}",
                        "user_interests": [interest.value for interest in user_profile.interests],
                        "user_budget": user_profile.budget_level.value,
                        "user_trip_type": user_profile.trip_type.value,
                        "user_embedding": user_profile.profile_embedding[:10],  # Truncated for example
                        "attraction_id": interaction["attraction_id"],
                        "user_rating": interaction["value"],
                        "interaction_type": interaction["interaction_type"],
                        "seasonal_preference": user_profile.seasonal_preferences.get("dry_season", 0.5)
                    })
        
        return training_data

# Singleton instance
mock_data_generator = MockDataGenerator()
