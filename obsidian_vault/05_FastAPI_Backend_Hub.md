---
tags:
  - #hub
  - #backend
---
# 💙 05 FastAPI Backend Subsystem Hub

> **Master Hub**: [[00_Master_Hub]] | **Architecture**: [[01_System_Architecture]]

---

## 🔌 API Routers & Services

- [[files/backend_main_py]] — FastAPI Server Entry point.
- [[files/backend_routers_anomalies_py]] — Anomaly Detection REST Endpoint.
- [[files/backend_routers_rag_py]] — RAG Document Upload & Query REST Endpoint.
- [[files/backend_routers_datasets_py]] — Dataset Ingestion & Management Endpoint.
- [[files/backend_routers_health_py]] — Health Check Endpoint.

## 💾 Storage & Data Layer
- [[files/backend_storage_database_py]] — SQLite Database Connection & Session Pool.
- [[files/backend_storage_file_store_py]] — Local File Upload Manager.
- [[files/backend_dependencies_py]] — FastAPI Dependency Injection.
- [[files/backend_config_py]] — Application Settings & API Keys.
