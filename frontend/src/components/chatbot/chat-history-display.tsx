// src/components/chatbot/chat-history-display.tsx
import React from "react";
import ChatMessage from "./chat-message";
import {
  ChatMessage as ChatMessageType,
  initialSuggestions,
  KnowledgeBase,
} from "@/components/data/constants";
import ChatSuggestions from "./chat-suggestions";
import { MessageSquare } from "lucide-react";

/**
 * Props for the ChatHistoryDisplay component.
 * @interface
 */
interface ChatHistoryDisplayProps {
  /** The array of chat messages to display. */
  chatHistory: ChatMessageType[];
  /** Callback function for when a suggestion is clicked. */
  onSuggestionClick: (suggestion: string) => void;
  /** The currently selected knowledge base. Can be null for general chat. */
  selectedKnowledgeBase: KnowledgeBase | null;
}

/**
 * ChatHistoryDisplay component manages the display of chat messages and initial suggestions.
 * @param {ChatHistoryDisplayProps} props - The component props.
 * @returns {React.FC} A React functional component.
 */
const ChatHistoryDisplay: React.FC<ChatHistoryDisplayProps> = ({
  chatHistory,
  onSuggestionClick,
  selectedKnowledgeBase,
}) => {
  return (
    <div className="flex-1 flex flex-col">
      {/* Top bar showing selected knowledge base */}
      <div className="flex items-center justify-between mb-6 p-4 bg-muted rounded-xl">
        <div className="flex items-center space-x-3">
          <div className="w-8 h-8 bg-gradient-to-r from-primary to-secondary rounded-lg flex items-center justify-center">
            <MessageSquare className="w-4 h-4 text-primary-foreground" />
          </div>
          <div>
            <span className="text-sm text-muted-foreground">
              Chatting with:
            </span>
            <span className="ml-2 font-semibold text-foreground">
              {selectedKnowledgeBase
                ? selectedKnowledgeBase.name
                : "General Chat"}
            </span>
          </div>
        </div>
        {/*
          This button is currently handled by the parent (ChatbotPage)
          but could be lifted here if the state for showKnowledgeBaseSelector
          was also passed down. For now, it's commented out to avoid redundancy.
        */}
        {/* <button
          onClick={() => {
            // Logic to go back to KB selection
          }}
          className="px-4 py-2 text-primary hover:bg-card rounded-lg transition-colors font-medium text-sm"
        >
          Change Knowledge Base
        </button> */}
      </div>

      {/* Show logo and suggestions only when no chat history */}
      {chatHistory.length === 0 ? (
        <div className="flex-1 flex flex-col items-center justify-center p-4">
          {/* Logo and Greeting */}
          <div className="text-center mb-16">
            <img
              src="/array-logo.png" // Ensure this path is correct relative to your public folder
              alt="Array Logo"
              className="h-16 mx-auto mb-8"
            />
            <h1 className="text-xl sm:text-2xl md:text-3xl lg:text-4xl font-semibold bg-gradient-to-r from-primary to-secondary text-transparent bg-clip-text text-center">
              How can I assist you?
            </h1>
          </div>

          {/* Chat Suggestions */}
          <ChatSuggestions
            suggestions={initialSuggestions}
            onSuggestionClick={onSuggestionClick}
          />
        </div>
      ) : (
        /* Show chat history when there are messages */
        <div className="flex-1 w-full max-w-4xl mx-auto overflow-y-auto mb-4 p-4">
          {chatHistory.map((msg, index) => (
            <ChatMessage key={index} message={msg} />
          ))}
        </div>
      )}
    </div>
  );
};

export default ChatHistoryDisplay;
