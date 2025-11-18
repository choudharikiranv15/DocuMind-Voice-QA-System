import axios from 'axios'

// Use environment variable for API URL, fallback to localhost for development
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8080'

const api = axios.create({
    baseURL: API_BASE_URL,
    headers: {
        'Content-Type': 'application/json',
    },
    withCredentials: false, // Set to true if using cookies for auth
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
export const askQuestion = async (question, documentName = null, language = 'auto') => {
    const response = await api.post('/ask', {
        question,
        document_name: documentName,
        language: language  // Support multilingual TTS
    })

    if (!response.data.success) {
        throw new Error(response.data.message || 'Query failed')
    }

    return response.data
}

// TTS APIs
export const getSupportedLanguages = async () => {
    const response = await api.get('/tts/languages')

    if (!response.data.success) {
        throw new Error(response.data.message || 'Failed to get languages')
    }

    return response.data.languages
}

export const textToSpeech = async (text, language = 'auto') => {
    const response = await api.post('/speak', {
        text,
        language
    })

    if (!response.data.success) {
        throw new Error(response.data.message || 'TTS failed')
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

// Voice Preference APIs
export const getAvailableEngines = async () => {
    const response = await api.get('/tts/engines')

    if (!response.data.success) {
        throw new Error(response.data.message || 'Failed to get available engines')
    }

    return response.data
}

export const getVoicePreferences = async () => {
    const response = await api.get('/voice/preferences')

    if (!response.data.success) {
        throw new Error(response.data.message || 'Failed to get voice preferences')
    }

    return response.data.preferences
}

export const updateVoicePreferences = async (preferences) => {
    const response = await api.put('/voice/preferences', preferences)

    if (!response.data.success) {
        throw new Error(response.data.message || 'Failed to update voice preferences')
    }

    return response.data
}

// Account Management APIs
export const changePassword = async (currentPassword, newPassword) => {
    const response = await api.post('/auth/change-password', {
        current_password: currentPassword,
        new_password: newPassword
    })

    if (!response.data.success) {
        throw new Error(response.data.message || 'Failed to change password')
    }

    return response.data
}

export const changeEmail = async (newEmail, password) => {
    const response = await api.post('/auth/change-email', {
        new_email: newEmail,
        password: password
    })

    if (!response.data.success) {
        throw new Error(response.data.message || 'Failed to change email')
    }

    return response.data
}

export const deleteAccount = async (password, confirmation) => {
    const response = await api.delete('/auth/delete-account', {
        data: {
            password: password,
            confirmation: confirmation
        }
    })

    if (!response.data.success) {
        throw new Error(response.data.message || 'Failed to delete account')
    }

    return response.data
}

export default api
