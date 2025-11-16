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

    // Dummy data for demonstration as backend is not active
    const [dummyCompetitors, setDummyCompetitors] = useState([
        {
            id: '1',
            name: 'Кофемания',
            website_url: 'https://www.coffeemania.ru',
            their_advantages: ['Широкая сеть заведений', 'Высокий уровень сервиса', 'Известный бренд'],
            our_advantages: ['Более низкие цены', 'Уникальные сорта кофе', 'Уютная атмосфера'],
            ai_actions: ['Запустить акцию "Кофе с собой за полцены" в утренние часы.', 'Предложить программу лояльности для постоянных клиентов.', 'Активно продвигать уникальные сорта кофе в соцсетях.'],
        },
        {
            id: '2',
            name: 'Шоколадница',
            website_url: 'https://shoko.ru',
            their_advantages: ['Разнообразное меню (еда)', 'Удобное расположение', 'Большая проходимость'],
            our_advantages: ['Более современный дизайн', 'Быстрое обслуживание', 'Фокус на качестве кофе'],
            ai_actions: ['Разработать комбо-предложения "кофе + десерт" для увеличения среднего чека.', 'Улучшить скорость обслуживания в часы пик.', 'Провести дегустацию новых десертов.'],
        },
        {
            id: '3',
            name: 'Starbucks',
            website_url: 'https://www.starbucks.ru',
            their_advantages: ['Мировой бренд', 'Мобильное приложение', 'Персонализация напитков'],
            our_advantages: ['Более гибкая ценовая политика', 'Локальная адаптация меню', 'Более тесное взаимодействие с комьюнити'],
            ai_actions: ['Запустить локальную рекламную кампанию с акцентом на уникальность.', 'Предложить кастомизацию напитков, недоступную у конкурента.', 'Организовать мероприятия для местного сообщества.'],
        },
    ]);

    const addCompetitorMutation = useMutation({
        mutationFn: (newCompetitor: any) => {
            // Simulate API call and add to dummy data
            return new Promise(resolve => setTimeout(() => {
                const newId = (dummyCompetitors.length + 1).toString();
                const newComp = {
                    ...newCompetitor,
                    id: newId,
                    their_advantages: ['(AI-анализ в процессе)'],
                    our_advantages: ['(AI-анализ в процессе)'],
                    ai_actions: ['(AI-анализ в процессе)'],
                };
                setDummyCompetitors(prev => [...prev, newComp]);
                resolve(newComp);
            }, 500));
        },
        onSuccess: () => queryClient.invalidateQueries({ queryKey: ["competitors"] }),
    });

    const deleteCompetitorMutation = useMutation({
        mutationFn: (id: string) => {
            // Simulate API call and remove from dummy data
            return new Promise(resolve => setTimeout(() => {
                setDummyCompetitors(prev => prev.filter(comp => comp.id !== id));
                resolve(true);
            }, 500));
        },
        onSuccess: () => queryClient.invalidateQueries({ queryKey: ["competitors"] }),
    });

    // No actual scan mutation needed for dummy data, but keep the button for UI
    const scanCompetitorMutation = useMutation({
        mutationFn: (id: string) => {
            return new Promise(resolve => setTimeout(() => {
                console.log(`Simulating scan for ${id}`);
                resolve(true);
            }, 1000));
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
                    {dummyCompetitors.length === 0 && (
                        <Card className="p-6 text-center text-gray-500">
                            <p>Пока нет конкурентов. Нажмите "+" чтобы добавить первого.</p>
                        </Card>
                    )}
                    {dummyCompetitors.map((competitor) => (
                        <Card key={competitor.id} className="p-6">
                            <div className="flex justify-between items-center mb-4">
                                <div>
                                    <h3 className="font-bold text-2xl text-cyan-300">{competitor.name}</h3>
                                    <p className="text-sm text-gray-400 break-all">{competitor.website_url || 'No URL'}</p>
                                </div>
                                <div className="flex items-center gap-2">
                                    <NeonButton size="sm" onClick={() => scanCompetitorMutation.mutate(competitor.id)} isLoading={scanCompetitorMutation.isPending && scanCompetitorMutation.variables === competitor.id}>
                                        <Zap size={18} /> Сканировать
                                    </NeonButton>
                                    <NeonButton size="sm" onClick={() => deleteCompetitorMutation.mutate(competitor.id)} className="bg-red-500/10 border-red-500/50 hover:bg-red-500/20">
                                        <Trash2 size={18} /> Удалить
                                    </NeonButton>
                                </div>
                            </div>

                            <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mt-4 border-t border-cyan-500/20 pt-4">
                                <div>
                                    <h4 className="font-semibold text-lg text-gray-300 flex items-center gap-2 mb-2"><TrendingDown size={20} className="text-red-400" /> Их преимущества</h4>
                                    <ul className="list-disc list-inside text-sm text-gray-400 space-y-1">
                                        {competitor.their_advantages.map((adv, i) => <li key={i}>{adv}</li>)}
                                    </ul>
                                </div>
                                <div>
                                    <h4 className="font-semibold text-lg text-gray-300 flex items-center gap-2 mb-2"><TrendingUp size={20} className="text-green-400" /> Наши преимущества</h4>
                                    <ul className="list-disc list-inside text-sm text-gray-400 space-y-1">
                                        {competitor.our_advantages.map((adv, i) => <li key={i}>{adv}</li>)}
                                    </ul>
                                </div>
                                <div>
                                    <h4 className="font-semibold text-lg text-gray-300 flex items-center gap-2 mb-2"><Lightbulb size={20} className="text-yellow-400" /> Действия AI</h4>
                                    <ul className="list-disc list-inside text-sm text-gray-400 space-y-1">
                                        {competitor.ai_actions.map((action, i) => <li key={i}>{action}</li>)}
                                    </ul>
                                </div>
                            </div>
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
