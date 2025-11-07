# 📁 Project Structure - DocuMind Voice

## ✅ Clean Directory Structure

```
DocuMind_Voice/
│
├── 📁 backend/                    # Backend API Server
│   ├── app.py                     # Flask application entry point
│   ├── requirements.txt           # Python dependencies
│   ├── .env                       # Environment variables (not in git)
│   ├── .env.example              # Environment template
│   ├── .gitignore                # Backend-specific gitignore
│   ├── README.md                 # Backend documentation
│   │
│   ├── 📁 src/                   # Core application modules
│   │   ├── __init__.py
│   │   ├── stt_handler.py        # ✨ Enhanced STT with fallbacks
│   │   ├── tts_handler.py        # Text-to-Speech
│   │   ├── rag_system.py         # RAG orchestration
│   │   ├── pdf_processor.py      # PDF processing
│   │   ├── llm_handler.py        # LLM integration
│   │   ├── retriever.py          # Vector search
│   │   └── simple_vector_store.py # Vector storage
│   │
│   ├── 📁 config/                # Configuration
│   │   └── config.py             # App configuration
│   │
│   ├── 📁 templates/             # HTML templates
│   │   ├── index.html            # Main interface
│   │   └── voice_test.html       # Voice testing page
│   │
│   ├── 📁 data/                  # Data storage
│   │   ├── pdfs/                 # Uploaded PDF files
│   │   ├── audio/                # Generated audio files
│   │   └── chroma_db/            # Vector database
│   │
│   └── 📁 tests/                 # Test scripts
│       ├── test_stt.py
│       ├── test_tts.py
│       ├── test_voice_pipeline.py
│       ├── test_improved_stt.py
│       └── create_test_audio.py
│
├── 📁 frontend/                   # React Application (Coming Soon)
│   ├── package.json
│   ├── vite.config.js
│   ├── 📁 src/
│   │   ├── App.jsx
│   │   ├── main.jsx
│   │   ├── 📁 components/
│   │   ├── 📁 pages/
│   │   └── 📁 utils/
│   └── 📁 public/
│
├── 📁 docs/                       # Documentation
│   ├── QUICKSTART.md             # Quick start guide
│   ├── README_VOICE.md           # Voice features documentation
│   ├── PROJECT_RESTRUCTURE.md    # Restructuring details
│   ├── VOICE_TEST_RESULTS.md     # Test results
│   ├── SETUP_INSTRUCTIONS.md     # Setup guide
│   └── ENHANCED_STT_SUMMARY.md   # STT improvements
│
├── 📁 rag_env/                    # Python virtual environment
│   └── (virtual environment files)
│
├── 📁 models/                     # Model storage (optional)
│   └── (downloaded models)
│
├── 📁 .vscode/                    # VS Code settings
│   └── settings.json
│
├── 📁 .git/                       # Git repository
│
├── .gitignore                     # Root gitignore
├── README.md                      # Main project README
├── STRUCTURE.md                   # This file
├── docker-compose.yml             # Docker setup
├── Dockerfile                     # Docker configuration
└── setup.py                       # Python package setup

```

## 📊 File Count Summary

| Directory | Files | Purpose |
|-----------|-------|---------|
| `backend/` | ~30 | API server, core logic |
| `frontend/` | 0 | React app (to be built) |
| `docs/` | 6 | Documentation |
| `rag_env/` | ~1000 | Python packages |
| Root | 6 | Config & setup |

## 🎯 Key Directories Explained

### Backend (`backend/`)
**Purpose**: Flask API server with all backend logic

**Key Files**:
- `app.py` - Main Flask application
- `src/stt_handler.py` - Enhanced STT with 3 fallback options
- `src/rag_system.py` - RAG orchestration
- `requirements.txt` - All Python dependencies

**Data Storage**:
- `data/pdfs/` - User uploaded PDFs
- `data/audio/` - Generated TTS audio files
- `data/chroma_db/` - Vector database

### Frontend (`frontend/`)
**Purpose**: React application (to be built in Day 2)

**Will Contain**:
- React components
- Voice recording UI
- Chat interface
- Waveform visualization
- File upload interface

### Documentation (`docs/`)
**Purpose**: All project documentation

**Files**:
- Quick start guides
- API documentation
- Feature explanations
- Test results
- Setup instructions

### Virtual Environment (`rag_env/`)
**Purpose**: Isolated Python environment

**Contains**:
- All Python packages
- Dependencies
- Scripts

## 🗑️ Removed Duplicates

### Files Removed from Root:
- ❌ `app_flask.py` → ✅ `backend/app.py`
- ❌ `requirements.txt` → ✅ `backend/requirements.txt`
- ❌ `.env` → ✅ `backend/.env`
- ❌ `.env.example` → ✅ `backend/.env.example`

### Directories Removed from Root:
- ❌ `src/` → ✅ `backend/src/`
- ❌ `config/` → ✅ `backend/config/`
- ❌ `templates/` → ✅ `backend/templates/`
- ❌ `data/` → ✅ `backend/data/`
- ❌ `test_audio/` → ✅ `backend/data/audio/`
- ❌ `__pycache__/` → Deleted

### Test Files Moved:
- ❌ `test_*.py` → ✅ `backend/test_*.py`
- ❌ `create_test_audio.py` → ✅ `backend/create_test_audio.py`

### Documentation Moved:
- ❌ `*.md` (various) → ✅ `docs/*.md`

## ✅ Verification Checklist

- [x] Backend folder contains all backend code
- [x] Frontend folder created (empty, ready for React)
- [x] Documentation organized in docs/
- [x] No duplicate files in root
- [x] Virtual environment intact
- [x] Git repository preserved
- [x] All test files in backend/
- [x] Clean root directory

## 🚀 Running the Project

### Backend
```bash
cd backend
..\rag_env\Scripts\activate
python app.py
```

### Frontend (Coming Soon)
```bash
cd frontend
npm install
npm run dev
```

## 📝 Notes

1. **Root directory is clean** - Only essential config files
2. **Backend is self-contained** - All backend code in one place
3. **Frontend ready** - Empty folder ready for React app
4. **Documentation organized** - All docs in docs/ folder
5. **No duplicates** - Each file exists in only one location

## 🎉 Benefits of This Structure

1. **Clear Separation** - Frontend and backend are independent
2. **Easy Deployment** - Can deploy frontend/backend separately
3. **Better Organization** - Everything has its place
4. **Scalability** - Easy to add new features
5. **Maintainability** - Easy to find and update files
6. **Clean Root** - No clutter in main directory

---

**Status**: ✅ Structure Verified and Clean  
**Last Updated**: November 7, 2025
