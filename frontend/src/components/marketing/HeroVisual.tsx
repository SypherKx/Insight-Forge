import { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { Search, Sparkles, CheckCircle2, FileText, Activity, ArrowRight } from "lucide-react";

const sampleQueries = [
  {
    id: "q1",
    label: "Paxlovid renal dosage",
    question: "What is the recommended Paxlovid dosage for moderate renal impairment?",
    doc: "FDA Clinical Guidelines 2025.pdf",
    page: "Page 14, Sec 4.2",
    score: 99.4,
    answer: "Administer 150 mg nirmatrelvir (one 150 mg tablet) and 100 mg ritonavir (one 100 mg tablet) together twice daily for 5 days.",
    tag: "FDA GUIDELINE",
  },
  {
    id: "q2",
    label: "Pediatric leukemia trial",
    question: "What were the Phase 3 trial survival outcomes in pediatric B-cell leukemia?",
    doc: "PubMed_Article_38291.pdf",
    page: "Page 8, Table 3",
    score: 98.8,
    answer: "Combination immunotherapy demonstrated a 42% improvement in 3-year event-free survival rate compared to standard chemotherapy.",
    tag: "PUBMED RESEARCH",
  },
  {
    id: "q3",
    label: "Anatomy 101 action potential",
    question: "Explain Phase 0 and Phase 2 of the cardiac action potential.",
    doc: "Medical_Physiology_Textbook.pdf",
    page: "Chapter 7, Page 142",
    score: 97.5,
    answer: "Phase 0 rapid depolarization is mediated by voltage-gated Fast Na+ channels. Phase 2 plateau is sustained by inward L-type Ca2+ current.",
    tag: "UNIVERSITY SYLLABUS",
  },
];

export function HeroVisual() {
  const [activeIdx, setActiveIdx] = useState(0);
  const activeItem = sampleQueries[activeIdx];

  return (
    <motion.div
      initial={{ opacity: 0, y: 25 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.8, ease: [0.22, 1, 0.36, 1] }}
      className="relative w-full"
    >
      {/* Outer Floating Card Container */}
      <div className="rounded-2xl border border-[var(--hairline)] bg-[var(--surface-card)] p-6 shadow-xl transition-colors duration-300">
        
        {/* Interactive Header & Status */}
        <div className="flex items-center justify-between border-b border-[var(--hairline)] pb-4 mb-4">
          <div className="flex items-center gap-2">
            <Sparkles className="h-4 w-4 text-[var(--primary)]" />
            <span className="text-xs font-sans font-semibold uppercase tracking-wider text-[var(--ink)]">
              LIVE RAG VECTOR SEARCH
            </span>
          </div>
          <span className="badge-coral text-[11px]">
            <Sparkles className="h-3 w-3 inline mr-1" /> FAISS 100% LOCAL
          </span>
        </div>

        {/* Interactive Clickable Sample Buttons */}
        <div className="mb-4">
          <div className="caption text-[11px] uppercase font-semibold text-[var(--muted)] mb-2">
            TRY CLICKING A CLINICAL QUESTION:
          </div>
          <div className="flex flex-wrap gap-2">
            {sampleQueries.map((item, idx) => (
              <button
                key={item.id}
                onClick={() => setActiveIdx(idx)}
                className={`text-xs px-3 py-1.5 rounded-full font-medium transition-all ${
                  activeIdx === idx
                    ? "bg-[var(--primary)] text-white shadow-sm font-semibold scale-105"
                    : "bg-[var(--canvas)] text-[var(--ink)] border border-[var(--hairline)] hover:border-[var(--primary)]"
                }`}
              >
                {item.label}
              </button>
            ))}
          </div>
        </div>

        {/* Simulated Search Input Box */}
        <div className="relative flex items-center rounded-xl border border-[var(--hairline)] bg-[var(--canvas)] px-4 py-3 shadow-inner mb-4">
          <Search className="h-4 w-4 text-[var(--primary)] mr-2 shrink-0" />
          <span className="text-sm font-medium text-[var(--ink)] truncate">
            {activeItem.question}
          </span>
        </div>

        {/* Animated Answer & Citation Result Card */}
        <AnimatePresence mode="wait">
          <motion.div
            key={activeItem.id}
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -10 }}
            transition={{ duration: 0.3 }}
            className="rounded-xl border border-[var(--hairline)] bg-[var(--canvas)] p-5 shadow-sm space-y-3"
          >
            {/* Document Source Header */}
            <div className="flex items-center justify-between border-b border-[var(--hairline)] pb-3">
              <div className="flex items-center gap-2">
                <FileText className="h-4 w-4 text-[var(--primary)]" />
                <span className="text-xs font-semibold text-[var(--ink)]">{activeItem.doc}</span>
                <span className="text-[11px] text-[var(--muted)] font-mono">({activeItem.page})</span>
              </div>
              <span className="text-xs font-mono font-bold text-[var(--success)] flex items-center gap-1">
                <CheckCircle2 className="h-3.5 w-3.5" /> {activeItem.score}% Match
              </span>
            </div>

            {/* Answer Content */}
            <p className="body-md text-sm text-[var(--body-strong)] leading-relaxed">
              "{activeItem.answer}"
            </p>

            {/* Evidence Footer Pill */}
            <div className="pt-2 flex items-center justify-between text-xs border-t border-[var(--hairline)]">
              <span className="badge-pill text-[10px]">{activeItem.tag}</span>
              <span className="text-[11px] font-semibold text-[var(--primary)] flex items-center gap-1">
                Ground-Truth Cited <ArrowRight className="h-3 w-3" />
              </span>
            </div>
          </motion.div>
        </AnimatePresence>

        {/* Real-time Health Signal Indicator */}
        <div className="mt-4 flex items-center justify-between text-xs text-[var(--muted)] pt-2 border-t border-[var(--hairline)]">
          <span className="flex items-center gap-1.5">
            <Activity className="h-3.5 w-3.5 text-[var(--success)] animate-pulse" />
            <span className="font-mono text-[11px]">PETTITT CHANGE-POINT DETECTOR: ONLINE</span>
          </span>
          <span className="font-mono text-[11px] font-bold text-[var(--ink)]">0.4ms Latency</span>
        </div>
      </div>
    </motion.div>
  );
}