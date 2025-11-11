import { useState, useEffect } from 'react'

export default function BrowserWarning() {
    const [show, setShow] = useState(false)
    const [dismissed, setDismissed] = useState(false)

    useEffect(() => {
        // Check if browser supports Web Speech API
        const isSupported = 'webkitSpeechRecognition' in window || 'SpeechRecognition' in window

        // Check if user has already dismissed the warning
        const wasDismissed = localStorage.getItem('browser-warning-dismissed') === 'true'

        if (!isSupported && !wasDismissed) {
            setShow(true)
        }
    }, [])

    const handleDismiss = () => {
        setDismissed(true)
        setShow(false)
        localStorage.setItem('browser-warning-dismissed', 'true')
    }

    if (!show || dismissed) {
        return null
    }

    return (
        <div className="bg-yellow-500/10 border-l-4 border-yellow-500 p-4 mb-4">
            <div className="flex items-start justify-between">
                <div className="flex items-start gap-3">
                    <svg
                        className="w-6 h-6 text-yellow-500 flex-shrink-0 mt-0.5"
                        fill="none"
                        stroke="currentColor"
                        viewBox="0 0 24 24"
                    >
                        <path
                            strokeLinecap="round"
                            strokeLinejoin="round"
                            strokeWidth={2}
                            d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"
                        />
                    </svg>
                    <div>
                        <h3 className="text-sm font-semibold text-yellow-300">
                            Voice Features Limited
                        </h3>
                        <p className="mt-1 text-sm text-yellow-200/80">
                            Your browser doesn't support voice recognition. For the best experience, please use{' '}
                            <span className="font-medium text-yellow-100">Chrome, Edge, or Safari</span>.
                            <br />
                            Text input works perfectly in all browsers.
                        </p>
                    </div>
                </div>
                <button
                    onClick={handleDismiss}
                    className="text-yellow-400 hover:text-yellow-300 transition-colors ml-4"
                    aria-label="Dismiss warning"
                >
                    <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                    </svg>
                </button>
            </div>
        </div>
    )
}
