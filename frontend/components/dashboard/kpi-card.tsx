"use client";

import { TrendingUp, TrendingDown } from 'lucide-react';
import { Card } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";

interface KPICardProps {
  title: string;
  value: string;
  trend: { value: number; isPositive: boolean };
  badge: { label: string; variant: "success" | "warning" };
  description: string;
}

export default function KPICard({ title, value, trend, badge, description }: KPICardProps) {
  const badgeVariants = {
    success: "bg-success/20 text-success border-success/30 border",
    warning: "bg-warning/20 text-warning border-warning/30 border",
  };

  return (
    <Card className="card-gradient relative overflow-hidden border-border bg-card p-6 transition-all duration-200 hover:border-primary/30 hover:shadow-md">
      {/* Background gradient accent */}
      <div className="absolute inset-0 bg-gradient-to-br from-primary/5 via-transparent to-transparent pointer-events-none" />

      <div className="relative z-10">
        {/* Header with title and badge */}
        <div className="flex items-start justify-between mb-4">
          <h3 className="text-sm font-medium text-muted-foreground">{title}</h3>
          <Badge className={badgeVariants[badge.variant]} variant="outline">
            {badge.label}
          </Badge>
        </div>

        {/* Main value */}
        <div className="mb-4">
          <p className="text-3xl font-bold text-foreground">{value}</p>
        </div>

        {/* Trend indicator and description */}
        <div className="flex items-center justify-between pt-4 border-t border-border">
          <span className="text-xs text-muted-foreground">{description}</span>
          <div className={`flex items-center gap-1 text-xs font-medium ${trend.isPositive ? "text-success" : "text-destructive"}`}>
            {trend.isPositive ? (
              <TrendingUp className="h-4 w-4" />
            ) : (
              <TrendingDown className="h-4 w-4" />
            )}
            <span>{trend.value}%</span>
          </div>
        </div>
      </div>
    </Card>
  );
}
