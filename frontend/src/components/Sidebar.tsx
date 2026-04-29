import { Link, useRouterState } from "@tanstack/react-router";
import { LayoutDashboard, MessageSquare, Stethoscope, Sprout, Settings } from "lucide-react";
import { cn } from "@/lib/utils";

const nav = [
  { to: "/", label: "Dashboard", icon: LayoutDashboard },
  { to: "/chat", label: "RAG Chat", icon: MessageSquare },
  { to: "/diagnose", label: "Diagnosis", icon: Stethoscope },
];

export function Sidebar() {
  const pathname = useRouterState({ select: (s) => s.location.pathname });

  return (
    <aside className="w-60 shrink-0 border-r border-border/60 bg-sidebar/80 backdrop-blur flex flex-col p-4 gap-6">
      <Link to="/" className="flex items-center gap-3 px-2 pt-2">
        <div className="size-9 rounded-xl bg-gradient-to-br from-primary to-secondary grid place-items-center text-primary-foreground shadow-glow">
          <Sprout className="size-5" strokeWidth={2.5} />
        </div>
        <div className="leading-tight">
          <div className="font-semibold tracking-tight">AgriSense AI</div>
          <div className="text-[11px] text-muted-foreground">Harvest Intelligence</div>
        </div>
      </Link>

      <nav className="flex flex-col gap-1">
        {nav.map(({ to, label, icon: Icon }) => {
          const active = pathname === to;
          return (
            <Link
              key={to}
              to={to}
              className={cn(
                "flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium transition-all",
                active
                  ? "bg-sidebar-accent text-foreground glow-ring"
                  : "text-muted-foreground hover:bg-sidebar-accent/60 hover:text-foreground",
              )}
            >
              <Icon className="size-4" />
              {label}
              {active && <span className="ml-auto size-1.5 rounded-full bg-primary shadow-[0_0_8px_var(--primary)]" />}
            </Link>
          );
        })}
      </nav>

      <div className="mt-auto flex flex-col gap-3">
        <div className="rounded-xl border border-border/60 surface p-4">
          <div className="text-[11px] uppercase tracking-wider text-muted-foreground mb-1">Soil Moisture</div>
          <div className="text-2xl font-semibold tabular-nums text-primary glow-text">62.1%</div>
          <div className="mt-2 h-1.5 rounded-full bg-muted overflow-hidden">
            <div className="h-full w-[62%] rounded-full bg-gradient-to-r from-primary to-secondary" />
          </div>
        </div>
        <button className="flex items-center gap-2 px-3 py-2 rounded-lg text-sm text-muted-foreground hover:text-foreground hover:bg-sidebar-accent/60 transition-colors">
          <Settings className="size-4" />
          Settings
        </button>
      </div>
    </aside>
  );
}
