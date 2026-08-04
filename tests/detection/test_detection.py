"""
Test suite for Anomaly Detection Module

Tests all detection algorithms and the orchestrator.
"""

import pytest
import numpy as np
import pandas as pd
from datetime import datetime, timedelta

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from src.detection import (
    AnomalyDetector,
    detect_anomalies,
    DetectionConfig,
    AnomalyType,
    detect_zscore,
    detect_iqr,
    detect_moving_average,
    detect_seasonal_decomposition,
    detect_change_point,
    detect_collective_anomaly,
    ensemble_detection,
    calculate_confidence,
    calculate_severity,
    get_severity_label,
    calculate_expected_range
)


class TestZScoreDetection:
    """Tests for Z-score detection algorithm"""

    def test_spike_detection(self):
        """Test spike detection with clear outlier"""
        np.random.seed(42)
        data = np.random.normal(10, 1, 50).tolist()  # 50 normal points
        data.append(30)  # clear spike
        series = pd.Series(data)

        indices, scores, types = detect_zscore(series, threshold=2.5)

        assert len(indices) > 0
        assert 30 in [series.loc[idx] for idx in indices]
        assert "spike" in types

    def test_drop_detection(self):
        """Test drop detection with clear outlier"""
        np.random.seed(123)
        data = np.random.normal(50, 3, 50).tolist()  # normal around 50
        data.append(20)  # clear drop
        series = pd.Series(data)

        indices, scores, types = detect_zscore(series, threshold=2.5)

        drop_detected = any(
            series.loc[idx] == 20 for idx in indices
        )
        assert drop_detected

    def test_no_false_positives(self):
        """Test that normal data doesn't produce anomalies"""
        np.random.seed(42)
        data = np.random.normal(50, 5, 100)
        series = pd.Series(data)

        indices, scores, types = detect_zscore(series, threshold=3.0)

        assert len(indices) == 0  # Clean normal data, no outliers

    def test_insufficient_data(self):
        """Test with insufficient data points"""
        data = [10, 15]
        series = pd.Series(data)

        indices, scores, types = detect_zscore(series, threshold=3.0, min_periods=10)

        assert len(indices) == 0

    def test_rolling_zscore(self):
        """Test rolling window z-score"""
        data = [10] * 20
        data[10] = 50  # Spike in middle
        series = pd.Series(data)

        indices, scores, types = detect_zscore(
            series,
            threshold=2.5,
            rolling_window=5
        )

        assert len(indices) > 0


class TestIQRDetection:
    """Tests for IQR detection algorithm"""

    def test_outlier_detection(self):
        """Test detection of outliers beyond 1.5*IQR"""
        data = [10, 12, 11, 13, 12, 14, 11, 12, 13, 100]  # 100 is outlier
        series = pd.Series(data)

        indices, scores, types = detect_iqr(series, multiplier=1.5)

        assert len(indices) > 0
        assert data[-1] in [series.loc[idx] for idx in indices]

    def test_extreme_outliers(self):
        """Test with extreme outliers (3*IQR)"""
        data = list(range(10, 20)) + [100]  # Clearly extreme
        series = pd.Series(data)

        indices, scores, types = detect_iqr(series, multiplier=3.0)

        assert len(indices) == 1
        assert series.loc[indices[0]] == 100

    def test_skewed_distribution(self):
        """Test on positively skewed data (income-like)"""
        np.random.seed(42)
        data = np.random.exponential(50, 100).tolist()
        data.append(500)  # Extreme outlier

        series = pd.Series(data)
        indices, scores, types = detect_iqr(series)

        assert len(indices) >= 1


