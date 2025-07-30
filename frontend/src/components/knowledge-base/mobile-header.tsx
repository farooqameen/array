import React from "react";
import { Menu } from "lucide-react";

interface MobileHeaderProps {
  setSidebarOpen: (open: boolean) => void;
}

const MobileHeader: React.FC<MobileHeaderProps> = ({ setSidebarOpen }) => (
  <header className="lg:hidden bg-background border-b border-border px-4 py-3 flex items-center justify-between sticky top-0 z-40">
    <div className="flex items-center space-x-3">
      <button
        onClick={() => setSidebarOpen(true)}
        className="p-2 rounded-lg hover:bg-muted transition-colors"
      >
        <Menu className="w-5 h-5 text-foreground" />
      </button>
      <h1 className="text-lg font-semibold text-foreground">Knowledge Base</h1>
    </div>
  </header>
);

export default MobileHeader;
