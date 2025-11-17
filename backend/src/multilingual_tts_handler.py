# src/multilingual_tts_handler.py - Multilingual TTS with gTTS (primary) + Coqui (fallback)
"""
Multilingual Text-to-Speech Handler
- Primary: gTTS (supports 100+ languages including Hindi, Kannada)
- Fallback: Coqui TTS (for English only, better quality)
- Memory efficient for Render free tier (512MB RAM)
"""
import os
import logging
import hashlib
from typing import Dict, Any, Optional
from gtts import gTTS
from pathlib import Path

logger = logging.getLogger(__name__)


class MultilingualTTSHandler:
    """
    Multilingual TTS handler with gTTS as primary and Coqui as fallback

    Supported Languages:
    - English (en)
    - Hindi (hi)
    - Kannada (kn)
    - Tamil (ta)
    - Telugu (te)
    - And 100+ more via gTTS
    """

    # Language codes supported by gTTS
    SUPPORTED_LANGUAGES = {
        'en': 'English',
        'hi': 'Hindi',
        'kn': 'Kannada',
        'ta': 'Tamil',
        'te': 'Telugu',
        'mr': 'Marathi',
        'bn': 'Bengali',
        'gu': 'Gujarati',
        'ml': 'Malayalam',
        'pa': 'Punjabi',
        'ur': 'Urdu',
        # Add more as needed
    }

    def __init__(self, output_dir="./data/audio", enable_coqui_fallback=True):
        """
        Initialize multilingual TTS handler

        Args:
            output_dir: Directory to save generated audio files
            enable_coqui_fallback: Enable Coqui TTS as fallback for English (default: True)
        """
        self.output_dir = output_dir
        self.enable_coqui_fallback = enable_coqui_fallback
        os.makedirs(output_dir, exist_ok=True)

        # Initialize Coqui fallback (lazy loading)
        self.coqui_handler = None
        self.coqui_available = False

        if enable_coqui_fallback:
            try:
                from src.coqui_tts_handler import CoquiTTSHandler
                self.coqui_handler = CoquiTTSHandler(output_dir=output_dir)
                logger.info("✓ Coqui TTS available as fallback for English")
                self.coqui_available = True
            except Exception as e:
                logger.warning(f"Coqui TTS not available: {e}. Using gTTS for all languages.")
                self.coqui_available = False

        logger.info(f"Multilingual TTS Handler initialized (gTTS primary, Coqui fallback: {self.coqui_available})")

    def detect_language(self, text: str) -> str:
        """
        Auto-detect language from text

        Args:
            text: Input text

        Returns:
            Language code (e.g., 'en', 'hi', 'kn')
        """
        try:
            from langdetect import detect
            detected = detect(text)

            # Map langdetect codes to gTTS codes
            lang_mapping = {
                'en': 'en',
                'hi': 'hi',
                'kn': 'kn',
                'ta': 'ta',
                'te': 'te',
                'mr': 'mr',
                'bn': 'bn',
                'gu': 'gu',
                'ml': 'ml',
                'pa': 'pa',
                'ur': 'ur',
            }

            result = lang_mapping.get(detected, 'en')
            logger.info(f"Detected language: {result} ({self.SUPPORTED_LANGUAGES.get(result, 'Unknown')})")
            return result

        except ImportError:
            logger.warning("langdetect not installed. Install with: pip install langdetect")
            logger.info("Defaulting to English")
            return 'en'
        except Exception as e:
            logger.warning(f"Language detection failed: {e}. Defaulting to English")
            return 'en'

    def synthesize(self, text: str, language: str = 'auto', output_filename: Optional[str] = None) -> Dict[str, Any]:
        """
        Convert text to speech using gTTS (primary) or Coqui (fallback)

        Args:
            text: Text to convert to speech
            language: Language code ('en', 'hi', 'kn', 'auto' for auto-detection)
            output_filename: Optional custom filename (without extension)

        Returns:
            dict with 'audio_path', 'duration', 'text', 'filename', 'language', 'engine'
        """
        try:
            if not text or len(text.strip()) == 0:
                raise ValueError("Text cannot be empty")

            # Auto-detect language if requested
            if language == 'auto':
                language = self.detect_language(text)

            # Validate language
            if language not in self.SUPPORTED_LANGUAGES and language != 'en':
                logger.warning(f"Unsupported language: {language}. Defaulting to English")
                language = 'en'

            # Clean text for TTS
            cleaned_text = self._clean_text_for_tts(text)

            # Decide which engine to use
            use_coqui = (
                language == 'en' and
                self.coqui_available and
                len(cleaned_text) < 500  # Use Coqui only for shorter texts to save time
            )

            if use_coqui:
                logger.info("Using Coqui TTS for English (high quality)")
                return self._synthesize_with_coqui(cleaned_text, output_filename)
            else:
                logger.info(f"Using gTTS for {self.SUPPORTED_LANGUAGES.get(language, language)}")
                return self._synthesize_with_gtts(cleaned_text, language, output_filename)

        except Exception as e:
            logger.error(f"TTS synthesis failed: {e}")
            # Last resort fallback to gTTS English
            logger.warning("Falling back to gTTS English")
            return self._synthesize_with_gtts(text, 'en', output_filename)

    def _synthesize_with_gtts(self, text: str, language: str, output_filename: Optional[str] = None) -> Dict[str, Any]:
        """Synthesize speech using gTTS"""
        try:
            # Generate filename
            if output_filename is None:
                text_hash = hashlib.md5(text.encode()).hexdigest()[:8]
                output_filename = f"gtts_{language}_{text_hash}"

            output_path = os.path.join(self.output_dir, f"{output_filename}.mp3")

            logger.info(f"Synthesizing with gTTS ({language}): {len(text)} characters")

            # Create gTTS object
            tts = gTTS(text=text, lang=language, slow=False)

            # Save to file
            tts.save(output_path)

            # Get audio duration (approximate)
            duration = self._estimate_duration(text, language)

            result = {
                'audio_path': output_path,
                'duration': duration,
                'text': text,
                'filename': f"{output_filename}.mp3",
                'language': language,
                'language_name': self.SUPPORTED_LANGUAGES.get(language, language),
                'engine': 'gTTS'
            }

            logger.info(f"✓ gTTS synthesis complete. Duration: ~{duration:.2f}s")
            return result

        except Exception as e:
            logger.error(f"gTTS synthesis failed: {e}")
            raise

    def _synthesize_with_coqui(self, text: str, output_filename: Optional[str] = None) -> Dict[str, Any]:
        """Synthesize speech using Coqui TTS (English only, fallback)"""
        try:
            if not self.coqui_handler:
                raise Exception("Coqui TTS not available")

            logger.info(f"Synthesizing with Coqui TTS: {len(text)} characters")

            result = self.coqui_handler.synthesize(text, output_filename)
            result['engine'] = 'Coqui TTS'
            result['language'] = 'en'
            result['language_name'] = 'English'

            return result

        except Exception as e:
            logger.error(f"Coqui TTS failed: {e}. Falling back to gTTS")
            return self._synthesize_with_gtts(text, 'en', output_filename)

    def _clean_text_for_tts(self, text: str) -> str:
        """
        Clean text for TTS by removing markdown formatting and special symbols

        Args:
            text: Raw text with possible markdown formatting

        Returns:
            Clean text suitable for TTS
        """
        import re

        # Remove markdown bold/italic: **text** or *text*
        text = re.sub(r'\*\*([^\*]+)\*\*', r'\1', text)
        text = re.sub(r'\*([^\*]+)\*', r'\1', text)

        # Remove markdown headers: ## Header -> Header
        text = re.sub(r'#{1,6}\s+', '', text)

        # Remove page references: (Page X)
        text = re.sub(r'\(Page \d+\)', '', text)

        # Remove backticks: `code`
        text = re.sub(r'`([^`]+)`', r'\1', text)

        # Remove excessive newlines
        text = re.sub(r'\n{3,}', '\n\n', text)

        # Remove bullet points and convert to comma-separated
        text = re.sub(r'\n\s*[-*•]\s+', ', ', text)

        # Remove extra spaces
        text = re.sub(r'\s+', ' ', text)

        return text.strip()

    def _estimate_duration(self, text: str, language: str) -> float:
        """
        Estimate audio duration based on text length and language

        Args:
            text: Input text
            language: Language code

        Returns:
            Estimated duration in seconds
        """
        # Average speaking rates (words per minute)
        wpm_rates = {
            'en': 150,  # English
            'hi': 140,  # Hindi
            'kn': 130,  # Kannada
            'ta': 130,  # Tamil
            'te': 130,  # Telugu
        }

        wpm = wpm_rates.get(language, 140)

        # Estimate word count
        word_count = len(text.split())

        # Calculate duration in seconds
        duration = (word_count / wpm) * 60

        return max(1.0, duration)  # Minimum 1 second

    def get_supported_languages(self) -> Dict[str, str]:
        """Get list of supported languages"""
        return self.SUPPORTED_LANGUAGES.copy()

    def is_language_supported(self, language: str) -> bool:
        """Check if a language is supported"""
        return language in self.SUPPORTED_LANGUAGES
