"use client";

import { useEffect, useState } from "react";

interface TelegramWebApp {
  ready: () => void;
  expand: () => void;
  close: () => void;
  MainButton: {
    text: string;
    show: () => void;
    hide: () => void;
    onClick: (callback: () => void) => void;
  };
  initDataUnsafe: {
    user?: {
      id: number;
      first_name: string;
      last_name?: string;
      username?: string;
    };
  };
  themeParams: {
    bg_color?: string;
    text_color?: string;
    hint_color?: string;
    link_color?: string;
    button_color?: string;
    button_text_color?: string;
  };
}

declare global {
  interface Window {
    Telegram?: {
      WebApp: TelegramWebApp;
    };
  }
}

interface Action {
  id: number;
  action_type: string;
  description: string;
  impact_amount?: number;
  required_approval: boolean;
  was_approved?: boolean;
  executed_at: string;
}

interface Metrics {
  total_actions: number;
  time_saved_hours: number;
  automation_rate: number;
  pending_approvals: number;
}

export default function TelegramApp() {
  const [tg, setTg] = useState<TelegramWebApp | null>(null);
  const [user, setUser] = useState<any>(null);
  const [activeTab, setActiveTab] = useState<"dashboard" | "actions" | "approvals">("dashboard");
  const [actions, setActions] = useState<Action[]>([]);
  const [pendingActions, setPendingActions] = useState<Action[]>([]);
  const [metrics, setMetrics] = useState<Metrics | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // Initialize Telegram WebApp
    if (window.Telegram?.WebApp) {
      const webapp = window.Telegram.WebApp;
      webapp.ready();
      webapp.expand();

      setTg(webapp);
      setUser(webapp.initDataUnsafe.user);

      // Fetch data
      fetchData();
    } else {
      setLoading(false);
    }
  }, []);

  const fetchData = async () => {
    try {
      setLoading(true);

      // Get user ID from Telegram (in production, this would be from the auth)
      const userId = tg?.initDataUnsafe.user?.id || 1;

      // Fetch recent actions
      const actionsRes = await fetch(`/api/v1/actions/recent?user_id=${userId}&limit=10`);
      if (actionsRes.ok) {
        const actionsData = await actionsRes.json();
        setActions(actionsData);
      }

      // Fetch pending approvals
      const pendingRes = await fetch(`/api/v1/actions/pending?user_id=${userId}`);
      if (pendingRes.ok) {
        const pendingData = await pendingRes.json();
        setPendingActions(pendingData);
      }

      // Fetch metrics
      const metricsRes = await fetch(`/api/v1/metrics/performance?user_id=${userId}`);
      if (metricsRes.ok) {
        const metricsData = await metricsRes.json();
        setMetrics(metricsData);
      }
    } catch (error) {
      console.error("Error fetching data:", error);
    } finally {
      setLoading(false);
    }
  };

  const handleApprove = async (actionId: number) => {
    try {
      const res = await fetch(`/api/v1/actions/approve/${actionId}`, {
        method: "POST",
      });

      if (res.ok) {
        // Refresh data
        await fetchData();
        if (tg) {
          tg.MainButton.text = "Approved!";
          tg.MainButton.show();
          setTimeout(() => tg.MainButton.hide(), 2000);
        }
      }
    } catch (error) {
      console.error("Error approving action:", error);
    }
  };

  const handleDecline = async (actionId: number) => {
    try {
      const res = await fetch(`/api/v1/actions/decline/${actionId}`, {
        method: "POST",
      });

      if (res.ok) {
        await fetchData();
      }
    } catch (error) {
      console.error("Error declining action:", error);
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gradient-to-b from-blue-50 to-white">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
          <p className="mt-4 text-gray-600">Загрузка...</p>
        </div>
      </div>
    );
  }

  if (!window.Telegram?.WebApp) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gradient-to-b from-blue-50 to-white p-4">
        <div className="max-w-md bg-white rounded-lg shadow-lg p-8 text-center">
          <h1 className="text-2xl font-bold text-gray-800 mb-4">Alfa Business Assistant</h1>
          <p className="text-gray-600 mb-4">
            This app is designed to run inside Telegram.
          </p>
          <p className="text-sm text-gray-500">
            Please open it from your Telegram bot to access all features.
          </p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-b from-blue-50 to-white">
      {/* Header */}
      <div className="bg-white shadow-sm p-4 mb-4">
        <h1 className="text-2xl font-bold text-gray-800">Alfa Business Assistant</h1>
        {user && (
          <p className="text-sm text-gray-600">
            Привет, {user.first_name}!
          </p>
        )}
      </div>

      {/* Tabs */}
      <div className="flex border-b border-gray-200 mb-4 bg-white">
        <button
          onClick={() => setActiveTab("dashboard")}
          className={`flex-1 py-3 px-4 text-center font-medium ${
            activeTab === "dashboard"
              ? "border-b-2 border-blue-600 text-blue-600"
              : "text-gray-600"
          }`}
        >
          Дашборд
        </button>
        <button
          onClick={() => setActiveTab("actions")}
          className={`flex-1 py-3 px-4 text-center font-medium ${
            activeTab === "actions"
              ? "border-b-2 border-blue-600 text-blue-600"
              : "text-gray-600"
          }`}
        >
          Действия
        </button>
        <button
          onClick={() => setActiveTab("approvals")}
          className={`flex-1 py-3 px-4 text-center font-medium relative ${
            activeTab === "approvals"
              ? "border-b-2 border-blue-600 text-blue-600"
              : "text-gray-600"
          }`}
        >
          Одобрения
          {pendingActions.length > 0 && (
            <span className="absolute top-2 right-2 bg-red-500 text-white text-xs rounded-full w-5 h-5 flex items-center justify-center">
              {pendingActions.length}
            </span>
          )}
        </button>
      </div>

      {/* Content */}
      <div className="p-4">
        {activeTab === "dashboard" && (
          <div className="space-y-4">
            {/* Metrics Cards */}
            <div className="grid grid-cols-2 gap-4">
              <div className="bg-white rounded-lg shadow p-4">
                <p className="text-sm text-gray-600">Всего действий</p>
                <p className="text-2xl font-bold text-gray-800">
                  {metrics?.total_actions || 0}
                </p>
              </div>
              <div className="bg-white rounded-lg shadow p-4">
                <p className="text-sm text-gray-600">Время сэкономлено</p>
                <p className="text-2xl font-bold text-blue-600">
                  {metrics?.time_saved_hours || 0}ч
                </p>
              </div>
              <div className="bg-white rounded-lg shadow p-4">
                <p className="text-sm text-gray-600">Автоматизировано</p>
                <p className="text-2xl font-bold text-green-600">
                  {metrics?.automation_rate || 0}%
                </p>
              </div>
              <div className="bg-white rounded-lg shadow p-4">
                <p className="text-sm text-gray-600">Ожидает одобрения</p>
                <p className="text-2xl font-bold text-orange-600">
                  {metrics?.pending_approvals || 0}
                </p>
              </div>
            </div>

            {/* Recent Actions Summary */}
            <div className="bg-white rounded-lg shadow p-4">
              <h3 className="font-semibold text-gray-800 mb-3">Последние действия</h3>
              <div className="space-y-2">
                {actions.slice(0, 5).map((action) => (
                  <div key={action.id} className="flex justify-between items-center py-2 border-b">
                    <div className="flex-1">
                      <p className="text-sm font-medium text-gray-800">{action.action_type}</p>
                      <p className="text-xs text-gray-600">{action.description}</p>
                    </div>
                    <span className={`text-xs px-2 py-1 rounded ${
                      action.was_approved === true
                        ? "bg-green-100 text-green-800"
                        : action.was_approved === false
                        ? "bg-red-100 text-red-800"
                        : "bg-gray-100 text-gray-800"
                    }`}>
                      {action.was_approved === true ? "✓" : action.was_approved === false ? "✗" : "•"}
                    </span>
                  </div>
                ))}
              </div>
            </div>
          </div>
        )}

        {activeTab === "actions" && (
          <div className="space-y-3">
            {actions.map((action) => (
              <div key={action.id} className="bg-white rounded-lg shadow p-4">
                <div className="flex justify-between items-start mb-2">
                  <div>
                    <h4 className="font-semibold text-gray-800">{action.action_type}</h4>
                    <p className="text-sm text-gray-600">{action.description}</p>
                  </div>
                  <span className={`text-xs px-2 py-1 rounded ${
                    action.was_approved === true
                      ? "bg-green-100 text-green-800"
                      : action.was_approved === false
                      ? "bg-red-100 text-red-800"
                      : "bg-yellow-100 text-yellow-800"
                  }`}>
                    {action.was_approved === true
                      ? "Одобрено"
                      : action.was_approved === false
                      ? "Отклонено"
                      : "Ожидает"}
                  </span>
                </div>
                {action.impact_amount && (
                  <p className="text-sm text-gray-700">
                    Сумма: ₽{action.impact_amount.toLocaleString()}
                  </p>
                )}
                <p className="text-xs text-gray-500 mt-2">
                  {new Date(action.executed_at).toLocaleString("ru-RU")}
                </p>
              </div>
            ))}
          </div>
        )}

        {activeTab === "approvals" && (
          <div className="space-y-3">
            {pendingActions.length === 0 ? (
              <div className="bg-white rounded-lg shadow p-8 text-center">
                <p className="text-gray-600">Нет ожидающих одобрений</p>
              </div>
            ) : (
              pendingActions.map((action) => (
                <div key={action.id} className="bg-white rounded-lg shadow p-4">
                  <h4 className="font-semibold text-gray-800 mb-2">{action.action_type}</h4>
                  <p className="text-sm text-gray-600 mb-3">{action.description}</p>
                  {action.impact_amount && (
                    <p className="text-sm font-medium text-gray-700 mb-3">
                      Сумма: ₽{action.impact_amount.toLocaleString()}
                    </p>
                  )}
                  <div className="flex gap-2">
                    <button
                      onClick={() => handleApprove(action.id)}
                      className="flex-1 bg-green-600 text-white py-2 px-4 rounded-lg hover:bg-green-700 transition"
                    >
                      Одобрить
                    </button>
                    <button
                      onClick={() => handleDecline(action.id)}
                      className="flex-1 bg-red-600 text-white py-2 px-4 rounded-lg hover:bg-red-700 transition"
                    >
                      Отклонить
                    </button>
                  </div>
                </div>
              ))
            )}
          </div>
        )}
      </div>
    </div>
  );
}
