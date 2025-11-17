"use client";

import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from "recharts";
import { Card } from "@/components/ui/card";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { AlertCircle, TrendingUp } from 'lucide-react';

interface DashboardTabsProps {
  activeTab: string;
  setActiveTab: (tab: string) => void;
}

// Mock data for charts
const chartData = [
  { month: "Jan", value: 45000 },
  { month: "Feb", value: 52000 },
  { month: "Mar", value: 48000 },
  { month: "Apr", value: 61000 },
  { month: "May", value: 55000 },
  { month: "Jun", value: 67000 },
  { month: "Jul", value: 72000 },
  { month: "Aug", value: 78000 },
  { month: "Sep", value: 85000 },
  { month: "Oct", value: 92000 },
  { month: "Nov", value: 105000 },
  { month: "Dec", value: 124500 },
];

export default function DashboardTabs({ activeTab, setActiveTab }: DashboardTabsProps) {
  return (
    <Tabs value={activeTab} onValueChange={setActiveTab} className="w-full">
      {/* Tab List */}
      <TabsList className="grid w-full grid-cols-4 bg-muted/50 border border-border rounded-lg p-1 mb-6">
        <TabsTrigger
          value="finance"
          className="data-[state=active]:bg-card data-[state=active]:text-foreground data-[state=active]:shadow-sm rounded-md text-xs sm:text-sm"
        >
          Finance
        </TabsTrigger>
        <TabsTrigger
          value="competitors"
          className="data-[state=active]:bg-card data-[state=active]:text-foreground data-[state=active]:shadow-sm rounded-md text-xs sm:text-sm"
        >
          Competitors
        </TabsTrigger>
        <TabsTrigger
          value="legal"
          className="data-[state=active]:bg-card data-[state=active]:text-foreground data-[state=active]:shadow-sm rounded-md text-xs sm:text-sm"
        >
          Legal
        </TabsTrigger>
        <TabsTrigger
          value="trends"
          className="data-[state=active]:bg-card data-[state=active]:text-foreground data-[state=active]:shadow-sm rounded-md text-xs sm:text-sm"
        >
          Trends
        </TabsTrigger>
      </TabsList>

      {/* Finance Tab */}
      <TabsContent value="finance" className="space-y-6">
        <Card className="card-gradient border-border bg-card p-6">
          <h3 className="text-lg font-semibold text-foreground mb-6">Revenue Forecast</h3>
          <ResponsiveContainer width="100%" height={300}>
            <LineChart data={chartData}>
              <CartesianGrid strokeDasharray="3 3" stroke="var(--color-border)" />
              <XAxis dataKey="month" stroke="var(--color-muted-foreground)" />
              <YAxis stroke="var(--color-muted-foreground)" />
              <Tooltip
                contentStyle={{
                  backgroundColor: "var(--color-card)",
                  border: "1px solid var(--color-border)",
                  borderRadius: "0.75rem",
                }}
              />
              <Line
                type="monotone"
                dataKey="value"
                stroke="var(--color-primary)"
                dot={{ fill: "var(--color-primary)", r: 4 }}
                activeDot={{ r: 6 }}
                strokeWidth={2}
              />
            </LineChart>
          </ResponsiveContainer>
        </Card>

        {/* Insight Callouts */}
        <div className="grid gap-4 sm:grid-cols-2">
          <Card className="card-gradient border-primary/20 bg-primary/5 p-4 border">
            <div className="flex gap-3">
              <TrendingUp className="h-5 w-5 text-primary flex-shrink-0 mt-0.5" />
              <div>
                <h4 className="font-semibold text-foreground text-sm mb-1">Revenue Growing</h4>
                <p className="text-xs text-muted-foreground">
                  Projected 18% YoY growth. Sustain current marketing spend.
                </p>
              </div>
            </div>
          </Card>
          <Card className="card-gradient border-warning/20 bg-warning/5 p-4 border">
            <div className="flex gap-3">
              <AlertCircle className="h-5 w-5 text-warning flex-shrink-0 mt-0.5" />
              <div>
                <h4 className="font-semibold text-foreground text-sm mb-1">Monitor Spending</h4>
                <p className="text-xs text-muted-foreground">
                  Ops costs increased 8% last month. Review vendor contracts.
                </p>
              </div>
            </div>
          </Card>
        </div>
      </TabsContent>

      {/* Competitors Tab */}
      <TabsContent value="competitors" className="space-y-6">
        <Card className="card-gradient border-border bg-card p-6">
          <h3 className="text-lg font-semibold text-foreground mb-6">Competitor Market Share</h3>
          <ResponsiveContainer width="100%" height={300}>
            <LineChart data={chartData}>
              <CartesianGrid strokeDasharray="3 3" stroke="var(--color-border)" />
              <XAxis dataKey="month" stroke="var(--color-muted-foreground)" />
              <YAxis stroke="var(--color-muted-foreground)" />
              <Tooltip
                contentStyle={{
                  backgroundColor: "var(--color-card)",
                  border: "1px solid var(--color-border)",
                  borderRadius: "0.75rem",
                }}
              />
              <Line
                type="monotone"
                dataKey="value"
                stroke="var(--color-secondary)"
                dot={{ fill: "var(--color-secondary)", r: 4 }}
                activeDot={{ r: 6 }}
                strokeWidth={2}
              />
            </LineChart>
          </ResponsiveContainer>
        </Card>

        {/* Insight Callouts */}
        <div className="grid gap-4 sm:grid-cols-2">
          <Card className="card-gradient border-warning/20 bg-warning/5 p-4 border">
            <div className="flex gap-3">
              <AlertCircle className="h-5 w-5 text-warning flex-shrink-0 mt-0.5" />
              <div>
                <h4 className="font-semibold text-foreground text-sm mb-1">New Entrant Alert</h4>
                <p className="text-xs text-muted-foreground">
                  TechVenture raised $50M Series B. Expect aggressive pricing.
                </p>
              </div>
            </div>
          </Card>
          <Card className="card-gradient border-primary/20 bg-primary/5 p-4 border">
            <div className="flex gap-3">
              <TrendingUp className="h-5 w-5 text-primary flex-shrink-0 mt-0.5" />
              <div>
                <h4 className="font-semibold text-foreground text-sm mb-1">Market Opportunity</h4>
                <p className="text-xs text-muted-foreground">
                  Competitor discontinued product line. Addressable gap: $12M.
                </p>
              </div>
            </div>
          </Card>
        </div>
      </TabsContent>

      {/* Legal Tab */}
      <TabsContent value="legal" className="space-y-6">
        <Card className="card-gradient border-border bg-card p-6">
          <h3 className="text-lg font-semibold text-foreground mb-6">Compliance Timeline</h3>
          <ResponsiveContainer width="100%" height={300}>
            <LineChart data={chartData}>
              <CartesianGrid strokeDasharray="3 3" stroke="var(--color-border)" />
              <XAxis dataKey="month" stroke="var(--color-muted-foreground)" />
              <YAxis stroke="var(--color-muted-foreground)" />
              <Tooltip
                contentStyle={{
                  backgroundColor: "var(--color-card)",
                  border: "1px solid var(--color-border)",
                  borderRadius: "0.75rem",
                }}
              />
              <Line
                type="monotone"
                dataKey="value"
                stroke="var(--color-destructive)"
                dot={{ fill: "var(--color-destructive)", r: 4 }}
                activeDot={{ r: 6 }}
                strokeWidth={2}
              />
            </LineChart>
          </ResponsiveContainer>
        </Card>

        {/* Insight Callouts */}
        <div className="grid gap-4 sm:grid-cols-2">
          <Card className="card-gradient border-destructive/20 bg-destructive/5 p-4 border">
            <div className="flex gap-3">
              <AlertCircle className="h-5 w-5 text-destructive flex-shrink-0 mt-0.5" />
              <div>
                <h4 className="font-semibold text-foreground text-sm mb-1">Tax Deadline</h4>
                <p className="text-xs text-muted-foreground">
                  Q4 filing due December 15. Notify accounting team now.
                </p>
              </div>
            </div>
          </Card>
          <Card className="card-gradient border-primary/20 bg-primary/5 p-4 border">
            <div className="flex gap-3">
              <TrendingUp className="h-5 w-5 text-primary flex-shrink-0 mt-0.5" />
              <div>
                <h4 className="font-semibold text-foreground text-sm mb-1">Regulation Updated</h4>
                <p className="text-xs text-muted-foreground">
                  GDPR clarification for SaaS vendors. No action needed.
                </p>
              </div>
            </div>
          </Card>
        </div>
      </TabsContent>

      {/* Trends Tab */}
      <TabsContent value="trends" className="space-y-6">
        <Card className="card-gradient border-border bg-card p-6">
          <h3 className="text-lg font-semibold text-foreground mb-6">Market Trends</h3>
          <ResponsiveContainer width="100%" height={300}>
            <LineChart data={chartData}>
              <CartesianGrid strokeDasharray="3 3" stroke="var(--color-border)" />
              <XAxis dataKey="month" stroke="var(--color-muted-foreground)" />
              <YAxis stroke="var(--color-muted-foreground)" />
              <Tooltip
                contentStyle={{
                  backgroundColor: "var(--color-card)",
                  border: "1px solid var(--color-border)",
                  borderRadius: "0.75rem",
                }}
              />
              <Line
                type="monotone"
                dataKey="value"
                stroke="var(--color-accent)"
                dot={{ fill: "var(--color-accent)", r: 4 }}
                activeDot={{ r: 6 }}
                strokeWidth={2}
              />
            </LineChart>
          </ResponsiveContainer>
        </Card>

        {/* Insight Callouts */}
        <div className="grid gap-4 sm:grid-cols-2">
          <Card className="card-gradient border-primary/20 bg-primary/5 p-4 border">
            <div className="flex gap-3">
              <TrendingUp className="h-5 w-5 text-primary flex-shrink-0 mt-0.5" />
              <div>
                <h4 className="font-semibold text-foreground text-sm mb-1">AI Adoption Surge</h4>
                <p className="text-xs text-muted-foreground">
                  Enterprise adoption of AI tools up 34% YoY. Opportunity for B2B.
                </p>
              </div>
            </div>
          </Card>
          <Card className="card-gradient border-warning/20 bg-warning/5 p-4 border">
            <div className="flex gap-3">
              <AlertCircle className="h-5 w-5 text-warning flex-shrink-0 mt-0.5" />
              <div>
                <h4 className="font-semibold text-foreground text-sm mb-1">Economic Headwind</h4>
                <p className="text-xs text-muted-foreground">
                  Interest rates impact SMB budgets. Accelerate sales cycle.
                </p>
              </div>
            </div>
          </Card>
        </div>
      </TabsContent>
    </Tabs>
  );
}
