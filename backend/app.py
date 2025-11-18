# app_flask.py - Flask interface for RAG System with Voice Support
from flask import Flask, render_template, request, jsonify, session, send_file
from flask_cors import CORS
import os
from werkzeug.utils import secure_filename
from config.config import Config
from src.rag_system import RAGSystem
from src.stt_handler import STTHandler
from src.multilingual_tts_handler import MultilingualTTSHandler  # Multilingual TTS (gTTS + Coqui)
from src.database import Database
from src.auth.jwt_handler import generate_jwt, verify_jwt
from src.auth.decorators import require_auth
from src.limits import UserLimits
from src.error_tracking import init_sentry, capture_exception, add_breadcrumb, set_user_context
from src.email_service import get_email_service
from src.analytics import get_analytics_service
from src.auth.password_reset import PasswordResetService
import bcrypt
import secrets
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# Initialize Sentry for error tracking
init_sentry(app)

# CORS Configuration for production
cors_origins = os.getenv('CORS_ORIGINS', 'http://localhost:5173,http://localhost:3000').split(',')
CORS(app, resources={
    r"/*": {
        "origins": cors_origins,
        "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        "allow_headers": [
            "Content-Type",
            "Authorization",
            "baggage",           # Sentry tracing
            "sentry-trace",      # Sentry tracing
            "X-Requested-With",  # Common AJAX header
            "Accept",            # Standard header
            "Origin"             # CORS header
        ],
        "expose_headers": ["Content-Type", "Authorization"],
        "supports_credentials": True,
        "max_age": 3600  # Cache preflight requests for 1 hour
    }
})

app.secret_key = os.getenv('SECRET_KEY', secrets.token_hex(16))
app.config['UPLOAD_FOLDER'] = './data/pdfs'
app.config['AUDIO_FOLDER'] = './data/audio'
app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024  # 50MB max

# Create necessary directories
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(app.config['AUDIO_FOLDER'], exist_ok=True)

# Initialize systems
config = Config()
rag_system = RAGSystem(config)
stt_handler = STTHandler()  # Uses Groq Whisper API
tts_handler = MultilingualTTSHandler(
    output_dir=app.config['AUDIO_FOLDER'],
    enable_coqui_fallback=True  # gTTS primary, Coqui fallback for English
)
db = Database()  # Database connection
user_limits = UserLimits(rag_system.cache, db)  # User limits manager
email_service = get_email_service()  # Email service
analytics = get_analytics_service()  # Analytics service
password_reset_service = PasswordResetService(rag_system.cache)  # Password reset service

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/voice-test')
def voice_test():
    return render_template('voice_test.html')

# ============= AUTHENTICATION ENDPOINTS =============

@app.route('/auth/signup', methods=['POST'])
def signup():
    """User registration endpoint with role/occupation"""
    try:
        data = request.json
        email = data.get('email', '').strip().lower()
        password = data.get('password', '').strip()
        role = data.get('role', '').strip()  # student, professional, researcher, other
        institution = data.get('institution', '').strip()
        occupation = data.get('occupation', '').strip()

        # Validation
        if not email or not password:
            return jsonify({'success': False, 'message': 'Email and password are required'}), 400

        if len(password) < 6:
            return jsonify({'success': False, 'message': 'Password must be at least 6 characters'}), 400

        # Check if user already exists
        existing_user = db.get_user_by_email(email)
        if existing_user:
            return jsonify({'success': False, 'message': 'User already exists'}), 400

        # Hash password
        password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

        # Create user
        user = db.create_user(email, password_hash, role, institution, occupation)

        # Generate JWT
        token = generate_jwt(user['id'], user['email'])

        # Track signup event
        analytics.track_signup(user['id'], email, role)
        add_breadcrumb('User signed up', category='auth', data={'email': email, 'role': role})

        return jsonify({
            'success': True,
            'message': 'User created successfully',
            'token': token,
            'user': {
                'id': user['id'],
                'email': user['email'],
                'role': user.get('role'),
                'institution': user.get('institution')
            }
        })

    except Exception as e:
        logger.error(f"Signup error: {str(e)}")
        capture_exception(e, {'endpoint': 'signup'})
        return jsonify({'success': False, 'message': str(e)}), 500


