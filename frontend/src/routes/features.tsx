import { createFileRoute, Link } from "@tanstack/react-router";
import { Database, Cpu, GitBranch, Brain, ArrowRight, Check, Stethoscope, ShieldCheck, Sparkles, LayoutDashboard } from "lucide-react";
import { MarketingLayout } from "@/components/marketing/MarketingLayout";
import { GlowBadge } from "@/components/premium/GlowBadge";
import { PremiumButton } from "@/components/premium/PremiumButton";

export const Route = createFileRoute("/features")({
  head: () => ({
    meta: [
      { title: "Capabilities — InsightForge Healthcare & Education RAG" },
      {
        name: "description",
        content:
          "Cited RAG document search, clinical vitals anomaly detection, and protocol attribution for medical & academic teams.",
      },
    ],
  }),
  component: FeaturesPage,
});

const capabilities = [
  {
    id: "rag",
    icon: Brain,
    product: "CLINICAL & ACADEMIC RAG",
    eyebrow: "RETRIEVAL-AUGMENTED GENERATION",
    title: "Ground-Truth RAG Search for Medical PDFs & Syllabi",
    body: "Indexes PubMed studies, FDA drug labels, hospital EMR records, and university textbooks into local FAISS vector spaces for cited zero-hallucination answers.",
    bullets: [
      "FAISS dense vector index search across medical PDFs & lecture decks",
      "Page, paragraph, and table evidence citations",
      "Grounded prompt synthesis using Groq Llama 3.3 70B",
      "100% local index disk persistence for data privacy",
    ],
    metric: "384-D FAISS Vectors",
    status: "Active Engine",
  },
  {
    id: "anomalies",
    icon: Stethoscope,
    product: "VITALS & LAB ANOMALY ENGINE",
    eyebrow: "STATISTICAL DETECTORS",
    title: "Multi-Algorithm Outlier Detection for Vitals & Lab Spikes",
    body: "Fuses Z-score, MAD, IQR, and Pettitt change-point detection to alert clinical teams to patient blood lab spikes or academic engagement drops.",
    bullets: [
      "Pettitt change-point test for vital baseline shifts",
      "False-positive signal suppression tailored for hospital ICU monitors",
      "Adaptive baselining across patient cohorts and student groups",
      "Real-time severity score calibration",
    ],
    metric: "Pettitt Change-Point",
    status: "ICU Monitor Ready",
  },
  {
    id: "attribution",
    icon: GitBranch,
    product: "PROTOCOL ATTRIBUTION",
    eyebrow: "ROOT CAUSE ANALYSIS",
    title: "Dimensional Root-Cause Attribution for Medical Events",
    body: "Calculates impact attribution to pinpoint exact suspect dimensions like Medication Dosage, ICU Ward, or Course Module.",
    bullets: [
      "Drug dosage & treatment protocol contribution scoring",
      "Student cohort drop-off segment isolation",
      "Multivariate correlation graphs across clinical trial runs",
      "Interactive drill-down diagnostics",
    ],
    metric: "Multivariate Impact",
    status: "Statistical Isolation",
  },
  {
    id: "ingestion",
    icon: Database,
    product: "MEDICAL DATA INGESTION",
    eyebrow: "HIPAA & FERPA READY PIPELINE",
    title: "Schema-Aware Ingestion for Medical Records & Academic Docs",
    body: "Upload EMR CSV files, lab results, PubMed PDFs, or lecture slide decks. Schema inference and data cleanups execute automatically.",
    bullets: [
      "Automatic schema detection for patient lab CSVs & medical records",
      "PDF text chunking windowing for research papers & textbooks",
      "Outlier-resilient numeric cleaning for clinical trial datasets",
      "Air-gapped local processing options",
    ],
    metric: "Auto Schema Infer",
    status: "PDF Chunk Windowing",
  },
];

