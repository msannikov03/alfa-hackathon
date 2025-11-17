"use client";
import { useState } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import {
  Upload,
  Loader2,
  BarChart,
  AlertTriangle,
  CheckCircle,
} from "lucide-react";
import dynamic from "next/dynamic";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Alert, AlertDescription } from "@/components/ui/alert";
import api from "@/lib/api";
import type { AxiosError } from "axios";

// ... existing recharts imports ...
const DynamicLineChart = dynamic(
  () => import("recharts").then((mod) => mod.LineChart),
  { ssr: false }
);
const DynamicResponsiveContainer = dynamic(
  () => import("recharts").then((mod) => mod.ResponsiveContainer),
  { ssr: false }
);
const DynamicLine = dynamic(() => import("recharts").then((mod) => mod.Line), {
  ssr: false,
});
const DynamicXAxis = dynamic(
  () => import("recharts").then((mod) => mod.XAxis),
  { ssr: false }
);
const DynamicYAxis = dynamic(
  () => import("recharts").then((mod) => mod.YAxis),
  { ssr: false }
);
const DynamicCartesianGrid = dynamic(
  () => import("recharts").then((mod) => mod.CartesianGrid),
  { ssr: false }
);
const DynamicTooltip = dynamic(
  () => import("recharts").then((mod) => mod.Tooltip),
  { ssr: false }
);
const DynamicLegend = dynamic(
  () => import("recharts").then((mod) => mod.Legend),
  { ssr: false }
);
const DynamicReferenceLine = dynamic(
  () => import("recharts").then((mod) => mod.ReferenceLine),
  { ssr: false }
);

type PageState = "initial" | "mapping" | "forecasting" | "results" | "demo";

// Hardcoded demo forecast data (proof of concept)
const demoForecastData = {
  predicted_data: [
    { date: "14 янв", balance: 125000, income: 45000, expense: 28000 },
    { date: "15 янв", balance: 138000, income: 42000, expense: 29000 },
    { date: "16 янв", balance: 151000, income: 48000, expense: 35000 },
    { date: "17 янв", balance: 159000, income: 43000, expense: 35000 },
    { date: "18 янв", balance: 172000, income: 51000, expense: 38000 },
    { date: "19 янв", balance: 168000, income: 38000, expense: 42000 },
    { date: "20 янв", balance: 177000, income: 46000, expense: 37000 },
  ],
  insights: {
    risks: [
      { message: "Ожидается небольшое снижение денежного потока 19 января из-за увеличения расходов" },
      { message: "Выручка в выходные обычно на 15% ниже, чем в будни" },
    ],
    recommendations: [
      { message: "Рассмотрите возможность отложить крупные покупки до 20 января" },
      { message: "Сильная восходящая тенденция указывает на возможность небольших инвестиций в расширение" },
      { message: "Сохраняйте текущие уровни расходов для стабильного роста" },
    ],
  },
};