@app.route('/auth/login', methods=['GET', 'POST', 'OPTIONS'])
def login():
    """User login endpoint"""
    # Handle OPTIONS request (CORS preflight)
    if request.method == 'OPTIONS':
        return '', 204

    # Handle GET request (browser navigation/prefetch)
    if request.method == 'GET':
        return jsonify({
            'error': 'Method Not Allowed',
            'message': 'This is an API endpoint. Please use POST method with credentials.',
            'endpoint': '/auth/login',
            'method_required': 'POST'
        }), 405

    try:
        data = request.json
        email = data.get('email', '').strip().lower()
        password = data.get('password', '').strip()

        # Validation
        if not email or not password:
            return jsonify({'success': False, 'message': 'Email and password are required'}), 400

        # Get user
        user = db.get_user_by_email(email)
        if not user:
            return jsonify({'success': False, 'message': 'Invalid credentials'}), 401

        # Verify password
        if not bcrypt.checkpw(password.encode('utf-8'), user['password_hash'].encode('utf-8')):
            return jsonify({'success': False, 'message': 'Invalid credentials'}), 401

        # Generate JWT
        token = generate_jwt(user['id'], user['email'])

        # Track login event
        analytics.track_login(user['id'], user['email'])
        add_breadcrumb('User logged in', category='auth', data={'email': user['email']})

        return jsonify({
            'success': True,
            'message': 'Login successful',
            'token': token,
            'user': {
                'id': user['id'],
                'email': user['email'],
                'role': user.get('role'),
                'is_verified': user.get('is_verified', False)
            }
        })

    except Exception as e:
        logger.error(f"Login error: {str(e)}")
        capture_exception(e, {'endpoint': 'login'})
        return jsonify({'success': False, 'message': str(e)}), 500


@app.route('/auth/me', methods=['GET'])
@require_auth
def get_current_user():
    """Get current user information"""
    try:
        user = db.get_user_by_id(request.user_id)
        if not user:
            return jsonify({'success': False, 'message': 'User not found'}), 404

        return jsonify({
            'success': True,
            'user': {
                'id': user['id'],
                'email': user['email'],
                'created_at': user['created_at'].isoformat() if hasattr(user['created_at'], 'isoformat') else str(user['created_at'])
            }
        })

    except Exception as e:
        logger.error(f"Get user error: {str(e)}")
        return jsonify({'success': False, 'message': str(e)}), 500


@app.route('/auth/forgot-password', methods=['POST'])
def forgot_password():
    """Request password reset"""
    try:
        data = request.json
        email = data.get('email', '').strip().lower()

        if not email:
            return jsonify({'success': False, 'message': 'Email is required'}), 400

        # Check rate limit
        is_allowed, request_count = password_reset_service.check_rate_limit(email)
        if not is_allowed:
            return jsonify({
                'success': False,
                'message': 'Too many password reset requests. Please try again later.'
            }), 429

        # Generate reset token
        token = password_reset_service.generate_reset_token(email)

        if token:
            # Send reset email
            frontend_url = os.getenv('FRONTEND_URL', 'http://localhost:5173')
            reset_link = f"{frontend_url}/reset-password?token={token}"
            email_service.send_password_reset_email(email, reset_link)

            logger.info(f"Password reset requested for {email}")
            add_breadcrumb('Password reset requested', category='auth', data={'email': email})

        # Always return success (don't reveal if email exists)
        return jsonify({
            'success': True,
            'message': 'If that email exists, a password reset link has been sent.'
        })

    except Exception as e:
        logger.error(f"Forgot password error: {str(e)}")
        capture_exception(e, {'endpoint': 'forgot_password'})
        return jsonify({'success': False, 'message': 'An error occurred'}), 500


