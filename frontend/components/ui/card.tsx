"use client";

import * as React from "react";

export interface CardProps extends React.HTMLAttributes<HTMLDivElement> {}

const Card = React.forwardRef<HTMLDivElement, CardProps>(
  ({ className = "", ...props }, ref) => {
    return (
      <div
        ref={ref}
        className={`bg-card border border-border rounded-lg shadow-sm transition-all duration-200 ${className}`}
        {...props}
      />
    );
  }
);
Card.displayName = "Card";

export { Card };
