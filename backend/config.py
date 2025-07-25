import os
from typing import Dict, Any
from dataclasses import dataclass

# Load environment variables
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

@dataclass
class Settings:
    # API Keys (Temporary - Replace with actual keys)
    GOOGLE_GEMINI_API_KEY: str = os.getenv("GOOGLE_GEMINI_API_KEY", "AIzaSyDtEm0pOrArYk3qB5xV7nW8mJ2fL1cP9Qs_TEMP")
    OPENROUTE_SERVICE_API_KEY: str = os.getenv("OPENROUTE_SERVICE_API_KEY", "5b3ce3597851110001cf6248temp1234567890abcdef")
    GOOGLE_MAPS_API_KEY: str = os.getenv("GOOGLE_MAPS_API_KEY", "AIzaSyBtEm0pOrArYk3qB5xV7nW8mJ2fL1cP9Qt_TEMP")
    
    # Qdrant Configuration
    QDRANT_HOST: str = os.getenv("QDRANT_HOST", "localhost")
    QDRANT_PORT: int = int(os.getenv("QDRANT_PORT", "6333"))
    QDRANT_API_KEY: str = os.getenv("QDRANT_API_KEY", "")
    QDRANT_COLLECTION_NAME: str = os.getenv("QDRANT_COLLECTION_NAME", "sri_lanka_attractions")
    QDRANT_USE_MOCK: bool = os.getenv("USE_MOCK_VECTOR_DB", "true").lower() == "true"
    
    # Database Configuration
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./sri_lanka.db")
    
    # Planning Configuration
    DEFAULT_DAILY_HOURS: int = 9  # 9 AM to 6 PM
    MIN_CLUSTER_RADIUS_KM: float = 2.0  # Minimum cluster radius
    MAX_CLUSTER_RADIUS_KM: float = 15.0  # Maximum cluster radius
    INTRA_CLUSTER_MAX_DISTANCE_KM: float = 3.0  # Max distance within cluster
    INTER_CLUSTER_MIN_DISTANCE_KM: float = 8.0  # Min distance between clusters
    MAX_ATTRACTIONS_PER_CLUSTER: int = 8
    
    # Travel Time Configuration - Using actual dataset values
    USE_DATASET_VISIT_TIMES: bool = True  # Use times from dataset
    DEFAULT_VISIT_TIME_MINUTES: int = 120  # Fallback if not in dataset
    
    # PEAR Model Configuration
    EMBEDDING_MODEL: str = "sentence-transformers/all-MiniLM-L6-v2"
    PEAR_MODEL_DIM: int = 384
    
    def __post_init__(self):
        if self.DEFAULT_VISIT_TIME_MINUTES is None:
            self.DEFAULT_VISIT_TIME_MINUTES = {
                "Cultural": 90,
                "Historical": 120,
                "Nature": 180,
                "Beach": 240,
                "Wildlife": 300,
                "Adventure": 360
            }

settings = Settings()

# Travel Planning Constants
PLANNING_CONFIG = {
    "clustering": {
        "algorithm": "DBSCAN",
        "eps_km": settings.MAX_CLUSTER_RADIUS_KM,
        "min_samples": 2
    },
    "optimization": {
        "max_iterations": 1000,
        "time_buffer_minutes": 30
    },
    "scoring": {
        "interest_weight": 0.4,
        "rating_weight": 0.3,
        "time_efficiency_weight": 0.3
    }
}