"use client";
import React, { useState, useEffect, useRef } from "react";
import {
  Plus,
  MessageSquare,
  Bot,
  ChevronRight,
  Filter,
  Folder,
  Brain,
  ArrowLeft,
  CircleHelp,
  Loader2,
  SendHorizontal,
} from "lucide-react";
import Sidebar from "@/components/sidebar";

// Types
interface Message {
  id: string;
  content: string;
  isUser: boolean;
  timestamp: Date;
  sources?: string[];
}

interface ChatSession {
  id: string;
  title: string;
  knowledgeBaseId: number;
  knowledgeBaseName: string;
  lastMessage: string;
  timestamp: string;
  messageCount: number;
}

interface KnowledgeBase {
  id: number;
  name: string;
  description: string;
  documentsCount: number;
  scrapedPagesCount: number;
  category: string;
  lastUpdated: string;
}

const ChatbotPage = () => {
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const [activeSection, setActiveSection] = useState("chatbot");
  const [isCollapsed, setIsCollapsed] = useState(false);

  // Chat states
  const [selectedKnowledgeBase, setSelectedKnowledgeBase] =
    useState<KnowledgeBase | null>(null);
  const [currentChat, setCurrentChat] = useState<string | null>(null);
  const [messages, setMessages] = useState<Message[]>([]);
  const [inputMessage, setInputMessage] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [showKnowledgeBaseSelector, setShowKnowledgeBaseSelector] =
    useState(true);
  const [chatHistory, setChatHistory] = useState<ChatSession[]>([]);
  const [chatSidebarOpen, setChatSidebarOpen] = useState(true);

  const messagesEndRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLTextAreaElement>(null);

  // Mock data
  const knowledgeBases: KnowledgeBase[] = [
    {
      id: 1,
      name: "Financial Reports 2024",
      description: "All financial documents and reports for 2024",
      documentsCount: 15,
      scrapedPagesCount: 0,
      category: "finance",
      lastUpdated: "2024-01-20",
    },
    {
      id: 2,
      name: "Product Documentation",
      description: "Technical documentation and user guides",
      documentsCount: 8,
      scrapedPagesCount: 45,
      category: "product",
      lastUpdated: "2024-01-18",
    },
    {
      id: 3,
      name: "Marketing Materials",
      description: "Marketing strategies, campaigns, and brand guidelines",
      documentsCount: 12,
      scrapedPagesCount: 23,
      category: "marketing",
      lastUpdated: "2024-01-16",
    },
  ];

  const mockChatHistory: ChatSession[] = [
    {
      id: "1",
      title: "CIU Obligations and Liability Limitation",
      knowledgeBaseId: 1,
      knowledgeBaseName: "Financial Reports 2024",
      lastMessage: "What were the key highlights from Q4?",
      timestamp: "2024-01-20",
      messageCount: 12,
    },
    {
      id: "2",
      title: "Insurance Code Principles",
      knowledgeBaseId: 2,
      knowledgeBaseName: "Product Documentation",
      lastMessage: "Can you explain the authentication flow?",
      timestamp: "2024-01-19",
      messageCount: 8,
    },
    {
      id: "3",
      title: "Discussing CBB",
      knowledgeBaseId: 3,
      knowledgeBaseName: "Marketing Materials",
      lastMessage: "What are our approved color schemes?",
      timestamp: "2024-01-18",
      messageCount: 5,
    },
    {
      id: "4",
      title: "GCC Fund Passporting Regime Explained",
      knowledgeBaseId: 1,
      knowledgeBaseName: "Financial Reports 2024",
      lastMessage: "How does the passporting regime work?",
      timestamp: "2024-01-17",
      messageCount: 15,
    },
    {
      id: "5",
      title: "Bank Communication Standards Discussion",
      knowledgeBaseId: 2,
      knowledgeBaseName: "Product Documentation",
      lastMessage: "What are the compliance requirements?",
      timestamp: "2024-01-16",
      messageCount: 7,
    },
  ];

  useEffect(() => {
    setChatHistory(mockChatHistory);
  }, []);

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  const handleKnowledgeBaseSelect = (kb: KnowledgeBase) => {
    setSelectedKnowledgeBase(kb);
    setShowKnowledgeBaseSelector(false);
    setCurrentChat(null);
    setMessages([]);

    const welcomeMessage: Message = {
      id: Date.now().toString(),
      content: `Hello! I'm ready to help you with questions about "${kb.name}". This knowledge base contains ${kb.documentsCount} documents and ${kb.scrapedPagesCount} scraped pages. What would you like to know?`,
      isUser: false,
      timestamp: new Date(),
    };
    setMessages([welcomeMessage]);
  };

  const handleSendMessage = async () => {
    if (!inputMessage.trim() || isLoading || !selectedKnowledgeBase) return;

    const userMessage: Message = {
      id: Date.now().toString(),
      content: inputMessage,
      isUser: true,
      timestamp: new Date(),
    };

    setMessages((prev) => [...prev, userMessage]);
    setInputMessage("");
    setIsLoading(true);

    setTimeout(() => {
      const aiResponse: Message = {
        id: (Date.now() + 1).toString(),
        content: `Based on the documents in "${selectedKnowledgeBase.name}", here's what I found regarding your question: "${inputMessage}"\n\nThis is a simulated response. In a real implementation, this would be processed by your AI system using the selected knowledge base as context.`,
        isUser: false,
        timestamp: new Date(),
        sources: ["Document 1.pdf", "Report 2.docx"],
      };

      setMessages((prev) => [...prev, aiResponse]);
      setIsLoading(false);
    }, 1500);
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };

  const startNewChat = () => {
    setCurrentChat(null);
    setMessages([]);
    setShowKnowledgeBaseSelector(true);
    setSelectedKnowledgeBase(null);
  };

  const loadChatSession = (session: ChatSession) => {
    const kb = knowledgeBases.find((k) => k.id === session.knowledgeBaseId);
    if (kb) {
      setSelectedKnowledgeBase(kb);
      setShowKnowledgeBaseSelector(false);
      setCurrentChat(session.id);

      const mockMessages: Message[] = [
        {
          id: "1",
          content: `Hello! I'm ready to help you with questions about "${kb.name}".`,
          isUser: false,
          timestamp: new Date(session.timestamp),
        },
        {
          id: "2",
          content: session.lastMessage,
          isUser: true,
          timestamp: new Date(session.timestamp),
        },
      ];
      setMessages(mockMessages);
    }
  };

  // Chat History Sidebar Component
  const ChatSidebar = () => (
    <div
      style={
        {
          "--sidebar-width": "16rem",
          "--sidebar-width-icon": "3rem",
        } as React.CSSProperties
      }
      className="group/sidebar-wrapper flex min-h-svh has-[[data-variant=inset]]:bg-white w-fit"
      data-sentry-element="SidebarProvider"
      data-sentry-component="ChatSidebar"
      data-sentry-source-file="chat-sidebar.tsx"
    >
      <div
        className="group peer hidden text-sidebar-foreground md:block"
        data-state={chatSidebarOpen ? "expanded" : "collapsed"}
        data-collapsible=""
        data-variant="sidebar"
        data-side="right"
      >
        <div className="relative w-[--sidebar-width] bg-transparent transition-[width] duration-200 ease-linear group-data-[collapsible=offcanvas]:w-0 group-data-[side=right]:rotate-180 group-data-[collapsible=icon]:w-[--sidebar-width-icon]" />

        <div className="fixed inset-y-0 z-10 hidden transition-[left,right,width] duration-200 ease-linear md:flex right-0 group-data-[collapsible=offcanvas]:right-[calc(var(--sidebar-width)*-1)] group-data-[collapsible=icon]:w-[--sidebar-width-icon] group-data-[side=left]:border-r group-data-[side=right]:border-l size-full max-w-xs sm:max-w-sm md:max-w-md lg:max-w-xs">
          <div
            data-sidebar="sidebar"
            className="flex size-full flex-col bg-white group-data-[variant=floating]:rounded-lg group-data-[variant=floating]:border group-data-[variant=floating]:border-sidebar-border group-data-[variant=floating]:shadow"
          >
            {/* Header */}
            <div
              data-sidebar="header"
              className="flex flex-col gap-2 p-2 px-4 py-2 sm:px-5 sm:py-3"
            />

            {/* Content */}
            <div
              data-sidebar="content"
              className="flex min-h-0 flex-1 flex-col gap-2 overflow-auto group-data-[collapsible=icon]:overflow-hidden overflow-y-auto"
            >
              <div
                data-sidebar="group"
                className="relative flex w-full min-w-0 flex-col p-2 pl-4"
              >
                <div
                  data-sidebar="group-label"
                  className="flex h-8 shrink-0 items-center rounded-md px-2 font-medium text-sidebar-foreground/70 outline-none ring-sidebar-ring transition-[margin,opacity] duration-200 ease-linear focus-visible:ring-2 text-md group-data-[collapsible=icon]:-mt-8 group-data-[collapsible=icon]:opacity-0"
                >
                  <Bot className="size-4 mr-2 shrink-0" />
                  CHATBOT HISTORY
                </div>

                <ul
                  data-sidebar="menu"
                  className="flex w-full min-w-0 flex-col gap-1 space-y-1"
                >
                  {/* New Chat Button */}
                  <li
                    data-sidebar="menu-item"
                    className="group/menu-item relative w-full min-w-0 list-none my-0.5"
                  >
                    <button
                      onClick={startNewChat}
                      data-sidebar="menu-button"
                      data-size="lg"
                      data-active="false"
                      className="peer/menu-button flex w-full items-center gap-2 overflow-hidden rounded-md p-2 text-left outline-none ring-sidebar-ring transition-[width,height,padding] focus-visible:ring-2 hover:bg-gray-100 dark:hover:bg-gray-600 h-11 text-sm group-data-[collapsible=icon]:!p-0"
                    >
                      <Plus className="size-4 mr-2 shrink-0" />
                      New Chat
                    </button>
                  </li>

                  {/* Chat History */}
                  {chatHistory.map((session) => (
                    <li
                      key={session.id}
                      data-sidebar="menu-item"
                      className="group/menu-item relative w-full min-w-0 list-none"
                    >
                      <button
                        onClick={() => loadChatSession(session)}
                        data-sidebar="menu-button"
                        data-size="lg"
                        data-active={
                          currentChat === session.id ? "true" : "false"
                        }
                        className={`peer/menu-button flex w-full items-center gap-2 overflow-hidden rounded-md p-2 text-left outline-none ring-sidebar-ring transition-[width,height,padding] focus-visible:ring-2 h-11 text-sm group-data-[collapsible=icon]:!p-0 hover:bg-gray-100 dark:hover:bg-gray-600 ${
                          currentChat === session.id
                            ? "bg-white-accent text-sidebar-accent-foreground font-medium"
                            : ""
                        }`}
                      >
                        <MessageSquare className="size-4" />
                        <div
                          className="overflow-hidden ml-2 max-w-full"
                          title={session.title}
                        >
                          <span className="truncate">{session.title}</span>
                        </div>
                      </button>
                    </li>
                  ))}
                </ul>
              </div>
            </div>

            {/* Footer */}
            <div
              data-sidebar="footer"
              className="flex flex-col gap-2 p-2 px-4 py-2 sm:px-5 sm:py-3"
            />

            {/* Rail Button */}
            <button
              onClick={() => setChatSidebarOpen(!chatSidebarOpen)}
              className="inline-flex gap-2 whitespace-nowrap text-sm font-medium transition-colors focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring disabled:pointer-events-none disabled:opacity-50 size-9 absolute inset-y-12 z-20 items-center justify-center w-6 -left-3 bg-white border border-gray-200 shadow rounded-full hover:bg-gray-200 hover:text-accent-foreground"
              data-sidebar="rail"
              data-side="right"
              aria-label="Toggle Sidebar"
              title="Toggle Sidebar"
            >
              <ChevronRight className="s-4" />
            </button>
          </div>
        </div>
      </div>
    </div>
  );

  // Knowledge Base Selector Component
  const EmptyScreen = () => (
    <div className="mx-auto max-w-full sm:max-w-2xl lg:max-w-4xl px-4 sm:px-6 lg:px-8">
      <div className="flex flex-col items-center gap-6 rounded-3xl mt-6">
        <div className="w-full flex flex-col items-center">
          <div className="flex justify-center mb-6">
            <div className="flex flex-col items-center justify-center px-2 py-4 w-full max-w-xs mx-auto">
              <div className="w-20 h-20 bg-gradient-to-r from-cyan-400 via-purple-500 to-pink-500 rounded-2xl flex items-center justify-center mx-auto mb-6">
                <Brain className="w-10 h-10 text-white" />
              </div>
              <h1 className="text-base sm:text-lg md:text-2xl font-semibold bg-gradient-to-r from-cyan-400 via-purple-500 to-pink-500 text-transparent bg-clip-text text-center">
                How can I assist you?
              </h1>
            </div>
          </div>

          <div className="w-full grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
            {knowledgeBases.map((kb) => (
              <div key={kb.id} className="w-full">
                <div
                  onClick={() => handleKnowledgeBaseSelect(kb)}
                  className="rounded-xl border bg-card text-card-foreground shadow size-full hover:cursor-pointer hover:shadow-xl border-none transition-shadow duration-200"
                >
                  <div className="flex items-center space-x-3 p-6 pt-4 pb-2">
                    <h3 className="font-semibold leading-none tracking-tight flex justify-center">
                      <Folder className="size-6 text-gray-800 dark:text-white" />
                    </h3>
                  </div>
                  <div className="flex justify-center text-center p-4">
                    <div className="space-y-2">
                      <p className="text-sm sm:text-base lg:text-lg font-semibold">
                        {kb.name}
                      </p>
                      <p className="text-xs text-gray-600">{kb.description}</p>
                      <div className="flex items-center justify-center space-x-4 text-xs text-gray-500">
                        <span>{kb.documentsCount} docs</span>
                        <span>{kb.scrapedPagesCount} pages</span>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );

  // Main Chat Interface
  const Chat = () => (
    <div className="h-screen relative group w-full pl-0 peer-[[data-state=open]]:lg:pl-[250px] peer-[[data-state=open]]:xl:pl-[300px]">
      {/* Help Button */}
      <button className="fixed top-16 right-16 bg-primary text-white rounded-full p-2 shadow-lg z-[2] select-none">
        <CircleHelp className="w-6 h-6" />
      </button>

      <div className="h-[calc(100dvh-0px)] overflow-y-auto scrollbar-hidden">
        <div className="pb-[80px] pt-4 md:pt-10">
          {showKnowledgeBaseSelector ? (
            <EmptyScreen />
          ) : (
            <div className="mx-auto max-w-full sm:max-w-2xl lg:max-w-4xl px-4 sm:px-6 lg:px-8">
              {/* Chat Header */}
              <div className="flex items-center justify-between mb-6 p-4 bg-white rounded-xl border border-gray-200">
                <div className="flex items-center space-x-3">
                  <button
                    onClick={() => setShowKnowledgeBaseSelector(true)}
                    className="p-2 hover:bg-gray-100 rounded-lg transition-colors"
                  >
                    <ArrowLeft className="w-5 h-5" />
                  </button>
                  <div className="w-10 h-10 bg-gradient-to-r from-cyan-400 via-purple-500 to-pink-500 rounded-xl flex items-center justify-center">
                    <Bot className="w-5 h-5 text-white" />
                  </div>
                  <div>
                    <h2 className="font-semibold text-gray-900">
                      {selectedKnowledgeBase?.name}
                    </h2>
                    <p className="text-sm text-gray-500">
                      {selectedKnowledgeBase?.documentsCount} documents •{" "}
                      {selectedKnowledgeBase?.scrapedPagesCount} pages
                    </p>
                  </div>
                </div>

                <button
                  onClick={startNewChat}
                  className="bg-gradient-to-r from-cyan-400 via-purple-500 to-pink-500 text-white px-4 py-2 rounded-lg font-semibold hover:shadow-lg transition-all flex items-center space-x-2"
                >
                  <Plus className="w-4 h-4" />
                  <span>New Chat</span>
                </button>
              </div>

              {/* Messages */}
              <div className="space-y-4 mb-6">
                {messages.map((message) => (
                  <div
                    key={message.id}
                    className={`flex ${
                      message.isUser ? "justify-end" : "justify-start"
                    }`}
                  >
                    <div
                      className={`max-w-3xl p-4 rounded-2xl ${
                        message.isUser
                          ? "bg-gradient-to-r from-cyan-400 via-purple-500 to-pink-500 text-white"
                          : "bg-white border border-gray-200"
                      }`}
                    >
                      <div className="whitespace-pre-wrap">
                        {message.content}
                      </div>

                      {message.sources && (
                        <div className="mt-3 pt-3 border-t border-gray-200">
                          <p className="text-xs text-gray-500 mb-2">Sources:</p>
                          <div className="flex flex-wrap gap-2">
                            {message.sources.map((source, index) => (
                              <span
                                key={index}
                                className="text-xs px-2 py-1 bg-gray-100 rounded-full text-gray-600"
                              >
                                {source}
                              </span>
                            ))}
                          </div>
                        </div>
                      )}

                      <div
                        className={`text-xs mt-2 ${
                          message.isUser ? "text-white/70" : "text-gray-500"
                        }`}
                      >
                        {message.timestamp.toLocaleTimeString()}
                      </div>
                    </div>
                  </div>
                ))}

                {isLoading && (
                  <div className="flex justify-start">
                    <div className="bg-white border border-gray-200 p-4 rounded-2xl">
                      <div className="flex items-center space-x-2">
                        <Loader2 className="w-4 h-4 animate-spin" />
                        <span className="text-sm text-gray-500">
                          Thinking...
                        </span>
                      </div>
                    </div>
                  </div>
                )}

                <div ref={messagesEndRef} />
              </div>
            </div>
          )}
        </div>

        {/* Input Area */}
        {!showKnowledgeBaseSelector && (
          <div className="fixed bottom-0 left-1/2 transform -translate-x-1/2 z-20 sm:px-4 pb-4 flex justify-center backdrop-blur-0 sm:backdrop-blur-md w-full sm:w-10/12 md:w-8/12 lg:w-7/12">
            <div className="w-full max-w-full sm:max-w-xl md:max-w-2xl lg:max-w-3xl rounded-xl border border-gray-200 bg-white/70 p-0">
              <div className="relative flex max-h-[900px] bg-white rounded-md w-full flex-col overflow-hidden px-8 sm:pr-12 p-2">
                <textarea
                  ref={inputRef}
                  value={inputMessage}
                  onChange={(e) => setInputMessage(e.target.value)}
                  onKeyPress={handleKeyPress}
                  tabIndex={0}
                  placeholder="Send a message."
                  className="min-h-[50px] max-h-[120px] w-full resize-none bg-transparent pr-4 py-[1rem] focus-within:outline-none sm:text-sm overflow-auto scrollbar-hidden"
                  spellCheck="false"
                  autoComplete="off"
                  autoCorrect="off"
                  rows={1}
                  maxLength={5000}
                  style={{ height: "52px !important" }}
                />

                <div className="absolute right-4 bottom-3 flex items-center gap-1.5">
                  <button
                    onClick={handleSendMessage}
                    disabled={!inputMessage.trim() || isLoading}
                    className="inline-flex items-center justify-center gap-2 whitespace-nowrap rounded-md text-sm font-medium focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring disabled:pointer-events-none shadow size-9 mb-1 p-0 bg-primary hover:bg-secondary text-white disabled:opacity-50 disabled:cursor-not-allowed transition"
                    type="button"
                  >
                    <SendHorizontal className="size-4" />
                    <span className="sr-only">Send message</span>
                  </button>

                  <button
                    type="button"
                    className="flex items-center justify-center rounded-full border bg-white p-2 mb-1 hover:bg-secondary hover:text-white transition-colors"
                  >
                    <Filter className="size-4" />
                  </button>
                </div>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );

  return (
    <div className="min-w-full px-6 py-2 h-3/5">
      <div
        style={
          {
            "--sidebar-width": "16rem",
            "--sidebar-width-icon": "3rem",
          } as React.CSSProperties
        }
        className="group/sidebar-wrapper flex min-h-svh w-full has-[[data-variant=inset]]:bg-white"
      >
        {/* Your existing sidebar */}
        <Sidebar
          sidebarOpen={sidebarOpen}
          setSidebarOpen={setSidebarOpen}
          isCollapsed={isCollapsed}
          setIsCollapsed={setIsCollapsed}
        />

        {/* Main Content */}
        <main className="flex w-full flex-1 flex-col md:peer-data-[variant=inset]:m-2 md:peer-data-[state=collapsed]:peer-data-[variant=inset]:ml-2 md:peer-data-[variant=inset]:ml-0 md:peer-data-[variant=inset]:rounded-xl md:peer-data-[variant=inset]:shadow relative bg-white dark:bg-zinc-900 rounded-3xl shadow-lg p-2 mt-5">
          <div className="flex flex-col overflow-y-auto">
            <header className="flex h-16 shrink-0 items-center gap-2 transition-[width,height] ease-linear group-has-[[data-collapsible=icon]]/sidebar-wrapper:h-12" />

            <div className="flex w-full overflow-hidden">
              <div className="flex-1 overflow-hidden flex justify-center items-start">
                <div className="w-full max-w-4xl h-full">
                  <Chat />
                </div>
              </div>
            </div>
          </div>
        </main>

        {/* Chat History Sidebar */}
        {!showKnowledgeBaseSelector && <ChatSidebar />}
      </div>
    </div>
  );
};

export default ChatbotPage;
