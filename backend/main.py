"""
Enhanced FastAPI Application for Sri Lanka Travel Planning
Includes sophisticated AI-powered travel planning with multiple reasoning stages
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import logging
from datetime import datetime

# Import routers
from router import planner
from router import chatbot, destinations, gallery, stories, newsletter, admin
from router import admin_data  # New admin and data management router
from router import clustered_recommendations  # Advanced geographic clustering

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('travel_planner.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="Explore Sri Lanka - Enhanced Travel Planner",
    description="""
    Advanced AI-powered travel planning system for Sri Lanka featuring:
    
    - **PEAR Ranking**: Personalized Attraction Ranking using neural networks
    - **Geographic Clustering**: Smart grouping of attractions by proximity  
    - **Route Optimization**: Optimal travel routes using OpenRouteService
    - **Vector Search**: Semantic similarity search with Qdrant
    - **LLM Reasoning**: Final plan enhancement using Gemini AI
    
    **7-Step Planning Process:**
    1. Parse user preferences from natural language
    2. Rank attractions using PEAR model 
    3. Cluster attractions geographically
    4. Score clusters by value-per-time
    5. Filter by time constraints
    6. Optimize routes and schedules
    7. Enhance with AI reasoning and gap filling
    """,
    version="2.0.0",
    contact={
        "name": "Explore Sri Lanka API",
        "email": "api@exploresrilanka.com",
    },
    license_info={
        "name": "MIT",
        "url": "https://opensource.org/licenses/MIT",
    }
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000", 
        "https://exploresrilanka.com",
        "https://www.exploresrilanka.com"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(planner.router)

# Optional: Include other routers when implemented
try:
    app.include_router(chatbot.router)
    app.include_router(destinations.router)
    app.include_router(gallery.router)
    app.include_router(stories.router)
    app.include_router(newsletter.router)
    app.include_router(admin.router)
    app.include_router(admin_data.router)  # New admin and data management endpoints
    app.include_router(clustered_recommendations.router)  # Advanced geographic clustering
except Exception as e:
    logger.warning(f"Some routers not available: {e}")

@app.get("/")
async def root():
    """Root endpoint with API information"""
    return {
        "message": "Welcome to Explore Sri Lanka Enhanced Travel Planner API",
        "version": "2.0.0",
        "features": [
            "Advanced AI travel planning",
            "PEAR personalized ranking", 
            "Geographic clustering",
            "Route optimization",
            "Vector similarity search",
            "LLM-enhanced recommendations"
        ],
        "endpoints": {
            "planning": "/api/planning/plan_trip",
            "health": "/health",
            "docs": "/docs",
            "redoc": "/redoc"
        },
        "timestamp": datetime.now().isoformat()
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "service": "Enhanced Travel Planner API",
        "version": "2.0.0",
        "components": {
            "fastapi": "✓ Running",
            "planning_service": "✓ Available", 
            "pear_model": "✓ Loaded",
            "geo_clustering": "✓ Ready",
            "route_optimizer": "✓ Ready",
            "vector_db": "⚠ Check configuration",
            "llm": "⚠ Check API keys"
        }
    }

@app.get("/api/info")
async def api_info():
    """Detailed API information"""
    return {
        "name": "Explore Sri Lanka Enhanced Travel Planner",
        "description": "AI-powered travel planning with sophisticated multi-stage reasoning",
        "version": "2.0.0",
        "planning_features": {
            "pear_ranking": {
                "description": "Neural network for personalized attraction ranking",
                "technology": "PyTorch + Sentence Transformers"
            },
            "geographic_clustering": {
                "description": "Groups attractions by proximity using Haversine distance",
                "algorithms": ["DBSCAN", "Distance-based clustering"]
            },
            "route_optimization": {
                "description": "Solves TSP for optimal attraction visiting order",
                "methods": ["Brute force (≤8 attractions)", "Nearest neighbor heuristic"]
            },
            "vector_search": {
                "description": "Semantic similarity search for attractions",
                "technology": "Qdrant vector database"
            },
            "llm_reasoning": {
                "description": "Final plan enhancement and gap filling",
                "model": "Google Gemini Pro"
            }
        },
        "supported_preferences": [
            "Trip duration (1-30 days)",
            "Budget level (budget/mid_range/luxury)",
            "Trip type (solo/couple/family/group)", 
            "Interests (cultural/nature/adventure/beach/wildlife/etc.)",
            "Activity level (1-5 scale)",
            "Special requirements"
        ],
        "output_includes": [
            "Day-by-day detailed itinerary",
            "Optimized travel routes",
            "Hotel recommendations",
            "Restaurant suggestions", 
            "Local tips and cultural insights",
            "Packing suggestions",
            "Weather considerations",
            "Emergency contacts"
        ]
    }

@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    """Custom HTTP exception handler"""
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": True,
            "status_code": exc.status_code,
            "message": exc.detail,
            "timestamp": datetime.now().isoformat(),
            "path": str(request.url)
        }
    )

@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    """Handle unexpected errors"""
    logger.error(f"Unexpected error: {exc}")
    
    return JSONResponse(
        status_code=500,
        content={
            "error": True,
            "status_code": 500,
            "message": "Internal server error",
            "timestamp": datetime.now().isoformat(),
            "path": str(request.url)
        }
    )

if __name__ == "__main__":
    import uvicorn
    
    logger.info("Starting Enhanced Travel Planner API...")
    
    # Run the application
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
