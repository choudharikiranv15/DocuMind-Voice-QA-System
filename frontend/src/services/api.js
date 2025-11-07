import axios from 'axios'

const API_BASE_URL = 'http://localhost:8080'

const api = axios.create({
    baseURL: API_BASE_URL,
    headers: {
        'Content-Type': 'application/json',
    },
})

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
export const askQuestion = async (question) => {
    const response = await api.post('/ask', { question })

    if (!response.data.success) {
        throw new Error(response.data.message || 'Query failed')
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
