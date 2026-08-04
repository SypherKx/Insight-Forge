"""
Pydantic models for Root Cause Analysis.

These models define the structured output format for root cause insights.
"""

from datetime import datetime
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field, validator
from enum import Enum


class AnalysisMethod(str, Enum):
    """Enumeration of analysis methods."""
    SEGMENTATION = "segmentation"
    CORRELATION = "correlation"
    CHANGE_POINT = "change_point"
    ATTRIBUTION = "attribution"
    COMBINED = "combined"


class SegmentContribution(BaseModel):
    """
    Contribution of a specific segment to the anomaly.

    Attributes:
        segment: Segment identifier (e.g., "Region: US-East", "Product: Premium")
        contribution: Percentage contribution (0-100)
        baseline_ratio: Ratio of segment performance vs baseline (e.g., 0.3 = 70% below)
        segment_value: Actual value for this segment at anomaly time
        baseline_value: Expected baseline value for this segment
        statistical_significance: P-value for the deviation (if applicable)
        segment_size: Number of data points in this segment
    """
    segment: str = Field(..., description="Segment identifier with dimension and value")
    contribution: float = Field(..., ge=0, le=100, description="Percentage contribution to anomaly")
    baseline_ratio: float = Field(..., description="Ratio: segment_value / baseline_value")
    segment_value: Optional[float] = Field(None, description="Actual segment value")
    baseline_value: Optional[float] = Field(None, description="Expected baseline value")
    statistical_significance: Optional[float] = Field(None, ge=0, le=1, description="P-value")
    segment_size: Optional[int] = Field(None, description="Count of observations in segment")

    @validator('contribution')
    def round_contribution(cls, v):
        """Round contribution to 2 decimal places."""
        return round(v, 2)

    @validator('baseline_ratio')
    def round_baseline_ratio(cls, v):
        """Round baseline_ratio to 3 decimal places."""
        return round(v, 3)


class CorrelationResult(BaseModel):
    """
    Correlation between anomaly metric and another metric.

    Attributes:
        metric: Name of correlated metric
        coefficient: Pearson/Spearman correlation coefficient (-1 to 1)
        p_value: Statistical significance (0-1)
        lag_hours: Time lag in hours where correlation is strongest
        lag_direction: Whether correlated metric leads or lags anomaly
        sample_size: Number of data points used in correlation
        method: Correlation method used ('pearson' or 'spearman')
    """
    metric: str = Field(..., description="Name of correlated metric")
    coefficient: float = Field(..., ge=-1, le=1, description="Correlation coefficient")
    p_value: Optional[float] = Field(None, ge=0, le=1, description="Statistical significance")
    lag_hours: Optional[float] = Field(None, ge=0, description="Time lag in hours")
    lag_direction: Optional[str] = Field(None, description="'lead', 'lag', or 'synchronous'")
    sample_size: Optional[int] = Field(None, description="Number of data points")
    method: str = Field("pearson", description="Correlation method used")

    @validator('coefficient')
    def round_coefficient(cls, v):
        """Round coefficient to 3 decimal places."""
        return round(v, 3)

    @validator('p_value')
    def round_p_value(cls, v):
        """Round p_value to 4 decimal places."""
        if v is not None:
            return round(v, 4)
        return v


class ChangePoint(BaseModel):
    """
    Detected change point indicating when the anomaly started.

    Attributes:
        detected_at: Timestamp when change was detected
        confidence: Confidence score (0-1)
        method: Method used for change point detection
        before_mean: Mean value before change point
        after_mean: Mean value after change point
        before_std: Standard deviation before change point
        after_std: Standard deviation after change point
        change_magnitude: Relative change ((after - before) / before)
        statistical_test: Name of statistical test used
        test_statistic: Value of test statistic
        p_value: P-value of change point test
    """
    detected_at: datetime = Field(..., description="Timestamp of detected change")
    confidence: float = Field(..., ge=0, le=1, description="Confidence in detection")
    method: str = Field(..., description="Detection method used")
    before_mean: Optional[float] = Field(None, description="Mean before change")
    after_mean: Optional[float] = Field(None, description="Mean after change")
    before_std: Optional[float] = Field(None, description="Std dev before change")
    after_std: Optional[float] = Field(None, description="Std dev after change")
    change_magnitude: Optional[float] = Field(None, description="Relative change magnitude")
    statistical_test: Optional[str] = Field(None, description="Test name")
    test_statistic: Optional[float] = Field(None, description="Test statistic value")
    p_value: Optional[float] = Field(None, ge=0, le=1, description="Test p-value")

    @validator('confidence')
    def round_confidence(cls, v):
        """Round confidence to 3 decimal places."""
        return round(v, 3)

    @validator('change_magnitude')
    def round_change_magnitude(cls, v):
        """Round change_magnitude to 3 decimal places."""
        if v is not None:
            return round(v, 3)
        return v


