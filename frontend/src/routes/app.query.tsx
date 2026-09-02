import { createFileRoute } from "@tanstack/react-router";
import { useState, useEffect, useRef } from "react";
import { motion, AnimatePresence } from "framer-motion";
import {
  Search,
  Sparkles,
  FileText,
  CheckCircle2,
  Upload,
  Cpu,
  Bot,
  HardDrive,
  Trash2,
  Database,
  FileCode,
  Layers,
  AlertCircle,
  FileCheck2,
  BookOpen
} from "lucide-react";
import { PageHeader } from "@/components/dashboard/DashboardShell";
import { GlassCard } from "@/components/premium/GlassCard";
import { GlowBadge } from "@/components/premium/GlowBadge";
import { PremiumButton } from "@/components/premium/PremiumButton";
import { queryRAG, uploadRAGDocuments, getRAGStats, clearRAGKnowledgeBase } from "../services/api";

export const Route = createFileRoute("/app/query")({
  head: () => ({ meta: [{ title: "RAG Document Intelligence & Ollama Q&A — InsightForge" }] }),
  component: QueryPage,
});

const LOCAL_MODEL = "llama3.2:3b";
const LOCAL_MODEL_LABEL = "Llama 3.2 3B — Local Ollama";

const samplePrompts = [
  "Summarize the key points of the uploaded document",
  "What are the main findings and conclusions?",
  "List any action items, protocols, or recommendations",
  "Explain the core terms and concepts described in the text",
];

interface IndexedFile {
  name: string;
  size_bytes: number;
  extension: string;
}

