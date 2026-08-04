import { createFileRoute, Link } from "@tanstack/react-router";
import { useState } from "react";
import { motion } from "framer-motion";
import {
  ArrowRight,
  Brain,
  Database,
  ShieldCheck,
  Activity,
  Cpu,
  GitBranch,
  Search,
  Check,
  Zap,
  Sparkles,
  Stethoscope,
  BookOpen,
  ArrowDown,
} from "lucide-react";
import { MarketingLayout } from "@/components/marketing/MarketingLayout";
import { HeroVisual } from "@/components/marketing/HeroVisual";
import { PremiumButton } from "@/components/premium/PremiumButton";

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
      "Grounded prompt synthesis using Groq Llama 3.3 70B",
    ],
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
  },
];

const pricingTiers = [
  {
    name: "Academic Researcher",
    price: "$0",
    period: "free local edition",
    description: "For individual medical researchers, students, and professors.",
    featured: false,
    features: [
      "100% local FAISS RAG index",
      "Up to 100K rows of lab data per CSV",
      "PubMed paper & textbook PDF search",
      "Basic Z-score & IQR detectors",
    ],
    cta: "Start Free Research",
    link: "/app/upload",
  },
  {
    name: "Clinical Department",
    price: "$99",
    period: "per seat / month",
    description: "For hospital wards, clinical trial teams, and university faculties.",
    featured: true,
    features: [
      "Everything in Academic",
      "Multi-algorithm vital anomaly engine",
      "Dimensional protocol root-cause attribution",
      "HIPAA / FERPA ready privacy architecture",
      "Groq & Llama 3.3 medical LLM synthesis",
    ],
    cta: "Try Clinical Edition",
    link: "/app/upload",
  },
  {
    name: "Hospital Network",
    price: "Custom",
    period: "enterprise SLA",
    description: "For hospital networks, EMR integrations, and medical schools.",
    featured: false,
    features: [
      "Air-gapped on-premise FAISS RAG pipelines",
      "BYOK encryption & BAA compliance audit",
      "Custom clinical protocol detector plugins",
      "24/7 medical SLA & dedicated engineer",
    ],
    cta: "Contact Clinical Sales",
    link: "/about",
  },
];

