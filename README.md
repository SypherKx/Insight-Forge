# 🛠️ InsightForge AI — Local Retrieval-Augmented Generation (RAG) for Healthcare & Education

> **AI-powered healthcare and educational intelligence platform that detects clinical vitals anomalies, uncovers protocol root causes, and delivers grounded, context-aware explanations using a local Retrieval-Augmented Generation (RAG) pipeline and semantic vector search.**

Welcome to **InsightForge AI**—a production-grade **RAG (Retrieval-Augmented Generation)** platform designed for **Healthcare & Education**! InsightForge AI connects clinical vital anomaly detection and academic metric tracking with local LLMs (Ollama `llama3.2:3b` / Groq) and FAISS vector knowledge bases.

InsightForge AI helps medical clinicians, clinical trialists, researchers, and university faculties monitor key health and academic signals in real time (blood lab test spikes, patient ICU vitals, course completion drop-offs). It automatically detects deviations, traces them to protocol root causes, and uses a local RAG pipeline to pull context from clinical guidelines (FDA drug protocols, PubMed medical research papers, university lecture syllabi) to explain **what** happened and **why** with exact page and paragraph citations.

---

## 📁 Clean Repository Structure

```
Insight-Forge-AI/
├── backend/                  # FastAPI REST API & Storage Engine
│   ├── main.py               # Application entry point & CORS configuration
│   ├── config.py             # App settings (Pydantic BaseSettings)
│   ├── routers/              # Endpoint routes (health, datasets, anomalies, RAG)
│   ├── services/             # Business logic & RAG integration
│   └── storage/              # SQLite DB models & file storage
│
├── frontend/                 # React 19 + Vite 7 Modern Editorial Web App
│   ├── src/                  # App components, TanStack router, services, & styles
│   ├── public/               # Static web assets
│   └── package.json          # Node dependencies
│
├── src/                      # Core AI & Analytical Python Packages
│   ├── detection/            # Statistical anomaly detection (Z-score, IQR, Pettitt test)
│   ├── root_cause/           # Driver dimension quantification & correlation analysis
│   ├── explainer/            # Context synthesis & LLM prompt generators
│   ├── ingestion/            # Document parsing, cleaning, and metadata validation
│   └── rag/                  # FAISS vector store, text chunking, and dense embeddings
│
├── data/                     # Sample datasets and generator scripts
│   ├── sample_data.csv       # Clinical & academic test dataset
│   └── generate_sample.py    # Synthetic dataset generator script
│
├── scripts/                  # Repository utility & verification scripts
│   ├── verify_ingestion.py   # Verification suite for RAG & ingestion pipeline
│   └── generate_obsidian_vault.py # Rebuilds Obsidian architecture knowledge graph
│
├── tests/                    # Pytest test suite (83 unit & integration tests)
│   ├── detection/            # Anomaly detection unit tests
│   └── ingestion/            # Pipeline, cleaner, and validator tests
│
├── docs/                     # System architecture & design documentation
│   └── architecture.md       # Comprehensive technical design doc
│
└── obsidian_vault/           # Interactive Obsidian Knowledge Graph (57 module notes)
```

---

## 🚀 How the RAG Pipeline Works

Here is a breakdown of the RAG architecture implemented in `src/rag/`:

```
┌──────────────────┐      ┌─────────────────┐      ┌────────────────────────┐
│  Upload Context  │ ───> │ Text Chunking   │ ───> │  Dense Embeddings      │
│ (Medical PDF, MD)│      │ (Size: 500 chars)│      │  (all-MiniLM-L6-v2)    │
└──────────────────┘      └─────────────────┘      └────────────────────────┘
                                                                │
                                                                ▼
┌──────────────────┐      ┌─────────────────┐      ┌────────────────────────┐
│   FastAPI API    │ <─── │ Local Ollama /  │ <─── │  FAISS Vector Index    │
│  Response        │      │   Groq LLM      │      │ (IndexFlatIP Search)   │
└──────────────────┘      └─────────────────┘      └────────────────────────┘
```

