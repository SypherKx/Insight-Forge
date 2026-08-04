"""
Generate sample business data with injected anomalies for demo purposes.
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import os


def generate_sample_data(output_path: str = "sample_data.csv"):
    """Generate realistic business data with anomalies."""
    np.random.seed(42)

    # 365 days of data
    dates = pd.date_range(start="2025-01-01", periods=365, freq="D")

    regions = ["US-East", "US-West", "Europe", "Asia"]
    products = ["Enterprise", "Pro", "Basic"]

    rows = []

    for date in dates:
        for region in regions:
            for product in products:
                # Base revenue with seasonal patterns
                day_of_year = date.dayofyear
                weekday_factor = 1.0 if date.weekday() < 5 else 0.6

                # Seasonal: higher in Q4, lower in Q1
                seasonal = 1.0 + 0.2 * np.sin(2 * np.pi * (day_of_year - 90) / 365)

                # Product and region base values
                product_base = {"Enterprise": 50000, "Pro": 15000, "Basic": 5000}
                region_base = {"US-East": 1.0, "US-West": 0.85, "Europe": 0.75, "Asia": 0.6}

                base = product_base[product] * region_base[region] * seasonal * weekday_factor

                # Normal noise
                revenue = base * (1 + np.random.normal(0, 0.05))
                orders = max(1, int(revenue / (product_base[product] / 10) + np.random.normal(0, 2)))
                support_tickets = max(0, int(np.random.poisson(5 + orders * 0.1)))
                churn_rate = max(0, min(0.15, 0.03 + np.random.normal(0, 0.005)))

                # ═══ INJECT ANOMALIES ═══

                # Anomaly 1: Revenue crash in US-East Enterprise on March 15
                if (date == pd.Timestamp("2025-03-15") and
                    region == "US-East" and product == "Enterprise"):
                    revenue *= 0.35  # 65% drop
                    support_tickets *= 4  # Support spike

                # Anomaly 2: Revenue spike in US-West Pro on June 20
                if (date == pd.Timestamp("2025-06-20") and
                    region == "US-West" and product == "Pro"):
                    revenue *= 3.2  # Massive spike

                # Anomaly 3: Gradual decline in Europe for a week
                if (pd.Timestamp("2025-08-10") <= date <= pd.Timestamp("2025-08-16") and
                    region == "Europe"):
                    day_offset = (date - pd.Timestamp("2025-08-10")).days
                    decline = 1.0 - 0.08 * day_offset
                    revenue *= decline
                    churn_rate *= (1 + 0.1 * day_offset)

                # Anomaly 4: Asia orders spike on Nov 11 (Singles Day)
                if (date == pd.Timestamp("2025-11-11") and region == "Asia"):
                    revenue *= 4.5
                    orders *= 5

                # Anomaly 5: Support ticket explosion everywhere Dec 24
                if date == pd.Timestamp("2025-12-24"):
                    support_tickets *= 6

                rows.append({
                    "date": date.strftime("%Y-%m-%d"),
                    "region": region,
                    "product": product,
                    "revenue": round(revenue, 2),
                    "orders": orders,
                    "support_tickets": support_tickets,
                    "churn_rate": round(churn_rate, 4),
                })

    df = pd.DataFrame(rows)
    df.to_csv(output_path, index=False)
    print(f"Generated {len(df)} rows → {output_path}")
    print(f"  Columns: {list(df.columns)}")
    print(f"  Date range: {df['date'].min()} to {df['date'].max()}")
    print(f"  Regions: {df['region'].unique().tolist()}")
    print(f"  Products: {df['product'].unique().tolist()}")
    return df


if __name__ == "__main__":
    generate_sample_data()
