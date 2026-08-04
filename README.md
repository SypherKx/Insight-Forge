# 🛠️ InsightForge AI
> **My First Journey into RAG: Business Anomaly Detection & AI-Powered Explanations**

Hey there! 👋 Welcome to **InsightForge AI**—this is my very first project exploring **RAG (Retrieval-Augmented Generation)**! I built this platform to learn how to connect statistical anomaly detection with LLMs and custom knowledge bases. 

InsightForge AI helps businesses monitor key metrics (revenue, orders, active users) in real time. It automatically detects deviations (anomalies), traces them to their root cause, and uses a custom local RAG pipeline to pull context from business documents (like marketing reports or operations guides) to explain **what** happened and **why** in plain English.

---

## 🧠 Why I Built This & My RAG Learning Journey

Traditional dashboards are great at showing you *what* changed, but they never tell you *why*. When a metric drops, you usually have to dig through internal slack messages, doc files, or incident logs to piece together the context. 

I wanted to solve this by building a system that:
1. Detects anomalies statistically.
2. Automatically searches our internal documentation to find corresponding events (e.g., "AWS Server outage in APAC region" or "Marketing campaign launched").
3. Synthesizes these two sources of information into an actionable summary.

Since this was my first RAG project, my main goal was to understand vector databases, text chunking strategies, and dense embeddings.

---

## 🚀 How I Built the RAG Pipeline

Here is a breakdown of the RAG architecture I implemented in the `src/rag/` folder:

```
┌──────────────────┐      ┌─────────────────┐      ┌────────────────────────┐
│  Upload Context  │ ───> │ Text Chunking   │ ───> │  Dense Embeddings      │
│ (PDF, MD, TXT)   │      │ (Size: 500 chars)│      │  (all-MiniLM-L6-v2)    │
└──────────────────┘      └─────────────────┘      └────────────────────────┘
                                                                │
                                                                ▼
┌──────────────────┐      ┌─────────────────┐      ┌────────────────────────┐
│   FastAPI API    │ <─── │   Groq LLM      │ <─── │  FAISS Vector Index    │
│  Response        │      │ (Llama 3.3 70B) │      │ (IndexFlatIP Search)   │
└──────────────────┘      └─────────────────┘      └────────────────────────┘
```

### 1. Ingestion & Chunking (`ingestion.py` & `chunker.py`)
*   **File Ingestion**: Implemented a parser that supports uploading `.pdf`, `.txt`, and `.md` documents.
*   **Overlapping Chunks**: Used a character-based windowing approach (default: `chunk_size=500` with `overlap=50`). The overlap ensures that sentences or contexts are not chopped in half at chunk boundaries.

### 2. Dense Vector Embeddings (`embeddings.py`)
*   To represent the meaning of text chunks, I used the local **Hugging Face Sentence-Transformers** library.
*   Model: `sentence-transformers/all-MiniLM-L6-v2`. It maps each text chunk into a **384-dimensional dense vector**, which represents its semantic meaning.

### 3. Local Vector Database (`vectorstore.py` & `retriever.py`)
*   **Facebook AI Similarity Search (FAISS)**: Since I wanted to run everything locally without subscribing to a cloud database, I used FAISS (`faiss-cpu`).
*   **Index Flat Inner Product (`IndexFlatIP`)**: I normalized the embedding vectors and used FAISS's Inner Product index to calculate **Cosine Similarity** scores.
*   **Incremental Updates & Save/Load**: Implemented pickle serialization to save the index (`.faiss` and `.meta` files) on disk, allowing index persistence.

### 4. LLM Retrieval & Prompt Synthesis (`pipeline.py`)
*   When an anomaly is selected or a query is asked, the system encodes the query and searches the FAISS index for the top `k` matching text chunks.
*   The retrieved context is inserted into a prompt template alongside the anomaly stats and sent to the **Groq API (Llama 3.3 70B)** to generate a grounded, hallucination-free explanation.

### 💡 Core Things I Learned
*   **Chunking is key**: If chunks are too small, you lose context. If they are too large, the embeddings get diluted and you exceed context limits.
*   **Cosine Similarity**: Normalizing vectors before running an Inner Product search is a highly efficient way to compute similarity.
*   **Persistence**: Balancing in-memory FAISS indices with disk serialization is crucial for building fast local web app search capabilities.

---

## ✨ Features

*   **🔍 Statistical Outlier Detection**: Ensemble algorithms (IQR, Z-score, Pettitt test) automatically find spikes, drops, or behavioral shifts in your data.
*   **📊 Root Cause Analysis**: Quantifies exact driver segments (e.g., *Region: APAC*) using statistical impact attribution.
*   **💬 RAG Knowledge Search**: Drag context files (marketing calendars, release logs) into the RAG pipeline and query them using natural language.
*   **✨ Premium Visual UI**: A state-of-the-art dark-mode interface built with glassmorphism, responsive charts, and fluid micro-animations.

---

## ⚡ Quick Start

Get your local instance running in under 5 minutes.

### Step 1: Install Backend & RAG Dependencies

1. Navigate to the project directory:
   ```bash
   cd "c:\Users\itska\OneDrive\Desktop\insight forge"
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
# Paste your Groq API key here for RAG & Explanations:
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
   bun install   # or npm install
   ```

3. Start the hot-reloading development server:
   ```bash
   bun run dev   # or npm run dev
   ```

4. Open in your browser:
   *   **App UI**: http://localhost:5173

---

## 🛠️ The Tech Stack

### Backend & AI
*   **RAG Engine**: FAISS Index Flat Inner Product, Sentence Transformers (`all-MiniLM-L6-v2`), PyPDF / docx parsing.
*   **FastAPI**: High performance Python backend routing.
*   **Pandas & NumPy**: Core data structure handling and matrix normalization.

### Premium Frontend
*   **React 19 & Vite 7**: The latest runtime and build engine.
*   **TanStack Router**: Type-safe routing for navigating views.
*   **Tailwind CSS 4 & Framer Motion**: Sleek styling and responsive glassmorphic animations.
*   **Recharts**: Modern business analytics visualizations.

---

## 💬 A Message to My Viewers & Fellow Learners

Thanks for checking out my project! As this is my **first time building a Retrieval-Augmented Generation (RAG) system**, I'm incredibly excited about the potential of vector databases and LLM context synthesis. 

If you are also learning RAG or have feedback on how I can optimize my chunking overlaps, FAISS indexing, or retrieval prompt structures, I'd love to connect! Open an issue or drop a line—let's build together! 🚀
