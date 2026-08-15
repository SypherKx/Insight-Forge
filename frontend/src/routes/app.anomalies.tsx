import { createFileRoute } from "@tanstack/react-router";
import { useMemo, useState, useEffect } from "react";
import { Filter, Search } from "lucide-react";
import { PageHeader } from "@/components/dashboard/DashboardShell";
import { GlassCard } from "@/components/premium/GlassCard";
import { GlowBadge } from "@/components/premium/GlowBadge";
import { mockAnomalies, mockDatasets } from "@/lib/mock-data";
import { getDatasets } from "../services/api";

export const Route = createFileRoute("/app/anomalies")({
  head: () => ({ meta: [{ title: "Clinical Anomaly Signals — InsightForge Health & Edu" }] }),
  component: AnomaliesPage,
});

export function AnomaliesPage() {
  const [datasetsList, setDatasetsList] = useState(mockDatasets);
  const [selectedDatasetId, setSelectedDatasetId] = useState<string>("ds_01");
  const [anomaliesList] = useState(mockAnomalies);
  const [minScore, setMinScore] = useState(0.2);
  const [q, setQ] = useState("");

  useEffect(() => {
    async function loadDatasets() {
      try {
        const res = await getDatasets(1, 20);
        if (res && res.datasets && res.datasets.length > 0) {
          setDatasetsList(res.datasets as any);
        }
      } catch (err) {
        console.log("Using healthcare mock anomaly dataset list.");
      }
    }
    loadDatasets();
  }, []);

  const filtered = useMemo(() => {
    return anomaliesList
      .filter((a) => (a.score ?? 0.8) >= minScore)
      .filter((a) => {
        if (!q) return true;
        const searchTarget = `${a.metric} ${a.type} ${a.summary}`.toLowerCase();
        return searchTarget.includes(q.toLowerCase());
      });
  }, [anomaliesList, minScore, q]);

  return (
    <>
      <PageHeader
        title="Clinical & Academic Anomaly Signals"
        description="Filter and score-rank detected blood lab spikes, patient vital drops, and student engagement deviations."
      />

      <div className="p-6 md:p-8 space-y-6 bg-[#000000] min-h-screen text-white">
        {/* FILTER CONTROLS */}
        <GlassCard variant="canvas" className="p-6 border border-white/10 shadow-sm bg-[#0a0a0a]">
          <div className="grid gap-6 md:grid-cols-3 items-end">
            <div>
              <label className="eyebrow-cap text-[#9dabad] block mb-2">
                Search Metric or Medical Summary
              </label>
              <div className="relative flex items-center">
                <Search className="absolute left-3.5 h-4 w-4 text-[#9dabad]" />
                <input
                  type="text"
                  value={q}
                  onChange={(e) => setQ(e.target.value)}
                  placeholder="e.g. glucose, heart_rate, exam..."
                  className="w-full rounded-lg border border-white/10 bg-[#141414] pl-10 pr-3 py-2 text-sm text-white outline-none focus:border-[#c1fbd4]"
                />
              </div>
            </div>

            <div>
              <label className="eyebrow-cap text-[#9dabad] block mb-2">
                Select Medical Dataset
              </label>
              <select
                value={selectedDatasetId}
                onChange={(e) => setSelectedDatasetId(e.target.value)}
                className="w-full rounded-lg border border-white/10 bg-[#141414] px-3 py-2 text-sm text-white outline-none focus:border-[#c1fbd4]"
              >
                {datasetsList.map((d) => (
                  <option key={d.id} value={d.id} className="bg-[#141414] text-white">
                    {d.name} ({d.anomalies} anomalies)
                  </option>
                ))}
              </select>
            </div>

            <div>
              <div className="flex justify-between eyebrow-cap text-[#9dabad] mb-2">
                <span>Minimum Confidence Score</span>
                <span className="font-mono text-[#c1fbd4] font-bold">{minScore.toFixed(2)}</span>
              </div>
              <input
                type="range"
                min={0}
                max={1}
                step={0.05}
                value={minScore}
                onChange={(e) => setMinScore(Number(e.target.value))}
                className="w-full accent-[#c1fbd4] cursor-pointer"
              />
            </div>
          </div>
        </GlassCard>

        {/* ANOMALIES SIGNAL TABLE */}
        <GlassCard variant="canvas" className="overflow-hidden border border-white/10 shadow-sm bg-[#0a0a0a]">
          <div className="flex items-center justify-between border-b border-white/10 px-6 py-4">
            <span className="eyebrow-cap text-[#9dabad] flex items-center gap-2">
              <Filter className="h-4 w-4 text-[#c1fbd4]" /> Showing {filtered.length} signal matches
            </span>
            <GlowBadge variant="mint">PETTITT TEST RANKED</GlowBadge>
          </div>

          <div className="overflow-x-auto">
            <table className="w-full text-left text-sm">
              <thead className="bg-[#141414] border-b border-white/10 eyebrow-cap text-[#9dabad]">
                <tr>
                  <th className="px-6 py-3">Metric Name</th>
                  <th className="px-6 py-3">Anomaly Type</th>
                  <th className="px-6 py-3">Severity</th>
                  <th className="px-6 py-3 text-right">Score</th>
                  <th className="px-6 py-3 text-right">Value</th>
                  <th className="px-6 py-3 text-right">Baseline</th>
                  <th className="px-6 py-3">Clinical Summary</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-white/10">
                {filtered.map((a) => (
                  <tr key={a.id} className="hover:bg-[#141414] transition">
                    <td className="px-6 py-4 font-mono font-medium text-white">{a.metric}</td>
                    <td className="px-6 py-4 capitalize font-semibold text-white">{a.type}</td>
                    <td className="px-6 py-4">
                      <GlowBadge variant={a.severity === "critical" ? "mint" : "shade"}>
                        {a.severity.toUpperCase()}
                      </GlowBadge>
                    </td>
                    <td className="px-6 py-4 text-right font-mono font-bold text-[#c1fbd4]">
                      {a.score.toFixed(2)}
                    </td>
                    <td className="px-6 py-4 text-right font-mono font-bold text-white">{a.value}</td>
                    <td className="px-6 py-4 text-right font-mono text-[#9dabad]">{a.expected}</td>
                    <td className="px-6 py-4 text-xs text-[#e4e4e7] max-w-sm">{a.summary}</td>
                  </tr>
                ))}
                {filtered.length === 0 && (
                  <tr>
                    <td colSpan={7} className="px-6 py-12 text-center text-[#9dabad]">
                      No medical anomalies match the current filter criteria.
                    </td>
                  </tr>
                )}
              </tbody>
            </table>
          </div>
        </GlassCard>
      </div>
    </>
  );
}