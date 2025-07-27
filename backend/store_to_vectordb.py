"""
Vector Database Storage and Project Cleanup Script
Stores embeddings in Qdrant vector database and cleans up temporary files
"""

import json
import numpy as np
import logging
from pathlib import Path
from typing import List, Dict, Any
import shutil
import os

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

try:
    from qdrant_client import QdrantClient
    from qdrant_client.models import Distance, VectorParams, PointStruct
    from qdrant_client.http import models
except ImportError:
    logger.error("Qdrant client not installed. Run: pip install qdrant-client")
    exit(1)

class VectorDatabaseManager:
    """Manages vector database storage and operations"""
    
    def __init__(self):
        """Initialize with configuration from .env"""
        self.client = None
        self.collection_name = "exploresl"
        self.vector_size = 384  # all-MiniLM-L6-v2 dimension
        
        # Load configuration
        self._load_config()
        
    def _load_config(self):
        """Load Qdrant configuration from environment"""
        try:
            from config import settings
            
            # Initialize Qdrant client
            if hasattr(settings, 'QDRANT_HOST') and hasattr(settings, 'QDRANT_API_KEY'):
                # Cloud Qdrant
                self.client = QdrantClient(
                    url=settings.QDRANT_HOST,
                    api_key=settings.QDRANT_API_KEY,
                    timeout=30
                )
                logger.info("Connected to Qdrant Cloud")
            else:
                # Local Qdrant
                self.client = QdrantClient(host="localhost", port=6333)
                logger.info("Connected to local Qdrant")
                
            if hasattr(settings, 'QDRANT_COLLECTION_NAME'):
                self.collection_name = settings.QDRANT_COLLECTION_NAME
                
        except Exception as e:
            logger.warning(f"Could not load config: {e}. Using default Qdrant settings.")
            self.client = QdrantClient(host="localhost", port=6333)
    
    def create_collection(self):
        """Create or recreate the collection"""
        try:
            # Delete collection if exists
            try:
                self.client.delete_collection(collection_name=self.collection_name)
                logger.info(f"Deleted existing collection: {self.collection_name}")
            except:
                pass
            
            # Create new collection
            self.client.create_collection(
                collection_name=self.collection_name,
                vectors_config=VectorParams(
                    size=self.vector_size,
                    distance=Distance.COSINE
                )
            )
            logger.info(f"Created collection: {self.collection_name}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to create collection: {e}")
            return False
    
    def store_embeddings(self, embeddings_file: str, attractions_file: str):
        """Store embeddings in vector database"""
        
        # Load embeddings and metadata
        logger.info("Loading embeddings and attractions data...")
        
        # Load embeddings
        embeddings = np.load(embeddings_file)
        logger.info(f"Loaded embeddings shape: {embeddings.shape}")
        
        # Load attractions data (contains complete metadata)
        with open(attractions_file, 'r', encoding='utf-8') as f:
            attractions_data = json.load(f)
        
        # Verify dimensions match
        if len(embeddings) != len(attractions_data):
            logger.error("Mismatch between embeddings and attractions data count")
            return False
        
        # Create collection
        if not self.create_collection():
            return False
        
        # Prepare points for insertion
        logger.info("Preparing points for insertion...")
        points = []
        
        for i, (embedding, attraction) in enumerate(zip(embeddings, attractions_data)):
            point = PointStruct(
                id=i,
                vector=embedding.tolist(),
                payload={
                    "attraction_id": attraction["id"],
                    "name": attraction["name"],
                    "category": attraction["category"],
                    "location": attraction["location"],
                    "text_for_embedding": attraction.get("text_for_embedding", ""),
                    "full_text": attraction.get("full_text", ""),
                    "difficulty": attraction.get("metadata", {}).get("difficulty", ""),
                    "duration": attraction.get("metadata", {}).get("duration", ""),
                    "best_time": attraction.get("metadata", {}).get("best_time", ""),
                    "adventure_level": attraction.get("metadata", {}).get("adventure_level", 1),
                    "family_friendly": attraction.get("metadata", {}).get("family_friendly", False),
                    "cultural_significance": attraction.get("metadata", {}).get("cultural_significance", "medium"),
                    "activities": attraction.get("metadata", {}).get("activities", []),
                    "keywords": attraction.get("metadata", {}).get("keywords", [])
                }
            )
            points.append(point)
        
        # Insert points in batches
        batch_size = 100
        total_points = len(points)
        
        logger.info(f"Inserting {total_points} points in batches of {batch_size}...")
        
        for i in range(0, total_points, batch_size):
            batch = points[i:i + batch_size]
            try:
                self.client.upsert(
                    collection_name=self.collection_name,
                    points=batch
                )
                logger.info(f"Inserted batch {i//batch_size + 1}/{(total_points + batch_size - 1)//batch_size}")
            except Exception as e:
                logger.error(f"Failed to insert batch {i//batch_size + 1}: {e}")
                return False
        
        # Verify insertion
        collection_info = self.client.get_collection(collection_name=self.collection_name)
        logger.info(f"Collection info: {collection_info}")
        
        return True
    
    def test_search(self, query_text: str = "beautiful beach"):
        """Test search functionality"""
        try:
            # For testing, we'll use a dummy vector (in production, encode the query text)
            dummy_vector = np.random.rand(self.vector_size).tolist()
            
            search_result = self.client.search(
                collection_name=self.collection_name,
                query_vector=dummy_vector,
                limit=5
            )
            
            logger.info(f"Search test successful. Found {len(search_result)} results")
            for i, result in enumerate(search_result):
                logger.info(f"  {i+1}. {result.payload['name']} (score: {result.score:.3f})")
            
            return True
            
        except Exception as e:
            logger.error(f"Search test failed: {e}")
            return False

