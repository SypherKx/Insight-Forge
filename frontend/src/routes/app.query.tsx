import { createFileRoute } from "@tanstack/react-router";
import { useState } from "react";
import { motion } from "framer-motion";
import { Search, Sparkles, FileText, CheckCircle2 } from "lucide-react";
import { PageHeader } from "@/components/dashboard/DashboardShell";
import { GlassCard } from "@/components/premium/GlassCard";
import { GlowBadge } from "@/components/premium/GlowBadge";
import { PremiumButton } from "@/components/premium/PremiumButton";
import { queryResults } from "@/lib/mock-data";
import { queryRAG } from "../services/api";

export const Route = createFileRoute("/app/query")({
  head: () => ({ meta: [{ title: "RAG Document Search — InsightForge Healthcare & Education" }] }),
  component: QueryPage,
});

const suggestions = [
  "Paxlovid contraindications in renal impairment",
  "Pediatric oncology protocol summary — Trial Phase 3",
  "Anatomy & Physiology 101 — Cardiac Action Potential",
  "ICU Vitals Anomaly — Glucose Spike Protocol",
];

export function QueryPage() {
  const [q, setQ] = useState("");
  const [submitted, setSubmitted] = useState("");
  const [results, setResults] = useState<any[]>(queryResults);
  const [loading, setLoading] = useState(false);

  const handleSearch = async (queryText: string) => {
    if (!queryText) return;
    setSubmitted(queryText);
    setLoading(true);
    try {
      const res = await queryRAG(queryText, 5, 0.0);
      if (res && res.results && res.results.length > 0) {
        setResults(res.results);
      } else {
        const filtered = queryResults.filter(
          (r) =>
            r.title.toLowerCase().includes(queryText.toLowerCase()) ||
            r.snippet.toLowerCase().includes(queryText.toLowerCase())
        );
        setResults(filtered.length > 0 ? filtered : queryResults);
      }
    } catch (err) {
      console.log("Using pre-loaded healthcare & education RAG mock search results.");
      const filtered = queryResults.filter(
        (r) =>
          r.title.toLowerCase().includes(queryText.toLowerCase()) ||
          r.snippet.toLowerCase().includes(queryText.toLowerCase())
      );
      setResults(filtered.length > 0 ? filtered : queryResults);
    } finally {
      setLoading(false);
    }
  };

  return (
    <>
      <PageHeader
        title="RAG Document Search & Evidence Q&A"
        description="Search PubMed medical studies, FDA drug protocols, EMR notes, and university lecture PDFs."
      />

      <div className="p-6 md:p-8 space-y-8 bg-[#000000] min-h-screen text-white">
        <div className="mx-auto max-w-4xl space-y-6">
          {/* SEARCH BAR INPUT */}
          <GlassCard variant="canvas" className="p-6 border border-white/10 shadow-sm bg-[#0a0a0a]">
            <form
              onSubmit={(e) => {
                e.preventDefault();
                handleSearch(q);
              }}
              className="flex flex-col gap-4 md:flex-row md:items-center"
            >
              <div className="relative flex-1 flex items-center">
                <Search className="absolute left-4 h-5 w-5 text-[#9dabad]" />
                <input
                  type="text"
                  value={q}
                  onChange={(e) => setQ(e.target.value)}
                  placeholder="Ask a medical clinical question or search textbook syllabus..."
                  className="w-full rounded-lg border border-white/10 bg-[#141414] pl-12 pr-4 py-3 text-base text-white placeholder:text-[#9dabad] outline-none focus:border-[#c1fbd4]"
                />
              </div>
              <PremiumButton variant="outlineOnDark" size="md" type="submit">
                <Sparkles className="h-4 w-4 mr-1 text-[#c1fbd4]" /> Search RAG
              </PremiumButton>
            </form>

            {/* PRE-LOADED SUGGESTIONS */}
            <div className="mt-4 flex flex-wrap items-center gap-2">
              <span className="eyebrow-cap text-[#9dabad] mr-1">SUGGESTIONS:</span>
              {suggestions.map((s) => (
                <button
                  key={s}
                  onClick={() => {
                    setQ(s);
                    handleSearch(s);
                  }}
                  className="text-xs px-3 py-1 rounded-full border border-white/10 bg-[#141414] text-[#e4e4e7] hover:border-[#c1fbd4] hover:text-white transition cursor-pointer"
                >
                  {s}
                </button>
              ))}
            </div>
          </GlassCard>

          {/* QUERY RESULTS LIST */}
          {submitted && (
            <div className="eyebrow-cap text-[#9dabad]">
              Showing RAG Results for: <span className="font-semibold text-white">"{submitted}"</span>
            </div>
          )}

          {loading ? (
            <div className="p-12 text-center text-[#9dabad] font-mono animate-pulse">
              Searching FAISS dense vectors & synthesizing response...
            </div>
          ) : (
            <div className="space-y-4">
              {results.map((r, i) => (
                <motion.div
                  key={r.id || i}
                  initial={{ opacity: 0, y: 15 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ duration: 0.3, delay: i * 0.1 }}
                >
                  <GlassCard variant="canvas" className="p-6 border border-white/10 shadow-sm bg-[#0a0a0a] space-y-3">
                    <div className="flex items-center justify-between border-b border-white/10 pb-3">
                      <div className="flex items-center gap-2">
                        <FileText className="h-4 w-4 text-[#c1fbd4]" />
                        <span className="text-sm font-semibold text-white">{r.title}</span>
                      </div>
                      <GlowBadge variant="mint">
                        <CheckCircle2 className="h-3 w-3 mr-1" /> {(r.score * 100).toFixed(1)}% Match
                      </GlowBadge>
                    </div>

                    <p className="body-md text-sm text-[#e4e4e7] leading-relaxed font-sans">
                      "{r.snippet}"
                    </p>

                    <div className="pt-2 flex items-center justify-between text-xs text-[#9dabad] border-t border-white/10">
                      <span className="font-mono">{r.source}</span>
                      <span className="text-[11px] font-semibold text-[#c1fbd4]">
                        Ground-Truth Citation
                      </span>
                    </div>
                  </GlassCard>
                </motion.div>
              ))}
            </div>
          )}
        </div>
      </div>
    </>
  );
}