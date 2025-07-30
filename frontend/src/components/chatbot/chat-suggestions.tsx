// src/components/chatbot/chat-suggestions.tsx
import React from "react";

/**
 * Props for the ChatSuggestions component.
 * @interface
 */
interface ChatSuggestionsProps {
  /** An array of string suggestions. */
  suggestions: string[];
  /** Callback function when a suggestion is clicked. */
  onSuggestionClick: (suggestion: string) => void;
}

/**
 * ChatSuggestions component displays a grid of suggested questions for the chatbot.
 * @param {ChatSuggestionsProps} props - The component props.
 * @returns {React.FC} A React functional component.
 */
const ChatSuggestions: React.FC<ChatSuggestionsProps> = ({
  suggestions,
  onSuggestionClick,
}) => {
  // Array of SVG icons for suggestions (can be replaced with Lucide icons if preferred)
  const suggestionIcons = [
    <svg
      className="size-6 text-foreground"
      aria-hidden="true"
      xmlns="http://www.w3.org/2000/svg"
      width="24"
      height="24"
      fill="none"
      viewBox="0 0 24 24"
    >
      <path
        stroke="currentColor"
        strokeLinecap="round"
        strokeLinejoin="round"
        strokeWidth="2"
        d="M7.556 8.5h8m-8 3.5H12m7.111-7H4.89a.896.896 0 0 0-.629.256.868.868 0 0 0-.26.619v9.25c0 .232.094.455.26.619A.896.896 0 0 0 4.89 16H9l3 4 3-4h4.111a.896.896 0 0 0 .629-.256.868.868 0 0 0 .26-.619v-9.25a.868.868 0 0 0-.26-.619.896.896 0 0 0-.63-.256Z"
      />
    </svg>,
    <svg
      className="size-6 text-foreground"
      aria-hidden="true"
      xmlns="http://www.w3.org/2000/svg"
      width="24"
      height="24"
      fill="none"
      viewBox="0 0 24 24"
    >
      <path
        stroke="currentColor"
        strokeLinecap="round"
        strokeLinejoin="round"
        strokeWidth="2"
        d="M9 9a3 3 0 0 1 3-3m-2 15h4m0-3c0-4.1 4-4.9 4-9A6 6 0 1 0 6 9c0 4 4 5 4 9h4Z"
      />
    </svg>,
    <svg
      className="size-6 text-foreground"
      aria-hidden="true"
      xmlns="http://www.w3.org/2000/svg"
      width="24"
      height="24"
      fill="none"
      viewBox="0 0 24 24"
    >
      <path
        stroke="currentColor"
        strokeLinecap="round"
        strokeLinejoin="round"
        strokeWidth="2"
        d="M10 3v4a1 1 0 0 1-1 1H5m4 10v-2m3 2v-6m3 6v-3m4-11v16a1 1 0 0 1-1 1H6a1 1 0 0 1-1-1V7.914a1 1 0 0 1 .293-.707l3.914-3.914A1 1 0 0 1 9.914 3H18a1 1 0 0 1 1 1Z"
      />
    </svg>,
  ];

  return (
    <div className="grid grid-cols-1 md:grid-cols-3 gap-6 max-w-4xl w-full mb-12">
      {suggestions.map((suggestion, index) => (
        <button
          key={index}
          onClick={() => onSuggestionClick(suggestion)}
          className="rounded-xl border bg-card text-card-foreground shadow size-full hover:cursor-pointer hover:shadow-xl border-none transition-shadow duration-200"
        >
          <div className="flex items-center space-x-3 p-6 pt-4 pb-2">
            <h3 className="font-semibold leading-none tracking-tight flex justify-center">
              {suggestionIcons[index % suggestionIcons.length]}{" "}
              {/* Use modulo for icon repetition */}
            </h3>
          </div>
          <div className="flex justify-center text-center p-4">
            <p className="text-sm sm:text-base lg:text-lg text-muted-foreground">
              {suggestion}
            </p>
          </div>
        </button>
      ))}
    </div>
  );
};

export default ChatSuggestions;
