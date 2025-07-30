// src/components/document/document-sections-nav.tsx
import React from "react";
import { ChevronDown, ChevronRight } from "lucide-react";

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

interface SectionTreeItemProps {
  /** The section node to render. */
  section: SectionNode;
  /** The current depth of the section in the tree (for indentation). */
  depth: number;
  /** Set of IDs of currently expanded sections. */
  expandedSections: Set<string>;
  /** Callback to toggle the expansion state of a section. */
  toggleSectionExpansion: (id: string) => void;
  /** Callback to select a section and scroll to it. */
  onSelectSection: (id: string) => void;
  /** The ID of the currently selected section. */
  selectedSectionId: string | null;
  /** Text to highlight in section titles. */
  highlightedText: string;
}

/**
 * Renders a single expandable item in the document section navigation tree.
 * @param {object} props - The component props.
 * @param {SectionNode} props.section - The section data.
 * @param {number} props.depth - The nesting level of the section.
 * @param {Set<string>} props.expandedSections - Set of currently expanded section IDs.
 * @param {(id: string) => void} props.toggleSectionExpansion - Function to toggle section expansion.
 * @param {(id: string) => void} props.onSelectSection - Function to select a section.
 * @param {string | null} props.selectedSectionId - ID of the currently selected section.
 * @param {string} props.highlightedText - Text to highlight in the section title.
 */
const SectionTreeItem: React.FC<SectionTreeItemProps> = React.memo(
  ({
    section,
    depth,
    expandedSections,
    toggleSectionExpansion,
    onSelectSection,
    selectedSectionId,
    highlightedText,
  }) => {
    const isExpanded = expandedSections.has(section.id);
    const hasChildren = section.children && section.children.length > 0;
    const isSelected = selectedSectionId === section.id;

    /**
     * Renders the section title with optional highlighting.
     * @param {string} title - The original title string.
     * @param {string} highlight - The substring to highlight.
     * @returns {React.ReactNode} The rendered title with highlighting.
     */
    const renderTitle = (title: string, highlight: string) => {
      if (!highlight) return title;
      const parts = title.split(new RegExp(`(${highlight})`, "gi"));
      return (
        <span>
          {parts.map((part, i) =>
            part.toLowerCase() === highlight.toLowerCase() ? (
              <span
                key={i}
                className="bg-yellow-200 font-semibold rounded px-0.5"
              >
                {part}
              </span>
            ) : (
              part
            )
          )}
        </span>
      );
    };

    return (
      <div className={`mt-1`}>
        <div
          className={`flex items-center text-sm font-medium cursor-pointer rounded-md py-2 px-3 transition-colors duration-200
          ${
            isSelected
              ? "bg-primary/10 text-primary border-l-2 border-primary"
              : "text-foreground hover:bg-muted"
          }
          ${depth > 0 ? `ml-${depth * 4}` : ""}
        `}
          onClick={() => onSelectSection(section.id)}
          role="button"
          aria-label={`Select section ${section.title}`}
        >
          {hasChildren && (
            <button
              onClick={(e) => {
                e.stopPropagation(); // Prevent selecting the section when toggling expansion
                toggleSectionExpansion(section.id);
              }}
              className="p-1 -ml-1 text-muted-foreground hover:bg-accent rounded-md transition-colors"
              aria-expanded={isExpanded}
              aria-controls={`section-children-${section.id}`}
              aria-label={isExpanded ? "Collapse section" : "Expand section"}
            >
              {isExpanded ? (
                <ChevronDown className="w-4 h-4" />
              ) : (
                <ChevronRight className="w-4 h-4" />
              )}
            </button>
          )}
          <span
            className={`${
              hasChildren ? "ml-1" : depth > 0 ? "ml-5" : "ml-0"
            } flex-1 truncate`}
          >
            {renderTitle(section.title, highlightedText)}
          </span>
        </div>

        {isExpanded && hasChildren && (
          <div id={`section-children-${section.id}`} role="group">
            {section.children.map((child) => (
              <SectionTreeItem
                key={child.id}
                section={child}
                depth={depth + 1}
                expandedSections={expandedSections}
                toggleSectionExpansion={toggleSectionExpansion}
                onSelectSection={onSelectSection}
                selectedSectionId={selectedSectionId}
                highlightedText={highlightedText}
              />
            ))}
          </div>
        )}
      </div>
    );
  }
);

SectionTreeItem.displayName = "SectionTreeItem";

interface DocumentSectionsNavProps {
  /** The array of top-level section nodes to display. */
  sections: SectionNode[];
  /** Set of IDs of currently expanded sections. */
  expandedSections: Set<string>;
  /** Callback to toggle the expansion state of a section. */
  toggleSectionExpansion: (id: string) => void;
  /** Callback to select a section and scroll to its content. */
  onSelectSection: (id: string) => void;
  /** The ID of the currently selected section. */
  selectedSectionId: string | null;
  /** Text to highlight in section titles during search. */
  highlightedText: string;
}

/**
 * Renders the hierarchical navigation for document sections (Table of Contents).
 * @param {object} props - The component props.
 * @param {SectionNode[]} props.sections - The array of section nodes.
 * @param {Set<string>} props.expandedSections - Set of expanded section IDs.
 * @param {(id: string) => void} props.toggleSectionExpansion - Function to toggle section expansion.
 * @param {(id: string) => void} props.onSelectSection - Function to select a section.
 * @param {string | null} props.selectedSectionId - ID of the selected section.
 * @param {string} props.highlightedText - Text for highlighting in section titles.
 */
const DocumentSectionsNav: React.FC<DocumentSectionsNavProps> = ({
  sections,
  expandedSections,
  toggleSectionExpansion,
  onSelectSection,
  selectedSectionId,
  highlightedText,
}) => {
  return (
    <nav className="space-y-1" aria-label="Document Sections">
      {sections.map((section) => (
        <SectionTreeItem
          key={section.id}
          section={section}
          depth={0}
          expandedSections={expandedSections}
          toggleSectionExpansion={toggleSectionExpansion}
          onSelectSection={onSelectSection}
          selectedSectionId={selectedSectionId}
          highlightedText={highlightedText}
        />
      ))}
    </nav>
  );
};

export default DocumentSectionsNav;
