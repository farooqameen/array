import React from "react";
import { ChevronRight } from "lucide-react";

/**
 * Props for the FeatureCard component.
 */
interface FeatureCardProps {
  id: string;
  icon: React.ReactNode;
  title: string;
  description: string;
  gradientClass: string; // Tailwind gradient utility class
  action: () => void;
  isVisible: boolean;
  delay: number; // Animation delay in milliseconds
}

/**
 * FeatureCard renders a single feature tile with icon, title, description, and animation.
 * Supports entry animation and hover effects.
 */
const FeatureCard: React.FC<FeatureCardProps> = ({
  id,
  icon,
  title,
  description,
  gradientClass,
  action,
  isVisible,
  delay,
}) => (
  <div
    id={id}
    onClick={action}
    className={`
      group bg-card text-card-foreground rounded-2xl p-6 border border-border 
      hover:border-primary/40 hover:shadow-xl cursor-pointer 
      transition-all duration-500 transform
      ${isVisible ? "translate-y-0 opacity-100" : "translate-y-4 opacity-0"}
      hover:scale-[1.02]
    `}
    style={{ transitionDelay: `${delay}ms` }}
  >
    <div
      className={`
        w-14 h-14 rounded-xl flex items-center justify-center mb-5 
        text-primary-foreground group-hover:shadow-lg 
        transition-all duration-300 ${gradientClass}
      `}
    >
      {icon}
    </div>
    <h3 className="text-xl font-bold mb-3">{title}</h3>
    <p className="text-muted-foreground text-sm leading-relaxed mb-5 line-clamp-2">
      {description}
    </p>
    <div className="flex items-center text-primary font-semibold text-xs group-hover:translate-x-1 transition-transform">
      Learn More <ChevronRight className="w-3 h-3 ml-1" />
    </div>
  </div>
);

export default FeatureCard;
