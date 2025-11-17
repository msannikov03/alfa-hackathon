"use client";
import { useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { Zap, AlertTriangle, CheckCircle, Lightbulb } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import api from "@/lib/api";
import { getClientUserId } from "@/lib/user";

const InsightCard = ({
  children,
  className = "",
}: {
  children: React.ReactNode;
  className?: string;
}) => (
  <Card
    className={`p-6 hover:shadow-md transition-all duration-300 ${className}`}
  >
    {children}
  </Card>
);

const InsightTypeIcon = ({ type }: { type: string }) => {
  switch (type) {
    case "Opportunity":
    case "Возможность":
      return <Lightbulb className="w-5 h-5 text-green-600" />;
    case "Threat":
    case "Угроза":
      return <AlertTriangle className="w-5 h-5 text-red-600" />;
    case "Efficiency Improvement":
    case "Улучшение эффективности":
      return <CheckCircle className="w-5 h-5 text-blue-600" />;
    default:
      return <Zap className="w-5 h-5 text-gray-600" />;
  }
};

type PageState = "initial" | "analyzing" | "results";

export default function TrendsPage() {
  const [pageState, setPageState] = useState<PageState>("initial");
  const [analysisError, setAnalysisError] = useState<string | null>(null);
  const userId = getClientUserId();

  const {
    data: trends,
    isLoading,
    refetch,
  } = useQuery({
    queryKey: ["trends", userId],
    queryFn: () => api.get("/trends", { params: { user_id: userId } }).then((res) => res.data),
    enabled: false,
  });

  const handleAnalyze = async () => {
    setAnalysisError(null);
    setPageState("analyzing");
    const result = await refetch({ throwOnError: false });
    if (result.error) {
      setAnalysisError("Не удалось построить тренды. Попробуйте снова через минуту.");
      setPageState("initial");
      return;
    }
    setPageState("results");
  };

  const renderInitialState = () => (
    <div className="flex items-center justify-center min-h-96">
      <Button
        size="lg"
        onClick={handleAnalyze}
        disabled={isLoading}
        className="gap-2"
      >
        <Zap className="w-5 h-5" />
        {isLoading ? "Анализ..." : "Начать анализ трендов"}
      </Button>
    </div>
  );

  const renderAnalyzingState = () => (
    <div className="flex items-center justify-center min-h-96">
      <div className="text-center">
        <Zap className="w-12 h-12 text-primary animate-pulse mx-auto mb-4" />
        <p className="text-lg text-muted-foreground">Анализирую тренды...</p>
      </div>
    </div>
  );

  const renderResultsState = () => (
    <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
      {trends?.map((trend: any, index: number) => (
        <InsightCard key={index}>
          <div className="flex items-start justify-between mb-3">
            <div className="flex-1 pr-2">
              <p className="text-xs uppercase text-muted-foreground mb-1">{trend.insight_type}</p>
              <h3 className="text-lg font-bold text-foreground">{trend.title}</h3>
            </div>
            <InsightTypeIcon type={trend.insight_type} />
          </div>
          <p className="text-sm text-muted-foreground mb-4">
            &laquo;{trend.observation}&raquo;
          </p>
          <div className="space-y-2 pt-4 border-t">
            <div className="flex items-center gap-2">
              <Badge variant="secondary">Действие</Badge>
              <span className="text-sm text-foreground">
                {trend.recommendation?.action || "Без рекомендации"}
              </span>
            </div>
            {trend.recommendation?.justification && (
              <p className="text-xs text-muted-foreground italic">
                {trend.recommendation.justification}
              </p>
            )}
          </div>
        </InsightCard>
      ))}
    </div>
  );

  return (
    <div className="min-h-screen p-4 sm:p-6 lg:p-8 bg-background">
      <div className="max-w-7xl mx-auto">
        <div className="flex justify-between items-center mb-8">
          <h1 className="text-4xl font-bold text-foreground">Стратегические тренды</h1>
          {pageState === "results" && (
            <Button variant="outline" onClick={() => setPageState("initial")} className="text-foreground border-border hover:bg-accent">
              Анализировать снова
            </Button>
          )}
        </div>
        {analysisError && (
          <Card className="p-4 mb-6 bg-destructive/5 border-destructive/30 text-sm text-destructive">
            {analysisError}
          </Card>
        )}
        {pageState === "initial" && renderInitialState()}
        {pageState === "analyzing" && renderAnalyzingState()}
        {pageState === "results" && renderResultsState()}
      </div>
    </div>
  );
}
