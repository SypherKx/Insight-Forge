# Root Cause Analysis Module

## Overview

Production-ready root cause analysis engine for InsightForge AI. Implements statistical methods to determine why an anomaly occurred, with no LLM dependencies.

## Components

### 1. Segmentation Analyzer (`segmenter.py`)

Breaks down anomalies by categorical dimensions to identify affected segments.

**Methods:**
- Segment-level deviation from historical baseline
- Statistical significance testing (t-test)
- Contribution percentage calculation

**Key Class:** `SegmentationAnalyzer`

**Usage:**
```python
analyzer = SegmentationAnalyzer(min_segment_size=10, baseline_window=7)
contributions = analyzer.analyze(
    anomaly_timestamp=anomaly_time,
    metric='revenue',
    data=df,
    dimensions=['region', 'product', 'channel']
)
```

### 2. Correlation Analyzer (`correlator.py`)

Finds metrics that are correlated with the anomaly, including time lags.

**Methods:**
- Pearson and Spearman correlations
- Cross-correlation for lag detection
- Multiple testing correction (Benjamini-Hochberg)

**Key Class:** `CorrelationAnalyzer`

**Usage:**
```python
analyzer = CorrelationAnalyzer(
    correlation_window=168,  # 1 week of hourly data
    lag_range=24,  # Test up to 24 hours
    min_correlation=0.3
)
correlations = analyzer.analyze(
    anomaly_timestamp=anomaly_time,
    primary_metric='revenue',
    data=df,
    max_metrics=20
)
```

### 3. Attribution Analyzer (`attribution.py`)

Quantifies contribution of different factors to total anomaly impact.

**Methods:**
- Additive attribution
- Variance decomposition
- Shapley values for factor interactions
- Bootstrap confidence intervals

**Key Class:** `AttributionAnalyzer`

**Usage:**
```python
analyzer = AttributionAnalyzer(method='variance', bootstrap_samples=1000)
result = analyzer.attribute_impact(
    anomaly_timestamp=anomaly_time,
    metric='revenue',
    data=df,
    dimensions=['region', 'product', 'channel']
)
```

### 4. Root Cause Analyzer (`analyzer.py`)

Main orchestrator combining all methods.

**Key Class:** `RootCauseAnalyzer`

**Usage:**
```python
analyzer = RootCauseAnalyzer(
    min_confidence=0.3,
    max_primary_drivers=10,
    max_correlations=10
)

insight = analyzer.analyze_anomaly(
    anomaly_id='anomaly-001',
    anomaly_timestamp=anomaly_time,
    metric='revenue',
    anomaly_value=observed_value,
    expected_range=[min_expected, max_expected],
    data=df,
    dimensions=['region', 'product', 'channel'],
    time_column='date',
)
```

**Output:**
```python
RootCauseInsight(
    anomaly_id='anomaly-001',
    metric='revenue',
    anomaly_value=4500.0,
    expected_range=[8000.0, 10000.0],
    primary_drivers=[
        SegmentContribution(
            segment='region: APAC',
            contribution=67.5,  # % of total impact
            baseline_ratio=0.3  # 70% below baseline
        ),
        ...
    ],
    correlations=[
        CorrelationResult(
            metric='marketing_spend',
            coefficient=-0.82,
            p_value=0.001,
            lag_hours=2,
            lag_direction='lead'  # marketing drop led revenue drop
        ),
    ],
    hypothesis='Revenue drop driven by APAC region underperformance, correlated with reduced marketing spend.',
    confidence=0.87,
    methods_used=['segmentation', 'correlation', 'change_point'],
    supporting_evidence={
        'total_segments_analyzed': 12,
        'num_significant_segments': 2,
        'correlation_analysis': {
            'num_correlations_found': 3,
            'strongest_correlation': 0.82,
        },
    },
    processing_time_sec=2.34,
)
```

## Data Requirements

The `data` DataFrame should contain:
- `time_column`: Datetime column for time series
- `metric`: Numeric column being analyzed
- `dimensions`: Categorical columns for segmentation
- Additional numeric columns for correlation analysis

