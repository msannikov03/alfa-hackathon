"use client";

import { Loader2 } from "lucide-react";
import * as React from "react";

export interface ButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  isLoading?: boolean;
}

const NeonButton = React.forwardRef<HTMLButtonElement, ButtonProps>(
  ({ className, children, isLoading, ...props }, ref) => {
    return (
      <button
        className={`px-5 py-2 rounded-lg font-semibold text-white bg-cyan-500/10 border border-cyan-500/50
                   hover:bg-cyan-500/20 hover:shadow-cyan-500/20 hover:shadow-lg transition-all duration-300 
                   transform hover:scale-105 flex items-center justify-center gap-2 disabled:opacity-50 disabled:cursor-not-allowed ${className}`}
        ref={ref}
        disabled={isLoading}
        {...props}
      >
        {isLoading ? <Loader2 className="animate-spin" /> : children}
      </button>
    );
  }
);
NeonButton.displayName = "NeonButton";

export { NeonButton };