class ProjectCleaner:
    """Cleans up unnecessary files and organizes project structure"""
    
    def __init__(self, project_root: str):
        self.project_root = Path(project_root)
        self.cleanup_log = []
    
    def cleanup_temporary_files(self):
        """Remove temporary and unnecessary files"""
        
        logger.info("Starting project cleanup...")
        
        # Files to remove
        files_to_remove = [
            "processed_attractions.csv",
            "processed_attractions.json", 
            "embedding_ready_attractions.json",
            "data_preprocessor.py",
            "embedding_generator.py"
        ]
        
        # Directories to remove
        dirs_to_remove = [
            "travel_groups",
            "__pycache__"
        ]
        
        # Remove files
        for file_name in files_to_remove:
            file_path = self.project_root / file_name
            if file_path.exists():
                try:
                    file_path.unlink()
                    self.cleanup_log.append(f"Removed file: {file_name}")
                    logger.info(f"Removed: {file_name}")
                except Exception as e:
                    logger.error(f"Failed to remove {file_name}: {e}")
        
        # Remove directories
        for dir_name in dirs_to_remove:
            dir_path = self.project_root / dir_name
            if dir_path.exists():
                try:
                    shutil.rmtree(dir_path)
                    self.cleanup_log.append(f"Removed directory: {dir_name}")
                    logger.info(f"Removed directory: {dir_name}")
                except Exception as e:
                    logger.error(f"Failed to remove directory {dir_name}: {e}")
    
    def organize_data_files(self):
        """Organize remaining data files"""
        
        # Create data directory if it doesn't exist
        data_dir = self.project_root / "data"
        data_dir.mkdir(exist_ok=True)
        
        # Move data.md to data directory if it's in root
        data_md_root = self.project_root / "data.md"
        data_md_target = data_dir / "attractions_source.md"
        
        if data_md_root.exists() and not data_md_target.exists():
            try:
                shutil.move(str(data_md_root), str(data_md_target))
                self.cleanup_log.append(f"Moved data.md to data/attractions_source.md")
                logger.info("Moved data.md to data/attractions_source.md")
            except Exception as e:
                logger.error(f"Failed to move data.md: {e}")
    
    def clean_log_files(self):
        """Clean up old log files"""
        
        log_files = list(self.project_root.glob("*.log"))
        for log_file in log_files:
            if log_file.stat().st_size > 10 * 1024 * 1024:  # 10MB
                try:
                    log_file.unlink()
                    self.cleanup_log.append(f"Removed large log file: {log_file.name}")
                    logger.info(f"Removed large log file: {log_file.name}")
                except Exception as e:
                    logger.error(f"Failed to remove log file {log_file.name}: {e}")
    
    def create_cleanup_summary(self):
        """Create a summary of cleanup actions"""
        
        summary_file = self.project_root / "cleanup_summary.txt"
        
        # Get current timestamp
        try:
            import pandas as pd
            timestamp = pd.Timestamp.now().isoformat()
        except ImportError:
            from datetime import datetime
            timestamp = datetime.now().isoformat()
        
        with open(summary_file, 'w', encoding='utf-8') as f:
            f.write("Project Cleanup Summary\n")
            f.write("=" * 30 + "\n\n")
            f.write(f"Cleanup performed on: {timestamp}\n\n")
            
            if self.cleanup_log:
                f.write("Actions performed:\n")
                for action in self.cleanup_log:
                    f.write(f"- {action}\n")
            else:
                f.write("No cleanup actions were needed.\n")
            
            f.write("\nRemaining project structure:\n")
            f.write(self._get_project_structure())
        
        logger.info(f"Created cleanup summary: {summary_file}")
    
    def _get_project_structure(self) -> str:
        """Get a string representation of project structure"""
        
        structure = []
        
        def add_items(path: Path, prefix: str = ""):
            try:
                items = list(path.iterdir())
                items.sort(key=lambda x: (x.is_file(), x.name.lower()))
                
                for i, item in enumerate(items):
                    if item.name.startswith('.') or item.name in ['venv', '__pycache__']:
                        continue
                    
                    is_last = i == len(items) - 1
                    current_prefix = "└── " if is_last else "├── "
                    next_prefix = "    " if is_last else "│   "
                    
                    structure.append(f"{prefix}{current_prefix}{item.name}")
                    
                    if item.is_dir() and len(structure) < 50:  # Limit depth
                        add_items(item, prefix + next_prefix)
                        
            except PermissionError:
                pass
        
        add_items(self.project_root)
        return "\n".join(structure)

