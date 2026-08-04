# 🛠️ InsightForge AI — Retrieval-Augmented Generation (RAG) for Healthcare & Education

> **My Journey into RAG: Healthcare & Educational Anomaly Intelligence & Cited Evidence Q&A**

Welcome to **InsightForge AI**—a **RAG (Retrieval-Augmented Generation)** platform designed for **Healthcare & Education**! I built this platform to connect clinical vital anomaly detection and academic metric tracking with LLMs and local vector knowledge bases. 

InsightForge AI helps medical clinicians, clinical trialists, researchers, and university faculties monitor key health and academic signals in real time (blood lab test spikes, patient ICU vitals, course completion drop-offs). It automatically detects deviations, traces them to protocol root causes, and uses a local RAG pipeline to pull context from clinical guidelines (FDA drug protocols, PubMed medical research papers, university lecture syllabi) to explain **what** happened and **why** with exact page and paragraph citations.

---

## 🧠 Why I Built This & My RAG Learning Journey

Traditional medical dashboards show *what* patient vital metric changed, but they don't give you immediate clinical protocol context. When a vital spikes or a trial metric drops, doctors and researchers have to manually search through 100-page PDF clinical guidelines, PubMed literature, or EMR records.

I wanted to solve this by building a system that:
1. Detects clinical and academic anomalies statistically (Z-score, MAD, IQR, Pettitt change-point test).
2. Automatically searches internal medical documentation & textbooks to find corresponding evidence (e.g., "Paxlovid dosage adjustment in renal impairment" or "Pediatric leukemia Phase 3 trial").
3. Synthesizes these two sources of information into a zero-hallucination, cited executive summary.

Since this was my RAG project, my main goal was to master vector databases, text chunking strategies, and dense embeddings for sensitive domain data.

---

## 🚀 How I Built the RAG Pipeline

Here is a breakdown of the RAG architecture implemented in `src/rag/`:

```
┌──────────────────┐      ┌─────────────────┐      ┌────────────────────────┐
│  Upload Context  │ ───> │ Text Chunking   │ ───> │  Dense Embeddings      │
│ (Medical PDF, MD)│      │ (Size: 500 chars)│      │  (all-MiniLM-L6-v2)    │
└──────────────────┘      └─────────────────┘      └────────────────────────┘
                                                                │
                                                                ▼
┌──────────────────┐      ┌─────────────────┐      ┌────────────────────────┐
│   FastAPI API    │ <─── │   Groq LLM      │ <─── │  FAISS Vector Index    │
│  Response        │      │ (Llama 3.3 70B) │      │ (IndexFlatIP Search)   │
└──────────────────┘      └─────────────────┘      └────────────────────────┘
```

### 1. Ingestion & Chunking (`ingestion.py` & `chunker.py`)
*   **File Ingestion**: Supports uploading PubMed `.pdf` papers, EMR `.csv` files, `.txt`, and `.md` textbook syllabi.
*   **Overlapping Chunks**: Uses a windowing approach (`chunk_size=500` with `overlap=50`) to ensure medical sentences and clinical dosages are never split across boundaries.

### 2. Dense Vector Embeddings (`embeddings.py`)
*   Uses local **Hugging Face Sentence-Transformers** (`sentence-transformers/all-MiniLM-L6-v2`) to map each clinical text chunk into a **384-dimensional dense vector**.

### 3. Local Vector Database (`vectorstore.py` & `retriever.py`)
*   **Facebook AI Similarity Search (FAISS)**: Runs 100% locally with `faiss-cpu` to ensure HIPAA & FERPA ready data privacy with zero third-party cloud data leakage.
*   **Cosine Similarity**: Normalizes embedding vectors and uses FAISS `IndexFlatIP` to calculate relevance scores.
*   **Index Persistence**: Disk serialization (`.faiss` and `.meta` files) saves indices to disk.

### 4. LLM Retrieval & Prompt Synthesis (`pipeline.py`)
*   Searches the FAISS index for top `k` matching text chunks for any query.
*   Inserts retrieved evidence into prompt templates alongside anomaly stats and sends it to the **Groq API (Llama 3.3 70B)** to generate cited, grounded explanations.

---

## ✨ Features

*   **🔍 Statistical Health Signal Detection**: Ensemble algorithms (IQR, Z-score, Pettitt test) automatically isolate vital drops or lab test spikes.
*   **📊 Protocol & Curriculum Attribution**: Quantifies exact driver dimensions (e.g., *Medication Dosage: Paxlovid* or *ICU Ward: 4*).
*   **💬 Medical RAG Evidence Search**: Search FDA drug labels, PubMed papers, and textbook syllabi using natural language.
*   **✨ Warm Editorial Interface**: A warm-tinted interface with Light/Dark mode toggling, responsive charts, and smooth scroll animations.

---

## ⚡ Quick Start

### Step 1: Install Backend & RAG Dependencies

1. Navigate to the project directory:
   ```bash
   cd "c:\Users\itska\OneDrive\Desktop\Insight-Forge-master\Insight-Forge-master"
   ```

2. Setup virtual environment:
   ```bash
   python -m venv venv
   # On Windows:
   venv\Scripts\activate
   # On macOS/Linux:
   source venv/bin/activate
   ```

3. Install requirements (includes `faiss-cpu` and `sentence-transformers`):
   ```bash
   pip install -r requirements.txt
   ```

4. Start FastAPI server:
   ```bash
   python -m uvicorn backend.main:app --reload --host 127.0.0.1 --port 8000
   ```
   *   **API Documentation**: http://localhost:8000/docs

---

### Step 2: Configure Environment Variables

Edit/create `.env` in the root directory:
```env
GROQ_API_KEY=your_groq_api_key_here
DATABASE_URL=sqlite:///./insightforge.db
RAG_ENABLED=true
```

---

### Step 3: Run the Frontend Application

1. Open a new terminal tab and enter the `frontend` directory:
   ```bash
   cd frontend
   ```

2. Install dependencies:
   ```bash
   npm install   # or bun install
   ```

3. Start the hot-reloading development server:
   ```bash
   npm run dev
   ```

4. Open in your browser:
   *   **App UI**: http://localhost:8081

---

## 🛠️ The Tech Stack

### Backend & AI
*   **RAG Engine**: FAISS Index Flat Inner Product, Sentence Transformers (`all-MiniLM-L6-v2`), PyPDF.
*   **FastAPI**: High performance Python backend routing.
*   **Pandas & NumPy**: Core statistical data processing.

### Frontend
*   **React 19 & Vite 7**: Modern UI runtime and build engine.
*   **TanStack Router**: Type-safe routing for views.
*   **Tailwind CSS 4 & Framer Motion**: Responsive styling and scroll animations.
*   **Recharts**: Clinical and academic metric charts.

---

## 💬 A Message to Viewers & Fellow Learners

Thanks for checking out my project! As a project exploring **Retrieval-Augmented Generation (RAG) for Healthcare & Education**, I'm incredibly excited about the potential of vector databases and cited LLM synthesis. 

If you are also exploring RAG or have feedback on optimizing FAISS indices, chunking overlaps, or clinical prompt structures, let's connect! Open an issue or drop a line—let me know your thoughts! 🚀