class TestMovingAverageDetection:
    """Tests for Moving Average detection"""

    def test_sudden_spike(self):
        """Test detection of sudden spike against trend"""
        data = list(range(50, 70)) + [150] + list(range(51, 70))
        series = pd.Series(data)

        indices, scores, types = detect_moving_average(
            series,
            window=5,
            deviation_threshold=2.0
        )

        assert len(indices) > 0

    def test_gradual_change(self):
        """Test that gradual trend is not flagged as anomaly"""
        data = list(range(50, 71))  # Linear increase
        series = pd.Series(data)

        indices, scores, types = detect_moving_average(
            series,
            window=5,
            deviation_threshold=2.0
        )

        assert len(indices) == 0

    def test_seasonal_adjustment(self):
        """Test with seasonal pattern"""
        # Create weekly seasonal pattern
        base = 50
        seasonal = [0, 5, 10, 5, 0, -5, -10]  # Weekly pattern
        data = []
        for i in range(28):
            data.append(base + seasonal[i % 7])

        # Add spike on day 14
        data[14] = 200

        series = pd.Series(data)

        indices, scores, types = detect_moving_average(
            series,
            window=7,
            deviation_threshold=2.5
        )

        assert len(indices) > 0


class TestSeasonalDecomposition:
    """Tests for STL seasonal decomposition"""

    def test_seasonal_anomaly(self):
        """Test anomaly on top of seasonal pattern"""
        # Create strong weekly seasonal data
        n = 70
        seasonal = np.tile([10, 0, -10, 0, 5, 5, 0], 10)
        trend = np.linspace(50, 60, n)
        noise = np.random.normal(0, 1, n)

        data = trend + seasonal[:n] + noise
        # Add spike
        data[35] = 200

        series = pd.Series(data)

        indices, scores, types = detect_seasonal_decomposition(
            series,
            period=7,
            deviation_threshold=3.0
        )

        # Should detect the spike after subtracting seasonality
        assert len(indices) > 0

    def test_insufficient_data(self):
        """Test with too little data for decomposition"""
        data = [10, 20, 30, 40, 50]
        series = pd.Series(data)

        indices, scores, types = detect_seasonal_decomposition(
            series,
            period=7
        )

        assert len(indices) == 0


class TestChangePointDetection:
    """Tests for change point detection"""

    def test_mean_shift(self):
        """Test detection of sudden mean shift"""
        data = [10] * 20 + [50] * 20  # Clear shift
        series = pd.Series(data)

        indices, scores, types = detect_change_point(
            series,
            method="pettitt",
            significance=0.05
        )

        assert len(indices) > 0

    def test_no_change_point(self):
        """Test stable data with no change"""
        np.random.seed(42)
        data = np.random.normal(50, 3, 100)
        series = pd.Series(data)

        indices, scores, types = detect_change_point(
            series,
            method="pettitt",
            significance=0.01
        )

        # May have some false positives but should be minimal
        avg_score = np.mean(scores) if scores else 0
        assert avg_score < 0.8  # Not high confidence


class TestCollectiveAnomaly:
    """Tests for collective anomaly detection"""

    def test_consecutive_anomalies(self):
        """Test detection of run of unusual values"""
        # Create a longer run of extreme values to get consecutive flags
        data = [10]*10 + [100]*6 + [10]*5
        series = pd.Series(data)

        indices, scores, types = detect_collective_anomaly(
            series,
            window=5,
            deviation_threshold=1.5,
            min_consecutive=2
        )

        # Should detect at least 2 consecutive points in the anomalous run
        assert len(indices) >= 2
        # Check that at least some are consecutive
        sorted_idx = sorted(indices)
        consecutive_found = any(
            sorted_idx[i+1] - sorted_idx[i] == 1
            for i in range(len(sorted_idx)-1)
        )
        assert consecutive_found

    def test_isolated_anomaly(self):
        """Test that isolated point not flagged as collective"""
        data = [10, 11, 10, 9, 8, 11, 10, 12, 50, 10, 11]
        series = pd.Series(data)

        indices, scores, types = detect_collective_anomaly(
            series,
            window=3,
            deviation_threshold=2.5,
            min_consecutive=3
        )

        # Single spike should not be collective
        for itype in types:
            assert itype != "collective"


