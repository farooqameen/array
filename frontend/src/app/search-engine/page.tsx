"use client";

import React, { useState, useEffect } from "react";
import DocumentLayout from "@/components/layouts/document-layout";
import KnowledgeBaseSelector from "@/components/knowledge-base/knowledge-base-selector";
import DocumentViewer from "@/components/knowledge-base/document-viewer";
import UploadForm from "@/components/upload/uploadForm";
import { ChevronLeft, Upload, Search, Sparkles } from "lucide-react";
import { Button } from "@/components/ui/button";
import WaveLogo from "@/components/ui/array-logo";
import Link from "next/link"; // Import Link for client-side navigation
import { useSearchParams } from "next/navigation";
/**
 * Props for the Card component.
 * @interface CardProps
 * @property {React.ReactNode} icon - The icon to display in the card.
 * @property {string} title - The title of the card.
 * @property {string} description - The description text for the card.
 * @property {() => void} [onClick] - Optional click handler for button-based cards.
 * @property {string} [href] - Optional href for link-based cards (uses next/link).
 */
interface CardProps {
  icon: React.ReactNode;
  title: string;
  description: string;
  onClick?: () => void;
  href?: string;
}

/**
 * DocumentViewerPage component.
 * Manages the different views for document interaction:
 * - Initial selection (General Search, Upload, Smart Search)
 * - Knowledge Base selection
 * - Document Viewer
 * - Document Upload
 * - Smart Search (coming soon placeholder)
 * @returns {React.FC} The DocumentViewerPage component.
 */
const DocumentViewerPage: React.FC = () => {
  // pass parameter through url to indicate originally 
  // where user was directed to exactly to which tool
  const searchParams = useSearchParams();
  useEffect(() => {
  const initialView = searchParams.get("view");

  if (
    initialView === "selector" ||
    initialView === "viewer" ||
    initialView === "upload" ||
    initialView === "smart" ||
    initialView === "general-search"
  ) {
    setViewMode(initialView as typeof viewMode);
  }
}, [searchParams]);
  /**
   * State to control the current view mode of the page.
   * @type {'selector' | 'viewer' | 'upload' | 'smart' | null | 'general-search'}
   */
  const [viewMode, setViewMode] = useState<
    "selector" | "viewer" | "upload" | "smart" | null | "general-search"
  >(null);

  /**
   * State to hold the currently selected knowledge base.
   * @type {any | null}
   */
  const [selectedKnowledgeBase, setSelectedKnowledgeBase] = useState<
    any | null
  >(null);

  /**
   * Effect hook to handle transitions to the document viewer when "general-search" mode is activated.
   * Resets selectedKnowledgeBase to null to ensure a general search.
   */
  useEffect(() => {
    if (viewMode === "general-search") {
      setSelectedKnowledgeBase(null);
      setViewMode("viewer");
    }
  }, [viewMode]);

  /**
   * Handles the selection of a knowledge base.
   * Sets the selected knowledge base and switches the view mode to 'viewer'.
   * @param {any | null} kb - The selected knowledge base object, or null.
   */
  const handleSelectKnowledgeBase = (kb: any | null) => {
    setSelectedKnowledgeBase(kb);
    setViewMode("viewer");
  };

  /**
   * Handles the "Back" action.
   * Resets the selected knowledge base and switches the view mode back to null (initial selection screen).
   */
  const handleBack = () => {
    setSelectedKnowledgeBase(null);
    setViewMode(null);
  };

  /**
   * Reusable Card component for displaying navigation options.
   * It can act as a button or a next/link based on the props provided.
   * @param {CardProps} props - The props for the Card component.
   * @returns {JSX.Element} A card element.
   */
  const Card: React.FC<CardProps> = ({
    icon,
    title,
    description,
    onClick,
    href,
  }) => {
    const content = (
      <>
        <div className="w-16 h-16 bg-gradient-to-r from-secondary to-primary rounded-2xl flex items-center justify-center mb-6">
          {icon}
        </div>
        <h3 className="text-xl font-bold text-foreground mb-4">{title}</h3>
        <p className="text-muted-foreground leading-relaxed mb-4">
          {description}
        </p>
        <div className="flex items-center text-primary font-semibold text-sm">
          Open <ChevronLeft className="w-4 h-4 ml-1 rotate-180" />
        </div>
      </>
    );

    if (href) {
      // If href is provided, render as a Next.js Link component
      return (
        <Link
          href={href}
          className="bg-card border-2 border-border rounded-2xl p-8 text-left hover:shadow-lg hover:border-primary/40 cursor-pointer transition-all transform hover:scale-105 block"
        >
          {content}
        </Link>
      );
    }

    // Otherwise, render as a button
    return (
      <button
        onClick={onClick}
        className="bg-card border-2 border-border rounded-2xl p-8 text-left hover:shadow-lg hover:border-primary/40 cursor-pointer transition-all transform hover:scale-105"
      >
        {content}
      </button>
    );
  };

  return (
    <DocumentLayout>
      <main className="p-6 lg:p-10 flex flex-col items-center min-h-full w-full">
        <div className="w-full max-w-6xl">
          {/* Initial view: Selection cards */}
          {viewMode === null && (
            <>
              <div className="flex justify-center mb-12">
                <WaveLogo width={200} height={200} />
              </div>
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                <Card
                  icon={<Search className="w-8 h-8 text-white" />}
                  title="General Search"
                  description="Search across all documents without selecting a specific knowledge base."
                  onClick={() => setViewMode("general-search")}
                />
                <Card
                  icon={<Upload className="w-8 h-8 text-white" />}
                  title="Upload Documents"
                  description="Add new documents to your knowledge base."
                  onClick={() => setViewMode("upload")}
                />
                <Card
                  icon={<Sparkles className="w-8 h-8 text-white" />}
                  title="Smart Search"
                  description="AI-assisted semantic document search."
                  href="/smart-search" // Link to the dedicated smart-search page
                />
              </div>
            </>
          )}

          {/* Knowledge Base Selector view */}
          {viewMode === "selector" && (
            <>
              <Button
                onClick={handleBack}
                className="mb-4 flex items-center text-sm text-primary hover:underline cursor-pointer"
              >
                <ChevronLeft className="size-5 mr-1" /> Back
              </Button>
              <KnowledgeBaseSelector
                onSelectKnowledgeBase={handleSelectKnowledgeBase}
              />
            </>
          )}

          {/* Document Viewer view (for general search or specific KB) */}
          {viewMode === "viewer" && (
            <>
              <button
                onClick={handleBack}
                className="mb-4 flex items-center text-sm text-primary hover:underline cursor-pointer"
              >
                <ChevronLeft className="w-4 h-4 mr-1" /> Back
              </button>
              <DocumentViewer
                selectedKnowledgeBase={selectedKnowledgeBase}
                onSelectKnowledgeBaseChange={handleBack} // This seems to be a callback to go back
              />
            </>
          )}

          {/* Upload Documents view */}
          {viewMode === "upload" && (
            <>
              <button
                onClick={handleBack}
                className="mb-4 flex items-center text-sm text-primary hover:underline cursor-pointer"
              >
                <ChevronLeft className="w-4 h-4 mr-1" /> Back
              </button>
              <UploadForm />
            </>
          )}
        </div>
      </main>
    </DocumentLayout>
  );
};

export default DocumentViewerPage;
