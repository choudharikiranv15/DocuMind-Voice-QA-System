# DocuMind Voice - Quick Start (10-Day MVP)

## 🎯 What We Built (Day 1)

✅ Voice Input (STT) - Groq Whisper API  
✅ Voice Output (TTS) - gTTS  
✅ Complete voice pipeline integrated with existing RAG  
✅ Test interface ready  

## 🚀 Setup (5 minutes)

### 1. Install Dependencies
```bash
# Activate virtual environment
.\rag_env\Scripts\activate

# Install voice packages (already done if you followed along)
pip install gtts pydub flask-cors
```

### 2. Configure API Key
Make sure your `.env` file has:
```
GROQ_API_KEY=your_groq_api_key_here
```

### 3. Run the Server
```bash
python app_flask.py
```

### 4. Test Voice Features
Open in browser:
- **Main App**: http://localhost:8080
- **Voice Test**: http://localhost:8080/voice-test

## 📡 API Endpoints

### 1. Speech to Text
```bash
POST /transcribe
Content-Type: multipart/form-data

# Upload audio file
curl -X POST http://localhost:8080/transcribe \
  -F "audio=@recording.wav"
```

### 2. Text to Speech
```bash
POST /speak
Content-Type: application/json

curl -X POST http://localhost:8080/speak \
  -H "Content-Type: application/json" \
  -d '{"text": "Hello from DocuMind Voice"}'
```

### 3. Voice Query (Full Pipeline)
```bash
POST /voice-query
Content-Type: multipart/form-data

# Ask question via voice, get voice response
curl -X POST http://localhost:8080/voice-query \
  -F "audio=@question.wav"
```

## 🎤 How to Use

### Text Mode (Existing)
1. Upload PDF
2. Type question
3. Get text answer

### Voice Mode (NEW!)
1. Upload PDF
2. Click microphone button
3. Speak your question
4. Get spoken answer

## 📊 Current Architecture

```
User Voice Input
      ↓
Groq Whisper API (STT)
      ↓
Text Question
      ↓
RAG System (Your existing code)
      ↓
Text Answer
      ↓
gTTS (TTS)
      ↓
Audio Response
```

## 🔧 Tech Stack

**Voice Processing:**
- STT: Groq Whisper API (free tier, 30 req/min)
- TTS: gTTS (Google TTS, free, unlimited)

**Why This Stack:**
- ✅ No complex dependencies (no FFmpeg, no CUDA)
- ✅ Works on Windows without issues
- ✅ Free tier sufficient for MVP
- ✅ Fast setup (5 minutes vs 2 hours)
- ✅ Production-ready APIs

## 📈 Next Steps (Days 2-10)

### Days 2-3: React Frontend
- Build modern UI with voice controls
- Add waveform visualization
- Implement real-time recording

### Days 4-5: Multi-user Support
- Add user authentication (JWT)
- Per-user document storage
- Session management

### Days 6-7: Database Setup
- PostgreSQL for metadata
- Redis for caching
- Qdrant for vectors

### Days 8-9: Deployment
- Docker containerization
- Deploy to VPS
- SSL setup

### Day 10: Polish & Testing
- Load testing
- Bug fixes
- Documentation

## 🎯 MVP Features Checklist

**Core (Done ✅)**
- [x] PDF upload & processing
- [x] Text-based Q&A
- [x] Voice input (STT)
- [x] Voice output (TTS)
- [x] Voice-to-voice pipeline

**Next Priority**
- [ ] React frontend with voice UI
- [ ] User authentication
- [ ] Multi-user document isolation
- [ ] Deployment ready

## 💡 Tips

1. **For best voice quality**: Speak clearly, minimize background noise
2. **API limits**: Groq free tier = 30 requests/min (plenty for MVP)
3. **Audio format**: WAV works best, but MP3/M4A also supported
4. **Response time**: ~2-5 seconds for complete voice pipeline

## 🐛 Troubleshooting

### "No Groq API key found"
- Check `.env` file has `GROQ_API_KEY=...`
- Restart server after adding key

### "Microphone not accessible"
- Use HTTPS or localhost
- Grant browser microphone permissions

### "gTTS error"
- Requires internet connection
- Check firewall settings

## 📝 Git Workflow

```bash
# Commit today's work
git add .
git commit -m "Day 1: Add voice capabilities (STT/TTS)"
git push origin main
```

## 🎉 Success Metrics

**Day 1 Complete:**
- Voice input working ✅
- Voice output working ✅
- Test interface ready ✅
- Zero complex dependencies ✅
- Fast setup time ✅

**Ready for Day 2!**

---

**Questions?** Check `README_VOICE.md` for detailed documentation.
