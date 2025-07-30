import React from "react";

const FloatingElementsBackground = () => (
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
        <div className="w-1 h-1 bg-gradient-to-r from-primary to-secondary rounded-full animate-pulse" />
      </div>
    ))}
  </div>
);

export default FloatingElementsBackground;