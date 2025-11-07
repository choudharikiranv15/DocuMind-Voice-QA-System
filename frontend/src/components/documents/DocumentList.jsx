import { useDocumentStore } from '../../stores/documentStore'
import DocumentCard from './DocumentCard'

export default function DocumentList() {
    const documents = useDocumentStore(state => state.documents)

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
        <div className="space-y-2">
            <h3 className="text-sm font-medium text-gray-700 mb-3">
                Uploaded Documents ({documents.length})
            </h3>
            {documents.map((doc) => (
                <DocumentCard key={doc.id} document={doc} />
            ))}
        </div>
    )
}
