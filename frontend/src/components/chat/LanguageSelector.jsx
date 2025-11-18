import { useState, useEffect } from 'react'
import { motion } from 'framer-motion'
import { getSupportedLanguages } from '../../services/api'

export default function LanguageSelector({ selectedLanguage, onLanguageChange }) {
    const [languages, setLanguages] = useState({})
    const [loading, setLoading] = useState(true)
    const [isOpen, setIsOpen] = useState(false)

    // Only 3 languages supported as per requirements
    const priorityLanguages = ['auto', 'en', 'kn', 'hi']

    useEffect(() => {
        fetchLanguages()
    }, [])

    const fetchLanguages = async () => {
        try {
            const langs = await getSupportedLanguages()
            setLanguages(langs)
        } catch (error) {
            console.error('Failed to load languages:', error)
            // Fallback to 3 supported languages
            setLanguages({
                'en': 'English',
                'kn': 'Kannada',
                'hi': 'Hindi'
            })
        } finally {
            setLoading(false)
        }
    }

    const getLanguageName = (code) => {
        if (code === 'auto') return '🌐 Auto-detect'
        return languages[code] || code
    }

    const getLanguageFlag = (code) => {
        const flags = {
            'auto': '🌐',
            'en': '🇬🇧',
            'hi': '🇮🇳',
            'kn': '🇮🇳',
            'ta': '🇮🇳',
            'te': '🇮🇳',
            'mr': '🇮🇳',
            'bn': '🇮🇳',
        }
        return flags[code] || '🌍'
    }

    // Sort languages: priority first, then alphabetically
    const sortedLanguages = () => {
        const allCodes = ['auto', ...Object.keys(languages)]
        const priority = allCodes.filter(code => priorityLanguages.includes(code))
        const others = allCodes.filter(code => !priorityLanguages.includes(code)).sort()
        return [...priority, ...others]
    }

    if (loading) {
        return (
            <div className="flex items-center gap-2 text-gray-400">
                <div className="w-5 h-5 border-2 border-blue-500/30 border-t-blue-500 rounded-full animate-spin"></div>
                <span className="text-sm">Loading languages...</span>
            </div>
        )
    }

    return (
        <div className="relative">
            {/* Selected Language Display */}
            <motion.button
                whileHover={{ scale: 1.02 }}
                whileTap={{ scale: 0.98 }}
                onClick={() => setIsOpen(!isOpen)}
                className="flex items-center gap-2 px-3 py-2 bg-gray-800/50 hover:bg-gray-700/50
                          border border-gray-700/50 rounded-lg transition-all duration-200
                          text-sm font-medium text-gray-300 hover:text-white"
            >
                <span className="text-lg">{getLanguageFlag(selectedLanguage)}</span>
                <span className="hidden sm:inline">{getLanguageName(selectedLanguage)}</span>
                <svg
                    className={`w-4 h-4 transition-transform ${isOpen ? 'rotate-180' : ''}`}
                    fill="none"
                    stroke="currentColor"
                    viewBox="0 0 24 24"
                >
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
                </svg>
            </motion.button>

            {/* Dropdown Menu */}
            {isOpen && (
                <>
                    {/* Backdrop */}
                    <div
                        className="fixed inset-0 z-10"
                        onClick={() => setIsOpen(false)}
                    />

                    {/* Dropdown */}
                    <motion.div
                        initial={{ opacity: 0, y: -10 }}
                        animate={{ opacity: 1, y: 0 }}
                        exit={{ opacity: 0, y: -10 }}
                        className="absolute bottom-full mb-2 left-0 w-64 max-h-96 overflow-y-auto
                                  bg-gray-800 border border-gray-700 rounded-lg shadow-2xl z-20
                                  scrollbar-thin scrollbar-thumb-gray-700 scrollbar-track-gray-800"
                    >
                        {/* Header */}
                        <div className="sticky top-0 bg-gray-800 border-b border-gray-700 p-3">
                            <h3 className="text-sm font-semibold text-gray-200">
                                Select Voice Language
                            </h3>
                            <p className="text-xs text-gray-400 mt-1">
                                Auto-detect or choose manually
                            </p>
                        </div>

                        {/* Language List */}
                        <div className="p-2">
                            {sortedLanguages().map((code) => (
                                <motion.button
                                    key={code}
                                    whileHover={{ backgroundColor: 'rgba(59, 130, 246, 0.1)' }}
                                    onClick={() => {
                                        onLanguageChange(code)
                                        setIsOpen(false)
                                    }}
                                    className={`w-full flex items-center gap-3 px-3 py-2.5 rounded-lg
                                              text-left transition-colors duration-150
                                              ${selectedLanguage === code
                                            ? 'bg-blue-500/20 text-blue-400 border border-blue-500/30'
                                            : 'text-gray-300 hover:text-white'
                                        }`}
                                >
                                    <span className="text-xl">{getLanguageFlag(code)}</span>
                                    <div className="flex-1">
                                        <div className="text-sm font-medium">
                                            {getLanguageName(code)}
                                        </div>
                                        {code === 'auto' && (
                                            <div className="text-xs text-gray-500 mt-0.5">
                                                Automatically detect language
                                            </div>
                                        )}
                                    </div>
                                    {selectedLanguage === code && (
                                        <svg className="w-5 h-5 text-blue-400" fill="currentColor" viewBox="0 0 20 20">
                                            <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                                        </svg>
                                    )}
                                </motion.button>
                            ))}
                        </div>

                        {/* Footer Info */}
                        <div className="sticky bottom-0 bg-gray-800 border-t border-gray-700 p-3">
                            <p className="text-xs text-gray-500 text-center">
                                Voice response in English, Kannada, or Hindi
                            </p>
                        </div>
                    </motion.div>
                </>
            )}
        </div>
    )
}
