# backend/src/stt_handler.py - Enhanced Speech-to-Text with fallback options
import os
import tempfile
import logging
from groq import Groq

logger = logging.getLogger(__name__)

class STTHandler:
    """
    Enhanced Speech-to-Text handler with multiple fallback options
    
    Priority order:
    1. Groq Whisper API (primary - best quality)
    2. OpenAI Whisper API (fallback 1)
    3. Google Speech Recognition (fallback 2 - free but requires internet)
    """
    
    def __init__(self, groq_api_key=None, openai_api_key=None):
        """
        Initialize STT Handler with multiple API options
        
        Args:
            groq_api_key: Groq API key (if None, reads from environment)
            openai_api_key: OpenAI API key for fallback (if None, reads from environment)
        """
        # Primary: Groq Whisper
        self.groq_api_key = groq_api_key or os.getenv('GROQ_API_KEY')
        self.groq_client = None
        if self.groq_api_key:
            try:
                self.groq_client = Groq(api_key=self.groq_api_key)
                logger.info("✅ Groq Whisper API initialized (primary)")
            except Exception as e:
                logger.warning(f"⚠️  Groq initialization failed: {str(e)}")
        
        # Fallback 1: OpenAI Whisper
        self.openai_api_key = openai_api_key or os.getenv('OPENAI_API_KEY')
        self.openai_client = None
        if self.openai_api_key:
            try:
                from openai import OpenAI
                self.openai_client = OpenAI(api_key=self.openai_api_key)
                logger.info("✅ OpenAI Whisper API initialized (fallback 1)")
            except ImportError:
                logger.warning("⚠️  OpenAI package not installed. Install with: pip install openai")
            except Exception as e:
                logger.warning(f"⚠️  OpenAI initialization failed: {str(e)}")
        
        # Fallback 2: Google Speech Recognition (free)
        self.google_sr_available = False
        try:
            import speech_recognition as sr
            self.recognizer = sr.Recognizer()
            self.google_sr_available = True
            logger.info("✅ Google Speech Recognition initialized (fallback 2)")
        except ImportError:
            logger.warning("⚠️  speech_recognition not installed. Install with: pip install SpeechRecognition")
        
        if not any([self.groq_client, self.openai_client, self.google_sr_available]):
            logger.error("❌ No STT service available! Please configure at least one API key.")
    
    def transcribe(self, audio_file_path, language=None):
        """
        Transcribe audio file to text with automatic fallback
        
        Args:
            audio_file_path: Path to audio file (mp3, wav, m4a, etc.)
            language: Optional language code (en, es, fr, etc.)
        
        Returns:
            dict with 'text', 'language', 'duration', 'service_used'
        """
        # Try Groq first (best quality)
        if self.groq_client:
            try:
                return self._transcribe_with_groq(audio_file_path, language)
            except Exception as e:
                logger.warning(f"⚠️  Groq transcription failed: {str(e)}, trying fallback...")
        
        # Try OpenAI Whisper
        if self.openai_client:
            try:
                return self._transcribe_with_openai(audio_file_path, language)
            except Exception as e:
                logger.warning(f"⚠️  OpenAI transcription failed: {str(e)}, trying fallback...")
        
        # Try Google Speech Recognition
        if self.google_sr_available:
            try:
                return self._transcribe_with_google(audio_file_path, language)
            except Exception as e:
                logger.error(f"❌ Google SR transcription failed: {str(e)}")
        
        raise Exception("All STT services failed. Please check your API keys and internet connection.")
    
    def _transcribe_with_groq(self, audio_file_path, language=None):
        """Transcribe using Groq Whisper API (primary method) - English only"""
        logger.info(f"🎤 Transcribing with Groq Whisper: {audio_file_path}")

        with open(audio_file_path, 'rb') as audio_file:
            # Use whisper-large-v3-turbo for better accuracy and speed
            # Force English language for better accuracy (user input is always in English)
            transcription = self.groq_client.audio.transcriptions.create(
                file=(os.path.basename(audio_file_path), audio_file.read()),
                model="whisper-large-v3-turbo",  # Better model
                language="en",  # Always English - user input requirement
                response_format="verbose_json",
                temperature=0.0  # More deterministic output
            )
        
        result = {
            'text': transcription.text.strip(),
            'language': language or getattr(transcription, 'language', 'en'),
            'duration': getattr(transcription, 'duration', 0),
            'segments': [],
            'service_used': 'groq_whisper'
        }
        
        logger.info(f"✅ Groq transcription: '{result['text'][:100]}...'")
        return result
    
    def _transcribe_with_openai(self, audio_file_path, language=None):
        """Transcribe using OpenAI Whisper API (fallback 1) - English only"""
        logger.info(f"🎤 Transcribing with OpenAI Whisper: {audio_file_path}")

        with open(audio_file_path, 'rb') as audio_file:
            transcription = self.openai_client.audio.transcriptions.create(
                file=audio_file,
                model="whisper-1",
                language="en",  # Always English - user input requirement
                response_format="verbose_json",
                temperature=0.0
            )
        
        result = {
            'text': transcription.text.strip(),
            'language': language or getattr(transcription, 'language', 'en'),
            'duration': getattr(transcription, 'duration', 0),
            'segments': [],
            'service_used': 'openai_whisper'
        }
        
        logger.info(f"✅ OpenAI transcription: '{result['text'][:100]}...'")
        return result
    
    def _transcribe_with_google(self, audio_file_path, language=None):
        """Transcribe using Google Speech Recognition (fallback 2 - free)"""
        logger.info(f"🎤 Transcribing with Google SR: {audio_file_path}")
        
        import speech_recognition as sr
        
        # Convert audio to WAV if needed
        audio_file = sr.AudioFile(audio_file_path)
        
        with audio_file as source:
            audio_data = self.recognizer.record(source)
        
        # Transcribe
        text = self.recognizer.recognize_google(
            audio_data,
            language=language or 'en-US',
            show_all=False
        )
        
        result = {
            'text': text.strip(),
            'language': language or 'en',
            'duration': 0,
            'segments': [],
            'service_used': 'google_sr'
        }
        
        logger.info(f"✅ Google SR transcription: '{result['text'][:100]}...'")
        return result
    
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
    
    def get_available_services(self):
        """Get list of available STT services"""
        services = []
        if self.groq_client:
            services.append('groq_whisper')
        if self.openai_client:
            services.append('openai_whisper')
        if self.google_sr_available:
            services.append('google_sr')
        return services
