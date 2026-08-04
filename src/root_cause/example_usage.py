"""
Example Usage: Root Cause Analysis for Anomaly Detection

This example demonstrates how to use the Root Cause Analysis module
in a typical anomaly investigation workflow.

Prerequisites:
    pip install pandas numpy scipy pydantic

Example data structure should have:
- timestamp column (datetime)
- metric of interest (numeric)
- dimension columns (categorical: region, product, channel, etc.)
- related metrics (for correlation analysis)
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
# For running from within the src/root_cause directory
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from root_cause import RootCauseAnalyzer, SegmentationAnalyzer, CorrelationAnalyzer, AttributionAnalyzer


def generate_sample_data(
    n_days: int = 90,
    hourly: bool = True,
    anomaly_day: int = 60
):
    """
    Generate synthetic e-commerce dataset with a revenue anomaly.

    Args:
        n_days: Number of days of data
        hourly: Whether to use hourly or daily frequency
        anomaly_day: Day when anomaly occurs

    Returns:
        DataFrame with synthetic data
    """
    freq = 'H' if hourly else 'D'
    periods = n_days * 24 if hourly else n_days

    # Date range
    start_date = datetime(2025, 1, 1)
    dates = pd.date_range(start=start_date, periods=periods, freq=freq)

    # Base trends
    trend = np.linspace(10000, 15000, periods)
    seasonal_daily = 2000 * np.sin(2 * np.pi * np.arange(periods) / 24)  # Daily pattern
    seasonal_weekly = 1500 * np.sin(2 * np.pi * np.arange(periods) / (24 * 7))  # Weekly pattern

    # Dimensions
    regions = ['US-East', 'US-West', 'EU-West', 'APAC']
    products = ['Basic', 'Standard', 'Premium']
    channels = ['Web', 'Mobile', 'Direct']

    # Generate baseline data per segment
    data = []

    for region_idx, region in enumerate(regions):
        for product_idx, product in enumerate(products):
            for channel_idx, channel in enumerate(channels):
                # Segment base value (region/product/channel combination)
                region_factor = 0.7 + (region_idx * 0.2)
                product_factor = 0.5 + (product_idx * 0.25)
                channel_factor = 0.8 + (channel_idx * 0.1)

                # Generate time series
                for i, date in enumerate(dates):
                    # Base value with trends and seasonality
                    base = (
                        trend[i] *
                        region_factor *
                        product_factor *
                        channel_factor * 0.5
                    )

                    # Add seasonality
                    base += seasonal_daily[i % 24] * region_factor
                    base += seasonal_weekly[i % (24 * 7)] * product_factor

                    # Random noise
                    noise = np.random.normal(0, base * 0.05)

                    revenue = max(0, base + noise)

                    # Create a spike anomaly for specific segments on anomaly_day
                    anomaly_effect = 0
                    if i >= anomaly_day * 24 and i < (anomaly_day + 1) * 24:
                        # Affected: APAC region, Premium product, Web channel
                        if (region == 'APAC-Lite' if hourly else 'APAC' and
                            product == 'Premium' and
                            channel == 'Web'):
                            anomaly_effect = revenue * (-0.7)  # 70% drop

                    data.append({
                        'date': date,
                        'region': region,
                        'product': product,
                        'channel': channel,
                        'revenue': revenue + anomaly_effect,
                        'sessions': int(revenue / 25 + np.random.randint(50, 200)),
                        'conversions': int(revenue / 100 + np.random.randint(10, 50)),
                        'marketing_spend': revenue * 0.15 + np.random.normal(0, 100),
                        'support_tickets': int(np.random.exponential(10)),
                    })

    df = pd.DataFrame(data)

    # Add derived metrics
    df['conversion_rate'] = df['conversions'] / df['sessions'].clip(1)
    df['revenue_per_session'] = df['revenue'] / df['sessions'].clip(1)

    return df


def main():
    """
    Main example demonstrating root cause analysis workflow.
    """
    print("=" * 80)
    print("InsightForge AI - Root Cause Analysis Example")
    print("=" * 80)
    print()

    # Step 1: Generate synthetic data
    print("Step 1: Generating synthetic e-commerce dataset...")
    data = generate_sample_data(n_days=90, hourly=True, anomaly_day=60)
    print(f"Generated {len(data)} rows across {data['date'].nunique()} hours")
    print(f"Dimensions: region={data['region'].nunique()}, product={data['product'].nunique()}, channel={data['channel'].nunique()}")
    print()

    # Step 2: Identify anomaly
    # We know from generation that anomaly is on day 60
    anomaly_date = datetime(2025, 1, 1) + timedelta(days=60)
    print(f"Step 2: Simulating anomaly detection result on {anomaly_date.date()}")
    print("Metric: revenue dropped significantly")
    print()

    # Calculate anomaly value (at anomaly time, all segments combined)
    anomaly_hour = data[data['date'] == anomaly_date]['revenue'].sum()
    # Expected range from historical (days 50-59)
    historical = data[(data['date'] >= anomaly_date - timedelta(days=7)) & (data['date'] < anomaly_date)]
    expected_mean = historical['revenue'].mean()
    expected_std = historical['revenue'].std()
    expected_range = [expected_mean - expected_std, expected_mean + expected_std]

    print(f"Anomaly value: {anomaly_hour:,.2f}")
    print(f"Expected range: [{expected_range[0]:,.2f}, {expected_range[1]:,.2f}]")
    print()

    # Step 3: Run Root Cause Analysis
    print("Step 3: Running Root Cause Analysis...")
    print()

    # Initialize analyzer
    analyzer = RootCauseAnalyzer(
        min_confidence=0.3,
        max_primary_drivers=5,
        max_correlations=5,
    )

    # Run analysis
    insight = analyzer.analyze_anomaly(
        anomaly_id="demo-anomaly-001",
        anomaly_timestamp=anomaly_date,
        metric="revenue",
        anomaly_value=anomaly_hour,
        expected_range=expected_range,
        data=data,
        dimensions=["region", "product", "channel"],
        time_column="date",
        dataset_id="demo-dataset-001",
        metadata={"description": "Demo analysis of revenue drop"},
    )

    # Step 4: Display Results
    print("=" * 80)
    print("ROOT CAUSE ANALYSIS RESULTS")
    print("=" * 80)
    print()

    if insight:
        print(f"Anomaly ID: {insight.anomaly_id}")
        print(f"Metric: {insight.metric}")
        print(f"Anomaly Value: {insight.anomaly_value:,.2f}")
        print(f"Expected Range: [{insight.expected_range[0]:,.2f}, {insight.expected_range[1]:,.2f}]")
        print(f"Confidence: {insight.confidence:.2%}")
        print(f"Processing Time: {insight.processing_time_sec:.2f}s")
        print()

        print("Methods Used:", ", ".join([m.value for m in insight.methods_used]))
        print()

        print("-" * 40)
        print("PRIMARY DRIVERS (Ranked by Impact)")
        print("-" * 40)
        for i, driver in enumerate(insight.primary_drivers, 1):
            print(f"{i}. {driver.segment}")
            print(f"   Contribution: {driver.contribution:.1f}%")
            print(f"   Baseline ratio: {driver.baseline_ratio:.2%}")
            if driver.statistical_significance:
                print(f"   Significance: p={driver.statistical_significance:.4f}")
            print()

        print("-" * 40)
        print("CORRELATED METRICS")
        print("-" * 40)
        for i, corr in enumerate(insight.correlations, 1):
            print(f"{i}. {corr.metric}")
            print(f"   Correlation: r={corr.coefficient:.3f} (p={corr.p_value:.4f})")
            if corr.lag_hours:
                print(f"   Lag: {corr.lag_hours:.1f}h ({corr.lag_direction})")
            print()

        if insight.change_point:
            print("-" * 40)
            print("CHANGE POINT DETECTED")
            print("-" * 40)
            cp = insight.change_point
            print(f"Detected at: {cp.detected_at.strftime('%Y-%m-%d %H:%M')}")
            print(f"Confidence: {cp.confidence:.2%}")
            print(f"Change magnitude: {cp.change_magnitude:.2%}")
            print(f"Before mean: {cp.before_mean:,.2f}")
            print(f"After mean: {cp.after_mean:,.2f}")
            print()

        print("-" * 40)
        print("HYPOTHESIS")
        print("-" * 40)
        print(insight.hypothesis)
        print()

        print("-" * 40)
        print("SUPPORTING EVIDENCE")
        print("-" * 40)
        for key, value in insight.supporting_evidence.items():
            print(f"{key}: {value}")
        print()

        print("=" * 80)
        print("Analysis Summary")
        print("=" * 80)
        summary = insight.to_summary_dict()
        for key, value in summary.items():
            print(f"{key}: {value}")

    else:
        print("ERROR: Analysis failed to produce results")

    print()
    print("Performance Stats:")
    stats = analyzer.get_performance_stats()
    for key, value in stats.items():
        print(f"  {key}: {value}")

    print()
    print("Example complete!")


def quick_analysis_demo():
    """
    Minimal example showing basic usage.
    """
    print("\n" + "=" * 80)
    print("QUICK DEMO - 5 Lines of Code")
    print("=" * 80)
    print()

    # Create simple dataset
    dates = pd.date_range('2025-01-01', periods=1000, freq='H')
    data = pd.DataFrame({
        'date': dates,
        'revenue': np.random.normal(10000, 1000, 1000),
        'region': np.random.choice(['US', 'EU', 'APAC'], 1000),
        'product': np.random.choice(['Basic', 'Premium'], 1000),
    })

    # Inject anomaly
    data.loc[500:520, 'revenue'] *= 0.5

    # Run analysis
    analyzer = RootCauseAnalyzer()

    insight = analyzer.analyze_anomaly(
        anomaly_id="quick-demo-001",
        anomaly_timestamp=dates[500],
        metric="revenue",
        anomaly_value=data.loc[500, 'revenue'],
        expected_range=[9000, 1100],
        data=data,
        dimensions=["region", "product"],
        time_column="date",
    )

    if insight:
        print(f"Top driver: {insight.primary_drivers[0].segment if insight.primary_drivers else 'None'}")
        print(f"Confidence: {insight.confidence:.2%}")
        print(f"Hypothesis: {insight.hypothesis}")
    else:
        print("No significant findings")


if __name__ == "__main__":
    # Run full example
    try:
        main()
    except Exception as e:
        print(f"Error running main example: {e}")
        import traceback
        traceback.print_exc()

    # Run quick demo
    try:
        quick_analysis_demo()
    except Exception as e:
        print(f"Error running quick demo: {e}")
