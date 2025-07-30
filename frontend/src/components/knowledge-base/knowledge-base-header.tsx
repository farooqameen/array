import React from "react";
import { Database, Plus } from "lucide-react";

interface KnowledgeBaseHeaderProps {
  isVisible: boolean;
  onCreateNew: () => void;
}

const KnowledgeBaseHeader: React.FC<KnowledgeBaseHeaderProps> = ({
  isVisible,
  onCreateNew,
}) => (
  <section
    id="header"
    className={`mb-12 transform transition-all duration-1000 ${
      isVisible ? "translate-y-0 opacity-100" : "translate-y-10 opacity-0"
    }`}
  >
    <div className="max-w-7xl mx-auto">
      <div className="flex flex-col lg:flex-row lg:items-center lg:justify-between gap-6">
        <div>
          <div className="inline-flex items-center space-x-2 bg-gradient-to-r from-primary/10 to-secondary/10 rounded-full px-4 py-2 mb-4 border border-primary/20">
            <Database className="w-4 h-4 text-primary" />
            <span className="text-sm font-semibold text-primary">
              Knowledge Repository
            </span>
          </div>

          <h1 className="text-3xl md:text-5xl font-bold text-foreground mb-4">
            Knowledge Base
          </h1>

          <p className="text-lg text-muted-foreground max-w-3xl">
            Create organized knowledge bases for different topics. Each
            knowledge base can contain uploaded documents and scraped web
            content.
          </p>
        </div>

        <div>
          <button
            onClick={onCreateNew}
            className="bg-gradient-to-r from-primary to-secondary text-primary-foreground px-6 py-3 rounded-xl font-semibold flex items-center justify-center space-x-2 hover:shadow-lg transition-all transform hover:scale-105"
          >
            <Plus className="w-5 h-5" />
            <span>New Knowledge Base</span>
          </button>
        </div>
      </div>
    </div>
  </section>
);

export default KnowledgeBaseHeader;
