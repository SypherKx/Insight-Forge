# InsightForge AI - System Architecture

## 1. Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────────────┐
│                              SaaS UI (Frontend)                         │
│                    React/Next.js + TypeScript + Tailwind               │
└──────────────────────────────────┬──────────────────────────────────────┘
                                   │ HTTPS/WebSocket
                                   │
┌─────────────────────────────────────────────────────────────────────────┐
│                          API Gateway / Load Balancer                    │
│                    Rate Limiting, Auth, Routing, Caching               │
└──────────────────────────────────┬──────────────────────────────────────┘
                                   │
        ┌───────────────────────────┼───────────────────────────┐
        │                           │                           │
        ▼                           ▼                           ▼
┌─────────────────┐      ┌─────────────────┐      ┌─────────────────┐
│   Auth Service  │      │  API Services   │      │  WebSocket      │
│   (JWT/OAuth)   │      │  (FastAPI)      │      │  Service        │
└─────────────────┘      └─────────────────┘      └─────────────────┘
                                 │
              ┌──────────────────┼──────────────────┐
              │                  │                  │
              ▼                  ▼                  ▼
    ┌──────────────┐  ┌──────────────┐  ┌──────────────┐
    │ Ingestion    │  │ Detection    │  │ Explanation  │
    │ Service      │  │ Service      │  │ Service      │
    └──────────────┘  └──────────────┘  └──────────────┘
              │                  │                  │
              │         ┌────────┼────────┐         │
              │         │        │        │         │
              ▼         ▼        ▼        ▼         ▼
    ┌─────────────────────────────────────────────────────┐
    │              Message Queue (RabbitMQ/Kafka)        │
    │         For async processing & decoupling          │
    └─────────────────────────────────────────────────────┘
              │                  │                  │
              └──────────────────┼──────────────────┘
                                 │
              ┌──────────────────┼──────────────────┐
              │                  │                  │
              ▼                  ▼                  ▼
    ┌──────────────┐  ┌──────────────┐  ┌──────────────┐
    │ PostgreSQL   │  │   Redis       │  │   Vector      │
    │ (Metadata,   │  │  (Cache,      │  │   Store      │
    │  Results)    │  │   Sessions)   │  │  (Pinecone/  │
    └──────────────┘  └──────────────┘  │   Weaviate)  │
                                          └──────────────┘
              │                  │
              └──────────────────┼──────────────────┘
                                 │
                                 ▼
                    ┌─────────────────────────┐
                    │   Object Storage        │
                    │  (S3/MinIO)             │
                    │  - Raw CSV files        │
                    │  - Exports/Reports      │
                    └─────────────────────────┘

