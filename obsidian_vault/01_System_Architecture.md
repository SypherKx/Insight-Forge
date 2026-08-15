---
tags:
  - #hub
  - #architecture
---
# 🏛️ 01 System Architecture

> **Master Hub**: [[00_Master_Hub]]

---

## 🔄 End-to-End Subsystem Connections

```mermaid
graph TD
    Client[React Frontend] -->|REST API| Backend[FastAPI Backend]
    
    subgraph RAG System
        Backend --> RAG[RAG Pipeline Orchestrator]
        RAG --> Ingestion[Document Ingestion]
        RAG --> Chunker[Text Chunker]
        RAG --> Embeddings[HuggingFace Embeddings]
        RAG --> FAISS[FAISS Vector Store]
        RAG --> Groq[Groq LLM Client]
    end

    subgraph Anomaly System
        Backend --> Anomaly[Anomaly Detector]
        Anomaly --> Algorithms[Z-Score / MAD / IQR / Pettitt]
        Anomaly --> Scorer[Ensemble Scorer]
        Anomaly --> RootCause[Root Cause Analyzer]
    end

    subgraph Persistence
        Backend --> DB[(SQLite Database)]
        FAISS --> DiskIndex[FAISS Vector Files]
    end
```

---

## 🔗 Direct Links to Subsystem Hubs

- [[02_RAG_Pipeline_Hub]]
- [[03_Statistical_Anomaly_Hub]]
- [[04_Root_Cause_Engine_Hub]]
- [[05_FastAPI_Backend_Hub]]
- [[06_Frontend_App_Hub]]
