"use client";

import { useMemo, useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { AxiosError } from "axios";
import { TrendingUp } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import KPICard from "@/components/dashboard/kpi-card";
import ActivityFeed from "@/components/dashboard/activity-feed";
import AutonomousActions from "@/components/dashboard/autonomous-actions";
import DashboardTabs from "@/components/dashboard/dashboard-tabs";
import api from "@/lib/api";
import { getClientUserId } from "@/lib/user";

interface PerformanceMetrics {
  total_actions: number;
  approved_actions: number;
  pending_approvals: number;
  time_saved_hours: number;
  automation_rate: number;
  decisions_made: number;
}

interface SavingsMetrics {
  total_actions: number;
  time_saved_hours: number;
  money_saved_rub: number;
  avg_action_value: number;
}

interface ForecastPoint {
  date: string;
  balance: number;
}

interface CashFlowForecast {
  predicted_data: ForecastPoint[];
}

interface ComplianceAlert {
  id: string;
  status: string;
  action_required: string;
  due_date: string | null;
}

const formatCurrency = new Intl.NumberFormat("ru-RU", {
  style: "currency",
  currency: "RUB",
  maximumFractionDigits: 0,
});

export default function MainDashboard() {
  const [activeTab, setActiveTab] = useState("finance");
  const [userId] = useState<number>(() => getClientUserId());

  const {
    data: performanceMetrics,
    isLoading: performanceLoading,
  } = useQuery({
    queryKey: ["performance-metrics", userId],
    queryFn: async () => {
      const response = await api.get<PerformanceMetrics>("/v1/metrics/performance", {
        params: { user_id: userId },
      });
      return response.data;
    },
  });

  const { data: savingsMetrics, isLoading: savingsLoading } = useQuery({
    queryKey: ["savings-metrics", userId],
    queryFn: async () => {
      const response = await api.get<SavingsMetrics>("/v1/metrics/savings", {
        params: { user_id: userId },
      });
      return response.data;
    },
  });

  const { data: financeForecast, isLoading: forecastLoading } = useQuery({
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
    retry: false,
  });

  const { data: complianceAlerts = [], isLoading: alertsLoading } = useQuery({
    queryKey: ["compliance-alerts", userId],
    queryFn: async () => {
      const response = await api.get<ComplianceAlert[]>("/v1/legal/compliance-alerts", {
        params: { user_id: userId },
      });
      return response.data;
    },
  });

  const kpis = useMemo(() => {
    const balanceToday = financeForecast?.predicted_data?.[0]?.balance ?? null;
    const balanceTomorrow = financeForecast?.predicted_data?.[1]?.balance ?? null;
    const balanceChange =
      balanceToday !== null && balanceTomorrow !== null ? balanceTomorrow - balanceToday : 0;
    const balanceTrend =
      balanceToday !== null && balanceToday !== 0 ? (balanceChange / Math.abs(balanceToday)) * 100 : 0;

    const decisionsMade = performanceMetrics?.decisions_made ?? 0;
    const pendingApprovals = performanceMetrics?.pending_approvals ?? 0;
    const automationRate = performanceMetrics?.automation_rate ?? 0;

    const pendingAlerts = complianceAlerts.filter((alert) => alert.status !== "completed");
    const nextDue = pendingAlerts
      .map((alert) => alert.due_date)
      .filter(Boolean)
      .sort()
      .at(0);

    const runwayPoints = financeForecast?.predicted_data ?? [];
    const runwayDays = (() => {
      if (!runwayPoints.length) return 0;
      const negativeIndex = runwayPoints.findIndex((point) => point.balance < 0);
      if (negativeIndex === -1) {
        return runwayPoints.length - 1;
      }
      return negativeIndex;
    })();
    const avgDailyChange = (() => {
      if (runwayPoints.length < 2) return 0;
      const first = runwayPoints[0].balance;
      const last = runwayPoints[runwayPoints.length - 1].balance;
      return (last - first) / (runwayPoints.length - 1);
    })();

    const dailyChangeLabel = (() => {
      if (avgDailyChange === 0) {
        return "0 ₽/день";
      }
      const formatted = formatCurrency.format(Math.abs(avgDailyChange));
      return `${avgDailyChange >= 0 ? "+" : "-"}${formatted}/день`;
    })();

    const badgeForAlerts = pendingAlerts.length === 0 ? "success" : pendingAlerts.length > 2 ? "danger" : "warning";

    return [
      {
        title: "Текущий баланс",
        value: balanceToday !== null ? formatCurrency.format(balanceToday) : "—",
        trend: {
          value: Number(balanceTrend.toFixed(1)),
          isPositive: balanceTrend >= 0,
          label: `${balanceTrend >= 0 ? "+" : ""}${balanceTrend.toFixed(1)}%`,
        },
        badge: {
          label: balanceTrend >= 0 ? "Рост" : "Просадка",
          variant: balanceTrend >= 0 ? "success" : "danger",
        } as const,
        description:
          balanceTomorrow !== null
            ? `Прогноз на завтра: ${formatCurrency.format(balanceTomorrow)}`
            : "Загрузите CSV с транзакциями",
      },
      {
        title: "Решения AI",
        value: decisionsMade.toString(),
        trend: {
          value: automationRate,
          isPositive: automationRate >= 50,
          label: `${automationRate.toFixed(1)}%`,
        },
        badge: {
          label: pendingApprovals ? "Нужна проверка" : "Оптимально",
          variant: pendingApprovals ? "warning" : "success",
        } as const,
        description: `Ожидает подтверждения: ${pendingApprovals}`,
      },
      {
        title: "Комплаенс",
        value: pendingAlerts.length.toString(),
        trend: {
          value: pendingAlerts.length,
          isPositive: pendingAlerts.length === 0,
          label: pendingAlerts.length ? `${pendingAlerts.length} активн.` : "0",
        },
        badge: {
          label: pendingAlerts.length ? "Внимание" : "Нет рисков",
          variant: badgeForAlerts,
        } as const,
        description: nextDue ? `Ближайший дедлайн: ${new Date(nextDue).toLocaleDateString("ru-RU")}` : "Все дедлайны закрыты",
      },
      {
        title: "Денежный запас",
        value: runwayDays ? `${runwayDays} дн.` : "—",
        trend: {
          value: avgDailyChange,
          isPositive: avgDailyChange >= 0,
          label: dailyChangeLabel,
        },
        badge: {
          label: runwayDays >= 7 ? "Стабильно" : "Короткий горизонт",
          variant: runwayDays >= 7 ? "success" : "warning",
        } as const,
        description: savingsMetrics
          ? `Сэкономлено временем: ${savingsMetrics.time_saved_hours.toFixed(1)} ч`
          : "Подождите обновления",
      },
    ];
  }, [
    financeForecast,
    performanceMetrics,
    complianceAlerts,
    savingsMetrics,
  ]);

  const kpiLoading = performanceLoading || savingsLoading || forecastLoading || alertsLoading;

  return (
    <div className="min-h-screen bg-background">
      {/* Hero Section */}
      <section className="border-b border-border bg-gradient-to-br from-background via-background to-primary/5 px-6 py-12 sm:px-8 md:py-16">
        <div className="mx-auto max-w-7xl">
          <div className="mb-8 flex items-center gap-3">
            <div className="rounded-lg border border-primary/20 bg-primary/10 p-2.5">
              <TrendingUp className="h-5 w-5 text-primary" />
            </div>
            <span className="text-xs font-semibold uppercase tracking-widest text-primary">
              AI-Powered Control Center
            </span>
          </div>

          <div className="grid gap-6 md:grid-cols-3 md:gap-8 lg:gap-12">
            <div className="md:col-span-2">
              <h1 className="text-4xl font-bold tracking-tight text-foreground sm:text-5xl md:text-6xl mb-4">
                Alfa Business Assistant
              </h1>
              <p className="text-lg text-muted-foreground leading-relaxed max-w-xl">
                Your autonomous AI copilot for smarter decisions. Monitor KPIs, track compliance, analyze competitors, and manage cash flow—all in one place.
              </p>
            </div>

            <div className="flex flex-col gap-3 md:justify-end">
              <Button className="gap-2 bg-primary hover:bg-primary/90 text-primary-foreground font-semibold">
                Start Monitoring
              </Button>
              <Button variant="outline" className="gap-2 border-border hover:bg-muted">
                View Documentation
              </Button>
            </div>
          </div>
        </div>
      </section>

      {/* Main Content */}
      <div className="mx-auto max-w-7xl px-6 py-8 sm:px-8 md:py-12">
        {/* KPI Grid */}
        <section className="mb-12">
          <div className="flex items-center justify-between mb-6">
            <h2 className="text-2xl font-bold text-foreground">Цифры автопилота</h2>
            {kpiLoading && <span className="text-sm text-muted-foreground">Обновляем данные...</span>}
          </div>
          <div className="grid gap-6 sm:grid-cols-2 lg:grid-cols-4">
            {kpis.map((kpi) => (
              <KPICard
                key={kpi.title}
                title={kpi.title}
                value={kpi.value}
                trend={kpi.trend}
                badge={kpi.badge}
                description={kpi.description}
              />
            ))}
          </div>
        </section>

        {/* Tabs and Activity Feed */}
        <div className="grid gap-8 lg:grid-cols-3">
          {/* Main Content Area with Tabs */}
          <div className="lg:col-span-2">
            <DashboardTabs activeTab={activeTab} setActiveTab={setActiveTab} />
          </div>

          {/* Right Sidebar - Autonomous Actions */}
          <div className="lg:col-span-1">
            <AutonomousActions />
          </div>
        </div>

        {/* Activity Feed */}
        <section className="mt-8">
          <h2 className="mb-6 text-2xl font-bold text-foreground">Real-Time Activity Feed</h2>
          <ActivityFeed />
        </section>

        {/* Integration Placeholders */}
        <section className="mt-12 pt-8 border-t border-border">
          <h3 className="mb-6 text-xl font-bold text-foreground">Integration Status</h3>
          <div className="grid gap-4 sm:grid-cols-2">
            <Card className="card-gradient border-border bg-card p-6">
              <div className="flex items-center justify-between">
                <div>
                  <h4 className="font-semibold text-foreground mb-1">Telegram Bot</h4>
                  <p className="text-sm text-muted-foreground">Real-time alerts on mobile</p>
                </div>
                <Badge variant="secondary" className="bg-muted text-muted-foreground">
                  Not Connected
                </Badge>
              </div>
            </Card>
            <Card className="card-gradient border-border bg-card p-6">
              <div className="flex items-center justify-between">
                <div>
                  <h4 className="font-semibold text-foreground mb-1">WebSocket Live Status</h4>
                  <p className="text-sm text-muted-foreground">Live data synchronization</p>
                </div>
                <Badge className="bg-success/20 text-success border-success/30 border">
                  Connected
                </Badge>
              </div>
            </Card>
          </div>
        </section>
      </div>
    </div>
  );
}