export function QueryPage() {
  const [q, setQ] = useState("");
  const selectedModel = LOCAL_MODEL;
  const [submitted, setSubmitted] = useState("");
  const [results, setResults] = useState<any[]>([]);
  const [aiAnswer, setAiAnswer] = useState<string | null>(null);
  const [usedLlm, setUsedLlm] = useState<boolean>(false);
  const [activeModel, setActiveModel] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const [hasSearched, setHasSearched] = useState(false);

  // Document Knowledge Base State
  const [uploading, setUploading] = useState(false);
  const [uploadStatus, setUploadStatus] = useState<string | null>(null);
  const [indexedFiles, setIndexedFiles] = useState<IndexedFile[]>([]);
  const [totalVectors, setTotalVectors] = useState<number>(0);
  const [isClearing, setIsClearing] = useState(false);
  const [dragActive, setDragActive] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const loadStats = async () => {
    try {
      const stats = await getRAGStats();
      if (stats) {
        setTotalVectors(stats.total_vectors || 0);
        if (stats.files && Array.isArray(stats.files)) {
          setIndexedFiles(stats.files);
        }
      }
    } catch (err) {
      console.log("Could not load stats yet", err);
    }
  };

  useEffect(() => {
    loadStats();
  }, []);

  const handleSearch = async (queryText: string) => {
    if (!queryText || !queryText.trim()) return;
    const cleanQ = queryText.trim();
    setSubmitted(cleanQ);
    setHasSearched(true);
    setLoading(true);
    setAiAnswer(null);
    setUsedLlm(false);

    try {
      const res = await queryRAG(cleanQ, 5, 0.0, LOCAL_MODEL);

      if (res) {
        if (res.answer) {
          setAiAnswer(res.answer);
          setUsedLlm(res.used_llm || false);
          setActiveModel(res.llm_model || selectedModel);
        }

        if (res.results && res.results.length > 0) {
          const mapped = res.results.map((r: any, idx: number) => {
            const meta = r.metadata || {};
            const docName = meta.title || meta.file_name || meta.source || r.document_id || `Document #${idx + 1}`;
            return {
              id: r.chunk_id || `chunk_${idx}`,
              title: docName,
              snippet: r.text || "",
              score: typeof r.score === "number" ? r.score : 0.85,
              source: meta.source || meta.file_name || `Vector Passage [${idx + 1}]`,
              tokenCount: meta.token_count,
            };
          });
          setResults(mapped);
        } else {
          setResults([]);
          if (!res.answer) {
            setAiAnswer("No relevant excerpts found in your uploaded documents for this query. Upload more documents to expand your knowledge base.");
          }
        }
      } else {
        setResults([]);
        setAiAnswer("No response received from RAG service.");
      }
    } catch (err: any) {
      console.error("Query failed:", err);
      setResults([]);
      setAiAnswer("Query failed. Please ensure the backend server is running and files are uploaded.");
    } finally {
      setLoading(false);
    }
  };

  const processFiles = async (files: FileList | File[]) => {
    if (!files || files.length === 0) return;
    const fileArray = Array.from(files);

    setUploading(true);
    setUploadStatus(`Ingesting ${fileArray.length} document(s) & generating FAISS vector embeddings...`);

    try {
      const res = await uploadRAGDocuments(fileArray);
      setUploadStatus(
        `✓ Successfully ingested ${res.documents_ingested} document(s) and created ${res.chunks_created} vector chunks!`
      );
      await loadStats();
    } catch (err: any) {
      setUploadStatus(`Ingestion error: ${err?.message || "Failed to process documents."}`);
    } finally {
      setUploading(false);
    }
  };

  const handleFileUpload = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files) {
      processFiles(e.target.files);
    }
  };

  const handleClear = async () => {
    if (!confirm("Are you sure you want to clear all indexed documents from the vector database?")) return;
    setIsClearing(true);
    try {
      await clearRAGKnowledgeBase();
      setResults([]);
      setAiAnswer(null);
      setSubmitted("");
      setHasSearched(false);
      setUploadStatus("Knowledge base cleared. Upload new documents to start.");
      await loadStats();
    } catch (err) {
      console.error("Clear failed", err);
    } finally {
      setIsClearing(false);
    }
  };

  const formatFileSize = (bytes: number) => {
    if (bytes < 1024) return `${bytes} B`;
    if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
    return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
  };

  return (
    <>
      <PageHeader
        title="Document Intelligence & Local RAG Q&A"
        description="Upload your real PDFs, Text files, Word docs, or CSVs. Ask any questions and synthesize grounded answers with local Ollama models."
      />

      <div className="p-6 md:p-8 space-y-8 bg-[#000000] min-h-screen text-white">
        <div className="mx-auto max-w-4xl space-y-6">

          {/* 1. DOCUMENT KNOWLEDGE BASE & UPLOADER CARD */}
          <GlassCard variant="canvas" className="p-6 border border-white/10 shadow-sm bg-[#0a0a0a] space-y-5">
            <div className="flex flex-col md:flex-row items-start md:items-center justify-between gap-4 border-b border-white/10 pb-4">
              <div className="flex items-center gap-2">
                <Database className="h-5 w-5 text-[#c1fbd4]" />
                <span className="text-base font-semibold text-white">Your Knowledge Base</span>
                <GlowBadge variant="mint">
                  {totalVectors} Vector Chunks
                </GlowBadge>
              </div>

              {indexedFiles.length > 0 && (
                <button
                  onClick={handleClear}
                  disabled={isClearing}
                  className="flex items-center gap-1.5 text-xs text-[#ff6b6b] hover:text-white hover:bg-[#ff6b6b]/20 px-3 py-1.5 rounded-lg border border-[#ff6b6b]/30 transition cursor-pointer"
                  title="Clear all indexed documents"
                >
                  <Trash2 className="h-3.5 w-3.5" />
                  {isClearing ? "Clearing..." : "Clear Knowledge Base"}
                </button>
              )}
            </div>

            {/* LIST OF INDEXED FILES */}
            {indexedFiles.length > 0 ? (
              <div className="space-y-2">
                <div className="text-xs font-semibold text-[#9dabad] uppercase tracking-wider">
                  Currently Indexed Documents ({indexedFiles.length})
                </div>
                <div className="grid grid-cols-1 sm:grid-cols-2 gap-2">
                  {indexedFiles.map((file, idx) => (
                    <div
                      key={idx}
                      className="flex items-center justify-between p-2.5 rounded-lg bg-[#141414] border border-white/10 text-xs"
                    >
                      <div className="flex items-center gap-2 truncate pr-2">
                        <FileCheck2 className="h-4 w-4 text-[#c1fbd4] shrink-0" />
                        <span className="text-[#f4f4f5] font-mono truncate">{file.name}</span>
                      </div>
                      <span className="text-[11px] text-[#9dabad] shrink-0">
                        {formatFileSize(file.size_bytes)}
                      </span>
                    </div>
                  ))}
                </div>
              </div>
            ) : (
              <div className="p-4 rounded-lg bg-[#141414]/60 border border-dashed border-white/15 text-center text-xs text-[#9dabad] space-y-1">
                <BookOpen className="h-6 w-6 text-[#9dabad] mx-auto opacity-70" />
                <div className="font-semibold text-white">No documents uploaded yet</div>
                <div>Upload your files below to build your private vector index.</div>
              </div>
            )}

            {/* DRAG & DROP / FILE UPLOAD AREA */}
            <div
              onDragOver={(e) => {
                e.preventDefault();
                setDragActive(true);
              }}
              onDragLeave={() => setDragActive(false)}
              onDrop={(e) => {
                e.preventDefault();
                setDragActive(false);
                if (e.dataTransfer.files) {
                  processFiles(e.dataTransfer.files);
                }
              }}
              onClick={() => fileInputRef.current?.click()}
              className={`border-2 border-dashed rounded-xl p-6 text-center cursor-pointer transition flex flex-col items-center justify-center gap-2 ${
                dragActive
                  ? "border-[#c1fbd4] bg-[#c1fbd4]/5"
                  : "border-white/20 bg-[#121212] hover:border-[#c1fbd4]/50 hover:bg-[#161616]"
              }`}
            >
              <Upload className="h-6 w-6 text-[#c1fbd4]" />
              <div className="text-sm font-semibold text-white">
                {uploading ? "Ingesting & vectorizing..." : "Click or Drag & Drop Documents to Index"}
              </div>
              <div className="text-xs text-[#9dabad]">
                Supported: PDF (.pdf), Text (.txt), Markdown (.md), Word (.docx), CSV (.csv), JSON (.json)
              </div>
              <input
                ref={fileInputRef}
                type="file"
                accept=".pdf,.txt,.md,.docx,.csv,.json,.log,.rst,.html,.xml"
                multiple
                onChange={handleFileUpload}
                className="hidden"
                disabled={uploading}
              />
            </div>

            {uploadStatus && (
              <div className="text-xs font-mono text-[#c1fbd4] bg-[#c1fbd4]/10 p-3 rounded-lg border border-[#c1fbd4]/20 flex items-center gap-2">
                <CheckCircle2 className="h-4 w-4 shrink-0" />
                <span>{uploadStatus}</span>
              </div>
            )}
          </GlassCard>

          {/* 2. LOCAL OLLAMA MODEL BADGE */}
          <GlassCard variant="canvas" className="p-4 border border-white/10 shadow-sm bg-[#0a0a0a]">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2">
                <Bot className="h-4 w-4 text-[#c1fbd4]" />
                <span className="text-xs font-semibold text-white">Synthesis Model:</span>
              </div>
              <GlowBadge variant="mint">
                <Cpu className="h-3 w-3 mr-1" />
                {LOCAL_MODEL_LABEL}
              </GlowBadge>
            </div>
          </GlassCard>

          {/* 3. SEARCH & QUESTION INPUT */}
          <GlassCard variant="canvas" className="p-6 border border-white/10 shadow-sm bg-[#0a0a0a] space-y-4">
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
                  placeholder="Ask any question about your uploaded documents..."
                  className="w-full rounded-lg border border-white/10 bg-[#141414] pl-12 pr-4 py-3 text-base text-white placeholder:text-[#9dabad] outline-none focus:border-[#c1fbd4]"
                />
              </div>
              <PremiumButton variant="outlineOnDark" size="md" type="submit" disabled={loading || !q.trim()}>
                <Sparkles className="h-4 w-4 mr-1 text-[#c1fbd4]" /> Search & Synthesize
              </PremiumButton>
            </form>

            {/* SAMPLE PROMPTS */}
            <div className="flex flex-wrap items-center gap-2 pt-1">
              <span className="eyebrow-cap text-[#9dabad] mr-1 text-[11px]">SUGGESTIONS:</span>
              {samplePrompts.map((p, idx) => (
                <button
                  key={idx}
                  onClick={() => {
                    setQ(p);
                    handleSearch(p);
                  }}
                  className="text-xs px-3 py-1 rounded-full border border-white/10 bg-[#141414] text-[#e4e4e7] hover:border-[#c1fbd4] hover:text-white transition cursor-pointer"
                >
                  {p}
                </button>
              ))}
            </div>
          </GlassCard>

          {/* 4. RESULTS SECTION */}
          {submitted && (
            <div className="eyebrow-cap text-[#9dabad] flex items-center justify-between">
              <span>Query: <span className="font-semibold text-white">"{submitted}"</span></span>
              <span className="font-mono text-xs text-[#c1fbd4]">Model: {selectedModel}</span>
            </div>
          )}

          {loading ? (
            <div className="p-12 text-center text-[#9dabad] font-mono animate-pulse space-y-3 bg-[#0a0a0a] rounded-xl border border-white/10">
              <Sparkles className="h-7 w-7 text-[#c1fbd4] mx-auto animate-spin" />
              <div className="text-sm text-white">Searching vector index & synthesizing response via Ollama...</div>
              <div className="text-xs text-[#9dabad]">Retrieving cosine similarity matches from your files</div>
            </div>
          ) : (
            <div className="space-y-6">

              {/* AI SYNTHESIZED ANSWER */}
              {aiAnswer && (
                <motion.div
                  initial={{ opacity: 0, y: 15 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ duration: 0.3 }}
                >
                  <GlassCard variant="canvas" className="p-6 border border-[#c1fbd4]/40 shadow-lg bg-[#0d140e] space-y-4">
                    <div className="flex items-center justify-between border-b border-[#c1fbd4]/20 pb-3">
                      <div className="flex items-center gap-2">
                        <Bot className="h-5 w-5 text-[#c1fbd4]" />
                        <span className="text-sm font-semibold text-white">AI Synthesized Answer</span>
                      </div>
                      <GlowBadge variant="mint">
                        <Cpu className="h-3 w-3 mr-1" /> {activeModel || selectedModel}
                      </GlowBadge>
                    </div>

                    <div className="text-sm text-[#f4f4f5] leading-relaxed whitespace-pre-line font-sans">
                      {aiAnswer}
                    </div>

                    <div className="pt-2 flex items-center justify-between text-xs text-[#9dabad] border-t border-[#c1fbd4]/20">
                      <span>Grounded strictly on retrieved context</span>
                      <span className="text-[11px] font-mono text-[#c1fbd4]">
                        {usedLlm ? "✓ Live Ollama Inference" : "FAISS Context Fallback"}
                      </span>
                    </div>
                  </GlassCard>
                </motion.div>
              )}

              {/* RETRIEVED VECTOR PASSAGES (EXACT CITATIONS FROM UPLOADED FILES) */}
              {results.length > 0 && (
                <div className="space-y-4">
                  <div className="eyebrow-cap text-[#9dabad] flex items-center gap-2">
                    <Layers className="h-4 w-4 text-[#c1fbd4]" />
                    <span>Exact Document Citations ({results.length} Matches)</span>
                  </div>

                  {results.map((r, i) => (
                    <motion.div
                      key={r.id || i}
                      initial={{ opacity: 0, y: 15 }}
                      animate={{ opacity: 1, y: 0 }}
                      transition={{ duration: 0.3, delay: i * 0.08 }}
                    >
                      <GlassCard variant="canvas" className="p-6 border border-white/10 shadow-sm bg-[#0a0a0a] space-y-3">
                        <div className="flex items-center justify-between border-b border-white/10 pb-3">
                          <div className="flex items-center gap-2 truncate pr-2">
                            <FileText className="h-4 w-4 text-[#c1fbd4] shrink-0" />
                            <span className="text-sm font-semibold text-white truncate">{r.title}</span>
                          </div>
                          <GlowBadge variant="mint">
                            <CheckCircle2 className="h-3 w-3 mr-1" /> {(r.score * 100).toFixed(1)}% Match
                          </GlowBadge>
                        </div>

                        <p className="body-md text-sm text-[#e4e4e7] leading-relaxed font-sans whitespace-pre-line bg-[#141414] p-3 rounded-lg border border-white/5">
                          "{r.snippet}"
                        </p>

                        <div className="pt-2 flex items-center justify-between text-xs text-[#9dabad] border-t border-white/10">
                          <span className="font-mono text-[11px] truncate max-w-md">{r.source}</span>
                          <span className="text-[11px] font-semibold text-[#c1fbd4] shrink-0">
                            FAISS Vector Chunk #{i + 1}
                          </span>
                        </div>
                      </GlassCard>
                    </motion.div>
                  ))}
                </div>
              )}

              {/* EMPTY SEARCH STATE */}
              {hasSearched && results.length === 0 && !aiAnswer && (
                <div className="p-12 text-center text-[#9dabad] bg-[#0a0a0a] rounded-xl border border-white/10 space-y-3">
                  <AlertCircle className="h-8 w-8 text-[#9dabad] mx-auto opacity-70" />
                  <div className="text-base font-semibold text-white">No Matching Context Found</div>
                  <p className="text-xs max-w-md mx-auto">
                    Try refining your query or upload more documents to your knowledge base above.
                  </p>
                </div>
              )}

            </div>
          )}

        </div>
      </div>
    </>
  );
}