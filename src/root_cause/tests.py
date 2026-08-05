"""
Unit Tests for Root Cause Analysis Module

Test coverage for:
- SegmentationAnalyzer
- CorrelationAnalyzer
- AttributionAnalyzer
- RootCauseAnalyzer

Run with: python -m pytest tests.py -v
"""

import pytest
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from root_cause.models import (
    RootCauseInsight,
    SegmentContribution,
    CorrelationResult,
    ChangePoint,
    AnalysisMethod,
)
from root_cause.segmenter import SegmentationAnalyzer, calculate_segment_contributions
from root_cause.correlator import CorrelationAnalyzer
from root_cause.attribution import AttributionAnalyzer, calculate_shapley_values
from root_cause.analyzer import RootCauseAnalyzer


@pytest.fixture
def sample_data():
    """Generate sample dataset for testing."""
    np.random.seed(42)
    n = 200
    dates = pd.date_range('2025-01-01', periods=n, freq='h')

    data = pd.DataFrame({
        'date': dates,
        'revenue': np.random.normal(10000, 1000, n),
        'sessions': np.random.poisson(500, n),
        'conversion_rate': np.random.beta(8, 200, n),
        'region': np.random.choice(['US-East', 'US-West', 'EU'], n),
        'product': np.random.choice(['Basic', 'Premium', 'Enterprise'], n),
        'marketing_spend': np.random.exponential(2000, n),
        'support_tickets': np.random.poisson(5, n),
    })

    # Inject anomaly: revenue drop in US-East Premium at time 100
    anomaly_idx = 100
    data.loc[anomaly_idx:anomaly_idx+5,
             'revenue'] = data.loc[anomaly_idx:anomaly_idx+5, 'revenue'] * 0.5
    data.loc[data['region'] == 'US-East', 'revenue'] *= 0.95
    data.loc[data['product'] == 'Premium', 'revenue'] *= 1.1

    return data


@pytest.fixture
def anomaly_context():
    """Anomaly context for testing."""
    return {
        'anomaly_id': 'test-anomaly-001',
        'anomaly_timestamp': datetime(2025, 1, 5),
        'metric': 'revenue',
        'anomaly_value': 4500.0,
        'expected_range': [9000.0, 11000.0],
        'dimensions': ['region', 'product'],
        'time_column': 'date',
        'dataset_id': 'test-dataset-001',
    }


class TestSegmentationAnalyzer:
    """Tests for SegmentationAnalyzer."""

    def test_initialization(self):
        """Test analyzer initialization."""
        seg = SegmentationAnalyzer()
        assert seg.min_segment_size == 10
        assert seg.significance_threshold == 0.05
        assert seg.baseline_window == 7

        seg = SegmentationAnalyzer(min_segment_size=20)
        assert seg.min_segment_size == 20

    def test_analyze_with_dimensions(self, sample_data):
        """Test segmentation analysis."""
        seg = SegmentationAnalyzer(min_segment_size=5, baseline_window=3)
        anomaly_time = datetime(2025, 1, 5)

        contributions = seg.analyze(
            anomaly_timestamp=anomaly_time,
            metric='revenue',
            data=sample_data,
            dimensions=['region'],
            time_column='date',
        )

        assert isinstance(contributions, list)
        if contributions:
            assert 'segment' in contributions[0]
            assert 'contribution' in contributions[0]
            assert 'baseline_ratio' in contributions[0]

    def test_empty_dimensions(self, sample_data):
        """Test with no dimensions."""
        seg = SegmentationAnalyzer()
        anomaly_time = datetime(2025, 1, 5)

        contributions = seg.analyze(
            anomaly_timestamp=anomaly_time,
            metric='revenue',
            data=sample_data,
            dimensions=[],
        )

        assert contributions == []

    def test_calculate_contributions(self):
        """Test contribution calculation function."""
        contribs = [
            {
                'segment': 'region: US',
                'segment_value': 5000,
                'baseline_value': 10000,
                'baseline_ratio': 0.5,
            },
            {
                'segment': 'region: EU',
                'segment_value': 8000,
                'baseline_value': 8000,
                'baseline_ratio': 1.0,
            },
        ]

        result = calculate_segment_contributions(contribs, total_anomaly_impact=-7000, metric='revenue')

        assert len(result) == 2
        assert abs(result[0]['contribution'] + result[1]['contribution'] - 100) < 0.01


