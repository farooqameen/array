import React from "react";
import {
  Card,
  CardContent,
  CardHeader,
  CardFooter,
} from "@/components/ui/card";

const SkeletonLoader: React.FC = () => {
  return (
    <div className="grid gap-6">
      {[...Array(3)].map((_, i) => (
        <Card key={i} className="overflow-hidden">
          <CardHeader className="bg-muted/50 p-4">
            <div className="h-5 w-3/4 bg-muted rounded animate-pulse"></div>
          </CardHeader>
          <CardContent className="p-4 space-y-3">
            <div className="h-4 w-full bg-muted rounded animate-pulse"></div>
            <div className="h-4 w-5/6 bg-muted rounded animate-pulse"></div>
            <div className="h-4 w-full bg-muted rounded animate-pulse"></div>
            <div className="h-4 w-3/4 bg-muted rounded animate-pulse"></div>
          </CardContent>
          <CardFooter className="bg-muted/50 p-3 flex justify-between items-center">
            <div className="h-4 w-1/3 bg-muted rounded animate-pulse"></div>
            <div className="h-6 w-1/4 bg-muted rounded-full animate-pulse"></div>
          </CardFooter>
        </Card>
      ))}
    </div>
  );
};

export default SkeletonLoader;
