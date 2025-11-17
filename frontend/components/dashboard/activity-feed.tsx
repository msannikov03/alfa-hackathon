"use client";

import { useMemo, useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { CheckCircle, AlertCircle, Clock, Zap, Loader2 } from "lucide-react";
import { Card } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import api from "@/lib/api";
import { getClientUserId } from "@/lib/user";

type FeedStatus = "approved" | "pending" | "needs-review";

interface RecentAction {
  id: number;
  action_type: string;
  description: string | null;
  required_approval: boolean;
  was_approved: boolean | null;
  executed_at: string;
}

const statusConfig: Record<FeedStatus, { badge: string; label: string }> = {
  approved: {
    badge: "bg-success/20 text-success border-success/30 border",
    label: "Выполнено",
  },
  pending: {
    badge: "bg-warning/20 text-warning border-warning/30 border",
    label: "Ожидает решения",
  },
  "needs-review": {
    badge: "bg-destructive/20 text-destructive border-destructive/30 border",
    label: "Отклонено",
  },
};

const resolveStatus = (action: RecentAction): FeedStatus => {
  if (action.was_approved === false) {
    return "needs-review";
  }
  if (action.was_approved === null && action.required_approval) {
    return "pending";
  }
  return "approved";
};

const resolveIcon = (status: FeedStatus) => {
  if (status === "approved") return <CheckCircle className="h-5 w-5" />;
  if (status === "pending") return <Clock className="h-5 w-5" />;
  return <AlertCircle className="h-5 w-5" />;
};

export default function ActivityFeed() {
  const [userId] = useState<number>(() => getClientUserId());

  const {
    data: actions = [],
    isLoading,
    isError,
  } = useQuery({
    queryKey: ["recent-actions", userId],
    queryFn: async () => {
      const response = await api.get<RecentAction[]>("/v1/actions/recent", {
        params: { user_id: userId, limit: 10 },
      });
      return response.data;
    },
  });

  const timelineItems = useMemo(
    () =>
      actions.map((action) => {
        const status = resolveStatus(action);
        return {
          id: action.id,
          title: action.action_type.replace(/_/g, " "),
          description: action.description || "Описание недоступно",
          timestamp: new Date(action.executed_at).toLocaleString("ru-RU"),
          status,
          icon: resolveIcon(status),
        };
      }),
    [actions]
  );

  if (isLoading) {
    return (
      <Card className="card-gradient border-border bg-card p-6 text-center">
        <div className="flex items-center justify-center gap-2 text-muted-foreground">
          <Loader2 className="h-4 w-4 animate-spin" />
          <span>Загружаем активность...</span>
        </div>
      </Card>
    );
  }

  if (isError) {
    return (
      <Card className="card-gradient border-border bg-card p-6">
        <div className="flex items-center gap-2 text-destructive">
          <AlertCircle className="h-4 w-4" />
          <p>Не удалось получить ленту действий.</p>
        </div>
      </Card>
    );
  }

  if (!timelineItems.length) {
    return (
      <Card className="card-gradient border-border bg-card p-6 text-center">
        <p className="text-muted-foreground">
          Пока активности нет — автопилот готовится к следующим действиям.
        </p>
      </Card>
    );
  }

  return (
    <div className="space-y-4">
      {timelineItems.map((activity) => (
        <Card
          key={activity.id}
          className="card-gradient border-border bg-card p-4 transition-all duration-200 hover:border-primary/30 hover:shadow-sm"
        >
          <div className="flex gap-4">
            <div className="flex-shrink-0 mt-1 p-2 rounded-lg bg-muted flex items-center justify-center">
              <div className="text-muted-foreground">{activity.icon}</div>
            </div>
            <div className="flex-1 min-w-0">
              <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-2 mb-2">
                <h4 className="font-semibold text-foreground text-sm">{activity.title}</h4>
                <Badge className={statusConfig[activity.status].badge} variant="outline">
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