class RootCauseInsight(BaseModel):
    """
    Complete root cause analysis for a single anomaly.

    Attributes:
        anomaly_id: Unique identifier of the anomaly
        anomaly_timestamp: When the anomaly occurred
        metric: The metric that showed anomalous behavior
        anomaly_value: The anomalous value
        expected_range: Expected range [min, max] for the metric
        primary_drivers: Ranked list of main contributors (sorted by impact)
        correlations: List of correlated metrics with coefficients
        change_point: Detected change point (if any)
        hypothesis: Natural language hypothesis summarizing findings
        confidence: Overall confidence score (0-1)
        methods_used: List of analysis methods applied
        supporting_evidence: Additional statistical evidence
        processing_time_sec: Time taken to perform analysis
        metadata: Additional context (dataset info, dimensions, etc.)
    """
    anomaly_id: str = Field(..., description="Unique anomaly identifier")
    anomaly_timestamp: datetime = Field(..., description="When anomaly occurred")
    metric: str = Field(..., description="Anomalous metric name")
    anomaly_value: float = Field(..., description="The anomalous value observed")
    expected_range: List[float] = Field(..., min_items=2, description="Expected [min, max]")
    primary_drivers: List[SegmentContribution] = Field(
        default=[], description="Ranked list of primary drivers"
    )
    correlations: List[CorrelationResult] = Field(
        default=[], description="Correlated metrics"
    )
    change_point: Optional[ChangePoint] = Field(None, description="Detected change point")
    hypothesis: str = Field(..., description="Narrative hypothesis of root cause")
    confidence: float = Field(..., ge=0, le=1, description="Overall confidence")
    methods_used: List[AnalysisMethod] = Field(
        default=[], description="Analysis methods applied"
    )
    supporting_evidence: Dict[str, Any] = Field(
        default_factory=dict, description="Additional statistical evidence"
    )
    processing_time_sec: Optional[float] = Field(None, description="Analysis duration")
    metadata: Dict[str, Any] = Field(
        default_factory=dict, description="Additional metadata"
    )

    @validator('confidence')
    def round_confidence(cls, v):
        """Round confidence to 3 decimal places."""
        return round(v, 3)

    @validator('expected_range')
    def validate_range(cls, v):
        """Ensure expected_range is [min, max] with min <= max."""
        if len(v) != 2:
            raise ValueError("expected_range must have exactly 2 elements")
        if v[0] > v[1]:
            raise ValueError("expected_range min must be <= max")
        return [round(v[0], 4), round(v[1], 4)]

    def get_top_driver(self) -> Optional[SegmentContribution]:
        """Get the top contributing driver."""
        return self.primary_drivers[0] if self.primary_drivers else None

    def get_strongest_correlation(self) -> Optional[CorrelationResult]:
        """Get the strongest absolute correlation."""
        if not self.correlations:
            return None
        return max(self.correlations, key=lambda c: abs(c.coefficient))

    def to_summary_dict(self) -> Dict[str, Any]:
        """Convert to summary dictionary for quick overview."""
        return {
            "anomaly_id": self.anomaly_id,
            "metric": self.metric,
            "anomaly_value": self.anomaly_value,
            "expected_range": self.expected_range,
            "top_driver": self.get_top_driver().dict() if self.get_top_driver() else None,
            "num_drivers": len(self.primary_drivers),
            "num_correlations": len(self.correlations),
            "hypothesis": self.hypothesis,
            "confidence": self.confidence,
            "has_change_point": self.change_point is not None,
        }
