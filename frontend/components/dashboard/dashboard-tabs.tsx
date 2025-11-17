"use client";

import { useMemo, useState } from "react";
import { useQuery } from "@tanstack/react-query";
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  Legend,
} from "recharts";
import { AxiosError } from "axios";
import { Card } from "@/components/ui/card";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { AlertCircle, TrendingUp, Shield, Loader2, Target } from "lucide-react";
import api from "@/lib/api";
import { getClientUserId } from "@/lib/user";

interface DashboardTabsProps {
  activeTab: string;
  setActiveTab: (tab: string) => void;
}

interface ForecastPoint {
  date: string;
  balance: number;
}

interface CashFlowForecast {
  predicted_data: ForecastPoint[];
  insights?: {
    risks?: { severity: string; message: string }[];
    recommendations?: { message: string }[];
  };
}

interface CompetitorInsights {
  summary: string;
  overall_position: string;
  market_share: string;
  price_index: string;
  growth_rate: string;
  competitor_names: string[];
  benchmarks: Record<string, { us: number; competitor_avg: number }>;
}

interface LegalUpdate {
  id: string;
  title: string;
  summary: string;
  category: string;
  impact_level: string;
  detected_at: string;
}

interface TrendInsight {
  title: string;
  insight_type: string;
  observation: string;
  recommendation?: { action: string; justification: string };
}

const formatCurrency = new Intl.NumberFormat("ru-RU", {
  style: "currency",
  currency: "RUB",
  maximumFractionDigits: 0,
});

const benchmarkLabels: Record<string, string> = {
  pricing: "Цены",
  quality: "Качество",
  service: "Сервис",
  online_presence: "Онлайн",
  customer_satisfaction: "Лояльность",
};

const impactStyles: Record<string, string> = {
  High: "bg-destructive/10 text-destructive border-destructive/30",
  Medium: "bg-warning/10 text-warning border-warning/30",
  Low: "bg-success/10 text-success border-success/30",
};

const loadingCard = (message: string) => (
  <Card className="card-gradient border-border bg-card p-6">
    <div className="flex items-center gap-2 text-muted-foreground">
      <Loader2 className="h-4 w-4 animate-spin" />
      <span>{message}</span>
    </div>
  </Card>
);

const errorCard = (message: string) => (
  <Card className="card-gradient border-border bg-card p-6">
    <div className="flex items-center gap-2 text-destructive">
      <AlertCircle className="h-4 w-4" />
      <span>{message}</span>
    </div>
  </Card>
);

const emptyCard = (message: string) => (
  <Card className="card-gradient border-border bg-card p-6 text-center">
    <p className="text-muted-foreground">{message}</p>
  </Card>
);

