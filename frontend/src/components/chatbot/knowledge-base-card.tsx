// src/components/chatbot/knowledge-base-card.tsx
import React from "react";
import { ChevronRight, MessageSquare } from "lucide-react";
import { KnowledgeBase } from "@/components/data/constants"; // Import the type

/**
 * Props for the KnowledgeBaseCard component.
 * @interface
 */
interface KnowledgeBaseCardProps {
  /** The knowledge base data to display. */
  kb: KnowledgeBase;
  /** Callback function when the card is clicked. */
  onClick: (kb: KnowledgeBase) => void;
}

/**
 * KnowledgeBaseCard component displays a single knowledge base as a selectable card.
 * @param {KnowledgeBaseCardProps} props - The component props.
 * @returns {React.FC} A React functional component.
 */
const KnowledgeBaseCard: React.FC<KnowledgeBaseCardProps> = ({
  kb,
  onClick,
}) => {
  return (
    <button
      onClick={() => onClick(kb)}
      className="bg-card border-2 border-border rounded-2xl p-8 text-left hover:shadow-lg hover:border-primary/40 cursor-pointer transition-all transform hover:scale-105"
    >
      <div className="w-16 h-16 bg-gradient-to-r from-primary to-secondary rounded-2xl flex items-center justify-center mb-6">
        <MessageSquare className="w-8 h-8 text-primary-foreground" />
      </div>
      <h3 className="text-xl font-bold text-foreground mb-4">{kb.name}</h3>
      <p className="text-muted-foreground leading-relaxed mb-4">
        {kb.description}
      </p>
      <div className="flex items-center justify-between text-sm text-muted-foreground mb-4">
        <span>{kb.documentsCount} documents</span>
        <span>{kb.scrapedPagesCount} scraped pages</span>
      </div>
      <div className="flex items-center text-primary font-semibold text-sm">
        Chat with {kb.name}
        <ChevronRight className="w-4 h-4 ml-1" />
      </div>
    </button>
  );
};

export default KnowledgeBaseCard;
