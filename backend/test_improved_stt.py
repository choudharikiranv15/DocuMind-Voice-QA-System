"""Test improved STT with fallback options"""
import sys
sys.path.insert(0, '.')

from src.stt_handler import STTHandler
import os

print("=" * 60)
print("🎤 Testing Improved STT Handler")
print("=" * 60)

# Initialize STT handler
stt = STTHandler()

# Check available services
services = stt.get_available_services()
print(f"\n✅ Available STT services: {', '.join(services)}")

if not services:
    print("\n❌ No STT services available!")
    print("Please configure at least one API key in .env:")
    print("  - GROQ_API_KEY (recommended)")
    print("  - OPENAI_API_KEY (fallback)")
    print("  - Or install: pip install SpeechRecognition")
    exit(1)

# Test with audio file
test_audio = "../test_audio/test_question.mp3"

if not os.path.exists(test_audio):
    print(f"\n⚠️  Test audio file not found: {test_audio}")
    print("Creating test audio...")
    from gtts import gTTS
    os.makedirs("../test_audio", exist_ok=True)
    text = "What is artificial intelligence and how does it work?"
    tts = gTTS(text=text, lang='en', slow=False)
    tts.save(test_audio)
    print(f"✅ Created: {test_audio}")

print(f"\n🎤 Transcribing: {test_audio}")
print("-" * 60)

try:
    result = stt.transcribe(test_audio)
    
    print(f"\n✅ Transcription successful!")
    print(f"\n📝 Transcribed Text:")
    print(f"   {result['text']}")
    print(f"\n📊 Details:")
    print(f"   Service used: {result['service_used']}")
    print(f"   Language: {result['language']}")
    print(f"   Duration: {result['duration']:.2f}s")
    
except Exception as e:
    print(f"\n❌ Transcription failed: {str(e)}")

print("\n" + "=" * 60)
print("✅ Test complete!")
print("=" * 60)
