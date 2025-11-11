import { useState, useEffect } from 'react'
import { Routes, Route, Navigate } from 'react-router-dom'
import { Toaster } from 'react-hot-toast'
import Layout from './components/layout/Layout'
import ChatContainer from './components/chat/ChatContainer'
import Sidebar from './components/layout/Sidebar'
import BrowserWarning from './components/common/BrowserWarning'
import Login from './pages/Login'
import Signup from './pages/Signup'
import ProtectedRoute from './components/auth/ProtectedRoute'
import useAuthStore from './stores/authStore'

function MainApp() {
    const [sidebarOpen, setSidebarOpen] = useState(true)
    const { user, logout } = useAuthStore()

    return (
        <Layout>
            <div className="flex h-screen overflow-hidden bg-[#0f172a]">
                {/* Sidebar */}
                <Sidebar isOpen={sidebarOpen} onClose={() => setSidebarOpen(false)} />

                {/* Main Content */}
                <div className="flex-1 flex flex-col">
                    {/* Header */}
                    <header className="bg-[#1e293b] border-b border-gray-800 px-6 py-4 flex items-center justify-between">
                        <div className="flex items-center gap-4">
                            <button
                                onClick={() => setSidebarOpen(!sidebarOpen)}
                                className="p-2 hover:bg-gray-800 rounded-lg transition-all duration-200 text-gray-400 hover:text-white"
                            >
                                <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h16M4 18h16" />
                                </svg>
                            </button>
                            <div className="flex items-center gap-3">
                                <h1 className="text-xl font-bold text-white">
                                    DOCUMIND <span className="text-indigo-400">VOICE</span>
                                </h1>
                            </div>
                        </div>
                        <div className="flex items-center gap-4">
                            <span className="text-gray-400 text-sm">{user?.email}</span>
                            <button
                                onClick={logout}
                                className="text-gray-400 hover:text-white transition-colors text-sm"
                            >
                                Logout
                            </button>
                        </div>
                    </header>

                    {/* Browser Compatibility Warning */}
                    <div className="px-6 pt-4">
                        <BrowserWarning />
                    </div>

                    {/* Chat Area */}
                    <ChatContainer />
                </div>
            </div>
        </Layout>
    )
}

function App() {
    const initializeAuth = useAuthStore(state => state.initializeAuth)

    // Initialize auth on app load
    useEffect(() => {
        initializeAuth()
    }, [initializeAuth])

    return (
        <>
            <Toaster
                position="top-right"
                toastOptions={{
                    duration: 3000,
                    style: {
                        background: '#1e293b',
                        color: '#fff',
                        borderRadius: '12px',
                    },
                    success: {
                        iconTheme: {
                            primary: '#6366f1',
                            secondary: '#fff',
                        },
                    },
                }}
            />
            <Routes>
                <Route path="/login" element={<Login />} />
                <Route path="/signup" element={<Signup />} />
                <Route
                    path="/"
                    element={
                        <ProtectedRoute>
                            <MainApp />
                        </ProtectedRoute>
                    }
                />
                <Route path="*" element={<Navigate to="/" replace />} />
            </Routes>
        </>
    )
}

export default App
