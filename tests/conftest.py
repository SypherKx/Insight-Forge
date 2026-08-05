"""
Test configuration and shared fixtures.
"""

import sys
from pathlib import Path

# Add src to path for imports during testing
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

import pytest
import pandas as pd
import numpy as np


@pytest.fixture(scope="session")
def test_data_dir():
    """Return path to test data directory."""
    return Path(__file__).parent / "data"


@pytest.fixture
def sample_business_data():
    """Create sample business dataset for testing."""
    np.random.seed(42)
    dates = pd.date_range("2025-01-01", periods=1000, freq="h")
    return pd.DataFrame({
        "timestamp": dates,
        "sensor_id": np.random.choice(["S1", "S2", "S3", "S4"], 1000),
        "temperature": np.random.normal(50, 10, 1000),
        "pressure": np.random.uniform(100, 200, 1000),
        "status": np.random.choice(["OK", "WARNING", "ERROR"], 1000, p=[0.8, 0.15, 0.05]),
        "value": np.random.exponential(100, 1000)
    })


@pytest.fixture
def sample_time_series():
    """Create sample time series dataset."""
    dates = pd.date_range("2025-01-01", periods=365, freq="D")
    trend = np.linspace(100, 150, 365)
    seasonal = 10 * np.sin(2 * np.pi * np.arange(365) / 365)
    noise = np.random.normal(0, 2, 365)

    return pd.DataFrame({
        "date": dates,
        "revenue": trend + seasonal + noise,
        "orders": np.random.poisson(100, 365),
        "customers": np.random.poisson(50, 365)
    })


@pytest.fixture(autouse=True)
def setup_logging(caplog):
    """Set up logging capture for all tests."""
    import logging
    logging.basicConfig(level=logging.DEBUG)
