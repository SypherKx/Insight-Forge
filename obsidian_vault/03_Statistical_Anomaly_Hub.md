---
tags:
  - #hub
  - #anomaly
---
# 💚 03 Statistical Anomaly Engine Hub

> **Master Hub**: [[00_Master_Hub]] | **Architecture**: [[01_System_Architecture]]

---

## 🧮 Core Anomaly Modules

- [[files/src_detection_detector_py]] — Anomaly Detector Orchestrator (`AnomalyDetector`).
- [[files/src_detection_algorithms_py]] — Algorithms implementation (Z-Score, MAD, IQR, Pettitt Test).
- [[files/src_detection_scorer_py]] — Anomaly severity & ensemble scoring.
- [[files/src_detection_models_py]] — Data models for raw signals & anomaly alerts.

---

## ⚡ Connected Backend Routes
- Connected Backend Routers: [[files/backend_routers_anomalies_py]] & [[files/backend_services_analysis_py]]
