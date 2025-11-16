"use client";

import { useEffect, useState, useRef } from "react";

interface Action {
  id: number;
  action_type: string;
  description: string;
  impact_amount?: number;
  required_approval: boolean;
  was_approved?: boolean;
  executed_at: string;
}

interface WebSocketMessage {
  type: string;
  timestamp: string;
  data: any;
}

interface Metrics {
  total_actions: number;
  time_saved_hours: number;
  automation_rate: number;
  pending_approvals: number;
  approved_actions: number;
  decisions_made: number;
}

export default function DashboardPage() {
  const [actions, setActions] = useState<Action[]>([]);
  const [metrics, setMetrics] = useState<Metrics | null>(null);
  const [ws, setWs] = useState<WebSocket | null>(null);
  const [connected, setConnected] = useState(false);
  const [notifications, setNotifications] = useState<WebSocketMessage[]>([]);
  const [userId, setUserId] = useState<number | null>(null);
  const [username, setUsername] = useState<string>("");
  const wsRef = useRef<WebSocket | null>(null);

  useEffect(() => {
    // Check authentication
    const token = localStorage.getItem("token");
    const storedUserId = localStorage.getItem("user_id");
    const storedUsername = localStorage.getItem("username");

    if (!token || !storedUserId) {
      // Redirect to login if not authenticated
      window.location.href = "/login";
      return;
    }

    setUserId(parseInt(storedUserId));
    setUsername(storedUsername || "User");

    // Fetch initial data
    fetchData();

    // Connect to WebSocket
    connectWebSocket();

    return () => {
      if (wsRef.current) {
        wsRef.current.close();
      }
    };
  }, []);

  const connectWebSocket = () => {
    try {
      const storedUserId = localStorage.getItem("user_id");
      if (!storedUserId) return;

      const wsProtocol = window.location.protocol === "https:" ? "wss:" : "ws:";
      const wsHost = window.location.host;
      const socket = new WebSocket(`${wsProtocol}//${wsHost}/ws?user_id=${storedUserId}`);

      socket.onopen = () => {
        console.log("WebSocket connected");
        setConnected(true);
      };

      socket.onmessage = (event) => {
        const message: WebSocketMessage = JSON.parse(event.data);
        console.log("WebSocket message:", message);

        // Handle different message types
        switch (message.type) {
          case "action_taken":
            setNotifications((prev) => [message, ...prev].slice(0, 10));
            fetchData(); // Refresh data
            break;
          case "approval_needed":
            setNotifications((prev) => [message, ...prev].slice(0, 10));
            fetchData();
            break;
          case "metric_update":
            // Update metrics in real-time
            break;
          case "briefing_ready":
            setNotifications((prev) => [message, ...prev].slice(0, 10));
            break;
        }
      };

      socket.onclose = () => {
        console.log("WebSocket disconnected");
        setConnected(false);

        // Reconnect after 5 seconds
        setTimeout(() => connectWebSocket(), 5000);
      };

      socket.onerror = (error) => {
        console.error("WebSocket error:", error);
      };

      wsRef.current = socket;
      setWs(socket);
    } catch (error) {
      console.error("Error connecting to WebSocket:", error);
    }
  };

  const fetchData = async () => {
    try {
      const storedUserId = localStorage.getItem("user_id");
      const token = localStorage.getItem("token");

      if (!storedUserId || !token) return;

      const headers = {
        Authorization: `Bearer ${token}`,
      };

      // Fetch recent actions
      const actionsRes = await fetch(
        `/api/v1/actions/recent?user_id=${storedUserId}&limit=20`,
        { headers }
      );
      if (actionsRes.ok) {
        const actionsData = await actionsRes.json();
        setActions(actionsData);
      }

      // Fetch metrics
      const metricsRes = await fetch(
        `/api/v1/metrics/performance?user_id=${storedUserId}`,
        { headers }
      );
      if (metricsRes.ok) {
        const metricsData = await metricsRes.json();
        setMetrics(metricsData);
      }
    } catch (error) {
      console.error("Error fetching data:", error);
    }
  };

  const handleApprove = async (actionId: number) => {
    try {
      const res = await fetch(`/api/v1/actions/approve/${actionId}`, {
        method: "POST",
      });

      if (res.ok) {
        await fetchData();
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

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-50 to-blue-50 p-6">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="mb-8">
          <div className="flex justify-between items-center">
            <div>
              <h1 className="text-4xl font-bold text-gray-900">Business Dashboard</h1>
              <p className="text-gray-600 mt-2">
                Welcome, {username} | Real-time AI Business Assistant
              </p>
            </div>
            <div className="flex items-center gap-4">
              <div className="flex items-center gap-2">
                <div className={`w-3 h-3 rounded-full ${connected ? "bg-green-500" : "bg-red-500"}`}></div>
                <span className="text-sm text-gray-600">
                  {connected ? "Live" : "Connecting..."}
                </span>
              </div>
              <button
                onClick={() => {
                  localStorage.clear();
                  window.location.href = "/login";
                }}
                className="text-sm px-4 py-2 bg-gray-200 text-gray-700 rounded-lg hover:bg-gray-300 transition"
              >
                Logout
              </button>
            </div>
          </div>
        </div>

        {/* Metrics Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 mb-8">
          <div className="bg-white rounded-xl shadow-lg p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-gray-600 text-sm font-medium">Tasks Completed</p>
                <p className="text-3xl font-bold text-gray-900 mt-2">
                  {metrics?.total_actions || 0}
                </p>
                <p className="text-sm text-green-600 mt-1">
                  +{metrics?.approved_actions || 0} approved
                </p>
              </div>
              <div className="w-12 h-12 bg-blue-100 rounded-full flex items-center justify-center">
                <span className="text-2xl">✓</span>
              </div>
            </div>
          </div>

          <div className="bg-white rounded-xl shadow-lg p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-gray-600 text-sm font-medium">Time Saved</p>
                <p className="text-3xl font-bold text-gray-900 mt-2">
                  {metrics?.time_saved_hours || 0}h
                </p>
                <p className="text-sm text-blue-600 mt-1">
                  ~{Math.round((metrics?.time_saved_hours || 0) * 60)} minutes
                </p>
              </div>
              <div className="w-12 h-12 bg-purple-100 rounded-full flex items-center justify-center">
                <span className="text-2xl">⏱</span>
              </div>
            </div>
          </div>

          <div className="bg-white rounded-xl shadow-lg p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-gray-600 text-sm font-medium">Automation Rate</p>
                <p className="text-3xl font-bold text-gray-900 mt-2">
                  {metrics?.automation_rate || 0}%
                </p>
                <p className="text-sm text-green-600 mt-1">
                  {metrics?.decisions_made || 0} decisions made
                </p>
              </div>
              <div className="w-12 h-12 bg-green-100 rounded-full flex items-center justify-center">
                <span className="text-2xl">🤖</span>
              </div>
            </div>
          </div>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Recent Actions Feed */}
          <div className="lg:col-span-2">
            <div className="bg-white rounded-xl shadow-lg p-6">
              <h2 className="text-xl font-bold text-gray-900 mb-4">Autonomous Action Feed</h2>
              <div className="space-y-3 max-h-[600px] overflow-y-auto">
                {actions.map((action) => (
                  <div
                    key={action.id}
                    className="border border-gray-200 rounded-lg p-4 hover:shadow-md transition"
                  >
                    <div className="flex justify-between items-start mb-2">
                      <div className="flex-1">
                        <div className="flex items-center gap-2">
                          <h4 className="font-semibold text-gray-900">{action.action_type}</h4>
                          <span className={`text-xs px-2 py-1 rounded-full ${
                            action.was_approved === true
                              ? "bg-green-100 text-green-800"
                              : action.was_approved === false
                              ? "bg-red-100 text-red-800"
                              : "bg-yellow-100 text-yellow-800"
                          }`}>
                            {action.was_approved === true
                              ? "Approved"
                              : action.was_approved === false
                              ? "Declined"
                              : "Pending"}
                          </span>
                        </div>
                        <p className="text-sm text-gray-600 mt-1">{action.description}</p>
                      </div>
                    </div>

                    {action.impact_amount && (
                      <p className="text-sm font-medium text-gray-700 mb-2">
                        Amount: ₽{action.impact_amount.toLocaleString()}
                      </p>
                    )}

                    <div className="flex items-center justify-between">
                      <p className="text-xs text-gray-500">
                        {new Date(action.executed_at).toLocaleString()}
                      </p>

                      {action.required_approval && action.was_approved === null && (
                        <div className="flex gap-2">
                          <button
                            onClick={() => handleApprove(action.id)}
                            className="text-xs px-3 py-1 bg-green-600 text-white rounded hover:bg-green-700 transition"
                          >
                            Approve
                          </button>
                          <button
                            onClick={() => handleDecline(action.id)}
                            className="text-xs px-3 py-1 bg-red-600 text-white rounded hover:bg-red-700 transition"
                          >
                            Decline
                          </button>
                        </div>
                      )}
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>

          {/* Live Notifications */}
          <div className="lg:col-span-1">
            <div className="bg-white rounded-xl shadow-lg p-6">
              <h2 className="text-xl font-bold text-gray-900 mb-4">Live Updates</h2>
              <div className="space-y-3 max-h-[600px] overflow-y-auto">
                {notifications.length === 0 ? (
                  <p className="text-gray-500 text-sm text-center py-8">
                    Waiting for updates...
                  </p>
                ) : (
                  notifications.map((notification, index) => (
                    <div
                      key={index}
                      className={`p-3 rounded-lg ${
                        notification.type === "action_taken"
                          ? "bg-blue-50 border border-blue-200"
                          : notification.type === "approval_needed"
                          ? "bg-yellow-50 border border-yellow-200"
                          : "bg-green-50 border border-green-200"
                      }`}
                    >
                      <div className="flex items-start gap-2">
                        <span className="text-lg">
                          {notification.type === "action_taken"
                            ? "✓"
                            : notification.type === "approval_needed"
                            ? "⚠"
                            : "📋"}
                        </span>
                        <div className="flex-1">
                          <p className="text-sm font-medium text-gray-900">
                            {notification.type.replace("_", " ").toUpperCase()}
                          </p>
                          <p className="text-xs text-gray-600 mt-1">
                            {new Date(notification.timestamp).toLocaleTimeString()}
                          </p>
                        </div>
                      </div>
                    </div>
                  ))
                )}
              </div>
            </div>

            {/* Quick Stats */}
            <div className="bg-white rounded-xl shadow-lg p-6 mt-6">
              <h2 className="text-xl font-bold text-gray-900 mb-4">Quick Stats</h2>
              <div className="space-y-3">
                <div className="flex justify-between items-center">
                  <span className="text-sm text-gray-600">Pending Approvals</span>
                  <span className="text-lg font-bold text-orange-600">
                    {metrics?.pending_approvals || 0}
                  </span>
                </div>
                <div className="flex justify-between items-center">
                  <span className="text-sm text-gray-600">Approved Today</span>
                  <span className="text-lg font-bold text-green-600">
                    {metrics?.approved_actions || 0}
                  </span>
                </div>
                <div className="flex justify-between items-center">
                  <span className="text-sm text-gray-600">Decisions Made</span>
                  <span className="text-lg font-bold text-blue-600">
                    {metrics?.decisions_made || 0}
                  </span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
