import { motion } from 'framer-motion'

export default function DeskSetup3D() {
    return (
        <div className="relative w-full h-full flex items-center justify-center" style={{ perspective: '1200px' }}>
            {/* 3D Desk Container */}
            <motion.div
                initial={{ opacity: 0, scale: 0.8, rotateX: 20 }}
                animate={{
                    opacity: 1,
                    scale: 1,
                    rotateX: 0,
                    rotateY: [0, 5, 0, -5, 0],
                }}
                transition={{
                    opacity: { duration: 0.8 },
                    scale: { duration: 0.8 },
                    rotateX: { duration: 0.8 },
                    rotateY: {
                        duration: 8,
                        repeat: Infinity,
                        ease: "easeInOut"
                    }
                }}
                className="relative"
                style={{
                    transformStyle: 'preserve-3d',
                    transform: 'rotateX(-10deg) rotateY(-15deg)'
                }}
            >
                {/* Desk Base */}
                <div className="relative" style={{ transformStyle: 'preserve-3d' }}>
                    {/* Desk Surface */}
                    <motion.div
                        className="relative bg-gradient-to-br from-gray-800 via-gray-700 to-gray-800 rounded-2xl shadow-2xl"
                        style={{
                            width: '500px',
                            height: '350px',
                            transform: 'translateZ(0px)',
                            boxShadow: '0 30px 60px rgba(0,0,0,0.5)'
                        }}
                    >
                        {/* Desk Top Shadow */}
                        <div className="absolute inset-0 bg-black/20 rounded-2xl" style={{ transform: 'translateZ(-2px)' }}></div>
                    </motion.div>

                    {/* Monitor */}
                    <motion.div
                        initial={{ y: 20, opacity: 0 }}
                        animate={{ y: 0, opacity: 1 }}
                        transition={{ delay: 0.3, duration: 0.6 }}
                        className="absolute left-1/2 -translate-x-1/2"
                        style={{
                            bottom: '180px',
                            transformStyle: 'preserve-3d',
                        }}
                    >
                        {/* Monitor Screen */}
                        <div
                            className="relative bg-gradient-to-br from-gray-900 to-black rounded-2xl p-3 shadow-2xl"
                            style={{
                                width: '320px',
                                height: '200px',
                                transform: 'translateZ(50px)',
                                boxShadow: '0 20px 60px rgba(6, 182, 212, 0.3)'
                            }}
                        >
                            {/* Screen Content - DocGuru Interface */}
                            <div className="w-full h-full bg-[#0a0f1e] rounded-xl overflow-hidden relative border-2 border-cyan-500/30">
                                {/* Screen Glow */}
                                <div className="absolute inset-0 bg-gradient-to-br from-cyan-500/20 to-purple-500/20"></div>

                                {/* DocGuru Logo on Screen */}
                                <div className="relative z-10 flex flex-col items-center justify-center h-full p-4">
                                    <motion.div
                                        animate={{
                                            scale: [1, 1.05, 1],
                                            opacity: [0.8, 1, 0.8]
                                        }}
                                        transition={{
                                            duration: 3,
                                            repeat: Infinity,
                                            ease: "easeInOut"
                                        }}
                                        className="flex items-center gap-2 mb-3"
                                    >
                                        <div className="w-10 h-10 bg-gradient-to-br from-cyan-500 to-purple-600 rounded-lg flex items-center justify-center">
                                            <svg className="w-6 h-6 text-white" viewBox="0 0 24 24" fill="currentColor">
                                                <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm0 18c-4.41 0-8-3.59-8-8 0-1.48.41-2.86 1.12-4.06l10.94 10.94C14.86 19.59 13.48 20 12 20zm6.88-3.94L8.94 6.12C10.14 5.41 11.52 5 13 5c4.41 0 8 3.59 8 8 0 1.48-.41 2.86-1.12 4.06z"/>
                                            </svg>
                                        </div>
                                        <span className="text-white text-xl font-bold">DocGuru</span>
                                    </motion.div>

                                    {/* Animated Lines */}
                                    <div className="space-y-2 w-full">
                                        <motion.div
                                            animate={{ width: ['60%', '80%', '60%'] }}
                                            transition={{ duration: 2, repeat: Infinity }}
                                            className="h-2 bg-gradient-to-r from-cyan-500/50 to-transparent rounded mx-auto"
                                        ></motion.div>
                                        <motion.div
                                            animate={{ width: ['70%', '90%', '70%'] }}
                                            transition={{ duration: 2.5, repeat: Infinity }}
                                            className="h-2 bg-gradient-to-r from-purple-500/50 to-transparent rounded mx-auto"
                                        ></motion.div>
                                        <motion.div
                                            animate={{ width: ['50%', '70%', '50%'] }}
                                            transition={{ duration: 3, repeat: Infinity }}
                                            className="h-2 bg-gradient-to-r from-pink-500/50 to-transparent rounded mx-auto"
                                        ></motion.div>
                                    </div>
                                </div>
                            </div>
                        </div>

                        {/* Monitor Stand */}
                        <div
                            className="absolute left-1/2 -translate-x-1/2 w-16 h-12 bg-gradient-to-b from-gray-700 to-gray-800"
                            style={{
                                bottom: '-12px',
                                transform: 'translateX(-50%) translateZ(25px)',
                                clipPath: 'polygon(30% 0, 70% 0, 100% 100%, 0 100%)'
                            }}
                        ></div>
                        <div
                            className="absolute left-1/2 -translate-x-1/2 w-24 h-2 bg-gradient-to-b from-gray-800 to-gray-900 rounded-full"
                            style={{
                                bottom: '-14px',
                                transform: 'translateX(-50%) translateZ(0px)'
                            }}
                        ></div>
                    </motion.div>

                    {/* Keyboard */}
                    <motion.div
                        initial={{ y: 20, opacity: 0 }}
                        animate={{ y: 0, opacity: 1 }}
                        transition={{ delay: 0.5, duration: 0.6 }}
                        className="absolute left-1/2 -translate-x-1/2"
                        style={{
                            bottom: '80px',
                            transformStyle: 'preserve-3d',
                        }}
                    >
                        <div
                            className="bg-gradient-to-br from-gray-800 to-gray-900 rounded-xl p-3 shadow-xl"
                            style={{
                                width: '220px',
                                height: '80px',
                                transform: 'translateZ(10px) rotateX(5deg)',
                            }}
                        >
                            {/* Keyboard Keys */}
                            <div className="grid grid-cols-12 gap-1">
                                {[...Array(36)].map((_, i) => (
                                    <motion.div
                                        key={i}
                                        animate={{
                                            opacity: [0.3, 0.5, 0.3]
                                        }}
                                        transition={{
                                            duration: 2,
                                            repeat: Infinity,
                                            delay: i * 0.05
                                        }}
                                        className="h-2 bg-gray-700 rounded-sm"
                                        style={{ gridColumn: i === 35 ? 'span 4' : 'span 1' }}
                                    />
                                ))}
                            </div>
                        </div>
                    </motion.div>

                    {/* Mouse */}
                    <motion.div
                        initial={{ x: 20, opacity: 0 }}
                        animate={{ x: 0, opacity: 1 }}
                        transition={{ delay: 0.7, duration: 0.6 }}
                        className="absolute"
                        style={{
                            right: '80px',
                            bottom: '90px',
                            transformStyle: 'preserve-3d',
                        }}
                    >
                        <div
                            className="bg-gradient-to-br from-gray-700 to-gray-800 rounded-full shadow-lg"
                            style={{
                                width: '35px',
                                height: '50px',
                                transform: 'translateZ(10px) rotateX(5deg)',
                            }}
                        >
                            <div className="w-1 h-4 bg-gray-900 mx-auto mt-2 rounded-full"></div>
                        </div>
                    </motion.div>

                    {/* Coffee Mug */}
                    <motion.div
                        initial={{ x: -20, opacity: 0 }}
                        animate={{
                            x: 0,
                            opacity: 1,
                        }}
                        transition={{ delay: 0.9, duration: 0.6 }}
                        className="absolute"
                        style={{
                            left: '70px',
                            bottom: '90px',
                            transformStyle: 'preserve-3d',
                        }}
                    >
                        <div
                            className="relative bg-gradient-to-br from-cyan-600 to-cyan-700 rounded-lg shadow-lg"
                            style={{
                                width: '40px',
                                height: '45px',
                                transform: 'translateZ(10px)',
                            }}
                        >
                            {/* Steam */}
                            <motion.div
                                animate={{
                                    opacity: [0.3, 0.6, 0.3],
                                    y: [-5, -15, -5]
                                }}
                                transition={{
                                    duration: 2,
                                    repeat: Infinity,
                                }}
                                className="absolute -top-3 left-1/2 -translate-x-1/2"
                            >
                                <div className="w-1 h-3 bg-cyan-400/40 rounded-full blur-sm"></div>
                            </motion.div>
                            {/* Handle */}
                            <div
                                className="absolute right-0 top-1/2 -translate-y-1/2 w-3 h-5 border-2 border-cyan-600 rounded-r-full"
                                style={{ transform: 'translateX(8px) translateY(-50%)' }}
                            ></div>
                        </div>
                    </motion.div>

                    {/* Notebook/Book */}
                    <motion.div
                        initial={{ opacity: 0, scale: 0.8 }}
                        animate={{ opacity: 1, scale: 1 }}
                        transition={{ delay: 1.1, duration: 0.6 }}
                        className="absolute"
                        style={{
                            right: '60px',
                            bottom: '100px',
                            transformStyle: 'preserve-3d',
                        }}
                    >
                        <div
                            className="bg-gradient-to-br from-purple-600 to-purple-700 shadow-lg"
                            style={{
                                width: '60px',
                                height: '80px',
                                transform: 'translateZ(5px) rotateZ(15deg) rotateY(-20deg)',
                                borderRadius: '4px'
                            }}
                        >
                            <div className="w-full h-1 bg-purple-800/50 mt-10"></div>
                            <div className="w-full h-1 bg-purple-800/30 mt-2"></div>
                        </div>
                    </motion.div>

                    {/* Plant */}
                    <motion.div
                        initial={{ opacity: 0, y: 20 }}
                        animate={{
                            opacity: 1,
                            y: 0,
                        }}
                        transition={{ delay: 1.3, duration: 0.6 }}
                        className="absolute"
                        style={{
                            left: '50px',
                            bottom: '100px',
                            transformStyle: 'preserve-3d',
                        }}
                    >
                        {/* Pot */}
                        <div
                            className="relative bg-gradient-to-br from-red-800 to-red-900 shadow-lg"
                            style={{
                                width: '35px',
                                height: '35px',
                                transform: 'translateZ(5px)',
                                borderRadius: '4px',
                                clipPath: 'polygon(15% 0, 85% 0, 100% 100%, 0 100%)'
                            }}
                        >
                            {/* Leaves */}
                            <motion.div
                                animate={{ rotate: [0, 5, 0, -5, 0] }}
                                transition={{ duration: 4, repeat: Infinity }}
                                className="absolute -top-6 left-1/2 -translate-x-1/2"
                            >
                                <div className="w-6 h-8 bg-green-500 rounded-full" style={{ clipPath: 'ellipse(50% 60% at 50% 40%)' }}></div>
                            </motion.div>
                            <motion.div
                                animate={{ rotate: [0, -5, 0, 5, 0] }}
                                transition={{ duration: 3.5, repeat: Infinity }}
                                className="absolute -top-5 left-0"
                            >
                                <div className="w-5 h-7 bg-green-600 rounded-full" style={{ clipPath: 'ellipse(50% 60% at 50% 40%)' }}></div>
                            </motion.div>
                            <motion.div
                                animate={{ rotate: [0, 3, 0, -3, 0] }}
                                transition={{ duration: 4.5, repeat: Infinity }}
                                className="absolute -top-5 right-0"
                            >
                                <div className="w-5 h-7 bg-green-600 rounded-full" style={{ clipPath: 'ellipse(50% 60% at 50% 40%)' }}></div>
                            </motion.div>
                        </div>
                    </motion.div>
                </div>

                {/* Ambient Lighting */}
                <div className="absolute inset-0 pointer-events-none">
                    <div className="absolute top-0 left-1/4 w-64 h-64 bg-cyan-500/20 rounded-full blur-3xl"></div>
                    <div className="absolute bottom-0 right-1/4 w-64 h-64 bg-purple-500/20 rounded-full blur-3xl"></div>
                </div>
            </motion.div>

            {/* Shadow */}
            <div
                className="absolute bottom-0 left-1/2 -translate-x-1/2 w-[600px] h-32 bg-black/30 rounded-full blur-3xl"
                style={{ transform: 'translateX(-50%) translateY(50px)' }}
            ></div>
        </div>
    )
}
