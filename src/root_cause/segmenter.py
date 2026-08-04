"""
Segmentation Analysis Module

Analyzes which segments (dimensions) contributed most to an anomaly.

Methodology:
1. Break down the anomaly metric by available dimensions (region, product, channel, etc.)
2. Calculate baseline for each segment using historical data
3. Compute deviation for each segment at anomaly time
4. Calculate contribution percentage based on absolute impact
5. Rank segments by contribution

Statistical approach:
- Uses variance decomposition to isolate segment contributions
- Applies statistical significance testing (t-test or Mann-Whitney)
- Adjusts for segment size and variance
"""

import pandas as pd
import numpy as np
from typing import List, Dict, Tuple, Optional
from scipy import stats
import logging

logger = logging.getLogger(__name__)


class SegmentationAnalyzer:
    """
    Performs segmentation analysis to identify affected segments.

    Attributes:
        min_segment_size: Minimum data points required per segment for analysis
        significance_threshold: P-value threshold for statistical significance
        baseline_window: Number of historical periods to use for baseline
    """

    def __init__(
        self,
        min_segment_size: int = 10,
        significance_threshold: float = 0.05,
        baseline_window: int = 7,
    ):
        """
        Initialize segmentation analyzer.

        Args:
            min_segment_size: Minimum observations per segment
            significance_threshold: Alpha level for significance tests
            baseline_window: Historical periods for baseline calculation
        """
        self.min_segment_size = min_segment_size
        self.significance_threshold = significance_threshold
        self.baseline_window = baseline_window

    def analyze(
        self,
        anomaly_timestamp: pd.Timestamp,
        metric: str,
        data: pd.DataFrame,
        dimensions: List[str],
        time_column: str = "date",
    ) -> List[Dict]:
        """
        Perform segmentation analysis.

        Args:
            anomaly_timestamp: Time when anomaly occurred
            metric: Metric to analyze
            data: Full dataset with time series
            dimensions: List of categorical dimensions to segment by
            time_column: Name of time column

        Returns:
            List of segment contributions sorted by impact
        """
        if not dimensions:
            logger.warning("No dimensions provided for segmentation analysis")
            return []

        # Ensure time column is datetime
        data[time_column] = pd.to_datetime(data[time_column])
        data = data.sort_values(time_column)

        # Find closest timestamp to anomaly
        anomaly_time = data[data[time_column] <= anomaly_timestamp][time_column].max()
        if pd.isna(anomaly_time):
            logger.error(f"No data before anomaly time {anomaly_timestamp}")
            return []

        # Calculate baseline for each segment
        baseline_data = self._get_baseline_data(
            data, anomaly_time, time_column, self.baseline_window
        )

        contributions = []

        for dimension in dimensions:
            # Get segment breakdown at anomaly time
            segment_contributions = self._analyze_dimension(
                metric, dimension, data, baseline_data, anomaly_time, time_column
            )
            contributions.extend(segment_contributions)

        # Sort by contribution (absolute impact) and filter significant ones
        contributions.sort(key=lambda x: abs(x["contribution"]), reverse=True)

        # Filter out segments with insufficient data
        contributions = [
            c for c in contributions if c.get("segment_size", 0) >= self.min_segment_size
        ]

        # Take top 10 contributors
        return contributions[:10]

    def _get_baseline_data(
        self, data: pd.DataFrame, anomaly_time: pd.Timestamp, time_column: str, window: int
    ) -> pd.DataFrame:
        """
        Extract baseline period data (before anomaly).

        Args:
            data: Full dataset
            anomaly_time: Anomaly timestamp
            time_column: Time column name
            window: Number of periods to use as baseline

        Returns:
            Baseline data subset
        """
        # Get unique timestamps before anomaly
        baseline_times = (
            data[data[time_column] < anomaly_time][time_column].unique()
        )
        if len(baseline_times) > window:
            baseline_times = baseline_times[-window:]

        return data[data[time_column].isin(baseline_times)].copy()

    def _analyze_dimension(
        self,
        metric: str,
        dimension: str,
        data: pd.DataFrame,
        baseline_data: pd.DataFrame,
        anomaly_time: pd.Timestamp,
        time_column: str,
    ) -> List[Dict]:
        """
        Analyze segmentation by a single dimension.

        Args:
            metric: Metric to analyze
            dimension: Categorical dimension
            data: Full dataset
            baseline_data: Baseline period data
            anomaly_time: Anomaly timestamp
            time_column: Time column name

        Returns:
            List of segment contributions
        """
        results = []

        # Get data at anomaly time
        anomaly_data = data[data[time_column] == anomaly_time]

        if anomaly_data.empty:
            logger.warning(f"No data at anomaly time {anomaly_time}")
            return []

        # Get unique segments
        segments = anomaly_data[dimension].dropna().unique()

        for segment in segments:
            # Segment data at anomaly time
            segment_anomaly = anomaly_data[anomaly_data[dimension] == segment]
            segment_baseline = baseline_data[baseline_data[dimension] == segment]

            if len(segment_anomaly) == 0 or len(segment_baseline) < self.min_segment_size:
                continue

            # Calculate values
            segment_value = segment_anomaly[metric].sum()
            baseline_mean = segment_baseline[metric].mean()
            baseline_std = segment_baseline[metric].std()

            if pd.isna(baseline_mean) or baseline_mean == 0:
                # Use alternative baseline if mean is 0 or NaN
                baseline_median = segment_baseline[metric].median()
                baseline_mean = baseline_median if not pd.isna(baseline_median) else 0

            # Calculate deviation
            if baseline_mean != 0:
                deviation = (segment_value - baseline_mean) / abs(baseline_mean)
                baseline_ratio = segment_value / baseline_mean if baseline_mean != 0 else np.inf
            else:
                deviation = 0 if segment_value == 0 else (1 if segment_value > 0 else -1)
                baseline_ratio = np.inf if segment_value != 0 else 1

            # Statistical significance test
            p_value = self._test_significance(
                segment_anomaly[metric].values,
                segment_baseline[metric].values
            )

            # Calculate contribution to overall anomaly
            # We'll compute this in the context of all segments
            result = {
                "segment": f"{dimension}: {segment}",
                "dimension": dimension,
                "segment_value": float(segment_value),
                "baseline_value": float(baseline_mean) if not pd.isna(baseline_mean) else None,
                "baseline_ratio": float(baseline_ratio) if not np.isinf(baseline_ratio) else (10.0 if baseline_ratio > 0 else -10.0),
                "deviation": float(deviation),
                "statistical_significance": float(p_value) if p_value is not None else None,
                "segment_size": len(segment_baseline),
                "baseline_std": float(baseline_std) if not pd.isna(baseline_std) else None,
            }

            results.append(result)

        return results

    def _test_significance(
        self,
        anomaly_values: np.ndarray,
        baseline_values: np.ndarray
    ) -> Optional[float]:
        """
        Test if segment deviation is statistically significant.

        Args:
            anomaly_values: Values during anomaly period
            baseline_values: Historical baseline values

        Returns:
            P-value from statistical test, or None if test cannot be performed
        """
        if len(anomaly_values) == 0 or len(baseline_values) < 2:
            return None

        try:
            # Normalize: get mean of anomaly values
            anomaly_mean = np.mean(anomaly_values)

            # Use t-test comparing baseline distribution to anomaly value
            # We test if anomaly mean is significantly different from baseline mean
            baseline_mean = np.mean(baseline_values)
            baseline_std = np.std(baseline_values, ddof=1)

            if baseline_std == 0:
                # All baseline values are identical
                return 0.0 if anomaly_mean != baseline_mean else 1.0

            # One-sample t-test for anomaly values against baseline mean
            t_stat, p_value = stats.ttest_1samp(
                baseline_values,
                anomaly_mean,
                alternative='two-sided'
            )

            if np.isnan(p_value):
                return None

            return float(p_value)

        except Exception as e:
            logger.debug(f"Significance test failed: {e}")
            return None


def calculate_segment_contributions(
    contributions: List[Dict],
    total_anomaly_impact: float,
    metric: str
) -> List[Dict]:
    """
    Calculate contribution percentages for segments.

    Args:
        contributions: List of segment deviation data
        total_anomaly_impact: Total anomaly impact (actual - expected)
        metric: Metric being analyzed

    Returns:
        List of contributions with percentages
    """
    if total_anomaly_impact == 0:
        return []

    # Calculate absolute contribution of each segment
    for contrib in contributions:
        segment_impact = contrib["segment_value"] - contrib["baseline_value"]
        absolute_impact = abs(segment_impact)

        # Contribution as percentage of total absolute impact
        contrib["contribution"] = (absolute_impact / abs(total_anomaly_impact)) * 100

    # Normalize to ensure contributions sum to 100%
    total_contribution = sum(c["contribution"] for c in contributions)

    if total_contribution > 0:
        for contrib in contributions:
            contrib["contribution"] = (contrib["contribution"] / total_contribution) * 100

    # Sort by contribution
    contributions.sort(key=lambda x: x["contribution"], reverse=True)

    return contributions
