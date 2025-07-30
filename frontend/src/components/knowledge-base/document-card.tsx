// components/DocumentCard.tsx
import React from "react";
import { Document } from "@/lib/stores/knowledgeStore";
import {
  File,
  Globe,
  Calendar,
  Link2,
  Eye,
  Download,
  MoreVertical,
} from "lucide-react";

interface DocumentCardProps {
  doc: Document;
  onClick: (doc: Document) => void;
}

const DocumentCard: React.FC<DocumentCardProps> = ({ doc, onClick }) => (
  <div
    key={doc.id}
    onClick={() => onClick(doc)}
    className={`bg-card rounded-2xl border border-border p-6 transition-all ${
      doc.status === "processed"
        ? "hover:shadow-lg cursor-pointer hover:border-primary/40 transform hover:scale-[1.02]"
        : "opacity-60 cursor-not-allowed"
    }`}
  >
    <div className="flex items-center justify-between">
      <div className="flex items-center space-x-4">
        <div
          className={`w-12 h-12 rounded-xl flex items-center justify-center ${
            doc.source === "upload"
              ? "bg-gradient-to-r from-primary to-secondary"
              : "bg-gradient-to-r from-secondary to-[var(--chart-5)]"
          }`}
        >
          {doc.source === "upload" ? (
            <File className="w-6 h-6 text-primary-foreground" />
          ) : (
            <Globe className="w-6 h-6 text-primary-foreground" />
          )}
        </div>
        <div>
          <h3 className="font-semibold text-foreground text-lg">{doc.name}</h3>
          <div className="flex items-center space-x-4 text-sm text-muted-foreground mt-1">
            <span className="flex items-center">
              <Calendar className="w-4 h-4 mr-1" />
              {doc.uploadDate}
            </span>
            <span>{doc.size}</span>
            <span>
              {doc.pages} {doc.source === "upload" ? "pages" : "pages scraped"}
            </span>
            {doc.source === "scrape" && doc.url && (
              <span className="flex items-center">
                <Link2 className="w-4 h-4 mr-1" />
                <a
                  href={doc.url}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="hover:underline text-primary"
                >
                  {doc.url.length > 30
                    ? `${doc.url.substring(0, 27)}...`
                    : doc.url}
                </a>
              </span>
            )}
            <span
              className={`px-2 py-1 rounded-full text-xs ${
                doc.status === "processed"
                  ? "bg-green-100 text-green-800"
                  : "bg-yellow-100 text-yellow-800"
              }`}
            >
              {doc.status}
            </span>
          </div>
          {doc.status === "processed" && (
            <div className="text-xs text-primary mt-2 font-medium">
              Click to open in text editor
            </div>
          )}
        </div>
      </div>

      <div className="flex items-center space-x-2">
        <button
          onClick={(e) => {
            e.stopPropagation();
            // Handle view action
          }}
          className="p-2 hover:bg-muted rounded-lg transition-colors"
        >
          <Eye className="w-5 h-5 text-muted-foreground" />
        </button>
        <button
          onClick={(e) => {
            e.stopPropagation();
            // Handle download action
          }}
          className="p-2 hover:bg-muted rounded-lg transition-colors"
        >
          <Download className="w-5 h-5 text-muted-foreground" />
        </button>
        <button
          onClick={(e) => {
            e.stopPropagation();
            // Handle more options
          }}
          className="p-2 hover:bg-muted rounded-lg transition-colors"
        >
          <MoreVertical className="w-5 h-5 text-muted-foreground" />
        </button>
      </div>
    </div>
  </div>
);

export default DocumentCard;
