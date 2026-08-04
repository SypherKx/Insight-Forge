"""
Analysis Service — Orchestrates the full detection → root cause → explanation pipeline.

This is the core integration point that connects all modules.
"""

import sys
import os
import logging
import uuid
from datetime import datetime
from typing import Dict, Any, List, Optional, Tuple
from pathlib import Path

import pandas as pd
import numpy as np

# Add src to path for module imports
SRC_DIR = str(Path(__file__).resolve().parent.parent.parent / "src")
if SRC_DIR not in sys.path:
    sys.path.insert(0, SRC_DIR)

from detection.detector import AnomalyDetector
from detection.models import DetectionConfig, Anomaly
from root_cause.analyzer import RootCauseAnalyzer
from explainer.generator import ExplanationGenerator
from explainer.models import (
    ExplanationConfig,
    ExplanationRequest,
    AnomalyContext,
    RootCauseContext,
)

logger = logging.getLogger(__name__)


class AnalysisService:
    """
    Orchestrates the complete analysis pipeline:
    1. Anomaly Detection (statistical, NO LLM)
    2. Root Cause Analysis (statistical, NO LLM)
    3. Explanation Generation (LLM with template fallback)
    """

    def __init__(
        self,
        detection_config: Optional[DetectionConfig] = None,
        explanation_config: Optional[ExplanationConfig] = None,
    ):
        self.detector = AnomalyDetector(detection_config or DetectionConfig())
        self.root_cause_analyzer = RootCauseAnalyzer()
        self.explainer = ExplanationGenerator(explanation_config or ExplanationConfig())

        logger.info("AnalysisService initialized")

    def run_full_analysis(
        self,
        df: pd.DataFrame,
        dataset_id: str,
        time_column: Optional[str] = None,
        metric_columns: Optional[List[str]] = None,
        dimensions: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        """
        Run the complete analysis pipeline on a DataFrame.

        Args:
            df: Loaded DataFrame
            dataset_id: Dataset ID
            time_column: Time column name (auto-detect if None)
            metric_columns: Metric columns (auto-detect if None)
            dimensions: Categorical dimension columns

        Returns:
            Dict with anomalies, root_causes, and explanations
        """
        logger.info(f"Starting full analysis for dataset {dataset_id} ({len(df)} rows)")

        # Auto-detect time column if not provided
        if time_column is None:
            time_column = self._detect_time_column(df)

        # Auto-detect dimensions if not provided
        if dimensions is None:
            dimensions = self._detect_dimensions(df, time_column)

        # ═══════════════════════════════════════
        # STEP 1: Anomaly Detection
        # ═══════════════════════════════════════
        logger.info("Step 1: Running anomaly detection...")

        anomalies = self.detector.detect(
            data=df,
            metric_columns=metric_columns,
            time_column=time_column,
            dimensions=dimensions,
        )

        logger.info(f"Detected {len(anomalies)} anomalies")

        if not anomalies:
            return {
                "anomalies": [],
                "root_causes": [],
                "explanations": [],
                "summary": {"total_anomalies": 0},
            }

        # ═══════════════════════════════════════
        # STEP 2: Root Cause Analysis
        # ═══════════════════════════════════════
        logger.info("Step 2: Running root cause analysis...")

        results = []

        for anomaly in anomalies[:20]:  # Limit to top 20 anomalies
            result = self._analyze_single_anomaly(
                anomaly=anomaly,
                df=df,
                dataset_id=dataset_id,
                time_column=time_column,
                dimensions=dimensions,
            )
            if result:
                results.append(result)

        # Separate out the results
        all_anomalies = [r["anomaly"] for r in results]
        all_root_causes = [r["root_cause"] for r in results if r.get("root_cause")]
        all_explanations = [r["explanation"] for r in results if r.get("explanation")]

        # Build summary
        summary = self._build_summary(all_anomalies)

        logger.info(
            f"Analysis complete: {len(all_anomalies)} anomalies, "
            f"{len(all_root_causes)} root causes, "
            f"{len(all_explanations)} explanations"
        )

        return {
            "anomalies": all_anomalies,
            "root_causes": all_root_causes,
            "explanations": all_explanations,
            "summary": summary,
        }

    def _analyze_single_anomaly(
        self,
        anomaly: Anomaly,
        df: pd.DataFrame,
        dataset_id: str,
        time_column: Optional[str],
        dimensions: List[str],
    ) -> Optional[Dict[str, Any]]:
        """Analyze a single anomaly through root cause + explanation."""
        anomaly_id = str(uuid.uuid4())

        anomaly_dict = {
            "id": anomaly_id,
            "dataset_id": dataset_id,
            "timestamp": str(anomaly.timestamp) if anomaly.timestamp else None,
            "metric": anomaly.metric,
            "value": float(anomaly.value),
            "expected_min": float(anomaly.expected_range[0]),
            "expected_max": float(anomaly.expected_range[1]),
            "anomaly_type": anomaly.anomaly_type.value,
            "severity": float(anomaly.severity),
            "confidence": float(anomaly.confidence),
            "dimensions": anomaly.dimensions or {},
            "algorithm_scores": anomaly.algorithm_scores or {},
        }

        # Root Cause Analysis
        root_cause_dict = None
        try:
            if time_column and time_column in df.columns and dimensions:
                # Convert timestamp for comparison
                try:
                    anomaly_ts = pd.to_datetime(anomaly.timestamp)
                except Exception:
                    anomaly_ts = datetime.utcnow()

                insight = self.root_cause_analyzer.analyze_anomaly(
                    anomaly_id=anomaly_id,
                    anomaly_timestamp=anomaly_ts,
                    metric=anomaly.metric,
                    anomaly_value=float(anomaly.value),
                    expected_range=[
                        float(anomaly.expected_range[0]),
                        float(anomaly.expected_range[1]),
                    ],
                    data=df.copy(),
                    dimensions=dimensions,
                    time_column=time_column,
                    dataset_id=dataset_id,
                )

                if insight:
                    root_cause_dict = {
                        "anomaly_id": anomaly_id,
                        "hypothesis": insight.hypothesis,
                        "primary_drivers": [
                            {
                                "segment": d.segment,
                                "contribution": float(d.contribution),
                                "baseline_ratio": float(d.baseline_ratio),
                            }
                            for d in insight.primary_drivers
                        ],
                        "correlations": [
                            {
                                "metric": c.metric,
                                "coefficient": float(c.coefficient),
                                "p_value": float(c.p_value) if c.p_value else None,
                                "lag_hours": float(c.lag_hours) if c.lag_hours else None,
                            }
                            for c in insight.correlations
                        ],
                        "change_point": (
                            {
                                "detected_at": str(insight.change_point.detected_at),
                                "confidence": float(insight.change_point.confidence),
                                "before_mean": float(insight.change_point.before_mean),
                                "after_mean": float(insight.change_point.after_mean),
                                "change_magnitude": float(insight.change_point.change_magnitude),
                            }
                            if insight.change_point
                            else None
                        ),
                        "confidence": float(insight.confidence),
                        "methods_used": [m.value for m in insight.methods_used],
                        "supporting_evidence": insight.supporting_evidence,
                        "processing_time_sec": float(insight.processing_time_sec),
                    }
        except Exception as e:
            logger.warning(f"Root cause analysis failed for anomaly {anomaly_id}: {e}")

        # Explanation Generation
        explanation_dict = None
        try:
            anomaly_context = AnomalyContext(
                anomaly_id=anomaly_id,
                timestamp=pd.to_datetime(anomaly.timestamp) if anomaly.timestamp else datetime.utcnow(),
                metric=anomaly.metric,
                value=float(anomaly.value),
                expected_min=float(anomaly.expected_range[0]),
                expected_max=float(anomaly.expected_range[1]),
                anomaly_type=anomaly.anomaly_type.value,
                severity=float(anomaly.severity),
                confidence=float(anomaly.confidence),
                dimensions=anomaly.dimensions or {},
            )

            root_cause_context = RootCauseContext()
            if root_cause_dict:
                root_cause_context = RootCauseContext(
                    primary_drivers=root_cause_dict.get("primary_drivers", []),
                    correlations=root_cause_dict.get("correlations", []),
                    change_point=root_cause_dict.get("change_point"),
                    hypothesis=root_cause_dict.get("hypothesis", ""),
                    confidence=root_cause_dict.get("confidence", 0),
                )

            request = ExplanationRequest(
                anomaly=anomaly_context,
                root_cause=root_cause_context,
            )

            response = self.explainer.generate(request)

            explanation_dict = {
                "anomaly_id": anomaly_id,
                "text": response.explanation_text,
                "summary": response.summary,
                "recommendations": response.recommendations,
                "confidence": float(response.confidence),
                "evidence_citations": response.evidence_citations,
                "llm_model": response.llm_model,
                "tokens_input": response.tokens_input,
                "tokens_output": response.tokens_output,
                "latency_ms": response.latency_ms,
                "used_fallback": response.used_fallback,
            }
        except Exception as e:
            logger.warning(f"Explanation generation failed for anomaly {anomaly_id}: {e}")

        return {
            "anomaly": anomaly_dict,
            "root_cause": root_cause_dict,
            "explanation": explanation_dict,
        }

    def _detect_time_column(self, df: pd.DataFrame) -> Optional[str]:
        """Auto-detect datetime column."""
        for col in df.columns:
            if pd.api.types.is_datetime64_any_dtype(df[col]):
                return col
            # Try parsing as dates
            try:
                sample = df[col].dropna().head(20)
                if len(sample) > 0:
                    parsed = pd.to_datetime(sample, errors="coerce")
                    if parsed.notna().mean() > 0.8:
                        return col
            except Exception:
                continue
        return None

    def _detect_dimensions(
        self, df: pd.DataFrame, time_column: Optional[str]
    ) -> List[str]:
        """Auto-detect categorical dimension columns."""
        dims = []
        for col in df.columns:
            if col == time_column:
                continue
            if df[col].dtype == "object" or df[col].dtype.name == "category":
                n_unique = df[col].nunique()
                if 2 <= n_unique <= 50:
                    dims.append(col)
        return dims[:5]  # Limit to 5 dimensions

    def _build_summary(self, anomalies: List[Dict]) -> Dict[str, Any]:
        """Build anomaly summary statistics."""
        if not anomalies:
            return {"total_anomalies": 0}

        severities = [a["severity"] for a in anomalies]
        types = [a["anomaly_type"] for a in anomalies]

        severity_levels = {}
        for s in severities:
            if s >= 0.7:
                level = "critical"
            elif s >= 0.4:
                level = "high"
            elif s >= 0.2:
                level = "medium"
            else:
                level = "low"
            severity_levels[level] = severity_levels.get(level, 0) + 1

        return {
            "total_anomalies": len(anomalies),
            "avg_severity": float(np.mean(severities)),
            "max_severity": float(max(severities)),
            "by_type": {t: types.count(t) for t in set(types)},
            "by_severity_level": severity_levels,
            "metrics_affected": list(set(a["metric"] for a in anomalies)),
        }
