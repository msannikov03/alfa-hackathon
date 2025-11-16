"use client";
import { useState } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { Bot, Edit, Loader2, Save, Zap } from "lucide-react";
import { NeonButton } from "@/components/ui/button";
import api from "@/lib/api";

// --- UI Components (re-using from competitors page for consistency) ---

const Card = ({ children, className = '' }: { children: React.ReactNode, className?: string }) => (
    <div className={`bg-black/20 backdrop-blur-md border border-cyan-500/20 rounded-xl shadow-lg shadow-cyan-500/5 ${className}`}>
        {children}
    </div>
);

const ImpactPill = ({ level }: { level: string }) => {
    const styles = {
        High: 'bg-red-500/20 text-red-300 border-red-500/50',
        Medium: 'bg-yellow-500/20 text-yellow-300 border-yellow-500/50',
        Low: 'bg-blue-500/20 text-blue-300 border-blue-500/50',
    };
    const style = styles[level as keyof typeof styles] || 'bg-gray-500/20 text-gray-300';
    return <span className={`px-2 py-1 text-xs font-semibold rounded-full border ${style}`}>{level}</span>;
};

const LegalUpdateCard = ({ update }: { update: any }) => (
    <Card className="p-4">
        <div className="flex justify-between items-start mb-2">
            <h3 className="font-bold text-lg text-cyan-300 pr-4">{update.title}</h3>
            <ImpactPill level={update.impact_level} />
        </div>
        <p className="text-sm text-gray-400 mb-3">{update.summary}</p>
        <div className="flex justify-between items-center">
            <span className="text-xs font-mono text-gray-500">{update.category}</span>
            <span className="text-xs text-gray-500">{new Date(update.detected_at).toISOString().split('T')[0]}</span>
        </div>
    </Card>
);

// --- Main Page Component ---

export default function LegalPage() {
    const queryClient = useQueryClient();
    const [scanStarted, setScanStarted] = useState(false);

    const { data: updates, isLoading: isLoadingUpdates } = useQuery({
        queryKey: ["legalUpdates"],
        queryFn: () => api.get("/legal/updates").then(res => res.data),
    });

    const scanMutation = useMutation({
        mutationFn: () => api.post("/legal/scan"),
        onSuccess: () => {
            // We can't invalidate immediately, as it's a background task.
            // Show user that scan is initiated, and refetch after a delay
            console.log("Scan initiated");
            setScanStarted(true);

            // Hide notification after 5 seconds
            setTimeout(() => {
                setScanStarted(false);
            }, 5000);

            // Refetch after 5 seconds to see if new data is available
            setTimeout(() => {
                queryClient.invalidateQueries({ queryKey: ["legalUpdates"] });
            }, 5000);
        }
    });

    return (
        <div className="min-h-screen p-4 sm:p-6 lg:p-8 bg-gray-900 text-white font-sans">
            <div className="max-w-7xl mx-auto">
                <div className="flex justify-between items-center mb-8">
                    <h1 className="text-4xl font-bold text-cyan-300 drop-shadow-[0_0_5px_rgba(0,255,255,0.3)]">
                        Юридический мониторинг
                    </h1>
                    <NeonButton onClick={() => scanMutation.mutate()} isLoading={scanMutation.isPending}>
                        <Zap size={18} />
                        Сканировать
                    </NeonButton>
                </div>

                {scanStarted && (
                    <Card className="p-4 bg-blue-900/20 border-blue-500/30 mb-6">
                        <div className="flex items-center gap-3">
                            <Loader2 className="animate-spin text-blue-400" size={20} />
                            <p className="text-blue-300">Сканирование законодательных изменений запущено в фоновом режиме...</p>
                        </div>
                    </Card>
                )}

                <div className="space-y-6">
                    <h2 className="text-2xl font-semibold tracking-tight text-gray-400 border-b-2 border-cyan-500/20 pb-2">Релевантные обновления</h2>
                    <div className="space-y-4">
                        {isLoadingUpdates && <p>Загрузка обновлений...</p>}
                        {updates?.map((update: any) => (
                            <LegalUpdateCard key={update.id} update={update} />
                        ))}
                        {!isLoadingUpdates && updates?.length === 0 && (
                            <Card className="p-6 text-center text-gray-500">
                                <p>Нет релевантных обновлений. Убедитесь, что ваш бизнес-контекст сохранен в <a href="/dashboard/settings" className="text-cyan-400 hover:underline">Настройках</a>, и запустите сканирование.</p>
                            </Card>
                        )}
                    </div>
                </div>
            </div>
        </div>
    );
}