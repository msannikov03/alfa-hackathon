"use client";

import Link from "next/link";
import {
  ArrowRight,
  Users,
  Shield,
  Landmark,
  LineChart,
  Sparkles,
} from "lucide-react";

const Card = ({
  children,
  className = "",
}: {
  children: React.ReactNode;
  className?: string;
}) => (
  <div
    className={`bg-card border border-border rounded-lg transition-all duration-300 hover:border-primary/50 hover:shadow-md ${className}`}
  >
    {children}
  </div>
);

const DashboardWidget = ({
  href,
  icon: Icon,
  title,
  description,
}: {
  href: string;
  icon: React.ElementType;
  title: string;
  description: string;
}) => {
  return (
    <Link href={href}>
      <Card className="p-6 group h-full flex flex-col justify-between hover:shadow-lg">
        <div>
          <div className="flex items-center gap-3 mb-4">
            <div className="p-2.5 bg-primary/10 rounded-lg border border-primary/20 group-hover:border-primary/50 group-hover:bg-primary/15 transition-all duration-300">
              <Icon className="text-primary h-5 w-5" />
            </div>
            <h3 className="font-semibold text-base text-foreground group-hover:text-primary transition-colors duration-300">
              {title}
            </h3>
          </div>
          <p className="text-sm text-muted-foreground leading-relaxed">
            {description}
          </p>
        </div>
        <div className="flex justify-end items-center text-sm mt-6">
          <ArrowRight className="text-muted-foreground group-hover:text-primary group-hover:translate-x-1 transition-all duration-300 h-4 w-4" />
        </div>
      </Card>
    </Link>
  );
};

export default function DashboardHomePage() {
  return (
    <div className="min-h-screen p-6 sm:p-8 lg:p-10 bg-background">
      <div className="max-w-7xl mx-auto">
        <div className="mb-12">
          <div className="flex items-center gap-3 mb-4">
            <div className="p-2 bg-primary/10 rounded-lg border border-primary/20">
              <Sparkles className="h-5 w-5 text-primary" />
            </div>
            <span className="text-xs font-semibold text-primary uppercase tracking-widest">
              Бизнес-ассистент нового поколения
            </span>
          </div>
          <h1 className="text-5xl sm:text-6xl font-bold mb-4 text-foreground tracking-tight">
            Alfa Intelligence
          </h1>
          <p className="text-lg text-muted-foreground max-w-2xl leading-relaxed">
            Ваш автономный бизнес-помощник. Получайте аналитику, прогнозы и
            рекомендации в реальном времени для роста вашего бизнеса.
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          <DashboardWidget
            href="/dashboard/competitors"
            icon={Users}
            title="Конкуренты"
            description="Анализируйте действия конкурентов в реальном времени и получайте стратегические инсайты."
          />
          <DashboardWidget
            href="/dashboard/legal"
            icon={Shield}
            title="Юридическое"
            description="Отслеживайте законодательные изменения, чтобы избежать штрафов и снизить риски."
          />
          <DashboardWidget
            href="/dashboard/finance"
            icon={Landmark}
            title="Финансы"
            description="Получайте прогнозы денежных потоков и избегайте кассовых разрывов заранее."
          />
          <DashboardWidget
            href="/dashboard/trends"
            icon={LineChart}
            title="Тренды"
            description="Откройте новые рыночные возможности и опережайте конкурентов."
          />
        </div>
      </div>
    </div>
  );
}
