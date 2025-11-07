# app_flask.py - Flask interface for RAG System with Voice Support
from flask import Flask, render_template, request, jsonify, session, send_file
from flask_cors import CORS
import os
from werkzeug.utils import secure_filename
from config.config import Config
from src.rag_system import RAGSystem
from src.stt_handler import STTHandler
from src.tts_handler import TTSHandler
import secrets
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)  # Enable CORS for frontend
app.secret_key = secrets.token_hex(16)
app.config['UPLOAD_FOLDER'] = './data/pdfs'
app.config['AUDIO_FOLDER'] = './data/audio'
app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024  # 50MB max

# Create necessary directories
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(app.config['AUDIO_FOLDER'], exist_ok=True)

# Initialize systems
rag_system = RAGSystem(Config())
stt_handler = STTHandler(model_size="base")  # base model for speed
tts_handler = TTSHandler(output_dir=app.config['AUDIO_FOLDER'])

# Store conversation history per session
conversations = {}

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/voice-test')
def voice_test():
    return render_template('voice_test.html')

@app.route('/upload', methods=['POST'])
def upload_pdf():
    if 'file' not in request.files:
        return jsonify({'success': False, 'message': 'No file uploaded'})
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'success': False, 'message': 'No file selected'})
    
    if not file.filename.endswith('.pdf'):
        return jsonify({'success': False, 'message': 'Only PDF files are allowed'})
    
    try:
        # Save file
        filename = secure_filename(file.filename)
        os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        
        # Process document
        result = rag_system.add_document(filepath)
        
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
def ask_question():
    data = request.json
    question = data.get('question', '').strip()
    
    if not question:
        return jsonify({'success': False, 'message': 'Please enter a question'})
    
    try:
        # Get or create conversation history for this session
        session_id = session.get('session_id')
        if not session_id:
            session_id = secrets.token_hex(8)
            session['session_id'] = session_id
        
        if session_id not in conversations:
            conversations[session_id] = []
        
        # Get response
        response = rag_system.query(question, conversations[session_id])
        
        # Update conversation history
        conversations[session_id].append(question)
        conversations[session_id].append(response['answer'])
        
        return jsonify({
            'success': True,
            'answer': response['answer'],
            'metadata': {
                'sources_used': response.get('sources_used', 0),
                'confidence': response.get('confidence', 0),
                'query_type': response.get('query_type', 'unknown')
            }
        })
        
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

@app.route('/clear', methods=['POST'])
def clear_conversation():
    session_id = session.get('session_id')
    if session_id and session_id in conversations:
        conversations[session_id] = []
    rag_system.clear_conversation_history()
    return jsonify({'success': True})

@app.route('/stats', methods=['GET'])
def get_stats():
    try:
        stats = rag_system.get_system_stats()
        return jsonify({'success': True, 'stats': stats})
    except Exception as e:
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
def voice_query():
    """Complete voice pipeline: audio -> text -> RAG -> text -> audio"""
    try:
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
        
        # Step 2: Get RAG response
        logger.info("Step 2: Querying RAG system...")
        session_id = session.get('session_id')
        if not session_id:
            session_id = secrets.token_hex(8)
            session['session_id'] = session_id
        
        if session_id not in conversations:
            conversations[session_id] = []
        
        response = rag_system.query(question, conversations[session_id])
        answer = response['answer']
        
        # Update conversation history
        conversations[session_id].append(question)
        conversations[session_id].append(answer)
        
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

if __name__ == '__main__':
    print("🚀 Starting DocuMind Voice - Multimodal RAG System")
    print("🎤 Voice Input: Faster-Whisper STT")
    print("🔊 Voice Output: Piper TTS")
    print("🧠 RAG Engine: Llama-3.1 + MiniLM")
    print("🌐 Open your browser at: http://localhost:8080")
    print("\nEndpoints:")
    print("  POST /upload - Upload PDF")
    print("  POST /ask - Text query")
    print("  POST /transcribe - Audio to text")
    print("  POST /speak - Text to audio")
    print("  POST /voice-query - Complete voice pipeline")
    app.run(host='127.0.0.1', port=8080, debug=False)
