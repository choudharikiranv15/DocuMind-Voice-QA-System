import { create } from 'zustand'

export const useDocumentStore = create((set) => ({
    documents: [],
    currentDocument: null,

    addDocument: (document) => set((state) => ({
        documents: [...state.documents, { ...document, id: Date.now() }],
        currentDocument: { ...document, id: Date.now() }
    })),

    setCurrentDocument: (document) => set({ currentDocument: document }),

    removeDocument: (id) => set((state) => ({
        documents: state.documents.filter(doc => doc.id !== id),
        currentDocument: state.currentDocument?.id === id ? null : state.currentDocument
    })),

    clearDocuments: () => set({ documents: [], currentDocument: null })
}))
