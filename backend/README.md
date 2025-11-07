# DocuMind Voice - Backend

## 🎤 Enhanced Speech-to-Text with Fallback Options

### STT Service Priority:
1. **Groq Whisper API** (Primary) - Best quality, fast
2. **OpenAI Whisper API** (Fallback 1) - High quality
3. **Google Speech Recognition** (Fallback 2) - Free, requires internet

### Features:
- ✅ Automatic fallback if primary service fails
- ✅ Better transcription accuracy with `whisper-large-v3-turbo`
- ✅ Temperature=0.0 for deterministic output
- ✅ Multiple API support
- ✅ Free fallback option (Google SR)

## 🚀 Quick Start

### 1. Install Dependencies
```bash
cd backend
pip install -r requirements.txt
```

### 2. Configure API Keys
Create `.env` file:
```env
# Primary STT (required)
GROQ_API_KEY=your_groq_key_here

# Fallback STT (optional but recommended)
OPENAI_API_KEY=your_openai_key_here

# LLM
LLM_MODEL=llama-3.1-8b-instant
```

### 3. Run Server
```bash
python app.py
```

Server runs on: http://localhost:8080

## 📡 API Endpoints

### Voice Endpoints
- `POST /transcribe` - Speech to text
- `POST /speak` - Text to speech
- `POST /voice-query` - Complete voice pipeline

### Document Endpoints
- `POST /upload` - Upload PDF
- `POST /ask` - Text query
- `GET /stats` - System statistics

### Audio
- `GET /audio/<filename>` - Serve audio files

## 🔧 STT Configuration

### Using Groq (Recommended)
```python
from src.stt_handler import STTHandler

stt = STTHandler(groq_api_key="your_key")
result = stt.transcribe("audio.mp3")
```

### With Fallback
```python
stt = STTHandler(
    groq_api_key="groq_key",
    openai_api_key="openai_key"  # Fallback
)
```

### Check Available Services
```python
services = stt.get_available_services()
# Returns: ['groq_whisper', 'openai_whisper', 'google_sr']
```

## 📊 Transcription Quality

| Service | Quality | Speed | Cost |
|---------|---------|-------|------|
| Groq Whisper | ⭐⭐⭐⭐⭐ | Very Fast | Free tier |
| OpenAI Whisper | ⭐⭐⭐⭐⭐ | Fast | $0.006/min |
| Google SR | ⭐⭐⭐ | Medium | Free |

## 🐛 Troubleshooting

### "No STT service available"
- Add at least one API key to `.env`
- Or install SpeechRecognition for free fallback

### "Groq transcription failed"
- Check API key is valid
- System automatically tries fallback services

### Poor transcription quality
- Ensure clear audio with minimal background noise
- Use higher quality audio files (WAV preferred)
- Groq Whisper gives best results

## 📝 Project Structure

```
backend/
├── app.py                 # Flask application
├── src/
│   ├── stt_handler.py    # Enhanced STT with fallbacks
│   ├── tts_handler.py    # Text-to-speech
│   ├── rag_system.py     # RAG orchestration
│   ├── pdf_processor.py  # PDF processing
│   ├── llm_handler.py    # LLM integration
│   └── retriever.py      # Vector search
├── config/
│   └── config.py         # Configuration
├── templates/            # HTML templates
├── data/
│   ├── pdfs/            # Uploaded PDFs
│   ├── audio/           # Generated audio
│   └── chroma_db/       # Vector database
└── requirements.txt      # Dependencies
```

## 🎯 Next Steps

1. Test improved STT accuracy
2. Add frontend React app
3. Implement user authentication
4. Deploy to production

## 📈 Performance

- **STT Latency**: 1-3 seconds (Groq)
- **TTS Latency**: 1-2 seconds
- **Total Pipeline**: 4-7 seconds
- **Fallback Time**: +2-3 seconds if needed

## 🔐 Security

- API keys stored in `.env` (not committed)
- CORS enabled for frontend
- JWT authentication ready
- Rate limiting recommended for production
