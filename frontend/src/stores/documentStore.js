import { create } from 'zustand'
import { listDocuments, deleteDocument, clearAllDocuments } from '../services/api'

export const useDocumentStore = create((set, get) => ({
    documents: [],
    currentDocument: null,
    loading: false,
    error: null,

    // Fetch documents from backend
    fetchDocuments: async () => {
        set({ loading: true, error: null })
        try {
            const docs = await listDocuments()
            // Backend returns array of document objects with {name, total_chunks, text_chunks, etc.}
            const formattedDocs = docs.map((doc, index) => ({
                id: index,
                name: doc.name,
                total_chunks: doc.total_chunks,
                text_chunks: doc.text_chunks,
                table_chunks: doc.table_chunks,
                image_chunks: doc.image_chunks
            }))
            set({ documents: formattedDocs, loading: false })
        } catch (error) {
            set({ error: error.message, loading: false })
        }
    },

    addDocument: (document) => set((state) => {
        const newDoc = { ...document, id: Date.now() }
        return {
            documents: [...state.documents, newDoc],
            currentDocument: newDoc
        }
    }),

    setCurrentDocument: (document) => set({ currentDocument: document }),

    removeDocument: async (documentName) => {
        set({ loading: true, error: null })
        try {
            await deleteDocument(documentName)
            set((state) => ({
                documents: state.documents.filter(doc => doc.name !== documentName),
                currentDocument: state.currentDocument?.name === documentName ? null : state.currentDocument,
                loading: false
            }))
        } catch (error) {
            set({ error: error.message, loading: false })
        }
    },

    clearDocuments: async () => {
        set({ loading: true, error: null })
        try {
            await clearAllDocuments()
            set({ documents: [], currentDocument: null, loading: false })
        } catch (error) {
            set({ error: error.message, loading: false })
        }
    }
}))
