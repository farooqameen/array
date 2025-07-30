import * as React from "react";
import { cva, type VariantProps } from "class-variance-authority";
import { cn } from "@/lib/utils";

const badgeVariants = cva(
  "inline-flex items-center rounded-md border px-2.5 py-0.5 text-xs font-semibold transition-colors focus:outline-none focus:ring-2 focus:ring-ring focus:ring-offset-2",
  {
    variants: {
      variant: {
        default:
          "border-transparent bg-primary text-primary-foreground shadow hover:bg-primary/80",
        secondary:
          "border-transparent bg-secondary text-secondary-foreground hover:bg-secondary/80",
        destructive:
          "border-transparent bg-destructive text-destructive-foreground shadow hover:bg-destructive/80",
        red:
          "border-transparent shadow " +
          "bg-red-200 dark:bg-red-900 hover:bg-red-200/80 hover:dark:bg-red-900/80",
        blue:
          "border-transparent shadow " +
          "bg-blue-200 dark:bg-blue-900 hover:bg-blue-200/80 hover:dark:bg-blue-900/80",
        purple:
          "border-transparent shadow " +
          "bg-purple-200 dark:bg-purple-900 hover:bg-purple-200/80 hover:dark:bg-purple-900/80",
        green:
          "border-transparent shadow " +
          "bg-green-200 dark:bg-green-900 hover:bg-green-200/80 hover:dark:bg-green-900/80",
        cyan:
          "border-transparent shadow " +
          "bg-cyan-200 dark:bg-cyan-900 hover:bg-cyan-200/80 hover:dark:bg-cyan-900/80",
        amber:
          "border-transparent shadow " +
          "bg-amber-200 dark:bg-amber-900 hover:bg-amber-200/80 hover:dark:bg-amber-900/80",
        pink:
          "border-transparent shadow " +
          "bg-pink-200 dark:bg-pink-900 hover:bg-pink-200/80 hover:dark:bg-pink-900/80",
        gray:
          "border-transparent shadow " +
          "bg-gray-200 dark:bg-gray-900 hover:bg-gray-200/80 hover:dark:bg-gray-900/80",
        emerald:
          "border-transparent shadow " +
          "bg-emerald-200 dark:bg-emerald-900 hover:bg-emerald-200/80 hover:dark:bg-emerald-900/80",
        fuchsia:
          "border-transparent shadow " +
          "bg-fuchsia-200 dark:bg-fuchsia-900 hover:bg-fuchsia-200/80 hover:dark:bg-fuchsia-900/80",
        outline: "text-foreground",
      },
    },
    defaultVariants: {
      variant: "default",
    },
  }
);

interface BadgeProps
  extends React.HTMLAttributes<HTMLDivElement>,
    VariantProps<typeof badgeVariants> {}

function Badge({ className, variant, ...props }: BadgeProps) {
  return (
    <div className={cn(badgeVariants({ variant }), className)} {...props} />
  );
}

export { Badge, badgeVariants };
