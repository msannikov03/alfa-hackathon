"use client";
import { useState } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { Upload, Bot, Loader2, BarChart, FileCheck2, AlertTriangle, CheckCircle } from "lucide-react";
import dynamic from 'next/dynamic';
import { NeonButton } from "@/components/ui/button";
import api from "@/lib/api";

// Dynamically import LineChart with SSR disabled
const DynamicLineChart = dynamic(() =>
    import('recharts').then(mod => mod.LineChart),
    { ssr: false }
);
const DynamicResponsiveContainer = dynamic(() =>
    import('recharts').then(mod => mod.ResponsiveContainer),
    { ssr: false }
);
const DynamicLine = dynamic(() =>
    import('recharts').then(mod => mod.Line),
    { ssr: false }
);
const DynamicXAxis = dynamic(() =>
    import('recharts').then(mod => mod.XAxis),
    { ssr: false }
);
const DynamicYAxis = dynamic(() =>
    import('recharts').then(mod => mod.YAxis),
    { ssr: false }
);
const DynamicCartesianGrid = dynamic(() =>
    import('recharts').then(mod => mod.CartesianGrid),
    { ssr: false }
);
const DynamicTooltip = dynamic(() =>
    import('recharts').then(mod => mod.Tooltip),
    { ssr: false }
);
const DynamicLegend = dynamic(() =>
    import('recharts').then(mod => mod.Legend),
    { ssr: false }
);
const DynamicReferenceLine = dynamic(() =>
    import('recharts').then(mod => mod.ReferenceLine),
    { ssr: false }
);

// --- UI Components ---
const Card = ({ children, className = '' }: { children: React.ReactNode, className?: string }) => (
    <div className={`bg-black/20 backdrop-blur-md border border-cyan-500/20 rounded-xl shadow-lg shadow-cyan-500/5 ${className}`}>
        {children}
    </div>
);

// --- Page States ---
type PageState = 'initial' | 'mapping' | 'forecasting' | 'results';

