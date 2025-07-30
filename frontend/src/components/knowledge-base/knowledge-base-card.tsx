import React from "react";
import { KnowledgeBase } from "@/lib/stores/knowledgeStore";
import { Folder, Plus, Trash2, FileText, Globe, Calendar, ChevronRight } from "lucide-react";

interface KnowledgeBaseCardProps {
  kb: KnowledgeBase;
  onSelect: (id: number) => void;
  onAddContent: (id: number) => void;
  onDelete: (id: number) => void;
}

const KnowledgeBaseCard: React.FC<KnowledgeBaseCardProps> = ({
  kb,
  onSelect,
  onAddContent,
  onDelete,
}) => (
  <div
    key={kb.id}
    onClick={() => onSelect(kb.id)}
    className="bg-card rounded-2xl border border-border p-6 hover:shadow-lg hover:border-primary/40 cursor-pointer transition-all transform hover:scale-105"
  >
    <div className="flex items-center justify-between mb-4">
      <div className="w-12 h-12 bg-gradient-to-r from-primary to-secondary rounded-xl flex items-center justify-center">
        <Folder className="w-6 h-6 text-primary-foreground" />
      </div>
      <div className="flex items-center space-x-2">
        <button
          onClick={(e) => {
            e.stopPropagation();
            onAddContent(kb.id);
          }}
          className="p-2 hover:bg-muted rounded-lg transition-colors"
        >
          <Plus className="w-5 h-5 text-muted-foreground" />
        </button>
        <button
          onClick={(e) => {
            e.stopPropagation();
            if (confirm("Are you sure you want to delete this knowledge base?")) {
              onDelete(kb.id);
            }
          }}
          className="p-2 hover:bg-destructive/10 rounded-lg transition-colors"
        >
          <Trash2 className="w-5 h-5 text-destructive" />
        </button>
      </div>
    </div>

    <h3 className="text-xl font-bold text-foreground mb-2">{kb.name}</h3>
    <p className="text-muted-foreground text-sm mb-4 line-clamp-2">
      {kb.description}
    </p>

    <div className="space-y-2 text-sm text-muted-foreground">
      <div className="flex items-center justify-between">
        <span className="flex items-center">
          <FileText className="w-4 h-4 mr-2" />
          Documents
        </span>
        <span className="font-semibold">{kb.documents.length}</span> {/* Use kb.documents.length instead of documentsCount */}
      </div>
      <div className="flex items-center justify-between">
        <span className="flex items-center">
          <Globe className="w-4 h-4 mr-2" />
          Scraped Pages
        </span>
        <span className="font-semibold">{kb.scrapedPagesCount}</span>
      </div>
      <div className="flex items-center justify-between">
        <span className="flex items-center">
          <Calendar className="w-4 h-4 mr-2" />
          Last Updated
        </span>
        <span className="font-semibold">{kb.lastUpdated}</span>
      </div>
    </div>

    <div className="mt-4 pt-4 border-t border-border">
      <div className="flex items-center text-primary font-semibold text-sm">
        Open Knowledge Base <ChevronRight className="w-4 h-4 ml-1" />
      </div>
    </div>
  </div>
);

export default KnowledgeBaseCard;