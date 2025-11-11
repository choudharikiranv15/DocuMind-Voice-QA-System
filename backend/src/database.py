"""
Database connection and operations using Supabase
"""
import os
from supabase import create_client, Client
from typing import Optional, Dict, Any
from dotenv import load_dotenv

load_dotenv()

# Supabase client singleton
_supabase_client: Optional[Client] = None


def get_supabase_client() -> Client:
    """Get or create Supabase client"""
    global _supabase_client

    if _supabase_client is None:
        url = os.getenv("SUPABASE_URL")
        key = os.getenv("SUPABASE_KEY")

        if not url or not key:
            raise ValueError("SUPABASE_URL and SUPABASE_KEY must be set in environment")

        _supabase_client = create_client(url, key)

    return _supabase_client


class Database:
    """Database operations wrapper"""

    def __init__(self):
        self.client = get_supabase_client()

    def create_user(self, email: str, password_hash: str) -> Dict[str, Any]:
        """Create a new user"""
        response = self.client.table('users').insert({
            'email': email,
            'password_hash': password_hash
        }).execute()

        if response.data:
            return response.data[0]
        raise Exception("Failed to create user")

    def get_user_by_email(self, email: str) -> Optional[Dict[str, Any]]:
        """Get user by email"""
        response = self.client.table('users').select('*').eq('email', email).execute()

        if response.data and len(response.data) > 0:
            return response.data[0]
        return None

    def get_user_by_id(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Get user by ID"""
        response = self.client.table('users').select('*').eq('id', user_id).execute()

        if response.data and len(response.data) > 0:
            return response.data[0]
        return None
