import axios from 'axios'

const API_BASE_URL = 'http://localhost:8080'

const api = axios.create({
    baseURL: API_BASE_URL,
    headers: {
        'Content-Type': 'application/json',
    },
})

// Request interceptor to add auth token from localStorage
api.interceptors.request.use(
    (config) => {
        // Get token from localStorage
        const authStorage = localStorage.getItem('auth-storage')
        if (authStorage) {
            try {
                const authData = JSON.parse(authStorage)
                if (authData.state && authData.state.token) {
                    config.headers.Authorization = `Bearer ${authData.state.token}`
                }
            } catch (error) {
                console.error('Failed to parse auth data:', error)
            }
        }
        return config
    },
    (error) => {
        return Promise.reject(error)
    }
)

// Document APIs
export const uploadDocument = async (file) => {
    const formData = new FormData()
    formData.append('file', file)

    const response = await api.post('/upload', formData, {
        headers: {
            'Content-Type': 'multipart/form-data',
        },
    })

    if (!response.data.success) {
        throw new Error(response.data.message || 'Upload failed')
    }

    return {
        name: response.data.message.replace('Successfully added ', ''),
        statistics: response.data.statistics,
    }
}

// Chat APIs
export const askQuestion = async (question, documentName = null) => {
    const response = await api.post('/ask', {
        question,
        document_name: documentName
    })

    if (!response.data.success) {
        throw new Error(response.data.message || 'Query failed')
    }

    return response.data
}

// Document Management APIs
export const listDocuments = async () => {
    const response = await api.get('/documents')

    if (!response.data.success) {
        throw new Error(response.data.message || 'Failed to list documents')
    }

    return response.data.documents
}

export const deleteDocument = async (documentName) => {
    const response = await api.delete(`/documents/${encodeURIComponent(documentName)}`)

    if (!response.data.success) {
        throw new Error(response.data.message || 'Failed to delete document')
    }

    return response.data
}

export const clearAllDocuments = async () => {
    const response = await api.post('/documents/clear-all')

    if (!response.data.success) {
        throw new Error(response.data.message || 'Failed to clear documents')
    }

    return response.data
}

// Voice APIs
export const transcribeAudio = async (audioBlob) => {
    const formData = new FormData()
    formData.append('audio', audioBlob, 'recording.wav')

    const response = await api.post('/transcribe', formData, {
        headers: {
            'Content-Type': 'multipart/form-data',
        },
    })

    if (!response.data.success) {
        throw new Error(response.data.message || 'Transcription failed')
    }

    return response.data
}

export const textToSpeech = async (text) => {
    const response = await api.post('/speak', { text })

    if (!response.data.success) {
        throw new Error(response.data.message || 'TTS failed')
    }

    return response.data
}

export const voiceQuery = async (audioBlob) => {
    const formData = new FormData()
    formData.append('audio', audioBlob, 'query.wav')

    const response = await api.post('/voice-query', formData, {
        headers: {
            'Content-Type': 'multipart/form-data',
        },
    })

    if (!response.data.success) {
        throw new Error(response.data.message || 'Voice query failed')
    }

    return response.data
}

// System APIs
export const getStats = async () => {
    const response = await api.get('/stats')

    if (!response.data.success) {
        throw new Error(response.data.message || 'Failed to get stats')
    }

    return response.data.stats
}

export default api