External:
┌─────────────────┐
│   LLM Provider  │
│  (Anthropic     │
│   Claude API)   │
└─────────────────┘
```

**Key Design Principles:**
- **Strict Separation**: Statistical detection (NO LLM) vs Explanation (LLM-only)
- **Async Processing**: Message queue decouples services for scalability
- **Multi-layer Caching**: Redis for frequent queries
- **Stateless Services**: Horizontal scaling capability
- **Clear Service Boundaries**: Each service has single responsibility

---

## 2. Module Breakdown

### 2.1 Ingestion Service
**Responsibilities:**
- CSV file upload and validation
- Schema inference and data type detection
- Data quality checks (missing values, duplicates, outliers in metadata)
- Store raw CSV to object storage
- Create dataset metadata record in PostgreSQL
- Publish "dataset_uploaded" event to message queue

**Interface:**
- `POST /api/v1/datasets/upload`
- `GET /api/v1/datasets/{id}/status`
- `GET /api/v1/datasets` (list with pagination)

**Outputs:**
- Dataset metadata (ID, name, row count, column schema, file path)
- Validation report
- Event: `dataset_uploaded` (dataset_id, storage_path, schema)

---

### 2.2 Detection Service
**Responsibilities:**
- Subscribe to "dataset_uploaded" events
- Load CSV data (chunked for large files)
- Apply statistical anomaly detection algorithms:
  - **Z-Score** (for normal distributions)
  - **IQR Method** (for skewed distributions)
  - **Moving Average & Exponential Smoothing** (for time series)
  - **Seasonal Decomposition** (STL for periodic patterns)
  - **Percentile-based thresholds** (robust to outliers)
- Detect:
  - Point anomalies (single data points)
  - Collective anomalies (sequences)
  - Contextual anomalies (segment-specific)
- Store anomaly results in PostgreSQL
- Publish "anomalies_detected" event

**Critical: NO LLM usage. Pure statistical methods only.**

**Interface:**
- Gets data from message queue (event-driven)
- Background worker pattern

**Outputs:**
- Anomaly records (timestamp, metric, value, anomaly_type, severity, confidence_score)
- Aggregated anomaly summary
- Event: `anomalies_detected` (dataset_id, anomaly_count, time_period)

---

### 2.3 Root Cause Analysis Service
**Responsibilities:**
- Subscribe to "anomalies_detected" events
- For each significant anomaly:
  - **Segmentation Analysis**: Split data by dimensions (region, product, segment) to isolate affected groups
  - **Correlation Analysis**: Compute Pearson/Spearman correlations between metrics
  - **Change Point Detection**: Identify when deviation started
  - **Feature Importance**: Calculate contribution of different factors (variance decomposition)
  - **Cross-metric validation**: Check if anomaly appears in related metrics
- Generate structured root cause hypotheses:
  ```json
  {
    "anomaly_id": "uuid",
    "primary_drivers": [
      {"dimension": "region", "value": "US-East", "impact": 0.67},
      {"dimension": "product", "value": "Enterprise", "impact": 0.23}
    ],
    "correlations": [{"metric": "support_tickets", "correlation": 0.82}],
    "confidence": 0.89,
    "method": "segmentation_variance_analysis"
  }
  ```
- Store root cause results
- Publish "root_cause_complete" event

**Interface:**
- Event-driven background service
- May call RAG module for contextual knowledge

**Outputs:**
- Root cause hypotheses with quantitative impact scores
- Supporting data segments
- Event: `root_cause_complete` (anomaly_id, hypotheses)

---

### 2.4 RAG Module (Optional, for Context)
**Responsibilities:**
- Maintain vector store of business context documents:
  - Metric definitions & business glossaries
  - Known issues/historical incidents
  - Process documentation
  - Org structure (who owns what)
- Provide semantic search: "Find relevant context for revenue drop in Q1"
- Retrieve top-k relevant documents based on anomaly metadata
- Return context snippets to root cause service

**Interface:**
- `POST /api/v1/rag/query` (internal)
- Input: anomaly metadata, business question
- Output: relevant context documents with relevance scores

**Tech:**
- Embedding model: sentence-transformers (all-MiniLM-L6-v2)
- Vector DB: Pinecone/Weaviate for production, ChromaDB for simple deployments

---

### 2.5 Explanation Generator Service
**Responsibilities:**
- Subscribe to "root_cause_complete" events
- Compose final natural language explanation:
  - What happened (anomaly facts)
  - Where it happened (segments affected)
  - Why it happened (root cause with supporting evidence)
  - What to do next (actionable recommendations)
- **LLM Usage (ONLY HERE)**:
  - Template-based fallback if LLM unavailable
  - Prompt includes: anomaly data, root cause analysis, RAG context
  - System prompt enforces: "Base explanation strictly on provided data. Do not invent."
- Store explanation in PostgreSQL
- Publish "explanation_ready" event

**Interface:**
- Event-driven
- Calls LLM API (Anthropic Claude) with structured prompt
- Fallback to template rendering if API fails

**Outputs:**
- Human-readable explanation text
- Confidence score
- Evidence citations (data points, correlations)
- Event: `explanation_ready` (anomaly_id, explanation_id)

---

### 2.6 API Services
**Responsibilities:**
- Expose REST/GraphQL endpoints to frontend
- Handle authentication & authorization
- Orchestrate request flow (trigger processing, fetch results)
- Real-time updates via WebSocket
- Query building for complex filters

**Key Endpoints:**
See Section 5 for full API design.

---

### 2.7 WebSocket Service
**Responsibilities:**
- Push real-time updates when analysis completes
- Stream processing progress (dataset upload, detection, analysis)
- Connection management per user
- Reconnection handling

---

### 2.8 Monitoring & Logging Service
**Responsibilities:**
- Distributed tracing (OpenTelemetry)
- Structured logging (JSON format)
- Metrics collection:
  - Processing times per stage
  - Anomaly detection rate
  - False positive tracking (feedback loop)
  - LLM usage/costs
- Alerting on failures
- Audit trail for compliance

---

## 3. Tech Stack

### 3.1 Backend Core
- **Language**: Python 3.11+
  - **Why**: Rich data science ecosystem (pandas, numpy, scipy), async support, rapid development
- **Framework**: FastAPI
  - **Why**: Async, automatic OpenAPI docs, type hints, high performance
- **Task Queue**: Celery + Redis (or RabbitMQ)
  - **Why**: Proven distributed task processing, result backend, scheduling
- **Message Broker**: RabbitMQ (or Apache Kafka for very high scale)
  - **Why**: Reliable pub/sub, durable messages, complex routing

### 3.2 Data Storage
- **Primary Database**: PostgreSQL 15+
  - **Why**: ACID compliance, JSONB support, excellent for structured metadata, mature ecosystem
  - **Extensions**: pgvector (if needed), timescaledb (for time series optimization)
- **Cache**: Redis 7+
  - **Why**: Sub-millisecond reads, pub/sub for real-time, session storage
- **Object Storage**: AWS S3 / MinIO (self-hosted)
  - **Why**: Cheap, scalable, durable storage for raw CSVs and exports
- **Vector Database**: Pinecone (managed) or Weaviate (self-hosted)
  - **Why**: Optimized for similarity search, filtering, scales to millions of vectors

### 3.3 Frontend
- **Framework**: Next.js 14 (App Router)
  - **Why**: SSR/SSG, API routes, great SEO, React ecosystem
- **Language**: TypeScript
  - **Why**: Type safety, better DX, catches bugs early
- **Styling**: Tailwind CSS + shadcn/ui
  - **Why**: Utility-first, customizable, accessible components
- **State Management**: Zustand
  - **Why**: Simple, minimal boilerplate, great for SaaS apps
- **Charts**: Recharts or Chart.js
  - **Why**: Interactive visualizations, time series support
- **Real-time**: Socket.io client
  - **Why**: Reliable WebSocket with fallbacks

### 3.4 Machine Learning / Analytics
- **Data Processing**: pandas, numpy
  - **Why**: Industry standard, optimized C extensions
- **Statistical Tests**: scipy.stats, statsmodels
  - **Why**: Comprehensive statistical methods
- **Time Series**: statsmodels.tsa, scikit-learn
  - **Why**: Seasonal decomposition, ARIMA, clustering
- **ML Framework**: scikit-learn
  - **Why**: Correlation, feature importance, robust scaling
- **Embeddings**: sentence-transformers
  - **Why**: Local, privacy-preserving, good quality

### 3.5 LLM (Explanation Layer Only)
- **Provider**: Anthropic Claude API
  - **Why**: High quality, reasoning ability, structured output support
- **Fallback**: Local template system (Jinja2)
  - **Why**: Graceful degradation when API unavailable

### 3.6 Infrastructure
- **Containerization**: Docker + Docker Compose
- **Orchestration**: Kubernetes (production), Docker Compose (dev)
- **CI/CD**: GitHub Actions / GitLab CI
- **Monitoring**:
  - **Metrics**: Prometheus + Grafana
  - **Tracing**: Jaeger / Tempo (OpenTelemetry)
  - **Logs**: ELK Stack or Loki + Grafana
- **Secret Management**: HashiCorp Vault or AWS Secrets Manager
- **API Gateway**: Kong / Traefik / AWS ALB
  - **Why**: Rate limiting, auth, SSL termination, routing

### 3.7 Development & Quality
- **Testing**: pytest, pytest-asyncio, pytest-cov
  - **Why**: Async testing support, good ecosystem
- **Code Quality**: black, isort, flake8, mypy
- **API Testing**: httpx,VAULT_C/Postman
- **Linting**: Ruff (fast Python linter)
- **Pre-commit hooks**: pre-commit framework

---

## 4. Data Flow

### 4.1 End-to-End Flow

```
1. CSV UPLOAD
   User → UI → API Gateway → Ingestion Service
   ├─ Validate file size, type
   ├─ Parse headers, infer types
   ├─ Sanity check (too many nulls, etc.)
   ├─ Upload raw CSV to S3/MinIO
   ├─ Create metadata record in PostgreSQL
   └─ Publish event: "dataset_uploaded"

