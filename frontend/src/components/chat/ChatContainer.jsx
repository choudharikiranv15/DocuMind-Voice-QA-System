import { useRef, useEffect } from 'react'
import { useChatStore } from '../../stores/chatStore'
import MessageList from './MessageList'
import ChatInput from './ChatInput'

export default function ChatContainer() {
    const messages = useChatStore(state => state.messages)
    const messagesEndRef = useRef(null)

    const scrollToBottom = () => {
        messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
    }

    useEffect(() => {
        scrollToBottom()
    }, [messages])

    return (
        <div className="flex-1 flex flex-col overflow-hidden bg-[#0f172a]">
            {/* Messages Area */}
            <div className="flex-1 overflow-y-auto px-4 py-6">
                {messages.length === 0 ? (
                    <div className="h-full flex items-center justify-center">
                        <div className="text-center max-w-2xl">
                            <div className="mb-8">
                                <div className="inline-flex items-center justify-center w-24 h-24 rounded-full bg-gradient-to-br from-indigo-500 via-purple-500 to-pink-500 mb-6 shadow-2xl shadow-indigo-500/30">
                                    <svg className="w-12 h-12 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 11a7 7 0 01-7 7m0 0a7 7 0 01-7-7m7 7v4m0 0H8m4 0h4m-4-8a3 3 0 01-3-3V5a3 3 0 116 0v6a3 3 0 01-3 3z" />
                                    </svg>
                                </div>
                            </div>
                            <h2 className="text-4xl font-bold text-white mb-4">
                                Talk to Your Documents
                            </h2>
                            <p className="text-gray-400 text-lg mb-8">
                                Use voice commands to ask questions and get answers directly from your documents
                            </p>
                            <div className="flex items-center justify-center gap-4">
                                <button className="px-6 py-3 bg-indigo-600 hover:bg-indigo-700 text-white rounded-lg font-medium transition-all duration-200 hover:scale-105 shadow-lg shadow-indigo-500/30">
                                    Try Demo
                                </button>
                                <button className="px-6 py-3 bg-gray-800 hover:bg-gray-700 text-white rounded-lg font-medium transition-all duration-200">
                                    Upload File
                                </button>
                            </div>
                        </div>
                    </div>
                ) : (
                    <>
                        <MessageList />
                        <div ref={messagesEndRef} />
                    </>
                )}
            </div>

            {/* Input Area */}
            <div className="border-t border-gray-800 bg-[#1e293b]">
                <ChatInput />
            </div>
        </div>
    )
}
