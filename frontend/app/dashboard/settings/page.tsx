"use client";
import { useState } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { Settings as SettingsIcon, User, Save, Loader2, Bot } from "lucide-react";
import api from "@/lib/api";
import { NeonButton } from "@/components/ui/button";

// --- UI Components ---
const Card = ({ children, className = '' }: { children: React.ReactNode, className?: string }) => (
    <div className={`bg-black/20 backdrop-blur-md border border-cyan-500/20 rounded-xl shadow-lg shadow-cyan-500/5 ${className}`}>
        {children}
    </div>
);

export default function SettingsPage() {
    const [rawDescription, setRawDescription] = useState('');
    const queryClient = useQueryClient();

    const { data: context, isLoading: isLoadingContext } = useQuery({
        queryKey: ["businessContext"],
        queryFn: () => api.get("/v1/legal/business-context").then(res => {
            setRawDescription(res.data.raw_description);
            return res.data;
        }),
    });

    const updateContextMutation = useMutation({
        mutationFn: (description: string) => api.post("/v1/legal/business-context", { raw_description: description }),
        onSuccess: () => queryClient.invalidateQueries({ queryKey: ["businessContext"] }),
    });

    return (
        <div className="min-h-screen p-4 sm:p-6 lg:p-8 bg-gray-900 text-white font-sans">
            <div className="max-w-7xl mx-auto">
                <div className="flex justify-between items-center mb-8">
                    <h1 className="text-4xl font-bold text-cyan-300 drop-shadow-[0_0_5px_rgba(0,255,255,0.3)]">
                        Настройки
                    </h1>
                </div>

                <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                    {/* User Profile Section */}
                    <Card className="p-6">
                        <h2 className="text-2xl font-semibold tracking-tight text-gray-400 border-b-2 border-cyan-500/20 pb-2 mb-4 flex items-center gap-2">
                            <User size={24} /> Профиль пользователя
                        </h2>
                        {isLoadingContext ? ( // Re-using isLoadingContext for user profile as well for simplicity
                            <Loader2 className="animate-spin" />
                        ) : (
                            <div className="space-y-3">
                                <p><span className="font-semibold text-cyan-300">Email:</span> user@example.com</p>
                                <p><span className="font-semibold text-cyan-300">Telegram ID:</span> {process.env.NEXT_PUBLIC_TEMP_USER_ID || '1'}</p>
                                <p className="text-sm text-gray-500">
                                    (В реальном приложении здесь будут отображаться данные текущего пользователя)
                                </p>
                            </div>
                        )}
                    </Card>

                    {/* Business Context Section */}
                    <Card className="p-6">
                        <h2 className="text-2xl font-semibold tracking-tight text-gray-400 border-b-2 border-cyan-500/20 pb-2 mb-4 flex items-center gap-2">
                            <Bot size={24} /> Контекст бизнеса
                        </h2>
                        <p className="text-sm text-gray-400 mb-4">Опишите ваш бизнес в свободной форме. AI проанализирует и структурирует его для точного поиска.</p>
                        <textarea
                            value={rawDescription}
                            onChange={(e) => setRawDescription(e.target.value)}
                            className="w-full h-24 bg-gray-900/80 border border-gray-700 rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-cyan-500"
                            placeholder="Например: 'У меня кофейня в Москве, работаем как ООО...'"
                        />
                        <NeonButton 
                            onClick={() => updateContextMutation.mutate(rawDescription)} 
                            isLoading={updateContextMutation.isPending}
                            disabled={rawDescription === context?.raw_description}
                            className="w-full mt-2"
                        >
                            <Save size={18} />
                            Сохранить и проанализировать
                        </NeonButton>

                        {isLoadingContext && <Loader2 className="animate-spin mt-4" />}
                        {context && (
                            <div className="mt-4 space-y-2 text-sm">
                                <h4 className="font-semibold text-cyan-400">Структурированные данные:</h4>
                                <p><span className="font-mono text-gray-500">Industry:</span> {context.structured_data?.industry}</p>
                                <p><span className="font-mono text-gray-500">Location:</span> {context.structured_data?.location}</p>
                                <p><span className="font-mono text-gray-500">Keywords:</span> {context.structured_data?.keywords?.join(', ')}</p>
                            </div>
                        )}
                    </Card>
                </div>
            </div>
        </div>
    );
}