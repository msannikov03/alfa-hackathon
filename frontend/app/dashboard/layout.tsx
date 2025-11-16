"use client";

import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { Shield, LineChart, Landmark, Users, Settings, LayoutDashboard } from 'lucide-react';
import { Tooltip, TooltipContent, TooltipProvider, TooltipTrigger } from '@/components/ui/tooltip';

const navItems = [
    { href: '/dashboard', icon: LayoutDashboard, label: 'Главная' },
    { href: '/dashboard/competitors', icon: Users, label: 'Конкуренты' },
    { href: '/dashboard/legal', icon: Shield, label: 'Законы' },
    { href: '/dashboard/finance', icon: Landmark, label: 'Финансы' },
    { href: '/dashboard/trends', icon: LineChart, label: 'Тренды' },
];

const Sidebar = () => {
    const pathname = usePathname();

    return (
        <aside className="fixed inset-y-0 left-0 z-10 flex-col border-r border-cyan-500/20 bg-gray-900/80 backdrop-blur-lg hidden md:flex">
            <nav className="flex flex-col items-center gap-4 px-2 sm:py-5">
                <Link
                    href="/dashboard/settings"
                    className="group flex h-9 w-9 shrink-0 items-center justify-center gap-2 rounded-full bg-gradient-to-r from-cyan-500 to-blue-500 text-lg font-semibold text-white md:h-8 md:w-8 md:text-base"
                >
                    A
                    <span className="sr-only">Alfa Intelligence</span>
                </Link>
                <TooltipProvider>
                    {navItems.map(item => (
                        <Tooltip key={item.href}>
                            <TooltipTrigger asChild>
                                <Link
                                    href={item.href}
                                    className={`flex h-9 w-9 items-center justify-center rounded-lg transition-colors md:h-8 md:w-8 ${
                                        pathname === item.href
                                            ? 'bg-cyan-500/20 text-cyan-300'
                                            : 'text-gray-400 hover:text-white'
                                    }`}
                                >
                                    <item.icon className="h-5 w-5" />
                                    <span className="sr-only">{item.label}</span>
                                </Link>
                            </TooltipTrigger>
                            <TooltipContent side="right">{item.label}</TooltipContent>
                        </Tooltip>
                    ))}
                </TooltipProvider>
            </nav>
            <nav className="mt-auto flex flex-col items-center gap-4 px-2 sm:py-5">
                <TooltipProvider>
                    <Tooltip>
                        <TooltipTrigger asChild>
                            <Link
                                href="/dashboard/settings"
                                className={`flex h-9 w-9 items-center justify-center rounded-lg transition-colors md:h-8 md:w-8 ${
                                    pathname === '/dashboard/settings'
                                        ? 'bg-cyan-500/20 text-cyan-300'
                                        : 'text-gray-400 hover:text-white'
                                }`}
                            >
                                <Settings className="h-5 w-5" />
                                <span className="sr-only">Настройки</span>
                            </Link>
                        </TooltipTrigger>
                        <TooltipContent side="right">Настройки</TooltipContent>
                    </Tooltip>
                </TooltipProvider>
            </nav>
        </aside>
    );
};


export default function DashboardLayout({
    children,
}: {
    children: React.ReactNode;
}) {
    return (
        <div className="flex min-h-screen w-full">
            <Sidebar />
            <main className="flex-1 md:pl-14">
                {children}
            </main>
        </div>
    );
}