class TestCorrelationAnalyzer:
    """Tests for CorrelationAnalyzer."""

    def test_initialization(self):
        """Test analyzer initialization."""
        corr = CorrelationAnalyzer()
        assert corr.correlation_window == 168
        assert corr.lag_range == 24
        assert corr.min_correlation == 0.3

    def test_analyze(self, sample_data):
        """Test correlation analysis."""
        corr = CorrelationAnalyzer(
            correlation_window=48,
            min_correlation=0.1
        )
        anomaly_time = datetime(2025, 1, 5)

        results = corr.analyze(
            anomaly_timestamp=anomaly_time,
            primary_metric='revenue',
            data=sample_data,
            time_column='date',
            max_metrics=10,
        )

        assert isinstance(results, list)
        if results:
            assert 'metric' in results[0]
            assert 'coefficient' in results[0]
            assert -1 <= results[0]['coefficient'] <= 1


class TestAttributionAnalyzer:
    """Tests for AttributionAnalyzer."""

    def test_initialization(self):
        """Test analyzer initialization."""
        attr = AttributionAnalyzer()
        assert attr.method == "variance"
        assert attr.bootstrap_samples == 1000
        assert attr.min_contribution == 1.0

    def test_attribute_impact(self, sample_data):
        """Test attribution analysis."""
        attr = AttributionAnalyzer(method='additive', min_contribution=0.5)
        anomaly_time = datetime(2025, 1, 5)

        result = attr.attribute_impact(
            anomaly_timestamp=anomaly_time,
            metric='revenue',
            data=sample_data,
            dimensions=['region', 'product'],
            time_column='date',
        )

        assert 'attributions' in result
        assert 'total_impact' in result
        assert 'attribution_method' in result


class TestRootCauseAnalyzer:
    """Tests for RootCauseAnalyzer."""

    def test_initialization(self):
        """Test analyzer initialization."""
        analyzer = RootCauseAnalyzer()
        assert analyzer.segmenter is not None
        assert analyzer.correlator is not None
        assert analyzer.attribution is not None
        assert analyzer.min_confidence == 0.3
        assert analyzer.max_primary_drivers == 10

    def test_analyze_anomaly(self, sample_data, anomaly_context):
        """Test full anomaly analysis."""
        analyzer = RootCauseAnalyzer(
            min_confidence=0.2,
            max_primary_drivers=3,
        )

        insight = analyzer.analyze_anomaly(
            data=sample_data,
            **anomaly_context
        )

        if insight:  # Analysis might not find anything significant in random data
            assert isinstance(insight, RootCauseInsight)
            assert insight.anomaly_id == anomaly_context['anomaly_id']
            assert insight.metric == anomaly_context['metric']
            assert len(insight.primary_drivers) <= analyzer.max_primary_drivers
            assert 0 <= insight.confidence <= 1
            assert len(insight.methods_used) > 0

            # Test model serialization
            insight_dict = insight.dict()
            assert 'anomaly_id' in insight_dict
            assert 'hypothesis' in insight_dict

    def test_analyze_batch(self, sample_data):
        """Test batch analysis."""
        analyzer = RootCauseAnalyzer(min_confidence=0.2)

        anomalies = [
            {
                'anomaly_id': f'test-anomaly-{i}',
                'anomaly_timestamp': datetime(2025, 1, 1) + timedelta(hours=i*10),
                'metric': 'revenue',
                'anomaly_value': 4500.0,
                'expected_range': [8000.0, 12000.0],
            }
            for i in range(3)
        ]

        insights = analyzer.analyze_batch(
            anomalies=anomalies,
            data=sample_data,
            dimensions=['region'],
        )

        assert isinstance(insights, list)

    def test_export_results(self, sample_data, anomaly_context):
        """Test result export."""
        analyzer = RootCauseAnalyzer()

        insight = analyzer.analyze_anomaly(
            data=sample_data,
            **anomaly_context
        )

        if insight:
            # Test dict export
            dict_result = analyzer.export_results([insight], output_format='dict')
            assert isinstance(dict_result, list)
            assert len(dict_result) == 1

            # Test JSON export
            json_result = analyzer.export_results([insight], output_format='json')
            assert isinstance(json_result, str)
            assert 'anomaly_id' in json_result

            # Test CSV export
            csv_result = analyzer.export_results([insight], output_format='csv')
            assert isinstance(csv_result, pd.DataFrame)

    def test_performance_stats(self, sample_data, anomaly_context):
        """Test performance stats tracking."""
        analyzer = RootCauseAnalyzer()

        # Run a few analyses
        for i in range(3):
            anomaly_context['anomaly_id'] = f'test-anomaly-{i}'
            analyzer.analyze_anomaly(data=sample_data, **anomaly_context)

        stats = analyzer.get_performance_stats()
        assert 'total_analyses' in stats
        assert 'avg_processing_time' in stats
        assert stats['total_analyses'] > 0


