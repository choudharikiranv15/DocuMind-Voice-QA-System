import { useState } from 'react'
import { toast } from 'react-hot-toast'
import { useChatStore } from '../../stores/chatStore'
import { useVoiceStore } from '../../stores/voiceStore'
import { askQuestion, voiceQuery } from '../../services/api'
import VoiceRecorder from '../voice/VoiceRecorder'

export default function ChatInput() {
    const [input, setInput] = useState('')
    const [loading, setLoading] = useState(false)
    const addMessage = useChatStore(state => state.addMessage)
    const isRecording = useVoiceStore(state => state.isRecording)

    const handleSubmit = async (e) => {
        e.preventDefault()
        if (!input.trim() || loading) return

        const userMessage = input.trim()
        setInput('')
        setLoading(true)

        // Add user message
        addMessage({
            role: 'user',
            text: userMessage,
            timestamp: new Date().toISOString()
        })

        try {
            const response = await askQuestion(userMessage)

            // Add AI response
            addMessage({
                role: 'assistant',
                text: response.answer,
                metadata: response.metadata,
                timestamp: new Date().toISOString()
            })
        } catch (error) {
            toast.error(error.message || 'Failed to get response')
        } finally {
            setLoading(false)
        }
    }

    const handleVoiceMessage = async (audioBlob) => {
        setLoading(true)
        const loadingToast = toast.loading('Processing voice message...')

        try {
            const response = await voiceQuery(audioBlob)

            // Add user message (transcribed)
            addMessage({
                role: 'user',
                text: response.question,
                timestamp: new Date().toISOString()
            })

            // Add AI response with audio
            addMessage({
                role: 'assistant',
                text: response.answer,
                audioUrl: response.audio_url,
                metadata: response.metadata,
                timestamp: new Date().toISOString()
            })

            toast.success('Voice message processed!', { id: loadingToast })
        } catch (error) {
            toast.error(error.message || 'Failed to process voice', { id: loadingToast })
        } finally {
            setLoading(false)
        }
    }

    return (
        <div className="p-6">
            <form onSubmit={handleSubmit} className="max-w-4xl mx-auto">
                <div className="flex items-end gap-3">
                    {/* Voice Recorder - Prominent position */}
                    <VoiceRecorder onRecordingComplete={handleVoiceMessage} disabled={loading} />

                    {/* Text Input */}
                    <div className="flex-1 relative">
                        <input
                            type="text"
                            value={input}
                            onChange={(e) => setInput(e.target.value)}
                            placeholder="Type a message..."
                            disabled={loading || isRecording}
                            className="w-full px-6 py-4 bg-[#0f172a] border border-gray-800 rounded-2xl focus:outline-none focus:ring-2 focus:ring-indigo-500 text-white placeholder-gray-500 transition-all duration-200"
                        />
                    </div>

                    {/* Send Button */}
                    <button
                        type="submit"
                        disabled={!input.trim() || loading || isRecording}
                        className="px-6 py-4 bg-indigo-600 hover:bg-indigo-700 text-white rounded-2xl disabled:opacity-50 disabled:cursor-not-allowed transition-all duration-200 hover:scale-105 shadow-lg shadow-indigo-500/30"
                    >
                        {loading ? (
                            <svg className="animate-spin h-5 w-5" fill="none" viewBox="0 0 24 24">
                                <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                                <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
                            </svg>
                        ) : (
                            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8" />
                            </svg>
                        )}
                    </button>
                </div>
            </form>
        </div>
    )
}
