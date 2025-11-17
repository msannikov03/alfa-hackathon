"use client";

import { useState } from "react";
import { Check, X, Loader2 } from 'lucide-react';
import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";

interface Action {
  id: string;
  title: string;
  description: string;
  impact: "high" | "medium" | "low";
  loading?: boolean;
}

const initialActions: Action[] = [
  {
    id: "1",
    title: "Increase Marketing Budget",
    description: "AI detected high ROI opportunity in Q1. Allocate +$25K.",
    impact: "high",
  },
  {
    id: "2",
    title: "Negotiate Vendor Contract",
    description: "Auto-draft renewal with 12% cost reduction.",
    impact: "medium",
  },
  {
    id: "3",
    title: "Schedule Compliance Review",
    description: "Quarterly audit check for tax preparation.",
    impact: "low",
  },
];

const impactColors = {
  high: "bg-destructive/20 text-destructive border-destructive/30",
  medium: "bg-warning/20 text-warning border-warning/30",
  low: "bg-muted text-muted-foreground border-border",
};

export default function AutonomousActions() {
  const [actions, setActions] = useState(initialActions);

  const handleApprove = (id: string) => {
    setActions((prev) =>
      prev.map((action) =>
        action.id === id ? { ...action, loading: true } : action
      )
    );

    // Simulate API call
    setTimeout(() => {
      setActions((prev) => prev.filter((action) => action.id !== id));
    }, 1500);
  };

  const handleDecline = (id: string) => {
    setActions((prev) => prev.filter((action) => action.id !== id));
  };

  return (
    <div>
      <h2 className="text-2xl font-bold text-foreground mb-6">Autonomous Actions Queue</h2>
      <div className="space-y-4">
        {actions.length === 0 ? (
          <Card className="card-gradient border-border bg-card p-8 text-center">
            <p className="text-muted-foreground">All actions processed. Great job!</p>
          </Card>
        ) : (
          actions.map((action) => (
            <Card
              key={action.id}
              className="card-gradient border-border bg-card p-4 transition-all duration-200 hover:border-primary/30"
            >
              <div className="space-y-3">
                {/* Header */}
                <div className="flex items-start justify-between gap-2">
                  <h3 className="font-semibold text-foreground text-sm">{action.title}</h3>
                  <Badge
                    className={`${impactColors[action.impact]} border`}
                    variant="outline"
                  >
                    {action.impact.charAt(0).toUpperCase() + action.impact.slice(1)} Impact
                  </Badge>
                </div>

                {/* Description */}
                <p className="text-xs text-muted-foreground">{action.description}</p>

                {/* Action Buttons */}
                <div className="flex gap-2 pt-2">
                  <Button
                    onClick={() => handleApprove(action.id)}
                    disabled={action.loading}
                    size="sm"
                    className="flex-1 gap-2 bg-success hover:bg-success/90 text-white font-medium"
                  >
                    {action.loading ? (
                      <>
                        <Loader2 className="h-4 w-4 animate-spin" />
                        Processing...
                      </>
                    ) : (
                      <>
                        <Check className="h-4 w-4" />
                        Approve
                      </>
                    )}
                  </Button>
                  <Button
                    onClick={() => handleDecline(action.id)}
                    disabled={action.loading}
                    variant="outline"
                    size="sm"
                    className="flex-1 gap-2 border-border hover:bg-destructive/10 hover:text-destructive"
                  >
                    <X className="h-4 w-4" />
                    Decline
                  </Button>
                </div>
              </div>
            </Card>
          ))
        )}
      </div>
    </div>
  );
}