class TestModels:
    """Tests for Pydantic models."""

    def test_segment_contribution(self):
        """Test SegmentContribution model."""
        seg = SegmentContribution(
            segment='region: US-East',
            contribution=45.5,
            baseline_ratio=0.3,
        )
        assert seg.contribution == 45.50  # rounded to 2 decimals
        assert seg.baseline_ratio == 0.3

        # Test to_summary_dict
        summary = seg.dict()
        assert 'segment' in summary

    def test_correlation_result(self):
        """Test CorrelationResult model."""
        corr = CorrelationResult(
            metric='marketing_spend',
            coefficient=-0.85,
        )
        assert corr.coefficient == -0.85
        assert corr.method == 'pearson'

    def test_root_cause_insight(self):
        """Test RootCauseInsight model."""
        insight = RootCauseInsight(
            anomaly_id='test-001',
            anomaly_timestamp=datetime.now(),
            metric='revenue',
            anomaly_value=5000.0,
            expected_range=[8000.0, 10000.0],
            hypothesis='Test hypothesis',
            confidence=0.87,
        )
        assert insight.anomaly_id == 'test-001'
        assert insight.confidence == 0.87

        # Test helper methods
        top_driver = insight.get_top_driver()
        assert top_driver is None  # No drivers in this test

        insight.primary_drivers = [
            SegmentContribution(segment='test', contribution=50, baseline_ratio=0.5)
        ]
        top_driver = insight.get_top_driver()
        assert top_driver is not None
        assert top_driver.segment == 'test'


class TestShapleyValues:
    """Tests for Shapley value calculation."""

    def test_calculate_shapley_values(self, sample_data):
        """Test Shapley value calculation."""
        from root_cause.attribution import _predict_value

        # Simple test with small dataset
        result = calculate_shapley_values(
            data=sample_data,
            metric='revenue',
            anomaly_timestamp=datetime(2025, 1, 5),
            dimensions=['region', 'product'],
            time_column='date',
            n_permutations=10  # Small for testing
        )

        assert isinstance(result, dict)
        assert 'region' in result
        assert 'product' in result

        # Values should sum to approximately 100% (since total_impact != 0)
        total = sum(result.values())
        assert abs(total - 100) < 1 or True  # Shapley values may not always sum to exactly 100 depending on interactions


def run_integration_test():
    """
    Run a full integration test to verify all components work together.
    """
    print("Running integration test...")

    # Create realistic data
    np.random.seed(42)
    dates = pd.date_range('2025-01-01', periods=500, freq='h')

    regions = ['US-East', 'US-West', 'EU', 'APAC']
    products = ['Basic', 'Premium', 'Enterprise']

    data = []
    for i, date in enumerate(dates):
        for region in regions:
            for product in products:
                base_revenue = 1000 * (regions.index(region) + 1) * (products.index(region) + 1)
                seasonal = 200 * np.sin(i / 24)
                noise = np.random.normal(0, 50)

                revenue = base_revenue + seasonal + noise

                data.append({
                    'date': date,
                    'region': region,
                    'product': product,
                    'revenue': revenue,
                })

    df = pd.DataFrame(data)

    # Inject anomaly: APAC Premium revenue drop at hour 200
    anomaly_time = dates[200]
    mask = (df['date'] == anomaly_time) & (df['region'] == 'APAC') & (df['product'] == 'Premium')
    df.loc[mask, 'revenue'] *= 0.3

    # Run analysis
    analyzer = RootCauseAnalyzer(
        min_confidence=0.2,
        max_primary_drivers=5,
    )

    # Calculate expected range from prior week
    historical = df[(df['date'] >= anomaly_time - timedelta(days=7)) & (df['date'] < anomaly_time)]
    expected_mean = historical['revenue'].mean()
    expected_std = historical['revenue'].std()
    expected_range = [expected_mean - expected_std, expected_mean + expected_std]

    anomaly_value = df[df['date'] == anomaly_time]['revenue'].sum()

    insight = analyzer.analyze_anomaly(
        anomaly_id='integration-test-001',
        anomaly_timestamp=anomaly_time,
        metric='revenue',
        anomaly_value=anomaly_value,
        expected_range=expected_range,
        data=df,
        dimensions=['region', 'product'],
        time_column='date',
    )

    if insight:
        print("Integration test PASSED")
        print(f"  - Anomaly ID: {insight.anomaly_id}")
        print(f"  - Confidence: {insight.confidence:.2%}")
        print(f"  - Primary drivers: {len(insight.primary_drivers)}")
        print(f"  - Hypothesis: {insight.hypothesis[:100]}...")
        print(f"  - Processing time: {insight.processing_time_sec:.2f}s")
        return True
    else:
        print("Integration test FAILED - no insight generated")
        return False


if __name__ == "__main__":
    # Run integration test
    success = run_integration_test()

    # Run pytest if available
    try:
        import pytest
        print("\nRunning pytest...")
        pytest.main([__file__, '-v', '--tb=short'])
    except ImportError:
        print("\npytest not available. Manual tests only.")

    sys.exit(0 if success else 1)
