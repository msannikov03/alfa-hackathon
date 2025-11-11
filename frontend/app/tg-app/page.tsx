"use client";

import { useEffect, useState } from "react";

export default function TelegramAppPage() {
  const [initData, setInitData] = useState<string>("");
  const [user, setUser] = useState<any>(null);

  useEffect(() => {
    // Check if running in Telegram WebApp
    if (typeof window !== "undefined" && window.Telegram?.WebApp) {
      const tg = window.Telegram.WebApp;
      tg.ready();
      tg.expand();
      
      setInitData(tg.initData);
      
      if (tg.initDataUnsafe?.user) {
        setUser(tg.initDataUnsafe.user);
      }
    }
  }, []);

  return (
    <div className="flex min-h-screen flex-col items-center justify-center p-8 bg-gradient-to-b from-blue-50 to-white">
      <div className="max-w-md w-full bg-white rounded-lg shadow-lg p-8">
        <h1 className="text-3xl font-bold mb-6 text-center text-blue-600">
          Alfa Business Assistant
        </h1>
        
        {user ? (
          <div className="space-y-4">
            <p className="text-lg">
              Welcome, <span className="font-semibold">{user.first_name}</span>!
            </p>
            <div className="bg-gray-50 rounded p-4">
              <p className="text-sm text-gray-600">User ID: {user.id}</p>
              {user.username && (
                <p className="text-sm text-gray-600">Username: @{user.username}</p>
              )}
            </div>
          </div>
        ) : (
          <div className="text-center">
            <p className="text-gray-600 mb-4">
              This app is designed to run inside Telegram.
            </p>
            <p className="text-sm text-gray-500">
              Please open it from your Telegram bot to access all features.
            </p>
          </div>
        )}
        
        <div className="mt-6 pt-6 border-t">
          <p className="text-sm text-gray-500 text-center">
            Powered by Alfa Business Assistant
          </p>
        </div>
      </div>
    </div>
  );
}

declare global {
  interface Window {
    Telegram?: {
      WebApp: any;
    };
  }
}
