"use client";

import Link from "next/link";
import { usePathname, useRouter } from "next/navigation";
import {
  Shield,
  LineChart,
  Landmark,
  Users,
  Settings,
  LayoutDashboard,
  LogOut,
  Bot,
  UserCircle,
} from "lucide-react";
import {
  Tooltip,
  TooltipContent,
  TooltipProvider,
  TooltipTrigger,
} from "@/components/ui/tooltip";

const navItems = [
  { href: "/dashboard", icon: LayoutDashboard, label: "Главная" },
  { href: "/dashboard/profile", icon: UserCircle, label: "Профиль" },
  { href: "/dashboard/assistant", icon: Bot, label: "AI Ассистент" },
  { href: "/dashboard/competitors", icon: Users, label: "Конкуренты" },
  { href: "/dashboard/legal", icon: Shield, label: "Законы" },
  { href: "/dashboard/finance", icon: Landmark, label: "Финансы" },
  { href: "/dashboard/trends", icon: LineChart, label: "Тренды" },
];

const Sidebar = () => {
  const pathname = usePathname();
  const router = useRouter();

  const handleLogout = () => {
    localStorage.removeItem("token");
    localStorage.removeItem("user_id");
    localStorage.removeItem("username");
    router.push("/");
  };

  return (
    <aside className="fixed inset-y-0 left-0 z-10 hidden md:flex flex-col border-r border-border bg-card w-16 backdrop-blur-sm">
      <nav className="flex flex-col items-center gap-2 px-2 py-6">
        <Link
          href="/dashboard"
          className="group flex h-10 w-10 shrink-0 items-center justify-center gap-2 rounded-lg bg-primary text-base font-bold text-primary-foreground transition-all duration-300 hover:shadow-lg hover:shadow-primary/30 mb-2"
        >
          A<span className="sr-only">Alfa Intelligence</span>
        </Link>
        <div className="w-8 h-px bg-border my-2" />
        <TooltipProvider>
          {navItems.map((item) => (
            <Tooltip key={item.href}>
              <TooltipTrigger asChild>
                <Link
                  href={item.href}
                  className={`flex h-10 w-10 items-center justify-center rounded-lg transition-all duration-200 ${
                    pathname === item.href
                      ? "bg-primary/20 text-primary shadow-lg shadow-primary/20"
                      : "text-muted-foreground hover:text-foreground hover:bg-muted"
                  }`}
                >
                  <item.icon className="h-5 w-5" />
                  <span className="sr-only">{item.label}</span>
                </Link>
              </TooltipTrigger>
              <TooltipContent side="right" className="font-medium">
                {item.label}
              </TooltipContent>
            </Tooltip>
          ))}
        </TooltipProvider>
      </nav>
      <nav className="mt-auto flex flex-col items-center gap-2 px-2 py-6">
        <div className="w-8 h-px bg-border my-2" />
        <TooltipProvider>
          <Tooltip>
            <TooltipTrigger asChild>
              <Link
                href="/dashboard/settings"
                className={`flex h-10 w-10 items-center justify-center rounded-lg transition-all duration-200 ${
                  pathname === "/dashboard/settings"
                    ? "bg-primary/20 text-primary shadow-lg shadow-primary/20"
                    : "text-muted-foreground hover:text-foreground hover:bg-muted"
                }`}
              >
                <Settings className="h-5 w-5" />
                <span className="sr-only">Settings</span>
              </Link>
            </TooltipTrigger>
            <TooltipContent side="right" className="font-medium">
              Settings
            </TooltipContent>
          </Tooltip>
          <Tooltip>
            <TooltipTrigger asChild>
              <button
                onClick={handleLogout}
                className="flex h-10 w-10 items-center justify-center rounded-lg text-muted-foreground hover:text-foreground hover:bg-muted transition-all duration-200"
              >
                <LogOut className="h-5 w-5" />
                <span className="sr-only">Logout</span>
              </button>
            </TooltipTrigger>
            <TooltipContent side="right" className="font-medium">
              Logout
            </TooltipContent>
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
    <div className="flex min-h-screen w-full bg-background">
      <Sidebar />
      <main className="flex-1 md:pl-16">{children}</main>
    </div>
  );
}
