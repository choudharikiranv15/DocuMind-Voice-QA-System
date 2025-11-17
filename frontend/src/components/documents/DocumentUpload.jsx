import { useState, useRef } from 'react'
import { motion } from 'framer-motion'
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

            <motion.div
                whileHover={{ scale: uploading ? 1 : 1.02 }}
                whileTap={{ scale: uploading ? 1 : 0.98 }}
                onDragEnter={handleDrag}
                onDragLeave={handleDrag}
                onDragOver={handleDrag}
                onDrop={handleDrop}
                onClick={() => !uploading && fileInputRef.current?.click()}
                className={`
          border-2 border-dashed rounded-xl p-4 text-center cursor-pointer
          transition-all duration-200 backdrop-blur-sm
          ${dragActive
                        ? 'border-cyan-500 bg-gradient-to-r from-cyan-500/10 to-purple-500/10 shadow-lg shadow-cyan-500/20'
                        : 'border-white/10 hover:border-cyan-500/50 bg-white/5'
                    }
          ${uploading ? 'opacity-50 cursor-not-allowed' : ''}
        `}
            >
                <div className="flex items-center gap-3">
                    <div className="w-10 h-10 rounded-lg bg-gradient-to-br from-cyan-500/20 to-purple-500/20 flex items-center justify-center flex-shrink-0">
                        {uploading ? (
                            <svg className="w-5 h-5 text-cyan-400 animate-spin" fill="none" viewBox="0 0 24 24">
                                <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                                <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
                            </svg>
                        ) : (
                            <svg
                                className="w-5 h-5 text-cyan-400"
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
                        )}
                    </div>
                    <div className="flex-1 text-left">
                        <p className="text-sm text-gray-300 font-medium">
                            {uploading ? 'Uploading...' : 'Upload PDF'}
                        </p>
                        <p className="text-xs text-gray-500">
                            {uploading ? 'Processing document' : 'Click or drop here'}
                        </p>
                    </div>
                </div>
            </motion.div>
        </div>
    )
}
