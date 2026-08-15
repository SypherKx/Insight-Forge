---
tags:
  - #hub
  - #rag
---
# 🩵 02 RAG Pipeline Subsystem Hub

> **Master Hub**: [[00_Master_Hub]] | **Architecture**: [[01_System_Architecture]]

---

## 🎯 Core RAG Pipeline Modules

- [[files/src_rag_pipeline_py]] — Central RAG Orchestrator (`RAGPipeline`).
- [[files/src_rag_ingestion_py]] — PDF/CSV/MD File Ingester.
- [[files/src_rag_chunker_py]] — Text Chunking engine (500 chars, 50 overlap).
- [[files/src_rag_embeddings_py]] — Dense Vector Generator (`all-MiniLM-L6-v2`).
- [[files/src_rag_vectorstore_py]] — FAISS CPU Vector Index (`IndexFlatIP`).
- [[files/src_rag_retriever_py]] — Top-K Context Retriever.
- [[files/src_rag_models_py]] — Dataclasses for Document & Chunk objects.

---

## ⚡ Data Flow Connections
- Connected Backend Routers: [[files/backend_routers_rag_py]] & [[files/backend_services_rag_service_py]]