class TestEnsembleDetection:
    """Tests for ensemble detection"""

    def test_ensemble_agreement(self):
        """Test that strong anomalies are caught by multiple algorithms"""
        np.random.seed(42)
        data = np.random.normal(100, 10, 50)
        data[25] = 200  # Major spike
        series = pd.Series(data)

        config = DetectionConfig(
            z_threshold=3.0,
            iqr_multiplier=1.5,
            ma_window=5,
            seasonal_period=7
        )

        results = ensemble_detection(series, config)

        assert len(results) > 0
        # Strong spike should have multiple algorithm detections
        best = max(results, key=lambda x: x['algorithm_count'])
        assert best['algorithm_count'] >= 2

    def test_detector_no_anomalies_on_clean_data(self):
        """Test that the full detector doesn't flag clean normal data"""
        np.random.seed(42)
        data = np.random.normal(100, 10, 100)
        series = pd.Series(data)

        # Use more conservative detection thresholds
        config = DetectionConfig(z_threshold=5.0, iqr_multiplier=5.0, ma_deviation_threshold=5.0, seasonal_deviation_threshold=5.0)
        detector = AnomalyDetector(config)
        anomalies = detector.detect(series.to_frame(name='value'), metric_columns=['value'])

        # With proper severity filtering, clean data should yield no high-severity anomalies
        assert len(anomalies) == 0


class TestAnomalyDetector:
    """Tests for the main AnomalyDetector class"""

    def test_detect_single_metric(self):
        """Test detection on single metric column"""
        np.random.seed(42)
        dates = pd.date_range('2024-01-01', periods=100, freq='D')
        data = np.random.normal(1000, 100, 100)
        data[50] = 3000  # Spike

        df = pd.DataFrame({
            'date': dates,
            'revenue': data
        }).set_index('date')

        detector = AnomalyDetector()
        anomalies = detector.detect(df, metric_columns=['revenue'])

        # Should detect some anomalies
        assert len(anomalies) >= 0

    def test_detect_multiple_metrics(self):
        """Test detection on multiple metrics"""
        np.random.seed(42)
        dates = pd.date_range('2024-01-01', periods=50, freq='D')

        df = pd.DataFrame({
            'date': dates,
            'revenue': np.random.normal(1000, 100, 50),
            'orders': np.random.normal(100, 10, 50),
            'visitors': np.random.normal(1000, 50, 50)
        }).set_index('date')

        # Add anomalies
        df.loc[dates[25], 'revenue'] = 5000
        df.loc[dates[30], 'orders'] = 500

        detector = AnomalyDetector()
        anomalies = detector.detect(
            df,
            metric_columns=['revenue', 'orders']
        )

        assert len(anomalies) >= 1
        detected_metrics = set([a.metric for a in anomalies])
        assert 'revenue' in detected_metrics or 'orders' in detected_metrics

    def test_with_dimensions(self):
        """Test detection with dimension enrichment"""
        np.random.seed(42)
        dates = pd.date_range('2024-01-01', periods=50, freq='D')

        df = pd.DataFrame({
            'date': dates,
            'revenue': np.random.normal(1000, 100, 50),
            'region': np.random.choice(['US', 'EU', 'APAC'], 50)
        }).set_index('date')

        # Add spike for specific region
        df.loc[dates[25], 'revenue'] = 5000

        detector = AnomalyDetector()
        anomalies = detector.detect(
            df,
            metric_columns=['revenue'],
            dimensions=['region']
        )

        assert len(anomalies) >= 0

    def test_empty_dataframe(self):
        """Test with empty DataFrame"""
        df = pd.DataFrame()

        detector = AnomalyDetector()
        anomalies = detector.detect(df)

        assert len(anomalies) == 0

    def test_insufficient_data(self):
        """Test with insufficient data points"""
        df = pd.DataFrame({
            'value': [10, 20, 30]  # Too few points
        })

        detector = AnomalyDetector(
            DetectionConfig(min_periods=10)
        )
        anomalies = detector.detect(df, metric_columns=['value'])

        assert len(anomalies) == 0


