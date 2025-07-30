// components/DocumentList.tsx
import React from "react";
import { Document } from "@/lib/stores/knowledgeStore";
import DocumentCard from "./document-card";
import EmptyState from "./empty-state";
import { Database } from "lucide-react";

interface DocumentListProps {
  documents: Document[];
  onDocumentClick: (doc: Document) => void;
  onAddFirstContent: () => void;
}

const DocumentList: React.FC<DocumentListProps> = ({
  documents,
  onDocumentClick,
  onAddFirstContent,
}) => (
  <section className="max-w-7xl mx-auto">
    <div className="grid gap-4">
      {documents.length === 0 ? (
        <EmptyState
          icon={Database}
          title="No content yet"
          description="Add documents or scrape web content to get started"
          buttonText="Add Your First Content"
          onButtonClick={onAddFirstContent}
        />
      ) : (
        documents.map((doc) => (
          <DocumentCard key={doc.id} doc={doc} onClick={onDocumentClick} />
        ))
      )}
    </div>
  </section>
);

export default DocumentList;
