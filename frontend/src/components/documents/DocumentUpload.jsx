import { useState, useRef } from 'react'
import { toast } from 'react-hot-toast'
import { uploadDocument } from '../../services/api'
import { useDocumentStore } from '../../stores/documentStore'

export default function DocumentUpload() {
    const [uploading, setUploading] = useState(false)
    const [dragActive, setDragActive] = useState(false)
    const fileInputRef = useRef(null)
    const addDocument = useDocumentStore(state => state.addDocument)

    const handleDrag = (e) => {
        e.preventDefault()
        e.stopPropagation()
        if (e.type === "dragenter" || e.type === "dragover") {
            setDragActive(true)
        } else if (e.type === "dragleave") {
            setDragActive(false)
        }
    }

    const handleDrop = (e) => {
        e.preventDefault()
        e.stopPropagation()
        setDragActive(false)

        if (e.dataTransfer.files && e.dataTransfer.files[0]) {
            handleFile(e.dataTransfer.files[0])
        }
    }

    const handleChange = (e) => {
        e.preventDefault()
        if (e.target.files && e.target.files[0]) {
            handleFile(e.target.files[0])
        }
    }

    const handleFile = async (file) => {
        if (!file.name.endsWith('.pdf')) {
            toast.error('Please upload a PDF file')
            return
        }

        setUploading(true)
        const loadingToast = toast.loading('Uploading and processing document...')

        try {
            const result = await uploadDocument(file)
            addDocument(result)

            // Refresh the document list from backend
            const fetchDocuments = useDocumentStore.getState().fetchDocuments
            await fetchDocuments()

            toast.success('Document uploaded and indexed!', { id: loadingToast })
        } catch (error) {
            toast.error(error.message || 'Failed to upload document', { id: loadingToast })
        } finally {
            setUploading(false)
        }
    }

    return (
        <div>
            <input
                ref={fileInputRef}
                type="file"
                accept=".pdf"
                onChange={handleChange}
                className="hidden"
            />

            <div
                onDragEnter={handleDrag}
                onDragLeave={handleDrag}
                onDragOver={handleDrag}
                onDrop={handleDrop}
                onClick={() => fileInputRef.current?.click()}
                className={`
          border-2 border-dashed rounded-xl p-6 text-center cursor-pointer
          transition-all duration-200
          ${dragActive
                        ? 'border-indigo-500 bg-indigo-500/10'
                        : 'border-gray-700 hover:border-indigo-500 bg-[#0f172a]'
                    }
          ${uploading ? 'opacity-50 cursor-not-allowed' : ''}
        `}
            >
                <div className="flex flex-col items-center">
                    <div className="w-12 h-12 rounded-full bg-indigo-500/20 flex items-center justify-center mb-3">
                        <svg
                            className="w-6 h-6 text-indigo-400"
                            fill="none"
                            stroke="currentColor"
                            viewBox="0 0 24 24"
                        >
                            <path
                                strokeLinecap="round"
                                strokeLinejoin="round"
                                strokeWidth={2}
                                d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12"
                            />
                        </svg>
                    </div>
                    <p className="text-sm text-gray-300 font-medium">
                        {uploading ? 'Uploading...' : 'Upload Document'}
                    </p>
                    <p className="text-xs text-gray-500 mt-1">
                        Click or drag PDF file here
                    </p>
                </div>
            </div>
        </div>
    )
}
