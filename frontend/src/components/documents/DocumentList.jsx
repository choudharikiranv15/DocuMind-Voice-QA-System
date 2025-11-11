import { useEffect } from 'react'
import { useDocumentStore } from '../../stores/documentStore'
import { toast } from 'react-hot-toast'
import DocumentCard from './DocumentCard'

export default function DocumentList() {
    const documents = useDocumentStore(state => state.documents)
    const fetchDocuments = useDocumentStore(state => state.fetchDocuments)
    const clearDocuments = useDocumentStore(state => state.clearDocuments)
    const loading = useDocumentStore(state => state.loading)
    const currentDocument = useDocumentStore(state => state.currentDocument)

    useEffect(() => {
        fetchDocuments()
    }, [fetchDocuments])

    const handleClearAll = async () => {
        if (confirm('Clear all documents from the vector store?')) {
            try {
                await clearDocuments()
                toast.success('All documents cleared')
            } catch (error) {
                toast.error('Failed to clear documents')
            }
        }
    }

    if (loading && documents.length === 0) {
        return (
            <div className="text-center py-8">
                <div className="animate-spin h-8 w-8 border-4 border-indigo-500 border-t-transparent rounded-full mx-auto"></div>
                <p className="mt-2 text-sm text-gray-500">Loading documents...</p>
            </div>
        )
    }

    if (documents.length === 0) {
        return (
            <div className="text-center py-8">
                <svg
                    className="mx-auto h-12 w-12 text-gray-400"
                    fill="none"
                    stroke="currentColor"
                    viewBox="0 0 24 24"
                >
                    <path
                        strokeLinecap="round"
                        strokeLinejoin="round"
                        strokeWidth={2}
                        d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"
                    />
                </svg>
                <p className="mt-2 text-sm text-gray-500">No documents uploaded</p>
                <p className="text-xs text-gray-400">Upload a PDF to get started</p>
            </div>
        )
    }

    return (
        <div className="space-y-3">
            <div className="flex items-center justify-between">
                <h3 className="text-sm font-medium text-gray-400">
                    Documents ({documents.length})
                </h3>
                {documents.length > 0 && (
                    <button
                        onClick={handleClearAll}
                        className="text-xs text-red-400 hover:text-red-300 transition-colors"
                    >
                        Clear All
                    </button>
                )}
            </div>

            {currentDocument && (
                <div className="text-xs bg-indigo-500/10 border border-indigo-500/20 rounded-lg p-2">
                    <p className="text-indigo-400 font-medium mb-1">Active Document:</p>
                    <p className="text-gray-300 break-words" title={currentDocument.name}>
                        {currentDocument.name.length > 50
                            ? currentDocument.name.substring(0, 47) + '...'
                            : currentDocument.name
                        }
                    </p>
                </div>
            )}

            <div className="space-y-2">
                {documents.map((doc, index) => (
                    <DocumentCard key={doc.name || index} document={doc} />
                ))}
            </div>
        </div>
    )
}
