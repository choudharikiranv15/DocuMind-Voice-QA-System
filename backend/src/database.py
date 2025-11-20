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

    def delete_user(self, user_id: str) -> bool:
        """Delete user account (cascades to related tables via ON DELETE CASCADE)"""
        try:
            response = self.client.table('users').delete().eq('id', user_id).execute()
            return bool(response.data)
        except Exception as e:
            import logging
            logging.error(f"Database error deleting user {user_id}: {e}")
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

    def search_documents(self, user_id: str, search_query: str = None, category: str = None, tags: list = None) -> list:
        """Search documents by query, category, or tags"""
        try:
            query = self.client.table('documents').select('*').eq('user_id', user_id)

            # Filter by category if provided
            if category and category != 'all':
                query = query.eq('category', category)

            # Filter by tags if provided (any tag match)
            if tags and len(tags) > 0:
                query = query.contains('tags', tags)

            # Text search on filename and description if provided
            if search_query and search_query.strip():
                # Use ilike for case-insensitive search
                query = query.or_(f"filename.ilike.%{search_query}%,description.ilike.%{search_query}%")

            response = query.order('uploaded_at', desc=True).execute()
            return response.data if response.data else []
        except Exception as e:
            import logging
            logging.error(f"Database error searching documents: {e}")
            return []

    def update_document_metadata(self, document_id: str, user_id: str, updates: Dict[str, Any]) -> bool:
        """Update document metadata (category, tags, description)"""
        try:
            response = self.client.table('documents').update(updates).eq('id', document_id).eq('user_id', user_id).execute()
            return bool(response.data)
        except Exception as e:
            import logging
            logging.error(f"Database error updating document metadata: {e}")
            return False

    def get_document_categories(self) -> list:
        """Get list of predefined document categories"""
        try:
            response = self.client.table('document_categories').select('*').order('name').execute()
            return response.data if response.data else []
        except Exception as e:
            import logging
            logging.error(f"Database error getting categories: {e}")
            return []

    def get_user_documents_with_filters(self, user_id: str, category: str = None, limit: int = 100) -> list:
        """Get user documents with optional category filter"""
        try:
            query = self.client.table('documents').select('*').eq('user_id', user_id)

            if category and category != 'all':
                query = query.eq('category', category)

            response = query.order('uploaded_at', desc=True).limit(limit).execute()
            return response.data if response.data else []
        except Exception as e:
            import logging
            logging.error(f"Database error getting documents: {e}")
            return []

    # ============= SITE FEEDBACK METHODS =============

    def save_site_feedback(self, feedback_data: Dict[str, Any]) -> bool:
        """Save general site feedback to database"""
        try:
            response = self.client.table('site_feedback').insert(feedback_data).execute()
            return bool(response.data)
        except Exception as e:
            import logging
            logging.error(f"Database error saving site feedback: {e}")
            return False

    def get_user_site_feedback(self, user_id: str) -> list:
        """Get all site feedback submitted by a user"""
        try:
            response = self.client.table('site_feedback') \
                .select('*') \
                .eq('user_id', user_id) \
                .order('created_at', desc=True) \
                .execute()
            return response.data if response.data else []
        except Exception as e:
            import logging
            logging.error(f"Database error getting user site feedback: {e}")
            return []

    def get_all_site_feedback(self, limit: int = 100, status: str = None) -> list:
        """Get all site feedback (admin use)"""
        try:
            query = self.client.table('site_feedback').select('*')

            if status:
                query = query.eq('status', status)

            response = query.order('created_at', desc=True).limit(limit).execute()
            return response.data if response.data else []
        except Exception as e:
            import logging
            logging.error(f"Database error getting all site feedback: {e}")
            return []

    # ============= ADMIN ANALYTICS METHODS =============

    def get_all_users(self, limit: int = 1000, offset: int = 0) -> list:
        """Get all users (admin only)"""
        try:
            response = self.client.table('users') \
                .select('id, email, role, institution, occupation, is_admin, created_at, last_login') \
                .order('created_at', desc=True) \
                .range(offset, offset + limit - 1) \
                .execute()
            return response.data if response.data else []
        except Exception as e:
            import logging
            logging.error(f"Database error getting all users: {e}")
            return []

    def get_user_stats_admin(self, user_id: str) -> dict:
        """Get detailed user statistics (admin only)"""
        try:
            # Get user info
            user_response = self.client.table('users').select('*').eq('id', user_id).execute()
            if not user_response.data:
                return {}

            user = user_response.data[0]

            # Get document count
            doc_response = self.client.table('documents').select('id').eq('user_id', user_id).execute()
            document_count = len(doc_response.data) if doc_response.data else 0

            # Get feedback count
            feedback_response = self.client.table('feedback').select('id').eq('user_id', user_id).execute()
            feedback_count = len(feedback_response.data) if feedback_response.data else 0

            # Get site feedback
            site_feedback_response = self.client.table('site_feedback').select('*').eq('user_id', user_id).execute()
            site_feedback = site_feedback_response.data if site_feedback_response.data else []

            return {
                'user': user,
                'document_count': document_count,
                'feedback_count': feedback_count,
                'site_feedback': site_feedback
            }
        except Exception as e:
            import logging
            logging.error(f"Database error getting user stats (admin): {e}")
            return {}

    def get_system_analytics(self) -> dict:
        """Get overall system analytics (admin only)"""
        try:
            # Total users
            users_response = self.client.table('users').select('id', count='exact').execute()
            total_users = users_response.count if users_response.count else 0

            # Total documents
            docs_response = self.client.table('documents').select('id', count='exact').execute()
            total_documents = docs_response.count if docs_response.count else 0

            # Total feedback
            feedback_response = self.client.table('site_feedback').select('id, overall_rating', count='exact').execute()
            total_feedback = feedback_response.count if feedback_response.count else 0

            # Average rating
            avg_rating = 0
            if feedback_response.data:
                ratings = [f['overall_rating'] for f in feedback_response.data if f.get('overall_rating')]
                avg_rating = sum(ratings) / len(ratings) if ratings else 0

            # Recent users (last 7 days)
            from datetime import datetime, timedelta
            week_ago = (datetime.now() - timedelta(days=7)).isoformat()
            recent_users_response = self.client.table('users') \
                .select('id', count='exact') \
                .gte('created_at', week_ago) \
                .execute()
            recent_users = recent_users_response.count if recent_users_response.count else 0

            return {
                'total_users': total_users,
                'total_documents': total_documents,
                'total_feedback': total_feedback,
                'average_rating': round(avg_rating, 2),
                'recent_users_week': recent_users
            }
        except Exception as e:
            import logging
            logging.error(f"Database error getting system analytics: {e}")
            return {}

    def get_feedback_analytics(self) -> dict:
        """Get feedback analytics (admin only)"""
        try:
            response = self.client.table('site_feedback').select('*').execute()
            feedbacks = response.data if response.data else []

            # Group by type
            by_type = {}
            by_rating = {1: 0, 2: 0, 3: 0, 4: 0, 5: 0}
            total_nps = []

            for feedback in feedbacks:
                # By type
                ftype = feedback.get('feedback_type', 'other')
                by_type[ftype] = by_type.get(ftype, 0) + 1

                # By rating
                rating = feedback.get('overall_rating')
                if rating in by_rating:
                    by_rating[rating] += 1

                # NPS
                if feedback.get('nps_score') is not None:
                    total_nps.append(feedback['nps_score'])

            # Calculate NPS
            nps_score = 0
            if total_nps:
                promoters = len([s for s in total_nps if s >= 9])
                detractors = len([s for s in total_nps if s <= 6])
                nps_score = ((promoters - detractors) / len(total_nps)) * 100

            return {
                'by_type': by_type,
                'by_rating': by_rating,
                'nps_score': round(nps_score, 1),
                'total_responses': len(feedbacks)
            }
        except Exception as e:
            import logging
            logging.error(f"Database error getting feedback analytics: {e}")
            return {}
