"use client";

import Link from 'next/link';
import { ArrowRight, Users, Shield, Landmark, LineChart } from "lucide-react";

const Card = ({ children, className = '' }: { children: React.ReactNode, className?: string }) => (
    <div className={`bg-black/20 backdrop-blur-md border border-cyan-500/20 rounded-xl shadow-lg shadow-cyan-500/5 ${className}`}>
        {children}
    </div>
);

const DashboardWidget = ({ href, icon: Icon, title, description }: { href: string, icon: React.ElementType, title: string, description: string }) => {
    return (
        <Link href={href}>
            <Card className="p-6 group hover:border-cyan-500/50 transition-all h-full flex flex-col justify-between">
                <div>
                    <div className="flex items-center gap-3 mb-3">
                        <div className="p-2 bg-gray-700 rounded-lg">
                            <Icon className="text-gray-300" />
                        </div>
                        <h3 className="font-bold text-lg text-cyan-300">{title}</h3>
                    </div>
                    <p className="text-sm text-gray-400">{description}</p>
                </div>
                <div className="flex justify-end items-center text-sm mt-4">
                    <ArrowRight className="text-gray-500 group-hover:text-white group-hover:translate-x-1 transition-transform" />
                </div>
            </Card>
        </Link>
    );
};

export default function DashboardHomePage() {
    return (
        <div className="min-h-screen p-4 sm:p-6 lg:p-8 bg-gray-900 text-white">
            <div className="max-w-7xl mx-auto">
                <h1 className="text-4xl font-bold mb-2 text-cyan-300 drop-shadow-[0_0_5px_rgba(0,255,255,0.3)]">
                    Alfa Intelligence
                </h1>
                <p className="text-lg text-gray-400 mb-8">
                    Ваш автономный бизнес-ассистент.
                </p>

                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
                    <DashboardWidget 
                        href="/dashboard/competitors"
                        icon={Users}
                        title="Конкуренты"
                        description="Анализируйте действия конкурентов в реальном времени."
                    />
                    <DashboardWidget 
                        href="/dashboard/legal"
                        icon={Shield}
                        title="Законы"
                        description="Отслеживайте изменения в законодательстве, чтобы избежать штрафов."
                    />
                    <DashboardWidget 
                        href="/dashboard/finance"
                        icon={Landmark}
                        title="Финансы"
                        description="Получайте прогнозы по денежному потоку и избегайте кассовых разрывов."
                    />
                    <DashboardWidget 
                        href="/dashboard/trends"
                        icon={LineChart}
                        title="Тренды"
                        description="Находите новые рыночные возможности и будьте на шаг впереди."
                    />
                </div>
            </div>
        </div>
    );
}