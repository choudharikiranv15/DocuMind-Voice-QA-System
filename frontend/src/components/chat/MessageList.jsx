import { useChatStore } from '../../stores/chatStore'
import Message from './Message'
import ThinkingAnimation from './ThinkingAnimation'

export default function MessageList({ isLoading }) {
    const messages = useChatStore(state => state.messages)

    return (
        <div className="max-w-4xl mx-auto space-y-6">
            {messages.map((message) => (
                <Message key={message.id} message={message} />
            ))}
            {isLoading && <ThinkingAnimation />}
        </div>
    )
}
