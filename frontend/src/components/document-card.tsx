// components/dashboard/dashboard-card.tsx
import { Card, CardContent } from "@/components/ui/card";
import React from "react";

interface DashboardCardProps {
  title: string;
  description: string;
  onClick: () => void;
}

const DashboardCard: React.FC<DashboardCardProps> = ({
  title,
  description,
  onClick,
}) => {
  return (
    <Card
      className="cursor-pointer hover:shadow-lg transition-shadow hover:border-primary/40 border-2 border-border rounded-2xl"
      onClick={onClick}
    >
      <CardContent className="p-8 flex flex-col items-center justify-center h-40">
        <h2 className="text-xl font-semibold mb-2">{title}</h2>
        <p className="text-sm text-muted-foreground text-center">
          {description}
        </p>
      </CardContent>
    </Card>
  );
};

export default DashboardCard;
