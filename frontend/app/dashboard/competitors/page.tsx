"use client";
import { useState } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { Plus, Search, Trash2, Zap, Loader2, TrendingUp, TrendingDown, Minus } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Badge } from "@/components/ui/badge";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog";
import api from "@/lib/api";

const AddCompetitorModal = ({
  isOpen,
  onClose,
  onAdd,
}: {
  isOpen: boolean;
  onClose: () => void;
  onAdd: (data: any) => void;
}) => {
  const [name, setName] = useState("");
  const [url, setUrl] = useState("");

  if (!isOpen) return null;

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    onAdd({ name, website_url: url });
    setName("");
    setUrl("");
    onClose();
  };

  return (
    <div className="fixed inset-0 bg-black/50 z-50 flex items-center justify-center p-4">
      <Card className="w-full max-w-md p-6">
        <h2 className="text-2xl font-bold mb-4 text-foreground">Добавить конкурента</h2>
        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <Label htmlFor="name">Название компании</Label>
            <Input
              id="name"
              value={name}
              onChange={(e) => setName(e.target.value)}
              placeholder="Название конкурента"
              required
            />
          </div>
          <div>
            <Label htmlFor="url">URL сайта</Label>
            <Input
              id="url"
              type="url"
              value={url}
              onChange={(e) => setUrl(e.target.value)}
              placeholder="https://competitor.com"
              required
            />
          </div>
          <div className="flex justify-end gap-3 pt-4">
            <Button variant="outline" onClick={onClose} className="text-foreground">
              Отмена
            </Button>
            <Button type="submit" className="bg-primary text-primary-foreground">Добавить</Button>
          </div>
        </form>
      </Card>
    </div>
  );
};

const BenchmarkBar = ({ label, usValue, competitorValue, better }: any) => {
  const maxValue = Math.max(usValue, competitorValue);
  const usWidth = (usValue / maxValue) * 100;
  const compWidth = (competitorValue / maxValue) * 100;

  return (
    <div className="space-y-2">
      <div className="flex items-center justify-between text-sm">
        <span className="text-foreground font-medium">{label}</span>
        <div className="flex items-center gap-2">
          {better ? (
            <TrendingUp className="w-4 h-4 text-green-600" />
          ) : (
            <TrendingDown className="w-4 h-4 text-red-600" />
          )}
          <span className={better ? "text-green-600" : "text-red-600"}>
            {better ? "Лучше" : "Отстаём"}
          </span>
        </div>
      </div>
      <div className="space-y-1">
        <div className="flex items-center gap-2">
          <span className="text-xs text-muted-foreground w-20">Вы</span>
          <div className="flex-1 bg-muted rounded-full h-2">
            <div
              className="bg-primary h-2 rounded-full transition-all"
              style={{ width: `${usWidth}%` }}
            />
          </div>
          <span className="text-xs font-semibold text-foreground w-8 text-right">
            {usValue}
          </span>
        </div>
        <div className="flex items-center gap-2">
          <span className="text-xs text-muted-foreground w-20">Конкурент</span>
          <div className="flex-1 bg-muted rounded-full h-2">
            <div
              className="bg-orange-500 h-2 rounded-full transition-all"
              style={{ width: `${compWidth}%` }}
            />
          </div>
          <span className="text-xs font-semibold text-foreground w-8 text-right">
            {competitorValue}
          </span>
        </div>
      </div>
    </div>
  );
};

