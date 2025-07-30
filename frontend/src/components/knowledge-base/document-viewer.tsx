"use client";

import React, {
  useState,
  useEffect,
  useRef,
  useCallback,
  useMemo,
} from "react";
import {
  Search,
  Info,
  Database,
  FolderTree,
} from "lucide-react";
import { MOCK_DOCUMENT_JSON } from "@/components/data/constants";
import DocumentSectionsNav from "./documents-sections-nav";
import DocumentInfoCard from "./document-info-card";
import SectionMetadata from "./document-sections-metadata";
import DocumentContentDisplay from "./document-content-display";

/**
 * @typedef {object} CustomFields
 * @property {string} [key: string] - Dynamic custom field keys and their string values.
 */
interface CustomFields {
  [key: string]: string;
}

/**
 * @typedef {object} SectionNode
 * @property {string} id - Unique identifier for the section.
 * @property {string} title - Title of the section.
 * @property {string[]} categories - Array of categories associated with the section.
 * @property {number} startPosition - Starting character index of the section content in the full document.
 * @property {number} endPosition - Ending character index of the section content in the full document.
 * @property {CustomFields} customFields - Custom metadata fields for the section.
 * @property {SectionNode[]} children - Nested child sections.
 * @property {string} [highlightedContent] - Content highlighted for search (optional).
 */
interface SectionNode {
  id: string;
  title: string;
  categories: string[];
  startPosition: number;
  endPosition: number;
  customFields: CustomFields;
  children: SectionNode[];
  highlightedContent?: string;
}

/**
 * @typedef {object} DocumentData
 * @property {string} id - Unique identifier for the document.
 * @property {string} title - Title of the document.
 * @property {string} description - Description of the document.
 * @property {string[]} categories - Categories associated with the document.
 * @property {string} sourceUrl - URL to the original source of the document.
 * @property {string} dateCreated - Creation date of the document (ISO format).
 * @property {string} dateModified - Last modification date of the document (ISO format).
 * @property {string} author - Author of the document.
 * @property {string} version - Version of the document.
 * @property {string[]} tags - Tags associated with the document.
 * @property {CustomFields} customFields - Custom metadata fields for the document.
 */
interface DocumentData {
  id: string;
  title: string;
  description: string;
  categories: string[];
  sourceUrl: string;
  dateCreated: string;
  dateModified: string;
  author: string;
  version: string;
  tags: string[];
  customFields: CustomFields;
}

/**
 * @typedef {object} FullDocumentExport
 * @property {DocumentData} document - Main document metadata.
 * @property {string} content - Full text content of the document.
 * @property {SectionNode[]} sections - Hierarchical structure of document sections.
 * @property {object} [metadata] - Additional export metadata.
 * @property {string} [metadata.exportDate] - Date of export.
 * @property {string} [metadata.version] - Version of the export schema.
 * @property {number} [metadata.totalSections] - Total number of sections.
 */
interface FullDocumentExport {
  document: DocumentData;
  content: string;
  sections: SectionNode[];
  metadata?: {
    exportDate: string;
    version: string;
    totalSections: number;
  };
}

interface DocumentViewerProps {
  /** The currently selected knowledge base object, or `null` for general search. */
  selectedKnowledgeBase: any | null;
  /** Callback to change the knowledge base selection (back to selector screen). */
  onSelectKnowledgeBaseChange: () => void;
}

/**
 * Main component for viewing a single document, including its table of contents,
 * searchable content, and detailed information.
 * @param {object} props - The component props.
 * @param {object | null} props.selectedKnowledgeBase - The currently selected knowledge base.
 * @param {function} props.onSelectKnowledgeBaseChange - Callback to trigger changing the knowledge base.
 */
