// src/components/ui/animated-background-elements.tsx
import React from "react";

/**
 * AnimatedBackgroundElements component renders subtle, floating background elements
 * to add visual flair to the page. It uses global CSS variables for colors.
 * @returns {React.FC} A React functional component.
 */
const AnimatedBackgroundElements: React.FC = () => {
  return (
    <div className="fixed inset-0 pointer-events-none overflow-hidden opacity-10 z-0">
      {[...Array(6)].map((_, i) => (
        <div
          key={i}
          className="absolute"
          style={{
            left: `${Math.random() * 100}%`,
            top: `${Math.random() * 100}%`,
            animationDelay: `${Math.random() * 5}s`,
          }}
        >
          {/* Using primary and secondary colors from global CSS */}
          <div className="w-1 h-1 bg-gradient-to-r from-primary to-secondary rounded-full animate-pulse" />
        </div>
      ))}
    </div>
  );
};

export default AnimatedBackgroundElements;
