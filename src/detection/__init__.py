"""
InsightForge AI - Anomaly Detection Module

Pure statistical anomaly detection for time series business data.
No LLM involvement - fast, deterministic, interpretable.

Main components:
- algorithms: Statistical detection methods (Z-score, IQR, Moving Average, Change Point)
- detector: Main AnomalyDetector orchestrator
- scorer: Confidence and severity calculation
- models: Data structures and configuration

Quick start:
    from detection import AnomalyDetector, DetectionConfig

    detector = AnomalyDetector()
    anomalies = detector.detect(df, metric_columns=['revenue', 'orders'])

    for anomaly in anomalies:
        print(f"{anomaly.timestamp}: {anomaly.metric} {anomaly.anomaly_type} "
              f"(severity={anomaly.severity:.2f}, confidence={anomaly.confidence:.1f})")
"""

from .models import (
    Anomaly,
    AnomalyType,
    Severity,
    DetectionConfig
)
from .algorithms import (
    detect_zscore,
    detect_iqr,
    detect_moving_average,
    detect_seasonal_decomposition,
    detect_change_point,
    detect_collective_anomaly,
    detect_contextual_anomaly,
    ensemble_detection
)
from .scorer import (
    calculate_confidence,
    calculate_severity,
    get_severity_label,
    score_anomalies,
    calculate_expected_range
)
from .detector import (
    AnomalyDetector,
    detect_anomalies
)

__all__ = [
    # Models
    'Anomaly',
    'AnomalyType',
    'Severity',
    'DetectionConfig',
    # Algorithms
    'detect_zscore',
    'detect_iqr',
    'detect_moving_average',
    'detect_seasonal_decomposition',
    'detect_change_point',
    'detect_collective_anomaly',
    'detect_contextual_anomaly',
    'ensemble_detection',
    # Scorer
    'calculate_confidence',
    'calculate_severity',
    'get_severity_label',
    'score_anomalies',
    'calculate_expected_range',
    # Detector
    'AnomalyDetector',
    'detect_anomalies'
]

__version__ = '1.0.0'
