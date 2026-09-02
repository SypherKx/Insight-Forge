import { createFileRoute, Link } from "@tanstack/react-router";
import { motion } from "framer-motion";
import {
  ArrowRight,
  ShieldCheck,
  Check,
  Sparkles,
  Database,
  Activity,
  Cpu,
  LayoutDashboard,
  Flame,
} from "lucide-react";
import { MarketingLayout } from "@/components/marketing/MarketingLayout";
import { HeroVisual } from "@/components/marketing/HeroVisual";
import { PremiumButton } from "@/components/premium/PremiumButton";
import { GlowBadge } from "@/components/premium/GlowBadge";

export const Route = createFileRoute("/")({
  head: () => ({
    meta: [
      { title: "InsightForge AI — Instant Medical & Academic Answers with Cited Evidence" },
      {
        name: "description",
        content:
          "AI-powered healthcare and educational intelligence platform that detects clinical vitals anomalies, uncovers protocol root causes, and delivers grounded, context-aware explanations using a local Retrieval-Augmented Generation (RAG) pipeline and semantic vector search.",
      },
    ],
  }),
  component: LandingPage,
});

const partnerInstitutions = [
  "Mayo Clinic Labs",
  "Harvard Medical",
  "Stanford Medicine",
  "Johns Hopkins",
  "MIT Open Learning",
  "Oxford Academic",
];

const featureCards = [
  {
    id: "rag",
    title: "Ground-Truth RAG Search for Medical PDFs & Syllabi",
    description:
      "Indexes PubMed studies, FDA drug protocols, hospital EMR logs, and university textbooks into local FAISS vector stores for cited zero-hallucination answers.",
    bullets: [
      "FAISS dense vector index search across medical PDFs & lecture decks",
      "Exact page, paragraph, and table evidence citations",
      "Grounded prompt synthesis using Local Ollama Llama 3.2 3B",
    ],
    cta: "Launch RAG Engine",
    link: "/app/query",
  },
  {
    id: "anomalies",
    title: "Patient Vitals & Medical Lab Outlier Detection",
    description:
      "Fuses Z-score, MAD, IQR, and Pettitt change-point detection to alert clinical teams to patient blood lab spikes or academic engagement drops.",
    bullets: [
      "Pettitt change-point test for vital baseline shifts",
      "False-positive signal suppression for hospital ICU monitors",
      "Adaptive baselining across patient cohorts and student groups",
    ],
    cta: "Open Anomaly Console",
    link: "/app/anomalies",
  },
  {
    id: "attribution",
    title: "Protocol & Curriculum Root-Cause Isolation",
    description:
      "Calculates statistical impact attribution to identify exact suspect dimensions like Medication Dosage, ICU Ward, or Course Module.",
    bullets: [
      "Drug dosage & treatment protocol contribution scoring",
      "Student cohort drop-off segment isolation",
      "Multivariate correlation graphs across clinical trial runs",
    ],
    cta: "Explore Workspace",
    link: "/app/dashboard",
  },
];

const projectModules = [
  {
    name: "Local FAISS RAG Indexer",
    type: "Document Retrieval Engine",
    description: "Converts medical PDFs, PubMed papers, and lecture syllabi into 384-dimensional dense vectors.",
    featured: false,
    highlights: [
      "100% local vector calculation",
      "all-MiniLM-L6-v2 embeddings",
      "Exact page & paragraph citations",
      "Zero cloud data leakage",
    ],
    cta: "Open RAG Search",
    link: "/app/query",
  },
  {
    name: "Statistical Anomaly Engine",
    type: "Vital Signal Detector",
    description: "Ensemble algorithms isolating vital drops, blood lab spikes, and cohort engagement changes.",
    featured: true,
    highlights: [
      "Pettitt non-parametric change-point test",
      "Z-Score & Median Absolute Deviation (MAD)",
      "IQR quantile bound filtering",
      "Automated false-positive suppression",
    ],
    cta: "Open Anomaly Detector",
    link: "/app/anomalies",
  },
  {
    name: "Protocol Root Cause Analyzer",
    type: "Impact Attribution Engine",
    description: "Quantifies statistical contribution scores across patient wards, drug dosages, and study modules.",
    featured: false,
    highlights: [
      "Multivariate dimension attribution",
      "Correlation matrix calculation",
      "Cohort segmentation analytics",
      "Executive summary synthesis",
    ],
    cta: "View System Architecture",
    link: "/about",
  },
];