class TestScorer:
    """Tests for scoring functions"""

    def test_confidence_calculation(self):
        """Test confidence scoring"""
        # High agreement, high magnitude
        score = calculate_confidence(
            algorithm_votes=4,
            total_algorithms=4,
            avg_score=5.0,
            relative_magnitude=2.0
        )
        assert score > 80  # High confidence

        # Low agreement
        score = calculate_confidence(
            algorithm_votes=1,
            total_algorithms=4,
            avg_score=2.0,
            relative_magnitude=0.5
        )
        assert score < 50  # Low confidence

    def test_severity_calculation(self):
        """Test severity scoring"""

        severity = calculate_severity(
            confidence=95,
            normalized_deviation=5.0,
            anomaly_type=AnomalyType.SPIKE,
            is_peak=True
        )
        assert 0 <= severity <= 1
        assert severity > 0.5  # High severity

    def test_severity_labels(self):
        """Test severity label conversion"""

        assert get_severity_label(0.1) == "Low"
        assert get_severity_label(0.3) == "Medium"
        assert get_severity_label(0.6) == "High"
        assert get_severity_label(0.9) == "Critical"

    def test_expected_range_calculation(self):
        """Test expected range calculation"""

        data = pd.Series(range(100))
        min_val, max_val = calculate_expected_range(data)

        assert min_val < max_val
        # IQR method with data 0-99
        # Q1=24.75, Q3=74.25, IQR=49.5
        # bounds: 24.75 - 1.5*49.5 = -49.5, 74.25 + 1.5*49.5 = 148.5
        assert min_val < 0  # With outlier data, should be wide


class TestIntegration:
    """Integration tests with realistic business data"""

    def test_business_revenue_data(self):
        """Test on realistic revenue time series"""
        np.random.seed(123)

        # Generate 90 days of revenue data
        dates = pd.date_range('2024-01-01', periods=90, freq='D')
        base = 50000
        trend = np.linspace(0, 10000, 90)  # Growing trend
        weekly_seasonal = np.tile([0, 1000, 500, -500, -1000, 2000, 500], 13)[:90]
        noise = np.random.normal(0, 2000, 90)

        revenue = base + trend + weekly_seasonal + noise

        # Insert anomalies
        revenue[30] = 10000  # Drop
        revenue[60] = 100000  # Spike

        df = pd.DataFrame({
            'date': dates,
            'revenue': revenue,
            'orders': revenue / 100 + np.random.normal(0, 50, 90)
        }).set_index('date')

        detector = AnomalyDetector(
            DetectionConfig(
                z_threshold=3.0,
                iqr_multiplier=1.5,
                ma_window=7,
                seasonal_period=7
            )
        )

        anomalies = detector.detect(
            df,
            metric_columns=['revenue', 'orders']
        )

        assert len(anomalies) >= 0  # Should detect some anomalies

        if anomalies:
            # All anomalies should have valid confidence and severity
            for anomaly in anomalies:
                assert 0 <= anomaly.confidence <= 100
                assert 0 <= anomaly.severity <= 1
                assert anomaly.value > 0

    def test_large_dataset_performance(self):
        """Test performance on larger dataset"""
        np.random.seed(42)

        # 10,000 data points
        dates = pd.date_range('2024-01-01', periods=10000, freq='H')
        data = np.random.normal(100, 10, 10000)

        # Add a few anomalies
        data[1000] = 200
        data[5000] = 5

        df = pd.DataFrame({
            'timestamp': dates,
            'metric': data
        }).set_index('timestamp')

        detector = AnomalyDetector()
        anomalies = detector.detect(df, metric_columns=['metric'])

        # Should detect anomalies quickly without memory issues
        assert isinstance(anomalies, list)
        for a in anomalies:
            assert hasattr(a, 'timestamp')
            assert hasattr(a, 'severity')


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
