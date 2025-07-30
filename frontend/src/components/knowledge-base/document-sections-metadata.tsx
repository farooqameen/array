import React from "react";
import {
  Info,
  Database,
  ExternalLink,
  FileBadge2,
  Clock,
  Gavel,
  Calendar,
  User,
  FolderTree,
  FileText,
  ShieldCheck,
} from "lucide-react";

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

interface SectionMetadataProps {
  /** The section node whose custom fields are to be displayed. */
  section: SectionNode;
}

/**
 * Displays the custom metadata fields for a given document section.
 * @param {object} props - The component props.
 * @param {SectionNode} props.section - The section data object.
 */
const SectionMetadata: React.FC<SectionMetadataProps> = ({ section }) => {
  /**
   * Helper function to render a custom field with an appropriate icon and formatted label.
   * @param {string} key - The key of the custom field.
   * @param {string} value - The value of the custom field.
   * @returns {JSX.Element} A div element displaying the custom field.
   */
  const renderCustomField = (key: string, value: string) => {
    let IconComponent: React.ElementType = Info; // Default icon

    // Map specific keys to Lucide icons
    switch (key.toLowerCase()) {
      case "importance":
        IconComponent = FileBadge2;
        break;
      case "lastupdated":
        IconComponent = Clock;
        break;
      case "sourcereference":
        IconComponent = ExternalLink;
        break;
      case "legalbasis":
        IconComponent = Gavel;
        break;
      case "constitutionalbasis":
        IconComponent = Gavel;
        break;
      case "scope":
        IconComponent = FolderTree;
        break;
      case "act":
        IconComponent = FileText;
        break;
      case "enforcement":
        IconComponent = ShieldCheck;
        break;
      case "penaltylevel":
        IconComponent = Gavel;
        break;
      case "reviewfrequency":
        IconComponent = Calendar;
        break;
      case "regulator":
        IconComponent = User;
        break;
      case "inspectioncycle":
        IconComponent = Calendar;
        break;
      case "jurisdiction":
        IconComponent = Gavel;
        break;
      case "effectivedate":
        IconComponent = Clock;
        break;
      case "reviewcycle":
        IconComponent = Calendar;
        break;
      case "confidentiality":
        IconComponent = ShieldCheck;
        break;
      default:
        IconComponent = Info;
        break;
    }

    const label = key
      .replace(/([A-Z])/g, " $1")
      .replace(/^./, (str) => str.toUpperCase()); // Convert camelCase to Title Case

    return (
      <div key={key} className="flex items-center text-muted-foreground">
        {IconComponent && <IconComponent className="w-4 h-4 mr-2" />}
        <span className="font-medium">{label}:</span>
        {/* Render as a clickable link if it's a URL */}
        {key.toLowerCase() === "sourcereference" && value.startsWith("http") ? (
          <a
            href={value}
            target="_blank"
            rel="noopener noreferrer"
            className="ml-1 text-primary hover:underline truncate"
          >
            {value}
          </a>
        ) : (
          <span className="ml-1 text-foreground">{value}</span>
        )}
      </div>
    );
  };

  if (Object.keys(section.customFields).length === 0) {
    return null; // Don't render if no custom fields
  }

  return (
    <div className="mt-8 pt-6 border-t border-border">
      <h4 className="text-xl font-semibold text-foreground mb-4 flex items-center">
        <Database className="w-6 h-6 mr-2 text-muted-foreground" />
        Section Title:{" "}
        <span className="ml-2 text-primary">{section.title}</span>
      </h4>
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-y-3 gap-x-4 text-base">
        {Object.entries(section.customFields).map(([key, value]) =>
          renderCustomField(key, value)
        )}
      </div>
    </div>
  );
};

export default SectionMetadata;
