# 🚀 Quick Reference Guide

## 📁 Project Structure

```
DocuMind_Voice/
├── backend/          # Flask API server
├── frontend/         # React app (Day 2)
├── docs/            # Documentation
├── test_audio/      # Test files
└── rag_env/         # Python virtual environment
```

## 🏃 Quick Commands

### Backend
```bash
# Start backend server
.\rag_env\Scripts\activate
python backend\app.py

# Test voice features
python backend\test_improved_stt.py
```

### Frontend (Day 2)
```bash
# Setup
cd frontend
npm install
npm run dev

# Build for production
npm run build
```

## 🔑 Environment Variables

### Backend `.env`
```env
GROQ_API_KEY=your_groq_key
OPENAI_API_KEY=your_openai_key  # Optional fallback
LLM_MODEL=llama-3.1-8b-instant
```

## 📡 API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/upload` | POST | Upload PDF |
| `/ask` | POST | Text query |
| `/transcribe` | POST | Audio → Text |
| `/speak` | POST | Text → Audio |
| `/voice-query` | POST | Complete voice pipeline |
| `/stats` | GET | System statistics |
| `/audio/<file>` | GET | Serve audio file |

## 🎤 Voice Features

### STT (Speech-to-Text)
- **Primary**: Groq Whisper API
- **Fallback 1**: OpenAI Whisper
- **Fallback 2**: Google SR (free)

### TTS (Text-to-Speech)
- **Primary**: gTTS (Google TTS)
- **Fallback**: Piper TTS (if installed)

## 🐛 Common Issues

### "No STT service available"
```bash
# Add API key to backend/.env
GROQ_API_KEY=your_key_here
```

### "Module not found"
```bash
# Install dependencies
pip install -r backend/requirements.txt
```

### Port already in use
```bash
# Kill process on port 8080
netstat -ano | findstr :8080
taskkill /PID <pid> /F
```

## 📊 Day 1 Status

✅ Backend restructured  
✅ Enhanced STT with fallbacks  
✅ Voice pipeline working  
✅ All tests passing  
✅ Code on GitHub  

## 🎯 Day 2 Goals

- [ ] Setup React app
- [ ] Build chat interface
- [ ] Add voice recording
- [ ] Connect to backend
- [ ] Polish UI

## 🔗 Useful Links

- Backend: http://localhost:8080
- Frontend: http://localhost:5173 (Day 2)
- GitHub: https://github.com/choudharikiranv15/DocuMind-Voice-QA-System
- Groq Console: https://console.groq.com

## 💡 Tips

1. Always activate virtual environment first
2. Backend must be running for frontend to work
3. Test voice in Chrome/Edge for best results
4. Commit frequently
5. Check logs if something fails

---

**Need help?** Check `docs/` folder for detailed guides!
