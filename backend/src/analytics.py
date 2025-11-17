"""
Analytics Service
Tracks user events and system metrics using PostHog and custom Supabase events.
"""
import os
import logging
from typing import Optional, Dict, Any
from datetime import datetime
from src.database import get_supabase_client

logger = logging.getLogger(__name__)

# PostHog initialization
POSTHOG_AVAILABLE = False
try:
    from posthog import Posthog
    POSTHOG_AVAILABLE = True
except ImportError:
    logger.warning("PostHog package not installed. Analytics will use Supabase only.")


class AnalyticsService:
    """Handles analytics tracking"""

    def __init__(self):
        self.client = get_supabase_client()
        self.posthog = None

        # Initialize PostHog if available
        if POSTHOG_AVAILABLE:
            api_key = os.getenv('POSTHOG_API_KEY')
            host = os.getenv('POSTHOG_HOST', 'https://app.posthog.com')

            if api_key and api_key != 'your_posthog_api_key_here':
                try:
                    self.posthog = Posthog(
                        api_key=api_key,
                        host=host
                    )
                    logger.info("✅ PostHog analytics initialized")
                except Exception as e:
                    logger.error(f"Failed to initialize PostHog: {e}")
            else:
                logger.warning("⚠️  PostHog API key not configured")

    def track_event(self, user_id: str, event_type: str, metadata: Optional[Dict[str, Any]] = None):
        """
        Track an event in both PostHog and Supabase

        Args:
            user_id: User's unique identifier
            event_type: Event name (e.g., 'user_signup', 'document_upload')
            metadata: Additional event data
        """
        metadata = metadata or {}

        # Track in Supabase (always)
        try:
            self.client.table('usage_events').insert({
                'user_id': user_id,
                'event_type': event_type,
                'timestamp': datetime.now().isoformat(),
                'metadata': metadata
            }).execute()
        except Exception as e:
            logger.error(f"Failed to track event in Supabase: {e}")

        # Track in PostHog (if available)
        if self.posthog:
            try:
                self.posthog.capture(
                    distinct_id=user_id,
                    event=event_type,
                    properties=metadata
                )
            except Exception as e:
                logger.error(f"Failed to track event in PostHog: {e}")

    def identify_user(self, user_id: str, properties: Dict[str, Any]):
        """
        Identify a user with properties (PostHog only)

        Args:
            user_id: User's unique identifier
            properties: User properties (email, role, etc.)
        """
        if self.posthog:
            try:
                self.posthog.identify(
                    distinct_id=user_id,
                    properties=properties
                )
            except Exception as e:
                logger.error(f"Failed to identify user in PostHog: {e}")

    def track_signup(self, user_id: str, email: str, role: str = None):
        """Track user signup"""
        self.track_event(user_id, 'user_signup', {
            'email': email,
            'role': role
        })
        self.identify_user(user_id, {
            'email': email,
            'role': role,
            'signup_date': datetime.now().isoformat()
        })

    def track_login(self, user_id: str, email: str):
        """Track user login"""
        self.track_event(user_id, 'user_login', {
            'email': email
        })

    def track_document_upload(self, user_id: str, filename: str, file_size: int):
        """Track document upload"""
        self.track_event(user_id, 'document_upload', {
            'filename': filename,
            'file_size': file_size
        })

    def track_query(self, user_id: str, query_type: str, query_length: int):
        """
        Track a query

        Args:
            user_id: User ID
            query_type: 'text' or 'voice'
            query_length: Length of the query in characters
        """
        self.track_event(user_id, 'query_asked', {
            'query_type': query_type,
            'query_length': query_length
        })

    def track_feedback(self, user_id: str, rating: int, has_comment: bool):
        """Track feedback submission"""
        self.track_event(user_id, 'feedback_submitted', {
            'rating': rating,
            'has_comment': has_comment
        })

    def track_email_verified(self, user_id: str):
        """Track email verification"""
        self.track_event(user_id, 'email_verified', {})

    def track_student_verification_requested(self, user_id: str):
        """Track student verification request"""
        self.track_event(user_id, 'student_verification_requested', {})

    def get_user_stats(self, user_id: str) -> Dict[str, Any]:
        """
        Get user statistics from database

        Args:
            user_id: User ID

        Returns:
            Dict with user stats
        """
        try:
            # Get total queries
            queries_response = self.client.table('usage_events').select('id', count='exact').eq('user_id', user_id).eq('event_type', 'query_asked').execute()
            total_queries = queries_response.count if queries_response.count else 0

            # Get total documents
            docs_response = self.client.table('documents').select('id', count='exact').eq('user_id', user_id).execute()
            total_documents = docs_response.count if docs_response.count else 0

            # Get user info
            user_response = self.client.table('users').select('created_at, email, role').eq('id', user_id).execute()
            user_data = user_response.data[0] if user_response.data else {}

            return {
                'total_queries': total_queries,
                'total_documents': total_documents,
                'member_since': user_data.get('created_at'),
                'email': user_data.get('email'),
                'role': user_data.get('role')
            }

        except Exception as e:
            logger.error(f"Failed to get user stats: {e}")
            return {
                'total_queries': 0,
                'total_documents': 0,
                'member_since': None
            }

    def shutdown(self):
        """Shutdown PostHog gracefully"""
        if self.posthog:
            try:
                self.posthog.shutdown()
            except Exception as e:
                logger.error(f"Error shutting down PostHog: {e}")


# Singleton instance
_analytics_service = None


def get_analytics_service() -> AnalyticsService:
    """Get or create analytics service instance"""
    global _analytics_service
    if _analytics_service is None:
        _analytics_service = AnalyticsService()
    return _analytics_service
