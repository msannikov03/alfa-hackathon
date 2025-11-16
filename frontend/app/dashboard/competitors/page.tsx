"use client";
import { useState } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { Plus, Search, Trash2, Zap, Loader2, Lightbulb, TrendingUp, TrendingDown } from "lucide-react";
import { NeonButton } from "@/components/ui/button";
import api from "@/lib/api"; // Assuming this is set up to point to the backend

// --- UI Components ---

const Card = ({ children, className = '' }: { children: React.ReactNode, className?: string }) => (
    <div className={`bg-black/20 backdrop-blur-md border border-cyan-500/20 rounded-xl shadow-lg shadow-cyan-500/5 ${className}`}>
        {children}
    </div>
);

const AddCompetitorModal = ({ isOpen, onClose, onAdd }: { isOpen: boolean, onClose: () => void, onAdd: (data: any) => void }) => {
    const [name, setName] = useState('');
    const [url, setUrl] = useState('');

    if (!isOpen) return null;

    const handleSubmit = (e: React.FormEvent) => {
        e.preventDefault();
        onAdd({ name, website_url: url });
        setName('');
        setUrl('');
        onClose();
    };

    return (
        <div className="fixed inset-0 bg-black/70 backdrop-blur-sm flex items-center justify-center z-50">
            <Card className="w-full max-w-md p-6 border-cyan-500/50">
                <h2 className="text-2xl font-bold mb-4 text-cyan-300">Новый конкурент</h2>
                <form onSubmit={handleSubmit}>
                    <div className="mb-4">
                        <label className="block text-sm font-medium text-gray-300 mb-1">Название</label>
                        <input type="text" value={name} onChange={e => setName(e.target.value)} className="w-full bg-gray-900 border border-gray-700 rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-cyan-500" required />
                    </div>
                    <div className="mb-6">
                        <label className="block text-sm font-medium text-gray-300 mb-1">Сайт (URL)</label>
                        <input type="url" value={url} onChange={e => setUrl(e.target.value)} className="w-full bg-gray-900 border border-gray-700 rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-cyan-500" placeholder="https://competitor.com" required />
                    </div>
                    <div className="flex justify-end gap-4">
                        <button type="button" onClick={onClose} className="px-4 py-2 rounded-lg text-gray-300 hover:bg-gray-700">Отмена</button>
                        <NeonButton type="submit">Добавить</NeonButton>
                    </div>
                </form>
            </Card>
        </div>
    );
};

// --- Main Page Component ---

export default function CompetitorsPage() {
    const [isModalOpen, setIsModalOpen] = useState(false);
    const queryClient = useQueryClient();

    // Fetch real competitors from API
    const { data: competitors, isLoading: isLoadingCompetitors } = useQuery({
        queryKey: ["competitors"],
        queryFn: () => api.get("/competitors").then(res => res.data),
    });

    const addCompetitorMutation = useMutation({
        mutationFn: (newCompetitor: any) => api.post("/competitors", newCompetitor).then(res => res.data),
        onSuccess: () => queryClient.invalidateQueries({ queryKey: ["competitors"] }),
    });

    const deleteCompetitorMutation = useMutation({
        mutationFn: (id: string) => api.delete(`/competitors/${id}`),
        onSuccess: () => queryClient.invalidateQueries({ queryKey: ["competitors"] }),
    });

    const scanCompetitorMutation = useMutation({
        mutationFn: (id: string) => api.post(`/competitors/${id}/scan`).then(res => res.data),
        onSuccess: () => {
            // Refetch competitors after scan
            setTimeout(() => {
                queryClient.invalidateQueries({ queryKey: ["competitors"] });
            }, 3000);
        },
    });

    return (
        <div className="min-h-screen p-4 sm:p-6 lg:p-8 bg-gray-900 text-white font-sans">
            <div className="max-w-7xl mx-auto">
                <div className="flex justify-between items-center mb-8">
                    <h1 className="text-4xl font-bold text-cyan-300 drop-shadow-[0_0_5px_rgba(0,255,255,0.3)]">
                        Анализ конкурентов
                    </h1>
                    <NeonButton onClick={() => setIsModalOpen(true)}>
                        <Plus size={18} />
                        Добавить
                    </NeonButton>
                </div>

                <div className="space-y-6">
                    {isLoadingCompetitors && (
                        <Card className="p-6 text-center">
                            <Loader2 className="animate-spin mx-auto text-cyan-400" size={32} />
                            <p className="text-gray-400 mt-2">Загрузка конкурентов...</p>
                        </Card>
                    )}
                    {!isLoadingCompetitors && (!competitors || competitors.length === 0) && (
                        <Card className="p-6 text-center text-gray-500">
                            <p>Пока нет конкурентов. Нажмите "+" чтобы добавить первого.</p>
                        </Card>
                    )}
                    {competitors?.map((competitor: any) => (
                        <Card key={competitor.id} className="p-6">
                            <div className="flex justify-between items-center mb-4">
                                <div>
                                    <h3 className="font-bold text-2xl text-cyan-300">{competitor.name}</h3>
                                    <p className="text-sm text-gray-400 break-all">{competitor.website_url || 'No URL'}</p>
                                </div>
                                <div className="flex items-center gap-2">
                                    <NeonButton onClick={() => scanCompetitorMutation.mutate(competitor.id)} isLoading={scanCompetitorMutation.isPending && scanCompetitorMutation.variables === competitor.id} className="px-3 py-1.5 text-sm">
                                        <Zap size={18} /> Сканировать
                                    </NeonButton>
                                    <NeonButton onClick={() => deleteCompetitorMutation.mutate(competitor.id)} className="px-3 py-1.5 text-sm bg-red-500/10 border-red-500/50 hover:bg-red-500/20">
                                        <Trash2 size={18} /> Удалить
                                    </NeonButton>
                                </div>
                            </div>

                            {competitor.last_scanned ? (
                                <div className="mt-4 border-t border-cyan-500/20 pt-4">
                                    <p className="text-xs text-gray-500">
                                        Последнее сканирование: {new Date(competitor.last_scanned).toLocaleString()}
                                    </p>
                                </div>
                            ) : (
                                <div className="mt-4 border-t border-cyan-500/20 pt-4 bg-gray-800/30 rounded-lg p-4 text-center">
                                    <p className="text-gray-400 text-sm">
                                        Нажмите "Сканировать" для анализа конкурента и получения рекомендаций AI
                                    </p>
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
