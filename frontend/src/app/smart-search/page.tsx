"use client";
import React, { useState } from "react";
import WaveLogo from "@/components/ui/array-logo";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { motion, AnimatePresence } from "framer-motion";
import { ArrowRight, XCircle, ChevronLeft } from "lucide-react";
import SmartSearchUI from "@/components/search/smart-search-ui";

/**
 * IndexSelectorPage component allows users to select an OpenSearch index
 * or navigate to a Smart Search session for an existing index.
 */
const IndexSelectorPage: React.FC = () => {
  const [selectedIndex, setSelectedIndex] = useState<string | null>(null);
  const [inputValue, setInputValue] = useState<string>("tempo");
  const [error, setError] = useState<string>("");

  /**
   * Handles starting a new search session with the entered index name.
   * Sets an error if the input is empty.
   */
  const handleStartSession = () => {
    if (inputValue.trim() === "") {
      setError("Index name cannot be empty.");
      return;
    }
    setError("");
    setSelectedIndex(inputValue.trim());
  };

  /**
   * Clears the input field and any current error messages.
   */
  const handleClearInput = () => {
    setInputValue("");
    setError("");
  };

  /**
   * Navigates the user back to the previous URL in browser history.
   */
  const handleGoBackToPreviousUrl = () => {
    window.history.back();
  };

  return (
    <div className="flex flex-col items-center justify-center min-h-screen bg-background p-4">
      <AnimatePresence>
        {!selectedIndex ? (
          <motion.div
            key="selector"
            initial={{ opacity: 0, y: -20 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: 20 }}
            transition={{ duration: 0.5 }}
            className="w-full max-w-md"
          >
            <div className="flex justify-center mb-8">
              <WaveLogo width={150} height={150} />
            </div>
            <h1 className="text-3xl font-bold text-center text-foreground mb-2">
              Smart Search
            </h1>
            <p className="text-muted-foreground text-center mb-8">
              Enter the name of the OpenSearch index to begin your session.
            </p>
            <div className="flex w-full items-start space-x-2">
              <Button
                type="button"
                variant="outline"
                size="icon"
                onClick={handleGoBackToPreviousUrl}
                className="h-12 w-12 flex-shrink-0"
                aria-label="Go Back to Previous Page"
              >
                <ChevronLeft className="h-5 w-5" />
              </Button>

              <Button
                type="button"
                variant="outline"
                size="icon"
                onClick={handleClearInput}
                className="h-12 w-12 flex-shrink-0"
                aria-label="Clear Input"
                disabled={!inputValue && !error}
              >
                <XCircle className="h-5 w-5" />
              </Button>

              <div className="grid flex-1 gap-2">
                <Input
                  id="index-name"
                  value={inputValue}
                  onChange={(e) => {
                    setInputValue(e.target.value);
                    if (error) setError("");
                  }}
                  onKeyPress={(e) => e.key === "Enter" && handleStartSession()}
                  placeholder="e.g., tempo"
                  className="h-12 text-lg"
                />
                {error && (
                  <p className="text-sm text-destructive pl-1">{error}</p>
                )}
              </div>
              <Button
                type="button"
                size="lg"
                onClick={handleStartSession}
                className="h-12 flex-shrink-0"
                aria-label="Start Search Session"
              >
                Go <ArrowRight className="ml-2 h-5 w-5" />
              </Button>
            </div>
          </motion.div>
        ) : (
          <motion.div
            key="search-ui"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ duration: 0.7 }}
            className="w-full h-full"
          >
            <SmartSearchUI
              indexName={selectedIndex}
              onBack={() => setSelectedIndex(null)}
            />
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
};

export default IndexSelectorPage;
