    "use client";

    import { useState } from "react";
    import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
    import { Check, X, Loader2, AlertCircle } from "lucide-react";
    import { Card } from "@/components/ui/card";
    import { Button } from "@/components/ui/button";
    import { Badge } from "@/components/ui/badge";
    import api from "@/lib/api";

    interface PendingAction {
      id: number;
      action_type: string;
      description: string | null;
      impact_amount: number | null;
      required_approval: boolean;
      was_approved: boolean | null;
      executed_at: string;
    }

    const impactColors: Record<string, string> = {
      high: "bg-destructive/20 text-destructive border-destructive/30",
      medium: "bg-warning/20 text-warning border-warning/30",
      low: "bg-muted text-muted-foreground border-border",
    };

    const getImpactLevel = (action: PendingAction) => {
      const amount = action.impact_amount ?? 0;
      if (amount >= 20000) return "high";
      if (amount >= 5000) return "medium";
      return "low";
    };

    const getInitialUserId = () => {
      if (typeof window === "undefined") {
        return 1;
      }
      const stored = localStorage.getItem("user_id");
      return stored ? parseInt(stored, 10) : 1;
    };

    export default function AutonomousActions() {
      const [userId] = useState<number>(() => getInitialUserId());
      const [processingId, setProcessingId] = useState<number | null>(null);
      const queryClient = useQueryClient();

      const {
        data: actions = [],
        isLoading,
        isError,
      } = useQuery({
        queryKey: ["pending-actions", userId],
        queryFn: async () => {
          const response = await api.get<PendingAction[]>("/v1/actions/pending", {
            params: { user_id: userId },
          });
          return response.data;
        },
      });

      const decisionMutation = useMutation({
        mutationFn: async ({
          actionId,
          decision,
        }: {
          actionId: number;
          decision: "approve" | "decline";
        }) => {
          setProcessingId(actionId);
          if (decision === "approve") {
            return api.post(`/v1/actions/approve/${actionId}`);
          }
          return api.post(`/v1/actions/decline/${actionId}`);
        },
        onSuccess: () => {
          queryClient.invalidateQueries({ queryKey: ["pending-actions", userId] });
          queryClient.invalidateQueries({ queryKey: ["recent-actions", userId] });
        },
        onSettled: () => setProcessingId(null),
      });

      const handleDecision = (actionId: number, decision: "approve" | "decline") => {
        decisionMutation.mutate({ actionId, decision });
      };

      const renderContent = () => {
        if (isLoading) {
          return (
            <Card className="card-gradient border-border bg-card p-8 text-center">
              <div className="flex items-center justify-center gap-2 text-muted-foreground">
                <Loader2 className="h-4 w-4 animate-spin" />
                <span>Загружаем действия...</span>
              </div>
            </Card>
          );
        }

        if (isError) {
          return (
            <Card className="card-gradient border-border bg-card p-6">
              <div className="flex items-center gap-2 text-destructive">
                <AlertCircle className="h-4 w-4" />
                <p>Не удалось загрузить очередь действий. Попробуйте позже.</p>
              </div>
            </Card>
          );
        }

        if (!actions.length) {
          return (
            <Card className="card-gradient border-border bg-card p-8 text-center">
              <p className="text-muted-foreground">Очередь пуста — все действия обработаны.</p>
            </Card>
          );
        }

        return actions.map((action) => {
          const impactLevel = getImpactLevel(action);

          return (
            <Card
              key={action.id}
              className="card-gradient border-border bg-card p-4 transition-all duration-200 hover:border-primary/30"
            >
              <div className="space-y-3">
                <div className="flex items-start justify-between gap-2">
                  <div>
                    <h3 className="font-semibold text-foreground text-sm">
                      {action.action_type.replace(/_/g, " ")}
                    </h3>
                    <p className="text-xs text-muted-foreground mt-1">
                      {new Date(action.executed_at).toLocaleString("ru-RU")}
                    </p>
                  </div>
                  <Badge className={`${impactColors[impactLevel]} border`} variant="outline">
                    {impactLevel === "high"
                      ? "Высокий"
                      : impactLevel === "medium"
                      ? "Средний"
                      : "Низкий"}
                  </Badge>
                </div>
                <p className="text-sm text-muted-foreground">
                  {action.description || "Описание недоступно"}
                </p>

                <div className="flex flex-wrap items-center gap-3 text-xs text-muted-foreground">
                  {typeof action.impact_amount === "number" && (
                    <span>
                      Потенциальное влияние:{" "}
                      <strong>
                        {action.impact_amount.toLocaleString("ru-RU", {
                          style: "currency",
                          currency: "RUB",
                          maximumFractionDigits: 0,
                        })}
                      </strong>
                    </span>
                  )}
                  {action.required_approval && <Badge variant="secondary">Требует согласования</Badge>}
                </div>

                <div className="flex gap-2 pt-2">
                  <Button
                    onClick={() => handleDecision(action.id, "approve")}
                    disabled={processingId === action.id && decisionMutation.isPending}
                    size="sm"
                    className="flex-1 gap-2 bg-success hover:bg-success/90 text-white font-medium"
                  >
                    {processingId === action.id && decisionMutation.isPending ? (
                      <>
                        <Loader2 className="h-4 w-4 animate-spin" />
                        Обработка...
                      </>
                    ) : (
                      <>
                        <Check className="h-4 w-4" />
                        Одобрить
                      </>
                    )}
                  </Button>
                  <Button
                    onClick={() => handleDecision(action.id, "decline")}
                    disabled={processingId === action.id && decisionMutation.isPending}
                    variant="outline"
                    size="sm"
                    className="flex-1 gap-2 border-border hover:bg-destructive/10 hover:text-destructive"
                  >
                    <X className="h-4 w-4" />
                    Отклонить
                  </Button>
                </div>
              </div>
            </Card>
          );
        });
      };

      return (
        <div>
          <h2 className="text-2xl font-bold text-foreground mb-6">Autonomous Actions Queue</h2>
          <div className="space-y-4">{renderContent()}</div>
        </div>
      );
    }
