"""
InsightForge AI - Root Cause Analysis Module

This module implements statistical root cause analysis for anomalies.
NO LLM USAGE - Pure statistical methods only.

Components:
- Segmentation Analysis: Compare affected segments against baseline
- Correlation Analysis: Find correlated metrics that changed simultaneously
- Change Point Detection: Identify when deviation started
- Impact Attribution: Quantify contribution of factors
"""

__version__ = "1.0.0"
__author__ = "InsightForge AI"

from .analyzer import RootCauseAnalyzer
from .segmenter import SegmentationAnalyzer
from .correlator import CorrelationAnalyzer
from .attribution import AttributionAnalyzer
from .models import (
    RootCauseInsight,
    SegmentContribution,
    CorrelationResult,
    ChangePoint,
    AnalysisMethod,
)

__all__ = [
    "RootCauseAnalyzer",
    "SegmentationAnalyzer",
    "CorrelationAnalyzer",
    "AttributionAnalyzer",
    "RootCauseInsight",
    "SegmentContribution",
    "CorrelationResult",
    "ChangePoint",
    "AnalysisMethod",
]
