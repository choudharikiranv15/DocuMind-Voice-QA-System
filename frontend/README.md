# DocuMind Voice - Frontend

Modern React frontend for DocuMind Voice with voice recording and playback capabilities.

## 🚀 Quick Start

```bash
# Install dependencies
npm install

# Start development server
npm run dev

# Build for production
npm run build
```

## 🎯 Features

- ✅ Document upload (drag & drop)
- ✅ Chat interface (ChatGPT-style)
- ✅ Voice recording
- ✅ Audio playback
- ✅ Real-time transcription
- ✅ Responsive design
- ✅ Modern UI with Tailwind CSS

## 📁 Project Structure

```
src/
├── components/
│   ├── layout/          # Layout components
│   ├── documents/       # Document management
│   ├── chat/           # Chat interface
│   └── voice/          # Voice features
├── stores/             # Zustand state management
├── services/           # API services
├── App.jsx            # Main app component
└── main.jsx           # Entry point
```

## 🔧 Configuration

Backend API URL is configured in `src/services/api.js`:
```javascript
const API_BASE_URL = 'http://localhost:8080'
```

## 🎨 Tech Stack

- **React 18** - UI library
- **Vite** - Build tool
- **Tailwind CSS** - Styling
- **Zustand** - State management
- **Axios** - HTTP client
- **React Hot Toast** - Notifications

## 📝 Available Scripts

- `npm run dev` - Start development server (port 5173)
- `npm run build` - Build for production
- `npm run preview` - Preview production build

## 🌐 Development

Frontend runs on: http://localhost:5173  
Backend API: http://localhost:8080

Make sure the backend is running before starting the frontend!

## 🎤 Voice Features

### Recording
- Click microphone button to start/stop recording
- Browser will request microphone permission
- Recording indicator shows when active

### Playback
- Audio responses play automatically
- Custom audio player with progress bar
- Play/pause and seek controls

## 📱 Responsive Design

- Mobile: Collapsible sidebar
- Tablet: Optimized layout
- Desktop: Full sidebar + chat

## 🐛 Troubleshooting

### "Cannot access microphone"
- Grant microphone permissions in browser
- Use HTTPS or localhost
- Check browser compatibility (Chrome/Edge recommended)

### "Network Error"
- Ensure backend is running on port 8080
- Check CORS is enabled in backend
- Verify API_BASE_URL in api.js

### Build errors
```bash
# Clear node_modules and reinstall
rm -rf node_modules package-lock.json
npm install
```

## 🎯 Next Steps

- [ ] Add dark mode
- [ ] Add keyboard shortcuts
- [ ] Add message markdown rendering
- [ ] Add waveform visualization
- [ ] Add user authentication
- [ ] Add settings panel

## 📄 License

Part of DocuMind Voice project
