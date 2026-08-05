import { Link, useRouterState } from "@tanstack/react-router";
import { LayoutDashboard, Upload, AlertOctagon, Search, ArrowLeft, Activity, Sparkles } from "lucide-react";
import { cn } from "@/lib/utils";
import { useEffect, useState } from "react";
import { checkHealth } from "../../services/api";

const nav = [
  {
    to: "/app/dashboard",
    label: "Dashboard",
    product: "WAYPOINT ATTRIBUTION",
    color: "var(--primary)",
    icon: LayoutDashboard,
  },
  {
    to: "/app/anomalies",
    label: "Anomalies",
    product: "TERRAFORM ENGINE",
    color: "#a9583e",
    icon: AlertOctagon,
  },
  {
    to: "/app/upload",
    label: "Upload Data",
    product: "NOMAD INGESTION",
    color: "var(--success)",
    icon: Upload,
  },
  {
    to: "/app/query",
    label: "Query Panel",
    product: "VAULT KNOWLEDGE RAG",
    color: "#254fad",
    icon: Search,
  },
] as const;

type ServiceStatus = "ok" | "warn" | "down";

export function Sidebar() {
  const path = useRouterState({ select: (s) => s.location.pathname });

  const [health, setHealth] = useState({
    api: "ok" as ServiceStatus,
    rag: "ok" as ServiceStatus,
    detector: "ok" as ServiceStatus,
  });

  useEffect(() => {
    let intervalId: any = null;

    async function fetchHealth() {
      try {
        const res = await checkHealth();
        setHealth({
          api: "ok",
          rag: res.rag_enabled ? "ok" : "down",
          detector: res.services?.detection_engine === "healthy" ? "ok" : "warn",
        });
      } catch (err) {
        setHealth({
          api: "down",
          rag: "down",
          detector: "down",
        });
        // Clear polling interval on connection error to keep UI snappy
        if (intervalId) clearInterval(intervalId);
      }
    }

    fetchHealth();
    intervalId = setInterval(fetchHealth, 60000);
    return () => {
      if (intervalId) clearInterval(intervalId);
    };
  }, []);

  return (
    <aside className="hidden md:flex w-[260px] shrink-0 flex-col border-r border-[var(--hairline)] bg-[var(--canvas)] transition-colors duration-300">
      {/* Brand Header */}
      <Link to="/" className="flex items-center gap-3 border-b border-[var(--hairline)] px-6 py-5">
        <div className="flex h-7 w-7 items-center justify-center rounded-md bg-[var(--primary)] text-white font-bold shadow-sm">
          <Sparkles className="h-4 w-4" />
        </div>
        <div className="flex items-baseline gap-1.5">
          <span className="text-base font-bold tracking-tight text-[var(--ink)]">InsightForge</span>
          <span className="text-xs font-semibold text-[var(--primary)]">AI</span>
        </div>
      </Link>

      {/* Navigation List */}
      <div className="flex-1 px-4 py-6">
        <div className="caption-uppercase px-2 pb-3 text-xs font-semibold text-[var(--muted)]">
          WORKSPACE MODULES
        </div>
        <ul className="flex flex-col gap-1.5">
          {nav.map((n) => {
            const active = path === n.to || (n.to !== "/app/dashboard" && path.startsWith(n.to));
            const Icon = n.icon;

            return (
              <li key={n.to}>
                <Link
                  to={n.to}
                  className={cn(
                    "group flex flex-col rounded-xl px-4 py-3 transition-all duration-200 border",
                    active
                      ? "bg-[var(--surface-card)] border-[var(--hairline)] text-[var(--ink)] font-semibold shadow-sm"
                      : "text-[var(--muted)] hover:text-[var(--ink)] hover:bg-[var(--surface-soft)] border-transparent"
                  )}
                >
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-2.5">
                      <Icon className="h-4 w-4" style={{ color: active ? "var(--primary)" : "currentColor" }} />
                      <span className="text-sm">{n.label}</span>
                    </div>
                    {active && <span className="h-2 w-2 rounded-full bg-[var(--primary)]" />}
                  </div>
                  <span className="font-mono text-[10px] uppercase text-[var(--muted)] mt-1">
                    {n.product}
                  </span>
                </Link>
              </li>
            );
          })}
        </ul>
      </div>

      {/* System Health Component */}
      <div className="border-t border-[var(--hairline)] p-4">
        <div className="rounded-xl border border-[var(--hairline)] bg-[var(--surface-soft)] p-4">
          <div className="flex items-center gap-2 text-xs font-semibold text-[var(--ink)] mb-2">
            <Activity className="h-4 w-4 text-[var(--success)]" /> System Status
          </div>
          <div className="space-y-2 font-mono text-[11px]">
            <Row label="FastAPI Backend" status={health.api} />
            <Row label="FAISS RAG Index" status={health.rag} />
            <Row label="Anomaly Detector" status={health.detector} />
          </div>
        </div>

        <Link
          to="/"
          className="mt-3 flex items-center justify-center gap-2 rounded-lg border border-[var(--hairline)] bg-[var(--canvas)] px-4 py-2.5 text-xs font-medium text-[var(--muted)] hover:text-[var(--ink)] hover:bg-[var(--surface-soft)] transition"
        >
          <ArrowLeft className="h-3.5 w-3.5" /> Return to Overview
        </Link>
      </div>
    </aside>
  );
}

function Row({ label, status }: { label: string; status: ServiceStatus }) {
  const colorClass =
    status === "ok" ? "bg-[var(--success)]" : status === "warn" ? "bg-[var(--accent-amber)]" : "bg-[var(--error)]";

  return (
    <div className="flex items-center justify-between text-[var(--muted)]">
      <span>{label}</span>
      <span className="flex items-center gap-1.5">
        <span className={cn("h-1.5 w-1.5 rounded-full", colorClass)} />
        <span className="text-[10px] font-semibold text-[var(--ink)]">
          {status === "ok" ? "OK" : status === "warn" ? "WARN" : "DOWN"}
        </span>
      </span>
    </div>
  );
}