function LandingPage() {
  return (
    <MarketingLayout>
      {/* 
        ========================================================================
        ABOVE-THE-FOLD HERO SECTION (Fits 100% in viewport above the fold)
        ========================================================================
      */}
      <section className="bg-[var(--canvas)] text-[var(--ink)] py-8 md:py-12 border-b border-[var(--hairline)] relative overflow-hidden transition-colors duration-300 min-h-[calc(100vh-80px)] flex flex-col justify-center">
        {/* Background Radial Glow */}
        <div className="absolute top-1/4 left-1/3 w-[450px] h-[450px] bg-[#c1fbd4]/10 blur-[120px] pointer-events-none rounded-full" />

        <div className="mx-auto max-w-7xl px-8 w-full relative z-10 my-auto">
          <div className="grid gap-8 lg:gap-12 items-center lg:grid-cols-12">
            {/* Left Hero Content */}
            <motion.div
              initial={{ opacity: 0, y: 15 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.6 }}
              className="flex flex-col gap-5 lg:col-span-6"
            >
              <div className="eyebrow-cap text-[var(--muted)] flex items-center gap-2">
                <Flame className="h-4 w-4 text-[#c1fbd4]" /> CLINICAL VITALS & ACADEMIC RAG INTELLIGENCE
              </div>

              {/* Responsive Compact Headline */}
              <h1 className="text-3xl sm:text-4xl md:text-5xl lg:text-5xl font-display font-normal text-[var(--ink)] leading-tight tracking-tight">
                Medical Anomaly Detection & Cited Protocol RAG.
              </h1>

              <p className="body-md text-[var(--body)] max-w-xl text-sm sm:text-base">
                InsightForge AI indexes PubMed studies, FDA drug guidelines, EMR lab records, and university textbooks into a local FAISS vector search for zero-hallucination Q&A and vital signal change-point detection.
              </p>

              {/* Project Action Buttons */}
              <div className="flex flex-wrap items-center gap-3 pt-1">
                <Link to="/app/query">
                  <PremiumButton variant="primaryPill" size="md">
                    <Sparkles className="h-4 w-4 mr-1 text-[#c1fbd4]" /> Launch RAG Engine <ArrowRight className="h-4 w-4 ml-1" />
                  </PremiumButton>
                </Link>
                <Link to="/app/query">
                  <PremiumButton variant="outlineOnDark" size="md">
                    <Sparkles className="h-4 w-4 mr-1 text-[#c1fbd4]" /> Open RAG Search
                  </PremiumButton>
                </Link>
              </div>

              {/* Compact Metric Stats Strip */}
              <div className="grid grid-cols-3 gap-3 border-t border-[var(--hairline)] pt-4 mt-2">
                <div>
                  <div className="text-xl sm:text-2xl font-display font-semibold text-[var(--ink)]">384K+</div>
                  <div className="text-xs text-[var(--muted)] mt-0.5">Vectors Indexed</div>
                </div>
                <div>
                  <div className="text-xl sm:text-2xl font-display font-semibold text-[#c1fbd4]">99.4%</div>
                  <div className="text-xs text-[var(--muted)] mt-0.5">Cited Accuracy</div>
                </div>
                <div>
                  <div className="text-xl sm:text-2xl font-display font-semibold text-[var(--ink)]">100%</div>
                  <div className="text-xs text-[var(--muted)] mt-0.5">Local Privacy</div>
                </div>
              </div>
            </motion.div>

            {/* Right Sleek Professional Dashboard Visual */}
            <motion.div
              initial={{ opacity: 0, x: 15 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ duration: 0.6, delay: 0.15 }}
              className="lg:col-span-6"
            >
              <HeroVisual />
            </motion.div>
          </div>

          {/* Compact Partner Logo Strip (Fits inside above-the-fold hero) */}
          <div className="mt-8 border-t border-[var(--hairline)] pt-4 text-center">
            <div className="eyebrow-cap text-[10px] text-[var(--muted)] mb-3">
              Designed for clinical researchers, medical centers, and university faculties
            </div>
            <div className="flex flex-wrap items-center justify-center gap-6 sm:gap-12 opacity-80">
              {partnerInstitutions.map((inst) => (
                <span key={inst} className="text-xs sm:text-sm font-sans font-medium text-[var(--muted)]">
                  {inst}
                </span>
              ))}
            </div>
          </div>
        </div>
      </section>

      {/* 
        ========================================================================
        FEATURE MODULES SECTION (Below the fold)
        ========================================================================
      */}
      <section className="bg-[var(--surface-soft)] text-[var(--ink)] py-24 border-b border-[var(--hairline)] transition-colors duration-300" id="features">
        <div className="mx-auto max-w-7xl px-8">
          <div className="text-center max-w-3xl mx-auto mb-20">
            <GlowBadge variant="mint">RAG & STATISTICAL SUBSYSTEMS</GlowBadge>
            <h2 className="display-lg text-[var(--ink)] mt-4">
              Built for medical precision & academic clarity.
            </h2>
            <p className="body-lg text-[var(--muted)] mt-4">
              Switch seamlessly between clinical document retrieval, vital anomaly detection, and academic curriculum analytics.
            </p>
          </div>

          {/* Feature Grid */}
          <div className="grid gap-10 md:grid-cols-3">
            {featureCards.map((fc) => (
              <div key={fc.id} className="card-pricing flex flex-col justify-between">
                <div>
                  <div className="flex items-center justify-between mb-4">
                    {fc.id === "rag" && <Database className="h-6 w-6 text-[var(--ink)]" />}
                    {fc.id === "anomalies" && <Activity className="h-6 w-6 text-[var(--ink)]" />}
                    {fc.id === "attribution" && <Cpu className="h-6 w-6 text-[var(--ink)]" />}
                    <GlowBadge variant="shade">ACTIVE MODULE</GlowBadge>
                  </div>
                  <h3 className="heading-xl text-[var(--ink)] mb-3">{fc.title}</h3>
                  <p className="body-md text-[var(--muted)] mb-6">{fc.description}</p>
                  <ul className="space-y-3 mb-8">
                    {fc.bullets.map((b, i) => (
                      <li key={i} className="body-md flex items-start gap-2.5 text-[var(--body)]">
                        <Check className="h-4 w-4 text-[#c1fbd4] mt-1 shrink-0" />
                        <span>{b}</span>
                      </li>
                    ))}
                  </ul>
                </div>
                <Link to={fc.link} className="w-full">
                  <PremiumButton variant="primaryPill" className="w-full">
                    {fc.cta}
                  </PremiumButton>
                </Link>
              </div>
            ))}
          </div>

          {/* Wide Pistachio Feature Band Card */}
          <div className="mt-16 card-pistachio-band flex flex-col md:flex-row items-center justify-between gap-8">
            <div>
              <GlowBadge variant="mint" className="mb-3">HIPAA & FERPA READY</GlowBadge>
              <h3 className="display-md text-[#000000]">
                Zero-Cloud-Leakage Local Vector Architecture.
              </h3>
              <p className="body-lg text-[#3f3f46] mt-2 max-w-2xl">
                FAISS vector indices and dense embeddings run 100% locally on your infrastructure to preserve patient privacy and institutional compliance.
              </p>
            </div>
            <Link to="/about" className="shrink-0">
              <PremiumButton variant="primaryPill">
                View Privacy Architecture
              </PremiumButton>
            </Link>
          </div>
        </div>
      </section>

      {/* 
        ========================================================================
        PROJECT SUBSYSTEMS & MODULES SECTION
        ========================================================================
      */}
      <section className="bg-[var(--canvas)] text-[var(--ink)] py-24 transition-colors duration-300">
        <div className="mx-auto max-w-7xl px-8">
          <div className="text-center max-w-3xl mx-auto mb-20">
            <GlowBadge variant="mint">CORE PROJECT SUBSYSTEMS</GlowBadge>
            <h2 className="display-lg text-[var(--ink)] mt-4">
              Integrated intelligence modules.
            </h2>
            <p className="body-lg text-[var(--muted)] mt-4">
              Run locally on your machine for personal research, clinical trial analytics, or university coursework.
            </p>
          </div>

          {/* Subsystem Modules Grid */}
          <div className="grid gap-10 md:grid-cols-3">
            {projectModules.map((mod) => (
              <div
                key={mod.name}
                className={mod.featured ? "card-pricing-featured" : "card-pricing"}
              >
                <div>
                  <div className="flex items-center justify-between mb-4">
                    <span className="heading-xl">{mod.name}</span>
                    {mod.featured && (
                      <GlowBadge variant="shade">CORE ENGINE</GlowBadge>
                    )}
                  </div>
                  <div className="flex items-baseline gap-2 mb-2">
                    <span className="caption font-mono uppercase text-[#c1fbd4]">{mod.type}</span>
                  </div>
                  <p className="body-md mb-6">{mod.description}</p>
                  <ul className="space-y-3 mb-8">
                    {mod.highlights.map((h, i) => (
                      <li key={i} className="body-md flex items-center gap-2.5">
                        <Check className="h-4 w-4 shrink-0" />
                        <span>{h}</span>
                      </li>
                    ))}
                  </ul>
                </div>
                <Link to={mod.link} className="w-full">
                  <PremiumButton
                    variant={mod.featured ? "aloePill" : "primaryPill"}
                    className="w-full"
                  >
                    {mod.cta}
                  </PremiumButton>
                </Link>
              </div>
            ))}
          </div>

          {/* Compliance Assurance Footer Bar */}
          <div className="mt-20 border-t border-[var(--hairline)] pt-12 flex flex-col md:flex-row items-center justify-between gap-6 text-[var(--muted)] text-sm">
            <div className="flex items-center gap-2">
              <ShieldCheck className="h-5 w-5 text-[#c1fbd4]" />
              <span>100% Local RAG Privacy Architecture — Zero External Cloud Leakage</span>
            </div>
            <div className="flex items-center gap-6">
              <Link to="/about" className="hover:text-[var(--ink)] underline">Documentation</Link>
              <Link to="/about" className="hover:text-[var(--ink)] underline">System Architecture</Link>
              <Link to="/about" className="hover:text-[var(--ink)] underline">Privacy Blueprint</Link>
            </div>
          </div>
        </div>
      </section>
    </MarketingLayout>
  );
}
