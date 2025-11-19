import { useState } from 'react'
import { motion, AnimatePresence } from 'framer-motion'

export default function OnboardingTutorial() {
    const [step, setStep] = useState(0)
    const [show, setShow] = useState(!localStorage.getItem('tutorial_completed'))

    const steps = [
        {
            title: "Welcome to DocuMind Voice! 👋",
            description: "Your AI-powered document assistant with multilingual voice support. Let's get you started!",
            icon: "🎓",
            action: "Get Started"
        },
        {
            title: "Upload Your Documents 📄",
            description: "Drag and drop PDFs or click to browse. You can upload up to 5 documents (10MB each) during beta.",
            icon: "📤",
            action: "Next"
        },
        {
            title: "Ask Questions 💬",
            description: "Type or speak your questions in natural language. Our AI will search across all your documents and provide accurate answers.",
            icon: "🤖",
            action: "Next"
        },
        {
            title: "Voice Features 🎤",
            description: "Click the microphone icon to ask questions with your voice. Responses can be read aloud in English, Hindi, or Kannada!",
            icon: "🗣️",
            action: "Next"
        },
        {
            title: "You're All Set! 🎉",
            description: "Start uploading documents and asking questions. Need help? Check the docs or contact support.",
            icon: "✨",
            action: "Start Using DocuMind"
        }
    ]

    const handleNext = () => {
        if (step < steps.length - 1) {
            setStep(step + 1)
        } else {
            localStorage.setItem('tutorial_completed', 'true')
            setShow(false)
        }
    }

    const handleSkip = () => {
        localStorage.setItem('tutorial_completed', 'true')
        setShow(false)
    }

    const handleBack = () => {
        if (step > 0) {
            setStep(step - 1)
        }
    }

    if (!show) return null

    return (
        <AnimatePresence>
            <motion.div
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                exit={{ opacity: 0 }}
                className="fixed inset-0 bg-black/70 backdrop-blur-sm z-50 flex items-center justify-center p-4"
                onClick={(e) => {
                    // Close on backdrop click (but not on modal click)
                    if (e.target === e.currentTarget) {
                        handleSkip()
                    }
                }}
            >
                <motion.div
                    initial={{ scale: 0.9, y: 20 }}
                    animate={{ scale: 1, y: 0 }}
                    exit={{ scale: 0.9, y: 20 }}
                    className="bg-gradient-to-br from-[#1e293b] to-[#0f172a] rounded-2xl p-8 max-w-md w-full border border-white/10 shadow-2xl"
                    onClick={(e) => e.stopPropagation()}
                >
                    {/* Icon */}
                    <div className="text-6xl mb-4 text-center animate-bounce-slow">
                        {steps[step].icon}
                    </div>

                    {/* Title */}
                    <h2 className="text-2xl font-bold text-white mb-3 text-center bg-gradient-to-r from-cyan-400 to-purple-400 bg-clip-text text-transparent">
                        {steps[step].title}
                    </h2>

                    {/* Description */}
                    <p className="text-gray-300 mb-6 text-center leading-relaxed">
                        {steps[step].description}
                    </p>

                    {/* Progress dots */}
                    <div className="flex gap-2 mb-6 justify-center">
                        {steps.map((_, i) => (
                            <button
                                key={i}
                                onClick={() => setStep(i)}
                                className={`h-2 rounded-full transition-all duration-300 ${
                                    i === step
                                        ? 'w-8 bg-gradient-to-r from-cyan-500 to-purple-500'
                                        : i < step
                                        ? 'w-2 bg-cyan-500/50'
                                        : 'w-2 bg-white/20'
                                }`}
                                aria-label={`Go to step ${i + 1}`}
                            />
                        ))}
                    </div>

                    {/* Step counter */}
                    <div className="text-center text-sm text-gray-400 mb-6">
                        Step {step + 1} of {steps.length}
                    </div>

                    {/* Buttons */}
                    <div className="flex gap-3">
                        {/* Back button (only show if not on first step) */}
                        {step > 0 && (
                            <button
                                onClick={handleBack}
                                className="px-4 py-2 text-gray-400 hover:text-white transition-colors rounded-lg hover:bg-white/5"
                            >
                                ← Back
                            </button>
                        )}

                        {/* Skip button (only show if not on last step) */}
                        {step < steps.length - 1 && (
                            <button
                                onClick={handleSkip}
                                className="px-4 py-2 text-gray-400 hover:text-white transition-colors rounded-lg hover:bg-white/5"
                            >
                                Skip
                            </button>
                        )}

                        {/* Next/Finish button */}
                        <button
                            onClick={handleNext}
                            className="flex-1 px-6 py-3 bg-gradient-to-r from-cyan-500 to-purple-600 hover:from-cyan-600 hover:to-purple-700 text-white font-semibold rounded-lg transition-all transform hover:scale-105 shadow-lg shadow-cyan-500/30"
                        >
                            {steps[step].action} →
                        </button>
                    </div>

                    {/* Reset tutorial link (small text at bottom) */}
                    <div className="mt-6 text-center">
                        <button
                            onClick={() => {
                                localStorage.removeItem('tutorial_completed')
                                setStep(0)
                                setShow(true)
                            }}
                            className="text-xs text-gray-500 hover:text-gray-300 transition-colors"
                        >
                            Restart tutorial
                        </button>
                    </div>
                </motion.div>
            </motion.div>
        </AnimatePresence>
    )
}