const DocumentViewer: React.FC<DocumentViewerProps> = ({
  selectedKnowledgeBase,
  onSelectKnowledgeBaseChange,
}) => {
  const [documentData] = useState<FullDocumentExport>(MOCK_DOCUMENT_JSON);
  const [expandedSections, setExpandedSections] = useState<Set<string>>(
    new Set()
  );
  const [selectedSectionId, setSelectedSectionId] = useState<string | null>(
    null
  );
  const [searchQuery, setSearchQuery] = useState(""); // State for content search
  const [sectionSearchQuery, setSectionSearchQuery] = useState(""); // State for section search
  const [showDocumentInfo, setShowDocumentInfo] = useState(true); // State for DocumentInfoCard
  const contentRef = useRef<HTMLDivElement>(null);

  /**
   * Effect to expand all sections by default on initial load.
   */
  useEffect(() => {
    const allSectionIds = new Set<string>();
    const collectIds = (nodes: SectionNode[]) => {
      nodes.forEach((node) => {
        allSectionIds.add(node.id);
        if (node.children) collectIds(node.children);
      });
    };
    collectIds(documentData.sections);
    setExpandedSections(allSectionIds);
  }, [documentData.sections]);

  /**
   * Helper function to find a section by ID in the nested structure.
   * @param {SectionNode[]} sections - Array of section nodes to search.
   * @param {string} id - The ID of the section to find.
   * @returns {SectionNode | null} The found section node or null if not found.
   */
  const findSectionById = useCallback(
    (sections: SectionNode[], id: string): SectionNode | null => {
      for (const section of sections) {
        if (section.id === id) return section;
        if (section.children && section.children.length > 0) {
          const found = findSectionById(section.children, id);
          if (found) return found;
        }
      }
      return null;
    },
    []
  );

  /**
   * Handles selection of a section from the navigation, scrolling the content into view.
   * @param {string} id - The ID of the selected section.
   */
  const handleSelectSection = useCallback(
    (id: string) => {
      setSelectedSectionId(id);
      const section = findSectionById(documentData.sections, id);
      if (contentRef.current && section) {
        // Find the line number based on startPosition
        const textBeforeSection = documentData.content.substring(
          0,
          section.startPosition
        );
        const lineNumber = textBeforeSection.split("\n").length - 1; // Subtract 1 as split gives one more element than lines

        // Estimate scroll position based on line height (adjust as needed for your font styles)
        const lineHeight = 24;
        const estimatedScrollTop = lineNumber * lineHeight;

        contentRef.current.scrollTo({
          top: estimatedScrollTop - 50, // Add some padding from the top
          behavior: "smooth",
        });
      }
    },
    [documentData.sections, documentData.content, findSectionById]
  );

  /**
   * Toggles the expanded state of a section in the navigation tree.
   * @param {string} id - The ID of the section to toggle.
   */
  const toggleSectionExpansion = useCallback((id: string) => {
    setExpandedSections((prev) => {
      const newSet = new Set(prev);
      if (newSet.has(id)) {
        newSet.delete(id);
      } else {
        newSet.add(id);
      }
      return newSet;
    });
  }, []);

  /**
   * Filters sections based on the section search query.
   * Memoized for performance.
   * @type {SectionNode[]}
   */
  const filteredSections = useMemo(() => {
    if (!sectionSearchQuery) return documentData.sections;

    const query = sectionSearchQuery.toLowerCase();
    const filter = (nodes: SectionNode[]): SectionNode[] => {
      const result: SectionNode[] = [];
      nodes.forEach((node) => {
        const matches =
          node.title.toLowerCase().includes(query) ||
          node.categories.some((cat) => cat.toLowerCase().includes(query));

        const filteredChildren = filter(node.children || []);

        if (matches || filteredChildren.length > 0) {
          result.push({ ...node, children: filteredChildren });
          // Ensure parent is expanded if children are shown due to search
          // Note: This side effect inside memo can be problematic if it causes re-renders.
          // Consider handling expansion logic outside, or ensure this only expands and never collapses.
          setExpandedSections((prev) => new Set(prev).add(node.id));
        }
      });
      return result;
    };
    return filter(documentData.sections);
  }, [documentData.sections, sectionSearchQuery]);

  const selectedSection = selectedSectionId
    ? findSectionById(documentData.sections, selectedSectionId)
    : null;

  return (
    <div className="flex flex-1 overflow-hidden">
      {/* Document Sections Navigation Sidebar */}
      <aside className="w-80 bg-card border-r border-border p-6 flex-shrink-0 overflow-y-auto">
        {/* Top bar showing selected knowledge base */}
        <div className="flex items-center justify-between mb-6 p-3 bg-muted rounded-xl">
          <div className="flex items-center space-x-2">
            <div className="w-6 h-6 bg-gradient-to-r from-primary to-purple-400 rounded-md flex items-center justify-center">
              <Database className="w-3 h-3 text-primary-foreground" />
            </div>
            <div>
              <span className="text-xs text-muted-foreground">
                Selected KB:
              </span>
              <span className="ml-1 font-semibold text-foreground truncate">
                {selectedKnowledgeBase
                  ? selectedKnowledgeBase.name
                  : "General Search"}
              </span>
            </div>
          </div>
          <button
            onClick={onSelectKnowledgeBaseChange}
            className="px-2 py-1 text-primary hover:bg-card rounded-md transition-colors font-medium text-xs"
            aria-label="Change knowledge base"
          >
            Change
          </button>
        </div>

        {/* Search for sections input */}
        <div className="relative mb-4">
          <Search className="absolute left-3 top-2.5 w-4 h-4 text-muted-foreground" />
          <input
            type="text"
            placeholder="Search sections..."
            value={sectionSearchQuery}
            onChange={(e) => setSectionSearchQuery(e.target.value)}
            className="w-full pl-10 pr-4 py-2 text-sm border border-border rounded-lg bg-background text-foreground focus:outline-none focus:ring-2 focus:ring-primary focus:border-transparent"
          />
        </div>
        <h3 className="text-sm font-semibold text-muted-foreground uppercase tracking-wider mb-4 flex items-center">
          <FolderTree className="w-4 h-4 mr-2" /> Document Sections
        </h3>

        {/* Document Sections Navigation Tree */}
        <DocumentSectionsNav
          sections={filteredSections}
          expandedSections={expandedSections}
          toggleSectionExpansion={toggleSectionExpansion}
          onSelectSection={handleSelectSection}
          selectedSectionId={selectedSectionId}
          highlightedText={sectionSearchQuery}
        />
      </aside>

      <main className="flex-1 flex flex-col bg-background overflow-y-auto">
        {/* Document Info Card */}
        {showDocumentInfo && (
          <DocumentInfoCard
            document={documentData.document}
            onClose={() => setShowDocumentInfo(false)}
          />
        )}
        <div className="p-6 border-b border-border sticky top-0 bg-card z-10">
          <div className="flex items-center justify-between">
            {/* Content search input */}
            <div className="relative flex-1 mr-4">
              <Search className="absolute left-3 top-3 w-5 h-5 text-muted-foreground" />
              <input
                type="text"
                placeholder="Search document content..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="w-full pl-12 pr-4 py-3 border border-border rounded-xl bg-background text-foreground focus:outline-none focus:ring-2 focus:ring-primary focus:border-transparent"
              />
            </div>
            <button
              onClick={() => setShowDocumentInfo(!showDocumentInfo)}
              className="px-4 py-2 text-sm font-medium text-foreground bg-muted rounded-lg hover:bg-accent transition-colors flex items-center"
              aria-label={
                showDocumentInfo ? "Hide Document Info" : "Show Document Info"
              }
            >
              <Info className="w-4 h-4 mr-2" />
              {showDocumentInfo ? "Hide Doc Info" : "Show Doc Info"}
            </button>
          </div>
        </div>
        <div
          ref={contentRef}
          className="flex-1 p-8 bg-background-light overflow-y-auto"
        >
          <div className="max-w-4xl mx-auto bg-card rounded-lg shadow-sm p-8">
            <div className="prose prose-gray max-w-none text-foreground leading-relaxed">
              {/* Render content with highlights */}
              <DocumentContentDisplay
                content={documentData.content}
                searchQuery={searchQuery}
                selectedSection={selectedSection}
              />
            </div>

            {/* Display custom fields for selected section */}
            {selectedSection &&
              Object.keys(selectedSection.customFields).length > 0 && (
                <SectionMetadata section={selectedSection} />
              )}
          </div>
        </div>
      </main>
    </div>
  );
};

export default DocumentViewer;