export default function FinancePage() {
    const [pageState, setPageState] = useState<PageState>('initial');
    const [file, setFile] = useState<File | null>(null);
    const [mapping, setMapping] = useState<any>(null);
    const [currentBalance, setCurrentBalance] = useState('');
    const queryClient = useQueryClient();

    const { data: forecastData, refetch: refetchForecast } = useQuery({
        queryKey: ["financeForecast"],
        queryFn: () => api.get("/finance/forecast").then(res => res.data),
        enabled: false, // Initially disabled
    });

    const mappingMutation = useMutation({
        mutationFn: (file: File) => {
            const formData = new FormData();
            formData.append('file', file);
            return api.post("/finance/upload-csv", formData, {
                headers: { 'Content-Type': 'multipart/form-data' },
            });
        },
        onSuccess: (data) => {
            setMapping(data.data.mapping);
            setPageState('mapping');
        },
    });

    const forecastMutation = useMutation({
        mutationFn: () => {
            const formData = new FormData();
            formData.append('file', file!);
            formData.append('mapping', JSON.stringify(mapping));
            formData.append('current_balance', currentBalance);
            return api.post("/finance/forecast", formData, {
                headers: { 'Content-Type': 'multipart/form-data' },
            });
        },
        onSuccess: () => {
            queryClient.invalidateQueries({ queryKey: ["financeForecast"] });
            refetchForecast();
            setPageState('results');
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
            <h2 className="text-2xl font-bold text-cyan-300 mb-4">Начать прогноз</h2>
            <p className="text-gray-400 mb-6">Загрузите выписку из вашего банка или CRM в формате CSV.</p>
            <label htmlFor="csv-upload" className="cursor-pointer">
                <NeonButton onClick={() => document.getElementById('csv-upload')?.click()} isLoading={mappingMutation.isPending}>
                    <Upload size={18} />
                    Загрузить CSV
                </NeonButton>
            </label>
            <input id="csv-upload" type="file" accept=".csv" className="hidden" onChange={handleFileChange} />
        </Card>
    );

    const renderMappingState = () => (
        <Card className="p-8">
            <div className="flex items-center gap-3 mb-4">
                <Bot size={24} className="text-cyan-400" />
                <h2 className="text-2xl font-bold text-cyan-300">AI определил структуру файла</h2>
            </div>
            <p className="text-gray-400 mb-6">Проверьте, правильно ли система сопоставила колонки вашего файла.</p>
            <div className="space-y-2 p-4 rounded-lg bg-gray-800/50 border border-gray-700">
                <p><span className="font-mono text-gray-500">Дата:</span> {mapping.date_column}</p>
                <p><span className="font-mono text-gray-500">Описание:</span> {mapping.description_column}</p>
                {mapping.amount_logic.type === 'single_column' ? (
                    <p><span className="font-mono text-gray-500">Сумма:</span> {mapping.amount_logic.amount_column}</p>
                ) : (
                    <>
                        <p><span className="font-mono text-gray-500">Доход:</span> {mapping.amount_logic.income_column}</p>
                        <p><span className="font-mono text-gray-500">Расход:</span> {mapping.amount_logic.expense_column}</p>
                    </>
                )}
            </div>
            <div className="mt-6">
                <label className="block text-sm font-medium text-gray-300 mb-1">Текущий баланс</label>
                <input type="number" value={currentBalance} onChange={e => setCurrentBalance(e.target.value)} className="w-full bg-gray-900 border border-gray-700 rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-cyan-500" placeholder="100000" />
            </div>
            <div className="flex justify-end gap-4 mt-6">
                <NeonButton onClick={() => setPageState('initial')} className="bg-gray-600/10 border-gray-600/50">Отмена</NeonButton>
                <NeonButton onClick={() => forecastMutation.mutate()} isLoading={forecastMutation.isPending} disabled={!currentBalance}>
                    <BarChart size={18} />
                    Создать прогноз
                </NeonButton>
            </div>
        </Card>
    );

    const renderResultsState = () => (
        <div>
            <Card className="p-6 mb-6">
                <h3 className="text-xl font-bold text-cyan-300 mb-4">Прогноз на 7 дней</h3>
                <DynamicResponsiveContainer width="100%" height={300}>
                    <DynamicLineChart data={forecastData?.predicted_data}>
                        <DynamicCartesianGrid strokeDasharray="3 3" stroke="rgba(0, 255, 255, 0.1)" />
                        <DynamicXAxis dataKey="date" tickFormatter={(str) => new Date(str).toISOString().split('T')[0]} stroke="#9ca3af" />
                        <DynamicYAxis stroke="#9ca3af" />
                        <DynamicTooltip contentStyle={{ backgroundColor: '#1f2937', border: '1px solid #4b5563' }} />
                        <DynamicLegend />
                        <DynamicReferenceLine y={0} stroke="#ef4444" strokeDasharray="4 4" />
                        <DynamicLine type="monotone" dataKey="balance" stroke="#06b6d4" strokeWidth={2} dot={{ r: 4 }} name="Баланс" />
                    </DynamicLineChart>
                </DynamicResponsiveContainer>
            </Card>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <Card className="p-6">
                    <h3 className="text-xl font-bold text-cyan-300 mb-4 flex items-center gap-2"><AlertTriangle className="text-red-400" /> Риски</h3>
                    <ul className="space-y-2">
                        {forecastData?.insights.risks.map((risk: any, i: number) => (
                            <li key={i} className="text-red-300">{risk.message}</li>
                        ))}
                        {forecastData?.insights.risks.length === 0 && <p className="text-gray-500">Значительных рисков не обнаружено.</p>}
                    </ul>
                </Card>
                <Card className="p-6">
                    <h3 className="text-xl font-bold text-cyan-300 mb-4 flex items-center gap-2"><CheckCircle className="text-green-400" /> Рекомендации</h3>
                    <ul className="space-y-2">
                        {forecastData?.insights.recommendations.map((rec: any, i: number) => (
                            <li key={i} className="text-green-300">{rec.message}</li>
                        ))}
                         {forecastData?.insights.recommendations.length === 0 && <p className="text-gray-500">Рекомендаций нет.</p>}
                    </ul>
                </Card>
            </div>
        </div>
    );

    const renderContent = () => {
        switch (pageState) {
            case 'initial': return renderInitialState();
            case 'mapping': return renderMappingState();
            case 'results': return renderResultsState();
            default: return renderInitialState();
        }
    };

    return (
        <div className="min-h-screen p-4 sm:p-6 lg:p-8 bg-gray-900 text-white font-sans">
            <div className="max-w-7xl mx-auto">
                <div className="flex justify-between items-center mb-8">
                    <h1 className="text-4xl font-bold text-cyan-300 drop-shadow-[0_0_5px_rgba(0,255,255,0.3)]">
                        Финансовый предиктор
                    </h1>
                    {pageState === 'results' && (
                        <NeonButton onClick={() => setPageState('initial')}>Начать заново</NeonButton>
                    )}
                </div>
                {renderContent()}
            </div>
        </div>
    );
}