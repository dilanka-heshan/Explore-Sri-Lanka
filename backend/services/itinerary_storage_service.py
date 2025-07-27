"""
Itinerary Storage Service
Handles storing, retrieving, and managing travel itineraries
"""

import json
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
import sqlite3
import os

from models.schemas import (
    StoredItinerary, TravelPlanRequest, TravelPlanResponse, 
    ItineraryQueryRequest
)

logger = logging.getLogger(__name__)

class ItineraryStorageService:
    """Service for managing stored itineraries"""
    
    def __init__(self, db_path: str = "itineraries.db"):
        self.db_path = db_path
        self._init_database()
    
    def _init_database(self):
        """Initialize SQLite database for itinerary storage"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Create itineraries table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS itineraries (
                    id TEXT PRIMARY KEY,
                    user_id TEXT,
                    session_id TEXT,
                    created_at TEXT,
                    updated_at TEXT,
                    original_request TEXT,
                    travel_plan TEXT,
                    user_rating INTEGER,
                    user_feedback TEXT,
                    modifications_made TEXT,
                    times_accessed INTEGER DEFAULT 0,
                    shared_count INTEGER DEFAULT 0,
                    is_public BOOLEAN DEFAULT 0,
                    status TEXT DEFAULT 'active'
                )
            """)
            
            # Create indexes for better query performance
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_user_id ON itineraries(user_id)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_session_id ON itineraries(session_id)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_created_at ON itineraries(created_at)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_status ON itineraries(status)")
            
            conn.commit()
            conn.close()
            
            logger.info(f"Initialized itinerary database at {self.db_path}")
            
        except Exception as e:
            logger.error(f"Failed to initialize database: {e}")
            raise
    
    async def store_itinerary(
        self, 
        request: TravelPlanRequest, 
        plan: TravelPlanResponse,
        user_id: Optional[str] = None,
        session_id: Optional[str] = None
    ) -> str:
        """Store a complete itinerary"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Prepare data
            itinerary_id = plan.plan_id
            session_id = session_id or f"session_{itinerary_id}"
            created_at = datetime.now().isoformat()
            
            # Serialize complex objects
            original_request_json = request.model_dump_json()
            travel_plan_json = plan.model_dump_json()
            
            # Insert into database
            cursor.execute("""
                INSERT OR REPLACE INTO itineraries 
                (id, user_id, session_id, created_at, updated_at, original_request, travel_plan)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                itinerary_id, user_id, session_id, created_at, created_at,
                original_request_json, travel_plan_json
            ))
            
            conn.commit()
            conn.close()
            
            logger.info(f"Stored itinerary {itinerary_id}")
            return itinerary_id
            
        except Exception as e:
            logger.error(f"Failed to store itinerary: {e}")
            raise
    
    async def get_itinerary(self, itinerary_id: str) -> Optional[StoredItinerary]:
        """Retrieve a stored itinerary"""
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row  # Enable dict-like access
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT * FROM itineraries WHERE id = ? AND status != 'deleted'
            """, (itinerary_id,))
            
            row = cursor.fetchone()
            if not row:
                return None
            
            # Increment access count
            cursor.execute("""
                UPDATE itineraries SET times_accessed = times_accessed + 1, 
                updated_at = ? WHERE id = ?
            """, (datetime.now().isoformat(), itinerary_id))
            
            conn.commit()
            conn.close()
            
            # Convert to StoredItinerary object
            return self._row_to_stored_itinerary(dict(row))
            
        except Exception as e:
            logger.error(f"Failed to retrieve itinerary {itinerary_id}: {e}")
            return None
    
    async def search_itineraries(self, query: ItineraryQueryRequest) -> List[StoredItinerary]:
        """Search for itineraries based on query parameters"""
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            # Build dynamic query
            sql_parts = ["SELECT * FROM itineraries WHERE status != 'deleted'"]
            params = []
            
            if query.user_id:
                sql_parts.append("AND user_id = ?")
                params.append(query.user_id)
            
            if query.session_id:
                sql_parts.append("AND session_id = ?")
                params.append(query.session_id)
            
            if query.status:
                sql_parts.append("AND status = ?")
                params.append(query.status)
            
            if query.date_range:
                if "start_date" in query.date_range:
                    sql_parts.append("AND created_at >= ?")
                    params.append(query.date_range["start_date"].isoformat())
                if "end_date" in query.date_range:
                    sql_parts.append("AND created_at <= ?")
                    params.append(query.date_range["end_date"].isoformat())
            
            # Add ordering and pagination
            sql_parts.append("ORDER BY created_at DESC")
            sql_parts.append("LIMIT ? OFFSET ?")
            params.extend([query.limit, query.offset])
            
            sql_query = " ".join(sql_parts)
            cursor.execute(sql_query, params)
            
            rows = cursor.fetchall()
            conn.close()
            
            # Convert to StoredItinerary objects
            results = []
            for row in rows:
                try:
                    stored_itinerary = self._row_to_stored_itinerary(dict(row))
                    results.append(stored_itinerary)
                except Exception as e:
                    logger.warning(f"Failed to convert row to StoredItinerary: {e}")
                    continue
            
            return results
            
        except Exception as e:
            logger.error(f"Failed to search itineraries: {e}")
            return []
    
    async def update_feedback(
        self, 
        itinerary_id: str, 
        rating: int, 
        feedback: Optional[str] = None
    ) -> bool:
        """Update user feedback for an itinerary"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                UPDATE itineraries 
                SET user_rating = ?, user_feedback = ?, updated_at = ?
                WHERE id = ?
            """, (rating, feedback, datetime.now().isoformat(), itinerary_id))
            
            success = cursor.rowcount > 0
            conn.commit()
            conn.close()
            
            if success:
                logger.info(f"Updated feedback for itinerary {itinerary_id}: rating={rating}")
            
            return success
            
        except Exception as e:
            logger.error(f"Failed to update feedback for {itinerary_id}: {e}")
            return False
    
    async def add_modification(self, itinerary_id: str, modification: str) -> bool:
        """Add a modification note to an itinerary"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Get current modifications
            cursor.execute("SELECT modifications_made FROM itineraries WHERE id = ?", (itinerary_id,))
            row = cursor.fetchone()
            
            if not row:
                return False
            
            current_mods = json.loads(row[0]) if row[0] else []
            current_mods.append({
                "timestamp": datetime.now().isoformat(),
                "modification": modification
            })
            
            # Update with new modifications
            cursor.execute("""
                UPDATE itineraries 
                SET modifications_made = ?, updated_at = ?
                WHERE id = ?
            """, (json.dumps(current_mods), datetime.now().isoformat(), itinerary_id))
            
            success = cursor.rowcount > 0
            conn.commit()
            conn.close()
            
            return success
            
        except Exception as e:
            logger.error(f"Failed to add modification to {itinerary_id}: {e}")
            return False
    
    async def get_user_statistics(self, user_id: str) -> Dict[str, Any]:
        """Get statistics for a specific user"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Total itineraries
            cursor.execute("""
                SELECT COUNT(*) as total, AVG(user_rating) as avg_rating 
                FROM itineraries WHERE user_id = ? AND status = 'active'
            """, (user_id,))
            
            stats = cursor.fetchone()
            total_itineraries = stats[0] if stats else 0
            avg_rating = stats[1] if stats and stats[1] else 0
            
            # Recent activity
            cursor.execute("""
                SELECT id, created_at FROM itineraries 
                WHERE user_id = ? AND status = 'active'
                ORDER BY created_at DESC LIMIT 5
            """, (user_id,))
            
            recent_itineraries = [
                {"id": row[0], "created_at": row[1]} 
                for row in cursor.fetchall()
            ]
            
            conn.close()
            
            return {
                "user_id": user_id,
                "total_itineraries": total_itineraries,
                "average_rating": round(avg_rating, 2) if avg_rating else None,
                "recent_itineraries": recent_itineraries
            }
            
        except Exception as e:
            logger.error(f"Failed to get user statistics for {user_id}: {e}")
            return {"error": str(e)}
    
    async def get_system_statistics(self) -> Dict[str, Any]:
        """Get overall system statistics"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Overall stats
            cursor.execute("""
                SELECT 
                    COUNT(*) as total_itineraries,
                    COUNT(DISTINCT user_id) as unique_users,
                    AVG(user_rating) as avg_rating,
                    SUM(times_accessed) as total_accesses
                FROM itineraries WHERE status = 'active'
            """)
            
            stats = cursor.fetchone()
            
            # Recent activity (last 7 days)
            week_ago = (datetime.now() - timedelta(days=7)).isoformat()
            cursor.execute("""
                SELECT COUNT(*) FROM itineraries 
                WHERE created_at >= ? AND status = 'active'
            """, (week_ago,))
            
            recent_count = cursor.fetchone()[0]
            
            # Popular destinations/attractions
            cursor.execute("""
                SELECT travel_plan FROM itineraries 
                WHERE status = 'active' 
                ORDER BY created_at DESC LIMIT 100
            """)
            
            # This would analyze popular destinations from travel plans
            # For now, just return basic stats
            
            conn.close()
            
            return {
                "total_itineraries": stats[0] if stats else 0,
                "unique_users": stats[1] if stats else 0,
                "average_rating": round(stats[2], 2) if stats and stats[2] else None,
                "total_accesses": stats[3] if stats else 0,
                "recent_itineraries_week": recent_count,
                "database_size_mb": round(os.path.getsize(self.db_path) / (1024*1024), 2) if os.path.exists(self.db_path) else 0
            }
            
        except Exception as e:
            logger.error(f"Failed to get system statistics: {e}")
            return {"error": str(e)}
    
    def _row_to_stored_itinerary(self, row: Dict[str, Any]) -> StoredItinerary:
        """Convert database row to StoredItinerary object"""
        try:
            # Parse JSON fields
            original_request = TravelPlanRequest.model_validate_json(row["original_request"])
            travel_plan = TravelPlanResponse.model_validate_json(row["travel_plan"])
            modifications = json.loads(row["modifications_made"]) if row["modifications_made"] else []
            
            return StoredItinerary(
                id=row["id"],
                user_id=row["user_id"],
                session_id=row["session_id"],
                created_at=datetime.fromisoformat(row["created_at"]),
                updated_at=datetime.fromisoformat(row["updated_at"]),
                original_request=original_request,
                travel_plan=travel_plan,
                user_rating=row["user_rating"],
                user_feedback=row["user_feedback"],
                modifications_made=modifications,
                times_accessed=row["times_accessed"],
                shared_count=row["shared_count"],
                is_public=bool(row["is_public"]),
                status=row["status"]
            )
            
        except Exception as e:
            logger.error(f"Failed to convert row to StoredItinerary: {e}")
            raise

# Singleton instance
itinerary_storage_service = ItineraryStorageService()