export default function CompetitorsPage() {
  const [isModalOpen, setIsModalOpen] = useState(false);
  const queryClient = useQueryClient();

  const { data: competitors, isLoading: isLoadingCompetitors } = useQuery({
    queryKey: ["competitors"],
    queryFn: () => api.get("/competitors").then((res) => res.data),
  });

  const { data: insights, isLoading: isLoadingInsights } = useQuery({
    queryKey: ["competitor-insights"],
    queryFn: () => api.get("/competitors/insights").then((res) => res.data),
    refetchInterval: 60000, // Refresh every minute
  });

  const addCompetitorMutation = useMutation({
    mutationFn: (newCompetitor: any) =>
      api.post("/competitors", newCompetitor).then((res) => res.data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["competitors"] });
      queryClient.invalidateQueries({ queryKey: ["competitor-insights"] });
    },
  });

  const deleteCompetitorMutation = useMutation({
    mutationFn: (id: string) => api.delete(`/competitors/${id}`),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["competitors"] });
      queryClient.invalidateQueries({ queryKey: ["competitor-insights"] });
    },
  });

  const scanCompetitorMutation = useMutation({
    mutationFn: (id: string) =>
      api.post(`/competitors/${id}/scan`).then((res) => res.data),
    onSuccess: () => {
      setTimeout(() => {
        queryClient.invalidateQueries({ queryKey: ["competitors"] });
        queryClient.invalidateQueries({ queryKey: ["competitor-insights"] });
      }, 3000);
    },
  });

  // Get benchmark data from insights
  const benchmarks = insights?.benchmarks || {};
  const hasBenchmarks = Object.keys(benchmarks).length > 0;

  // Map position to color
  const getPositionColor = (position: string) => {
    if (position === "Сильная") return "text-green-600";
    if (position === "Слабая") return "text-red-600";
    return "text-yellow-600";
  };

  return (
    <div className="min-h-screen p-4 sm:p-6 lg:p-8 bg-background">
      <div className="max-w-7xl mx-auto">
        <div className="flex justify-between items-center mb-8">
          <div>
            <h1 className="text-4xl font-bold text-foreground">Анализ конкурентов</h1>
            <p className="text-muted-foreground mt-1">Конкурентная разведка и бенчмаркинг на основе ИИ</p>
          </div>
          <Button onClick={() => setIsModalOpen(true)} className="gap-2">
            <Plus className="w-4 h-4" />
            Добавить конкурента
          </Button>
        </div>

        {/* AI Summary Card */}
        <Card className="p-6 mb-6 bg-gradient-to-br from-primary/5 to-secondary/5 border-primary/20">
          <h3 className="text-xl font-bold text-foreground mb-3">Сводка конкурентного анализа от ИИ</h3>
          {isLoadingInsights ? (
            <div className="flex items-center gap-2">
              <Loader2 className="animate-spin w-4 h-4" />
              <span className="text-muted-foreground">Генерация аналитики...</span>
            </div>
          ) : (
            <>
              <p className="text-foreground leading-relaxed mb-4">
                {insights?.summary || "Добавьте конкурентов и запустите сканирование для получения аналитики."}
              </p>
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mt-4">
                <div>
                  <p className="text-sm text-muted-foreground">Общая позиция</p>
                  <p className={`text-2xl font-bold ${getPositionColor(insights?.overall_position)}`}>
                    {insights?.overall_position || "Н/Д"}
                  </p>
                </div>
                <div>
                  <p className="text-sm text-muted-foreground">Доля рынка</p>
                  <p className="text-2xl font-bold text-foreground">{insights?.market_share || "Н/Д"}</p>
                </div>
                <div>
                  <p className="text-sm text-muted-foreground">Индекс цен</p>
                  <p className="text-2xl font-bold text-orange-600">{insights?.price_index || "Н/Д"}</p>
                </div>
                <div>
                  <p className="text-sm text-muted-foreground">Темп роста</p>
                  <p className="text-2xl font-bold text-green-600">{insights?.growth_rate || "Н/Д"}</p>
                </div>
              </div>
            </>
          )}
        </Card>

        {/* Benchmarking Card */}
        {hasBenchmarks && (
          <Card className="p-6 mb-6">
            <div className="flex items-center justify-between mb-6">
              <h3 className="text-xl font-bold text-foreground">Конкурентные показатели</h3>
              <span className="text-sm text-muted-foreground">Сравнение со средним конкурентом</span>
            </div>
            <div className="space-y-6">
              <BenchmarkBar
                label="Ценовая конкурентоспособность"
                usValue={benchmarks.pricing?.us || 0}
                competitorValue={benchmarks.pricing?.competitor_avg || 0}
                better={(benchmarks.pricing?.us || 0) >= (benchmarks.pricing?.competitor_avg || 0)}
              />
              <BenchmarkBar
                label="Качество продукта"
                usValue={benchmarks.quality?.us || 0}
                competitorValue={benchmarks.quality?.competitor_avg || 0}
                better={(benchmarks.quality?.us || 0) >= (benchmarks.quality?.competitor_avg || 0)}
              />
              <BenchmarkBar
                label="Качество обслуживания"
                usValue={benchmarks.service?.us || 0}
                competitorValue={benchmarks.service?.competitor_avg || 0}
                better={(benchmarks.service?.us || 0) >= (benchmarks.service?.competitor_avg || 0)}
              />
              <BenchmarkBar
                label="Онлайн-присутствие"
                usValue={benchmarks.online_presence?.us || 0}
                competitorValue={benchmarks.online_presence?.competitor_avg || 0}
                better={(benchmarks.online_presence?.us || 0) >= (benchmarks.online_presence?.competitor_avg || 0)}
              />
              <BenchmarkBar
                label="Удовлетворенность клиентов"
                usValue={benchmarks.customer_satisfaction?.us || 0}
                competitorValue={benchmarks.customer_satisfaction?.competitor_avg || 0}
                better={(benchmarks.customer_satisfaction?.us || 0) >= (benchmarks.customer_satisfaction?.competitor_avg || 0)}
              />
            </div>
          </Card>
        )}

        {/* Competitors List */}
        <div className="space-y-4">
          {isLoadingCompetitors && (
            <Card className="p-6 text-center">
              <Loader2 className="animate-spin mx-auto w-6 h-6 mb-2" />
              <p className="text-muted-foreground">Загрузка конкурентов...</p>
            </Card>
          )}
          {!isLoadingCompetitors && competitors?.length === 0 && (
            <Card className="p-6 text-center text-muted-foreground">
              <p>
                Конкуренты еще не добавлены. Нажмите «Добавить конкурента» для начала отслеживания конкурентов.
              </p>
            </Card>
          )}
          {competitors?.map((competitor: any) => (
            <Card key={competitor.id} className="p-6 hover:shadow-lg transition-shadow">
              <div className="flex justify-between items-start mb-4">
                <div className="flex-1">
                  <div className="flex items-center gap-3 mb-2">
                    <h3 className="text-xl font-bold text-foreground">{competitor.name}</h3>
                    <Badge variant="secondary">Отслеживается</Badge>
                  </div>
                  <p className="text-sm text-muted-foreground truncate mb-3">
                    {competitor.website_url || "URL не указан"}
                  </p>
                </div>
                <div className="flex items-center gap-2">
                  <Button
                    size="sm"
                    onClick={() => scanCompetitorMutation.mutate(competitor.id)}
                    disabled={scanCompetitorMutation.isPending}
                    className="gap-2"
                  >
                    <Zap className="w-4 h-4" />
                    Сканировать
                  </Button>
                  <Button
                    size="sm"
                    variant="destructive"
                    onClick={() =>
                      deleteCompetitorMutation.mutate(competitor.id)
                    }
                    className="gap-2"
                  >
                    <Trash2 className="w-4 h-4" />
                  </Button>
                </div>
              </div>

              {competitor.last_scanned ? (
                <div className="pt-4 border-t text-xs text-muted-foreground">
                  Последнее сканирование:{" "}
                  {new Date(competitor.last_scanned).toLocaleString("ru-RU")}
                </div>
              ) : (
                <div className="pt-4 border-t text-sm text-muted-foreground text-center py-3 bg-muted rounded">
                  Нажмите «Сканировать» для анализа этого конкурента
                </div>
              )}
            </Card>
          ))}
        </div>
      </div>

      <AddCompetitorModal
        isOpen={isModalOpen}
        onClose={() => setIsModalOpen(false)}
        onAdd={(data) => addCompetitorMutation.mutate(data)}
      />
    </div>
  );
}
