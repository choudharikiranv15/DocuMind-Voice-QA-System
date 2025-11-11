import { useDocumentStore } from '../../stores/documentStore'
import { toast } from 'react-hot-toast'

export default function DocumentCard({ document }) {
    const currentDocument = useDocumentStore(state => state.currentDocument)
    const setCurrentDocument = useDocumentStore(state => state.setCurrentDocument)
    const removeDocument = useDocumentStore(state => state.removeDocument)

    // Defensive check - ensure document is valid
    if (!document || typeof document !== 'object') {
        console.error('Invalid document:', document)
        return null
    }

    // Extract values safely
    const docName = String(document.name || 'Unknown')
    const totalChunks = Number(document.total_chunks || 0)
    const textChunks = Number(document.text_chunks || 0)
    const tableChunks = Number(document.table_chunks || 0)
    const imageChunks = Number(document.image_chunks || 0)

    const isActive = currentDocument?.name === docName

    // Truncate long document names
    const truncatedName = docName.length > 40 ? docName.substring(0, 37) + '...' : docName

    const handleDelete = async (e) => {
        e.stopPropagation()
        if (confirm(`Delete "${docName}"?`)) {
            try {
                await removeDocument(docName)
                toast.success('Document deleted')
            } catch (error) {
                toast.error('Failed to delete document')
            }
        }
    }

    return (
        <div
            onClick={() => setCurrentDocument(document)}
            className={`
        p-4 rounded-xl cursor-pointer transition-all duration-200 group
        ${isActive
                    ? 'bg-indigo-600 text-white shadow-lg shadow-indigo-500/30'
                    : 'bg-[#0f172a] hover:bg-gray-800 text-gray-300 border border-gray-800'
                }
      `}
        >
            <div className="flex items-start gap-3">
                <div className={`
          w-10 h-10 rounded-lg flex items-center justify-center flex-shrink-0
          ${isActive ? 'bg-white/20' : 'bg-indigo-500/20'}
        `}>
                    <svg
                        className={`w-5 h-5 ${isActive ? 'text-white' : 'text-indigo-400'}`}
                        fill="none"
                        stroke="currentColor"
                        viewBox="0 0 24 24"
                    >
                        <path
                            strokeLinecap="round"
                            strokeLinejoin="round"
                            strokeWidth={2}
                            d="M7 21h10a2 2 0 002-2V9.414a1 1 0 00-.293-.707l-5.414-5.414A1 1 0 0012.586 3H7a2 2 0 00-2 2v14a2 2 0 002 2z"
                        />
                    </svg>
                </div>
                <div className="flex-1 min-w-0">
                    <p
                        className={`text-sm font-medium ${isActive ? 'text-white' : 'text-gray-200'}`}
                        title={docName}
                    >
                        {truncatedName}
                    </p>
                    <div className="flex items-center gap-2 mt-1">
                        <span className={`text-xs ${isActive ? 'text-white/70' : 'text-gray-500'}`}>
                            {totalChunks} chunks
                        </span>
                        {textChunks > 0 && (
                            <span className={`text-xs ${isActive ? 'text-white/70' : 'text-gray-500'}`}>
                                • {textChunks} text
                            </span>
                        )}
                        {tableChunks > 0 && (
                            <span className={`text-xs ${isActive ? 'text-white/70' : 'text-gray-500'}`}>
                                • {tableChunks} tables
                            </span>
                        )}
                        {imageChunks > 0 && (
                            <span className={`text-xs ${isActive ? 'text-white/70' : 'text-gray-500'}`}>
                                • {imageChunks} images
                            </span>
                        )}
                        <span className={`px-2 py-0.5 rounded text-xs ${isActive ? 'bg-white/20 text-white' : 'bg-green-500/20 text-green-400'}`}>
                            {isActive ? 'Active' : 'Ready'}
                        </span>
                    </div>
                </div>
                <button
                    onClick={handleDelete}
                    className={`
            opacity-0 group-hover:opacity-100 transition-opacity
            p-1.5 rounded-lg hover:bg-red-500/20
            ${isActive ? 'text-white hover:text-red-300' : 'text-gray-400 hover:text-red-400'}
          `}
                >
                    <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                    </svg>
                </button>
            </div>
        </div>
    )
}
