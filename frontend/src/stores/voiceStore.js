import { create } from 'zustand'

export const useVoiceStore = create((set) => ({
    isRecording: false,
    currentAudioUrl: null,
    isPlaying: false,

    setIsRecording: (isRecording) => set({ isRecording }),

    setCurrentAudioUrl: (url) => set({ currentAudioUrl: url }),

    setIsPlaying: (isPlaying) => set({ isPlaying }),

    reset: () => set({
        isRecording: false,
        currentAudioUrl: null,
        isPlaying: false
    })
}))