## Statistical Methods

### Segmentation
- Baseline calculation: rolling N-period mean
- Deviation: `(value - baseline) / abs(baseline)`
- Significance: One-sample t-test against baseline distribution
- Contribution: `|segment_impact| / Σ|all_segments_impact|`

### Correlation
- Pearson for linear relationships
- Spearman for monotonic relationships
- Cross-correlation for time lags (FFT-based)
- Multiple testing: Benjamini-Hochberg FDR

### Attribution
- Additive method: Direct contribution by segment
- Variance method: ANOVA-style decomposition
- Shapley values: Game theory for interactions
- Bootstrap CIs: Resampling for confidence intervals

### Change Point
- Pettitt test for single change point
- CUSUM alternative
- Significance testing

## Performance

Typical analysis times on 100K rows with 3 dimensions:
- Segmentation: 0.5-1 second
- Correlation: 1-2 seconds
- Attribution: 0.5-1 seconds
- **Total: 2-4 seconds** (excluding I/O)

## Error Handling

All methods include:
- Missing data handling (NaN imputation where appropriate)
- Minimum sample size checks
- Constant series detection
- Exception trapping with logging

Return `None` or empty lists when analysis cannot be performed.

## Configuration

Adjust parameters in initializers:

**SegmentationAnalyzer:**
- `min_segment_size`: Minimum observations per segment (default: 10)
- `baseline_window`: Historical periods for baseline (default: 7)
- `significance_threshold`: Alpha level (default: 0.05)

**CorrelationAnalyzer:**
- `correlation_window`: Data points used (default: 168)
- `lag_range`: Maximum lag to test (default: 24)
- `min_correlation`: Minimum |r| to report (default: 0.3)

**AttributionAnalyzer:**
- `method`: 'additive', 'variance', or 'interaction' (default: 'variance')
- `bootstrap_samples`: For confidence intervals (default: 1000)

**RootCauseAnalyzer:**
- `min_confidence`: Output threshold (default: 0.3)
- `max_primary_drivers`: Limit results (default: 10)
- `max_correlations`: Limit results (default: 10)

## Testing

Run tests:
```bash
pytest tests.py -v
```

Run integration test:
```bash
python tests.py  # runs integration test then pytest
```

## Dependencies

```txt
pandas>=2.0.0
numpy>=1.24.0
scipy>=1.10.0
pydantic>=2.4.0
```

Install:
```bash
pip install -r requirements.txt
```

## Production Considerations

### Scalability
- All methods are vectorized with NumPy/pandas
- Memory usage scales with data size (consider chunking for >1M rows)
- Cache segmentation results if analyzing many anomalies on same dataset

### Monitoring
- `processing_time_sec` in output for performance tracking
- `analyzer.get_performance_stats()` for cumulative metrics
- Comprehensive logging at DEBUG level

### Accuracy
- Statistical significance thresholds are configurable
- Multiple testing correction controls false discovery rate
- Bootstrap CI provides uncertainty quantification
- Shapley values handle interaction effects correctly

## Limitations

1. **Causality**: Statistical correlation ≠ causation. Identifies patterns, not mechanisms.
2. **Multiple Comparisons**: Many hypotheses tested simultaneously. BH correction helps but doesn't eliminate false discoveries.
3. **Time Series Structure**: Assumes some independence. Strong autocorrelation may inflate significance.
4. **Segments**: Requires sufficient data per segment. Small segments dropped.
5. **Lag Detection**: Limited to fixed range. Long lags (>lag_range) not detected.

## Future Enhancements

- Causal inference with DoWhy library
- Granger causality for time series
- Bayesian hierarchical models for partial pooling
- Changepoint ensemble (multiple methods)
- Interactive mode with progressive refinement

## License

Part of InsightForge AI. See project license.

## References

- Pettitt, A.N. (1979). "A non-parametric approach to the change-point problem."
- Benjamini, Y., & Hochberg, Y. (1995). "Controlling the false discovery rate."
- Shapley, L.S. (1953). "A Value for n-Person Games."
