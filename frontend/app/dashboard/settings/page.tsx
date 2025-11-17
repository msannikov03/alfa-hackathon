"use client";
import { useEffect, useState } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { Bell, Key, Globe, Shield, Save, Check, Loader2 } from "lucide-react";
import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Badge } from "@/components/ui/badge";
import { Alert, AlertDescription } from "@/components/ui/alert";
import api from "@/lib/api";
import { getClientUserId } from "@/lib/user";

export default function SettingsPage() {
  const [saved, setSaved] = useState(false);
  const [notificationsEnabled, setNotificationsEnabled] = useState(true);
  const [emailNotifications, setEmailNotifications] = useState(true);
  const [telegramNotifications, setTelegramNotifications] = useState(true);
  const [language, setLanguage] = useState("ru");
  const [timezone, setTimezone] = useState("Europe/Moscow");
  const [currency, setCurrency] = useState("RUB");
  const [errorMessage, setErrorMessage] = useState<string | null>(null);

  const userId = getClientUserId();
  const queryClient = useQueryClient();

  const { data: settingsData, isLoading: isLoadingSettings } = useQuery({
    queryKey: ["userSettings", userId],
    queryFn: async () => {
      const response = await api.get("/settings");
      return response.data;
    },
  });

  /* eslint-disable react-hooks/set-state-in-effect -- sync toggles with backend snapshot */
  useEffect(() => {
    if (settingsData) {
      setNotificationsEnabled(settingsData.notifications.enabled);
      setEmailNotifications(settingsData.notifications.email);
      setTelegramNotifications(settingsData.notifications.telegram);
      setLanguage(settingsData.preferences.language);
      setTimezone(settingsData.preferences.timezone);
      setCurrency(settingsData.preferences.currency);
    }
  }, [settingsData]);
  /* eslint-enable react-hooks/set-state-in-effect */

  const updateSettingsMutation = useMutation({
    mutationFn: async () => {
      setErrorMessage(null);
      const payload = {
        notifications: {
          enabled: notificationsEnabled,
          email: emailNotifications,
          telegram: telegramNotifications,
        },
        preferences: {
          language,
          timezone,
          currency,
        },
      };
      const response = await api.post("/settings", payload);
      return response.data;
    },
    onSuccess: () => {
      setSaved(true);
      queryClient.invalidateQueries({ queryKey: ["userSettings", userId] });
      setTimeout(() => setSaved(false), 2000);
    },
    onError: () => {
      setErrorMessage("Не удалось сохранить настройки. Попробуйте ещё раз.");
    },
  });

  const handleSave = () => {
    updateSettingsMutation.mutate();
  };

  return (
    <div className="min-h-screen p-4 sm:p-6 lg:p-8 bg-background">
      <div className="max-w-4xl mx-auto">
        <div className="mb-8">
          <h1 className="text-4xl font-bold text-foreground mb-2">Настройки</h1>
          <p className="text-muted-foreground">Управляйте настройками и интеграциями</p>
        </div>

        <div className="space-y-6">
          {errorMessage && (
            <Alert variant="destructive">
              <AlertDescription>{errorMessage}</AlertDescription>
            </Alert>
          )}

          {/* Notifications */}
          <Card className="p-6">
            <div className="flex items-center gap-3 mb-6">
              <div className="p-2 bg-primary/10 rounded-lg">
                <Bell className="w-5 h-5 text-primary" />
              </div>
              <h2 className="text-2xl font-bold text-foreground">Уведомления</h2>
              {isLoadingSettings && <Loader2 className="w-4 h-4 animate-spin text-muted-foreground" />}
            </div>
            <div className="space-y-4">
              <div className="flex items-center justify-between p-4 rounded-lg border border-border hover:bg-muted/50 transition-colors">
                <div>
                  <p className="font-medium text-foreground">Включить уведомления</p>
                  <p className="text-sm text-muted-foreground">Получать обновления о вашем бизнесе</p>
                </div>
                <label className="relative inline-flex items-center cursor-pointer">
                  <input
                    type="checkbox"
                    checked={notificationsEnabled}
                    onChange={(e) => setNotificationsEnabled(e.target.checked)}
                    className="sr-only peer"
                  />
                  <div className="w-11 h-6 bg-muted peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-primary/20 rounded-full peer peer-checked:after:translate-x-full rtl:peer-checked:after:-translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:start-[2px] after:bg-white after:border-border after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-primary"></div>
                </label>
              </div>

              <div className="flex items-center justify-between p-4 rounded-lg border border-border hover:bg-muted/50 transition-colors">
                <div>
                  <p className="font-medium text-foreground">Email Notifications</p>
                  <p className="text-sm text-muted-foreground">Get daily briefings via email</p>
                </div>
                <label className="relative inline-flex items-center cursor-pointer">
                  <input
                    type="checkbox"
                    checked={emailNotifications}
                    onChange={(e) => setEmailNotifications(e.target.checked)}
                    className="sr-only peer"
                  />
                  <div className="w-11 h-6 bg-muted peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-primary/20 rounded-full peer peer-checked:after:translate-x-full rtl:peer-checked:after:-translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:start-[2px] after:bg-white after:border-border after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-primary"></div>
                </label>
              </div>

              <div className="flex items-center justify-between p-4 rounded-lg border border-border hover:bg-muted/50 transition-colors">
                <div>
                  <p className="font-medium text-foreground">Telegram Notifications</p>
                  <p className="text-sm text-muted-foreground">Receive alerts via Telegram bot</p>
                </div>
                <label className="relative inline-flex items-center cursor-pointer">
                  <input
                    type="checkbox"
                    checked={telegramNotifications}
                    onChange={(e) => setTelegramNotifications(e.target.checked)}
                    className="sr-only peer"
                  />
                  <div className="w-11 h-6 bg-muted peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-primary/20 rounded-full peer peer-checked:after:translate-x-full rtl:peer-checked:after:-translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:start-[2px] after:bg-white after:border-border after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-primary"></div>
                </label>
              </div>
            </div>
          </Card>

          {/* API Configuration */}
          <Card className="p-6">
            <div className="flex items-center gap-3 mb-6">
              <div className="p-2 bg-primary/10 rounded-lg">
                <Key className="w-5 h-5 text-primary" />
              </div>
              <h2 className="text-2xl font-bold text-foreground">API Configuration</h2>
            </div>
            <div className="space-y-4">
              <div>
                <Label htmlFor="api-endpoint" className="text-foreground">Backend API Endpoint</Label>
                <Input
                  id="api-endpoint"
                  type="text"
                  value={process.env.NEXT_PUBLIC_BACKEND_URL || "http://localhost:8000"}
                  disabled
                  className="mt-2 bg-muted text-muted-foreground"
                />
                <p className="text-xs text-muted-foreground mt-2">
                  This is configured via environment variables
                </p>
              </div>
              <div>
                <Label htmlFor="llm-provider" className="text-foreground">LLM Provider</Label>
                <div className="mt-2 flex items-center gap-2">
                  <Input
                    id="llm-provider"
                    type="text"
                    value="LLM7.io"
                    disabled
                    className="bg-muted text-muted-foreground"
                  />
                  <Badge variant="secondary" className="text-xs">Active</Badge>
                </div>
              </div>
            </div>
          </Card>

          {/* Language & Region */}
          <Card className="p-6">
            <div className="flex items-center gap-3 mb-6">
              <div className="p-2 bg-primary/10 rounded-lg">
                <Globe className="w-5 h-5 text-primary" />
              </div>
              <h2 className="text-2xl font-bold text-foreground">Language & Region</h2>
            </div>
            <div className="space-y-4">
              <div>
                <Label htmlFor="language" className="text-foreground">Language</Label>
                <select
                  id="language"
                  className="mt-2 w-full px-3 py-2 bg-card border border-border rounded-lg text-foreground focus:outline-none focus:ring-2 focus:ring-primary"
                  value={language}
                  onChange={(e) => setLanguage(e.target.value)}
                  disabled={isLoadingSettings || updateSettingsMutation.isPending}
                >
                  <option value="ru">Русский</option>
                  <option value="en">English</option>
                </select>
              </div>
              <div>
                <Label htmlFor="timezone" className="text-foreground">Timezone</Label>
                <select
                  id="timezone"
                  className="mt-2 w-full px-3 py-2 bg-card border border-border rounded-lg text-foreground focus:outline-none focus:ring-2 focus:ring-primary"
                  value={timezone}
                  onChange={(e) => setTimezone(e.target.value)}
                  disabled={isLoadingSettings || updateSettingsMutation.isPending}
                >
                  <option value="Europe/Moscow">Europe/Moscow (GMT+3)</option>
                  <option value="Europe/London">Europe/London (GMT+0)</option>
                  <option value="America/New_York">America/New_York (GMT-5)</option>
                </select>
              </div>
              <div>
                <Label htmlFor="currency" className="text-foreground">Currency</Label>
                <select
                  id="currency"
                  className="mt-2 w-full px-3 py-2 bg-card border border-border rounded-lg text-foreground focus:outline-none focus:ring-2 focus:ring-primary"
                  value={currency}
                  onChange={(e) => setCurrency(e.target.value)}
                  disabled={isLoadingSettings || updateSettingsMutation.isPending}
                >
                  <option value="RUB">₽ Russian Ruble (RUB)</option>
                  <option value="USD">$ US Dollar (USD)</option>
                  <option value="EUR">€ Euro (EUR)</option>
                </select>
              </div>
            </div>
          </Card>

          {/* Security */}
          <Card className="p-6">
            <div className="flex items-center gap-3 mb-6">
              <div className="p-2 bg-primary/10 rounded-lg">
                <Shield className="w-5 h-5 text-primary" />
              </div>
              <h2 className="text-2xl font-bold text-foreground">Security</h2>
            </div>
            <div className="space-y-4">
              <div>
                <Label htmlFor="current-password" className="text-foreground">Current Password</Label>
                <Input
                  id="current-password"
                  type="password"
                  placeholder="Enter current password"
                  className="mt-2"
                />
              </div>
              <div>
                <Label htmlFor="new-password" className="text-foreground">New Password</Label>
                <Input
                  id="new-password"
                  type="password"
                  placeholder="Enter new password"
                  className="mt-2"
                />
              </div>
              <div>
                <Label htmlFor="confirm-password" className="text-foreground">Confirm New Password</Label>
                <Input
                  id="confirm-password"
                  type="password"
                  placeholder="Confirm new password"
                  className="mt-2"
                />
              </div>
              <Button variant="outline" className="w-full text-foreground">
                Update Password
              </Button>
            </div>
          </Card>

          {/* Save Button */}
          <div className="flex justify-end gap-3">
            <Button
              onClick={handleSave}
              disabled={updateSettingsMutation.isPending || isLoadingSettings}
              className="gap-2 bg-primary text-primary-foreground hover:bg-primary/90"
            >
              {saved ? (
                <>
                  <Check className="w-4 h-4" />
                  Saved!
                </>
              ) : updateSettingsMutation.isPending ? (
                <>
                  <Loader2 className="w-4 h-4 animate-spin" />
                  Saving...
                </>
              ) : (
                <>
                  <Save className="w-4 h-4" />
                  Save Settings
                </>
              )}
            </Button>
          </div>
        </div>
      </div>
    </div>
  );
}
