// components/EmptyState.tsx
import React from "react";
import { LucideIcon } from "lucide-react";
import { Database } from "lucide-react"; // Default icon

interface EmptyStateProps {
  icon?: LucideIcon;
  title: string;
  description: string;
  buttonText: string;
  onButtonClick: () => void;
}

const EmptyState: React.FC<EmptyStateProps> = ({
  icon: IconComponent = Database,
  title,
  description,
  buttonText,
  onButtonClick,
}) => (
  <div className="text-center py-16">
    <div className="w-24 h-24 bg-muted rounded-full flex items-center justify-center mx-auto mb-6">
      <IconComponent className="w-12 h-12 text-muted-foreground" />
    </div>
    <h3 className="text-xl font-semibold text-foreground mb-2">{title}</h3>
    <p className="text-muted-foreground mb-8">{description}</p>
    <button
      onClick={onButtonClick}
      className="bg-gradient-to-r from-primary to-secondary text-primary-foreground px-6 py-3 rounded-xl font-semibold hover:shadow-lg transition-all"
    >
      {buttonText}
    </button>
  </div>
);

export default EmptyState;
