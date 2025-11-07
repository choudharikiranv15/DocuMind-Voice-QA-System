import DocumentUpload from '../documents/DocumentUpload'
import DocumentList from '../documents/DocumentList'

export default function Sidebar({ isOpen, onClose }) {
    return (
        <>
            {/* Mobile overlay */}
            {isOpen && (
                <div
                    className="fixed inset-0 bg-black/60 backdrop-blur-sm z-40 lg:hidden transition-opacity duration-300"
                    onClick={onClose}
                />
            )}

            {/* Sidebar */}
            <aside
                className={`
          fixed lg:static inset-y-0 left-0 z-50
          w-80 bg-[#1e293b] border-r border-gray-800
          transform transition-all duration-300 ease-in-out
          ${isOpen ? 'translate-x-0' : '-translate-x-full lg:translate-x-0'}
        `}
            >
                <div className="h-full flex flex-col">
                    {/* Sidebar Header */}
                    <div className="p-5 border-b border-gray-800">
                        <div className="flex items-center justify-between mb-5">
                            <div className="flex items-center gap-2">
                                <div className="w-8 h-8 bg-indigo-500/20 rounded-lg flex items-center justify-center">
                                    <svg className="w-5 h-5 text-indigo-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                                    </svg>
                                </div>
                                <h2 className="text-lg font-semibold text-white">Documents</h2>
                            </div>
                            <button
                                onClick={onClose}
                                className="lg:hidden p-2 hover:bg-gray-800 rounded-lg transition-all duration-200 text-gray-400"
                            >
                                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                                </svg>
                            </button>
                        </div>

                        {/* Upload Component */}
                        <DocumentUpload />
                    </div>

                    {/* Document List */}
                    <div className="flex-1 overflow-y-auto p-4">
                        <DocumentList />
                    </div>

                    {/* Sidebar Footer */}
                    <div className="p-4 border-t border-gray-800">
                        <div className="flex items-center justify-between text-xs">
                            <div className="flex items-center gap-2 text-gray-400">
                                <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse"></div>
                                <span>Online</span>
                            </div>
                            <span className="text-gray-600">v1.0</span>
                        </div>
                    </div>
                </div>
            </aside>
        </>
    )
}
