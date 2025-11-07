# 🎤 DocuMind Voice - Multimodal RAG System

> An AI-powered voice-enabled document assistant that reads, understands, and speaks about your documents.

[![Python](https://img.shields.io/badge/Python-3.11-blue.svg)](https://www.python.org/)
[![Flask](https://img.shields.io/badge/Flask-3.0-green.svg)](https://flask.palletsprojects.com/)
[![React](https://img.shields.io/badge/React-18-blue.svg)](https://reactjs.org/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

## 🌟 Features

- 🎤 **Voice Input** - Ask questions using your voice (Groq Whisper API)
- 🔊 **Voice Output** - Get spoken answers (gTTS)
- 📄 **PDF Processing** - Extract text, tables, and images
- 🧠 **RAG System** - Intelligent document retrieval and answering
- 💬 **Chat Interface** - Natural conversation with your documents
- 🔄 **Fallback Options** - Multiple STT services for reliability
- 🌐 **Multi-language** - Support for multiple languages

## 🏗️ Project Structure

```
DocuMind_Voice/
├── backend/              # Flask API server
│   ├── app.py           # Main application
│   ├── src/             # Core modules
│   │   ├── stt_handler.py    # Speech-to-Text (enhanced)
│   │   ├── tts_handler.py    # Text-to-Speech
│   │   ├── rag_system.py     # RAG orchestration
│   │   ├── pdf_processor.py  # PDF processing
│   │   └── llm_handler.py    # LLM integration
│   ├── config/          # Configuration
│   ├── templates/       # HTML templates
│   ├── data/           # Data storage
│   └── requirements.txt
│
├── frontend/            # React application (coming soon)
│   └── (React app)
│
├── docs/               # Documentation
│   ├── QUICKSTART.md
│   ├── README_VOICE.md
│   └── PROJECT_RESTRUCTURE.md
│
├── rag_env/            # Virtual environment
└── docker-compose.yml  # Docker setup
```

## 🚀 Quick Start

### Prerequisites
- Python 3.11+
- Node.js 18+ (for frontend)
- Groq API key ([Get one here](https://console.groq.com/))

### Backend Setup

1. **Clone the repository**
```bash
git clone https://github.com/choudharikiranv15/DocuMind-Voice-QA-System.git
cd DocuMind_Voice
```

2. **Create virtual environment**
```bash
python -m venv rag_env
.\rag_env\Scripts\activate  # Windows
# source rag_env/bin/activate  # Linux/Mac
```

3. **Install dependencies**
```bash
cd backend
pip install -r requirements.txt
```

4. **Configure environment**
```bash
# Copy .env.example to .env
copy .env.example .env

# Edit .env and add your API keys
GROQ_API_KEY=your_groq_key_here
```

5. **Run the server**
```bash
python app.py
```

Server runs on: **http://localhost:8080**

### Frontend Setup (Coming Soon)
```bash
cd frontend
npm install
npm run dev
```

## 📡 API Endpoints

### Voice Endpoints
- `POST /transcribe` - Convert speech to text
- `POST /speak` - Convert text to speech
- `POST /voice-query` - Complete voice-to-voice pipeline

### Document Endpoints
- `POST /upload` - Upload PDF document
- `POST /ask` - Ask question about documents
- `GET /stats` - Get system statistics

### Audio
- `GET /audio/<filename>` - Serve generated audio files

## 🎯 Usage Examples

### Voice Query (Complete Pipeline)
```bash
curl -X POST http://localhost:8080/voice-query \
  -F "audio=@question.mp3"
```

### Text Query
```bash
curl -X POST http://localhost:8080/ask \
  -H "Content-Type: application/json" \
  -d '{"question": "What is this document about?"}'
```

### Speech-to-Text
```bash
curl -X POST http://localhost:8080/transcribe \
  -F "audio=@recording.wav"
```

### Text-to-Speech
```bash
curl -X POST http://localhost:8080/speak \
  -H "Content-Type: application/json" \
  -d '{"text": "Hello from DocuMind Voice"}'
```

## 🔧 Configuration

### Environment Variables

```env
# Primary STT (required)
GROQ_API_KEY=your_groq_key_here

# Fallback STT (optional)
OPENAI_API_KEY=your_openai_key_here

# LLM Configuration
LLM_MODEL=llama-3.1-8b-instant
EMBEDDING_MODEL=all-MiniLM-L6-v2
```

### STT Fallback Chain

1. **Groq Whisper API** (Primary) - Best quality, fast
2. **OpenAI Whisper API** (Fallback 1) - High quality
3. **Google Speech Recognition** (Fallback 2) - Free

## 📊 Tech Stack

### Backend
- **Framework**: Flask 3.0
- **STT**: Groq Whisper API / OpenAI Whisper / Google SR
- **TTS**: gTTS (Google Text-to-Speech)
- **LLM**: Groq Llama-3.1-8B
- **Embeddings**: all-MiniLM-L6-v2
- **Vector DB**: ChromaDB / Simple Vector Store
- **PDF Processing**: PyMuPDF, pdfplumber

### Frontend (Coming Soon)
- **Framework**: React 18
- **Build Tool**: Vite
- **Styling**: TailwindCSS
- **State**: Zustand
- **Audio**: Web Audio API

## 🎨 Features in Detail

### Enhanced Speech-to-Text
- Multiple fallback options for reliability
- Better accuracy with `whisper-large-v3-turbo`
- Automatic service selection
- Language detection
- Verbose response format

### Intelligent RAG System
- Context-aware retrieval
- Multi-document support
- Table and image extraction
- Conversation history
- Source tracking

### Voice Pipeline
```
User Voice → STT → RAG Query → LLM Response → TTS → Audio Output
```

## 📈 Performance

| Metric | Value |
|--------|-------|
| STT Latency | 1-3 seconds |
| TTS Latency | 1-2 seconds |
| RAG Processing | 1-2 seconds |
| **Total Pipeline** | **4-7 seconds** |

## 🐛 Troubleshooting

### "No STT service available"
- Add `GROQ_API_KEY` to `backend/.env`
- Or install free fallback: `pip install SpeechRecognition`

### "Module not found" errors
- Ensure virtual environment is activated
- Run `pip install -r requirements.txt` in backend folder

### Poor transcription quality
- Use clear audio with minimal background noise
- Ensure Groq API key is configured (best quality)
- Check audio file format (WAV preferred)

## 📚 Documentation

- [Quick Start Guide](docs/QUICKSTART.md)
- [Voice Features](docs/README_VOICE.md)
- [Project Structure](docs/PROJECT_RESTRUCTURE.md)
- [Test Results](docs/VOICE_TEST_RESULTS.md)

## 🛣️ Roadmap

### Phase 1: Core Voice RAG ✅
- [x] Voice input (STT)
- [x] Voice output (TTS)
- [x] Complete voice pipeline
- [x] Enhanced STT with fallbacks
- [x] Project restructuring

### Phase 2: Frontend (In Progress)
- [ ] React application setup
- [ ] Voice recording UI
- [ ] Waveform visualization
- [ ] Chat interface
- [ ] File upload with progress

### Phase 3: Multi-user Support
- [ ] User authentication (JWT)
- [ ] Per-user document storage
- [ ] Session management
- [ ] Rate limiting

### Phase 4: Advanced Features
- [ ] Table understanding
- [ ] Diagram comprehension
- [ ] Multi-language support
- [ ] Real-time streaming

### Phase 5: Deployment
- [ ] Docker containerization
- [ ] Production deployment
- [ ] Monitoring & logging
- [ ] CI/CD pipeline

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 👤 Author

**Kiran V Choudhari**
- GitHub: [@choudharikiranv15](https://github.com/choudharikiranv15)

## 🙏 Acknowledgments

- [Groq](https://groq.com/) - Fast LLM inference
- [OpenAI](https://openai.com/) - Whisper model
- [Hugging Face](https://huggingface.co/) - Transformers and models
- [Flask](https://flask.palletsprojects.com/) - Web framework

## 📞 Support

For issues and questions:
- Open an [Issue](https://github.com/choudharikiranv15/DocuMind-Voice-QA-System/issues)
- Check [Documentation](docs/)

---

**Status**: ✅ Backend Complete | ⏳ Frontend In Progress  
**Version**: 1.0.0  
**Last Updated**: November 7, 2025
