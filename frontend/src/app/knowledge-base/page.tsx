// page.tsx
"use client";
import React, { useState, useEffect } from "react";
import { ArrowLeft } from "lucide-react";

// Components
import Sidebar from "@/components/sidebar";
import KnowledgeBaseList from "@/components/knowledge-base/knowledge-base-list";
import DocumentList from "@/components/knowledge-base/document-list";
import KnowledgeBaseHeader from "@/components/knowledge-base/knowledge-base-header";

// Modals
import CreateFolderModal from "@/components/create-folder-modal";
import AddContentModal from "@/components/add-content-modal";
import UploadModal from "@/components/upload/UploadModal";
import ScraperModal from "@/components/ScraperModal";

import {
  useKnowledgeStore,
  type Document,
  type KnowledgeBase,
} from "@/lib/stores/knowledgeStore";
import DocumentEditor from "@/components/texteditor";
import FloatingElementsBackground from "@/components/flowting-elements-background";
import StatsGrid from "@/components/knowledge-base/stats-grid";
import MobileHeader from "@/components/knowledge-base/mobile-header";
import FolderViewHeader from "@/components/knowledge-base/folder-view-header";

const KnowledgeBasePage = () => {
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const [activeSection, setActiveSection] = useState("database");
  const [isVisible, setIsVisible] = useState<Record<string, boolean>>({});
  const [isCollapsed, setIsCollapsed] = useState(false);
  const [selectedFolder, setSelectedFolder] = useState<number | null>(null);
  const [selectedDocument, setSelectedDocument] = useState<Document | null>(
    null
  );
  const [showCreateFolderModal, setShowCreateFolderModal] = useState(false);
  const [showAddContentModal, setShowAddContentModal] = useState(false);
  const [showUploadModal, setShowUploadModal] = useState(false);
  const [showScraperModal, setShowScraperModal] = useState(false);
  const [searchQuery, setSearchQuery] = useState("");
  const [uploadingFiles, setUploadingFiles] = useState<File[]>([]);
  const [uploadProgress, setUploadProgress] = useState<Record<string, number>>(
    {}
  );
  const [newKnowledgeBase, setNewKnowledgeBase] = useState<{
    name: string;
    description: string;
    category: string;
  }>({
    name: "",
    description: "",
    category: "",
  });

  // Zustand store
  const {
    knowledgeBases,
    addKnowledgeBase,
    addDocumentToKnowledgeBase,
    removeKnowledgeBase,
    getTotalDocuments,
    getTotalScrapedPages,
  } = useKnowledgeStore();

  useEffect(() => {
    const observer = new IntersectionObserver(
      (entries) => {
        entries.forEach((entry) => {
          setIsVisible((prev) => ({
            ...prev,
            [entry.target.id]: entry.isIntersecting,
          }));
        });
      },
      { threshold: 0.1 }
    );

    document.querySelectorAll("[id]").forEach((el) => {
      observer.observe(el);
    });

    return () => observer.disconnect();
  }, []);

  const handleFileUpload = async (files: File[], knowledgeBaseId: number) => {
    setUploadingFiles(files);

    for (const file of files) {
      const formData = new FormData();
      formData.append("file", file);
      formData.append("knowledgeBaseId", knowledgeBaseId.toString());

      try {
        setUploadProgress((prev) => ({ ...prev, [file.name]: 0 }));

        const response = await fetch("http://localhost:8000/upload", {
          method: "POST",
          body: formData,
        });

        if (response.ok) {
          const result = await response.json();

          const newDocument: Document = {
            id: Date.now() + Math.random(),
            name: result.filename,
            type: file.type,
            size: `${(file.size / 1024 / 1024).toFixed(2)} MB`,
            uploadDate: new Date().toISOString().split("T")[0],
            status: "processed",
            pages: result.pages || 1,
            source: "upload",
          };

          addDocumentToKnowledgeBase(knowledgeBaseId, newDocument);
          setUploadProgress((prev) => ({ ...prev, [file.name]: 100 }));
        } else {
          console.error("Upload failed:", response.statusText);
          setUploadProgress((prev) => ({ ...prev, [file.name]: -1 }));
        }
      } catch (error) {
        console.error("Upload error:", error);
        setUploadProgress((prev) => ({ ...prev, [file.name]: -1 }));
      }
    }

    setTimeout(() => {
      setUploadingFiles([]);
      setUploadProgress({});
      setShowUploadModal(false);
    }, 2000);
  };

  const handleCreateKnowledgeBase = () => {
    if (newKnowledgeBase.name.trim()) {
      const newKB: KnowledgeBase = {
        id: Date.now(),
        name: newKnowledgeBase.name,
        description: newKnowledgeBase.description,
        category: newKnowledgeBase.category,
        documentsCount: 0,
        scrapedPagesCount: 0,
        createdDate: new Date().toISOString().split("T")[0],
        lastUpdated: new Date().toISOString().split("T")[0],
        documents: [], // Initialize documents array
      };

      addKnowledgeBase(newKB);
      setNewKnowledgeBase({ name: "", description: "", category: "" });
      setShowCreateFolderModal(false);
    }
  };

  const handleDocumentClick = (doc: Document) => {
    if (doc.status === "processed") {
      setSelectedDocument(doc);
    }
  };

  const handleBackFromEditor = () => {
    setSelectedDocument(null);
  };

  const getSelectedFolderDocuments = (): Document[] => {
    const folder = knowledgeBases.find(
      (kb: KnowledgeBase) => kb.id === selectedFolder
    );
    return folder?.documents || [];
  };

  const selectedKnowledgeBase = knowledgeBases.find(
    (kb) => kb.id === selectedFolder
  );

  if (selectedDocument) {
    let jsonfilename = selectedDocument.name.replace(/\.[^/.]+$/, ".json");
    return (
      <div className="min-h-screen bg-background">
        <DocumentEditor filename={jsonfilename} />
        <div className="fixed top-4 left-4 z-50">
          <button
            onClick={handleBackFromEditor}
            className="bg-card border border-border shadow-lg px-4 py-2 rounded-lg hover:bg-muted transition-colors flex items-center space-x-2 text-foreground"
          >
            <ArrowLeft className="w-4 h-4" />
            <span>Back to Knowledge Base</span>
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-background">
      <FloatingElementsBackground />

      <Sidebar
      
        sidebarOpen={sidebarOpen}
        setSidebarOpen={setSidebarOpen}
        isCollapsed={isCollapsed}
        setIsCollapsed={setIsCollapsed}
      />

      <div
        className={`min-h-screen transition-all duration-300 ${
          isCollapsed ? "lg:ml-20" : "lg:ml-64"
        }`}
      >
        <MobileHeader setSidebarOpen={setSidebarOpen} />

        <main className="p-6 lg:p-8 bg-background min-h-screen">
          {!selectedFolder ? (
            <>
              <KnowledgeBaseHeader
                isVisible={isVisible.header}
                onCreateNew={() => setShowCreateFolderModal(true)}
              />

              <StatsGrid
                knowledgeBasesCount={knowledgeBases.length}
                totalDocuments={getTotalDocuments()}
                totalScrapedPages={getTotalScrapedPages()}
                categoriesCount={
                  new Set(
                    knowledgeBases
                      .map((kb: KnowledgeBase) => kb.category)
                      .filter(Boolean)
                  ).size
                }
              />

              <KnowledgeBaseList
                knowledgeBases={knowledgeBases}
                searchQuery={searchQuery}
                setSearchQuery={setSearchQuery}
                onSelectKnowledgeBase={setSelectedFolder}
                onAddContentToKnowledgeBase={(id) => {
                  setSelectedFolder(id);
                  setShowAddContentModal(true);
                }}
                onDeleteKnowledgeBase={removeKnowledgeBase}
                onCreateFirstKnowledgeBase={() =>
                  setShowCreateFolderModal(true)
                }
              />
            </>
          ) : (
            <>
              <FolderViewHeader
                selectedKnowledgeBase={selectedKnowledgeBase}
                onBack={() => setSelectedFolder(null)}
                onAddContent={() => setShowAddContentModal(true)}
              />
              <DocumentList
                documents={getSelectedFolderDocuments()}
                onDocumentClick={handleDocumentClick}
                onAddFirstContent={() => setShowAddContentModal(true)}
              />
            </>
          )}
        </main>
      </div>

      {/* Modals */}
      <CreateFolderModal
        show={showCreateFolderModal}
        onClose={() => setShowCreateFolderModal(false)}
        newKnowledgeBase={newKnowledgeBase}
        setNewKnowledgeBase={setNewKnowledgeBase}
        onCreate={handleCreateKnowledgeBase}
      />
      <AddContentModal
        show={showAddContentModal}
        onClose={() => setShowAddContentModal(false)}
        onShowUploadModal={() => {
          setShowAddContentModal(false);
          setShowUploadModal(true);
        }}
        onShowScraperModal={() => {
          setShowAddContentModal(false);
          setShowScraperModal(true);
        }}
      />
      <UploadModal
        show={showUploadModal}
        onClose={() => setShowUploadModal(false)}
        selectedFolderId={selectedFolder}
        onFileUpload={handleFileUpload}
        uploadingFiles={uploadingFiles}
        uploadProgress={uploadProgress}
      />
      <ScraperModal
        show={showScraperModal}
        onClose={() => setShowScraperModal(false)}
      />
    </div>
  );
};

export default KnowledgeBasePage;
