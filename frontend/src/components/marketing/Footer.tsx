import { Link } from "@tanstack/react-router";
import { Sparkles } from "lucide-react";

export function Footer() {
  return (
    <footer className="bg-[var(--surface-dark)] text-[var(--on-dark)] border-t border-white/10 py-16 transition-colors duration-300">
      <div className="mx-auto max-w-7xl px-6">
        {/* Custom Brand Logo */}
        <div className="flex items-center gap-2.5 mb-12">
          <div className="flex h-7 w-7 items-center justify-center rounded-md bg-[var(--primary)] text-white font-bold">
            <Sparkles className="h-4 w-4" />
          </div>
          <span className="text-xl font-serif font-medium tracking-tight text-[var(--on-dark)]">
            InsightForge <span className="font-sans text-xs text-[var(--primary)] uppercase font-semibold">AI</span>
          </span>
        </div>

        {/* 4-Column Directory Grid */}
        <div className="grid gap-12 md:grid-cols-4">
          <div className="flex flex-col gap-3 text-sm">
            <div className="caption-uppercase text-[var(--on-dark-soft)] mb-1">Product</div>
            <Link to="/app/anomalies" className="text-[var(--on-dark-soft)] hover:text-[var(--on-dark)] transition">
              Clinical Anomaly Engine
            </Link>
            <Link to="/app/query" className="text-[var(--on-dark-soft)] hover:text-[var(--on-dark)] transition">
              PubMed & Textbook RAG
            </Link>
            <Link to="/app/dashboard" className="text-[var(--on-dark-soft)] hover:text-[var(--on-dark)] transition">
              Protocol Attribution
            </Link>
            <Link to="/app/upload" className="text-[var(--on-dark-soft)] hover:text-[var(--on-dark)] transition">
              Medical PDF Ingestion
            </Link>
          </div>

          <div className="flex flex-col gap-3 text-sm">
            <div className="caption-uppercase text-[var(--on-dark-soft)] mb-1">Solutions</div>
            <Link to="/features" className="text-[var(--on-dark-soft)] hover:text-[var(--on-dark)] transition">
              Hospital Wards & ICUs
            </Link>
            <Link to="/features" className="text-[var(--on-dark-soft)] hover:text-[var(--on-dark)] transition">
              Medical Research Labs
            </Link>
            <Link to="/about" className="text-[var(--on-dark-soft)] hover:text-[var(--on-dark)] transition">
              University Faculties
            </Link>
            <a href="#pricing" className="text-[var(--on-dark-soft)] hover:text-[var(--on-dark)] transition">
              Commercial Plans
            </a>
          </div>

          <div className="flex flex-col gap-3 text-sm">
            <div className="caption-uppercase text-[var(--on-dark-soft)] mb-1">Research & Privacy</div>
            <a href="#" className="text-[var(--on-dark-soft)] hover:text-[var(--on-dark)] transition">
              FAISS Vector Benchmarks
            </a>
            <a href="#" className="text-[var(--on-dark-soft)] hover:text-[var(--on-dark)] transition">
              HIPAA & FERPA Compliance
            </a>
            <a href="#" className="text-[var(--on-dark-soft)] hover:text-[var(--on-dark)] transition">
              Model Safety Cards
            </a>
            <a href="#" className="text-[var(--on-dark-soft)] hover:text-[var(--on-dark)] transition">
              Documentation
            </a>
          </div>

          <div className="flex flex-col gap-3 text-sm">
            <div className="caption-uppercase text-[var(--on-dark-soft)] mb-1">Company</div>
            <Link to="/about" className="text-[var(--on-dark-soft)] hover:text-[var(--on-dark)] transition">
              About InsightForge
            </Link>
            <a href="#" className="text-[var(--on-dark-soft)] hover:text-[var(--on-dark)] transition">
              Careers
            </a>
            <a href="#" className="text-[var(--on-dark-soft)] hover:text-[var(--on-dark)] transition">
              Privacy Policy
            </a>
            <a href="#" className="text-[var(--on-dark-soft)] hover:text-[var(--on-dark)] transition">
              Terms of Service
            </a>
          </div>
        </div>

        {/* Copyright Footer Line */}
        <div className="mt-16 border-t border-white/10 pt-8 flex flex-col md:flex-row md:items-center justify-between text-xs text-[var(--on-dark-soft)]">
          <div>© {new Date().getFullYear()} InsightForge AI Inc. All rights reserved.</div>
          <div className="mt-2 md:mt-0">Clinical & Academic Retrieval-Augmented Generation Platform</div>
        </div>
      </div>
    </footer>
  );
}