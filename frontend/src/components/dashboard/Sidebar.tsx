import { Link, useRouterState } from "@tanstack/react-router";
import { LayoutDashboard, Upload, AlertOctagon, Search, ArrowLeft, Activity } from "lucide-react";
import { BrandLogo } from "@/components/brand/BrandLogo";
import { cn } from "@/lib/utils";
import { useEffect, useState } from "react";
import { checkHealth } from "../../services/api";

const nav = [
  {
    to: "/app/dashboard",
    label: "Dashboard",
    product: "WAYPOINT ATTRIBUTION",
    color: "#c1fbd4",
    icon: LayoutDashboard,
  },
  {
    to: "/app/anomalies",
    label: "Anomalies",
    product: "TERRAFORM ENGINE",
    color: "#c1fbd4",
    icon: AlertOctagon,
  },
  {
    to: "/app/upload",
    label: "Upload Data",
    product: "NOMAD INGESTION",
    color: "#c1fbd4",
    icon: Upload,
  },
  {
    to: "/app/query",
    label: "Query Panel",
    product: "VAULT KNOWLEDGE RAG",
    color: "#c1fbd4",
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
    <aside className="hidden md:flex w-[260px] shrink-0 flex-col border-r border-white/10 bg-[#0a0a0a] transition-colors duration-300 text-white">
      {/* Brand Header */}
      <Link to="/" className="flex items-center border-b border-white/10 px-6 py-5">
        <BrandLogo size="md" />
      </Link>

      {/* Navigation List */}
      <div className="flex-1 px-4 py-6">
        <div className="eyebrow-cap px-2 pb-3 text-[#9dabad]">
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
                      ? "bg-[#18181b] border-white/20 text-white font-semibold shadow-sm"
                      : "text-[#9dabad] hover:text-white hover:bg-[#141414] border-transparent"
                  )}
                >
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-2.5">
                      <Icon className="h-4 w-4" style={{ color: active ? "#c1fbd4" : "currentColor" }} />
                      <span className="text-sm">{n.label}</span>
                    </div>
                    {active && <span className="h-2 w-2 rounded-full bg-[#c1fbd4]" />}
                  </div>
                  <span className="font-mono text-[10px] uppercase text-[#9dabad] mt-1">
                    {n.product}
                  </span>
                </Link>
              </li>
            );
          })}
        </ul>
      </div>

      {/* System Health Component */}
      <div className="border-t border-white/10 p-4">
        <div className="rounded-xl border border-white/10 bg-[#141414] p-4">
          <div className="flex items-center gap-2 text-xs font-semibold text-white mb-2">
            <Activity className="h-4 w-4 text-[#c1fbd4]" /> System Status
          </div>
          <div className="space-y-2 font-mono text-[11px]">
            <Row label="FastAPI Backend" status={health.api} />
            <Row label="FAISS RAG Index" status={health.rag} />
            <Row label="Anomaly Detector" status={health.detector} />
          </div>
        </div>

        <Link
          to="/"
          className="mt-3 flex items-center justify-center gap-2 rounded-lg border border-white/10 bg-[#141414] px-4 py-2.5 text-xs font-medium text-[#9dabad] hover:text-white hover:bg-[#1f1f1f] transition"
        >
          <ArrowLeft className="h-3.5 w-3.5" /> Return to Overview
        </Link>
      </div>
    </aside>
  );
}

function Row({ label, status }: { label: string; status: ServiceStatus }) {
  const colorClass =
    status === "ok" ? "bg-[#c1fbd4]" : status === "warn" ? "bg-amber-400" : "bg-red-500";

  return (
    <div className="flex items-center justify-between text-[#9dabad]">
      <span>{label}</span>
      <span className="flex items-center gap-1.5">
        <span className={cn("h-1.5 w-1.5 rounded-full", colorClass)} />
        <span className="text-[10px] font-semibold text-white">
          {status === "ok" ? "OK" : status === "warn" ? "WARN" : "DOWN"}
        </span>
      </span>
    </div>
  );
}