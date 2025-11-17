"""
Error Tracking with Sentry
Captures and reports errors to Sentry for monitoring.
"""
import os
import sentry_sdk
from sentry_sdk.integrations.flask import FlaskIntegration
from sentry_sdk.integrations.logging import LoggingIntegration
import logging

logger = logging.getLogger(__name__)


def init_sentry(app=None):
    """
    Initialize Sentry error tracking

    Args:
        app: Flask app instance (optional)
    """
    sentry_dsn = os.getenv('SENTRY_DSN')
    environment = os.getenv('SENTRY_ENVIRONMENT', 'development')

    if not sentry_dsn or sentry_dsn == 'your_sentry_dsn_here':
        logger.warning("⚠️  Sentry DSN not configured. Error tracking is disabled.")
        logger.warning("   Set SENTRY_DSN in .env to enable error tracking.")
        return False

    try:
        integrations = [
            FlaskIntegration(
                transaction_style='url'
            ),
            LoggingIntegration(
                level=logging.INFO,  # Capture info and above as breadcrumbs
                event_level=logging.ERROR  # Send errors and above as events
            )
        ]

        sentry_sdk.init(
            dsn=sentry_dsn,
            environment=environment,
            integrations=integrations,
            # Set traces_sample_rate to 1.0 to capture 100%
            # of transactions for performance monitoring.
            # Reduce in production to save quota (e.g., 0.1 = 10%)
            traces_sample_rate=0.1 if environment == 'production' else 1.0,
            # Attach user context automatically
            send_default_pii=False,  # Don't send PII by default
            # Custom release tracking (optional)
            release=os.getenv('APP_VERSION', 'dev'),
        )

        logger.info(f"✅ Sentry initialized for environment: {environment}")
        return True

    except Exception as e:
        logger.error(f"❌ Failed to initialize Sentry: {e}")
        return False


def capture_exception(error, context=None):
    """
    Manually capture an exception with optional context

    Args:
        error: The exception to capture
        context: Additional context dictionary
    """
    if context:
        with sentry_sdk.push_scope() as scope:
            for key, value in context.items():
                scope.set_context(key, value)
            sentry_sdk.capture_exception(error)
    else:
        sentry_sdk.capture_exception(error)


def capture_message(message, level='info', context=None):
    """
    Capture a message (not an exception)

    Args:
        message: The message to capture
        level: Severity level ('debug', 'info', 'warning', 'error', 'fatal')
        context: Additional context dictionary
    """
    if context:
        with sentry_sdk.push_scope() as scope:
            for key, value in context.items():
                scope.set_context(key, value)
            sentry_sdk.capture_message(message, level=level)
    else:
        sentry_sdk.capture_message(message, level=level)


def set_user_context(user_id, email=None):
    """
    Set user context for error tracking

    Args:
        user_id: User's unique identifier
        email: User's email (optional)
    """
    sentry_sdk.set_user({
        "id": user_id,
        "email": email
    })


def add_breadcrumb(message, category='default', level='info', data=None):
    """
    Add a breadcrumb for tracing user actions

    Args:
        message: Breadcrumb message
        category: Category (e.g., 'auth', 'query', 'upload')
        level: Severity level
        data: Additional data dictionary
    """
    sentry_sdk.add_breadcrumb(
        message=message,
        category=category,
        level=level,
        data=data or {}
    )
