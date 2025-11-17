import { motion } from 'framer-motion'

export default function ThinkingAnimation() {
    return (
        <motion.div
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -10 }}
            className="flex justify-start mb-6"
        >
            <div className="flex gap-3 max-w-3xl">
                {/* AI Avatar */}
                <motion.div
                    initial={{ scale: 0 }}
                    animate={{ scale: 1 }}
                    transition={{ type: 'spring', stiffness: 200 }}
                    className="flex-shrink-0 w-10 h-10 rounded-full flex items-center justify-center text-white font-semibold shadow-lg bg-gradient-to-br from-purple-500 to-pink-600 shadow-purple-500/50"
                >
                    AI
                </motion.div>

                {/* Simple Thinking Card */}
                <motion.div
                    initial={{ scale: 0.95, opacity: 0 }}
                    animate={{ scale: 1, opacity: 1 }}
                    transition={{ duration: 0.3 }}
                    className="flex-1 rounded-2xl p-5 backdrop-blur-sm bg-white/5 border border-white/10 shadow-lg"
                >
                    {/* Simple Typing Dots */}
                    <div className="flex items-center gap-2">
                        {[0, 1, 2].map((i) => (
                            <motion.div
                                key={i}
                                className="w-2.5 h-2.5 rounded-full bg-gradient-to-r from-cyan-400 to-purple-400"
                                animate={{
                                    y: [0, -8, 0],
                                    opacity: [0.5, 1, 0.5]
                                }}
                                transition={{
                                    duration: 0.8,
                                    repeat: Infinity,
                                    delay: i * 0.15,
                                    ease: "easeInOut"
                                }}
                            />
                        ))}
                    </div>
                </motion.div>
            </div>
        </motion.div>
    )
}
