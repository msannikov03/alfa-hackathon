"use client";

import { useState } from "react";
import { TrendingUp, TrendingDown, Bell, CheckCircle, AlertCircle, Clock } from 'lucide-react';
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import KPICard from "@/components/dashboard/kpi-card";
import ActivityFeed from "@/components/dashboard/activity-feed";
import AutonomousActions from "@/components/dashboard/autonomous-actions";
import DashboardTabs from "@/components/dashboard/dashboard-tabs";

export default function MainDashboard() {
  const [activeTab, setActiveTab] = useState("finance");

  return (
    <div className="min-h-screen bg-background">
      {/* Hero Section */}
      <section className="border-b border-border bg-gradient-to-br from-background via-background to-primary/5 px-6 py-12 sm:px-8 md:py-16">
        <div className="mx-auto max-w-7xl">
          <div className="mb-8 flex items-center gap-3">
            <div className="rounded-lg border border-primary/20 bg-primary/10 p-2.5">
              <TrendingUp className="h-5 w-5 text-primary" />
            </div>
            <span className="text-xs font-semibold uppercase tracking-widest text-primary">
              AI-Powered Control Center
            </span>
          </div>

          <div className="grid gap-6 md:grid-cols-3 md:gap-8 lg:gap-12">
            <div className="md:col-span-2">
              <h1 className="text-4xl font-bold tracking-tight text-foreground sm:text-5xl md:text-6xl mb-4">
                Alfa Business Assistant
              </h1>
              <p className="text-lg text-muted-foreground leading-relaxed max-w-xl">
                Your autonomous AI copilot for smarter decisions. Monitor KPIs, track compliance, analyze competitors, and manage cash flow—all in one place.
              </p>
            </div>

            <div className="flex flex-col gap-3 md:justify-end">
              <Button className="gap-2 bg-primary hover:bg-primary/90 text-primary-foreground font-semibold">
                Start Monitoring
              </Button>
              <Button variant="outline" className="gap-2 border-border hover:bg-muted">
                View Documentation
              </Button>
            </div>
          </div>
        </div>
      </section>

      {/* Main Content */}
      <div className="mx-auto max-w-7xl px-6 py-8 sm:px-8 md:py-12">
        {/* KPI Grid */}
        <section className="mb-12">
          <h2 className="mb-6 text-2xl font-bold text-foreground">Key Performance Indicators</h2>
          <div className="grid gap-6 sm:grid-cols-2 lg:grid-cols-4">
            <KPICard
              title="Revenue Today"
              value="$124,500"
              trend={{ value: 12.5, isPositive: true }}
              badge={{ label: "On Track", variant: "success" }}
              description="↑ $15,200 from yesterday"
            />
            <KPICard
              title="Active Decisions"
              value="18"
              trend={{ value: 8.2, isPositive: true }}
              badge={{ label: "Optimal", variant: "success" }}
              description="5 pending review"
            />
            <KPICard
              title="Compliance Alerts"
              value="3"
              trend={{ value: 2.1, isPositive: false }}
              badge={{ label: "Monitor", variant: "warning" }}
              description="1 requires immediate action"
            />
            <KPICard
              title="Cash Runway"
              value="8.2 months"
              trend={{ value: 1.5, isPositive: true }}
              badge={{ label: "Healthy", variant: "success" }}
              description="Current burn rate: $45K/mo"
            />
          </div>
        </section>

        {/* Tabs and Activity Feed */}
        <div className="grid gap-8 lg:grid-cols-3">
          {/* Main Content Area with Tabs */}
          <div className="lg:col-span-2">
            <DashboardTabs activeTab={activeTab} setActiveTab={setActiveTab} />
          </div>

          {/* Right Sidebar - Autonomous Actions */}
          <div className="lg:col-span-1">
            <AutonomousActions />
          </div>
        </div>

        {/* Activity Feed */}
        <section className="mt-8">
          <h2 className="mb-6 text-2xl font-bold text-foreground">Real-Time Activity Feed</h2>
          <ActivityFeed />
        </section>

        {/* Integration Placeholders */}
        <section className="mt-12 pt-8 border-t border-border">
          <h3 className="mb-6 text-xl font-bold text-foreground">Integration Status</h3>
          <div className="grid gap-4 sm:grid-cols-2">
            <Card className="card-gradient border-border bg-card p-6">
              <div className="flex items-center justify-between">
                <div>
                  <h4 className="font-semibold text-foreground mb-1">Telegram Bot</h4>
                  <p className="text-sm text-muted-foreground">Real-time alerts on mobile</p>
                </div>
                <Badge variant="secondary" className="bg-muted text-muted-foreground">
                  Not Connected
                </Badge>
              </div>
            </Card>
            <Card className="card-gradient border-border bg-card p-6">
              <div className="flex items-center justify-between">
                <div>
                  <h4 className="font-semibold text-foreground mb-1">WebSocket Live Status</h4>
                  <p className="text-sm text-muted-foreground">Live data synchronization</p>
                </div>
                <Badge className="bg-success/20 text-success border-success/30 border">
                  Connected
                </Badge>
              </div>
            </Card>
          </div>
        </section>
      </div>
    </div>
  );
}
