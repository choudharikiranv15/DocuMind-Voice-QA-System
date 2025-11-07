# src/tts_handler.py - Text-to-Speech using Piper TTS
import os
import tempfile
import subprocess
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

class TTSHandler:
    """Handles Text-to-Speech conversion using Piper TTS"""
    
    def __init__(self, voice="en_US-lessac-medium", output_dir="./data/audio"):
        """
        Initialize Piper TTS handler
        
        Args:
            voice: Voice model to use (en_US-lessac-medium, en_GB-alan-medium, etc.)
            output_dir: Directory to save generated audio files
        """
        self.voice = voice
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)
        
        # Check if piper is installed
        self.piper_available = self._check_piper_installation()
        
        if not self.piper_available:
            logger.warning("Piper TTS not found. Using fallback TTS method.")
        else:
            logger.info(f"TTS Handler initialized with voice: {voice}")
    
    def _check_piper_installation(self):
        """Check if Piper TTS is installed"""
        try:
            result = subprocess.run(
                ['piper', '--version'],
                capture_output=True,
                text=True,
                timeout=5
            )
            return result.returncode == 0
        except (FileNotFoundError, subprocess.TimeoutExpired):
            return False
    
    def synthesize(self, text, output_filename=None):
        """
        Convert text to speech
        
        Args:
            text: Text to convert to speech
            output_filename: Optional custom filename (without extension)
        
        Returns:
            dict with 'audio_path', 'duration', 'text'
        """
        try:
            if not text or len(text.strip()) == 0:
                raise ValueError("Text cannot be empty")
            
            # Generate filename
            if output_filename is None:
                import hashlib
                text_hash = hashlib.md5(text.encode()).hexdigest()[:8]
                output_filename = f"tts_{text_hash}"
            
            output_path = os.path.join(self.output_dir, f"{output_filename}.wav")
            
            if self.piper_available:
                # Use Piper TTS
                logger.info(f"Synthesizing speech with Piper: {len(text)} characters")
                self._synthesize_with_piper(text, output_path)
            else:
                # Fallback: Use gTTS (Google Text-to-Speech) - requires internet
                logger.info(f"Synthesizing speech with gTTS fallback: {len(text)} characters")
                self._synthesize_with_gtts(text, output_path)
            
            # Get audio duration
            duration = self._get_audio_duration(output_path)
            
            result = {
                'audio_path': output_path,
                'duration': duration,
                'text': text,
                'filename': f"{output_filename}.wav"
            }
            
            logger.info(f"Speech synthesis complete. Duration: {duration:.2f}s")
            return result
            
        except Exception as e:
            logger.error(f"TTS error: {str(e)}")
            raise Exception(f"Failed to synthesize speech: {str(e)}")
    
    def _synthesize_with_piper(self, text, output_path):
        """Synthesize using Piper TTS"""
        try:
            # Run piper command
            process = subprocess.Popen(
                ['piper', '--model', self.voice, '--output_file', output_path],
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            stdout, stderr = process.communicate(input=text, timeout=30)
            
            if process.returncode != 0:
                raise Exception(f"Piper TTS failed: {stderr}")
                
        except subprocess.TimeoutExpired:
            process.kill()
            raise Exception("Piper TTS timeout")
    
    def _synthesize_with_gtts(self, text, output_path):
        """Fallback: Synthesize using gTTS (requires internet)"""
        try:
            from gtts import gTTS
            tts = gTTS(text=text, lang='en', slow=False)
            tts.save(output_path)
        except ImportError:
            # If gTTS not available, create a silent audio file as placeholder
            logger.warning("gTTS not available. Creating placeholder audio.")
            self._create_placeholder_audio(output_path)
        except Exception as e:
            logger.error(f"gTTS error: {str(e)}")
            self._create_placeholder_audio(output_path)
    
    def _create_placeholder_audio(self, output_path):
        """Create a placeholder silent audio file"""
        import wave
        import struct
        
        # Create 1 second of silence
        sample_rate = 22050
        duration = 1
        num_samples = sample_rate * duration
        
        with wave.open(output_path, 'w') as wav_file:
            wav_file.setnchannels(1)  # Mono
            wav_file.setsampwidth(2)  # 16-bit
            wav_file.setframerate(sample_rate)
            
            # Write silent samples
            for _ in range(num_samples):
                wav_file.writeframes(struct.pack('h', 0))
    
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
    
    def synthesize_streaming(self, text):
        """
        Synthesize speech in streaming mode (for future WebSocket support)
        
        Args:
            text: Text to convert to speech
        
        Yields:
            Audio chunks
        """
        # TODO: Implement streaming synthesis
        # For now, just return the full audio
        result = self.synthesize(text)
        with open(result['audio_path'], 'rb') as f:
            yield f.read()
