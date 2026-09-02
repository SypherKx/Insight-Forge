import { createFileRoute, Link, redirect } from "@tanstack/react-router";
import { motion } from "framer-motion";
import { Activity, AlertTriangle, FileText, Search, Upload, ArrowUpRight, CheckCircle2, ShieldCheck, Sparkles } from "lucide-react";
import {
  Bar, BarChart, Cell, Pie, PieChart, ResponsiveContainer, Tooltip, XAxis, YAxis,
} from "recharts";
import { PageHeader } from "@/components/dashboard/DashboardShell";
import { GlassCard } from "@/components/premium/GlassCard";
import { GlowBadge } from "@/components/premium/GlowBadge";
import { PremiumButton } from "@/components/premium/PremiumButton";
import { mockDatasets, mockAnomalies, severityDistribution, typeDistribution } from "@/lib/mock-data";
import { getDatasets } from "../services/api";
import { useEffect, useState } from "react";

export const Route = createFileRoute("/app/dashboard")({
  beforeLoad: () => {
    throw redirect({ to: "/app/query" });
  },
  head: () => ({ meta: [{ title: "Clinical & Educational RAG Cockpit — InsightForge" }] }),
  component: DashboardPage,
});

export function DashboardPage() {
  const [datasetsList, setDatasetsList] = useState(mockDatasets);
  const [anomaliesList, setAnomaliesList] = useState(mockAnomalies);

  useEffect(() => {
    let isMounted = true;
    async function loadBackendData() {
      try {
        const res = await getDatasets(1, 20);
        if (isMounted && res && res.datasets && res.datasets.length > 0) {
          setDatasetsList(res.datasets as any);
        }
      } catch (err) {
        // Fallback to preloaded mock data safely
      }
    }
    loadBackendData();
    return () => {
      isMounted = false;
    };
  }, []);

  return (
    <>
      <PageHeader
        title="Clinical & Educational RAG Cockpit"
        description="Monitor patient vitals anomalies, PubMed medical search, and academic lecture RAG indices."
        action={
          <div className="flex items-center gap-3">
            <Link to="/app/query">
              <PremiumButton variant="outlineOnDark" size="sm">
                <Search className="h-4 w-4" /> Query RAG
              </PremiumButton>
            </Link>
            <Link to="/app/upload">
              <PremiumButton variant="primaryPill" size="sm">
                <Upload className="h-4 w-4" /> Upload Medical PDF
              </PremiumButton>
            </Link>
          </div>
        }
      />

      <div className="p-6 md:p-8 space-y-8 bg-[var(--canvas)] min-h-screen text-[var(--ink)] transition-colors duration-300">
        {/* 1. TOP METRIC STAT CARDS */}
        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
          <GlassCard variant="canvas" className="p-5 border border-[var(--hairline)] shadow-sm bg-[var(--surface-card)]">
            <div className="flex items-center justify-between">
              <span className="caption text-xs uppercase font-semibold text-[var(--muted)]">Clinical Datasets</span>
              <FileText className="h-4 w-4 text-[#c1fbd4]" />
            </div>
            <div className="mt-3 text-3xl font-bold text-[var(--ink)]">{datasetsList.length}</div>
            <div className="mt-1 text-xs text-[var(--muted)]">EMR & PubMed Files</div>
          </GlassCard>

          <GlassCard variant="canvas" className="p-5 border border-[var(--hairline)] shadow-sm bg-[var(--surface-card)]">
            <div className="flex items-center justify-between">
              <span className="caption text-xs uppercase font-semibold text-[var(--muted)]">Active Health Signals</span>
              <AlertTriangle className="h-4 w-4 text-[#aa2d00]" />
            </div>
            <div className="mt-3 text-3xl font-bold text-[var(--ink)]">{anomaliesList.length}</div>
            <div className="mt-1 text-xs text-[#aa2d00] font-semibold">2 Critical Spikes Detected</div>
          </GlassCard>

          <GlassCard variant="canvas" className="p-5 border border-[var(--hairline)] shadow-sm bg-[var(--surface-card)]">
            <div className="flex items-center justify-between">
              <span className="caption text-xs uppercase font-semibold text-[var(--muted)]">FAISS Vectors Indexed</span>
              <Sparkles className="h-4 w-4 text-[#c1fbd4]" />
            </div>
            <div className="mt-3 text-3xl font-bold text-[var(--ink)]">384,210</div>
            <div className="mt-1 text-xs text-[#c1fbd4] font-semibold">100% Local Privacy</div>
          </GlassCard>

          <GlassCard variant="canvas" className="p-5 border border-[var(--hairline)] shadow-sm bg-[var(--surface-card)]">
            <div className="flex items-center justify-between">
              <span className="caption text-xs uppercase font-semibold text-[var(--muted)]">Grounded RAG Score</span>
              <ShieldCheck className="h-4 w-4 text-[#c1fbd4]" />
            </div>
            <div className="mt-3 text-3xl font-bold text-[var(--ink)]">99.2%</div>
            <div className="mt-1 text-xs text-[var(--muted)]">Page & Paragraph Cited</div>
          </GlassCard>
        </div>

        {/* 2. CHARTS OVERVIEW (SAFE NON-BLOCKING RESIZE CONTAINER) */}
        <div className="grid gap-6 lg:grid-cols-2 min-w-0">
          {/* Severity Distribution */}
          <GlassCard variant="canvas" className="p-6 border border-[var(--hairline)] shadow-sm bg-[var(--surface-card)] min-w-0">
            <div className="flex items-center justify-between mb-4">
              <div>
                <h3 className="heading-sm font-semibold text-[var(--ink)]">Clinical Severity Distribution</h3>
                <p className="caption text-xs text-[var(--muted)]">Breakdown of patient vital & academic metric alerts</p>
              </div>
              <GlowBadge variant="mint">REALTIME</GlowBadge>
            </div>
            <div className="h-[220px] w-full min-w-0">
              <ResponsiveContainer debounce={50} width="100%" height={220}>
                <PieChart>
                  <Pie
                    data={severityDistribution}
                    dataKey="count"
                    nameKey="severity"
                    innerRadius={55}
                    outerRadius={85}
                    paddingAngle={4}
                  >
                    {severityDistribution.map((s) => (
                      <Cell key={s.severity} fill={s.color} />
                    ))}
                  </Pie>
                  <Tooltip />
                </PieChart>
              </ResponsiveContainer>
            </div>
          </GlassCard>

          {/* Anomaly Types */}
          <GlassCard variant="canvas" className="p-6 border border-[var(--hairline)] shadow-sm bg-[var(--surface-card)] min-w-0">
            <div className="flex items-center justify-between mb-4">
              <div>
                <h3 className="heading-sm font-semibold text-[var(--ink)]">Anomaly Detection Classes</h3>
                <p className="caption text-xs text-[var(--muted)]">Spike, Drop, and Change-Point counts</p>
              </div>
              <GlowBadge variant="shade">STATISTICAL</GlowBadge>
            </div>
            <div className="h-[220px] w-full min-w-0">
              <ResponsiveContainer debounce={50} width="100%" height={220}>
                <BarChart data={typeDistribution} margin={{ left: 10, right: 10 }}>
                  <XAxis dataKey="type" stroke="#9dabad" fontSize={12} />
                  <YAxis stroke="#9dabad" fontSize={12} />
                  <Tooltip />
                  <Bar dataKey="count" fill="#c1fbd4" radius={[4, 4, 0, 0]} />
                </BarChart>
              </ResponsiveContainer>
            </div>
          </GlassCard>
        </div>

        {/* 3. RECENT ANOMALIES TABLE */}
        <GlassCard variant="canvas" className="overflow-hidden border border-[var(--hairline)] shadow-sm bg-[var(--surface-card)]">
          <div className="flex items-center justify-between border-b border-[var(--hairline)] px-6 py-4">
            <div>
              <h3 className="heading-sm font-semibold text-[var(--ink)]">Detected Health & Academic Signals</h3>
              <p className="caption text-xs text-[var(--muted)]">Real-time alerts with Pettitt change-point scores</p>
            </div>
            <Link to="/app/anomalies">
              <PremiumButton variant="outlineOnDark" size="sm">
                View All Anomalies <ArrowUpRight className="h-3.5 w-3.5" />
              </PremiumButton>
            </Link>
          </div>

          <div className="overflow-x-auto">
            <table className="w-full text-left text-sm">
              <thead className="bg-[var(--surface-soft)] border-b border-[var(--hairline)] text-xs uppercase font-semibold text-[var(--muted)]">
                <tr>
                  <th className="px-6 py-3">Metric Name</th>
                  <th className="px-6 py-3">Anomaly Type</th>
                  <th className="px-6 py-3">Severity</th>
                  <th className="px-6 py-3 text-right">Observed Value</th>
                  <th className="px-6 py-3 text-right">Expected</th>
                  <th className="px-6 py-3">Summary Findings</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-[var(--hairline)]">
                {anomaliesList.slice(0, 6).map((a) => (
                  <tr key={a.id} className="hover:bg-[var(--surface-soft)] transition">
                    <td className="px-6 py-4 font-mono font-medium text-[var(--ink)]">
                      <Link to="/app/anomalies" className="hover:underline text-[#c1fbd4]">
                        {a.metric}
                      </Link>
                    </td>
                    <td className="px-6 py-4 capitalize font-medium text-[var(--ink)]">{a.type}</td>
                    <td className="px-6 py-4">
                      <GlowBadge variant={a.severity === "critical" ? "coral" : "shade"}>
                        {a.severity.toUpperCase()}
                      </GlowBadge>
                    </td>
                    <td className="px-6 py-4 text-right font-mono font-bold text-[var(--ink)]">{a.value}</td>
                    <td className="px-6 py-4 text-right font-mono text-[var(--muted)]">{a.expected}</td>
                    <td className="px-6 py-4 text-xs text-[var(--body)] max-w-sm truncate">{a.summary}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </GlassCard>

        {/* 4. WORKSPACE UPLOADED DATASETS */}
        <GlassCard variant="canvas" className="overflow-hidden border border-[var(--hairline)] shadow-sm bg-[var(--surface-card)]">
          <div className="flex items-center justify-between border-b border-[var(--hairline)] px-6 py-4">
            <div>
              <h3 className="heading-sm font-semibold text-[var(--ink)]">Medical & Academic Datasets</h3>
              <p className="caption text-xs text-[var(--muted)]">Uploaded patient records, lab results, and PubMed PDFs</p>
            </div>
            <Link to="/app/upload">
              <PremiumButton variant="primaryPill" size="sm">
                + Add Dataset
              </PremiumButton>
            </Link>
          </div>

          <div className="overflow-x-auto">
            <table className="w-full text-left text-sm">
              <thead className="bg-[var(--surface-soft)] border-b border-[var(--hairline)] text-xs uppercase font-semibold text-[var(--muted)]">
                <tr>
                  <th className="px-6 py-3">File Name</th>
                  <th className="px-6 py-3">Status</th>
                  <th className="px-6 py-3 text-right">Row Count</th>
                  <th className="px-6 py-3 text-right">Anomalies</th>
                  <th className="px-6 py-3 text-right">Uploaded Date</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-[var(--hairline)]">
                {datasetsList.map((d) => (
                  <tr key={d.id} className="hover:bg-[var(--surface-soft)] transition">
                    <td className="px-6 py-4 font-medium text-[var(--ink)] flex items-center gap-2">
                      <FileText className="h-4 w-4 text-[#c1fbd4]" /> {d.name}
                    </td>
                    <td className="px-6 py-4">
                      <span className="inline-flex items-center gap-1.5 text-xs font-semibold text-[#c1fbd4]">
                        <CheckCircle2 className="h-3.5 w-3.5 text-[#c1fbd4]" /> Analyzed
                      </span>
                    </td>
                    <td className="px-6 py-4 text-right font-mono text-[var(--ink)]">{d.rows?.toLocaleString()}</td>
                    <td className="px-6 py-4 text-right font-mono font-bold text-[#aa2d00]">{d.anomalies}</td>
                    <td className="px-6 py-4 text-right font-mono text-xs text-[var(--muted)]">
                      {new Date(d.uploadedAt).toLocaleDateString()}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </GlassCard>
      </div>
    </>
  );
}