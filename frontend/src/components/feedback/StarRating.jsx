import { motion } from 'framer-motion'
import { useState } from 'react'

export default function StarRating({ rating, setRating, size = 'md', label, required = false }) {
    const [hoveredStar, setHoveredStar] = useState(0)

    const sizes = {
        sm: 'w-5 h-5',
        md: 'w-7 h-7',
        lg: 'w-9 h-9'
    }

    const handleClick = (value) => {
        setRating(value)
    }

    return (
        <div className="space-y-2">
            {label && (
                <label className="block text-sm font-medium text-gray-300">
                    {label}
                    {required && <span className="text-red-400 ml-1">*</span>}
                </label>
            )}
            <div className="flex items-center gap-1">
                {[1, 2, 3, 4, 5].map((value) => (
                    <motion.button
                        key={value}
                        type="button"
                        onClick={() => handleClick(value)}
                        onMouseEnter={() => setHoveredStar(value)}
                        onMouseLeave={() => setHoveredStar(0)}
                        whileHover={{ scale: 1.2 }}
                        whileTap={{ scale: 0.9 }}
                        className="focus:outline-none"
                    >
                        <svg
                            className={`${sizes[size]} transition-colors ${
                                value <= (hoveredStar || rating)
                                    ? 'text-yellow-400 fill-current'
                                    : 'text-gray-600 fill-current'
                            }`}
                            viewBox="0 0 20 20"
                        >
                            <path d="M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.07 3.292a1 1 0 00.95.69h3.462c.969 0 1.371 1.24.588 1.81l-2.8 2.034a1 1 0 00-.364 1.118l1.07 3.292c.3.921-.755 1.688-1.54 1.118l-2.8-2.034a1 1 0 00-1.175 0l-2.8 2.034c-.784.57-1.838-.197-1.539-1.118l1.07-3.292a1 1 0 00-.364-1.118L2.98 8.72c-.783-.57-.38-1.81.588-1.81h3.461a1 1 0 00.951-.69l1.07-3.292z" />
                        </svg>
                    </motion.button>
                ))}
                {rating > 0 && (
                    <motion.span
                        initial={{ opacity: 0, x: -10 }}
                        animate={{ opacity: 1, x: 0 }}
                        className="ml-2 text-sm text-gray-400"
                    >
                        {rating === 1 && '😞 Poor'}
                        {rating === 2 && '😕 Fair'}
                        {rating === 3 && '😐 Good'}
                        {rating === 4 && '😊 Very Good'}
                        {rating === 5 && '🤩 Excellent'}
                    </motion.span>
                )}
            </div>
        </div>
    )
}
