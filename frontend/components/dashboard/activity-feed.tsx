"use client";

import { CheckCircle, AlertCircle, Clock, Zap } from 'lucide-react';
import { Card } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";

interface ActivityItem {
  id: string;
  action: string;
  status: "approved" | "pending" | "needs-review";
  timestamp: string;
  description: string;
  icon: React.ReactNode;
}

const activities: ActivityItem[] = [
  {
    id: "1",
    action: "Competitor Price Drop Detected",
    status: "approved",
    timestamp: "2 minutes ago",
    description: "TechCorp reduced pricing by 15% on enterprise tier",
    icon: <Zap className="h-5 w-5" />,
  },
  {
    id: "2",
    action: "Compliance Alert - Tax Deadline",
    status: "needs-review",
    timestamp: "15 minutes ago",
    description: "Quarterly tax filing due in 5 days",
    icon: <AlertCircle className="h-5 w-5" />,
  },
  {
    id: "3",
    action: "Cash Flow Projection Updated",
    status: "pending",
    timestamp: "42 minutes ago",
    description: "AI model suggests expanding marketing budget",
    icon: <Clock className="h-5 w-5" />,
  },
  {
    id: "4",
    action: "Market Trend Analysis Complete",
    status: "approved",
    timestamp: "1 hour ago",
    description: "Growing demand in Q4 for product category B",
    icon: <CheckCircle className="h-5 w-5" />,
  },
];

const statusConfig = {
  approved: {
    badge: "bg-success/20 text-success border-success/30 border",
    label: "Approved",
  },
  pending: {
    badge: "bg-warning/20 text-warning border-warning/30 border",
    label: "Pending",
  },
  "needs-review": {
    badge: "bg-destructive/20 text-destructive border-destructive/30 border",
    label: "Needs Review",
  },
};

export default function ActivityFeed() {
  return (
    <div className="space-y-4">
      {activities.map((activity) => (
        <Card
          key={activity.id}
          className="card-gradient border-border bg-card p-4 transition-all duration-200 hover:border-primary/30 hover:shadow-sm"
        >
          <div className="flex gap-4">
            {/* Icon */}
            <div className="flex-shrink-0 mt-1 p-2 rounded-lg bg-muted flex items-center justify-center">
              <div className="text-muted-foreground">{activity.icon}</div>
            </div>

            {/* Content */}
            <div className="flex-1 min-w-0">
              <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-2 mb-2">
                <h4 className="font-semibold text-foreground text-sm">{activity.action}</h4>
                <Badge
                  className={statusConfig[activity.status].badge}
                  variant="outline"
                >
                  {statusConfig[activity.status].label}
                </Badge>
              </div>
              <p className="text-sm text-muted-foreground mb-2">{activity.description}</p>
              <p className="text-xs text-muted-foreground">{activity.timestamp}</p>
            </div>
          </div>
        </Card>
      ))}
    </div>
  );
}
