# src/coqui_tts_handler.py - Text-to-Speech using Coqui TTS (VITS)
"""
High-quality Text-to-Speech using Coqui TTS with VITS models.
Much better voice quality than gTTS - natural, human-like speech.
"""
import os
import logging
import hashlib
from pathlib import Path

logger = logging.getLogger(__name__)


class CoquiTTSHandler:
    """Handles Text-to-Speech conversion using Coqui TTS with VITS model"""

    def __init__(self, output_dir="./data/audio", model_name="tts_models/en/ljspeech/vits"):
        """
        Initialize Coqui TTS handler

        Args:
            output_dir: Directory to save generated audio files
            model_name: Coqui TTS model to use
                       Options:
                       - tts_models/en/ljspeech/vits (female, high quality)
                       - tts_models/en/vctk/vits (multi-speaker)
                       - tts_models/en/jenny/jenny (neural, very natural)
        """
        self.output_dir = output_dir
        self.model_name = model_name
        os.makedirs(output_dir, exist_ok=True)

        # Lazy load TTS to avoid initialization errors
        self.tts = None
        self.initialized = False

        logger.info(f"Coqui TTS Handler created with model: {model_name}")

    def _initialize_tts(self):
        """Lazy initialization of TTS model"""
        if self.initialized:
            return True

        try:
            from TTS.api import TTS

            logger.info(f"Loading Coqui TTS model: {self.model_name}")
            logger.info("First run may take a few minutes to download model...")

            # Initialize TTS
            self.tts = TTS(model_name=self.model_name, progress_bar=True)

            # Set to GPU if available
            if hasattr(self.tts, 'to'):
                try:
                    import torch
                    if torch.cuda.is_available():
                        self.tts.to('cuda')
                        logger.info("✓ Using GPU acceleration")
                    else:
                        logger.info("✓ Using CPU (GPU not available)")
                except:
                    logger.info("✓ Using CPU")

            self.initialized = True
            logger.info("✓ Coqui TTS model loaded successfully!")
            return True

        except ImportError:
            logger.error("Coqui TTS not installed! Install with: pip install TTS")
            return False
        except Exception as e:
            logger.error(f"Failed to initialize Coqui TTS: {str(e)}")
            return False

    def synthesize(self, text, output_filename=None, speaker=None):
        """
        Convert text to speech with high-quality Coqui TTS

        Args:
            text: Text to convert to speech
            output_filename: Optional custom filename (without extension)
            speaker: Optional speaker name for multi-speaker models

        Returns:
            dict with 'audio_path', 'duration', 'text', 'filename'
        """
        try:
            if not text or len(text.strip()) == 0:
                raise ValueError("Text cannot be empty")

            # Initialize TTS if needed
            if not self._initialize_tts():
                # Fallback to gTTS if Coqui fails
                logger.warning("Falling back to gTTS")
                return self._synthesize_with_gtts(text, output_filename)

            # Generate filename
            if output_filename is None:
                text_hash = hashlib.md5(text.encode()).hexdigest()[:8]
                output_filename = f"coqui_{text_hash}"

            output_path = os.path.join(self.output_dir, f"{output_filename}.wav")

            # Synthesize with Coqui TTS
            logger.info(f"Synthesizing speech with Coqui TTS: {len(text)} characters")

            # Run TTS
            if speaker and hasattr(self.tts, 'speakers'):
                # Multi-speaker model
                self.tts.tts_to_file(
                    text=text,
                    speaker=speaker,
                    file_path=output_path
                )
            else:
                # Single-speaker model
                self.tts.tts_to_file(
                    text=text,
                    file_path=output_path
                )

            # Get audio duration
            duration = self._get_audio_duration(output_path)

            result = {
                'audio_path': output_path,
                'duration': duration,
                'text': text,
                'filename': f"{output_filename}.wav",
                'model': self.model_name
            }

            logger.info(f"✓ Coqui TTS synthesis complete. Duration: {duration:.2f}s")
            return result

        except Exception as e:
            logger.error(f"Coqui TTS error: {str(e)}")
            logger.warning("Falling back to gTTS due to error")
            return self._synthesize_with_gtts(text, output_filename)

    def _synthesize_with_gtts(self, text, output_filename=None):
        """Fallback to gTTS if Coqui fails"""
        try:
            from gtts import gTTS

            if output_filename is None:
                text_hash = hashlib.md5(text.encode()).hexdigest()[:8]
                output_filename = f"gtts_{text_hash}"

            output_path = os.path.join(self.output_dir, f"{output_filename}.wav")

            logger.info(f"Synthesizing with gTTS fallback: {len(text)} characters")
            tts = gTTS(text=text, lang='en', slow=False)
            tts.save(output_path)

            duration = self._get_audio_duration(output_path)

            return {
                'audio_path': output_path,
                'duration': duration,
                'text': text,
                'filename': f"{output_filename}.wav",
                'model': 'gTTS (fallback)'
            }

        except Exception as e:
            logger.error(f"gTTS fallback also failed: {str(e)}")
            raise Exception(f"All TTS methods failed: {str(e)}")

    def _get_audio_duration(self, audio_path):
        """Get duration of audio file in seconds"""
        try:
            import wave
            with wave.open(audio_path, 'r') as wav_file:
                frames = wav_file.getnframes()
                rate = wav_file.getframerate()
                duration = frames / float(rate)
                return duration
        except Exception as e:
            logger.warning(f"Could not get audio duration: {str(e)}")
            return 0.0

    def list_available_speakers(self):
        """List available speakers for multi-speaker models"""
        try:
            if not self.initialized:
                self._initialize_tts()

            if hasattr(self.tts, 'speakers') and self.tts.speakers:
                return self.tts.speakers
            else:
                return []
        except:
            return []

    def list_available_models(self):
        """List all available Coqui TTS models"""
        try:
            from TTS.api import TTS
            return TTS().list_models()
        except:
            return []

    def synthesize_streaming(self, text):
        """
        Synthesize speech in streaming mode (for future WebSocket support)

        Args:
            text: Text to convert to speech

        Yields:
            Audio chunks
        """
        # Coqui TTS doesn't natively support streaming yet
        # Generate full audio and stream it in chunks
        result = self.synthesize(text)
        chunk_size = 4096

        with open(result['audio_path'], 'rb') as f:
            while True:
                chunk = f.read(chunk_size)
                if not chunk:
                    break
                yield chunk
