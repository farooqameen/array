// src/components/document/document-info-card.tsx
import React from "react";
import {
  FileText,
  User,
  Calendar,
  Tag,
  ExternalLink,
  Info,
  Gavel,
  Clock,
  ShieldCheck,
  X,
  Database,
} from "lucide-react";

/**
 * @typedef {object} CustomFields
 * @property {string} [key: string] - Dynamic custom field keys and their string values.
 */
interface CustomFields {
  [key: string]: string;
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

interface DocumentInfoCardProps {
  /** The document data to display. */
  document: DocumentData;
  /** Callback function to close the info card. */
  onClose: () => void;
}

/**
 * Displays comprehensive information about a document, including standard metadata and custom fields.
 * @param {object} props - The component props.
 * @param {DocumentData} props.document - The document data object.
 * @param {() => void} props.onClose - Function to call when the close button is clicked.
 */
const DocumentInfoCard: React.FC<DocumentInfoCardProps> = ({
  document,
  onClose,
}) => {
  /**
   * Helper function to render a custom field with an appropriate icon and formatted label.
   * @param {string} key - The key of the custom field.
   * @param {string} value - The value of the custom field.
   * @returns {JSX.Element} A div element displaying the custom field.
   */
  const renderCustomField = (key: string, value: string) => {
    let IconComponent: React.ElementType = Info; // Default icon

    // Assign specific icons based on the custom field key
    switch (key.toLowerCase()) {
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
      // Add more cases for other custom fields as needed
    }

    const label = key
      .replace(/([A-Z])/g, " $1")
      .replace(/^./, (str) => str.toUpperCase()); // Convert camelCase to Title Case

    return (
      <div
        key={key}
        className="flex items-center text-muted-foreground text-sm"
      >
        {IconComponent && <IconComponent className="w-4 h-4 mr-2" />}
        <span className="font-medium">{label}:</span>
        <span className="ml-1 text-foreground">{value}</span>
      </div>
    );
  };

  return (
    <div className="w-full bg-card border-b border-border p-6 shadow-sm">
      <div className="flex items-start justify-between mb-4">
        <div className="flex-1">
          <div className="flex items-center mb-2">
            <FileText className="w-6 h-6 text-primary mr-3" />
            <h1 className="text-2xl font-bold text-foreground">
              {document.title}
            </h1>
          </div>
          <p className="text-muted-foreground mb-4 text-sm md:text-base">
            {document.description}
          </p>

          {/* Standard Document Info */}
          <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 xl:grid-cols-5 gap-y-3 gap-x-4 text-sm">
            <div className="flex items-center text-muted-foreground">
              <User className="w-4 h-4 mr-2" />
              <span className="font-medium">Author:</span>
              <span className="ml-1 text-foreground">{document.author}</span>
            </div>
            <div className="flex items-center text-muted-foreground">
              <Calendar className="w-4 h-4 mr-2" />
              <span className="font-medium">Modified:</span>
              <span className="ml-1 text-foreground">
                {document.dateModified}
              </span>
            </div>
            <div className="flex items-center text-muted-foreground">
              <Tag className="w-4 h-4 mr-2" />
              <span className="font-medium">Version:</span>
              <span className="ml-1 text-foreground">{document.version}</span>
            </div>
            {document.sourceUrl && (
              <div className="flex items-center">
                <ExternalLink className="w-4 h-4 mr-2 text-primary" />
                <a
                  href={document.sourceUrl}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="text-primary hover:underline font-medium truncate"
                >
                  View Source
                </a>
              </div>
            )}
            <div className="flex flex-wrap gap-1 col-span-full xl:col-span-1">
              {document.categories.slice(0, 3).map((cat, i) => (
                <span
                  key={i}
                  className="text-xs px-2 py-1 bg-primary/10 text-primary rounded-full"
                >
                  {cat}
                </span>
              ))}
              {document.categories.length > 3 && (
                <span className="text-xs px-2 py-1 bg-muted text-muted-foreground rounded-full">
                  +{document.categories.length - 3} more
                </span>
              )}
            </div>
          </div>

          {/* Custom Fields Section */}
          {Object.keys(document.customFields).length > 0 && (
            <div className="mt-6 pt-4 border-t border-border">
              <h4 className="text-md font-semibold text-foreground mb-3 flex items-center">
                <Database className="w-5 h-5 mr-2 text-muted-foreground" />
                Additional Information
              </h4>
              <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-y-3 gap-x-4 text-sm">
                {Object.entries(document.customFields).map(([key, value]) =>
                  renderCustomField(key, value)
                )}
              </div>
            </div>
          )}
        </div>
        <button
          onClick={onClose}
          className="p-2 text-muted-foreground hover:text-foreground hover:bg-muted rounded-lg transition-colors flex-shrink-0 ml-4"
          title="Hide Document Information"
          aria-label="Close document information card"
        >
          <X className="w-5 h-5" />
        </button>
      </div>
    </div>
  );
};

export default DocumentInfoCard;
