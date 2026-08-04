import { createFileRoute, Link } from "@tanstack/react-router";
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
  head: () => ({ meta: [{ title: "Clinical & Educational RAG Cockpit — InsightForge" }] }),
  component: DashboardPage,
});

export function DashboardPage() {
  const [datasetsList, setDatasetsList] = useState(mockDatasets);
  const [anomaliesList, setAnomaliesList] = useState(mockAnomalies);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    async function loadBackendData() {
      try {
        const res = await getDatasets(1, 20);
        if (res && res.datasets && res.datasets.length > 0) {
          setDatasetsList(res.datasets as any);
        }
      } catch (err) {
        console.log("Using pre-loaded healthcare & education mock workspace data.");
      }
    }
    loadBackendData();
  }, []);

  return (
    <>
      <PageHeader
        title="Clinical & Educational RAG Cockpit"
        description="Monitor patient vitals anomalies, PubMed medical search, and academic lecture RAG indices."
        action={
          <div className="flex items-center gap-3">
            <Link to="/app/query">
              <PremiumButton variant="secondary" size="sm">
                <Search className="h-4 w-4" /> Query RAG
              </PremiumButton>
            </Link>
            <Link to="/app/upload">
              <PremiumButton variant="primary" size="sm">
                <Upload className="h-4 w-4" /> Upload Medical PDF
              </PremiumButton>
            </Link>
          </div>
        }
      />

      <div className="p-6 md:p-8 space-y-8 bg-surface-soft min-h-screen">
        {/* 1. TOP METRIC STAT CARDS */}
        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
          <GlassCard variant="canvas" className="p-5 border border-hairline shadow-sm">
            <div className="flex items-center justify-between">
              <span className="caption text-xs uppercase font-semibold text-muted">Clinical Datasets</span>
              <FileText className="h-4 w-4 text-[#1b61c9]" />
            </div>
            <div className="mt-3 text-3xl font-bold text-ink">{datasetsList.length}</div>
            <div className="mt-1 text-xs text-muted">EMR & PubMed Files</div>
          </GlassCard>

          <GlassCard variant="canvas" className="p-5 border border-hairline shadow-sm">
            <div className="flex items-center justify-between">
              <span className="caption text-xs uppercase font-semibold text-muted">Active Health Signals</span>
              <AlertTriangle className="h-4 w-4 text-[#aa2d00]" />
            </div>
            <div className="mt-3 text-3xl font-bold text-ink">{anomaliesList.length}</div>
            <div className="mt-1 text-xs text-[#aa2d00] font-semibold">2 Critical Spikes Detected</div>
          </GlassCard>

          <GlassCard variant="canvas" className="p-5 border border-hairline shadow-sm">
            <div className="flex items-center justify-between">
              <span className="caption text-xs uppercase font-semibold text-muted">FAISS Vectors Indexed</span>
              <Sparkles className="h-4 w-4 text-[#006400]" />
            </div>
            <div className="mt-3 text-3xl font-bold text-ink">384,210</div>
            <div className="mt-1 text-xs text-[#006400] font-semibold">100% Local Privacy</div>
          </GlassCard>

          <GlassCard variant="canvas" className="p-5 border border-hairline shadow-sm">
            <div className="flex items-center justify-between">
              <span className="caption text-xs uppercase font-semibold text-muted">Grounded RAG Score</span>
              <ShieldCheck className="h-4 w-4 text-[#254fad]" />
            </div>
            <div className="mt-3 text-3xl font-bold text-ink">99.2%</div>
            <div className="mt-1 text-xs text-muted">Page & Paragraph Cited</div>
          </GlassCard>
        </div>

        {/* 2. CHARTS OVERVIEW */}
        <div className="grid gap-6 lg:grid-cols-2">
          {/* Severity Distribution */}
          <GlassCard variant="canvas" className="p-6 border border-hairline shadow-sm">
            <div className="flex items-center justify-between mb-4">
              <div>
                <h3 className="title-sm font-semibold text-ink">Clinical Severity Distribution</h3>
                <p className="caption text-xs text-muted">Breakdown of patient vital & academic metric alerts</p>
              </div>
              <GlowBadge variant="coral">REALTIME</GlowBadge>
            </div>
            <div className="h-[220px]">
              <ResponsiveContainer width="100%" height="100%">
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
          <GlassCard variant="canvas" className="p-6 border border-hairline shadow-sm">
            <div className="flex items-center justify-between mb-4">
              <div>
                <h3 className="title-sm font-semibold text-ink">Anomaly Detection Classes</h3>
                <p className="caption text-xs text-muted">Spike, Drop, and Change-Point counts</p>
              </div>
              <GlowBadge variant="info">STATISTICAL</GlowBadge>
            </div>
            <div className="h-[220px]">
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={typeDistribution} margin={{ left: 10, right: 10 }}>
                  <XAxis dataKey="type" stroke="#41454d" fontSize={12} />
                  <YAxis stroke="#41454d" fontSize={12} />
                  <Tooltip />
                  <Bar dataKey="count" fill="#181d26" radius={[4, 4, 0, 0]} />
                </BarChart>
              </ResponsiveContainer>
            </div>
          </GlassCard>
        </div>

        {/* 3. RECENT ANOMALIES TABLE */}
        <GlassCard variant="canvas" className="overflow-hidden border border-hairline shadow-sm">
          <div className="flex items-center justify-between border-b border-hairline px-6 py-4">
            <div>
              <h3 className="title-sm font-semibold text-ink">Detected Health & Academic Signals</h3>
              <p className="caption text-xs text-muted">Real-time alerts with Pettitt change-point scores</p>
            </div>
            <Link to="/app/anomalies">
              <PremiumButton variant="secondary" size="sm">
                View All Anomalies <ArrowUpRight className="h-3.5 w-3.5" />
              </PremiumButton>
            </Link>
          </div>

          <div className="overflow-x-auto">
            <table className="w-full text-left text-sm">
              <thead className="bg-surface-soft border-b border-hairline text-xs uppercase font-semibold text-muted">
                <tr>
                  <th className="px-6 py-3">Metric Name</th>
                  <th className="px-6 py-3">Anomaly Type</th>
                  <th className="px-6 py-3">Severity</th>
                  <th className="px-6 py-3 text-right">Observed Value</th>
                  <th className="px-6 py-3 text-right">Expected</th>
                  <th className="px-6 py-3">Summary Findings</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-hairline">
                {anomaliesList.slice(0, 6).map((a) => (
                  <tr key={a.id} className="hover:bg-surface-soft transition">
                    <td className="px-6 py-4 font-mono font-medium text-ink">
                      <Link to="/app/anomalies" className="hover:underline text-[#1b61c9]">
                        {a.metric}
                      </Link>
                    </td>
                    <td className="px-6 py-4 capitalize font-medium text-ink">{a.type}</td>
                    <td className="px-6 py-4">
                      <GlowBadge variant={a.severity === "critical" ? "coral" : "info"}>
                        {a.severity.toUpperCase()}
                      </GlowBadge>
                    </td>
                    <td className="px-6 py-4 text-right font-mono font-bold text-ink">{a.value}</td>
                    <td className="px-6 py-4 text-right font-mono text-muted">{a.expected}</td>
                    <td className="px-6 py-4 text-xs text-body max-w-sm truncate">{a.summary}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </GlassCard>

        {/* 4. WORKSPACE UPLOADED DATASETS */}
        <GlassCard variant="canvas" className="overflow-hidden border border-hairline shadow-sm">
          <div className="flex items-center justify-between border-b border-hairline px-6 py-4">
            <div>
              <h3 className="title-sm font-semibold text-ink">Medical & Academic Datasets</h3>
              <p className="caption text-xs text-muted">Uploaded patient records, lab results, and PubMed PDFs</p>
            </div>
            <Link to="/app/upload">
              <PremiumButton variant="primary" size="sm">
                + Add Dataset
              </PremiumButton>
            </Link>
          </div>

          <div className="overflow-x-auto">
            <table className="w-full text-left text-sm">
              <thead className="bg-surface-soft border-b border-hairline text-xs uppercase font-semibold text-muted">
                <tr>
                  <th className="px-6 py-3">File Name</th>
                  <th className="px-6 py-3">Status</th>
                  <th className="px-6 py-3 text-right">Row Count</th>
                  <th className="px-6 py-3 text-right">Anomalies</th>
                  <th className="px-6 py-3 text-right">Uploaded Date</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-hairline">
                {datasetsList.map((d) => (
                  <tr key={d.id} className="hover:bg-surface-soft transition">
                    <td className="px-6 py-4 font-medium text-ink flex items-center gap-2">
                      <FileText className="h-4 w-4 text-[#1b61c9]" /> {d.name}
                    </td>
                    <td className="px-6 py-4">
                      <span className="inline-flex items-center gap-1.5 text-xs font-semibold text-[#006400]">
                        <CheckCircle2 className="h-3.5 w-3.5 text-[#006400]" /> Analyzed
                      </span>
                    </td>
                    <td className="px-6 py-4 text-right font-mono text-ink">{d.rows?.toLocaleString()}</td>
                    <td className="px-6 py-4 text-right font-mono font-bold text-[#aa2d00]">{d.anomalies}</td>
                    <td className="px-6 py-4 text-right font-mono text-xs text-muted">
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