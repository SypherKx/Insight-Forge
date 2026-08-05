import { createFileRoute, Link } from "@tanstack/react-router";
import { Database, Cpu, GitBranch, Brain, ArrowRight, Check, Stethoscope, BookOpen } from "lucide-react";
import { MarketingLayout } from "@/components/marketing/MarketingLayout";
import { Eyebrow, SectionHeading } from "@/components/premium/SectionHeading";
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
    icon: Brain,
    product: "CLINICAL & ACADEMIC VAULT RAG",
    eyebrow: "RETRIEVAL-AUGMENTED GENERATION",
    title: "Ground-Truth RAG Search for Medical PDFs & Syllabi",
    body: "Indexes PubMed studies, FDA drug labels, hospital EMR records, and university textbooks into local FAISS vector spaces for cited zero-hallucination answers.",
    bullets: [
      "FAISS dense vector index search across medical PDFs & lecture decks",
      "Page, paragraph, and table evidence citations",
      "Grounded prompt synthesis using Groq Llama 3.3 70B",
      "100% local index disk persistence for data privacy",
    ],
  },
  {
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
  },
  {
    icon: GitBranch,
    product: "WAYPOINT PROTOCOL ATTRIBUTION",
    eyebrow: "ROOT CAUSE ANALYSIS",
    title: "Dimensional Root-Cause Attribution for Medical Events",
    body: "Calculates impact attribution to pinpoint exact suspect dimensions like Medication Dosage, ICU Ward, or Course Module.",
    bullets: [
      "Drug dosage & treatment protocol contribution scoring",
      "Student cohort drop-off segment isolation",
      "Multivariate correlation graphs across clinical trial runs",
      "Interactive drill-down diagnostics",
    ],
  },
  {
    icon: Database,
    product: "NOMAD MEDICAL INGESTION",
    eyebrow: "HIPAA & FERPA READY PIPELINE",
    title: "Schema-Aware Ingestion for Medical Records & Academic Docs",
    body: "Upload EMR CSV files, lab results, PubMed PDFs, or lecture slide decks. Schema inference and data cleanups execute automatically.",
    bullets: [
      "Automatic schema detection for patient lab CSVs & medical records",
      "PDF text chunking windowing for research papers & textbooks",
      "Outlier-resilient numeric cleaning for clinical trial datasets",
      "Air-gapped local processing options",
    ],
  },
];

function FeaturesPage() {
  return (
    <MarketingLayout>
      {/* PAGE HEADER */}
      <section className="bg-[var(--canvas)] section-rhythm border-b border-[var(--hairline)] transition-colors duration-300">
        <div className="mx-auto max-w-5xl px-6 text-center">
          <Eyebrow className="justify-center">HEALTHCARE & EDUCATION RAG ARCHITECTURE</Eyebrow>
          <h1 className="display-lg text-[var(--ink)] mt-4 font-normal">
            Engineered for medical precision & academic clarity.
          </h1>
          <p className="body-md text-[var(--body)] max-w-2xl mx-auto mt-4">
            Four specialized modules built to accelerate medical research, assist clinical decision-making, and streamline academic document search.
          </p>
        </div>
      </section>

      {/* DETAILED MODULE SECTIONS */}
      <section className="bg-[var(--canvas)] section-rhythm border-b border-[var(--hairline)] transition-colors duration-300">
        <div className="mx-auto max-w-7xl px-6 flex flex-col gap-20">
          {capabilities.map((c, i) => {
            const Icon = c.icon;
            const isReverse = i % 2 === 1;

            return (
              <div
                key={c.title}
                className={`grid gap-12 items-center md:grid-cols-2 ${
                  isReverse ? "md:[&>*:first-child]:order-2" : ""
                }`}
              >
                <div>
                  <div className="flex items-center gap-2">
                    <span className="caption uppercase font-semibold text-[var(--primary)]">{c.product}</span>
                  </div>
                  <h2 className="display-md text-[var(--ink)] mt-3 font-normal">{c.title}</h2>
                  <p className="body-md text-[var(--body)] mt-4">{c.body}</p>

                  <ul className="mt-6 grid gap-3">
                    {c.bullets.map((b) => (
                      <li key={b} className="flex items-center gap-3 body-md text-[var(--body-strong)]">
                        <Check className="h-4 w-4 text-[var(--success)] shrink-0" />
                        <span>{b}</span>
                      </li>
                    ))}
                  </ul>
                </div>

                <div className="bg-[var(--surface-soft)] border border-[var(--hairline)] rounded-xl p-8 flex flex-col justify-between min-h-[280px] shadow-sm transition-colors duration-300">
                  <div className="flex items-center justify-between border-b border-[var(--hairline)] pb-4">
                    <span className="caption font-semibold text-[var(--ink)]">{c.product}</span>
                    <Icon className="h-5 w-5 text-[var(--primary)]" />
                  </div>
                  <div className="my-8 flex items-center justify-center">
                    <div className="flex h-20 w-20 items-center justify-center rounded-xl bg-[var(--surface-card)] border border-[var(--hairline)] shadow-sm">
                      <Icon className="h-10 w-10 text-[var(--primary)]" />
                    </div>
                  </div>
                  <div className="flex items-center justify-between text-xs text-[var(--muted)] font-mono">
                    <span>FAISS INDEX: ACTIVE</span>
                    <span className="text-[var(--success)] font-semibold">● READY</span>
                  </div>
                </div>
              </div>
            );
          })}
        </div>
      </section>

      {/* CTA BANNER */}
      <section className="bg-[var(--canvas)] section-rhythm transition-colors duration-300">
        <div className="mx-auto max-w-5xl px-6 text-center">
          <div className="bg-[var(--surface-card)] border border-[var(--hairline)] rounded-2xl p-12 shadow-md">
            <SectionHeading
              align="center"
              eyebrow="GET STARTED WITH HEALTHCARE RAG"
              title="Test the RAG platform with your clinical data."
              description="Upload a medical PDF or clinical dataset to explore cited document search."
            />
            <div className="mt-8 flex justify-center gap-4">
              <Link to="/app/upload">
                <PremiumButton variant="primary" size="lg">
                  Upload Medical Document <ArrowRight className="ml-2 h-4 w-4" />
                </PremiumButton>
              </Link>
            </div>
          </div>
        </div>
      </section>
    </MarketingLayout>
  );
}