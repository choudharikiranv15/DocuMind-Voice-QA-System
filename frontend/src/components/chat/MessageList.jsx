import { useChatStore } from '../../stores/chatStore'
import Message from './Message'

export default function MessageList() {
    const messages = useChatStore(state => state.messages)

    return (
        <div className="max-w-4xl mx-auto space-y-6">
            {messages.map((message) => (
                <Message key={message.id} message={message} />
            ))}
        </div>
    )
}
