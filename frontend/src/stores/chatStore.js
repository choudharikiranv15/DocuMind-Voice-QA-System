import { create } from 'zustand'

export const useChatStore = create((set) => ({
    messages: [],

    addMessage: (message) => set((state) => ({
        messages: [...state.messages, { ...message, id: Date.now() }]
    })),

    clearMessages: () => set({ messages: [] }),

    updateMessage: (id, updates) => set((state) => ({
        messages: state.messages.map(msg =>
            msg.id === id ? { ...msg, ...updates } : msg
        )
    }))
}))
