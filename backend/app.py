# app_flask.py - Flask interface for RAG System with Voice Support
from flask import Flask, render_template, request, jsonify, session, send_file
from flask_cors import CORS
import os
from werkzeug.utils import secure_filename
from config.config import Config
from src.rag_system import RAGSystem
from src.stt_handler import STTHandler
from src.coqui_tts_handler import CoquiTTSHandler  # Use Coqui TTS for better quality
from src.database import Database
from src.auth.jwt_handler import generate_jwt, verify_jwt
from src.auth.decorators import require_auth
from src.limits import UserLimits
import bcrypt
import secrets
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# CORS Configuration for production
cors_origins = os.getenv('CORS_ORIGINS', 'http://localhost:5173,http://localhost:3000').split(',')
CORS(app, resources={
    r"/*": {
        "origins": cors_origins,
        "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        "allow_headers": ["Content-Type", "Authorization"],
        "expose_headers": ["Content-Type", "Authorization"],
        "supports_credentials": True
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
rag_system = RAGSystem(Config())
stt_handler = STTHandler()  # Uses Groq Whisper API
tts_handler = CoquiTTSHandler(output_dir=app.config['AUDIO_FOLDER'])  # Coqui TTS with VITS
db = Database()  # Database connection
user_limits = UserLimits(rag_system.cache, db)  # User limits manager

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/voice-test')
def voice_test():
    return render_template('voice_test.html')

# ============= AUTHENTICATION ENDPOINTS =============

@app.route('/auth/signup', methods=['POST'])
def signup():
    """User registration endpoint"""
    try:
        data = request.json
        email = data.get('email', '').strip().lower()
        password = data.get('password', '').strip()

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
        user = db.create_user(email, password_hash)

        # Generate JWT
        token = generate_jwt(user['id'], user['email'])

        return jsonify({
            'success': True,
            'message': 'User created successfully',
            'token': token,
            'user': {
                'id': user['id'],
                'email': user['email']
            }
        })

    except Exception as e:
        logger.error(f"Signup error: {str(e)}")
        return jsonify({'success': False, 'message': str(e)}), 500


@app.route('/auth/login', methods=['POST'])
def login():
    """User login endpoint"""
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

        return jsonify({
            'success': True,
            'message': 'Login successful',
            'token': token,
            'user': {
                'id': user['id'],
                'email': user['email']
            }
        })

    except Exception as e:
        logger.error(f"Login error: {str(e)}")
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

        return jsonify({
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
            }
        })

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
def text_to_speech():
    """Convert text to speech"""
    try:
        data = request.json
        text = data.get('text', '').strip()
        
        if not text:
            return jsonify({'success': False, 'message': 'No text provided'})
        
        logger.info(f"Synthesizing speech for {len(text)} characters")
        
        # Synthesize speech
        result = tts_handler.synthesize(text)
        
        return jsonify({
            'success': True,
            'audio_url': f"/audio/{result['filename']}",
            'duration': result['duration'],
            'filename': result['filename']
        })
        
    except Exception as e:
        logger.error(f"TTS error: {str(e)}")
        return jsonify({'success': False, 'message': str(e)})

@app.route('/audio/<filename>', methods=['GET'])
def serve_audio(filename):
    """Serve generated audio files"""
    try:
        audio_path = os.path.join(app.config['AUDIO_FOLDER'], filename)
        if not os.path.exists(audio_path):
            return jsonify({'success': False, 'message': 'Audio file not found'}), 404
        
        return send_file(audio_path, mimetype='audio/wav')
    except Exception as e:
        logger.error(f"Audio serve error: {str(e)}")
        return jsonify({'success': False, 'message': str(e)}), 500

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
def clear_all_documents():
    """Clear all documents from the vector store"""
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
    print("Starting DocuMind Voice - Multimodal RAG System")
    print("Voice Input: Groq Whisper STT (with fallbacks)")
    print("Voice Output: Coqui TTS (VITS) - High Quality Neural Speech")
    print("RAG Engine: Llama-3.1 + MiniLM")
    print("Vector Store: ChromaDB (Persistent)")
    print(f"Redis Cache: {rag_system.cache.mode} ({rag_system.cache.enabled and 'enabled' or 'disabled'})")
    print(f"Beta Limits: {user_limits.MAX_DOCUMENTS_PER_USER} docs, {user_limits.MAX_QUERIES_PER_DAY} queries/day, {user_limits.MAX_FILE_SIZE_MB}MB files")
    print("Open your browser at: http://localhost:8080")
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
