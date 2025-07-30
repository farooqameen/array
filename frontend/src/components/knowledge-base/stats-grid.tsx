import React from "react";
import { LucideIcon } from "lucide-react";
import { Folder, FileText, Globe, Tag } from "lucide-react"; // Import all needed icons

interface StatCardProps {
  label: string;
  value: string;
  icon: LucideIcon;
  colorClass: string;
}

const StatCard: React.FC<StatCardProps> = ({
  label,
  value,
  icon: IconComponent,
  colorClass,
}) => (
  <div className="bg-card rounded-2xl p-6 border border-border hover:shadow-lg transition-all">
    <div
      className={`w-12 h-12 rounded-xl bg-gradient-to-r ${colorClass} flex items-center justify-center mb-4`}
    >
      <IconComponent className="w-6 h-6 text-primary-foreground" />
    </div>
    <div className="text-2xl font-bold text-foreground mb-1">{value}</div>
    <div className="text-sm text-muted-foreground">{label}</div>
  </div>
);

interface StatsGridProps {
  knowledgeBasesCount: number;
  totalDocuments: number;
  totalScrapedPages: number;
  categoriesCount: number;
}

const StatsGrid: React.FC<StatsGridProps> = ({
  knowledgeBasesCount,
  totalDocuments,
  totalScrapedPages,
  categoriesCount,
}) => (
  <section className="mb-12">
    <div className="grid grid-cols-2 lg:grid-cols-4 gap-6 max-w-7xl mx-auto">
      <StatCard
        label="Knowledge Bases"
        value={knowledgeBasesCount.toString()}
        icon={Folder}
        colorClass="from-primary to-[var(--chart-2)]" // Using custom properties for deeper gradients
      />
      <StatCard
        label="Total Documents"
        value={totalDocuments.toString()}
        icon={FileText}
        colorClass="from-secondary to-[var(--chart-5)]"
      />
      <StatCard
        label="Scraped Pages"
        value={totalScrapedPages.toString()}
        icon={Globe}
        colorClass="from-[var(--chart-3)] to-primary"
      />
      <StatCard
        label="Categories"
        value={categoriesCount.toString()}
        icon={Tag}
        colorClass="from-[var(--chart-5)] to-secondary"
      />
    </div>
  </section>
);

export default StatsGrid;
