---
tags:
  - #hub
  - #rootcause
---
# 💛 04 Root Cause Engine Hub

> **Master Hub**: [[00_Master_Hub]] | **Architecture**: [[01_System_Architecture]]

---

## 🔍 Root Cause Analysis Modules

- [[files/src_root_cause_analyzer_py]] — Root Cause Analyzer Orchestrator (`RootCauseAnalyzer`).
- [[files/src_root_cause_attribution_py]] — Dimension attribution calculator (`AttributionCalculator`).
- [[files/src_root_cause_correlator_py]] — Feature correlation engine (`FeatureCorrelator`).
- [[files/src_root_cause_segmenter_py]] — Data segmenter (`DataSegmenter`).
- [[files/src_root_cause_models_py]] — Root Cause Data Models (`RootCauseResult`).

---

## ⚡ Subsystem Connections
- Connected Anomaly Engine: [[03_Statistical_Anomaly_Hub]]
