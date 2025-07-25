"""
Database configuration and connection setup for Supabase
"""
import os
from typing import Optional, Generator
from sqlalchemy import create_engine, MetaData
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import StaticPool
import logging

# Supabase imports
try:
    from supabase import create_client, Client
    SUPABASE_AVAILABLE = True
except ImportError:
    SUPABASE_AVAILABLE = False
    logging.warning("Supabase client not available. Install with: pip install supabase")

logger = logging.getLogger(__name__)

# Load environment variables
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

# Database Configuration
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_ANON_KEY = os.getenv("SUPABASE_ANON_KEY")
SUPABASE_SERVICE_KEY = os.getenv("SUPABASE_SERVICE_KEY")

# For SQLAlchemy connection to Supabase PostgreSQL
DATABASE_URL = os.getenv("DATABASE_URL", f"postgresql://postgres:[YOUR-PASSWORD]@db.rgbxpspefdnmzaknzdes.supabase.co:5432/postgres")

# SQLAlchemy setup
engine = None
SessionLocal = None
Base = declarative_base()

# Supabase client
supabase: Optional[Client] = None

def init_database():
    """Initialize database connections"""
    global engine, SessionLocal, supabase
    
    try:
        # Initialize Supabase client
        if SUPABASE_AVAILABLE and SUPABASE_URL and SUPABASE_ANON_KEY:
            supabase = create_client(SUPABASE_URL, SUPABASE_ANON_KEY)
            logger.info("Supabase client initialized successfully")
        else:
            logger.warning("Supabase configuration missing or client not available")
        
        # Initialize SQLAlchemy engine (for more complex queries if needed)
        if DATABASE_URL and "postgresql://" in DATABASE_URL:
            engine = create_engine(
                DATABASE_URL,
                poolclass=StaticPool,
                connect_args={"check_same_thread": False} if "sqlite" in DATABASE_URL else {}
            )
            SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
            logger.info("SQLAlchemy engine initialized successfully")
        else:
            logger.warning("Database URL not configured properly")
            
    except Exception as e:
        logger.error(f"Database initialization failed: {e}")

def get_db() -> Generator[Session, None, None]:
    """
    Dependency to get database session
    """
    if SessionLocal is None:
        init_database()
    
    if SessionLocal is None:
        logger.error("Database not initialized properly")
        raise Exception("Database connection not available")
    
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_supabase_client() -> Optional[Client]:
    """
    Get Supabase client instance
    """
    global supabase
    if supabase is None:
        init_database()
    return supabase

# Database utility functions for Supabase
class SupabaseManager:
    """Manager class for Supabase operations"""
    
    def __init__(self):
        self.client = get_supabase_client()
    
    async def create_user(self, email: str, password: str, user_metadata: dict = None):
        """Create a new user"""
        if not self.client:
            raise Exception("Supabase client not available")
        
        try:
            response = self.client.auth.sign_up({
                "email": email,
                "password": password,
                "options": {"data": user_metadata} if user_metadata else None
            })
            return response
        except Exception as e:
            logger.error(f"Error creating user: {e}")
            raise
    
    async def authenticate_user(self, email: str, password: str):
        """Authenticate user"""
        if not self.client:
            raise Exception("Supabase client not available")
        
        try:
            response = self.client.auth.sign_in_with_password({
                "email": email,
                "password": password
            })
            return response
        except Exception as e:
            logger.error(f"Error authenticating user: {e}")
            raise
    
    def insert_data(self, table_name: str, data: dict):
        """Insert data into a table"""
        if not self.client:
            raise Exception("Supabase client not available")
        
        try:
            result = self.client.table(table_name).insert(data).execute()
            return result
        except Exception as e:
            logger.error(f"Error inserting data into {table_name}: {e}")
            raise
    
    def select_data(self, table_name: str, filters: dict = None, columns: str = "*"):
        """Select data from a table"""
        if not self.client:
            raise Exception("Supabase client not available")
        
        try:
            query = self.client.table(table_name).select(columns)
            
            if filters:
                for key, value in filters.items():
                    query = query.eq(key, value)
            
            result = query.execute()
            return result
        except Exception as e:
            logger.error(f"Error selecting data from {table_name}: {e}")
            raise
    
    def update_data(self, table_name: str, data: dict, filters: dict):
        """Update data in a table"""
        if not self.client:
            raise Exception("Supabase client not available")
        
        try:
            query = self.client.table(table_name).update(data)
            
            for key, value in filters.items():
                query = query.eq(key, value)
            
            result = query.execute()
            return result
        except Exception as e:
            logger.error(f"Error updating data in {table_name}: {e}")
            raise
    
    def delete_data(self, table_name: str, filters: dict):
        """Delete data from a table"""
        if not self.client:
            raise Exception("Supabase client not available")
        
        try:
            query = self.client.table(table_name)
            
            for key, value in filters.items():
                query = query.eq(key, value)
            
            result = query.delete().execute()
            return result
        except Exception as e:
            logger.error(f"Error deleting data from {table_name}: {e}")
            raise

# Initialize database on module import
init_database()

# Create global instance
supabase_manager = SupabaseManager()
