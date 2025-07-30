import React from "react";
import { KnowledgeBase } from "@/lib/stores/knowledgeStore";
import { ChevronLeft, Plus, Search } from "lucide-react";

interface FolderViewHeaderProps {
  selectedKnowledgeBase: KnowledgeBase | undefined;
  onBack: () => void;
  onAddContent: () => void;
}

const FolderViewHeader: React.FC<FolderViewHeaderProps> = ({
  selectedKnowledgeBase,
  onBack,
  onAddContent,
}) => (
  <section className="mb-8">
    <div className="flex items-center space-x-4 mb-6">
      <button
        onClick={onBack}
        className="p-2 hover:bg-muted rounded-lg transition-colors"
      >
        <ChevronLeft className="w-5 h-5 text-foreground" />
      </button>
      <div>
        <h1 className="text-2xl font-bold text-foreground">
          {selectedKnowledgeBase?.name}
        </h1>
        <p className="text-muted-foreground">
          {selectedKnowledgeBase?.description}
        </p>
      </div>
    </div>

    <div className="flex flex-col sm:flex-row gap-4">
      <button
        onClick={onAddContent}
        className="bg-gradient-to-r ml-8 from-primary to-secondary text-primary-foreground px-6 py-3 rounded-xl font-semibold flex items-center justify-center space-x-2 hover:shadow-lg transition-all"
      >
        <Plus className="w-5 h-5" />
        <span>Add Content</span>
      </button>

      <div className="relative flex-1">
        <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-5 h-5 text-muted-foreground" />
        <input
          type="text"
          placeholder="Search in this knowledge base..."
          className="w-full pl-12 pr-4 py-3 border border-input rounded-xl focus:ring-2 focus:ring-primary focus:border-transparent bg-background text-foreground"
        />
      </div>
    </div>
  </section>
);

export default FolderViewHeader;
