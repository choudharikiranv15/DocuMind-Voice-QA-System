import AudioPlayer from '../voice/AudioPlayer'

export default function Message({ message }) {
    const isUser = message.role === 'user'

    return (
        <div className={`flex ${isUser ? 'justify-end' : 'justify-start'} mb-6`}>
            <div className={`flex gap-3 max-w-3xl ${isUser ? 'flex-row-reverse' : 'flex-row'}`}>
                {/* Avatar */}
                <div className={`
          flex-shrink-0 w-10 h-10 rounded-full flex items-center justify-center text-white font-semibold
          ${isUser
                        ? 'bg-gradient-to-br from-indigo-500 to-purple-600'
                        : 'bg-gradient-to-br from-purple-500 to-pink-600'
                    }
        `}>
                    {isUser ? 'U' : 'AI'}
                </div>

                {/* Message Content */}
                <div className={`
          flex-1 rounded-2xl p-4
          ${isUser
                        ? 'bg-indigo-600 text-white'
                        : 'bg-[#1e293b] border border-gray-800 text-gray-100'
                    }
        `}>
                    {/* Text */}
                    <div className="prose prose-sm max-w-none">
                        <p className={`leading-relaxed ${isUser ? 'text-white' : 'text-gray-100'}`}>
                            {message.text}
                        </p>
                    </div>

                    {/* Audio Player (if message has audio) */}
                    {message.audioUrl && (
                        <div className="mt-3">
                            <AudioPlayer audioUrl={message.audioUrl} />
                        </div>
                    )}

                    {/* Metadata */}
                    {message.metadata && !isUser && (
                        <div className="mt-3 pt-3 border-t border-gray-700 text-xs text-gray-400">
                            <div className="flex items-center gap-4">
                                {message.metadata.sources_used > 0 && (
                                    <span className="flex items-center gap-1">
                                        <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.747 0 3.332.477 4.5 1.253v13C19.832 18.477 18.247 18 16.5 18c-1.746 0-3.332.477-4.5 1.253" />
                                        </svg>
                                        {message.metadata.sources_used} sources
                                    </span>
                                )}
                                {message.metadata.confidence && (
                                    <span className="flex items-center gap-1">
                                        <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                                        </svg>
                                        {Math.round(message.metadata.confidence * 100)}% confidence
                                    </span>
                                )}
                            </div>
                        </div>
                    )}

                    {/* Timestamp */}
                    <div className={`mt-2 text-xs ${isUser ? 'text-indigo-200' : 'text-gray-500'}`}>
                        {new Date(message.timestamp).toLocaleTimeString()}
                    </div>
                </div>
            </div>
        </div>
    )
}
