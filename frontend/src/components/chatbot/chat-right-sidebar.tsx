import React from "react";
import { Plus, MessageSquare, ChevronLeft, ChevronRight } from "lucide-react";
import { mockChatHistory } from "@/components/data/constants";

/**
 * Props for the ChatRightSidebar component.
 * @interface
 */
interface ChatRightSidebarProps {
  /** State for whether the right sidebar is collapsed. */
  isRightSidebarCollapsed: boolean;
  /** Callback function to toggle the right sidebar collapse state. */
  setIsRightSidebarCollapsed: (collapsed: boolean) => void;
}

/**
 * ChatRightSidebar component displays recent chat history and a "New Chat" button.
 * @param {ChatRightSidebarProps} props - The component props.
 * @returns {React.FC} A React functional component.
 */
const ChatRightSidebar: React.FC<ChatRightSidebarProps> = ({
  isRightSidebarCollapsed,
  setIsRightSidebarCollapsed,
}) => {
  return (
    <aside
      className={`hidden lg:flex flex-col flex-shrink-0 bg-card border-l border-border p-6 transition-all duration-300 ${
        isRightSidebarCollapsed ? "w-20 items-center" : "w-80"
      } overflow-y-auto fixed right-0 top-0 h-full z-30`}
    >
      <div
        className={`flex items-center ${
          isRightSidebarCollapsed ? "justify-center" : "justify-between"
        } mb-6`}
      >
        {!isRightSidebarCollapsed && (
          <h3 className="text-sm font-semibold text-muted-foreground uppercase tracking-wider">
            CHAT HISTORY
          </h3>
        )}
        <button
          onClick={() => setIsRightSidebarCollapsed(!isRightSidebarCollapsed)}
          className="p-2 rounded-lg hover:bg-accent transition-colors text-foreground"
          aria-label={
            isRightSidebarCollapsed
              ? "Expand right sidebar"
              : "Collapse right sidebar"
          }
        >
          {isRightSidebarCollapsed ? (
            <ChevronLeft className="w-5 h-5" />
          ) : (
            <ChevronRight className="w-5 h-5" />
          )}
        </button>
      </div>

      <div className="mb-6 w-full">
        {!isRightSidebarCollapsed ? (
          <button className="w-full bg-background text-foreground border border-border px-4 py-3 rounded-xl font-semibold flex items-center justify-center space-x-2 hover:shadow-lg transition-all hover:border-primary">
            <Plus className="w-4 h-4" />
            <span>New Chat</span>
          </button>
        ) : (
          <button className="w-10 h-10 bg-background text-foreground border border-border rounded-xl flex items-center justify-center hover:shadow-lg transition-all mx-auto hover:border-primary">
            <Plus className="w-4 h-4" />
          </button>
        )}
      </div>

      <nav className="space-y-2 flex-1 overflow-y-auto w-full">
        {mockChatHistory.map((chat, index) => (
          <a
            key={index}
            href="#" // Replace with actual routing or chat selection logic
            className={`flex items-center p-3 rounded-xl text-foreground hover:bg-accent transition-colors group ${
              isRightSidebarCollapsed ? "justify-center" : ""
            }`}
          >
            <MessageSquare
              className={`w-4 h-4 text-muted-foreground group-hover:text-foreground ${
                isRightSidebarCollapsed ? "" : "mr-3"
              }`}
            />
            {!isRightSidebarCollapsed && (
              <>
                <span className="text-sm flex-1 truncate">{chat}</span>
                <ChevronRight className="w-4 h-4 text-muted-foreground group-hover:text-foreground opacity-0 group-hover:opacity-100 transition-opacity" />
              </>
            )}
          </a>
        ))}
      </nav>
    </aside>
  );
};

export default ChatRightSidebar;
