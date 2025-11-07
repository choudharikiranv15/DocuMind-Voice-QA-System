# 📅 Day 2: React Frontend Development Plan

## 🎯 Goal
Build a modern, voice-enabled React frontend for DocuMind Voice with Spotify-style UI

---

## 📋 Tasks Breakdown (8-10 hours)

### Phase 1: Project Setup (1 hour)

#### 1.1 Initialize React App
```bash
cd frontend
npm create vite@latest . -- --template react
npm install
```

#### 1.2 Install Dependencies
```bash
# UI & Styling
npm install tailwindcss postcss autoprefixer
npm install @headlessui/react @heroicons/react
npm install clsx

# State Management
npm install zustand

# API & Data Fetching
npm install axios
npm install react-query

# Audio & Voice
npm install wavesurfer.js
npm install react-mic
npm install @types/dom-mediacapture-record

# Utilities
npm install react-hot-toast
npm install date-fns
```

#### 1.3 Configure Tailwind
```bash
npx tailwindcss init -p
```

---

### Phase 2: Core Components (2-3 hours)

#### 2.1 Layout Components
- `Layout.jsx` - Main app layout
- `Sidebar.jsx` - Document list sidebar
- `Header.jsx` - Top navigation bar
- `Footer.jsx` - Bottom player/controls

#### 2.2 Document Components
- `DocumentUpload.jsx` - Drag & drop PDF upload
- `DocumentList.jsx` - List of uploaded documents
- `DocumentCard.jsx` - Individual document item

#### 2.3 Chat Components
- `ChatContainer.jsx` - Main chat area
- `MessageList.jsx` - Display messages
- `Message.jsx` - Individual message bubble
- `ChatInput.jsx` - Text input with voice button

---

### Phase 3: Voice Features (2-3 hours)

#### 3.1 Voice Recording
- `VoiceRecorder.jsx` - Record audio button
- `RecordingIndicator.jsx` - Visual feedback while recording
- `AudioWaveform.jsx` - Waveform visualization

#### 3.2 Audio Player
- `AudioPlayer.jsx` - Spotify-style player
- `PlaybackControls.jsx` - Play/pause/seek controls
- `VolumeControl.jsx` - Volume slider
- `ProgressBar.jsx` - Playback progress

#### 3.3 Voice Integration
- `useVoiceRecording.js` - Custom hook for recording
- `useAudioPlayback.js` - Custom hook for playback
- `audioService.js` - API calls for STT/TTS

---

### Phase 4: State Management (1 hour)

#### 4.1 Zustand Stores
```javascript
// stores/documentStore.js
- documents list
- current document
- upload progress

// stores/chatStore.js
- messages
- conversation history
- loading states

// stores/voiceStore.js
- recording state
- audio playback state
- current audio URL

// stores/uiStore.js
- sidebar open/closed
- theme (light/dark)
- notifications
```

---

### Phase 5: API Integration (1-2 hours)

#### 5.1 API Service
```javascript
// services/api.js
- uploadDocument()
- askQuestion()
- transcribeAudio()
- textToSpeech()
- voiceQuery()
- getStats()
```

#### 5.2 React Query Setup
- Query keys
- Mutations
- Cache configuration
- Error handling

---

### Phase 6: UI Polish (1-2 hours)

#### 6.1 Styling
- Dark/Light theme toggle
- Smooth animations
- Loading skeletons
- Error states
- Empty states

#### 6.2 Responsive Design
- Mobile layout
- Tablet layout
- Desktop layout
- Touch-friendly controls

---

## 🎨 Design System

### Color Palette
```css
/* Light Mode */
--primary: #667eea
--secondary: #764ba2
--background: #ffffff
--surface: #f7fafc
--text: #1a202c
--text-secondary: #718096

/* Dark Mode */
--primary: #667eea
--secondary: #764ba2
--background: #1a202c
--surface: #2d3748
--text: #f7fafc
--text-secondary: #cbd5e0
```

### Typography
```css
--font-sans: 'Inter', system-ui, sans-serif
--font-mono: 'Fira Code', monospace
```

---

## 📁 Project Structure

```
frontend/
├── public/
│   └── assets/
├── src/
│   ├── components/
│   │   ├── layout/
│   │   │   ├── Layout.jsx
│   │   │   ├── Sidebar.jsx
│   │   │   ├── Header.jsx
│   │   │   └── Footer.jsx
│   │   ├── documents/
│   │   │   ├── DocumentUpload.jsx
│   │   │   ├── DocumentList.jsx
│   │   │   └── DocumentCard.jsx
│   │   ├── chat/
│   │   │   ├── ChatContainer.jsx
│   │   │   ├── MessageList.jsx
│   │   │   ├── Message.jsx
│   │   │   └── ChatInput.jsx
│   │   ├── voice/
│   │   │   ├── VoiceRecorder.jsx
│   │   │   ├── AudioPlayer.jsx
│   │   │   ├── AudioWaveform.jsx
│   │   │   └── RecordingIndicator.jsx
│   │   └── ui/
│   │       ├── Button.jsx
│   │       ├── Input.jsx
│   │       ├── Modal.jsx
│   │       └── Toast.jsx
│   ├── hooks/
│   │   ├── useVoiceRecording.js
│   │   ├── useAudioPlayback.js
│   │   └── useDocuments.js
│   ├── services/
│   │   ├── api.js
│   │   └── audioService.js
│   ├── stores/
│   │   ├── documentStore.js
│   │   ├── chatStore.js
│   │   ├── voiceStore.js
│   │   └── uiStore.js
│   ├── utils/
│   │   ├── formatters.js
│   │   └── validators.js
│   ├── App.jsx
│   ├── main.jsx
│   └── index.css
├── package.json
├── vite.config.js
├── tailwind.config.js
└── README.md
```

