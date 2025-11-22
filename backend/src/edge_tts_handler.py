# src/edge_tts_handler.py - Microsoft Edge TTS for Indian Regional Languages
"""
EdgeTTS Handler - High-quality TTS for Indian Languages
Supports: Hindi, Kannada, Tamil, Telugu, Malayalam, Bengali, Gujarati, Marathi, and more
Performance: 0.5-1s synthesis time
Quality: Excellent (Microsoft Neural TTS)
"""
import os
import logging
import hashlib
import asyncio
from typing import Dict, Any, Optional
from pathlib import Path

logger = logging.getLogger(__name__)


class EdgeTTSHandler:
    """
    Microsoft Edge TTS handler for high-quality Indian language synthesis

    Supported Languages:
    - Hindi (hi-IN)
    - Kannada (kn-IN)
    - Tamil (ta-IN)
    - Telugu (te-IN)
    - Malayalam (ml-IN)
    - Bengali (bn-IN)
    - Gujarati (gu-IN)
    - Marathi (mr-IN)
    - English (en-IN, en-US)
    """

    # Best voices for Indian languages
    VOICE_MAP = {
        'en': 'en-US-AriaNeural',  # English (US, female, natural)
        'hi': 'hi-IN-SwaraNeural',  # Hindi (female, natural)
        'kn': 'kn-IN-SapnaNeural',  # Kannada (female, natural)
        'ta': 'ta-IN-PallaviNeural',  # Tamil (female, natural)
        'te': 'te-IN-ShrutiNeural',  # Telugu (female, natural)
        'ml': 'ml-IN-SobhanaNeural',  # Malayalam (female, natural)
        'bn': 'bn-IN-TanishaaNeural',  # Bengali (female, natural)
        'gu': 'gu-IN-DhwaniNeural',  # Gujarati (female, natural)
        'mr': 'mr-IN-AarohiNeural',  # Marathi (female, natural)
    }

    def __init__(self, output_dir="./data/audio"):
        """
        Initialize EdgeTTS handler

        Args:
            output_dir: Directory to save generated audio files
        """
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)

        # Check if edge-tts is available
        try:
            import edge_tts
            self.edge_tts = edge_tts
            self.available = True
            logger.info("✓ EdgeTTS initialized (supports HI, KN, TA, TE, and more)")
        except ImportError:
            self.available = False
            logger.warning("EdgeTTS not available. Install: pip install edge-tts")

    def is_available(self) -> bool:
        """Check if EdgeTTS is available"""
        return self.available

    def synthesize(self, text: str, language: str = 'en', output_filename: Optional[str] = None) -> Dict[str, Any]:
        """
        Synthesize speech from text

        Args:
            text: Text to convert to speech
            language: Language code (en, hi, kn, ta, te, etc.)
            output_filename: Optional custom filename (without extension)

        Returns:
            dict with 'audio_path', 'duration', 'text', 'filename'
        """
        if not self.available:
            raise Exception("EdgeTTS not available")

        try:
            if not text or len(text.strip()) == 0:
                raise ValueError("Text cannot be empty")

            # Generate filename
            if output_filename is None:
                text_hash = hashlib.md5(f"{text}{language}".encode()).hexdigest()[:8]
                output_filename = f"edge_tts_{language}_{text_hash}"

            output_path = os.path.join(self.output_dir, f"{output_filename}.mp3")

            # Check if audio already exists (file-based caching)
            if os.path.exists(output_path):
                logger.info(f"Using cached EdgeTTS audio: {output_filename}.mp3")
            else:
                # Get voice for language
                voice = self.VOICE_MAP.get(language, 'en-US-AriaNeural')

                # Generate new audio (run async function in sync context)
                logger.info(f"Synthesizing with EdgeTTS ({voice}): {len(text)} characters")
                asyncio.run(self._synthesize_async(text, voice, output_path))

            # Get audio duration
            duration = self._get_audio_duration(output_path)

            result = {
                'audio_path': output_path,
                'duration': duration,
                'text': text,
                'filename': f"{output_filename}.mp3",
                'language': language,
                'voice': self.VOICE_MAP.get(language, 'en-US-AriaNeural')
            }

            logger.info(f"EdgeTTS synthesis complete. Duration: {duration:.2f}s")
            return result

        except Exception as e:
            logger.error(f"EdgeTTS error: {str(e)}")
            raise Exception(f"Failed to synthesize speech with EdgeTTS: {str(e)}")

    async def _synthesize_async(self, text: str, voice: str, output_path: str):
        """
        Async synthesis (EdgeTTS is async-only)

        Args:
            text: Text to synthesize
            voice: Voice name (e.g., 'hi-IN-SwaraNeural')
            output_path: Path to save audio file
        """
        communicate = self.edge_tts.Communicate(text, voice)
        await communicate.save(output_path)

    def _get_audio_duration(self, audio_path: str) -> float:
        """Get duration of MP3 audio file in seconds"""
        try:
            from mutagen.mp3 import MP3
            audio = MP3(audio_path)
            return audio.info.length
        except ImportError:
            # Fallback: estimate duration (average speech rate ~150 words/min)
            logger.warning("mutagen not installed. Using estimated duration.")
            with open(audio_path, 'rb') as f:
                file_size = len(f.read())
            # Rough estimate: 1 second of MP3 ≈ 16KB at 128kbps
            return file_size / 16000
        except Exception as e:
            logger.warning(f"Could not get audio duration: {str(e)}")
            return 0.0

    @staticmethod
    def get_supported_languages() -> list:
        """Get list of supported language codes"""
        return list(EdgeTTSHandler.VOICE_MAP.keys())

    @staticmethod
    def get_voice_for_language(language: str) -> str:
        """Get recommended voice for language"""
        return EdgeTTSHandler.VOICE_MAP.get(language, 'en-US-AriaNeural')