export default function DashboardTabs({ activeTab, setActiveTab }: DashboardTabsProps) {
  const [userId] = useState<number>(() => getClientUserId());

  const {
    data: financeForecast,
    isLoading: financeLoading,
    isError: financeError,
  } = useQuery({
    queryKey: ["finance-forecast", userId],
    queryFn: async () => {
      try {
        const response = await api.get<CashFlowForecast>("/v1/finance/forecast", {
          params: { user_id: userId },
        });
        return response.data;
      } catch (error) {
        const axiosError = error as AxiosError;
        if (axiosError.response?.status === 404) {
          return null;
        }
        throw error;
      }
    },
  });

  const {
    data: competitorInsights,
    isLoading: competitorLoading,
    isError: competitorError,
  } = useQuery({
    queryKey: ["competitor-insights", userId],
    queryFn: async () => {
      const response = await api.get<CompetitorInsights>("/v1/competitors/insights", {
        params: { user_id: userId },
      });
      return response.data;
    },
  });

  const {
    data: legalUpdates = [],
    isLoading: legalLoading,
    isError: legalError,
  } = useQuery({
    queryKey: ["legal-updates", userId],
    queryFn: async () => {
      const response = await api.get<LegalUpdate[]>("/v1/legal/updates", {
        params: { user_id: userId },
      });
      return response.data;
    },
  });

  const {
    data: trends = [],
    isLoading: trendsLoading,
    isError: trendsError,
  } = useQuery({
    queryKey: ["trend-insights", userId],
    queryFn: async () => {
      const response = await api.get<TrendInsight[]>("/v1/trends", {
        params: { user_id: userId },
      });
      return response.data;
    },
  });

  const financeChartData = useMemo(() => {
    if (!financeForecast?.predicted_data) return [];
    return financeForecast.predicted_data.map((point) => ({
      label: new Date(point.date).toLocaleDateString("ru-RU", {
        day: "2-digit",
        month: "short",
      }),
      balance: point.balance,
    }));
  }, [financeForecast]);

  const benchmarkChartData = useMemo(() => {
    if (!competitorInsights?.benchmarks) return [];
    return Object.entries(competitorInsights.benchmarks).map(([key, value]) => ({
      metric: benchmarkLabels[key] ?? key,
      us: value.us,
      competitors: value.competitor_avg,
    }));
  }, [competitorInsights]);

  const renderFinance = () => {
    if (financeLoading) return loadingCard("Загружаем прогноз...");
    if (financeError) return errorCard("Не удалось получить финансовый прогноз.");
    if (!financeChartData.length) return emptyCard("Добавьте транзакции, чтобы построить прогноз.");

    const risk = financeForecast?.insights?.risks?.[0];
    const recommendation = financeForecast?.insights?.recommendations?.[0];

    return (
      <>
        <Card className="card-gradient border-border bg-card p-6">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-lg font-semibold text-foreground">Прогноз денежного потока</h3>
            {financeChartData.length > 1 && (
              <span className="text-sm text-muted-foreground">
                {"Диапазон: "}
                {formatCurrency.format(Math.min(...financeChartData.map((p) => p.balance)))}
                {" – "}
                {formatCurrency.format(Math.max(...financeChartData.map((p) => p.balance)))}
              </span>
            )}
          </div>
          <ResponsiveContainer width="100%" height={300}>
            <LineChart data={financeChartData}>
              <CartesianGrid strokeDasharray="3 3" stroke="var(--color-border)" />
              <XAxis dataKey="label" stroke="var(--color-muted-foreground)" />
              <YAxis stroke="var(--color-muted-foreground)" domain={["auto", "auto"]} />
              <Tooltip
                formatter={(value: number) => formatCurrency.format(value)}
                contentStyle={{
                  backgroundColor: "var(--color-card)",
                  border: "1px solid var(--color-border)",
                  borderRadius: "0.75rem",
                }}
              />
              <Line
                type="monotone"
                dataKey="balance"
                stroke="var(--color-primary)"
                dot={{ fill: "var(--color-primary)", r: 3 }}
                activeDot={{ r: 5 }}
                strokeWidth={2}
              />
            </LineChart>
          </ResponsiveContainer>
        </Card>

        <div className="grid gap-4 sm:grid-cols-2">
          <Card className="card-gradient border-primary/20 bg-primary/5 p-4 border">
            <div className="flex gap-3">
              <TrendingUp className="h-5 w-5 text-primary flex-shrink-0 mt-0.5" />
              <div>
                <h4 className="font-semibold text-foreground text-sm mb-1">Рекомендация AI</h4>
                <p className="text-xs text-muted-foreground">
                  {recommendation?.message || "Создайте прогноз, чтобы получить советы"}
                </p>
              </div>
            </div>
          </Card>
          <Card className="card-gradient border-warning/20 bg-warning/5 p-4 border">
            <div className="flex gap-3">
              <AlertCircle className="h-5 w-5 text-warning flex-shrink-0 mt-0.5" />
              <div>
                <h4 className="font-semibold text-foreground text-sm mb-1">Финансовый риск</h4>
                <p className="text-xs text-muted-foreground">
                  {risk?.message || "Критичных рисков не обнаружено"}
                </p>
              </div>
            </div>
          </Card>
        </div>
      </>
    );
  };

  const renderCompetitors = () => {
    if (competitorLoading) return loadingCard("Собираем конкурентную аналитику...");
    if (competitorError) return errorCard("Не удалось загрузить данные по конкурентам.");
    if (!competitorInsights) return emptyCard("Добавьте конкурентов, чтобы начать мониторинг.");

    return (
      <>
        <Card className="card-gradient border-border bg-card p-6">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-lg font-semibold text-foreground">Рыночные показатели</h3>
            <span className={`text-sm font-medium ${competitorInsights.overall_position === "Сильная" ? "text-success" : "text-warning"}`}>
              {competitorInsights.overall_position}
            </span>
          </div>

          {benchmarkChartData.length ? (
            <ResponsiveContainer width="100%" height={300}>
              <LineChart data={benchmarkChartData}>
                <CartesianGrid strokeDasharray="3 3" stroke="var(--color-border)" />
                <XAxis dataKey="metric" stroke="var(--color-muted-foreground)" />
                <YAxis stroke="var(--color-muted-foreground)" domain={[0, 100]} />
                <Tooltip
                  contentStyle={{
                    backgroundColor: "var(--color-card)",
                    border: "1px solid var(--color-border)",
                    borderRadius: "0.75rem",
                  }}
                />
                <Legend />
                <Line type="monotone" dataKey="us" stroke="var(--color-primary)" strokeWidth={2} />
                <Line type="monotone" dataKey="competitors" stroke="var(--color-secondary)" strokeWidth={2} />
              </LineChart>
            </ResponsiveContainer>
          ) : (
            <p className="text-sm text-muted-foreground">Недостаточно данных для построения сравнения.</p>
          )}
        </Card>

        <div className="grid gap-4 sm:grid-cols-2">
          <Card className="card-gradient border-primary/20 bg-primary/5 p-4 border">
            <div className="flex gap-3">
              <Target className="h-5 w-5 text-primary flex-shrink-0 mt-0.5" />
              <div>
                <h4 className="font-semibold text-foreground text-sm mb-1">Краткое резюме</h4>
                <p className="text-xs text-muted-foreground">{competitorInsights.summary}</p>
              </div>
            </div>
          </Card>
          <Card className="card-gradient border-warning/20 bg-warning/5 p-4 border">
            <div className="flex gap-3">
              <AlertCircle className="h-5 w-5 text-warning flex-shrink-0 mt-0.5" />
              <div>
                <h4 className="font-semibold text-foreground text-sm mb-1">Метрики рынка</h4>
                <p className="text-xs text-muted-foreground">
                  Доля: {competitorInsights.market_share} • Цена: {competitorInsights.price_index} • Рост: {competitorInsights.growth_rate}
                </p>
              </div>
            </div>
          </Card>
        </div>
      </>
    );
  };

  const renderLegal = () => {
    if (legalLoading) return loadingCard("Загружаем юридические новости...");
    if (legalError) return errorCard("Не удалось получить юридические обновления.");
    if (!legalUpdates.length) return emptyCard("Свежих юридических обновлений пока нет.");

    return (
      <div className="space-y-4">
        {legalUpdates.slice(0, 5).map((update) => (
          <Card key={update.id} className="card-gradient border-border bg-card p-4">
            <div className="flex items-start justify-between gap-3">
              <div>
                <div className="flex items-center gap-2 mb-1">
                  <Shield className="h-4 w-4 text-primary" />
                  <p className="text-xs text-muted-foreground">
                    {new Date(update.detected_at).toLocaleDateString("ru-RU", {
                      day: "2-digit",
                      month: "short",
                    })}
                  </p>
                </div>
                <h4 className="font-semibold text-sm text-foreground mb-2">{update.title}</h4>
                <p className="text-sm text-muted-foreground">{update.summary}</p>
              </div>
              <span className={`text-xs px-2 py-1 rounded-full border ${impactStyles[update.impact_level] || "bg-muted text-muted-foreground border-border"}`}>
                {update.impact_level}
              </span>
            </div>
            <p className="text-xs text-muted-foreground mt-2">Категория: {update.category}</p>
          </Card>
        ))}
      </div>
    );
  };

  const renderTrends = () => {
    if (trendsLoading) return loadingCard("Готовим стратегические инсайты...");
    if (trendsError) return errorCard("Не удалось получить тренды.");
    if (!trends.length) return emptyCard("Тренды появятся после накопления данных.");

    return (
      <div className="space-y-4">
        {trends.map((trend, index) => (
          <Card key={`${trend.title}-${index}`} className="card-gradient border-border bg-card p-4">
            <div className="flex items-center gap-2 text-xs text-muted-foreground mb-2">
              <span className="font-semibold text-primary">{trend.insight_type}</span>
              <span>•</span>
              <span>#{index + 1}</span>
            </div>
            <h4 className="font-semibold text-foreground mb-2">{trend.title}</h4>
            <p className="text-sm text-muted-foreground mb-3">{trend.observation}</p>
            {trend.recommendation && (
              <div className="rounded-lg border border-primary/20 bg-primary/5 p-3 text-sm">
                <p className="font-medium text-foreground mb-1">Действие: {trend.recommendation.action}</p>
                <p className="text-muted-foreground">{trend.recommendation.justification}</p>
              </div>
            )}
          </Card>
        ))}
      </div>
    );
  };

  return (
    <Tabs value={activeTab} onValueChange={setActiveTab} className="w-full">
      <TabsList className="grid w-full grid-cols-4 bg-muted/50 border border-border rounded-lg p-1 mb-6">
        <TabsTrigger
          value="finance"
          className="data-[state=active]:bg-card data-[state=active]:text-foreground data-[state=active]:shadow-sm rounded-md text-xs sm:text-sm"
        >
          Finance
        </TabsTrigger>
        <TabsTrigger
          value="competitors"
          className="data-[state=active]:bg-card data-[state=active]:text-foreground data-[state=active]:shadow-sm rounded-md text-xs sm:text-sm"
        >
          Competitors
        </TabsTrigger>
        <TabsTrigger
          value="legal"
          className="data-[state=active]:bg-card data-[state=active]:text-foreground data-[state=active]:shadow-sm rounded-md text-xs sm:text-sm"
        >
          Legal
        </TabsTrigger>
        <TabsTrigger
          value="trends"
          className="data-[state=active]:bg-card data-[state=active]:text-foreground data-[state=active]:shadow-sm rounded-md text-xs sm:text-sm"
        >
          Trends
        </TabsTrigger>
      </TabsList>

      <TabsContent value="finance" className="space-y-6">
        {renderFinance()}
      </TabsContent>

      <TabsContent value="competitors" className="space-y-6">
        {renderCompetitors()}
      </TabsContent>

      <TabsContent value="legal" className="space-y-6">
        {renderLegal()}
      </TabsContent>

      <TabsContent value="trends" className="space-y-6">
        {renderTrends()}
      </TabsContent>
    </Tabs>
  );
}