function LandingPage() {
  return (
    <MarketingLayout>
      {/* 1. STUNNING IMPRESSIVE HERO SECTION */}
      <section className="bg-[var(--canvas)] section-rhythm border-b border-[var(--hairline)] transition-colors duration-300 relative overflow-hidden">
        <div className="mx-auto max-w-7xl px-6">
          <div className="grid gap-12 items-center md:grid-cols-12">
            {/* Left Hero Content */}
            <motion.div
              initial={{ opacity: 0, x: -30 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ duration: 0.8, ease: [0.22, 1, 0.36, 1] }}
              className="flex flex-col gap-6 md:col-span-6"
            >
              <div className="inline-flex items-center gap-2 text-xs font-sans font-semibold text-[var(--primary)] tracking-wider">
                <Sparkles className="h-4 w-4" /> HEALTHCARE & EDUCATION RAG INTELLIGENCE
              </div>

              {/* Serif Display Headline */}
              <h1 className="display-xl font-serif text-[var(--ink)]">
                Instant medical answers with cited evidence.
              </h1>

              <p className="body-md text-[var(--body)] max-w-xl text-lg leading-relaxed">
                InsightForge AI indexes PubMed studies, FDA drug guidelines, EMR lab records, and university textbooks into local FAISS vector search for zero-hallucination Q&A.
              </p>

              {/* Action Buttons */}
              <div className="mt-2 flex flex-wrap items-center gap-4">
                <Link to="/app/upload">
                  <PremiumButton variant="primary" size="lg">
                    Try RAG Search Free <ArrowRight className="ml-1.5 h-4 w-4" />
                  </PremiumButton>
                </Link>
                <a href="#features">
                  <button className="button-secondary">
                    Explore Capabilities <ArrowDown className="ml-1.5 h-4 w-4" />
                  </button>
                </a>
              </div>

              {/* Live Metric Stats Strip */}
              <div className="mt-6 grid grid-cols-3 gap-4 border-t border-[var(--hairline)] pt-6 text-center md:text-left">
                <div>
                  <div className="font-serif text-2xl font-normal text-[var(--ink)]">384K+</div>
                  <div className="text-xs text-[var(--muted)] mt-0.5">Vectors Indexed</div>
                </div>
                <div>
                  <div className="font-serif text-2xl font-normal text-[var(--primary)]">99.4%</div>
                  <div className="text-xs text-[var(--muted)] mt-0.5">Cited Accuracy</div>
                </div>
                <div>
                  <div className="font-serif text-2xl font-normal text-[var(--ink)]">100%</div>
                  <div className="text-xs text-[var(--muted)] mt-0.5">Local Privacy</div>
                </div>
              </div>
            </motion.div>

            {/* Right Interactive Visual */}
            <motion.div
              initial={{ opacity: 0, x: 30 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ duration: 0.8, ease: [0.22, 1, 0.36, 1] }}
              className="md:col-span-6"
            >
              <HeroVisual />
            </motion.div>
          </div>

          {/* MONOCHROME LOGO STRIP */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            transition={{ duration: 0.6 }}
            className="mt-20 border-t border-[var(--hairline)] pt-10"
          >
            <div className="caption text-center text-xs uppercase tracking-wider text-[var(--muted)] mb-6">
              Trusted by clinical researchers, medical centers, and academic institutions
            </div>
            <div className="flex flex-wrap items-center justify-center gap-10 md:gap-16 opacity-75">
              {partnerInstitutions.map((inst) => (
                <span key={inst} className="font-serif font-normal text-lg text-[var(--muted)] tracking-tight">
                  {inst}
                </span>
              ))}
            </div>
          </motion.div>
        </div>
      </section>

      {/* 2. LIGHT CREAM FEATURE CARDS (#efe9de) WITH SCROLL ANIMATIONS */}
      <section className="bg-[var(--canvas)] section-rhythm border-b border-[var(--hairline)] transition-colors duration-300" id="features">
        <div className="mx-auto max-w-7xl px-6">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            transition={{ duration: 0.6 }}
            className="text-center max-w-3xl mx-auto mb-16"
          >
            <span className="caption-uppercase">RAG & STATISTICAL MODULES</span>
            <h2 className="display-lg text-[var(--ink)] mt-3">
              Built for medical precision & academic clarity.
            </h2>
            <p className="body-md text-[var(--body)] mt-3">
              Switch between clinical document retrieval, vital anomaly detection, and academic curriculum analytics.
            </p>
          </motion.div>

          <div className="grid gap-8 md:grid-cols-3">
            {featureCards.map((fc, idx) => (
              <motion.div
                key={fc.id}
                initial={{ opacity: 0, y: 30 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true }}
                transition={{ duration: 0.6, delay: idx * 0.15 }}
                className="feature-card flex flex-col justify-between"
              >
                <div>
                  <div className="flex h-8 w-8 items-center justify-center rounded-md bg-[var(--primary)] text-white font-bold mb-4">
                    <Sparkles className="h-4 w-4" />
                  </div>
                  <h3 className="display-sm text-[var(--ink)] font-normal mb-3">{fc.title}</h3>
                  <p className="body-md text-[var(--body)]">{fc.description}</p>

                  <ul className="mt-6 flex flex-col gap-2.5 border-t border-[var(--hairline)] pt-6">
                    {fc.bullets.map((b) => (
                      <li key={b} className="flex items-center gap-2.5 body-sm text-[var(--body-strong)]">
                        <Check className="h-4 w-4 text-[var(--success)] shrink-0" />
                        <span>{b}</span>
                      </li>
                    ))}
                  </ul>
                </div>

                <div className="mt-8">
                  <Link to="/app/query">
                    <span className="text-link text-sm font-semibold inline-flex items-center gap-1">
                      Learn more <ArrowRight className="h-3.5 w-3.5" />
                    </span>
                  </Link>
                </div>
              </motion.div>
            ))}
          </div>
        </div>
      </section>

      {/* 3. DARK NAVY PRODUCT MOCKUP CARD (#181715) */}
      <section className="bg-[var(--canvas)] section-rhythm border-b border-[var(--hairline)] transition-colors duration-300">
        <div className="mx-auto max-w-7xl px-6">
          <motion.div
            initial={{ opacity: 0, scale: 0.97 }}
            whileInView={{ opacity: 1, scale: 1 }}
            viewport={{ once: true }}
            transition={{ duration: 0.7 }}
            className="product-mockup-card-dark grid gap-8 md:grid-cols-12 items-center"
          >
            <div className="md:col-span-6 flex flex-col gap-4">
              <span className="badge-coral">PRODUCT MOCKUP CHROME</span>
              <h2 className="display-lg text-[var(--on-dark)] font-normal">
                See real clinical code & RAG vectors in action.
              </h2>
              <p className="body-md text-[var(--on-dark-soft)]">
                Our local FAISS vector search index runs directly on your disk, delivering exact page and paragraph citations for every medical prompt.
              </p>
              <div className="mt-2">
                <Link to="/app/query">
                  <button className="button-secondary-on-dark">
                    Test RAG Search Engine <ArrowRight className="ml-1 h-4 w-4" />
                  </button>
                </Link>
              </div>
            </div>

            <div className="md:col-span-6 bg-[var(--surface-dark-soft)] border border-white/10 rounded-lg p-6 font-mono text-xs text-[var(--on-dark)] space-y-3">
              <div className="text-[var(--on-dark-soft)]">// FAISS Dense Vector Match Result</div>
              <div><span className="text-[#cc785c]">similarity_score:</span> 0.96</div>
              <div><span className="text-[#cc785c]">document:</span> "PubMed_Article_38291.pdf"</div>
              <div><span className="text-[#cc785c]">citation:</span> Page 14, Paragraph 3</div>
              <div className="pt-2 text-[var(--on-dark-soft)] border-t border-white/10">
                "Combination therapy demonstrated a 42% improvement in 3-year event-free survival rate in pediatric B-cell leukemia patients."
              </div>
            </div>
          </motion.div>
        </div>
      </section>

      {/* 4. FULL-BLEED CORAL CALLOUT CARD (#cc785c) */}
      <section className="bg-[var(--canvas)] section-rhythm border-b border-[var(--hairline)] transition-colors duration-300">
        <div className="mx-auto max-w-7xl px-6">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            transition={{ duration: 0.6 }}
            className="callout-card-coral flex flex-col md:flex-row md:items-center justify-between gap-8"
          >
            <div className="max-w-2xl">
              <span className="text-xs uppercase font-sans font-semibold tracking-wider text-white/80 block mb-2">
                CLINICAL DECISION SUPPORT
              </span>
              <h2 className="display-lg text-white font-normal">
                Empower your medical team with cited RAG AI.
              </h2>
              <p className="body-md text-white/90 mt-3">
                Stop skimming 100-page PDF clinical guidelines manually. Let InsightForge pull precise paragraph evidence instantly.
              </p>
            </div>
            <div>
              <Link to="/app/upload">
                <button className="button-on-coral">
                  Upload Medical PDF <ArrowRight className="ml-1 h-4 w-4" />
                </button>
              </Link>
            </div>
          </motion.div>
        </div>
      </section>

      {/* 5. PRICING GRID */}
      <section className="bg-[var(--canvas)] section-rhythm border-b border-[var(--hairline)] transition-colors duration-300" id="pricing">
        <div className="mx-auto max-w-7xl px-6">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            transition={{ duration: 0.6 }}
            className="text-center max-w-3xl mx-auto mb-16"
          >
            <span className="caption-uppercase">COMMERCIAL PRICING</span>
            <h2 className="display-lg text-[var(--ink)] mt-3">Plans built for research & healthcare.</h2>
            <p className="body-md text-[var(--body)] mt-3">
              Start free for academic research or deploy department-wide clinical decision support.
            </p>
          </motion.div>

          <div className="grid gap-8 md:grid-cols-3">
            {pricingTiers.map((tier, idx) => (
              <motion.div
                key={tier.name}
                initial={{ opacity: 0, y: 30 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true }}
                transition={{ duration: 0.6, delay: idx * 0.15 }}
                className={`rounded-xl p-8 flex flex-col justify-between border ${
                  tier.featured
                    ? "bg-[var(--surface-dark)] text-[var(--on-dark)] border-slate-800 shadow-xl"
                    : "bg-[var(--surface-card)] text-[var(--ink)] border-[var(--hairline)]"
                }`}
              >
                <div>
                  {tier.featured && (
                    <span className="badge-coral mb-4 inline-block">RECOMMENDED CLINICAL TIER</span>
                  )}
                  <h3 className="title-lg font-serif font-normal">{tier.name}</h3>
                  <div className="mt-4 flex items-baseline gap-2">
                    <span className="display-sm font-serif">{tier.price}</span>
                    <span className={`text-xs ${tier.featured ? "text-[var(--on-dark-soft)]" : "text-[var(--muted)]"}`}>
                      {tier.period}
                    </span>
                  </div>
                  <p className={`body-md mt-3 ${tier.featured ? "text-[var(--on-dark-soft)]" : "text-[var(--body)]"}`}>
                    {tier.description}
                  </p>

                  <ul className="mt-6 flex flex-col gap-3 border-t border-hairline/20 pt-6">
                    {tier.features.map((feat) => (
                      <li key={feat} className="flex items-center gap-2.5 text-sm">
                        <Check className="h-4 w-4 text-[var(--success)] shrink-0" />
                        <span>{feat}</span>
                      </li>
                    ))}
                  </ul>
                </div>

                <div className="mt-8">
                  <Link to={tier.link} className="w-full">
                    <button className={tier.featured ? "button-primary w-full" : "button-secondary w-full"}>
                      {tier.cta}
                    </button>
                  </Link>
                </div>
              </motion.div>
            ))}
          </div>
        </div>
      </section>

      {/* 6. DARK NAVY PRE-FOOTER CTA BAND (#181715) */}
      <section className="bg-[var(--canvas)] section-rhythm transition-colors duration-300">
        <div className="mx-auto max-w-7xl px-6">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            transition={{ duration: 0.6 }}
            className="product-mockup-card-dark text-center p-16"
          >
            <div className="flex h-10 w-10 items-center justify-center rounded-md bg-[var(--primary)] text-white font-bold mx-auto mb-4">
              <Sparkles className="h-5 w-5" />
            </div>
            <h2 className="display-lg text-[var(--on-dark)] font-normal">
              Start building with InsightForge Health & Edu RAG.
            </h2>
            <p className="body-md text-[var(--on-dark-soft)] max-w-xl mx-auto mt-4">
              Upload your medical PDFs or clinical datasets and experience cited RAG document intelligence in seconds.
            </p>
            <div className="mt-8 flex justify-center gap-4">
              <Link to="/app/upload">
                <PremiumButton variant="primary" size="lg">
                  Start Free Clinical RAG <ArrowRight className="ml-1 h-4 w-4" />
                </PremiumButton>
              </Link>
            </div>
          </motion.div>
        </div>
      </section>
    </MarketingLayout>
  );
}
