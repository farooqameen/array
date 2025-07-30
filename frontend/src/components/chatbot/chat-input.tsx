// src/components/chatbot/chat-input.tsx
import React from "react";
import { Send, Filter } from "lucide-react";

/**
 * Props for the ChatInput component.
 * @interface
 */
interface ChatInputProps {
  /** The current message value in the input field. */
  message: string;
  /** Callback function to update the message value. */
  onMessageChange: (value: string) => void;
  /** Callback function to handle sending the message. */
  onSendMessage: () => void;
}

/**
 * ChatInput component provides the text input field and send/filter buttons for the chatbot.
 * @param {ChatInputProps} props - The component props.
 * @returns {React.FC} A React functional component.
 */
const ChatInput: React.FC<ChatInputProps> = ({
  message,
  onMessageChange,
  onSendMessage,
}) => {
  return (
    <div className="w-full max-w-4xl mx-auto py-4">
      <div className="relative flex items-center bg-card border border-border rounded-2xl shadow-sm overflow-hidden">
        <input
          type="text"
          placeholder="Send a message..."
          className="flex-1 p-4 pr-16 bg-transparent text-foreground placeholder-muted-foreground focus:outline-none"
          value={message}
          onChange={(e) => onMessageChange(e.target.value)}
          onKeyPress={(e) => {
            if (e.key === "Enter") {
              onSendMessage();
            }
          }}
        />
        <button
          onClick={onSendMessage}
          className="absolute right-16 p-2 rounded-xl bg-gradient-to-r from-primary to-secondary text-primary-foreground hover:shadow-lg transition-colors"
          aria-label="Send message"
        >
          <Send className="w-5 h-5" />
        </button>
        <button
          className="absolute right-4 p-2 rounded-xl text-muted-foreground hover:bg-accent transition-colors"
          aria-label="Filter options"
        >
          <Filter className="w-5 h-5" />
        </button>
      </div>
    </div>
  );
};

export default ChatInput;