@app.route('/auth/reset-password', methods=['POST'])
def reset_password():
    """Reset password using token"""
    try:
        data = request.json
        token = data.get('token', '').strip()
        new_password = data.get('password', '').strip()

        if not token or not new_password:
            return jsonify({'success': False, 'message': 'Token and password are required'}), 400

        if len(new_password) < 6:
            return jsonify({'success': False, 'message': 'Password must be at least 6 characters'}), 400

        # Hash new password
        password_hash = bcrypt.hashpw(new_password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

        # Reset password
        success, message = password_reset_service.reset_password(token, password_hash)

        if success:
            logger.info("Password reset successful")
            add_breadcrumb('Password reset completed', category='auth')
            return jsonify({'success': True, 'message': message})
        else:
            return jsonify({'success': False, 'message': message}), 400

    except Exception as e:
        logger.error(f"Reset password error: {str(e)}")
        capture_exception(e, {'endpoint': 'reset_password'})
        return jsonify({'success': False, 'message': 'An error occurred'}), 500


@app.route('/auth/change-password', methods=['POST'])
@require_auth
def change_password():
    """Change password for logged-in user"""
    try:
        data = request.json
        current_password = data.get('current_password', '').strip()
        new_password = data.get('new_password', '').strip()

        # Validation
        if not current_password or not new_password:
            return jsonify({'success': False, 'message': 'Current and new passwords are required'}), 400

        if len(new_password) < 6:
            return jsonify({'success': False, 'message': 'New password must be at least 6 characters'}), 400

        if current_password == new_password:
            return jsonify({'success': False, 'message': 'New password must be different from current password'}), 400

        # Get user
        user = db.get_user_by_id(request.user_id)
        if not user:
            return jsonify({'success': False, 'message': 'User not found'}), 404

        # Verify current password
        if not bcrypt.checkpw(current_password.encode('utf-8'), user['password_hash'].encode('utf-8')):
            return jsonify({'success': False, 'message': 'Current password is incorrect'}), 401

        # Hash new password
        new_password_hash = bcrypt.hashpw(new_password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

        # Update password
        success = db.update_user(request.user_id, {'password_hash': new_password_hash})

        if success:
            logger.info(f"Password changed successfully for user {request.user_id}")
            add_breadcrumb('Password changed', category='auth', data={'user_id': request.user_id})
            analytics.track_event(request.user_id, 'password_changed')
            return jsonify({'success': True, 'message': 'Password changed successfully'})
        else:
            return jsonify({'success': False, 'message': 'Failed to update password'}), 500

    except Exception as e:
        logger.error(f"Change password error: {str(e)}")
        capture_exception(e, {'endpoint': 'change_password'})
        return jsonify({'success': False, 'message': 'An error occurred'}), 500


@app.route('/auth/change-email', methods=['POST'])
@require_auth
def change_email():
    """Change email for logged-in user"""
    try:
        data = request.json
        new_email = data.get('new_email', '').strip().lower()
        password = data.get('password', '').strip()

        # Validation
        if not new_email or not password:
            return jsonify({'success': False, 'message': 'New email and password are required'}), 400

        # Basic email validation
        if '@' not in new_email or '.' not in new_email:
            return jsonify({'success': False, 'message': 'Invalid email format'}), 400

        # Get user
        user = db.get_user_by_id(request.user_id)
        if not user:
            return jsonify({'success': False, 'message': 'User not found'}), 404

        # Check if new email is same as current
        if new_email == user['email']:
            return jsonify({'success': False, 'message': 'New email is same as current email'}), 400

        # Verify password
        if not bcrypt.checkpw(password.encode('utf-8'), user['password_hash'].encode('utf-8')):
            return jsonify({'success': False, 'message': 'Password is incorrect'}), 401

        # Check if new email already exists
        existing_user = db.get_user_by_email(new_email)
        if existing_user:
            return jsonify({'success': False, 'message': 'Email already in use'}), 400

        # Update email
        success = db.update_user(request.user_id, {'email': new_email})

        if success:
            logger.info(f"Email changed successfully for user {request.user_id}")
            add_breadcrumb('Email changed', category='auth', data={'user_id': request.user_id, 'new_email': new_email})
            analytics.track_event(request.user_id, 'email_changed')

            # Generate new JWT with updated email
            token = generate_jwt(request.user_id, new_email)

            return jsonify({
                'success': True,
                'message': 'Email changed successfully',
                'token': token,
                'email': new_email
            })
        else:
            return jsonify({'success': False, 'message': 'Failed to update email'}), 500

    except Exception as e:
        logger.error(f"Change email error: {str(e)}")
        capture_exception(e, {'endpoint': 'change_email'})
        return jsonify({'success': False, 'message': 'An error occurred'}), 500


@app.route('/auth/delete-account', methods=['DELETE'])
@require_auth
def delete_account():
    """Delete user account and all associated data (GDPR compliance)"""
    try:
        data = request.json
        password = data.get('password', '').strip()
        confirmation = data.get('confirmation', '').strip()

        # Validation
        if not password:
            return jsonify({'success': False, 'message': 'Password is required'}), 400

        if confirmation != 'DELETE':
            return jsonify({'success': False, 'message': 'Please type DELETE to confirm'}), 400

        # Get user
        user = db.get_user_by_id(request.user_id)
        if not user:
            return jsonify({'success': False, 'message': 'User not found'}), 404

        # Verify password
        if not bcrypt.checkpw(password.encode('utf-8'), user['password_hash'].encode('utf-8')):
            return jsonify({'success': False, 'message': 'Password is incorrect'}), 401

        logger.info(f"Deleting account for user {request.user_id}")

        # Delete user documents from vector store
        try:
            user_docs = rag_system.list_documents(user_id=request.user_id)
            for doc in user_docs:
                rag_system.delete_document(doc['name'], user_id=request.user_id)
            logger.info(f"Deleted {len(user_docs)} documents from vector store")
        except Exception as e:
            logger.warning(f"Error deleting documents from vector store: {e}")

        # Clear user cache
        try:
            cache_pattern = f"*_{request.user_id}"
            # Redis cache will auto-expire user's cached queries
            logger.info("User cache will auto-expire")
        except Exception as e:
            logger.warning(f"Error clearing user cache: {e}")

        # Delete user from database (cascades to related tables)
        success = db.delete_user(request.user_id)

        if success:
            logger.info(f"Account deleted successfully for user {request.user_id}")
            add_breadcrumb('Account deleted', category='auth', data={'user_id': request.user_id})
            analytics.track_event(request.user_id, 'account_deleted')

            return jsonify({
                'success': True,
                'message': 'Account deleted successfully. We\'re sorry to see you go!'
            })
        else:
            return jsonify({'success': False, 'message': 'Failed to delete account'}), 500

    except Exception as e:
        logger.error(f"Delete account error: {str(e)}")
        capture_exception(e, {'endpoint': 'delete_account'})
        return jsonify({'success': False, 'message': 'An error occurred'}), 500


# ============= FEEDBACK ENDPOINT =============

@app.route('/feedback', methods=['POST'])
@require_auth
def submit_feedback():
    """Submit feedback for an AI response"""
    try:
        data = request.json
        message_id = data.get('message_id')
        query = data.get('query', '')
        response = data.get('response', '')
        rating = data.get('rating')  # 1 or -1
        comment = data.get('comment', '')

        if not message_id or rating not in [1, -1]:
            return jsonify({'success': False, 'message': 'Invalid feedback data'}), 400

        # Save feedback
        success = db.save_feedback(
            user_id=request.user_id,
            message_id=message_id,
            query=query,
            response=response,
            rating=rating,
            comment=comment
        )

        if success:
            # Track feedback event
            analytics.track_feedback(request.user_id, rating, bool(comment))
            add_breadcrumb('Feedback submitted', category='feedback', data={'rating': rating})

            logger.info(f"Feedback submitted by user {request.user_id}: {rating}")
            return jsonify({'success': True, 'message': 'Feedback submitted successfully'})
        else:
            return jsonify({'success': False, 'message': 'Failed to save feedback'}), 500

    except Exception as e:
        logger.error(f"Feedback error: {str(e)}")
        capture_exception(e, {'endpoint': 'feedback'})
        return jsonify({'success': False, 'message': str(e)}), 500


# ============= USER STATS ENDPOINT =============

@app.route('/user/stats', methods=['GET'])
@require_auth
def get_user_stats():
    """Get user statistics"""
    try:
        stats = analytics.get_user_stats(request.user_id)

        # Get current plan
        plan = db.get_user_plan(request.user_id)
        if plan:
            stats['plan'] = {
                'type': plan['plan_type'],
                'max_documents': plan['max_documents'],
                'max_queries_per_day': plan['max_queries_per_day']
            }

        return jsonify({'success': True, 'stats': stats})

    except Exception as e:
        logger.error(f"Get user stats error: {str(e)}")
        capture_exception(e, {'endpoint': 'user_stats'})
        return jsonify({'success': False, 'message': str(e)}), 500


# ============= END AUTHENTICATION ENDPOINTS =============

@app.route('/upload', methods=['POST'])
@require_auth
def upload_pdf():
    if 'file' not in request.files:
        return jsonify({'success': False, 'message': 'No file uploaded'})

    file = request.files['file']
    if file.filename == '':
        return jsonify({'success': False, 'message': 'No file selected'})

    if not file.filename.endswith('.pdf'):
        return jsonify({'success': False, 'message': 'Only PDF files are allowed'})

    try:
        # Get user_id from JWT
        user_id = request.user_id

        # Check document limit (beta: 5 docs per user)
        current_docs = rag_system.list_documents(user_id=user_id)
        doc_limit = user_limits.check_document_limit(user_id, len(current_docs))

        if not doc_limit['allowed']:
            return jsonify({
                'success': False,
                'message': doc_limit['message'],
                'limit_reached': True,
                'limits': doc_limit
            }), 403

        # Check file size (beta: 10MB max)
        file.seek(0, 2)  # Seek to end
        file_size = file.tell()
        file.seek(0)  # Reset to beginning

        size_check = user_limits.check_file_size(file_size, file.filename)

        if not size_check['allowed']:
            return jsonify({
                'success': False,
                'message': size_check['message'],
                'file_too_large': True,
                'limits': size_check
            }), 413

        # Save file
        filename = secure_filename(file.filename)
        os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)

        # Process document with user_id for multi-tenancy
        result = rag_system.add_document(filepath, user_id=user_id)

        if result['success']:
            stats = result['statistics']
            return jsonify({
                'success': True,
                'message': f"Successfully added {result['document_name']}",
                'statistics': stats
            })
        else:
            return jsonify({'success': False, 'message': result['message']})

    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

@app.route('/ask', methods=['POST'])
@require_auth
def ask_question():
    data = request.json
    question = data.get('question', '').strip()
    document_name = data.get('document_name')  # Optional document filter
    language = data.get('language', 'auto')  # Optional language for TTS ('auto', 'en', 'hi', 'kn')

    if not question:
        return jsonify({'success': False, 'message': 'Please enter a question'})

    try:
        # Get user_id from JWT
        user_id = request.user_id

        # Query limit check (beta: 50 queries/day)
        query_limit = user_limits.check_query_limit(user_id)

        if not query_limit['allowed']:
            return jsonify({
                'success': False,
                'message': query_limit['message'],
                'limit_reached': True,
                'limits': query_limit
            }), 429

        # Check if user has uploaded any documents
        user_documents = rag_system.list_documents(user_id=user_id)
        if not user_documents or len(user_documents) == 0:
            return jsonify({
                'success': False,
                'message': 'Please upload at least one PDF document before asking questions.',
                'no_documents': True
            })

        # Get conversation history from Redis
        conversation_history = rag_system.cache.get_user_conversation(user_id)

        # Get response with user_id filtering for multi-tenancy
        response = rag_system.query(
            question,
            conversation_history,
            document_name=document_name,
            user_id=user_id
        )

        # Update conversation history and save to Redis
        conversation_history.append(question)
        conversation_history.append(response['answer'])
        rag_system.cache.save_user_conversation(user_id, conversation_history)

        # Generate unique audio ID for this response
        import hashlib
        from concurrent.futures import ThreadPoolExecutor
        import threading

        audio_id = hashlib.md5(response['answer'].encode()).hexdigest()[:12]
        audio_filename = f"auto_{audio_id}.wav"
        audio_url = f"/audio/{audio_filename}"

        # Use thread pool for better resource management
        if not hasattr(app, 'tts_executor'):
            app.tts_executor = ThreadPoolExecutor(max_workers=3, thread_name_prefix='tts-worker')

        # Start audio generation in background thread (non-blocking)
        def generate_audio_background():
            try:
                logger.info(f"🎵 Background: Generating audio for response (ID: {audio_id}, language: {language})...")
                tts_result = tts_handler.synthesize(
                    response['answer'],
                    language=language,  # Support multilingual TTS
                    output_filename=f"auto_{audio_id}"
                )
                logger.info(f"✅ Background: Audio ready at {audio_url} ({tts_result.get('engine', 'unknown')})")
            except Exception as tts_error:
                logger.error(f"❌ Background: TTS generation failed: {tts_error}")
                capture_exception(tts_error, {'context': 'background_tts', 'audio_id': audio_id})

        # Submit to thread pool instead of creating new threads
        app.tts_executor.submit(generate_audio_background)

        result_payload = {
            'success': True,
            'answer': response['answer'],
            'metadata': {
                'sources_used': response.get('sources_used', 0),
                'confidence': response.get('confidence', 0),
                'query_type': response.get('query_type', 'unknown'),
                'cached': response.get('cached', False)
            },
            'limits': {
                'queries_remaining': query_limit['remaining'],
                'queries_limit': query_limit['limit']
            },
            'audio': {
                'url': audio_url,
                'generating': True,  # Indicates audio is being generated
                'audio_id': audio_id
            }
        }

        return jsonify(result_payload)

    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

@app.route('/clear', methods=['POST'])
@require_auth
def clear_conversation():
    """Clear user's conversation history"""
    user_id = request.user_id
    # Clear conversation from Redis
    rag_system.cache.clear_user_conversation(user_id)
    rag_system.clear_conversation_history()
    return jsonify({'success': True, 'message': 'Conversation cleared'})

@app.route('/stats', methods=['GET'])
def get_stats():
    try:
        stats = rag_system.get_system_stats()
        return jsonify({'success': True, 'stats': stats})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

@app.route('/limits', methods=['GET'])
@require_auth
def get_user_limits():
    """Get user's current usage and limits"""
    try:
        user_id = request.user_id

        # Get current document count
        current_docs = rag_system.list_documents(user_id=user_id)
        document_count = len(current_docs)

        # Get comprehensive usage stats
        usage_stats = user_limits.get_user_usage_stats(user_id, document_count)

        return jsonify({
            'success': True,
            'usage': usage_stats,
            'beta_info': {
                'message': 'These are beta limits and may change.',
                'upgrade_available': False  # Future: paid plans
            }
        })

    except Exception as e:
        logger.error(f"Get limits error: {str(e)}")
        return jsonify({'success': False, 'message': str(e)})

@app.route('/transcribe', methods=['POST'])
def transcribe_audio():
    """Convert speech to text"""
    try:
        if 'audio' not in request.files:
            return jsonify({'success': False, 'message': 'No audio file provided'})
        
        audio_file = request.files['audio']
        if audio_file.filename == '':
            return jsonify({'success': False, 'message': 'No file selected'})
        
        # Get language parameter (optional)
        language = request.form.get('language', None)
        
        # Read audio bytes
        audio_bytes = audio_file.read()
        
        logger.info(f"Transcribing audio file: {audio_file.filename}")
        
        # Transcribe
        result = stt_handler.transcribe_from_bytes(audio_bytes, language)
        
        return jsonify({
            'success': True,
            'text': result['text'],
            'language': result['language'],
            'duration': result['duration']
        })
        
    except Exception as e:
        logger.error(f"Transcription error: {str(e)}")
        return jsonify({'success': False, 'message': str(e)})

@app.route('/speak', methods=['POST'])
@require_auth
def text_to_speech():
    """Convert text to speech with multilingual support and user preferences"""
    try:
        user_id = request.user_id
        data = request.json
        text = data.get('text', '').strip()
        language = data.get('language', 'auto')  # 'auto', 'en', 'hi', 'kn', etc.
        engine_preference = data.get('engine', None)  # Optional: 'auto', 'gtts', 'azure', 'coqui'

        if not text:
            return jsonify({'success': False, 'message': 'No text provided'})

        # Get user's voice preferences if no engine specified
        if not engine_preference:
            try:
                user_prefs = db.get_voice_preferences(user_id)
                if user_prefs:
                    engine_preference = user_prefs['engine_preference']
                else:
                    engine_preference = 'auto'
            except Exception as e:
                logger.warning(f"Could not fetch user voice preferences: {e}")
                engine_preference = 'auto'

        # Check user's plan for engine restrictions
        user_plan = db.get_user_plan(user_id)

        # Free users can only use 'auto' mode (which may use Azure automatically)
        # Paid users can explicitly choose Azure
        if user_plan and user_plan['plan_type'] == 'free' and engine_preference == 'azure':
            logger.info(f"Free user tried to use Azure explicitly, using auto mode")
            engine_preference = 'auto'

        logger.info(f"Synthesizing speech for {len(text)} characters (language: {language}, engine: {engine_preference})")

        # Synthesize speech with language and engine preference
        result = tts_handler.synthesize(text, language=language, engine_preference=engine_preference)

        return jsonify({
            'success': True,
            'audio_url': f"/audio/{result['filename']}",
            'duration': result['duration'],
            'filename': result['filename'],
            'language': result.get('language', 'unknown'),
            'language_name': result.get('language_name', 'Unknown'),
            'engine': result.get('engine', 'unknown')
        })

    except Exception as e:
        logger.error(f"TTS error: {str(e)}")
        return jsonify({'success': False, 'message': str(e)})

@app.route('/audio/<filename>', methods=['GET'])
def serve_audio(filename):
    """Serve generated audio files (supports both WAV and MP3)"""
    try:
        audio_path = os.path.join(app.config['AUDIO_FOLDER'], filename)
        if not os.path.exists(audio_path):
            return jsonify({'success': False, 'message': 'Audio file not found'}), 404

        # Determine MIME type based on extension
        mimetype = 'audio/mpeg' if filename.endswith('.mp3') else 'audio/wav'
        return send_file(audio_path, mimetype=mimetype)
    except Exception as e:
        logger.error(f"Audio serve error: {str(e)}")
        return jsonify({'success': False, 'message': str(e)}), 500


@app.route('/tts/languages', methods=['GET'])
def get_supported_languages():
    """Get list of supported TTS languages"""
    try:
        languages = tts_handler.get_supported_languages()
        return jsonify({
            'success': True,
            'languages': languages,
            'total': len(languages)
        })
    except Exception as e:
        logger.error(f"Get languages error: {str(e)}")
        return jsonify({'success': False, 'message': str(e)})


@app.route('/tts/engines', methods=['GET'])
@require_auth
def get_available_engines():
    """Get list of available TTS engines and user's access level"""
    try:
        user_id = request.user_id

        # Get user's plan using Supabase
        user_plan = db.get_user_plan(user_id)
        plan_type = user_plan['plan_type'] if user_plan else 'free'

        # Define engine info
        engines = {
            'auto': {
                'name': 'Auto (Smart Selection)',
                'description': 'Automatically selects the best engine based on language and text',
                'available': True,
                'quality': 'mixed',
                'free': True
            },
            'gtts': {
                'name': 'Google TTS (Standard)',
                'description': 'Free, reliable, supports 100+ languages',
                'available': True,
                'quality': 'good',
                'free': True
            },
            'azure': {
                'name': 'Azure Neural TTS (Premium)',
                'description': 'Best quality neural voices for Kannada, Hindi, and English',
                'available': tts_handler.azure_available,
                'quality': 'excellent',
                'free': False,
                'premium_only': True
            },
            'coqui': {
                'name': 'Coqui TTS (High Quality)',
                'description': 'High quality English voice',
                'available': tts_handler.coqui_available,
                'quality': 'very_good',
                'free': True
            }
        }

        # Free users can't explicitly select Azure
        if plan_type == 'free':
            engines['azure']['accessible'] = False
            engines['azure']['reason'] = 'Premium feature - upgrade to access'
        else:
            engines['azure']['accessible'] = True

        return jsonify({
            'success': True,
            'engines': engines,
            'user_plan': plan_type,
            'azure_configured': tts_handler.azure_available
        })

    except Exception as e:
        logger.error(f"Get engines error: {str(e)}")
        return jsonify({'success': False, 'message': str(e)})


@app.route('/voice/preferences', methods=['GET'])
@require_auth
def get_voice_preferences():
    """Get user's voice preferences"""
    try:
        user_id = request.user_id

        # Get voice preferences using Supabase
        prefs = db.get_voice_preferences(user_id)

        if not prefs:
            # Create default preferences if not exists
            db.update_voice_preferences(user_id, 'auto', 'auto')
            prefs = {
                'engine_preference': 'auto',
                'language_preference': 'auto'
            }

        return jsonify({
            'success': True,
            'preferences': prefs
        })

    except Exception as e:
        logger.error(f"Get voice preferences error: {str(e)}")
        return jsonify({'success': False, 'message': str(e)})


@app.route('/voice/preferences', methods=['PUT'])
@require_auth
def update_voice_preferences_endpoint():
    """Update user's voice preferences"""
    try:
        user_id = request.user_id
        data = request.json

        engine_preference = data.get('engine_preference', 'auto')
        language_preference = data.get('language_preference', 'auto')

        # Validate engine preference
        valid_engines = ['auto', 'gtts', 'azure', 'coqui']
        if engine_preference not in valid_engines:
            return jsonify({'success': False, 'message': f'Invalid engine. Must be one of: {", ".join(valid_engines)}'})

        # Check if user has access to Azure
        if engine_preference == 'azure':
            user_plan = db.get_user_plan(user_id)

            if user_plan and user_plan['plan_type'] == 'free':
                return jsonify({
                    'success': False,
                    'message': 'Azure Neural TTS is a premium feature. Please upgrade your plan.',
                    'premium_required': True
                })

        # Update preferences using Supabase
        success = db.update_voice_preferences(user_id, engine_preference, language_preference)

        if not success:
            return jsonify({'success': False, 'message': 'Failed to update preferences'})

        logger.info(f"Updated voice preferences for user {user_id}: engine={engine_preference}, language={language_preference}")

        return jsonify({
            'success': True,
            'message': 'Voice preferences updated successfully',
            'preferences': {
                'engine_preference': engine_preference,
                'language_preference': language_preference
            }
        })

    except Exception as e:
        logger.error(f"Update voice preferences error: {str(e)}")
        return jsonify({'success': False, 'message': str(e)})


def cleanup_old_audio_files():
    """Delete audio files older than 24 hours to save disk space"""
    try:
        import time
        import glob

        audio_folder = app.config['AUDIO_FOLDER']
        if not os.path.exists(audio_folder):
            return

        current_time = time.time()
        max_age = 24 * 3600  # 24 hours in seconds
        deleted_count = 0

        # Clean up both WAV and MP3 files
        for pattern in ["*.wav", "*.mp3"]:
            for audio_file in glob.glob(os.path.join(audio_folder, pattern)):
                file_age = current_time - os.path.getmtime(audio_file)
                if file_age > max_age:
                    try:
                        os.remove(audio_file)
                        deleted_count += 1
                    except Exception as e:
                        logger.warning(f"Failed to delete old audio file {audio_file}: {e}")

        if deleted_count > 0:
            logger.info(f"🧹 Cleaned up {deleted_count} old audio files")
    except Exception as e:
        logger.error(f"Audio cleanup error: {str(e)}")


# Schedule audio cleanup on startup and periodically
import atexit
from threading import Timer

def schedule_audio_cleanup():
    """Schedule periodic audio cleanup"""
    cleanup_old_audio_files()
    # Schedule next cleanup in 6 hours
    Timer(6 * 3600, schedule_audio_cleanup).start()

# Run cleanup on startup
cleanup_old_audio_files()

# Register cleanup on app shutdown
atexit.register(cleanup_old_audio_files)

@app.route('/voice-query', methods=['POST'])
@require_auth
def voice_query():
    """Complete voice pipeline: audio -> text -> RAG -> text -> audio"""
    try:
        user_id = request.user_id

        if 'audio' not in request.files:
            return jsonify({'success': False, 'message': 'No audio file provided'})

        audio_file = request.files['audio']
        audio_bytes = audio_file.read()

        # Step 1: Transcribe audio to text
        logger.info("Step 1: Transcribing audio...")
        transcription = stt_handler.transcribe_from_bytes(audio_bytes)
        question = transcription['text']

        if not question:
            return jsonify({'success': False, 'message': 'Could not transcribe audio'})

        logger.info(f"Transcribed: {question}")

        # Check if user has uploaded any documents
        user_documents = rag_system.list_documents(user_id=user_id)
        if not user_documents or len(user_documents) == 0:
            return jsonify({
                'success': False,
                'message': 'Please upload at least one PDF document before asking questions.',
                'no_documents': True
            })

        # Step 2: Get RAG response
        logger.info("Step 2: Querying RAG system...")
        conversation_history = rag_system.cache.get_user_conversation(user_id)

        response = rag_system.query(question, conversation_history, user_id=user_id)
        answer = response['answer']

        # Update conversation history and save to Redis
        conversation_history.append(question)
        conversation_history.append(answer)
        rag_system.cache.save_user_conversation(user_id, conversation_history)
        
        logger.info(f"RAG Answer: {answer[:100]}...")
        
        # Step 3: Convert answer to speech
        logger.info("Step 3: Synthesizing speech...")
        tts_result = tts_handler.synthesize(answer)
        
        return jsonify({
            'success': True,
            'question': question,
            'answer': answer,
            'audio_url': f"/audio/{tts_result['filename']}",
            'transcription_language': transcription['language'],
            'metadata': {
                'sources_used': response.get('sources_used', 0),
                'confidence': response.get('confidence', 0),
                'query_type': response.get('query_type', 'unknown')
            }
        })
        
    except Exception as e:
        logger.error(f"Voice query error: {str(e)}")
        return jsonify({'success': False, 'message': str(e)})

@app.route('/documents', methods=['GET'])
@require_auth
def list_documents():
    """List all indexed documents with statistics for current user"""
    try:
        user_id = request.user_id
        documents = rag_system.list_documents(user_id=user_id)
        return jsonify({
            'success': True,
            'documents': documents
        })
    except Exception as e:
        logger.error(f"List documents error: {str(e)}")
        return jsonify({'success': False, 'message': str(e)})

@app.route('/documents/<document_name>', methods=['DELETE'])
@require_auth
def delete_document(document_name):
    """Delete a specific document from the vector store for current user"""
    try:
        user_id = request.user_id
        result = rag_system.delete_document(document_name, user_id=user_id)
        if result['success']:
            return jsonify({
                'success': True,
                'message': f"Deleted {result['deleted_count']} chunks from '{document_name}'"
            })
        else:
            return jsonify(result)
    except Exception as e:
        logger.error(f"Delete document error: {str(e)}")
        return jsonify({'success': False, 'message': str(e)})

@app.route('/documents/clear-all', methods=['POST'])
@require_auth
def clear_all_documents():
    """Clear all documents from the vector store (requires authentication)"""
    try:
        result = rag_system.clear_all_documents()
        if result['success']:
            return jsonify({
                'success': True,
                'message': f"Cleared {result['deleted_count']} documents from the system"
            })
        else:
            return jsonify(result)
    except Exception as e:
        logger.error(f"Clear all documents error: {str(e)}")
        return jsonify({'success': False, 'message': str(e)})

@app.route('/cache/clear', methods=['POST'])
def clear_cache():
    """Clear all cache entries"""
    try:
        result = rag_system.cache.clear_all_cache()
        if result:
            return jsonify({
                'success': True,
                'message': 'Cache cleared successfully'
            })
        else:
            return jsonify({
                'success': False,
                'message': 'Cache not enabled or failed to clear'
            })
    except Exception as e:
        logger.error(f"Clear cache error: {str(e)}")
        return jsonify({'success': False, 'message': str(e)})

@app.route('/cache/stats', methods=['GET'])
def get_cache_stats():
    """Get cache statistics"""
    try:
        stats = rag_system.cache.get_cache_stats()
        return jsonify({
            'success': True,
            'cache': stats
        })
    except Exception as e:
        logger.error(f"Get cache stats error: {str(e)}")
        return jsonify({'success': False, 'message': str(e)})

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint with Redis status"""
    try:
        cache_health = rag_system.cache.health_check()

        return jsonify({
            'success': True,
            'status': 'healthy',
            'components': {
                'rag_system': 'healthy',
                'vector_store': 'healthy',
                'cache': cache_health
            }
        })
    except Exception as e:
        logger.error(f"Health check error: {str(e)}")
        return jsonify({
            'success': False,
            'status': 'unhealthy',
            'message': str(e)
        }), 500

if __name__ == '__main__':
    print("=" * 70)
    print("DocuMind Voice - Multimodal RAG System")
    print("=" * 70)

    # Run database migrations automatically
    print("\n🔄 Checking database migrations...")
    try:
        from src.migrator import run_migrations
        run_migrations()
        print("✅ Database migrations completed successfully\n")
    except Exception as e:
        print(f"⚠️  Migration check failed: {e}")
        print("Continuing with startup...\n")

    print("Configuration:")
    print("  Voice Input: Groq Whisper STT (with fallbacks)")
    print("  Voice Output: Coqui TTS (VITS) - High Quality Neural Speech")
    print("  RAG Engine: Llama-3.1 + MiniLM")
    print("  Vector Store: ChromaDB (Persistent)")
    print(f"  Redis Cache: {rag_system.cache.mode} ({rag_system.cache.enabled and 'enabled' or 'disabled'})")
    print(f"  Beta Limits: {user_limits.MAX_DOCUMENTS_PER_USER} docs, {user_limits.MAX_QUERIES_PER_DAY} queries/day, {user_limits.MAX_FILE_SIZE_MB}MB files")
    print("\n🌐 Open your browser at: http://localhost:8080")
    print("\nEndpoints:")
    print("  POST /auth/signup - User registration")
    print("  POST /auth/login - User login")
    print("  GET  /auth/me - Get current user")
    print("  POST /upload - Upload PDF (requires auth)")
    print("  GET  /documents - List all documents (requires auth)")
    print("  DELETE /documents/<name> - Delete specific document (requires auth)")
    print("  POST /documents/clear-all - Clear all documents (requires auth)")
    print("  POST /ask - Text query (requires auth)")
    print("  POST /transcribe - Audio to text")
    print("  POST /speak - Text to audio")
    print("  POST /voice-query - Complete voice pipeline (requires auth)")
    print("  GET  /limits - Get user limits and usage (requires auth)")
    print("  GET  /stats - System statistics")
    print("  GET  /cache/stats - Cache statistics")
    print("  POST /cache/clear - Clear cache")
    print("  GET  /health - Health check")
    port = int(os.getenv('PORT', 8080))
    # Use 0.0.0.0 for production (allows external connections)
    # Use 127.0.0.1 for local development
    host = '0.0.0.0' if os.getenv('FLASK_ENV') == 'production' else '127.0.0.1'
    app.run(host=host, port=port, debug=False)
