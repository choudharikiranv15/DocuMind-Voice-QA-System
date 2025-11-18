"""
Database connection and operations using Supabase
"""
import os
from supabase import create_client, Client
from typing import Optional, Dict, Any
from dotenv import load_dotenv
import threading

load_dotenv()

# Thread-local storage for connection pooling
_thread_local = threading.local()
_supabase_config = None
_config_lock = threading.Lock()


def get_supabase_client() -> Client:
    """Get or create Supabase client with thread-local connection pooling"""
    global _supabase_config

    # Initialize config once (thread-safe)
    if _supabase_config is None:
        with _config_lock:
            if _supabase_config is None:
                url = os.getenv("SUPABASE_URL")
                key = os.getenv("SUPABASE_KEY")

                if not url or not key:
                    raise ValueError("SUPABASE_URL and SUPABASE_KEY must be set in environment")

                _supabase_config = {'url': url, 'key': key}

    # Each thread gets its own client instance
    if not hasattr(_thread_local, 'supabase_client') or _thread_local.supabase_client is None:
        _thread_local.supabase_client = create_client(
            _supabase_config['url'],
            _supabase_config['key']
        )

    return _thread_local.supabase_client


class Database:
    """Database operations wrapper"""

    def __init__(self):
        self.client = get_supabase_client()

    def create_user(self, email: str, password_hash: str, role: str = None, institution: str = None, occupation: str = None) -> Dict[str, Any]:
        """Create a new user"""
        try:
            user_data = {
                'email': email,
                'password_hash': password_hash
            }

            if role:
                user_data['role'] = role
            if institution:
                user_data['institution'] = institution
            if occupation:
                user_data['occupation'] = occupation

            response = self.client.table('users').insert(user_data).execute()

            if response.data:
                return response.data[0]
            raise Exception("Failed to create user")
        except Exception as e:
            import logging
            logging.error(f"Database error creating user: {e}")
            raise Exception("An error occurred while creating the user account. Please try again.")

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

    def update_user(self, user_id: str, updates: Dict[str, Any]) -> bool:
        """Update user fields"""
        try:
            response = self.client.table('users').update(updates).eq('id', user_id).execute()
            return bool(response.data)
        except Exception as e:
            import logging
            logging.error(f"Database error updating user {user_id}: {e}")
            return False

    def save_feedback(self, user_id: str, message_id: str, query: str, response: str, rating: int, comment: str = None) -> bool:
        """Save user feedback for an AI response"""
        try:
            self.client.table('feedback').insert({
                'user_id': user_id,
                'message_id': message_id,
                'query': query,
                'response': response,
                'rating': rating,
                'comment': comment
            }).execute()
            return True
        except Exception as e:
            print(f"Error saving feedback: {e}")
            return False

    def get_user_plan(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Get user's plan details"""
        try:
            response = self.client.table('user_plans').select('*').eq('user_id', user_id).execute()
            if response.data and len(response.data) > 0:
                return response.data[0]
            return None
        except Exception:
            return None

    def update_user_plan(self, user_id: str, plan_type: str, max_documents: int, max_queries_per_day: int) -> bool:
        """Update user's plan"""
        try:
            response = self.client.table('user_plans').update({
                'plan_type': plan_type,
                'max_documents': max_documents,
                'max_queries_per_day': max_queries_per_day
            }).eq('user_id', user_id).execute()
            return bool(response.data)
        except Exception:
            return False

    def get_voice_preferences(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Get user's voice preferences"""
        try:
            response = self.client.table('user_voice_preferences').select('*').eq('user_id', user_id).execute()
            if response.data and len(response.data) > 0:
                return response.data[0]
            return None
        except Exception:
            return None

    def update_voice_preferences(self, user_id: str, engine_preference: str, language_preference: str) -> bool:
        """Update or insert user's voice preferences"""
        try:
            # Check if preferences exist
            existing = self.get_voice_preferences(user_id)

            if existing:
                # Update existing preferences
                response = self.client.table('user_voice_preferences').update({
                    'engine_preference': engine_preference,
                    'language_preference': language_preference,
                    'updated_at': 'NOW()'
                }).eq('user_id', user_id).execute()
            else:
                # Insert new preferences
                response = self.client.table('user_voice_preferences').insert({
                    'user_id': user_id,
                    'engine_preference': engine_preference,
                    'language_preference': language_preference
                }).execute()

            return bool(response.data)
        except Exception as e:
            import logging
            logging.error(f"Database error updating voice preferences: {e}")
            return False
