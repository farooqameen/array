// src/components/document/knowledge-base-selector.tsx
"use client";

import React from "react";
import { Search, ChevronRight, Database } from "lucide-react";
import { useKnowledgeStore } from "@/lib/stores/knowledgeStore";
import type { KnowledgeBase } from "@/lib/stores/knowledgeStore";

/**
 * @typedef {object} KnowledgeBase
 * @property {string} id - Unique identifier for the knowledge base.
 * @property {string} name - Display name of the knowledge base.
 * @property {string} description - Brief description of the knowledge base.
 * @property {number} documentsCount - Number of documents in the knowledge base.
 * @property {number} scrapedPagesCount - Number of scraped pages in the knowledge base.
 */

interface KnowledgeBaseSelectorProps {
  /** Callback function when a knowledge base is selected. */
  onSelectKnowledgeBase: (kb: KnowledgeBase | null) => void;
}

/**
 * Renders a selection interface for choosing a knowledge base for document search.
 * Allows users to select a specific knowledge base or opt for a general search.
 * @param {object} props - The component props.
 * @param {(kb: KnowledgeBase | null) => void} props.onSelectKnowledgeBase - Callback when a knowledge base is chosen. `null` for general search.
 */
const KnowledgeBaseSelector: React.FC<KnowledgeBaseSelectorProps> = ({
  onSelectKnowledgeBase,
}) => {
  const knowledgeBases = useKnowledgeStore((state) => state.knowledgeBases);

  return (
    <div className="flex-1 flex flex-col items-center justify-center p-4 min-h-screen bg-background">
      {/* Logo and Title */}
      <div className="text-center mb-16">
        <img
          src="/array-logo.png" // Ensure this path is correct
          alt="Array Logo"
          className="h-24 md:h-28 lg:h-32 mx-auto mb-10"
        />
        <h1 className="text-xl sm:text-2xl md:text-3xl lg:text-4xl font-semibold bg-gradient-to-r from-cyan-400 via-purple-500 to-pink-500 text-transparent bg-clip-text text-center mb-4">
          Choose Your Knowledge Base for Search
        </h1>
        <p className="text-lg text-muted-foreground max-w-2xl mx-auto">
          Select a knowledge base to narrow your document search, or choose
          general search for broader results.
        </p>
      </div>

      {/* Knowledge Base Options */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 max-w-5xl w-full mb-12">
        {/* General Document Search Option */}
        <button
          onClick={() => onSelectKnowledgeBase(null)}
          className="bg-card border-2 border-border rounded-2xl p-8 text-left hover:shadow-lg hover:border-primary/40 cursor-pointer transition-all transform hover:scale-105"
        >
          <div className="w-16 h-16 bg-gradient-to-r from-gray-400 to-gray-600 rounded-2xl flex items-center justify-center mb-6">
            <Search className="w-8 h-8 text-white" />
          </div>
          <h3 className="text-xl font-bold text-foreground mb-4">
            General Document Search
          </h3>
          <p className="text-muted-foreground leading-relaxed mb-4">
            Search across all available documents without a specific knowledge
            base.
          </p>
          <div className="flex items-center text-primary font-semibold text-sm">
            Start General Search <ChevronRight className="w-4 h-4 ml-1" />
          </div>
        </button>

        {/* Knowledge Base Specific Options */}
        {knowledgeBases.map((kb: KnowledgeBase) => (
          <button
            key={kb.id}
            onClick={() => onSelectKnowledgeBase(kb)}
            className="bg-card border-2 border-border rounded-2xl p-8 text-left hover:shadow-lg hover:border-primary/40 cursor-pointer transition-all transform hover:scale-105"
          >
            <div className="w-16 h-16 bg-gradient-to-r from-primary to-purple-400 rounded-2xl flex items-center justify-center mb-6">
              <Database className="w-8 h-8 text-white" />
            </div>
            <h3 className="text-xl font-bold text-foreground mb-4">
              {kb.name}
            </h3>
            <p className="text-muted-foreground leading-relaxed mb-4">
              {kb.description}
            </p>
            <div className="flex items-center justify-between text-sm text-muted-foreground mb-4">
              <span>{kb.documentsCount} documents</span>
              <span>{kb.scrapedPagesCount} scraped pages</span>
            </div>
            <div className="flex items-center text-primary font-semibold text-sm">
              Search in {kb.name} <ChevronRight className="w-4 h-4 ml-1" />
            </div>
          </button>
        ))}
      </div>
    </div>
  );
};

export default KnowledgeBaseSelector;