2. ANOMALY DETECTION (Async)
   Detection Service (event listener)
   ├─ Fetch dataset metadata from PostgreSQL
   ├─ Stream CSV from S3 (chunked, memory efficient)
   ├─ Apply statistical methods per numeric column:
   │  ├─ Check distribution (normal vs skewed)
   │  ├─ Apply Z-score or IQR accordingly
   │  ├─ For time series: decompose (trend/seasonal/residual)
   │  └─ Flag anomalies where value outside threshold (typically 3σ or 1.5×IQR)
   ├─ Aggregate by time windows & dimensions
   ├─ Calculate severity scores (z-score magnitude × unexpectedness)
   ├─ Store anomalies in PostgreSQL
   └─ Publish: "anomalies_detected"

3. ROOT CAUSE ANALYSIS (Async)
   Root Cause Service (event listener)
   ├─ Load anomaly context from PostgreSQL
   ├─ For each anomaly:
   │  ├─ SEGMENTATION: Group data by available dimensions
   │  │  └─ Calculate: Which segments deviated most? (variance ratio)
   │  ├─ CORRELATION: Compute with other metrics
   │  │  └─ Pearson/Spearman for linear/monotonic relationships
   │  ├─ CHANGE POINT: When did deviation start?
   │  │  └─ CUSUM or Pettitt test
   │  ├─ FEATURE IMPORTANCE: Variance decomposition
   │  │  └─ Calculate contribution of each factor (ANOVA-like)
   │  └─ CROSS-VALIDATION: Check related metrics
   ├─ (Optional) Query RAG for domain context
   │  └─ "What business processes affect [metric] in [segment]?"
   ├─ Score & rank hypotheses by:
   │  ├─ Effect size (impact magnitude)
   │  ├─ Statistical significance (p-value)
   │  ├─ Business plausibility (from RAG)
   │  └─ Simplicity (Occam's razor)
   ├─ Store root cause hypotheses
   └─ Publish: "root_cause_complete"

4. EXPLANATION GENERATION (Async)
   Explanation Service (event listener)
   ├─ Load anomaly + root cause data
   ├─ (Optional) Query RAG for additional context
   ├─ Build structured prompt:
   │  {
   │    "anomaly": {time, metric, value, expected_range},
   │    "root_causes": [{driver, impact, evidence}],
   │    "context": [relevant_documents],
   │    "instruction": "Explain clearly for business user. Include: what, where, why, what next."
   │  }
   ├─ Call Claude API (with timeout & retry)
   │  └─ Temperature: 0.3 (low, factual)
   │  └─ Max tokens: 500-800
   ├─ Parse & validate response
   ├─ Fallback to template if API fails/timeout
   ├─ Store explanation (text + score + evidence)
   └─ Publish: "explanation_ready"

5. RESPONSE TO USER
   API → WebSocket push OR UI polls
   ├─ User sees notification: "Analysis complete"
   ├─ UI fetches: GET /api/v1/anomalies/{id}/explanation
   └─ Display: Timeline chart + anomaly markers + narrative + recommendations

6. FEEDBACK LOOP (Optional)
   User rates explanation: "Helpful" / "Not helpful"
   └─ Store feedback → Improve prompts/validation rules
```

---

## 5. API Design

### Base URL: `/api/v1`

### Authentication
All endpoints except `/health` require:
- Header: `Authorization: Bearer <jwt_token>`
- JWT contains: `user_id`, `org_id`, `role`

---

### 5.1 Dataset Management

#### `POST /datasets/upload`
**Description**: Upload CSV file for analysis

**Request** (multipart/form-data):
- `file`: CSV file (max 500MB, configurable)
- `name`: Dataset name (optional, defaults to filename)
- `time_column`: Name of column containing timestamps (optional)
- `dimensions`: Comma-separated list of categorical columns (optional)

**Response**:
```json
{
  "dataset_id": "uuid",
  "name": "sales_data.csv",
  "status": "processing",
  "row_count": 150000,
  "column_count": 25,
  "uploaded_at": "2026-04-01T12:30:00Z",
  "estimated_completion": "2026-04-01T12:35:00Z"
}
```

**Errors**:
- `400`: Invalid CSV, missing required columns
- `413`: File too large
- `415`: Unsupported file type

---

#### `GET /datasets`
**Description**: List datasets with pagination and filters

**Query Parameters**:
- `page`: integer (default: 1)
- `per_page`: integer (default: 20, max: 100)
- `status`: filter by `processing|completed|failed`
- `created_after`, `created_before`: ISO dates
- `sort_by`: `created_at|name|row_count` (default: created_at)
- `sort_dir`: `asc|desc` (default: desc)

**Response**:
```json
{
  "datasets": [
    {
      "id": "uuid",
      "name": "sales_data.csv",
      "status": "completed",
      "row_count": 150000,
      "column_count": 25,
      "uploaded_at": "2026-04-01T12:30:00Z",
      "analysis_completed_at": "2026-04-01T12:32:00Z"
    }
  ],
  "pagination": {
    "page": 1,
    "per_page": 20,
    "total": 45,
    "total_pages": 3
  }
}
```

---

#### `GET /datasets/{dataset_id}`
**Description**: Get dataset details

**Response**:
```json
{
  "id": "uuid",
  "name": "sales_data.csv",
  "status": "completed",
  "metadata": {
    "row_count": 150000,
    "column_count": 25,
    "columns": [
      {"name": "date", "type": "datetime", "inferred": true},
      {"name": "revenue", "type": "float", "inferred": true},
      {"name": "region", "type": "categorical", "inferred": false, "user_provided": true}
    ]
  },
  "uploaded_at": "2026-04-01T12:30:00Z",
  "analysis_completed_at": "2026-04-01T12:32:00Z",
  "anomaly_count": 12
}
```

---

### 5.2 Anomaly Detection

#### `GET /datasets/{dataset_id}/anomalies`
**Description**: List detected anomalies

**Query Parameters**:
- `severity_min`: float (0-1, default: 0)
- `type`: filter by `spike|drop|deviation`
- `metric`: filter by metric/column name
- `start_date`, `end_date`: ISO datetime
- `page`, `per_page`

**Response**:
```json
{
  "anomalies": [
    {
      "id": "uuid",
      "timestamp": "2026-03-15T14:00:00Z",
      "metric": "revenue",
      "value": 24500.50,
      "expected_range": [45000, 50000],
      "anomaly_type": "drop",
      "severity": 0.87,
      "confidence": 0.94,
      "dimensions": {
        "region": "US-East",
        "product": "Enterprise"
      }
    }
  ],
  "pagination": { ... },
  "summary": {
    "total_anomalies": 12,
    "avg_severity": 0.72,
    "by_type": {"drop": 8, "spike": 3, "deviation": 1}
  }
}
```

---

#### `GET /anomalies/{anomaly_id}`
**Description**: Get anomaly details with root cause & explanation

**Response**:
```json
{
  "anomaly": {
    "id": "uuid",
    "dataset_id": "uuid",
    "timestamp": "2026-03-15T14:00:00Z",
    "metric": "revenue",
    "value": 24500.50,
    "expected_range": [45000, 50000],
    "anomaly_type": "drop",
    "severity": 0.87,
    "dimensions": {
      "region": "US-East",
      "product": "Enterprise"
    }
  },
  "root_cause": {
    "primary_drivers": [
      {
        "dimension": "region",
        "value": "US-East",
        "impact": 0.67,
        "evidence": "Revenue in US-East fell by 45% while other regions stable"
      },
      {
        "dimension": "product",
        "value": "Enterprise",
        "impact": 0.23,
        "evidence": "Enterprise deals delayed by 2 weeks"
      }
    ],
    "correlations": [
      {
        "metric": "support_tickets",
        "correlation": 0.82,
        "lag_hours": 4
      }
    ],
    "change_point_detected_at": "2026-03-15T10:00:00Z",
    "confidence": 0.89
  },
  "explanation": {
    "text": "On March 15, revenue dropped 45% to $24,500, significantly below the expected range of $45,000-$50,000. This anomaly was concentrated in the US-East region (67% impact) and affected Enterprise customers (23% impact). The likely cause is a payment processing outage reported in US-East between 10 AM-2 PM, corroborated by a spike in support tickets (+180%) 4 hours prior. Recommended: 1) Review payment processor SLA; 2) Notify affected customers with credits; 3) Implement circuit breaker for payment failures.",
    "confidence": 0.91,
    "generated_at": "2026-03-15T15:30:00Z",
    "llm_model": "claude-3-opus-20240229"
  }
}
```

---

### 5.3 RAG (Internal API, not exposed to frontend directly)

#### `POST /internal/rag/query`
**Description**: Query contextual knowledge (internal service-to-service)

**Request**:
```json
{
  "query": "What business processes affect revenue in US-East region?",
  "filters": {
    "document_type": "metric_definition|process_doc|incident",
    "region": "US-East"
  },
  "top_k": 5
}
```

**Response**:
```json
{
  "results": [
    {
      "document_id": "doc_123",
      "text": "Revenue for US-East is processed through the payment gateway API_v2. Outages in API_v2 affect settlement within 24 hours...",
      "source": "metric_definition:revenue",
      "relevance_score": 0.89,
      "metadata": {
        "last_updated": "2026-01-15"
      }
    }
  ]
}
```

---

### 5.4 Monitoring & Admin

#### `GET /health`
**Description**: Health check endpoint

**Response**:
```json
{
  "status": "healthy",
  "services": {
    "database": "healthy",
    "redis": "healthy",
    "s3": "healthy",
    "llm_api": "healthy"
  },
  "version": "1.2.3",
  "timestamp": "2026-04-01T12:41:00Z"
}
```

---

#### `GET /metrics` (Prometheus format)
**Description**: Expose metrics for monitoring

**Metrics**:
- `insightforge_requests_total` (counter, labels: endpoint, method, status)
- `insightforge_request_duration_seconds` (histogram)
- `insightforge_anomalies_detected_total` (counter)
- `insightforge_explanations_generated_total` (counter)
- `insightforge_llm_api_calls_total` (counter, labels: model, status)
- `insightforge_llm_tokens_total` (counter, labels: type)
- `insightforge_queue_duration_seconds` (histogram, labels: queue)
- `celery_task_duration_seconds` (histogram, labels: task_name)

---

## 6. Storage Strategy

### 6.1 PostgreSQL (Primary Database)

**Tables:**

1. **`users`**
   ```sql
   CREATE TABLE users (
     id UUID PRIMARY KEY,
     email VARCHAR(255) UNIQUE NOT NULL,
     org_id UUID NOT NULL,
     role VARCHAR(50) NOT NULL,
     created_at TIMESTAMPTZ DEFAULT NOW()
   );
   ```

2. **`organizations`**
   ```sql
   CREATE TABLE organizations (
     id UUID PRIMARY KEY,
     name VARCHAR(255) NOT NULL,
     plan VARCHAR(50) NOT NULL,
     settings JSONB DEFAULT '{}',
     created_at TIMESTAMPTZ DEFAULT NOW()
   );
   ```

3. **`datasets`**
   ```sql
   CREATE TABLE datasets (
     id UUID PRIMARY KEY,
     org_id UUID NOT NULL,
     name VARCHAR(255) NOT NULL,
     file_path VARCHAR(500) NOT NULL,  -- S3 key
     file_hash VARCHAR(64) NOT NULL,    -- SHA-256 for deduplication
     row_count INTEGER NOT NULL,
     column_count INTEGER NOT NULL,
     column_schema JSONB NOT NULL,      -- [{name, type, inferred}]
     time_column VARCHAR(100),          -- user-provided or inferred
     dimensions JSONB,                  -- list of categorical columns
     status VARCHAR(50) DEFAULT 'uploading',
     error_message TEXT,
     uploaded_by UUID REFERENCES users(id),
     uploaded_at TIMESTAMPTZ DEFAULT NOW(),
     processing_completed_at TIMESTAMPTZ,
     INDEX idx_datasets_org (org_id),
     INDEX idx_datasets_status (status)
   );
   ```

4. **`anomalies`**
   ```sql
   CREATE TABLE anomalies (
     id UUID PRIMARY KEY,
     dataset_id UUID NOT NULL REFERENCES datasets(id),
     timestamp TIMESTAMPTZ NOT NULL,
     metric VARCHAR(100) NOT NULL,
     value DOUBLE PRECISION NOT NULL,
     expected_min DOUBLE PRECISION,
     expected_max DOUBLE PRECISION,
     anomaly_type VARCHAR(50) NOT NULL,  -- spike|drop|deviation
     severity DOUBLE PRECISION NOT NULL CHECK (severity >= 0 AND severity <= 1),
     confidence DOUBLE PRECISION NOT NULL CHECK (confidence >= 0 AND confidence <= 1),
     dimensions JSONB,                    -- {segment: value, ...}
     z_score DOUBLE PRECISION,
     iqr_score DOUBLE PRECISION,
     created_at TIMESTAMPTZ DEFAULT NOW(),
     INDEX idx_anomalies_dataset (dataset_id),
     INDEX idx_anomalies_timestamp (timestamp),
     INDEX idx_anomalies_metric (metric),
     INDEX idx_anomalies_severity (severity DESC)
   );
   ```

5. **`root_causes`**
   ```sql
   CREATE TABLE root_causes (
     id UUID PRIMARY KEY,
     anomaly_id UUID NOT NULL REFERENCES anomalies(id),
     method VARCHAR(100) NOT NULL,       -- segmentation|correlation|change_point
     hypothesis JSONB NOT NULL,          -- {drivers: [], correlations: []}
     confidence DOUBLE PRECISION NOT NULL,
     supporting_data JSONB,              -- data snippets, p-values, etc.
     generated_at TIMESTAMPTZ DEFAULT NOW(),
     UNIQUE (anomaly_id, method)
   );
   ```

6. **`explanations`**
   ```sql
   CREATE TABLE explanations (
     id UUID PRIMARY KEY,
     anomaly_id UUID NOT NULL REFERENCES anomalies(id),
     root_cause_id UUID REFERENCES root_causes(id),
     text TEXT NOT NULL,
     confidence DOUBLE PRECISION NOT NULL,
     llm_model VARCHAR(100),
     tokens_input INTEGER,
     tokens_output INTEGER,
     llm_latency_ms INTEGER,
     generated_at TIMESTAMPTZ DEFAULT NOW(),
     user_feedback VARCHAR(20),          -- helpful|not_helpful|null
     INDEX idx_explanations_anomaly (anomaly_id)
   );
   ```

7. **`rag_documents`** (for RAG module)
   ```sql
   CREATE TABLE rag_documents (
     id UUID PRIMARY KEY,
     org_id UUID NOT NULL,
     document_type VARCHAR(50) NOT NULL, -- metric_def|process|incident|other
     title VARCHAR(500),
     content TEXT NOT NULL,
     embedding VECTOR(384),  -- pgvector, if co-locating vectors
     metadata JSONB DEFAULT '{}',
     created_by UUID REFERENCES users(id),
     created_at TIMESTAMPTZ DEFAULT NOW(),
     updated_at TIMESTAMPTZ DEFAULT NOW(),
     INDEX idx_rag_documents_org (org_id),
     INDEX idx_rag_documents_type (document_type)
   );
   ```

---

### 6.2 Redis

**Usage:**
- **Session storage**: `session:{session_id}` → user session data
- **Cache**: Frequent queries (dataset lists, anomaly summaries)
  - Key: `cache:datasets:{org_id}:{page}:{per_page}`
  - TTL: 5 minutes
- **Rate limiting**: `rate_limit:{user_id}:{endpoint}` (sliding window)
- **Pub/Sub**: Real-time notifications to WebSocket service
  - Channel: `notifications:{user_id}`

---

### 6.3 Object Storage (S3/MinIO)

**Bucket Structure:**
```
insightforge-raw/
  {org_id}/
    {dataset_id}/
      original.csv          (original upload)
      cleaned.csv           (if data cleaning applied)
      processed/            (intermediate chunks)
insightforge-exports/
  {org_id}/
    {export_id}/
      report_20260401.pdf
      data_export_20260401.csv
```

**Policy:**
- Versioning enabled
- Lifecycle: Move to cold storage after 30 days
- Encryption at rest (SSE-S3 or SSE-KMS)
- Pre-signed URLs for secure downloads

---

### 6.4 Vector Database (Pinecone/Weaviate)

**Collection/Index:** `insightforge-rag`

**Embedding**: 384-dim (all-MiniLM-L6-v2)

**Metadata fields:**
- `org_id`
- `document_type`
- `created_at`
- `source`

**Use case:** Semantic search for:
- Metric definitions
- Known issues/historical postmortems
- Business process documentation
- Org/team structure

**Example query:**
```python
# Embed query: "Why did revenue drop in US-East?"
# Search with metadata filter: org_id = X, document_type in ('incident', 'metric_def')
# Return top 5 results with similarity scores
```

---

## 7. Scalability Considerations

### 7.1 Horizontal Scaling

**API Services**:
- Stateless design → multiple replicas behind load balancer
- Auto-scaling based on CPU/memory or request rate
- Kubernetes HPA or AWS ASG

**Detection Service**:
- Worker pool: multiple Celery workers
- Scale horizontally by adding workers
- Partition datasets by org_id or size

**Database**:
- Read replicas for query-heavy workloads
- Connection pool (PgBouncer) to manage connections
- Consider sharding if > 10TB data (likely years away)

**Redis**:
- Redis Cluster for > 50GB datasets
- Replication + Sentinel for HA

**Message Queue**:
- RabbitMQ cluster with mirrored queues
- Partition by message type (detection, rca, explanation)

---

### 7.2 Performance Optimizations

**Ingestion:**
- Streaming CSV parsing (chunks of 10,000 rows)
- Background processing (don't block upload)
- Checksum verification for resume capability

**Detection:**
- Vectorized operations with numpy/pandas (not Python loops)
- Chunk-based processing for large datasets
- Cache intermediate results (stationarity tests, distributions)
- Parallel processing per metric (multiprocessing or Dask)

**Database Queries:**
- Indexes on all filter/sort columns
- Partition `anomalies` table by `timestamp` (monthly)
- Use materialized views for common aggregations
- Connection pooling

**Caching Strategy:**
- Tier 1: Redis (hot: recent datasets, active anomalies)
- Tier 2: CDN for static assets (UI)
- Tier 3: Database query cache (Prepared statements)

---

### 7.3 Cost Management

**LLM Usage**:
- Limit max tokens per explanation (e.g., 800 output)
- Cache explanations: if same anomaly pattern seen before, reuse
- Budget limits per org (monthly quota)
- Fallback to templates if budget exceeded

**Storage**:
- Compress CSVs (gzip) automatically
- Lifecycle policies: delete raw CSV after 90 days (keep metadata)
- Tiered storage: S3 Standard → IA → Glacier

**Database**:
- Aggressive archiving: Move anomalies > 2 years old to cold storage
- Partitioning for easier deletion
- Vacuum and analyze regularly

---

### 7.4 Resilience & Fault Tolerance

**Retry Patterns:**
- Exponential backoff for LLM API calls (max 3 retries)
- Dead letter queue for failed tasks (manual review)
- Circuit breaker for downstream dependencies

**Data Integrity:**
- Checksums for uploaded files
- Transactional writes (all-or-nothing for anomaly + root cause + explanation)
- Idempotent operations (event deduplication)

**High Availability:**
- Multi-AZ deployment (at least 2 availability zones)
- Database: PostgreSQL with streaming replication + automatic failover
- Redis: Sentinel or cluster mode
- Services: Multiple replicas, zero-downtime deployments

**Disaster Recovery:**
- Daily backups of PostgreSQL (WAL archiving)
- Cross-region replication for S3
- Backup vector database snapshots
- Test restore procedures monthly

---

### 7.5 Throughput & Capacity Planning

**Assumptions:**
- Average dataset: 100K rows × 20 columns = 2M data points
- Detection throughput: ~10M data points/sec with pandas + numpy
- Processing time: 2-10 seconds per dataset (statistical only)
- LLM explanation: 2-5 seconds per anomaly (batch up to 5 anomalies)

**Capacity:**
- Single detection worker: ~300 datasets/hour
- 10 workers: 3,000 datasets/hour (72,000/day)
- Scales linearly by adding workers

**Burst Handling:**
- Message queue buffers upload spikes
- Auto-scaling workers based on queue depth
- Rate limiting at API gateway: 10 uploads/minute per user

---

## 8. Interface Contracts

### 8.1 Event Schema (Message Queue)

All events follow this base structure:
```json
{
  "event_id": "uuid",
  "event_type": "dataset_uploaded|anomalies_detected|root_cause_complete|explanation_ready",
  "timestamp": "2026-04-01T12:30:00Z",
  "version": "1.0",
  "payload": { ... event-specific fields ... }
}
```

#### Event: `dataset_uploaded`
```json
{
  "event_type": "dataset_uploaded",
  "payload": {
    "dataset_id": "uuid",
    "org_id": "uuid",
    "storage_path": "s3://bucket/org/dataset/original.csv",
    "schema": [
      {"name": "date", "type": "datetime"},
      {"name": "revenue", "type": "float"}
    ],
    "time_column": "date",
    "dimensions": ["region", "product"],
    "row_count": 150000
  }
}
```

#### Event: `anomalies_detected`
```json
{
  "event_type": "anomalies_detected",
  "payload": {
    "dataset_id": "uuid",
    "anomaly_count": 12,
    "time_period": {
      "start": "2026-03-01",
      "end": "2026-03-31"
    },
    "processing_time_sec": 8.5,
    "anomaly_ids": ["uuid1", "uuid2", "..."]  // IDs of created anomaly records
  }
}
```

#### Event: `root_cause_complete`
```json
{
  "event_type": "root_cause_complete",
  "payload": {
    "anomaly_ids": ["uuid1", "uuid2"],
    "hypotheses_generated": 15,
    "processing_time_sec": 12.3
  }
}
```

#### Event: `explanation_ready`
```json
{
  "event_type": "explanation_ready",
  "payload": {
    "anomaly_id": "uuid",
    "explanation_id": "uuid",
    "processing_time_sec": 3.2
  }
}
```

---

### 8.2 Service-to-Service API Contracts

#### Detection Service → Database
- **Read**: `SELECT * FROM datasets WHERE id = $1`
- **Write**: `INSERT INTO anomalies (...) VALUES (...) RETURNING id`
- All writes are idempotent (check if anomaly exists at same timestamp+metric)

#### Root Cause → Detection Service (internal)
No direct call. Uses database as canonical source.

#### Explanation → LLM API
**Request**:
```json
{
  "model": "claude-3-opus-20240229",
  "max_tokens": 800,
  "temperature": 0.3,
  "system": "You are an AI business analyst. Explain anomalies clearly and factually based ONLY on the provided data. Never invent or speculate beyond evidence.",
  "messages": [
    {
      "role": "user",
      "content": "Analyze this anomaly:\n\n<anomaly>\n{anomaly_json}\n</anomaly>\n\n<root_cause_analysis>\n{root_cause_json}\n</root_cause_analysis>\n\n<contextual_information>\n{rag_context_json}</contextual_information>\n\nProvide a clear explanation with: 1) What happened, 2) Where, 3) Why, 4) Recommended actions. Use business language. Be concise (3-5 sentences)."
    }
  ]
}
```

**Response** (streaming or complete):
```json
{
  "id": "msg_123",
  "model": "claude-3-opus-20240229",
  "usage": {
    "input_tokens": 450,
    "output_tokens": 195
  },
  "content": [{"type": "text", "text": "On March 15, revenue dropped 45%..."}]
}
```

**Fallback Template** (if LLM fails):
```jinja2
{% if anomaly.anomaly_type == 'drop' %}
Revenue dropped {{ (1 - (anomaly.value / ((anomaly.expected_min+anomaly.expected_max)/2)) * 100)|round(1) }}%
{% elif anomaly.anomaly_type == 'spike' %}
Revenue spiked {{ ((anomaly.value / ((anomaly.expected_min+anomaly.expected_max)/2) - 1) * 100)|round(1) }}%
{% endif %}
to ${{ anomaly.value|round(2) }} on {{ anomaly.timestamp|date('YYYY-MM-DD HH:mm') }}.

{% if root_cause.primary_drivers %}
Primary driver: {{ root_cause.primary_drivers[0].dimension }} ({{ root_cause.primary_drivers[0].impact*100|round(1) }}% impact).
{% endif %}

{% if root_cause.correlations %}
Correlated with {{ root_cause.correlations[0].metric }} (r={{ root_cause.correlations[0].correlation|round(2) }}).
{% endif %}

Investigate the {{ root_cause.primary_drivers[0].dimension|default('affected segments') }} and review related metrics for further insights.
```

---

### 8.3 WebSocket Events

**Connection**: `wss://api.insightforge.ai/ws?token=<jwt>`

**Server → Client**:
```json
{
  "type": "notification|progress|error",
  "event": "dataset_uploaded|anomalies_detected|root_cause_complete|explanation_ready",
  "data": { ... },
  "timestamp": "2026-04-01T12:30:00Z"
}
```

**Examples:**

Progress update:
```json
{
  "type": "progress",
  "event": "dataset_processing",
  "data": {
    "dataset_id": "uuid",
    "stage": "detection",
    "progress_percent": 65,
    "message": "Analyzing monthly_revenue metric (65/100 columns complete)"
  }
}
```

Notification:
```json
{
  "type": "notification",
  "event": "explanation_ready",
  "data": {
    "anomaly_id": "uuid",
    "dataset_name": "sales_data.csv",
    "metric": "revenue",
    "timestamp": "2026-03-15T14:00:00Z",
    "severity": 0.87
  }
}
```

---

## 9. Security Considerations

### 9.1 Data Isolation
- **Multi-tenancy**: Every query includes `org_id` filter
- **Row-level security**: Database queries always filter by `org_id`
- **Storage isolation**: S3 paths encode org_id, bucket policies enforced
- **Network isolation**: Services communicate via private subnets (VPC)

### 9.2 Authentication & Authorization
- JWT tokens (short-lived, 1 hour) with refresh tokens
- OAuth 2.0 for enterprise SSO (optional)
- Role-based access control (RBAC):
  - `viewer`: Read-only
  - `analyst`: Can upload datasets, view analysis
  - `admin`: Manage users, settings

### 9.3 Data Protection
- **Encryption at rest**: S3 SSE-S3/SSE-KMS, PostgreSQL TLS, Redis AUTH
- **Encryption in transit**: HTTPS + WSS everywhere
- **PII Detection**: Optional PII scanning on upload (presidio)
- **Data retention**: Auto-delete raw CSV after configurable period (default: 90 days)
- **Audit logs**: All data access logged (who accessed what, when)

### 9.4 LLM Data Privacy
- **No sensitive PII** sent to Claude API in production (redact if present)
- **Business context only**: Explanations use aggregated metrics, not raw customer data
- **Opt-out flag**: Organizations can disable LLM explanations entirely
- **Data processing agreement**: Compliant with vendor (Anthropic) terms

### 9.5 API Security
- Rate limiting: 100 requests/minute per user
- Input validation: Pydantic models, strict schemas
- SQL injection prevention: Parameterized queries only
- CSRF protection for browser clients
- CORS: Configurable allowed origins per org

---

## 10. Error Handling & Observability

### 10.1 Error Types & Responses

**Client Errors (4xx)**:
```json
{
  "error": {
    "code": "INVALID_CSV",
    "message": "CSV parsing failed: column 'date' has mixed types",
    "details": {"line": 1543, "column": "date"},
    "request_id": "uuid"
  }
}
```

**Server Errors (5xx)**:
```json
{
  "error": {
    "code": "DETECTION_SERVICE_ERROR",
    "message": "Anomaly detection failed due to insufficient variance in dataset",
    "request_id": "uuid",
    "support_contact": "support@insightforge.ai"
  }
}
```

---

### 10.2 Logging Strategy

**Structured JSON logs**:
```json
{
  "timestamp": "2026-04-01T12:30:00Z",
  "level": "INFO",
  "service": "detection",
  "trace_id": "uuid",
  "user_id": "uuid",
  "org_id": "uuid",
  "dataset_id": "uuid",
  "message": "Anomaly detection completed",
  "metadata": {
    "rows_processed": 150000,
    "anomalies_found": 12,
    "duration_sec": 8.5
  }
}
```

**Log levels**:
- **DEBUG**: Detailed internal state (dev only)
- **INFO**: Normal operations (dataset uploaded, analysis complete)
- **WARNING**: Recoverable issues (LLM timeout, using fallback)
- **ERROR**: Service failures, exceptions
- **CRITICAL**: System down, data corruption

**Centralization**: Fluentd → Elasticsearch/Loki → Grafana

---

### 10.3 Metrics to Monitor

**Business Metrics:**
- Active organizations (DAU/MAU)
- Datasets uploaded per day
- Anomalies detected per day
- Explanation quality score (user feedback avg)

**Technical Metrics:**
- API request rate & latency (p50, p95, p99)
- Detection processing time distribution
- LLM API latency & error rate
- Queue depth & processing lag
- Database query performance (slow query log)
- Error rate by service
- Resource utilization (CPU, memory, disk)

**Alerting Thresholds:**
- Error rate > 1% for 5 minutes
- P95 latency > 5s for API
- Queue depth > 10,000 tasks
- LLM fallback rate > 10%
- Storage usage > 80%

---

## 11. Deployment Architecture (Production)

### 11.1 Infrastructure Topology

```
Region: us-east-1 (primary), eu-west-1 (DR backup)

VPC:
  - Public Subnets (2 AZs)
    • ALB/API Gateway
    • Bastion host
  - Private Subnets (2 AZs each)
    • EKS/ECS cluster for services
    • RDS (PostgreSQL) with read replica in second AZ
    • ElastiCache (Redis)
    • S3 (VPC endpoint)
    • RabbitMQ brokers

Container Registry: ECR / Docker Hub

CI/CD: GitHub Actions
  - Build → Test → Push to registry → Deploy to staging → Manual approval → Deploy to prod
  - Infrastructure as Code: Terraform
```

---

### 11.2 Environment Configuration

**Configuration Management:**
- Environment variables for secrets (via HashiCorp Vault)
- Config files for feature flags (S3/Redis connection strings)
- Kubernetes ConfigMaps & Secrets

**Environments:**
1. **Development**: Local Docker Compose (all services)
2. **Staging**: Production topology, sampled/obfuscated data
3. **Production**: Full topology, real data

---

### 11.3 Database Migration Strategy

- Alembic (Python) for schema migrations
- Zero-downtime migrations:
  - Add columns: `ALTER TABLE ADD COLUMN ... DEFAULT ...` (fast)
  - Backfill in batches
  - Remove columns: Deprecate → Nullable → Drop (2-3 releases)

---

### 11.4 Backup & Restore

**PostgreSQL:**
- Automated daily base backups + WAL archiving
- Retain 7 days of point-in-time recovery
- Test restore weekly

**S3:**
- Cross-region replication for critical exports
- Versioning enabled (recover from accidental delete)

**Redis:**
- RDB snapshots every 6 hours
- AOF for durability

---

## 12. Future Evolution

### Phase 2 (Post-MVP):
- **Multi-metric correlation**: Global correlation matrix across all metrics
- **Predictive alerts**: Forecast-based anomaly prediction (Prophet, LSTM)
- **Comparative analysis**: "Same anomaly last month vs this month"
- **Alerting integrations**: Slack, Teams, email notifications
- **User feedback loop**: Reinforcement learning for root cause ranking

### Phase 3:
- **Custom anomaly thresholds**: Per-org/user sensitivity tuning
- **Anomaly clustering**: Group similar anomalies automatically
- **Causal inference**: DoWhy library for causal graphs
- **Adaptive baselines**: Dynamic thresholds based on seasonality
- **Data quality scoring**: Include data quality issues in explanations

### Phase 4:
- **Cross-dataset analysis**: Compare anomalies across datasets
- **Natural language query**: "Show me all revenue drops in Q1"
- **Collaboration features**: Share anomalies, comment, assign
- **Advanced visualizations**: Sankey diagrams for root cause paths, heatmaps
- **API for partners**: White-label integrations

---

## 13. Key Design Decisions & Rationale

| Decision | Rationale |
|----------|-----------|
| **Python/FastAPI** | Data science stack maturity, async support, rapid iteration |
| **Separation: Detection (stats) vs Explanation (LLM)** | Control costs, ensure reliability, deterministic core logic |
| **Event-driven architecture** | Loose coupling, resilience, scalable processing |
| **PostgreSQL + JSONB** | Relational integrity for users/orgs, flexible schema for evolving data |
| **Redis caching** | Sub-ms response for frequent queries (anomaly lists, dataset metadata) |
| **S3 for raw files** | Cheap, scalable, durable, separates compute from storage |
| **Pinecone/Weaviate** | Purpose-built for vector search, scales better than pgvector for large contexts |
| **RabbitMQ vs Kafka** | RabbitMQ simpler for our throughput (<10K msgs/sec), queues durable |
| **React/Next.js** | Server-side rendering for SEO, API routes for full-stack simplicity |
| **Tailwind + shadcn/ui** | Fast UI development, accessible, customizable |
| **Celery** | Battle-tested, simple, good monitoring integration |
| **OpenTelemetry** | Vendor-agnostic observability, standard in industry |

---

## 14. Risk Mitigation

| Risk | Mitigation |
|------|------------|
| **LLM hallucinations** | Strict prompts, temperature=0.3, evidence citations, human-in-the-loop review |
| **Statistical false positives** | Configurable thresholds, multi-method consensus (require 2/3 methods to flag) |
| **Large dataset memory issues** | Chunked processing, streaming, memory limits per worker |
| **LLM API downtime** | Automatic fallback to templates, retry with backoff, circuit breaker |
| **Slow processing** | Auto-scaling workers, priority queues, estimated completion times |
| **Data privacy breaches** | PII detection, encryption, audit logs, SOC2 compliance roadmap |
| **Vendor lock-in** | Abstraction layers for LLM (plug-and-play), containerized deployment |
| **Scalability bottleneck** | Load testing, DB query optimization, partitioned tables, CDN |
| **Poor user experience** | Real-time progress updates, reasonable timeout expectations, graceful degradation |

---

## 15. Success Metrics (Technical)

- **Uptime**: 99.9% (excluding planned maintenance)
- **API Latency**: P95 < 500ms, P99 < 2s
- **Dataset Processing**: 95% complete within 30 seconds of upload (for 100K rows)
- **Explanation Generation**: 95% within 10 seconds (excluding LLM latency)
- **Availability**: Services auto-restart within 60s of failure
- **Data Durability**: 99.999999999% (11 nines) for stored files

---

**Document Version**: 1.0
**Last Updated**: 2026-04-01
**Status**: Draft for Review
