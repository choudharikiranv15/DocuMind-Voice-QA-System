# src/stt_handler.py - Speech-to-Text using Groq Whisper API
import os
import tempfile
import logging
from groq import Groq

logger = logging.getLogger(__name__)

class STTHandler:
    """Handles Speech-to-Text conversion using Groq Whisper API"""
    
    def __init__(self, api_key=None):
        """
        Initialize Groq Whisper API client
        
        Args:
            api_key: Groq API key (if None, reads from environment)
        """
        self.api_key = api_key or os.getenv('GROQ_API_KEY')
        if not self.api_key:
            logger.warning("No Groq API key found. STT will not work.")
            self.client = None
        else:
            self.client = Groq(api_key=self.api_key)
            logger.info("STT Handler initialized with Groq Whisper API")
    
    def transcribe(self, audio_file_path, language=None):
        """
        Transcribe audio file to text using Groq Whisper API
        
        Args:
            audio_file_path: Path to audio file (mp3, wav, m4a, etc.)
            language: Optional language code (en, es, fr, etc.)
        
        Returns:
            dict with 'text', 'language', 'duration'
        """
        try:
            if not self.client:
                raise Exception("Groq API key not configured")
            
            logger.info(f"Transcribing audio file: {audio_file_path}")
            
            # Open and transcribe audio file
            with open(audio_file_path, 'rb') as audio_file:
                transcription = self.client.audio.transcriptions.create(
                    file=(os.path.basename(audio_file_path), audio_file.read()),
                    model="whisper-large-v3",
                    language=language,
                    response_format="verbose_json"
                )
            
            result = {
                'text': transcription.text,
                'language': language or 'en',
                'duration': getattr(transcription, 'duration', 0),
                'segments': []
            }
            
            logger.info(f"Transcription complete. Text: {result['text'][:100]}...")
            return result
            
        except Exception as e:
            logger.error(f"Transcription error: {str(e)}")
            raise Exception(f"Failed to transcribe audio: {str(e)}")
    
    def transcribe_from_bytes(self, audio_bytes, language=None):
        """
        Transcribe audio from bytes (for uploaded files)
        
        Args:
            audio_bytes: Audio file content as bytes
            language: Optional language code
        
        Returns:
            dict with transcription results
        """
        # Save to temporary file
        with tempfile.NamedTemporaryFile(delete=False, suffix='.wav') as temp_file:
            temp_file.write(audio_bytes)
            temp_path = temp_file.name
        
        try:
            result = self.transcribe(temp_path, language)
            return result
        finally:
            # Clean up temp file
            if os.path.exists(temp_path):
                os.remove(temp_path)
