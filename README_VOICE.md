# DocuMind Voice - Quick Start Guide

## 🚀 What's New

Voice capabilities added to your RAG system:
- **Speech-to-Text (STT)**: Faster-Whisper
- **Text-to-Speech (TTS)**: gTTS (fallback) / Piper TTS (optional)
- **Voice Query Pipeline**: Complete voice-to-voice interaction

## 📦 Installation

### Step 1: Install Voice Dependencies

```bash
# Windows
install_voice.bat

# Or manually
pip install faster-whisper gtts pydub soundfile flask-cors
```

### Step 2: Start the Server

```bash
python app_flask.py
```

### Step 3: Test Voice Features

Open in browser:
- Main app: http://localhost:8080
- Voice test: http://localhost:8080/voice-test

## 🎯 API Endpoints

### 1. Speech to Text
```bash
POST /transcribe
Content-Type: multipart/form-data

Body:
- audio: audio file (wav, mp3, m4a, etc.)
- language: optional (en, es, fr, etc.)

Response:
{
  "success": true,
  "text": "transcribed text",
  "language": "en",
  "duration": 5.2
}
```

### 2. Text to Speech
```bash
POST /speak
Content-Type: application/json

Body:
{
  "text": "Hello, this is a test"
}

Response:
{
  "success": true,
  "audio_url": "/audio/tts_abc123.wav",
  "duration": 2.5,
  "filename": "tts_abc123.wav"
}
```

### 3. Voice Query (Complete Pipeline)
```bash
POST /voice-query
Content-Type: multipart/form-data

Body:
- audio: audio file with question

Response:
{
  "success": true,
  "question": "What is this document about?",
  "answer": "This document discusses...",
  "audio_url": "/audio/tts_xyz789.wav",
  "transcription_language": "en",
  "metadata": {
    "sources_used": 3,
    "confidence": 0.85,
    "query_type": "general"
  }
}
```

## 🔧 Configuration

### Using Piper TTS (Better Quality, Offline)

1. Download Piper:
   - Windows: https://github.com/rhasspy/piper/releases
   - Extract and add to PATH

2. Download a voice model:
   ```bash
   # Example: US English voice
   wget https://huggingface.co/rhasspy/piper-voices/resolve/main/en/en_US/lessac/medium/en_US-lessac-medium.onnx
   ```

3. System will automatically use Piper if available

### Using gTTS (Current Fallback)

- Requires internet connection
- Free and unlimited
- Good quality
- Automatically used if Piper not available

## 🎤 Testing Voice Features

### Test 1: Record and Transcribe
1. Go to http://localhost:8080/voice-test
2. Click "Start Recording"
3. Speak clearly
4. Click "Stop Recording"
5. See transcription

### Test 2: Text to Speech
1. Enter text in the textarea
2. Click "Generate Speech"
3. Listen to the audio

### Test 3: Voice Query
1. Upload a PDF first (main interface)
2. Go to voice test page
3. Click "Ask Question (Voice)"
4. Ask a question about your document
5. Get spoken answer

## 🏗️ Architecture

```
User speaks → Faster-Whisper (STT) → Text Query
                                          ↓
                                     RAG System
                                          ↓
                                    Text Answer
                                          ↓
                                   gTTS/Piper (TTS) → Audio Response
```

## 📊 Performance

### Faster-Whisper Models

| Model | Size | Speed | Accuracy |
|-------|------|-------|----------|
| tiny | 39 MB | Very Fast | Good |
| base | 74 MB | Fast | Better |
| small | 244 MB | Medium | Great |
| medium | 769 MB | Slow | Excellent |

Current: **base** (good balance)

### TTS Performance

- **gTTS**: ~1-2 seconds per sentence (internet required)
- **Piper**: ~0.5 seconds per sentence (offline)

## 🚀 Next Steps

### For MVP (Days 1-3) ✅
- [x] Add STT endpoint
- [x] Add TTS endpoint
- [x] Add voice query pipeline
- [x] Create test interface

### Days 4-6: React Frontend
- [ ] Build React app with voice UI
- [ ] Add audio recording component
- [ ] Add waveform visualization
- [ ] Spotify-style audio player

### Days 7-8: Multi-user Support
- [ ] Add user authentication
- [ ] Per-user document storage
- [ ] Session management with Redis

### Days 9-10: Deployment
- [ ] Docker containerization
- [ ] Deploy to VPS
- [ ] Add monitoring

## 🐛 Troubleshooting

### "No module named 'faster_whisper'"
```bash
pip install faster-whisper
```

### "Could not find Piper TTS"
- System will use gTTS fallback automatically
- Install Piper for better performance (optional)

### "Microphone not accessible"
- Use HTTPS or localhost
- Grant microphone permissions in browser

### "Audio file too large"
- Max file size: 50MB
- Compress audio or use shorter recordings

## 💡 Tips

1. **For best STT results**: Speak clearly, minimize background noise
2. **For faster processing**: Use smaller Whisper model (tiny/base)
3. **For better TTS quality**: Install Piper TTS
4. **For production**: Use Piper TTS (offline, faster, better quality)

## 📝 Model Downloads

First time running will download models:
- Faster-Whisper base: ~74 MB
- Sentence transformer: ~90 MB

Total: ~164 MB (one-time download)

## 🎯 Current Status

✅ Voice input working (Faster-Whisper)
✅ Voice output working (gTTS fallback)
✅ Complete voice pipeline working
✅ Test interface ready
⏳ React frontend (next)
⏳ Multi-user support (next)
⏳ Deployment (next)

---

**Ready to test?** Run `python app_flask.py` and visit http://localhost:8080/voice-test
