// src/components/document/document-content-display.tsx
import React, { useMemo } from "react";

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

interface DocumentContentDisplayProps {
  /** The full content string of the document. */
  content: string;
  /** The current search query to highlight in the content. */
  searchQuery: string;
  /** The currently selected section object, if any. Content will be truncated to this section if provided. */
  selectedSection: SectionNode | null;
}

/**
 * Displays the main document content, optionally truncated to a selected section,
 * with search query highlighting.
 * @param {object} props - The component props.
 * @param {string} props.content - The full document content.
 * @param {string} props.searchQuery - The text to highlight within the content.
 * @param {SectionNode | null} props.selectedSection - The section to display, or null for full document.
 */
const DocumentContentDisplay: React.FC<DocumentContentDisplayProps> = ({
  content,
  searchQuery,
  selectedSection,
}) => {
  /**
   * Memoized function to render the document content with highlighting.
   * If a section is selected, only that section's content is displayed.
   * Search query highlighting is applied if a query is present.
   */
  const renderContentWithHighlights = useMemo(() => {
    let contentToDisplay = content;

    // If a section is selected, narrow the content to only that section
    if (selectedSection) {
      contentToDisplay = content.substring(
        selectedSection.startPosition,
        selectedSection.endPosition
      );
    }

    if (!searchQuery) {
      return (
        <pre className="whitespace-pre-wrap font-sans text-foreground">
          {contentToDisplay}
        </pre>
      );
    }

    const parts: React.ReactNode[] = [];
    let lastIndex = 0;
    const lowerCaseContent = contentToDisplay.toLowerCase();
    const lowerCaseQuery = searchQuery.toLowerCase();

    // Use a global regex to find all matches
    const regex = new RegExp(lowerCaseQuery, "gi");
    let match;

    while ((match = regex.exec(lowerCaseContent)) !== null) {
      // Add text before the current match
      if (match.index > lastIndex) {
        parts.push(contentToDisplay.substring(lastIndex, match.index));
      }
      // Add the highlighted match
      parts.push(
        <mark
          key={match.index}
          className="bg-yellow-200 rounded px-0.5 text-foreground"
        >
          {contentToDisplay.substring(match.index, regex.lastIndex)}
        </mark>
      );
      lastIndex = regex.lastIndex;
    }

    // Add any remaining text after the last match
    if (lastIndex < contentToDisplay.length) {
      parts.push(contentToDisplay.substring(lastIndex));
    }

    return (
      <pre className="whitespace-pre-wrap font-sans text-foreground">
        {parts}
      </pre>
    );
  }, [content, selectedSection, searchQuery]);

  return (
    <div className="prose prose-gray max-w-none text-foreground leading-relaxed">
      {renderContentWithHighlights}
    </div>
  );
};

export default DocumentContentDisplay;
