"use client";
import { useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { Building2, Users, MapPin, Clock, TrendingUp, Sparkles, Bot } from "lucide-react";
import { Card } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import api from "@/lib/api";

export default function ProfilePage() {
  const [userId] = useState<string | null>(() => {
    if (typeof window === "undefined") {
      return null;
    }
    return localStorage.getItem("user_id");
  });

  const { data: profile } = useQuery({
    queryKey: ["userProfile", userId],
    queryFn: () => api.get(`/user/${userId}`).then((res) => res.data),
    enabled: !!userId,
  });

  const { data: metrics } = useQuery({
    queryKey: ["performanceMetrics", userId],
    queryFn: () => api.get(`/v1/metrics/performance?user_id=${userId}`).then((res) => res.data),
    enabled: !!userId,
  });

  // Hardcoded AI-generated business summary (proof of concept)
  const businessSummary = profile?.business_name ?
    `По результатам нашего анализа, ${profile.business_name} — процветающий ${profile.business_type || 'бизнес'} на конкурентном рынке Москвы. При стабильных ежедневных операциях и фокусе на качественном сервисе бизнес демонстрирует сильный потенциал роста. Наш ИИ выявил ключевые сильные стороны в вовлеченности клиентов и операционной эффективности. Стратегические рекомендации включают расширение цифрового присутствия и оптимизацию штата в часы пик.` :
    "Заполните профиль вашего бизнеса, чтобы получить сводку и персонализированные инсайты от ИИ.";

  const aiInsights = [
    {
      icon: TrendingUp,
      title: "Потенциал роста",
      value: "Высокий",
      description: "Сильная рыночная позиция с возможностями расширения",
      color: "text-green-600",
    },
    {
      icon: Users,
      title: "Удержание клиентов",
      value: "87%",
      description: "Выше среднего по отрасли, высокая лояльность",
      color: "text-blue-600",
    },
    {
      icon: Clock,
      title: "Операционная эффективность",
      value: "92%",
      description: "Отличное управление временем и оптимизация процессов",
      color: "text-purple-600",
    },
  ];

  return (
    <div className="min-h-screen p-4 sm:p-6 lg:p-8 bg-background">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-4xl font-bold text-foreground mb-2">Профиль бизнеса</h1>
          <p className="text-muted-foreground">Инсайты от ИИ о вашем бизнесе</p>
        </div>

        {/* Main Profile Card */}
        <Card className="p-8 mb-6 border-2 border-primary/20">
          <div className="flex items-start gap-6">
            <div className="p-4 bg-primary/10 rounded-xl border-2 border-primary/30">
              <Building2 className="w-12 h-12 text-primary" />
            </div>
            <div className="flex-1">
              <div className="flex items-center gap-3 mb-2">
                <h2 className="text-3xl font-bold text-foreground">
                  {profile?.business_name || "Демо кофейня"}
                </h2>
                <Badge variant="secondary" className="text-sm">
                  {profile?.business_type || "Общепит"}
                </Badge>
              </div>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mt-4">
                <div className="flex items-center gap-2 text-muted-foreground">
                  <MapPin className="w-4 h-4" />
                  <span className="text-sm">{profile?.business_context?.location || "Москва, Россия"}</span>
                </div>
                <div className="flex items-center gap-2 text-muted-foreground">
                  <Users className="w-4 h-4" />
                  <span className="text-sm">{profile?.business_context?.employee_count || 12} сотрудников</span>
                </div>
                <div className="flex items-center gap-2 text-muted-foreground">
                  <Clock className="w-4 h-4" />
                  <span className="text-sm">Пн-Вс: 8:00 - 22:00</span>
                </div>
              </div>
            </div>
          </div>
        </Card>

        {/* AI-Generated Summary */}
        <Card className="p-6 mb-6 bg-gradient-to-br from-primary/5 to-secondary/5 border-primary/20">
          <div className="flex items-start gap-4">
            <div className="p-3 bg-primary/20 rounded-lg">
              <Sparkles className="w-6 h-6 text-primary" />
            </div>
            <div className="flex-1">
              <h3 className="text-xl font-bold text-foreground mb-3 flex items-center gap-2">
                <Bot className="w-5 h-5 text-primary" />
                Сводка от ИИ о бизнесе
              </h3>
              <p className="text-foreground leading-relaxed">
                {businessSummary}
              </p>
            </div>
          </div>
        </Card>

        {/* AI Insights Grid */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-6">
          {aiInsights.map((insight, index) => (
            <Card key={index} className="p-6 hover:shadow-lg transition-shadow">
              <div className="flex items-start justify-between mb-4">
                <insight.icon className={`w-8 h-8 ${insight.color}`} />
                <Badge className="bg-primary/10 text-primary border-primary/20">Инсайт ИИ</Badge>
              </div>
              <h4 className="text-sm font-semibold text-muted-foreground mb-1">{insight.title}</h4>
              <p className="text-3xl font-bold text-foreground mb-2">{insight.value}</p>
              <p className="text-sm text-muted-foreground">{insight.description}</p>
            </Card>
          ))}
        </div>

        {/* Performance Metrics */}
        <Card className="p-6">
          <h3 className="text-2xl font-bold text-foreground mb-6">Показатели эффективности</h3>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-6">
            <div>
              <p className="text-sm text-muted-foreground mb-1">Всего действий ИИ</p>
              <p className="text-3xl font-bold text-foreground">{metrics?.total_actions || 156}</p>
            </div>
            <div>
              <p className="text-sm text-muted-foreground mb-1">Время сэкономлено</p>
              <p className="text-3xl font-bold text-primary">{metrics?.time_saved_hours || 39}ч</p>
            </div>
            <div>
              <p className="text-sm text-muted-foreground mb-1">Уровень автоматизации</p>
              <p className="text-3xl font-bold text-green-600">{metrics?.automation_rate || 94}%</p>
            </div>
            <div>
              <p className="text-sm text-muted-foreground mb-1">Принято решений</p>
              <p className="text-3xl font-bold text-foreground">{metrics?.decisions_made || 83}</p>
            </div>
          </div>
        </Card>

        {/* Business Details */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mt-6">
          <Card className="p-6">
            <h3 className="text-xl font-bold text-foreground mb-4">Детали бизнеса</h3>
            <div className="space-y-4">
              <div>
                <p className="text-sm text-muted-foreground">Владелец</p>
                <p className="text-foreground font-medium">{profile?.username || "demo_admin"}</p>
              </div>
              <div>
                <p className="text-sm text-muted-foreground">Дневная выручка (сред.)</p>
                <p className="text-foreground font-medium">₽125,000</p>
              </div>
              <div>
                <p className="text-sm text-muted-foreground">Клиентов (сред.)</p>
                <p className="text-foreground font-medium">280 в день</p>
              </div>
              <div>
                <p className="text-sm text-muted-foreground">Возраст бизнеса</p>
                <p className="text-foreground font-medium">3.5 года</p>
              </div>
            </div>
          </Card>

          <Card className="p-6">
            <h3 className="text-xl font-bold text-foreground mb-4">Ключевые сильные стороны</h3>
            <div className="space-y-3">
              <div className="flex items-start gap-3">
                <div className="w-2 h-2 bg-green-500 rounded-full mt-2" />
                <div>
                  <p className="text-foreground font-medium">Отличное расположение</p>
                  <p className="text-sm text-muted-foreground">Зона с высоким трафиком и отличной видимостью</p>
                </div>
              </div>
              <div className="flex items-start gap-3">
                <div className="w-2 h-2 bg-green-500 rounded-full mt-2" />
                <div>
                  <p className="text-foreground font-medium">Сильная клиентская база</p>
                  <p className="text-sm text-muted-foreground">Лояльные постоянные клиенты, 40% возврат</p>
                </div>
              </div>
              <div className="flex items-start gap-3">
                <div className="w-2 h-2 bg-green-500 rounded-full mt-2" />
                <div>
                  <p className="text-foreground font-medium">Эффективные операции</p>
                  <p className="text-sm text-muted-foreground">Оптимизированный рабочий процесс и управление запасами</p>
                </div>
              </div>
            </div>
          </Card>
        </div>
      </div>
    </div>
  );
}
