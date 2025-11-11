import { useState, useEffect, useRef } from 'react'
import { toast } from 'react-hot-toast'
import { useChatStore } from '../../stores/chatStore'
import { useDocumentStore } from '../../stores/documentStore'
import { askQuestion } from '../../services/api'

export default function ChatInput() {
    const [input, setInput] = useState('')
    const [loading, setLoading] = useState(false)
    const [isListening, setIsListening] = useState(false)
    const [transcript, setTranscript] = useState('')
    const recognitionRef = useRef(null)
    const addMessage = useChatStore(state => state.addMessage)
    const currentDocument = useDocumentStore(state => state.currentDocument)

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
            // Pass the current document name to filter results
            const response = await askQuestion(userMessage, currentDocument?.name)

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

    // Initialize speech recognition
    useEffect(() => {
        if (!('webkitSpeechRecognition' in window) && !('SpeechRecognition' in window)) {
            return
        }

        const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition
        const recognition = new SpeechRecognition()

        recognition.continuous = false
        recognition.interimResults = true
        recognition.lang = 'en-US'

        recognition.onstart = () => {
            setIsListening(true)
            setTranscript('')
        }

        recognition.onresult = (event) => {
            let interimTranscript = ''
            let finalTranscript = ''

            for (let i = event.resultIndex; i < event.results.length; i++) {
                const transcript = event.results[i][0].transcript
                if (event.results[i].isFinal) {
                    finalTranscript += transcript + ' '
                } else {
                    interimTranscript += transcript
                }
            }

            setTranscript(finalTranscript || interimTranscript)

            // If we have a final result, submit it
            if (finalTranscript) {
                setInput(finalTranscript.trim())
                setTimeout(() => {
                    const form = document.querySelector('form')
                    if (form) {
                        form.dispatchEvent(new Event('submit', { cancelable: true, bubbles: true }))
                    }
                }, 100)
            }
        }

        recognition.onerror = (event) => {
            setIsListening(false)
            if (event.error !== 'no-speech' && event.error !== 'aborted') {
                toast.error(`Voice recognition error: ${event.error}`)
            }
        }

        recognition.onend = () => {
            setIsListening(false)
        }

        recognitionRef.current = recognition

        return () => {
            if (recognitionRef.current) {
                recognitionRef.current.stop()
            }
        }
    }, [])

    const toggleVoiceRecording = () => {
        if (!recognitionRef.current) {
            toast.error('Speech recognition not supported in this browser')
            return
        }

        if (isListening) {
            recognitionRef.current.stop()
        } else {
            try {
                recognitionRef.current.start()
                toast.success('Listening... Speak now!')
            } catch (error) {
                console.error('Error starting recognition:', error)
                toast.error('Failed to start listening')
            }
        }
    }

    return (
        <div className="p-6">
            <form onSubmit={handleSubmit} className="max-w-4xl mx-auto">
                <div className="space-y-3">
                    {/* Show transcript when listening */}
                    {isListening && transcript && (
                        <div className="bg-indigo-500/10 border border-indigo-500/20 rounded-lg p-3">
                            <p className="text-sm text-indigo-300">{transcript}</p>
                        </div>
                    )}

                    <div className="flex items-end gap-3">
                        {/* Text Input */}
                        <div className="flex-1 relative">
                            <input
                                type="text"
                                value={input}
                                onChange={(e) => setInput(e.target.value)}
                                placeholder={isListening ? "Listening..." : "Type a message or use voice..."}
                                disabled={loading || isListening}
                                className="w-full px-6 py-4 bg-[#0f172a] border border-gray-800 rounded-2xl focus:outline-none focus:ring-2 focus:ring-indigo-500 text-white placeholder-gray-500 transition-all duration-200"
                            />
                        </div>

                        {/* Voice Button */}
                        <button
                            type="button"
                            onClick={toggleVoiceRecording}
                            disabled={loading}
                            className={`px-6 py-4 rounded-2xl disabled:opacity-50 disabled:cursor-not-allowed transition-all duration-200 hover:scale-105 text-white ${
                                isListening
                                    ? 'bg-red-500 hover:bg-red-600 animate-pulse'
                                    : 'bg-gray-800 hover:bg-gray-700'
                            }`}
                            title={isListening ? "Stop listening" : "Start voice input"}
                        >
                            {isListening ? (
                                <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 24 24">
                                    <rect x="6" y="6" width="12" height="12" rx="2" />
                                </svg>
                            ) : (
                                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 11a7 7 0 01-7 7m0 0a7 7 0 01-7-7m7 7v4m0 0H8m4 0h4m-4-8a3 3 0 01-3-3V5a3 3 0 116 0v6a3 3 0 01-3 3z" />
                                </svg>
                            )}
                        </button>

                        {/* Send Button */}
                        <button
                            type="submit"
                            disabled={!input.trim() || loading || isListening}
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
                </div>
            </form>
        </div>
    )
}
