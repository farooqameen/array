// src/components/layout/document-layout.tsx
"use client";

import React, { useState } from "react";
import Sidebar from "@/components/sidebar"; // Assuming sidebar is already refactored
import { Menu } from "lucide-react";

interface DocumentLayoutProps {
  children: React.ReactNode;
}

/**
 * Renders the main layout for the document viewer, including the sidebar and content area.
 * Manages the state for sidebar open/collapse.
 * @param {object} props - The component props.
 * @param {React.ReactNode} props.children - The content to be rendered within the main layout area.
 */
const DocumentLayout: React.FC<DocumentLayoutProps> = ({ children }) => {
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const [isCollapsed, setIsCollapsed] = useState(false);

  return (
    <div className="min-h-screen bg-background">
      <Sidebar
        sidebarOpen={sidebarOpen}
        setSidebarOpen={setSidebarOpen}
        isCollapsed={isCollapsed}
        setIsCollapsed={setIsCollapsed}
      />

      <div
        className={`min-h-screen transition-all duration-300 ${
          isCollapsed ? "lg:ml-24" : "lg:ml-72"
        }`}
      >
        {/* Mobile Header */}
        <header className="lg:hidden bg-card border-b border-border px-4 py-3 flex items-center justify-between sticky top-0 z-40">
          <div className="flex items-center space-x-3">
            <button
              onClick={() => setSidebarOpen(true)}
              className="p-2 rounded-lg hover:bg-muted transition-colors text-foreground"
              aria-label="Open sidebar"
            >
              <Menu className="w-5 h-5" />
            </button>
            <h1 className="text-lg font-semibold text-foreground">
              Document Viewer
            </h1>
          </div>
        </header>

        {children}
      </div>
    </div>
  );
};

export default DocumentLayout;
