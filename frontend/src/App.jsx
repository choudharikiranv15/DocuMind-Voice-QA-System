import { useState } from 'react'
import { Toaster } from 'react-hot-toast'
import Layout from './components/layout/Layout'
import ChatContainer from './components/chat/ChatContainer'
import Sidebar from './components/layout/Sidebar'

function App() {
    const [sidebarOpen, setSidebarOpen] = useState(true)

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
                                <button className="text-gray-400 hover:text-white transition-colors text-sm">
                                    Home
                                </button>
                                <button className="text-gray-400 hover:text-white transition-colors text-sm">
                                    Files
                                </button>
                            </div>
                        </header>

                        {/* Chat Area */}
                        <ChatContainer />
                    </div>
                </div>
            </Layout>
        </>
    )
}

export default App
