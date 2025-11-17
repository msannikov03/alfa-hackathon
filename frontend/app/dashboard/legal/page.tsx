"use client";
import { useState } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { Zap, AlertCircle, Loader2 } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Alert, AlertDescription } from "@/components/ui/alert";
import api from "@/lib/api";

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

  const { data: updates, isLoading: isLoadingUpdates } = useQuery({
    queryKey: ["legalUpdates"],
    queryFn: () => api.get("/legal/updates").then((res) => res.data),
  });

  const scanMutation = useMutation({
    mutationFn: () => api.post("/legal/scan"),
    onSuccess: () => {
      setScanStarted(true);
      setTimeout(() => setScanStarted(false), 5000);
      setTimeout(() => {
        queryClient.invalidateQueries({ queryKey: ["legalUpdates"] });
      }, 5000);
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