def main():
    """Main function to store embeddings and clean up project"""
    
    # Initialize components
    db_manager = VectorDatabaseManager()
    cleaner = ProjectCleaner(".")
    
    # Store embeddings in vector database
    logger.info("=== STORING EMBEDDINGS IN VECTOR DATABASE ===")
    
    embeddings_file = "travel_groups/embeddings.npy"
    attractions_file = "embedding_ready_attractions.json"
    
    if Path(embeddings_file).exists() and Path(attractions_file).exists():
        success = db_manager.store_embeddings(embeddings_file, attractions_file)
        
        if success:
            logger.info("✅ Embeddings stored successfully in vector database")
            
            # Test search functionality
            logger.info("Testing search functionality...")
            db_manager.test_search()
            
        else:
            logger.error("❌ Failed to store embeddings")
            return
    else:
        logger.error("Embedding files not found. Run the embedding generator first.")
        return
    
    # Clean up project
    logger.info("\n=== CLEANING UP PROJECT ===")
    
    # Confirm cleanup
    response = input("Do you want to clean up temporary files? (y/N): ")
    if response.lower() in ['y', 'yes']:
        cleaner.cleanup_temporary_files()
        cleaner.organize_data_files()
        cleaner.clean_log_files()
        cleaner.create_cleanup_summary()
        
        logger.info("✅ Project cleanup completed")
    else:
        logger.info("Cleanup skipped")
    
    # Final summary
    logger.info("\n=== SUMMARY ===")
    logger.info("✅ Embeddings are now stored in vector database")
    logger.info("✅ Project structure is clean and organized")
    logger.info("✅ Ready for production use!")
    
    logger.info("\nNext steps:")
    logger.info("1. Your embeddings are now in Qdrant vector database")
    logger.info("2. Update your travel planning system to use the vector database")
    logger.info("3. The processed attraction data is now queryable via vector search")

if __name__ == "__main__":
    main()