---

## 🎯 Key Features to Implement

### Must Have (Day 2)
- ✅ Document upload with drag & drop
- ✅ Chat interface (ChatGPT-style)
- ✅ Voice recording button
- ✅ Audio playback
- ✅ Text input with send button
- ✅ Loading states
- ✅ Error handling
- ✅ Responsive design

### Nice to Have (If time permits)
- ⏳ Waveform visualization
- ⏳ Dark mode toggle
- ⏳ Keyboard shortcuts
- ⏳ Message markdown rendering
- ⏳ Copy to clipboard
- ⏳ Download audio

### Future (Day 3+)
- ⏳ User authentication
- ⏳ Multiple conversations
- ⏳ Search in documents
- ⏳ Export chat history
- ⏳ Settings panel

---

## 🔧 Development Workflow

### Step-by-Step Implementation

#### Step 1: Setup (30 min)
```bash
cd frontend
npm create vite@latest . -- --template react
npm install
npm install tailwindcss postcss autoprefixer
npx tailwindcss init -p
```

#### Step 2: Basic Layout (1 hour)
1. Create Layout component
2. Add Sidebar
3. Add Header
4. Test responsive behavior

#### Step 3: Document Upload (1 hour)
1. Create upload component
2. Add drag & drop
3. Connect to backend API
4. Show upload progress

#### Step 4: Chat Interface (1.5 hours)
1. Create chat container
2. Add message list
3. Add input field
4. Connect to backend

#### Step 5: Voice Recording (1.5 hours)
1. Add microphone button
2. Implement recording logic
3. Show recording indicator
4. Send to backend

#### Step 6: Audio Playback (1 hour)
1. Create audio player
2. Add play/pause controls
3. Show progress bar
4. Handle audio URLs

#### Step 7: Polish (1-2 hours)
1. Add loading states
2. Add error handling
3. Improve styling
4. Test all features

---

## 🧪 Testing Checklist

### Functionality
- [ ] Upload PDF successfully
- [ ] Send text message
- [ ] Record voice message
- [ ] Play audio response
- [ ] See conversation history
- [ ] Handle errors gracefully

### UI/UX
- [ ] Responsive on mobile
- [ ] Smooth animations
- [ ] Clear loading states
- [ ] Intuitive controls
- [ ] Accessible (keyboard navigation)

### Performance
- [ ] Fast initial load
- [ ] Smooth scrolling
- [ ] No lag during recording
- [ ] Audio plays without delay

---

## 📊 Success Metrics

### Day 2 Goals
- ✅ Working React app
- ✅ Can upload documents
- ✅ Can send text queries
- ✅ Can record voice
- ✅ Can play audio responses
- ✅ Looks professional
- ✅ Mobile responsive

### Time Allocation
- Setup: 1 hour
- Components: 3 hours
- Voice features: 2 hours
- Integration: 1 hour
- Polish: 1-2 hours
- **Total: 8-10 hours**

---

## 🚀 Quick Start Commands

```bash
# Day 2 Morning
cd frontend
npm create vite@latest . -- --template react
npm install
npm install tailwindcss postcss autoprefixer zustand axios react-query
npx tailwindcss init -p

# Start development
npm run dev

# Backend (separate terminal)
cd ../backend
python app.py
```

---

## 💡 Pro Tips

1. **Start Simple**: Get basic functionality working first
2. **Component First**: Build components before connecting to API
3. **Mock Data**: Use mock data initially for faster development
4. **Incremental**: Test each feature as you build it
5. **Git Commits**: Commit after each major feature
6. **Break Time**: Take breaks every 2 hours

---

## 🎨 UI Inspiration

### Reference Apps
- ChatGPT (chat interface)
- Spotify (audio player)
- Notion (document list)
- Discord (sidebar layout)

### Design Principles
- **Clean**: Minimal, uncluttered
- **Modern**: Rounded corners, shadows
- **Intuitive**: Clear actions
- **Responsive**: Works on all devices
- **Fast**: Smooth animations

---

## 📝 Notes

- Backend runs on `http://localhost:8080`
- Frontend will run on `http://localhost:5173` (Vite default)
- Use CORS (already enabled in backend)
- Test voice features in Chrome/Edge (best browser support)

---

## 🎯 End of Day 2 Deliverables

1. ✅ Working React frontend
2. ✅ Connected to backend API
3. ✅ Voice recording functional
4. ✅ Audio playback working
5. ✅ Professional UI
6. ✅ Mobile responsive
7. ✅ Code pushed to GitHub

---

**Ready to start Day 2!** 🚀

Let's build an amazing voice-enabled UI! 💪
