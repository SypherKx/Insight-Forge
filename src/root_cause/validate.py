#!/usr/bin/env python3
"""
Quick validation script for the root cause module.
Ensures all imports work and runs a minimal sanity check.
"""

import sys
import os
import pandas as pd

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

try:
    print("Testing imports...")
    from root_cause import (
        RootCauseAnalyzer,
        SegmentationAnalyzer,
        CorrelationAnalyzer,
        AttributionAnalyzer,
        RootCauseInsight,
        SegmentContribution,
        CorrelationResult,
        ChangePoint,
        AnalysisMethod,
    )
    print("✓ All imports successful")

    print("\nTesting basic instantiation...")
    analyzer = RootCauseAnalyzer()
    print(f"✓ RootCauseAnalyzer created with segmenter, correlator, attribution")
    print(f"  - Min confidence: {analyzer.min_confidence}")
    print(f"  - Max drivers: {analyzer.max_primary_drivers}")
    print(f"  - Max correlations: {analyzer.max_correlations}")

    print("\nTesting component instantiation...")
    seg = SegmentationAnalyzer()
    print(f"✓ SegmentationAnalyzer (min_segment_size={seg.min_segment_size})")

    corr = CorrelationAnalyzer()
    print(f"✓ CorrelationAnalyzer (window={corr.correlation_window})")

    attr = AttributionAnalyzer()
    print(f"✓ AttributionAnalyzer (method={attr.method})")

    print("\n✓ All components instantiated successfully!")

    print("\nTesting Pydantic model creation...")
    segment = SegmentContribution(
        segment="region: US-East",
        contribution=45.5,
        baseline_ratio=0.3,
    )
    print(f"✓ SegmentContribution: {segment.segment}, contrib={segment.contribution}%")

    correlation = CorrelationResult(
        metric="marketing_spend",
        coefficient=-0.85,
    )
    print(f"✓ CorrelationResult: {correlation.metric}, r={correlation.coefficient}")

    change_point = ChangePoint(
        detected_at=pd.Timestamp.now(),
        confidence=0.87,
        method="pettitt_test",
    )
    print(f"✓ ChangePoint: confidence={change_point.confidence}")

    insight = RootCauseInsight(
        anomaly_id="test",
        anomaly_timestamp=pd.Timestamp.now(),
        metric="revenue",
        anomaly_value=1000.0,
        expected_range=[800.0, 1200.0],
        hypothesis="Test hypothesis",
        confidence=0.85,
    )
    print(f"✓ RootCauseInsight: id={insight.anomaly_id}, confidence={insight.confidence}")

    print("\n" + "="*60)
    print("✓ ALL VALIDATION CHECKS PASSED")
    print("="*60)
    print("\nThe root cause analysis module is ready for use.")
    print("See example_usage.py for full examples.")

except Exception as e:
    print(f"\n✗ ERROR: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
