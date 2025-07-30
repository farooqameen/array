// src/components/chatbot/chat-message.tsx
import React from "react";
import { Bot } from "lucide-react";
import { ChatMessage as ChatMessageType } from "@/components/data/constants"; // Alias to avoid naming conflict

/**
 * Props for the ChatMessage component.
 * @interface
 */
interface ChatMessageProps {
  /** The chat message data (type and text). */
  message: ChatMessageType;
}

/**
 * ChatMessage component displays a single chat message (user or bot).
 * @param {ChatMessageProps} props - The component props.
 * @returns {React.FC} A React functional component.
 */
const ChatMessage: React.FC<ChatMessageProps> = ({ message }) => {
  return (
    <div
      className={`mb-6 ${message.type === "user" ? "flex justify-end" : ""}`}
    >
      {message.type === "user" ? (
        <p className="bg-muted p-4 rounded-xl max-w-[600px] sm:max-w-[80vw] break-words text-foreground">
          {message.text}
        </p>
      ) : (
        <div className="group relative flex items-start p-4">
          <div className="flex size-[32px] shrink-0 select-none items-center justify-center rounded-md border shadow-sm bg-card">
            <Bot className="lucide lucide-bot text-muted-foreground" />
          </div>
          <div className="ml-4 flex-1 space-y-2 overflow-hidden">
            <div className="bg-muted border border-border rounded-xl p-4 max-w-[600px] sm:max-w-[80vw]">
              {/* Using dangerouslySetInnerHTML if content contains HTML (e.g., <br />) */}
              <p
                className="text-foreground leading-relaxed break-words"
                dangerouslySetInnerHTML={{ __html: message.text }}
              />
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default ChatMessage;
