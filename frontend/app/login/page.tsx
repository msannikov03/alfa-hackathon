"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { Loader2 } from "lucide-react";
import type { AxiosError } from "axios";

import api from "@/lib/api";

interface LoginResponse {
  access_token: string;
  token_type: string;
  user_id: number;
  username: string;
}

export default function LoginPage() {
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);
  const router = useRouter();

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    setError("");
    setLoading(true);

    try {
      const { data } = await api.post<LoginResponse>("/auth/login", {
        username,
        password,
      });

      localStorage.setItem("token", data.access_token);
      localStorage.setItem("user_id", data.user_id.toString());
      localStorage.setItem("username", data.username);
      router.push("/dashboard");
    } catch (err) {
      const message = extractErrorMessage(err);
      setError(message);
      console.error("Login error:", err);
    } finally {
      setLoading(false);
    }
  };

  const extractErrorMessage = (err: unknown) => {
    const fallback = "Login failed. Please check your credentials.";

    const axiosError = err as AxiosError<{ detail?: string }>;
    if (axiosError?.response?.data?.detail) {
      return axiosError.response.data.detail;
    }

    if (axiosError?.message?.toLowerCase().includes("network")) {
      return "Network error. Please make sure the backend is running.";
    }

    return fallback;
  };

  return (
    <div className="min-h-screen bg-background text-foreground flex items-center justify-center p-4">
      <div className="w-full max-w-md">
        <div className="mb-8">
          <h1 className="text-3xl font-semibold text-balance mb-2">
            Добро пожаловать в Alfa Intelligence
          </h1>
          <p className="text-muted-foreground text-base">
            Войдите в панель управления вашего бизнес-помощника
          </p>
        </div>

        {error && (
          <div className="mb-6 p-4 bg-destructive/10 border border-destructive/30 rounded-lg">
            <p className="text-sm text-destructive font-medium">{error}</p>
          </div>
        )}

        <form onSubmit={handleLogin} className="space-y-5">
          <div className="space-y-2">
            <label htmlFor="username" className="block text-sm font-medium">
              Имя пользователя
            </label>
            <input
              id="username"
              type="text"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              required
              className="w-full px-4 py-2.5 bg-input border border-border rounded-lg text-foreground placeholder-muted-foreground focus:outline-none focus:border-primary focus:ring-2 focus:ring-primary/20 transition duration-200"
              placeholder="Введите имя пользователя"
            />
          </div>

          <div className="space-y-2">
            <label htmlFor="password" className="block text-sm font-medium">
              Пароль
            </label>
            <input
              id="password"
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
              className="w-full px-4 py-2.5 bg-input border border-border rounded-lg text-foreground placeholder-muted-foreground focus:outline-none focus:border-primary focus:ring-2 focus:ring-primary/20 transition duration-200"
              placeholder="Введите пароль"
            />
          </div>

          <button
            type="submit"
            disabled={loading}
            className="w-full py-2.5 px-4 mt-6 rounded-lg font-semibold text-primary-foreground bg-primary hover:bg-primary/90 transition-colors duration-200 disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2"
          >
            {loading ? (
              <>
                <Loader2 className="w-4 h-4 animate-spin" />
                Вход...
              </>
            ) : (
              "Войти"
            )}
          </button>
        </form>

        <div className="mt-8 p-4 bg-muted border border-border rounded-lg">
          <p className="text-xs font-semibold text-muted-foreground uppercase tracking-wider mb-3">
            Демо-аккаунт
          </p>
          <div className="space-y-2 mb-4">
            <div className="flex justify-between items-center text-sm">
              <span className="text-muted-foreground">Логин:</span>
              <code className="bg-background px-2 py-1 rounded text-primary font-mono text-xs">
                demo_admin
              </code>
            </div>
            <div className="flex justify-between items-center text-sm">
              <span className="text-muted-foreground">Пароль:</span>
              <code className="bg-background px-2 py-1 rounded text-primary font-mono text-xs">
                demo123
              </code>
            </div>
          </div>
          <button
            type="button"
            onClick={() => {
              setUsername("demo_admin");
              setPassword("demo123");
            }}
            className="w-full py-2 px-3 bg-secondary hover:bg-secondary/90 text-secondary-foreground text-sm font-medium rounded-lg transition duration-200 border border-border"
          >
            Использовать демо-аккаунт
          </button>
        </div>

        <div className="mt-6 pt-6 border-t border-border text-center">
          <p className="text-xs text-muted-foreground">
            Нужна помощь? Напишите вашему{" "}
            <span className="text-primary font-medium">Telegram боту</span> или
            используйте{" "}
            <code className="bg-muted px-1.5 py-0.5 rounded text-primary font-mono text-xs">
              /setpassword
            </code>
          </p>
        </div>
      </div>
    </div>
  );
}
