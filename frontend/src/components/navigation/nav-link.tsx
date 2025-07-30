// src/components/navigation/nav-link.tsx

import React from "react";
import Link from "next/link";
import { usePathname } from "next/navigation";
import type { NavItem } from "@/components/data/constants";

/**
 * Props for the NavLink component.
 */
interface NavLinkProps {
  /**
   * Navigation item object containing name, label, href, and icon.
   */
  item: NavItem;

  /**
   * The currently active section name.
   */
  activeSection: string;

  /**
   * Function to update the active section when the link is clicked.
   */
  setActiveSection: (section: string) => void;

  /**
   * Boolean indicating whether the sidebar is collapsed.
   */
  isCollapsed: boolean;

  /**
   * Optional function to toggle the sidebar visibility.
   */
  setSidebarOpen?: (open: boolean) => void;
}

/**
 * NavLink renders a single navigation link with optional icon and label.
 * It handles highlighting for active routes and collapsible behavior for sidebar menus.
 *
 * @param {NavLinkProps} props - Props including the navigation item and UI state handlers.
 */
const NavLink: React.FC<NavLinkProps> = ({
  item,
  activeSection,
  setActiveSection,
  isCollapsed,
  setSidebarOpen,
}) => {
  const pathname = usePathname();

  // Determines if the current nav item is active based on route or section
  // Prioritize activeSection over pathname for highlighting
  // This allows setting active state without navigation
  const isActive = activeSection === item.name || pathname === item.href;


    /**
   * Handles link click behavior:
   * - Updates the active section
   * - Closes the sidebar if applicable
   */
  const handleClick = () => {
    setActiveSection(item.name);
    if (setSidebarOpen) setSidebarOpen(false);
  };

  return (
    <Link
      href={item.href}
      onClick={handleClick}
      className={`
        flex items-center space-x-3 p-3 rounded-lg w-full text-left
        transition-colors duration-200
        ${
          isActive
            ? "bg-primary text-primary-foreground"
            : "text-muted-foreground hover:bg-accent hover:text-foreground"
        }
        ${isCollapsed ? "justify-center" : ""}
      `}
    >
      {item.icon()}
      {!isCollapsed && (
        <span className="text-sm font-medium">{item.label}</span>
      )}
    </Link>
  );
};

export default NavLink;
