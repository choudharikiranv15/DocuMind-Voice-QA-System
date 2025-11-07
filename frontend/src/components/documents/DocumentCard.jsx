import { useDocumentStore } from '../../stores/documentStore'

export default function DocumentCard({ document }) {
    const currentDocument = useDocumentStore(state => state.currentDocument)
    const setCurrentDocument = useDocumentStore(state => state.setCurrentDocument)

    const isActive = currentDocument?.id === document.id

    return (
        <div
            onClick={() => setCurrentDocument(document)}
            className={`
        p-4 rounded-xl cursor-pointer transition-all duration-200
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
                    <p className={`text-sm font-medium truncate ${isActive ? 'text-white' : 'text-gray-200'}`}>
                        {document.name}
                    </p>
                    {document.statistics && (
                        <div className="flex items-center gap-2 mt-1">
                            <span className={`text-xs ${isActive ? 'text-white/70' : 'text-gray-500'}`}>
                                {document.statistics.total_chunks} chunks
                            </span>
                            <span className={`px-2 py-0.5 rounded text-xs ${isActive ? 'bg-white/20 text-white' : 'bg-green-500/20 text-green-400'}`}>
                                Ready
                            </span>
                        </div>
                    )}
                </div>
            </div>
        </div>
    )
}