function FeaturesPage() {
  return (
    <MarketingLayout>
      {/* PAGE HEADER HERO */}
      <section className="bg-[var(--canvas)] py-14 md:py-20 border-b border-[var(--hairline)] transition-colors duration-300">
        <div className="mx-auto max-w-4xl px-6 text-center">
          <GlowBadge variant="mint">HEALTHCARE & EDUCATION CAPABILITIES</GlowBadge>
          <h1 className="text-4xl sm:text-5xl font-display font-normal text-[var(--ink)] mt-4 leading-tight">
            Engineered for medical precision & academic clarity.
          </h1>
          <p className="body-lg text-[var(--muted)] max-w-2xl mx-auto mt-4 text-base sm:text-lg">
            Four specialized modules built to accelerate medical research, assist clinical decision-making, and streamline academic document search.
          </p>
        </div>
      </section>

      {/* DETAILED MODULE SECTIONS */}
      <section className="bg-[var(--canvas)] py-16 md:py-24 border-b border-[var(--hairline)] transition-colors duration-300">
        <div className="mx-auto max-w-7xl px-8 flex flex-col gap-24">
          {capabilities.map((c, i) => {
            const Icon = c.icon;
            const isReverse = i % 2 === 1;

            return (
              <div
                key={c.title}
                className={`grid gap-12 items-center lg:grid-cols-12 ${
                  isReverse ? "lg:[&>*:first-child]:order-2" : ""
                }`}
              >
                {/* Text Content */}
                <div className="lg:col-span-7 space-y-4">
                  <div className="flex items-center gap-2">
                    <span className="caption uppercase font-semibold text-[#c1fbd4] tracking-wider">{c.product}</span>
                  </div>
                  <h2 className="text-2xl sm:text-3xl font-display font-normal text-[var(--ink)] leading-snug">{c.title}</h2>
                  <p className="body-md text-[var(--body)] leading-relaxed">{c.body}</p>

                  <ul className="pt-2 grid gap-3">
                    {c.bullets.map((b) => (
                      <li key={b} className="flex items-start gap-3 body-md text-[var(--body-strong)]">
                        <Check className="h-4 w-4 text-[#c1fbd4] mt-1 shrink-0" />
                        <span>{b}</span>
                      </li>
                    ))}
                  </ul>
                </div>

                {/* Subsystem Graphic Card */}
                <div className="lg:col-span-5 bg-[var(--surface-card)] border border-[var(--hairline)] rounded-2xl p-8 flex flex-col justify-between min-h-[300px] shadow-lg transition-colors duration-300">
                  <div className="flex items-center justify-between border-b border-[var(--hairline)] pb-4">
                    <div className="flex items-center gap-2">
                      <Icon className="h-5 w-5 text-[#c1fbd4]" />
                      <span className="heading-sm text-[var(--ink)]">{c.product}</span>
                    </div>
                    <GlowBadge variant="shade">{c.status}</GlowBadge>
                  </div>

                  <div className="my-8 flex flex-col items-center justify-center text-center gap-3">
                    <div className="flex h-16 w-16 items-center justify-center rounded-2xl bg-[var(--surface-soft)] border border-[var(--hairline)] shadow-inner">
                      <Icon className="h-8 w-8 text-[#c1fbd4]" />
                    </div>
                    <div className="text-lg font-mono font-bold text-[var(--ink)]">{c.metric}</div>
                    <div className="text-xs text-[var(--muted)]">Local FAISS Matrix Persistence</div>
                  </div>

                  <div className="flex items-center justify-between text-xs text-[var(--muted)] font-mono pt-3 border-t border-[var(--hairline)]">
                    <span>STATUS: ACTIVE</span>
                    <span className="text-[#c1fbd4] font-semibold flex items-center gap-1">
                      <ShieldCheck className="h-3.5 w-3.5" /> 100% LOCAL PRIVACY
                    </span>
                  </div>
                </div>
              </div>
            );
          })}
        </div>
      </section>

      {/* CALL TO ACTION BANNER */}
      <section className="bg-[var(--surface-soft)] py-16 md:py-20 transition-colors duration-300">
        <div className="mx-auto max-w-4xl px-8 text-center">
          <div className="bg-[var(--surface-card)] border border-[var(--hairline)] rounded-2xl p-10 md:p-14 shadow-xl">
            <GlowBadge variant="mint" className="mb-4">READY TO FORGE INSIGHTS?</GlowBadge>
            <h2 className="text-3xl sm:text-4xl font-display font-normal text-[var(--ink)]">
              Launch the Clinical & Educational Workspace.
            </h2>
            <p className="body-md text-[var(--muted)] max-w-xl mx-auto mt-3">
              Upload your medical PDFs or lab CSV datasets and start querying grounded evidence today.
            </p>
            <div className="mt-8 flex flex-wrap justify-center gap-4">
              <Link to="/app/dashboard">
                <PremiumButton variant="primaryPill" size="lg">
                  <LayoutDashboard className="h-4 w-4 mr-1" /> Launch Workspace <ArrowRight className="ml-1 h-4 w-4" />
                </PremiumButton>
              </Link>
              <Link to="/app/query">
                <PremiumButton variant="outlineOnDark" size="lg">
                  <Sparkles className="h-4 w-4 mr-1 text-[#c1fbd4]" /> Open RAG Search
                </PremiumButton>
              </Link>
            </div>
          </div>
        </div>
      </section>
    </MarketingLayout>
  );
}