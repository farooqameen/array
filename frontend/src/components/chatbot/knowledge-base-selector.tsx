// src/components/chatbot/knowledge-base-selector.tsx
import React from "react";
import KnowledgeBaseCard from "./knowledge-base-card";
import { knowledgeBases, KnowledgeBase } from "@/components/data/constants";
import { MessageSquare, ChevronRight } from "lucide-react";

/**
 * Props for the KnowledgeBaseSelector component.
 * @interface
 */
interface KnowledgeBaseSelectorProps {
  /** Callback function to set the selected knowledge base. */
  onSelect: (kb: KnowledgeBase | null) => void;
}

/**
 * KnowledgeBaseSelector component displays options for selecting a knowledge base or general chat.
 * @param {KnowledgeBaseSelectorProps} props - The component props.
 * @returns {React.FC} A React functional component.
 */
const KnowledgeBaseSelector: React.FC<KnowledgeBaseSelectorProps> = ({
  onSelect,
}) => {
  return (
    <div className="flex-1 flex flex-col items-center justify-center p-4">
      {/* Logo and Title */}
      <div className="text-center mb-16">
        <img
          src="/array-logo.png" // Ensure this path is correct relative to your public folder
          alt="Array Logo"
          className="h-24 md:h-28 lg:h-32 mx-auto mb-10"
        />
        <h1 className="text-xl sm:text-2xl md:text-3xl lg:text-4xl font-semibold bg-gradient-to-r from-primary to-secondary text-transparent bg-clip-text text-center mb-4">
          Choose Your Knowledge Base
        </h1>
        <p className="text-lg text-muted-foreground max-w-2xl mx-auto">
          Select a knowledge base to chat with, or choose general chat for
          broader conversations.
        </p>
      </div>

      {/* Knowledge Base Options */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 max-w-5xl w-full mb-12">
        {/* General Chat Option */}
        <button
          onClick={() => onSelect(null)}
          className="bg-card border-2 border-border rounded-2xl p-8 text-left hover:shadow-lg hover:border-primary/40 cursor-pointer transition-all transform hover:scale-105"
        >
          <div className="w-16 h-16 bg-gradient-to-r from-muted-foreground to-gray-600 rounded-2xl flex items-center justify-center mb-6">
            <MessageSquare className="w-8 h-8 text-white" />
          </div>
          <h3 className="text-xl font-bold text-foreground mb-4">
            General Chat
          </h3>
          <p className="text-muted-foreground leading-relaxed mb-4">
            Chat without any specific knowledge base. General AI assistance and
            conversations.
          </p>
          <div className="flex items-center text-primary font-semibold text-sm">
            Start General Chat <ChevronRight className="w-4 h-4 ml-1" />
          </div>
        </button>

        {/* Dynamic Knowledge Base Options */}
        {knowledgeBases.map((kb) => (
          <KnowledgeBaseCard key={kb.id} kb={kb} onClick={onSelect} />
        ))}
      </div>
    </div>
  );
};

export default KnowledgeBaseSelector;
