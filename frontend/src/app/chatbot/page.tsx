// src/app/chatbot/page.tsx
"use client";

import React, { useState, useEffect } from "react";
import { Menu, MessageSquare } from "lucide-react";

import Sidebar from "@/components/sidebar";
import AnimatedBackgroundElements from "@/components/ui/animated-background-elements";
import KnowledgeBaseSelector from "@/components/chatbot/knowledge-base-selector";
import ChatHistoryDisplay from "@/components/chatbot/chat-history-display";
import ChatInput from "@/components/chatbot/chat-input";
import ChatRightSidebar from "@/components/chatbot/chat-right-sidebar";

// Import types from constants for better type safety
import { KnowledgeBase, ChatMessage } from "@/components/data/constants";

/**
 * ChatbotPage is the main component for the chatbot interface.
 * It manages the state for sidebar, active section, knowledge base selection,
 * chat history, and message input, orchestrating all the smaller chatbot components.
 * @returns {React.FC} A React functional component rendering the chatbot page.
 */
const ChatbotPage: React.FC = () => {
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const [activeSection, setActiveSection] = useState("chat"); // Set active section to 'chat' for sidebar highlighting
  const [isCollapsed, setIsCollapsed] = useState(false); // Left sidebar collapse state
  const [isRightSidebarCollapsed, setIsRightSidebarCollapsed] = useState(false); // Right sidebar collapse state
  const [message, setMessage] = useState("");
  const [chatHistory, setChatHistory] = useState<ChatMessage[]>([]);
  const [selectedKnowledgeBase, setSelectedKnowledgeBase] =
    useState<KnowledgeBase | null>(null);
  const [showKnowledgeBaseSelector, setShowKnowledgeBaseSelector] =
    useState(true);

  // Function to handle sending a message (placeholder for actual API call)
  const handleSendMessage = async () => {
    if (message.trim()) {
      const userMessage: ChatMessage = { type: "user", text: message.trim() };
      setChatHistory((prev) => [...prev, userMessage]);
      const currentMessage = message;
      setMessage("");

      try {
        // Mock API call to your backend
        const response = await fetch("http://localhost:8000/query", {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({
            query: currentMessage,
            knowledgeBaseId: selectedKnowledgeBase?.id,
          }),
        });
        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`);
        }
        const data = await response.json();
        let botText = data.response || data.answer || JSON.stringify(data);
        // Replace newlines for HTML display
        botText = botText.replace(/\\n|\\r\\n|\\r/g, "<br />");
        const botMessage: ChatMessage = { type: "bot", text: botText };
        setChatHistory((prev) => [...prev, botMessage]);
      } catch (error) {
        console.error("Error sending message:", error);
        const errorMessage: ChatMessage = {
          type: "bot",
          text: "Sorry, there was an error connecting to the bot or processing your request.",
        };
        setChatHistory((prev) => [...prev, errorMessage]);
      }
    }
  };

  const handleSuggestionClick = (suggestion: string) => {
    const userSuggestion: ChatMessage = { type: "user", text: suggestion };
    setChatHistory((prev) => [...prev, userSuggestion]);

    // Simulate bot response with a delay
    setTimeout(() => {
      const kbContext = selectedKnowledgeBase
        ? ` I'll search through the ${selectedKnowledgeBase.name} knowledge base to provide you with the most relevant information.`
        : "";
      const botResponse: ChatMessage = {
        type: "bot",
        text: `Thank you for your question about "${suggestion}".${kbContext} I'm here to help you with CBB regulations and banking compliance matters.`,
      };
      setChatHistory((prev) => [...prev, botResponse]);
    }, 1000);
  };

  const handleKnowledgeBaseSelection = (kb: KnowledgeBase | null) => {
    setSelectedKnowledgeBase(kb);
    setShowKnowledgeBaseSelector(false);
    setChatHistory([]); // Clear chat history when changing KB
  };

  const handleChangeKnowledgeBaseClick = () => {
    setShowKnowledgeBaseSelector(true);
    setChatHistory([]); // Clear chat history when going back to KB selection
  };

  return (
    <div className="min-h-screen bg-background flex">
      {/* Floating background elements */}
      <AnimatedBackgroundElements />

      {/* Sidebar - Re-using the Sidebar component */}
      <Sidebar
        sidebarOpen={sidebarOpen}
        setSidebarOpen={setSidebarOpen}
        isCollapsed={isCollapsed}
        setIsCollapsed={setIsCollapsed}
      />

      {/* Main Content Area */}
      <div
        className={`flex-1 transition-all duration-300 ${
          isCollapsed ? "lg:ml-24" : "lg:ml-72" // Adjusted margin for collapsed sidebar width
        } ${isRightSidebarCollapsed ? "lg:mr-20" : "lg:mr-80"}`}
      >
        {/* Mobile Header */}
        <header className="lg:hidden bg-card border-b border-border px-4 py-3 flex items-center justify-between sticky top-0 z-40 w-full">
          <div className="flex items-center space-x-3">
            <button
              onClick={() => setSidebarOpen(true)}
              className="p-2 rounded-lg hover:bg-accent transition-colors text-foreground"
            >
              <Menu className="w-5 h-5" />
            </button>
            <h1 className="text-lg font-semibold text-foreground">Chatbot</h1>
          </div>
        </header>

        {/* Chat Main Section */}
        <main className="flex flex-col p-6 lg:p-8 bg-background min-h-screen">
          {showKnowledgeBaseSelector ? (
            <KnowledgeBaseSelector onSelect={handleKnowledgeBaseSelection} />
          ) : (
            <>
              {/* Top bar showing selected knowledge base */}
              <div className="flex items-center justify-between mb-6 p-4 bg-muted rounded-xl">
                <div className="flex items-center space-x-3">
                  <div className="w-8 h-8 bg-gradient-to-r from-primary to-secondary rounded-lg flex items-center justify-center">
                    <MessageSquare className="w-4 h-4 text-primary-foreground" />
                  </div>
                  <div>
                    <span className="text-sm text-muted-foreground">
                      Chatting with:
                    </span>
                    <span className="ml-2 font-semibold text-foreground">
                      {selectedKnowledgeBase
                        ? selectedKnowledgeBase.name
                        : "General Chat"}
                    </span>
                  </div>
                </div>
                <button
                  onClick={handleChangeKnowledgeBaseClick}
                  className="px-4 py-2 text-primary hover:bg-card rounded-lg transition-colors font-medium text-sm"
                >
                  Change Knowledge Base
                </button>
              </div>

              <ChatHistoryDisplay
                chatHistory={chatHistory}
                onSuggestionClick={handleSuggestionClick}
                selectedKnowledgeBase={selectedKnowledgeBase}
              />
            </>
          )}

          {/* Chat Input */}
          <ChatInput
            message={message}
            onMessageChange={setMessage}
            onSendMessage={handleSendMessage}
          />
        </main>
      </div>

      {/* Chat History Sidebar (Right) */}
      <ChatRightSidebar
        isRightSidebarCollapsed={isRightSidebarCollapsed}
        setIsRightSidebarCollapsed={setIsRightSidebarCollapsed}
      />
    </div>
  );
};

export default ChatbotPage;