### 1. Ingestion & Chunking (`src/rag/ingestion.py` & `src/rag/chunker.py`)
* **File Ingestion**: Supports uploading PubMed `.pdf` papers, EMR `.csv` files, `.txt`, and `.md` textbook syllabi.
* **Overlapping Chunks**: Uses a windowing approach (`chunk_size=500` with `overlap=50`) to ensure medical sentences and clinical dosages are never split across boundaries.

### 2. Dense Vector Embeddings (`src/rag/embeddings.py`)
* Uses local **Hugging Face Sentence-Transformers** (`sentence-transformers/all-MiniLM-L6-v2`) to map each clinical text chunk into a **384-dimensional dense vector**.

### 3. Local Vector Database (`src/rag/vectorstore.py` & `src/rag/retriever.py`)
* **Facebook AI Similarity Search (FAISS)**: Runs 100% locally with `faiss-cpu` to ensure HIPAA & FERPA ready data privacy with zero third-party cloud data leakage.
* **Cosine Similarity**: Normalizes embedding vectors and uses FAISS `IndexFlatIP` to calculate relevance scores.

### 4. LLM Retrieval & Prompt Synthesis (`src/rag/pipeline.py` & `backend/services/rag_service.py`)
* Searches the FAISS index for top `k` matching text chunks for any query.
* Inserts retrieved evidence into prompt templates alongside anomaly stats and sends it to **Local Ollama (`llama3.2:3b`)** or **Groq API** to generate cited, grounded explanations.

---

## ✨ Core Features

* **🔍 Statistical Health Signal Detection**: Ensemble algorithms (IQR, Z-score, Pettitt test) automatically isolate vital drops or lab test spikes.
* **📊 Protocol & Curriculum Attribution**: Quantifies exact driver dimensions (e.g., *Medication Dosage: Paxlovid* or *ICU Ward: 4*).
* **💬 Medical RAG Evidence Search**: Search FDA drug labels, PubMed papers, and textbook syllabi using natural language with cited passages.
* **✨ Warm Editorial Interface**: A warm-tinted interface with Light/Dark mode toggling, responsive charts, and smooth scroll animations.

---

## ⚡ Quick Start & Development Guide

### Step 1: Backend Setup

1. **Setup Python Virtual Environment**:
   ```bash
   python -m venv venv
   # On Windows:
   venv\Scripts\activate
   # On macOS/Linux:
   source venv/bin/activate
   ```

2. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Verify Pipeline & Run Tests**:
   ```bash
   python scripts/verify_ingestion.py
   pytest
   ```

4. **Start FastAPI Backend Server**:
   ```bash
   python -m uvicorn backend.main:app --reload --host 127.0.0.1 --port 8000
   ```
   * **API Documentation (Swagger UI)**: `http://127.0.0.1:8000/docs`

---

### Step 2: Frontend Setup

1. **Navigate to `frontend/`**:
   ```bash
   cd frontend
   ```

2. **Install Node Dependencies**:
   ```bash
   npm install
   ```

3. **Start Development Server**:
   ```bash
   npm run dev
   ```
   * **App UI**: `http://localhost:8081`

---

### Step 3: Configure LLM Provider (Ollama or Groq)

Edit `.env` in the root directory:
```env
LLM_PROVIDER=ollama
OLLAMA_BASE_URL=http://localhost:11434
LLM_MODEL=llama3.2:3b
RAG_ENABLED=true

# Optional: Cloud LLM fallback
GROQ_API_KEY=your_groq_api_key_here
```

---

## 🛠️ Tech Stack Overview

### Backend & AI Engine
* **RAG Core**: FAISS (`faiss-cpu`), Sentence Transformers (`all-MiniLM-L6-v2`), PyPDF.
* **LLM Engine**: Local Ollama (`llama3.2:3b`) & Groq API integration.
* **FastAPI**: High performance Python backend framework.
* **Pandas & NumPy**: Core statistical processing and ensemble anomaly detection.

### Frontend Application
* **React 19 & Vite 7**: Modern UI runtime and build engine.
* **TanStack Router**: Type-safe routing for dashboard views.
* **Tailwind CSS 4 & Framer Motion**: Responsive styling and smooth scroll animations.
* **Recharts**: Clinical and academic metric charts.

---

## 💬 Community & Contributions

Contributions, bug reports, and feature requests are welcome! Feel free to open an issue or submit a pull request. 🚀
