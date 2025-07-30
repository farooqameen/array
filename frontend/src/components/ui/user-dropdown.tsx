"use client";

import {
  DropdownMenu,
  DropdownMenuTrigger,
  DropdownMenuContent,
  DropdownMenuItem,
} from "@/components/ui/dropdown-menu";
import { Users, Sun, Moon, LogOut } from "lucide-react";
import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import { logout } from "@/lib/auth/auth";

interface UserDropdownProps {
  isCollapsed: boolean;
}

// User dropdown
export function UserDropdown({ isCollapsed }: UserDropdownProps) {
  // Theme
  const [theme, setTheme] = useState<"light" | "dark">("light");

  // Router
  const router = useRouter();

  // Get saved theme
  useEffect(() => {
    if (typeof window !== "undefined") {
      const saved = localStorage.getItem("theme") as "light" | "dark" | null;
      if (saved) {
        setTheme(saved);
        document.documentElement.classList.add(saved);
      }
    }
  }, []);

  // Toggle theme
  const toggleTheme = () => {
    const newTheme = theme === "light" ? "dark" : "light";
    setTheme(newTheme);
    if (typeof window !== "undefined") {
      localStorage.setItem("theme", newTheme);
      document.documentElement.classList.remove(theme);
      document.documentElement.classList.add(newTheme);
    }
  };

  // Logout
  const handleLogout = async () => {
    try {
      logout(); // make sure this is async if it uses Cognito or API
      router.push("/login");
    } catch (e) {
      console.error("Logout failed:", e);
    }
  };

  return (
    <DropdownMenu>
      <DropdownMenuTrigger asChild>
        <button
          className={`flex items-center w-full ${
            isCollapsed ? "justify-center" : "space-x-3"
          } p-2 rounded-lg hover:bg-muted transition-colors`}
        >
          <div className="w-9 h-9 bg-gradient-to-r from-[#3C04FC] to-[#BB4CD8] rounded-full flex items-center justify-center">
            <Users className="w-4 h-4 text-white" />
          </div>

          {!isCollapsed && (
            <div className="flex flex-col text-left">
              <span className="text-sm font-medium text-foreground">
                User Profile
              </span>
              <span className="text-xs text-muted-foreground">
                Manage Account
              </span>
            </div>
          )}
        </button>
      </DropdownMenuTrigger>

      <DropdownMenuContent
        side={isCollapsed ? "right" : "bottom"}
        align={isCollapsed ? "start" : "end"}
        className="w-56 mt-2"
      >
        <DropdownMenuItem onClick={toggleTheme}>
          {theme === "light" ? (
            <>
              <Moon className="w-4 h-4 mr-2" />
              Switch to Dark
            </>
          ) : (
            <>
              <Sun className="w-4 h-4 mr-2" />
              Switch to Light
            </>
          )}
        </DropdownMenuItem>

        <DropdownMenuItem onClick={handleLogout}>
          <LogOut className="w-4 h-4 mr-2" />
          Logout
        </DropdownMenuItem>
      </DropdownMenuContent>
    </DropdownMenu>
  );
}
