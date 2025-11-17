"use client";
import { useEffect, useState } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { Zap, Loader2, CheckCircle2 } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Alert, AlertDescription } from "@/components/ui/alert";
import { Textarea } from "@/components/ui/textarea";
import api from "@/lib/api";
import { getClientUserId } from "@/lib/user";
import type { AxiosError } from "axios";

const ImpactBadge = ({ level }: { level: string }) => {
  const variants: Record<string, "destructive" | "secondary" | "default"> = {
    High: "destructive",
    Medium: "secondary",
    Low: "default",
  };
  return <Badge variant={variants[level] || "default"}>{level}</Badge>;
};

const LegalUpdateCard = ({ update }: { update: any }) => (
  <Card className="p-4">
    <div className="flex justify-between items-start mb-2">
      <h3 className="font-bold text-lg flex-1 pr-2 text-foreground">{update.title}</h3>
      <ImpactBadge level={update.impact_level} />
    </div>
    <p className="text-sm text-muted-foreground mb-3">{update.summary}</p>
    <div className="flex justify-between items-center text-xs text-muted-foreground">
      <span>{update.category}</span>
      <span>{new Date(update.detected_at).toISOString().split("T")[0]}</span>
    </div>
  </Card>
);

export default function LegalPage() {
  const queryClient = useQueryClient();
  const [scanStarted, setScanStarted] = useState(false);
  const [contextDraft, setContextDraft] = useState("");
  const userId = getClientUserId();

  const { data: businessContext, isLoading: isLoadingContext } = useQuery({
    queryKey: ["legalBusinessContext", userId],
    queryFn: async () => {
      try {
        const response = await api.get("/legal/business-context", { params: { user_id: userId } });
        return response.data;
      } catch (error) {
        const axiosError = error as AxiosError;
        if (axiosError.response?.status === 404) {
          return null;
        }
        throw error;
      }
    },
    retry: false,
  });

  /* eslint-disable react-hooks/set-state-in-effect -- hydrating form with server context requires syncing state */
  useEffect(() => {
    if (businessContext?.raw_description) {
      setContextDraft(businessContext.raw_description);
    }
  }, [businessContext?.raw_description]);
  /* eslint-enable react-hooks/set-state-in-effect */

  const { data: updates, isLoading: isLoadingUpdates } = useQuery({
    queryKey: ["legalUpdates", userId],
    queryFn: () => api.get("/legal/updates", { params: { user_id: userId } }).then((res) => res.data),
  });

  const { data: alerts, isLoading: isLoadingAlerts } = useQuery({
    queryKey: ["legalAlerts", userId],
    queryFn: () => api.get("/legal/compliance-alerts", { params: { user_id: userId } }).then((res) => res.data),
    staleTime: 30000,
  });

  const scanMutation = useMutation({
    mutationFn: () => api.post("/legal/scan"),
    onSuccess: () => {
      setScanStarted(true);
      setTimeout(() => setScanStarted(false), 5000);
      setTimeout(() => {
        queryClient.invalidateQueries({ queryKey: ["legalUpdates", userId] });
      }, 5000);
    },
  });

  const updateContextMutation = useMutation({
    mutationFn: () =>
      api
        .post("/legal/business-context", { raw_description: contextDraft })
        .then((res) => res.data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["legalBusinessContext", userId] });
    },
  });

  const completeAlertMutation = useMutation({
    mutationFn: (alertId: string) =>
      api.post(`/legal/compliance-alerts/${alertId}/complete`).then((res) => res.data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["legalAlerts", userId] });
    },
  });

  return (
    <div className="min-h-screen p-4 sm:p-6 lg:p-8 bg-background">
      <div className="max-w-7xl mx-auto">
        <div className="flex justify-between items-center mb-8">
          <h1 className="text-4xl font-bold text-foreground">Мониторинг законодательства</h1>
          <Button
            onClick={() => scanMutation.mutate()}
            disabled={scanMutation.isPending}
            className="gap-2"
          >
            <Zap className="w-4 h-4" />
            {scanMutation.isPending ? "Сканирование..." : "Сканировать обновления"}
          </Button>
        </div>

        {scanStarted && (
          <Alert className="mb-6">
            <Loader2 className="h-4 w-4 animate-spin" />
            <AlertDescription>
              Сканирование законодательных изменений в фоновом режиме...
            </AlertDescription>
          </Alert>
        )}

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
          <Card className="p-6">
            <div className="flex items-center justify-between mb-4">
              <div>
                <p className="text-sm uppercase text-muted-foreground">Контекст бизнеса</p>
                <h2 className="text-2xl font-semibold text-foreground">Настройки мониторинга</h2>
              </div>
              {updateContextMutation.isPending && (
                <Loader2 className="w-4 h-4 animate-spin text-muted-foreground" />
              )}
            </div>
            {isLoadingContext ? (
              <div className="flex items-center gap-2 text-muted-foreground">
                <Loader2 className="w-4 h-4 animate-spin" />
                <span>Загрузка контекста...</span>
              </div>
            ) : (
              <div className="space-y-4">
                {businessContext?.structured_data ? (
                  <div className="grid grid-cols-2 gap-3 text-sm">
                    {Object.entries(businessContext.structured_data).map(([key, value]) => (
                      <div key={key}>
                        <p className="text-muted-foreground capitalize">{key}</p>
                        <p className="font-medium text-foreground">
                          {Array.isArray(value) ? value.join(", ") : String(value)}
                        </p>
                      </div>
                    ))}
                  </div>
                ) : (
                  <p className="text-sm text-muted-foreground">
                    Опишите ваш бизнес, чтобы получать наиболее релевантные правовые обновления.
                  </p>
                )}
                <div className="space-y-2">
                  <Textarea
                    value={contextDraft}
                    onChange={(e) => setContextDraft(e.target.value)}
                    placeholder="Например: Розничная сеть из 12 магазинов одежды в Москве..."
                    rows={5}
                  />
                  <div className="flex justify-end">
                    <Button
                      onClick={() => updateContextMutation.mutate()}
                      disabled={!contextDraft || updateContextMutation.isPending}
                    >
                      Сохранить контекст
                    </Button>
                  </div>
                </div>
              </div>
            )}
          </Card>

          <Card className="p-6">
            <div className="flex items-center justify-between mb-4">
              <div>
                <p className="text-sm uppercase text-muted-foreground">Compliance</p>
                <h2 className="text-2xl font-semibold text-foreground">Требующие внимание задачи</h2>
              </div>
              {isLoadingAlerts && <Loader2 className="w-4 h-4 animate-spin text-muted-foreground" />}
            </div>
            {isLoadingAlerts ? (
              <div className="flex items-center gap-2 text-muted-foreground">
                <Loader2 className="w-4 h-4 animate-spin" />
                <span>Загрузка уведомлений...</span>
              </div>
            ) : alerts && alerts.length > 0 ? (
              <div className="space-y-4">
                {alerts.map((alert: any) => (
                  <Card key={alert.id} className="p-4 border border-muted">
                    <div className="flex items-center justify-between mb-2">
                      <Badge variant={alert.status === "completed" ? "outline" : "secondary"}>
                        {alert.status === "completed" ? "Выполнено" : "В работе"}
                      </Badge>
                      {alert.due_date && (
                        <span className="text-xs text-muted-foreground">
                          Срок: {new Date(alert.due_date).toLocaleDateString("ru-RU")}
                        </span>
                      )}
                    </div>
                    <p className="text-sm text-foreground mb-3">{alert.action_required}</p>
                    {alert.status !== "completed" && (
                      <Button
                        size="sm"
                        variant="outline"
                        className="gap-2"
                        disabled={completeAlertMutation.isPending}
                        onClick={() => completeAlertMutation.mutate(alert.id)}
                      >
                        <CheckCircle2 className="w-4 h-4" />
                        Отметить выполненным
                      </Button>
                    )}
                  </Card>
                ))}
              </div>
            ) : (
              <p className="text-sm text-muted-foreground">
                Задачи отсутствуют. После сканирования и обнаружения важных изменений они появятся здесь.
              </p>
            )}
          </Card>
        </div>

        <div className="space-y-6">
          <h2 className="text-2xl font-semibold text-foreground">Последние обновления</h2>
          <div className="space-y-4">
            {isLoadingUpdates && (
              <div className="flex justify-center py-8">
                <Loader2 className="w-6 h-6 animate-spin" />
              </div>
            )}
            {!isLoadingUpdates && updates?.length === 0 && (
              <Card className="p-6 text-center text-muted-foreground">
                <p>
                  Нет актуальных обновлений. Настройте контекст вашего бизнеса в{" "}
                  <a
                    href="/dashboard/settings"
                    className="text-primary hover:underline"
                  >
                    Настройках
                  </a>{" "}
                  и запустите сканирование.
                </p>
              </Card>
            )}
            {updates?.map((update: any) => (
              <LegalUpdateCard key={update.id} update={update} />
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}
