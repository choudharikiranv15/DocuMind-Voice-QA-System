import { useState } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import FeedbackModal from './FeedbackModal'

export default function FeedbackButton() {
    const [isModalOpen, setIsModalOpen] = useState(false)
    const [isHovered, setIsHovered] = useState(false)

    return (
        <>
            {/* Floating Feedback Button */}
            <motion.button
                onClick={() => setIsModalOpen(true)}
                onMouseEnter={() => setIsHovered(true)}
                onMouseLeave={() => setIsHovered(false)}
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
                className="fixed bottom-6 right-6 z-40 bg-gradient-to-r from-purple-600 to-pink-600 hover:from-purple-700 hover:to-pink-700 text-white rounded-full shadow-2xl shadow-purple-500/50 flex items-center gap-3 transition-all group"
                style={{
                    padding: isHovered ? '12px 24px 12px 16px' : '16px'
                }}
            >
                {/* Icon */}
                <motion.div
                    animate={{ rotate: isHovered ? 0 : 0 }}
                    transition={{ duration: 0.3 }}
                >
                    <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 8h10M7 12h4m1 8l-4-4H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-3l-4 4z" />
                    </svg>
                </motion.div>

                {/* Text (shown on hover) */}
                <AnimatePresence>
                    {isHovered && (
                        <motion.span
                            initial={{ width: 0, opacity: 0 }}
                            animate={{ width: 'auto', opacity: 1 }}
                            exit={{ width: 0, opacity: 0 }}
                            transition={{ duration: 0.2 }}
                            className="font-semibold text-sm whitespace-nowrap overflow-hidden"
                        >
                            Give Feedback
                        </motion.span>
                    )}
                </AnimatePresence>

                {/* Pulse animation */}
                <span className="absolute inset-0 rounded-full">
                    <span className="animate-ping absolute inset-0 rounded-full bg-purple-400 opacity-75" style={{ animationDuration: '3s' }} />
                </span>
            </motion.button>

            {/* Feedback Modal */}
            <FeedbackModal isOpen={isModalOpen} onClose={() => setIsModalOpen(false)} />
        </>
    )
}
