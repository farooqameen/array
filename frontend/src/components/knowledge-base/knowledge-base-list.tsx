// components/KnowledgeBaseList.tsx
import React from "react";
import { KnowledgeBase } from "@/lib/stores/knowledgeStore";
import KnowledgeBaseCard from "@/components/knowledge-base/knowledge-base-card";
import EmptyState from "@/components/knowledge-base/empty-state";
import { Database, Plus } from "lucide-react";
import { Search } from "lucide-react";

interface KnowledgeBaseListProps {
  knowledgeBases: KnowledgeBase[];
  searchQuery: string;
  setSearchQuery: (query: string) => void;
  onSelectKnowledgeBase: (id: number) => void;
  onAddContentToKnowledgeBase: (id: number) => void;
  onDeleteKnowledgeBase: (id: number) => void;
  onCreateFirstKnowledgeBase: () => void;
}

const KnowledgeBaseList: React.FC<KnowledgeBaseListProps> = ({
  knowledgeBases,
  searchQuery,
  setSearchQuery,
  onSelectKnowledgeBase,
  onAddContentToKnowledgeBase,
  onDeleteKnowledgeBase,
  onCreateFirstKnowledgeBase,
}) => {
  const filteredKnowledgeBases = knowledgeBases.filter(
    (kb) =>
      kb.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
      kb.description.toLowerCase().includes(searchQuery.toLowerCase())
  );

  return (
    <section id="knowledge-bases" className="max-w-7xl mx-auto">
      <div className="mb-8">
        <h2 className="text-2xl font-bold text-foreground mb-4">
          Your Knowledge Bases
        </h2>
        <div className="relative">
          <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-5 h-5 text-muted-foreground" />
          <input
            type="text"
            placeholder="Search knowledge bases..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="w-full pl-12 pr-4 py-3 border border-input rounded-xl focus:ring-2 focus:ring-primary focus:border-transparent bg-background text-foreground"
          />
        </div>
      </div>

      {knowledgeBases.length === 0 ? (
        <EmptyState
          icon={Database}
          title="No knowledge bases yet"
          description="Create your first knowledge base to get started"
          buttonText="Create Your First Knowledge Base"
          onButtonClick={onCreateFirstKnowledgeBase}
        />
      ) : (
        <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
          {filteredKnowledgeBases.length > 0 ? (
            filteredKnowledgeBases.map((kb) => (
              <KnowledgeBaseCard
                key={kb.id}
                kb={kb}
                onSelect={onSelectKnowledgeBase}
                onAddContent={onAddContentToKnowledgeBase}
                onDelete={onDeleteKnowledgeBase}
              />
            ))
          ) : (
            <div className="col-span-full text-center py-8 text-muted-foreground">
              No knowledge bases match your search.
            </div>
          )}
        </div>
      )}
    </section>
  );
};

export default KnowledgeBaseList;
