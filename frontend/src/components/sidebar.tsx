"use client";

import React from "react";
import { usePathname } from "next/navigation";
import { X, ChevronLeft, ChevronRight } from "lucide-react";
import { navItems } from "@/components/data/constants";
import { UserDropdown } from "./ui/user-dropdown";
import Link from "next/link";
import clsx from "clsx";
import WaveLogo from "./ui/array-logo";

interface SidebarProps {
  sidebarOpen: boolean;
  setSidebarOpen: (open: boolean) => void;
  isCollapsed: boolean;
  setIsCollapsed: (collapsed: boolean) => void;
}

const Sidebar: React.FC<SidebarProps> = ({
  sidebarOpen,
  setSidebarOpen,
  isCollapsed,
  setIsCollapsed,
}) => {
  const pathname = usePathname();

  return (
    <>
      {sidebarOpen && (
        <div
          className="fixed inset-0 bg-black/50 z-40 lg:hidden"
          onClick={() => setSidebarOpen(false)}
        />
      )}

      <aside
        className={clsx(
          "fixed inset-y-0 left-0 bg-card border-r border-border z-50 transition-all duration-300 ease-in-out flex flex-col",
          sidebarOpen ? "translate-x-0" : "-translate-x-full lg:translate-x-0",
          isCollapsed ? "w-24" : "w-72"
        )}
      >
        {/* Header */}
        <div
          className={clsx(
            "p-4 flex items-center border-b border-border transition-all",
            isCollapsed ? "justify-center" : "justify-between"
          )}
        >
          <div
            className={clsx(
              "flex items-center gap-3 transition-all duration-300",
              isCollapsed ? "justify-center" : ""
            )}
          >
            <div className={clsx("shrink-0", isCollapsed ? "" : "ml-1")}>
              <WaveLogo width={40} height={40} />
            </div>

            {!isCollapsed && (
              <h2 className="text-xl font-bold bg-gradient-to-r from-primary to-secondary bg-clip-text text-transparent whitespace-nowrap">
                RAG Tool
              </h2>
            )}
          </div>

          <div className="flex gap-2">
            {/** Collapse/Expand Toggle (Desktop Only) */}
            <button
              onClick={() => setIsCollapsed(!isCollapsed)}
              title={isCollapsed ? "Expand Sidebar" : "Collapse Sidebar"}
              className={clsx(
                "absolute top-5 -right-3 z-50 hidden lg:flex items-center justify-center w-8 h-8 rounded-full border border-border bg-background shadow-md hover:bg-accent transition-colors",
                isCollapsed ? "right-[-12px]" : "right-[-16px]"
              )}
            >
              {isCollapsed ? (
                <ChevronRight className="w-4 h-4" />
              ) : (
                <ChevronLeft className="w-4 h-4" />
              )}
            </button>
          </div>
        </div>

        {/* Nav */}
        <nav className="flex flex-col flex-grow p-4 space-y-2 overflow-y-auto">
          {navItems.map((item) => {
            const isActive = pathname === item.href;

            return (
              <Link
                key={item.name}
                href={item.href}
                onClick={() => setSidebarOpen(false)}
                className={clsx(
                  "flex items-center gap-3 px-4 py-2 rounded-lg transition-all text-sm font-medium",
                  isActive
                    ? "bg-accent text-primary"
                    : "hover:bg-muted text-muted-foreground",
                  isCollapsed && "justify-center"
                )}
              >
                {item.icon()}
                {!isCollapsed && <span>{item.label}</span>}
              </Link>
            );
          })}
        </nav>

        {/* Footer */}
        <div
          className={clsx(
            "p-4 border-t border-border mt-auto",
            isCollapsed ? "text-center" : ""
          )}
        >
          <UserDropdown isCollapsed={isCollapsed} />
        </div>
      </aside>
    </>
  );
};

export default Sidebar;
