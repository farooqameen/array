import React from "react";

interface QuickStartStepProps {
  stepNumber: string;
  icon: React.ReactNode;
  title: string;
  description: string;
}

/**
 * QuickStartStep shows a single step for onboarding with icon, title, description.
 */
const QuickStartStep: React.FC<QuickStartStepProps> = ({
  stepNumber,
  icon,
  title,
  description,
}) => (
  <div className="text-center">
    <div className="relative mb-6">
      <div className="w-20 h-20 mx-auto bg-card rounded-full flex items-center justify-center shadow-md border border-border mb-4">
        <div className="text-primary">{icon}</div>
      </div>
      <div className="absolute -top-2 -right-4 w-8 h-8 bg-gradient-to-r from-primary to-secondary rounded-full flex items-center justify-center text-primary-foreground font-bold text-sm">
        {stepNumber}
      </div>
    </div>
    <h3 className="text-xl font-bold text-foreground mb-3">{title}</h3>
    <p className="text-muted-foreground text-base">{description}</p>
  </div>
);

export default QuickStartStep;
