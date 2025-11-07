import { useState, useRef } from 'react'
import { toast } from 'react-hot-toast'
import { useVoiceStore } from '../../stores/voiceStore'

export default function VoiceRecorder({ onRecordingComplete, disabled }) {
    const [mediaRecorder, setMediaRecorder] = useState(null)
    const audioChunksRef = useRef([])
    const { isRecording, setIsRecording } = useVoiceStore()

    const startRecording = async () => {
        try {
            const stream = await navigator.mediaDevices.getUserMedia({ audio: true })
            const recorder = new MediaRecorder(stream)

            audioChunksRef.current = []

            recorder.ondataavailable = (event) => {
                audioChunksRef.current.push(event.data)
            }

            recorder.onstop = () => {
                const audioBlob = new Blob(audioChunksRef.current, { type: 'audio/wav' })
                onRecordingComplete(audioBlob)
                stream.getTracks().forEach(track => track.stop())
            }

            recorder.start()
            setMediaRecorder(recorder)
            setIsRecording(true)
            toast.success('Recording started')
        } catch (error) {
            toast.error('Could not access microphone')
            console.error('Error accessing microphone:', error)
        }
    }

    const stopRecording = () => {
        if (mediaRecorder && mediaRecorder.state !== 'inactive') {
            mediaRecorder.stop()
            setMediaRecorder(null)
            setIsRecording(false)
            toast.success('Recording stopped')
        }
    }

    const toggleRecording = () => {
        if (isRecording) {
            stopRecording()
        } else {
            startRecording()
        }
    }

    return (
        <button
            type="button"
            onClick={toggleRecording}
            disabled={disabled}
            className={`
        relative w-14 h-14 rounded-full transition-all duration-300 flex items-center justify-center
        ${isRecording
                    ? 'bg-gradient-to-br from-pink-500 via-purple-500 to-indigo-500 animate-pulse shadow-lg shadow-purple-500/50'
                    : 'bg-gradient-to-br from-indigo-500 via-purple-500 to-pink-500 hover:shadow-lg hover:shadow-indigo-500/50 hover:scale-105'
                }
        disabled:opacity-50 disabled:cursor-not-allowed
      `}
            title={isRecording ? 'Stop recording' : 'Start voice recording'}
        >
            <div className="absolute inset-0 rounded-full bg-gradient-to-br from-pink-500 via-purple-500 to-indigo-500 opacity-50 blur-xl"></div>
            <div className="relative">
                {isRecording ? (
                    <svg className="w-6 h-6 text-white" fill="currentColor" viewBox="0 0 24 24">
                        <rect x="6" y="6" width="12" height="12" rx="2" />
                    </svg>
                ) : (
                    <svg className="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 11a7 7 0 01-7 7m0 0a7 7 0 01-7-7m7 7v4m0 0H8m4 0h4m-4-8a3 3 0 01-3-3V5a3 3 0 116 0v6a3 3 0 01-3 3z" />
                    </svg>
                )}
            </div>
        </button>
    )
}
