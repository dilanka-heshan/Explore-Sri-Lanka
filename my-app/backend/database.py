import os
from supabase import create_client, Client
from typing import Optional
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Supabase configuration
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_ANON_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    raise ValueError("SUPABASE_URL and SUPABASE_ANON_KEY environment variables are required")

def get_supabase_client() -> Client:
    """Get Supabase client instance"""
    return create_client(SUPABASE_URL, SUPABASE_KEY)

class DatabaseManager:
    def __init__(self):
        self.client = get_supabase_client()
    
    async def execute_query(self, table: str, query_builder):
        """Execute a query and return results"""
        try:
            response = query_builder.execute()
            return response.data
        except Exception as e:
            print(f"Database error: {e}")
            raise e
    
    async def insert_record(self, table: str, data: dict):
        """Insert a new record"""
        try:
            response = self.client.table(table).insert(data).execute()
            return response.data[0] if response.data else None
        except Exception as e:
            print(f"Insert error: {e}")
            raise e
    
    async def update_record(self, table: str, record_id: str, data: dict):
        """Update an existing record"""
        try:
            response = self.client.table(table).update(data).eq('id', record_id).execute()
            return response.data[0] if response.data else None
        except Exception as e:
            print(f"Update error: {e}")
            raise e
    
    async def delete_record(self, table: str, record_id: str):
        """Delete a record"""
        try:
            response = self.client.table(table).delete().eq('id', record_id).execute()
            return response.data
        except Exception as e:
            print(f"Delete error: {e}")
            raise e