export default function FinancePage() {
  const [pageState, setPageState] = useState<PageState>("initial");
  const [file, setFile] = useState<File | null>(null);
  const [mapping, setMapping] = useState<any>(null);
  const [currentBalance, setCurrentBalance] = useState("");
  const queryClient = useQueryClient();

  const {
    data: forecastData,
    refetch: refetchForecast,
    isFetching: forecastFetching,
  } = useQuery({
    queryKey: ["financeForecast"],
    queryFn: async () => {
      try {
        const response = await api.get("/finance/forecast");
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

  const effectivePageState: PageState =
    pageState === "initial" && forecastData ? "results" : pageState;

  const mappingMutation = useMutation({
    mutationFn: (file: File) => {
      const formData = new FormData();
      formData.append("file", file);
      return api.post("/finance/upload-csv", formData, {
        headers: { "Content-Type": "multipart/form-data" },
      });
    },
    onSuccess: (data) => {
      setMapping(data.data.mapping);
      setPageState("mapping");
    },
  });

  const forecastMutation = useMutation({
    mutationFn: () => {
      const formData = new FormData();
      formData.append("file", file!);
      formData.append("mapping", JSON.stringify(mapping));
      formData.append("current_balance", currentBalance);
      return api.post("/finance/forecast", formData, {
        headers: { "Content-Type": "multipart/form-data" },
      });
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["financeForecast"] });
      refetchForecast();
      setPageState("results");
    },
  });

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files) {
      setFile(e.target.files[0]);
      mappingMutation.mutate(e.target.files[0]);
    }
  };

  const renderInitialState = () => (
    <Card className="p-8 text-center">
      <h2 className="text-2xl font-bold mb-4 text-foreground">Финансовое прогнозирование</h2>
      <p className="text-muted-foreground mb-6">
        Загрузите банковскую выписку или данные CRM в формате CSV, или посмотрите демо-прогноз.
      </p>
      <div className="flex flex-col sm:flex-row gap-4 justify-center items-center">
        <Button
          onClick={() => document.getElementById("csv-upload")?.click()}
          disabled={mappingMutation.isPending}
          className="gap-2 bg-primary text-primary-foreground hover:bg-primary/90"
        >
          <Upload className="w-4 h-4" />
          {mappingMutation.isPending ? "Обработка..." : "Загрузить CSV"}
        </Button>
        <span className="text-muted-foreground">или</span>
        <Button
          variant="outline"
          onClick={() => setPageState("demo")}
          className="gap-2 text-foreground"
        >
          <BarChart className="w-4 h-4" />
          Демо-прогноз
        </Button>
      </div>
      <input
        id="csv-upload"
        type="file"
        accept=".csv"
        className="hidden"
        onChange={handleFileChange}
      />
    </Card>
  );

  const renderMappingState = () => (
    <Card className="p-6">
      <h2 className="text-2xl font-bold mb-4 text-foreground">Проверьте соответствие столбцов</h2>
      <p className="text-muted-foreground mb-6">
        Проверьте обнаруженные столбцы из вашего файла.
      </p>
      <div className="space-y-2 p-4 rounded-lg bg-muted mb-6">
        <div>
          <span className="text-sm font-medium text-muted-foreground">
            Date:
          </span>{" "}
          {mapping.date_column}
        </div>
        <div>
          <span className="text-sm font-medium text-muted-foreground">
            Description:
          </span>{" "}
          {mapping.description_column}
        </div>
        {mapping.amount_logic.type === "single_column" ? (
          <div>
            <span className="text-sm font-medium text-muted-foreground">
              Amount:
            </span>{" "}
            {mapping.amount_logic.amount_column}
          </div>
        ) : (
          <>
            <div>
              <span className="text-sm font-medium text-muted-foreground">
                Income:
              </span>{" "}
              {mapping.amount_logic.income_column}
            </div>
            <div>
              <span className="text-sm font-medium text-muted-foreground">
                Expense:
              </span>{" "}
              {mapping.amount_logic.expense_column}
            </div>
          </>
        )}
      </div>
      <div className="mb-6">
        <Label htmlFor="balance">Текущий баланс</Label>
        <Input
          id="balance"
          type="number"
          value={currentBalance}
          onChange={(e) => setCurrentBalance(e.target.value)}
          placeholder="100000"
        />
      </div>
      <div className="flex justify-end gap-4">
        <Button variant="outline" onClick={() => setPageState("initial")}>
          Отмена
        </Button>
        <Button
          onClick={() => forecastMutation.mutate()}
          disabled={forecastMutation.isPending || !currentBalance}
          className="gap-2"
        >
          <BarChart className="w-4 h-4" />
          Создать прогноз
        </Button>
      </div>
    </Card>
  );

  const renderResultsState = () => {
    if (!forecastData) {
      return (
        <Card className="p-6 text-center text-muted-foreground">
          <p>У вас пока нет сохраненных прогнозов. Загрузите CSV, чтобы построить прогноз.</p>
        </Card>
      );
    }

    const risks = forecastData.insights?.risks ?? [];
    const recommendations = forecastData.insights?.recommendations ?? [];

    return (
      <div className="space-y-6">
        <Card className="p-6">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-xl font-bold text-foreground">Прогноз на 7 дней</h3>
            {forecastFetching && (
              <span className="text-sm text-muted-foreground">Обновляем данные...</span>
            )}
          </div>
          <DynamicResponsiveContainer width="100%" height={300}>
            <DynamicLineChart data={forecastData.predicted_data}>
            <DynamicCartesianGrid strokeDasharray="3 3" />
            <DynamicXAxis dataKey="date" />
            <DynamicYAxis />
            <DynamicTooltip />
            <DynamicLegend />
            <DynamicReferenceLine
              y={0}
              stroke="#ef4444"
              strokeDasharray="4 4"
            />
            <DynamicLine
              type="monotone"
              dataKey="balance"
              stroke="hsl(var(--primary))"
              strokeWidth={2}
            />
          </DynamicLineChart>
          </DynamicResponsiveContainer>
        </Card>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <Card className="p-6 border-orange-200 bg-orange-50/50">
            <div className="flex items-center gap-2 mb-4">
              <AlertTriangle className="w-5 h-5 text-orange-600" />
              <h3 className="text-xl font-bold text-foreground">Considerations</h3>
            </div>
            <div className="space-y-3">
              {risks.length > 0 ? (
                risks.map((risk: any, i: number) => (
                  <div key={i} className="flex items-start gap-3 p-3 bg-white rounded-lg border border-orange-100">
                    <div className="w-1.5 h-1.5 rounded-full bg-orange-500 mt-2 flex-shrink-0" />
                    <p className="text-sm text-foreground">{risk.message}</p>
                  </div>
                ))
              ) : (
                <p className="text-muted-foreground">No significant risks detected.</p>
              )}
            </div>
          </Card>

          <Card className="p-6 border-green-200 bg-green-50/50">
            <div className="flex items-center gap-2 mb-4">
              <CheckCircle className="w-5 h-5 text-green-600" />
              <h3 className="text-xl font-bold text-foreground">Recommendations</h3>
            </div>
            <div className="space-y-3">
              {recommendations.length > 0 ? (
                recommendations.map((rec: any, i: number) => (
                  <div key={i} className="flex items-start gap-3 p-3 bg-white rounded-lg border border-green-100">
                    <div className="w-1.5 h-1.5 rounded-full bg-green-500 mt-2 flex-shrink-0" />
                    <p className="text-sm text-foreground">{rec.message}</p>
                  </div>
                ))
              ) : (
                <p className="text-muted-foreground">No recommendations at this time.</p>
              )}
            </div>
          </Card>
        </div>
      </div>
    );
  };

  const renderDemoState = () => (
    <div className="space-y-6">
      <Card className="p-4 bg-gradient-to-br from-primary/5 to-secondary/5 border-primary/20">
        <p className="text-sm text-foreground">
          <strong>Демо-режим:</strong> Этот прогноз основан на демо-данных для демонстрации.
          Загрузите ваш реальный CSV-файл для персонализированных прогнозов.
        </p>
      </Card>

      <Card className="p-6">
        <h3 className="text-xl font-bold mb-4 text-foreground">Прогноз движения денежных средств на 7 дней</h3>
        <DynamicResponsiveContainer width="100%" height={300}>
          <DynamicLineChart data={demoForecastData.predicted_data}>
            <DynamicCartesianGrid strokeDasharray="3 3" />
            <DynamicXAxis dataKey="date" />
            <DynamicYAxis />
            <DynamicTooltip />
            <DynamicLegend />
            <DynamicReferenceLine
              y={0}
              stroke="#ef4444"
              strokeDasharray="4 4"
            />
            <DynamicLine
              type="monotone"
              dataKey="balance"
              stroke="hsl(var(--primary))"
              strokeWidth={2}
              name="Баланс"
            />
            <DynamicLine
              type="monotone"
              dataKey="income"
              stroke="#10b981"
              strokeWidth={2}
              name="Доходы"
            />
            <DynamicLine
              type="monotone"
              dataKey="expense"
              stroke="#ef4444"
              strokeWidth={2}
              name="Расходы"
            />
          </DynamicLineChart>
        </DynamicResponsiveContainer>
      </Card>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <Card className="p-6 border-orange-200 bg-orange-50/50">
          <div className="flex items-center gap-2 mb-4">
            <AlertTriangle className="w-5 h-5 text-orange-600" />
            <h3 className="text-xl font-bold text-foreground">Considerations</h3>
          </div>
          <div className="space-y-3">
            {demoForecastData.insights.risks.map((risk: any, i: number) => (
              <div key={i} className="flex items-start gap-3 p-3 bg-white rounded-lg border border-orange-100">
                <div className="w-1.5 h-1.5 rounded-full bg-orange-500 mt-2 flex-shrink-0" />
                <p className="text-sm text-foreground">{risk.message}</p>
              </div>
            ))}
          </div>
        </Card>

        <Card className="p-6 border-green-200 bg-green-50/50">
          <div className="flex items-center gap-2 mb-4">
            <CheckCircle className="w-5 h-5 text-green-600" />
            <h3 className="text-xl font-bold text-foreground">Recommendations</h3>
          </div>
          <div className="space-y-3">
            {demoForecastData.insights.recommendations.map((rec: any, i: number) => (
              <div key={i} className="flex items-start gap-3 p-3 bg-white rounded-lg border border-green-100">
                <div className="w-1.5 h-1.5 rounded-full bg-green-500 mt-2 flex-shrink-0" />
                <p className="text-sm text-foreground">{rec.message}</p>
              </div>
            ))}
          </div>
        </Card>
      </div>
    </div>
  );

  return (
    <div className="min-h-screen p-4 sm:p-6 lg:p-8 bg-background">
      <div className="max-w-7xl mx-auto">
        <div className="flex justify-between items-center mb-8">
          <h1 className="text-4xl font-bold text-foreground">Финансовый прогноз</h1>
          {(effectivePageState === "results" || pageState === "demo") && (
            <Button variant="outline" onClick={() => setPageState("initial")} className="text-foreground">
              Начать заново
            </Button>
          )}
        </div>
        {effectivePageState === "initial" && renderInitialState()}
        {effectivePageState === "mapping" && renderMappingState()}
        {effectivePageState === "results" && renderResultsState()}
        {pageState === "demo" && renderDemoState()}
      </div>
    </div>
  );
}
