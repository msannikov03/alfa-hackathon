"use client";
import { useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { motion, AnimatePresence } from "framer-motion";
import { Zap, Cpu, Scale, Landmark, Users, AlertTriangle, CheckCircle, Lightbulb } from "lucide-react";
import { NeonButton } from "@/components/ui/button";
import api from "@/lib/api";

// --- UI Components ---
const Card = ({ children, className = '' }: { children: React.ReactNode, className?: string }) => (
    <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        exit={{ opacity: 0, y: -20 }}
        className={`bg-black/20 backdrop-blur-md border border-cyan-500/20 rounded-xl shadow-lg shadow-cyan-500/5 ${className}`}
    >
        {children}
    </motion.div>
);

const InsightTypeIcon = ({ type }: { type: string }) => {
    switch (type) {
        case 'Opportunity': return <Lightbulb className="text-green-400" />;
        case 'Threat': return <AlertTriangle className="text-red-400" />;
        case 'Efficiency Improvement': return <CheckCircle className="text-blue-400" />;
        default: return <Zap className="text-gray-400" />;
    }
};

// --- Page States ---
type PageState = 'initial' | 'analyzing' | 'results';

const analysisSteps = [
    { text: "Parsing competitor actions...", icon: <Users /> },
    { text: "Correlating financial data...", icon: <Landmark /> },
    { text: "Synthesizing legal impacts...", icon: <Scale /> },
    { text: "Identifying strategic vectors...", icon: <Cpu /> },
];

export default function TrendsPage() {
    const [pageState, setPageState] = useState<PageState>('initial');

    const { data: trends, isLoading, isError, refetch } = useQuery({
        queryKey: ["trends"],
        queryFn: () => api.get("/trends").then(res => res.data),
        enabled: false, // Only fetch when the button is clicked
    });

    const handleAnalyze = () => {
        setPageState('analyzing');
        refetch().then(() => {
            setPageState('results');
        });
    };

    const renderInitialState = () => (
        <div className="flex flex-col items-center justify-center h-[60vh]">
            <motion.div initial={{ opacity: 0, scale: 0.8 }} animate={{ opacity: 1, scale: 1 }} transition={{ duration: 0.5 }}>
                <NeonButton onClick={handleAnalyze} isLoading={isLoading}>
                    <Zap size={20} />
                    Начать анализ трендов
                </NeonButton>
            </motion.div>
        </div>
    );

    const renderAnalyzingState = () => (
        <div className="flex flex-col items-center justify-center h-[60vh]">
            <motion.div
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                className="flex flex-col items-center gap-4"
            >
                <Cpu size={48} className="text-cyan-400 animate-pulse" />
                <AnimatePresence mode="wait">
                    {analysisSteps.map((step, index) => (
                        <motion.div
                            key={step.text}
                            initial={{ opacity: 0, y: 20 }}
                            animate={{ opacity: 1, y: 0 }}
                            transition={{ delay: index * 1.5, duration: 0.5 }}
                            className="flex items-center gap-2 text-lg text-gray-300"
                        >
                            {step.icon} {step.text}
                        </motion.div>
                    ))}
                </AnimatePresence>
            </motion.div>
        </div>
    );

    const renderResultsState = () => (
        <motion.div layout className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            {isError && <p className="text-red-500">Ошибка при анализе трендов.</p>}
            {trends?.map((trend: any, index: number) => (
                <Card key={index} className="p-6 flex flex-col">
                    <div className="flex items-start justify-between mb-3">
                        <h3 className="text-xl font-bold text-cyan-300 pr-4">{trend.title}</h3>
                        <InsightTypeIcon type={trend.insight_type} />
                    </div>
                    <p className="text-sm text-gray-400 mb-4 flex-grow">"{trend.observation}"</p>
                    <div className="mt-auto pt-4 border-t border-cyan-500/20">
                        <h4 className="font-semibold text-cyan-400 mb-2">Рекомендация:</h4>
                        <p className="text-sm text-gray-200 bg-gray-800/50 p-3 rounded-lg">{trend.recommendation.action}</p>
                        <p className="text-xs text-gray-500 mt-2">{trend.recommendation.justification}</p>
                    </div>
                </Card>
            ))}
        </motion.div>
    );

    const renderContent = () => {
        if (isLoading || pageState === 'analyzing') return renderAnalyzingState();
        if (pageState === 'results') return renderResultsState();
        return renderInitialState();
    };

    return (
        <div className="min-h-screen p-4 sm:p-6 lg:p-8 bg-gray-900 text-white font-sans">
            <div className="max-w-7xl mx-auto">
                <div className="flex justify-between items-center mb-8">
                    <h1 className="text-4xl font-bold text-cyan-300 drop-shadow-[0_0_5px_rgba(0,255,255,0.3)]">
                        Стратегические тренды
                    </h1>
                    {pageState === 'results' && (
                        <NeonButton onClick={() => setPageState('initial')}>Анализировать заново</NeonButton>
                    )}
                </div>
                <AnimatePresence mode="wait">
                    {renderContent()}
                </AnimatePresence>
            </div>
        </div>
    );
}