// src/app/page.tsx
"use client";
import React, { useState, useEffect } from "react";
import { Upload, Sparkles, Menu, ChevronRight, Play } from "lucide-react"; // only import icons directly used here now
import { useRouter, usePathname } from "next/navigation";

import Sidebar from "@/components/sidebar";
import AnimatedBackgroundElements from "@/components/ui/animated-background-elements";
import FeatureCard from "@/components/ui/feature-card";
import QuickStartStep from "@/components/ui/quick-start-step";

// Import data from constants
import {
  featureItemsData,
  quickStartStepsData,
  navItems,
} from "@/components/data/constants";

/**
 * RagToolInterface - Main page component rendering sidebar, hero, features, quick start steps.
 * Uses global CSS for colors, modular components and animation visibility detection.
 */
const RagToolInterface: React.FC = () => {
  const router = useRouter();
  const pathname = usePathname();
  
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const [activeSection, setActiveSection] = useState("home");  // Initial state for active section
  const [isVisible, setIsVisible] = useState<Record<string, boolean>>({});
  const [isCollapsed, setIsCollapsed] = useState(false);

  // Sync activeSection with current pathname
  useEffect(() => {
    const currentNavItem = navItems.find(item => item.href === pathname);
    if (currentNavItem) {
      setActiveSection(currentNavItem.name);
    }
  }, [pathname]);

  // Initialize featureItems using the data function from constants
  const featureItems = featureItemsData(setActiveSection);
  const quickStartSteps = quickStartStepsData;  // Quick start steps are directly from constants

  // IntersectionObserver to track visibility for animations
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

    const elementsToObserve = [
      document.getElementById("hero"),
      document.getElementById("features-header"),
      ...featureItems.map((_, index) =>
        document.getElementById(`feature-card-${index}`)
      ),
    ].filter(Boolean) as Element[];

    elementsToObserve.forEach((el) => observer.observe(el));

    return () => observer.disconnect();
  }, [featureItems]);  // Dependency updated to featureItems

  // Apply initial theme on first render based on localStorage or default to light
  useEffect(() => {
    const storedTheme = localStorage.getItem("theme") as
      | "light"
      | "dark"
      | null;
    if (storedTheme) {
      document.documentElement.classList.add(storedTheme);
    } else {
      document.documentElement.classList.add("light");
    }
  }, []);

  // Handle upload button click with navigation
  const handleUploadClick = () => {
    setActiveSection("search");
    router.push("/search-engine");
  };

  return (
    <div className="min-h-screen bg-background text-foreground">
      <AnimatedBackgroundElements />

      {/* Sidebar */}
      <Sidebar
        sidebarOpen={sidebarOpen}
        setSidebarOpen={setSidebarOpen}
        isCollapsed={isCollapsed}
        setIsCollapsed={setIsCollapsed}
      />

      {/* Main Content */}
      <div
        className={`min-h-screen transition-all duration-300 ${
          isCollapsed ? "lg:ml-24" : "lg:ml-72" // Adjusted margin for collapsed sidebar width
        }`}
      >
        {/* Mobile Header */}
        <header className="lg:hidden bg-card border-b border-border px-4 py-3 flex items-center justify-between sticky top-0 z-40">
          <div className="flex items-center space-x-3">
            <button
              onClick={() => setSidebarOpen(true)}
              className="p-2 rounded-lg hover:bg-accent transition-colors text-foreground"
            >
              <Menu className="w-5 h-5" />
            </button>
            <h1 className="text-lg font-semibold text-foreground">RAG Tool</h1>
          </div>
        </header>

        {/* Main Content Area */}
        <main className="p-6 lg:p-8 bg-background min-h-screen">
          {/* Hero Section */}
          <section
            id="hero"
            className={`mb-16 transform transition-all duration-1000 ${
              isVisible.hero
                ? "translate-y-0 opacity-100"
                : "translate-y-8 opacity-0"
            }`}
          >
            <div className="text-center max-w-4xl mx-auto">
              <div className="inline-flex items-center space-x-2 bg-primary/10 rounded-full px-5 py-2 mb-6 border border-primary/20">
                <Sparkles className="w-4 h-4 text-primary" />
                <span className="text-xs font-semibold text-primary">
                  Powered by Advanced RAG Technology
                </span>
              </div>
              <h1 className="text-3xl md:text-5xl lg:text-6xl font-bold text-foreground mb-6 leading-tight">
                Transform Your Documents
                <br />
                Into{" "}
                <span className="bg-gradient-to-r from-primary to-secondary bg-clip-text text-transparent">
                  {" "}
                  Intelligent Answers
                </span>
              </h1>
              <p className="text-lg md:text-xl text-muted-foreground max-w-3xl mx-auto mb-10 leading-relaxed">
                Drop your documents and let our AI-powered tool integrate them
                with OpenSearch, creating an intelligent knowledge base that
                answers questions using advanced RAG methodologies.
              </p>
              <div className="flex flex-col sm:flex-row gap-4 justify-center">
                <button
                  onClick={handleUploadClick}
                  className="group bg-gradient-to-r from-primary to-secondary text-primary-foreground px-8 py-4 rounded-xl font-semibold text-lg flex items-center justify-center space-x-2 hover:shadow-xl hover:shadow-primary/20 transition-all duration-300 transform hover:scale-105"
                >
                  <Upload className="w-5 h-5" />
                  <span>Upload Documents</span>
                  <ChevronRight className="w-5 h-5 group-hover:translate-x-1 transition-transform" />
                </button>
                <button className="group bg-card border-2 border-border text-foreground px-8 py-4 rounded-xl font-semibold text-lg flex items-center justify-center space-x-2 hover:border-primary hover:text-primary hover:shadow-md transition-all duration-300 transform hover:scale-105">
                  <Play className="w-5 h-5" />
                  <span>Watch Demo</span>
                </button>
              </div>
            </div>
          </section>

          {/* Features Grid */}
          <section id="features" className="mb-16">
            <div
              id="features-header"
              className={`text-center mb-12 transform transition-all duration-1000 delay-100 ${
                isVisible["features-header"]
                  ? "translate-y-0 opacity-100"
                  : "translate-y-8 opacity-0"
              }`}
            >
              <h2 className="text-2xl md:text-4xl font-bold text-foreground mb-5">
                Everything You Need for
                <span className="bg-gradient-to-r from-primary to-secondary bg-clip-text text-transparent">
                  {" "}
                  Smart Document Processing
                </span>
              </h2>
              <p className="text-lg text-muted-foreground max-w-2xl mx-auto">
                Powerful features designed to make your documents work for you
              </p>
            </div>

            <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
              {featureItems.map((feature, index) => (
                <FeatureCard
                  key={index}
                  id={`feature-card-${index}`}
                  icon={feature.icon}
                  title={feature.title}
                  description={feature.description}
                  gradientClass={feature.gradientClass}
                  action={() => {
                    feature.action(feature.sectionName)
                    router.push(feature.route);
                  }}
                  isVisible={isVisible[`feature-card-${index}`] || false}
                  delay={index * 80}
                />
              ))}
            </div>
          </section>

          {/* Quick Start Section */}
          <section className="bg-muted rounded-2xl p-10 mb-16">
            <div className="max-w-4xl mx-auto text-center">
              <h2 className="text-2xl md:text-3xl font-bold text-foreground mb-5">
                Get Started in 3 Simple Steps
              </h2>
              <p className="text-lg text-muted-foreground mb-10">
                From upload to intelligent answers in minutes
              </p>
              <div className="grid md:grid-cols-3 gap-8">
                {quickStartSteps.map((step, index) => (
                  <QuickStartStep
                    key={index}
                    stepNumber={step.stepNumber}
                    icon={step.icon}
                    title={step.title}
                    description={step.description}
                  />
                ))}
              </div>
            </div>
          </section>
        </main>
      </div>
    </div>
  );
};

export default RagToolInterface;