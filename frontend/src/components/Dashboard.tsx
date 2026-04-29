import { motion } from "framer-motion";
import {
  Area,
  AreaChart,
  Bar,
  BarChart,
  CartesianGrid,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";
import { Leaf, Droplets, ShieldAlert, TrendingUp, AlertTriangle, Bell } from "lucide-react";
import { alerts, cropHealthData, waterUsageData } from "@/lib/mockData";
import { cn } from "@/lib/utils";

const metrics = [
  {
    label: "Healthy plants",
    value: "1,247",
    delta: "+5.2%",
    deltaPositive: true,
    icon: Leaf,
    accent: "text-primary",
  },
  {
    label: "Diseased",
    value: "38",
    delta: "-1.1%",
    deltaPositive: true,
    icon: ShieldAlert,
    accent: "text-warning",
  },
  {
    label: "Water usage",
    value: "4.3k L",
    delta: "+8%",
    deltaPositive: false,
    icon: Droplets,
    accent: "text-chart-2",
  },
  {
    label: "Yield forecast",
    value: "78.4%",
    delta: "+2.4%",
    deltaPositive: true,
    icon: TrendingUp,
    accent: "text-primary",
  },
];

const severityStyle: Record<"high" | "medium" | "low", string> = {
  high: "bg-danger/10 border-danger/40 text-danger",
  medium: "bg-warning/10 border-warning/40 text-warning",
  low: "bg-primary/10 border-primary/30 text-primary",
};

export function Dashboard() {
  return (
    <div className="p-6 space-y-6 max-w-7xl mx-auto">
      {/* Metrics */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        {metrics.map((m, i) => (
          <motion.div
            key={m.label}
            initial={{ opacity: 0, y: 8 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: i * 0.05 }}
            className="surface border border-border/60 rounded-2xl p-5"
          >
            <div className="flex items-center justify-between mb-3">
              <div className="size-9 rounded-lg bg-accent/40 grid place-items-center">
                <m.icon className={cn("size-4", m.accent)} />
              </div>
              <span
                className={cn(
                  "text-[11px] font-medium px-1.5 py-0.5 rounded-md",
                  m.deltaPositive ? "text-success bg-success/10" : "text-warning bg-warning/10",
                )}
              >
                {m.delta}
              </span>
            </div>
            <div className="text-2xl font-semibold tabular-nums">{m.value}</div>
            <div className="text-xs text-muted-foreground mt-0.5">{m.label}</div>
          </motion.div>
        ))}
      </div>

      <div className="grid lg:grid-cols-3 gap-4">
        {/* Crop health chart */}
        <div className="lg:col-span-2 surface border border-border/60 rounded-2xl p-5">
          <div className="flex items-center justify-between mb-4">
            <div>
              <div className="text-[11px] uppercase tracking-wider text-muted-foreground">Last 7 days</div>
              <h3 className="font-semibold">Crop Health</h3>
            </div>
            <div className="flex items-center gap-3 text-xs">
              {[
                { c: "var(--primary)", l: "Healthy" },
                { c: "var(--warning)", l: "At risk" },
                { c: "var(--danger)", l: "Diseased" },
              ].map((x) => (
                <span key={x.l} className="flex items-center gap-1.5 text-muted-foreground">
                  <span className="size-2 rounded-full" style={{ background: x.c }} /> {x.l}
                </span>
              ))}
            </div>
          </div>
          <div className="h-64">
            <ResponsiveContainer>
              <AreaChart data={cropHealthData}>
                <defs>
                  <linearGradient id="g1" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="0%" stopColor="var(--primary)" stopOpacity={0.5} />
                    <stop offset="100%" stopColor="var(--primary)" stopOpacity={0} />
                  </linearGradient>
                </defs>
                <CartesianGrid strokeDasharray="3 3" stroke="var(--border)" vertical={false} />
                <XAxis dataKey="day" stroke="var(--muted-foreground)" fontSize={11} tickLine={false} axisLine={false} />
                <YAxis stroke="var(--muted-foreground)" fontSize={11} tickLine={false} axisLine={false} />
                <Tooltip
                  contentStyle={{
                    background: "var(--surface-elevated)",
                    border: "1px solid var(--border)",
                    borderRadius: 10,
                    fontSize: 12,
                  }}
                />
                <Area type="monotone" dataKey="healthy" stroke="var(--primary)" strokeWidth={2} fill="url(#g1)" />
                <Area type="monotone" dataKey="at_risk" stroke="var(--warning)" strokeWidth={1.5} fillOpacity={0} />
                <Area type="monotone" dataKey="diseased" stroke="var(--danger)" strokeWidth={1.5} fillOpacity={0} />
              </AreaChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Alerts */}
        <div className="surface border border-border/60 rounded-2xl p-5">
          <div className="flex items-center gap-2 mb-4">
            <Bell className="size-4 text-primary" />
            <h3 className="font-semibold">Alerts</h3>
            <span className="ml-auto text-[11px] text-muted-foreground">{alerts.length} active</span>
          </div>
          <ul className="space-y-3">
            {alerts.map((a) => (
              <li
                key={a.id}
                className={cn("rounded-xl border p-3", severityStyle[a.severity])}
              >
                <div className="flex items-start gap-2">
                  <AlertTriangle className="size-4 shrink-0 mt-0.5" />
                  <div className="min-w-0">
                    <div className="text-sm font-medium text-foreground truncate">{a.title}</div>
                    <p className="text-xs text-muted-foreground mt-0.5 leading-relaxed">{a.description}</p>
                  </div>
                </div>
              </li>
            ))}
          </ul>
        </div>
      </div>

      {/* Water usage */}
      <div className="surface border border-border/60 rounded-2xl p-5">
        <div className="flex items-center justify-between mb-4">
          <div>
            <div className="text-[11px] uppercase tracking-wider text-muted-foreground">Daily</div>
            <h3 className="font-semibold">Water Usage (Liters)</h3>
          </div>
        </div>
        <div className="h-56">
          <ResponsiveContainer>
            <BarChart data={waterUsageData}>
              <CartesianGrid strokeDasharray="3 3" stroke="var(--border)" vertical={false} />
              <XAxis dataKey="day" stroke="var(--muted-foreground)" fontSize={11} tickLine={false} axisLine={false} />
              <YAxis stroke="var(--muted-foreground)" fontSize={11} tickLine={false} axisLine={false} />
              <Tooltip
                contentStyle={{
                  background: "var(--surface-elevated)",
                  border: "1px solid var(--border)",
                  borderRadius: 10,
                  fontSize: 12,
                }}
                cursor={{ fill: "var(--accent)", opacity: 0.4 }}
              />
              <Bar dataKey="liters" fill="var(--primary)" radius={[8, 8, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>
    </div>
  );
}
