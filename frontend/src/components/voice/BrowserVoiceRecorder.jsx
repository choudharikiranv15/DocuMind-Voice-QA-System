import { useState, useEffect, useRef } from 'react'
import { toast } from 'react-hot-toast'

export default function BrowserVoiceRecorder({ onTranscript, disabled }) {
    const [isListening, setIsListening] = useState(false)
    const [transcript, setTranscript] = useState('')
    const [isSupported, setIsSupported] = useState(true)
    const recognitionRef = useRef(null)

    useEffect(() => {
        // Check if browser supports Web Speech API
        if (!('webkitSpeechRecognition' in window) && !('SpeechRecognition' in window)) {
            setIsSupported(false)
            console.error('Browser does not support Speech Recognition')
            return
        }

        // Initialize Speech Recognition
        const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition
        const recognition = new SpeechRecognition()

        recognition.continuous = false
        recognition.interimResults = true
        recognition.lang = 'en-US'

        recognition.onstart = () => {
            setIsListening(true)
            if (import.meta.env.DEV) console.log('Speech recognition started')
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

            // If we have a final result, send it
            if (finalTranscript) {
                onTranscript(finalTranscript.trim())
            }
        }

        recognition.onerror = (event) => {
            console.error('Speech recognition error:', event.error)
            setIsListening(false)

            switch (event.error) {
                case 'no-speech':
                    toast.error('No speech detected. Please try again.')
                    break
                case 'audio-capture':
                    toast.error('No microphone found. Please check your device.')
                    break
                case 'not-allowed':
                    toast.error('Microphone permission denied. Please allow access.')
                    break
                case 'network':
                    toast.error('Network error. Please check your internet connection.')
                    break
                default:
                    toast.error(`Speech recognition error: ${event.error}`)
            }
        }

        recognition.onend = () => {
            setIsListening(false)
            if (import.meta.env.DEV) console.log('Speech recognition ended')
        }

        recognitionRef.current = recognition

        return () => {
            if (recognitionRef.current) {
                recognitionRef.current.stop()
            }
        }
    }, [onTranscript])

    const startListening = () => {
        if (!isSupported) {
            toast.error('Speech recognition not supported in this browser. Use Chrome or Edge.')
            return
        }

        if (recognitionRef.current && !isListening) {
            setTranscript('')
            try {
                recognitionRef.current.start()
                toast.success('Listening... Speak now!')
            } catch (error) {
                console.error('Error starting recognition:', error)
                toast.error('Failed to start listening')
            }
        }
    }

    const stopListening = () => {
        if (recognitionRef.current && isListening) {
            recognitionRef.current.stop()
        }
    }

    if (!isSupported) {
        return (
            <div className="text-center p-4 bg-yellow-500/10 border border-yellow-500/20 rounded-lg">
                <p className="text-sm text-yellow-400">
                    Voice recognition not supported in this browser.
                    <br />
                    Please use Chrome, Edge, or Safari.
                </p>
            </div>
        )
    }

    return (
        <div className="flex items-center gap-3">
            <button
                onClick={isListening ? stopListening : startListening}
                disabled={disabled}
                className={`
                    relative p-3 rounded-full transition-all duration-200
                    ${isListening
                        ? 'bg-red-500 hover:bg-red-600 animate-pulse'
                        : 'bg-indigo-600 hover:bg-indigo-700'
                    }
                    ${disabled ? 'opacity-50 cursor-not-allowed' : ''}
                    text-white shadow-lg
                `}
                title={isListening ? 'Stop listening' : 'Start voice input'}
            >
                {isListening ? (
                    <svg className="w-6 h-6" fill="currentColor" viewBox="0 0 24 24">
                        <rect x="6" y="6" width="12" height="12" rx="2" />
                    </svg>
                ) : (
                    <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 11a7 7 0 01-7 7m0 0a7 7 0 01-7-7m7 7v4m0 0H8m4 0h4m-4-8a3 3 0 01-3-3V5a3 3 0 116 0v6a3 3 0 01-3 3z" />
                    </svg>
                )}
            </button>

            {isListening && (
                <div className="flex-1">
                    <div className="bg-gray-800 rounded-lg p-3 border border-gray-700">
                        <p className="text-sm text-gray-300">
                            {transcript || 'Listening...'}
                        </p>
                    </div>
                </div>
            )}
        </div>
    )
}
