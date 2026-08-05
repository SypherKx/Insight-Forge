#!/usr/bin/env python3
"""
Example: Basic CSV Ingestion Pipeline Usage

This example demonstrates how to use the InsightForge Ingestion Service
to upload and process a CSV file.
"""

import sys
from pathlib import Path
import tempfile
import pandas as pd
import numpy as np

# Add project root to path for imports
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.ingestion import (
    IngestionPipeline,
    StorageEngine,
    IngestionRequest,
    PreprocessingConfig
)


def create_sample_csv(filepath: Path) -> None:
    """Create a sample CSV file for demonstration."""
    np.random.seed(42)

    # Generate sample business data
    dates = pd.date_range("2025-01-01", periods=1000, freq="h")
    df = pd.DataFrame({
        "timestamp": dates,
        "revenue": np.random.uniform(1000, 5000, 1000),
        "orders": np.random.randint(10, 100, 1000),
        "region": np.random.choice(["US-East", "US-West", "EU-West", "APAC"], 1000),
        "product_category": np.random.choice(
            ["Electronics", "Furniture", "Clothing", "Software"],
            1000
        ),
        "customer_satisfaction": np.random.uniform(3.0, 5.0, 1000)
    })

    # Add some missing values
    df.loc[10:20, "revenue"] = np.nan
    df.loc[50:55, "customer_satisfaction"] = np.nan

    # Add duplicates
    df = pd.concat([df, df.head(10)]).reset_index(drop=True)

    # Save to CSV
    df.to_csv(filepath, index=False)
    print(f"Created sample CSV: {filepath} ({filepath.stat().st_size / 1024:.1f} KB)")


def main():
    """Run example ingestion pipeline."""
    print("=" * 60)
    print("InsightForge AI - Ingestion Pipeline Example")
    print("=" * 60)

    # Setup temporary directory for this example
    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir = Path(tmpdir)

        # Create sample CSV
        csv_path = tmpdir / "sales_data.csv"
        create_sample_csv(csv_path)

        # Configure storage (local filesystem for this example)
        storage = StorageEngine(
            storage_type="local",
            base_path=str(tmpdir / "storage"),
            database_url=f"sqlite:///{tmpdir / 'metadata.db'}"
        )

        # Configure preprocessing
        config = PreprocessingConfig(
            name="Example Pipeline",
            drop_duplicate_rows=True,
            drop_high_null_columns=True,
            fill_missing_numeric="median",
            create_time_features=True,
            normalize_numeric=False  # Keep original values for now
        )

        # Create pipeline
        pipeline = IngestionPipeline(
            storage_engine=storage,
            preprocessing_config=config,
            max_file_size_mb=10  # Small limit for demo
        )

        # Create ingestion request
        request = IngestionRequest(
            name="Q1 2025 Sales Data",
            time_column="timestamp",
            dimensions=["region", "product_category"]
        )

        print("\n" + "-" * 60)
        print("Processing upload...")
        print("-" * 60)

        # Process the upload
        result = pipeline.process_upload(
            file_path=csv_path,
            request=request,
            org_id="demo-org-001",
            user_id="demo-user-001"
        )

        # Display results
        if result.success:
            print("\n✓ UPLOAD SUCCESSFUL")
            print(f"\nDataset ID: {result.dataset_id}")
            print(f"Name: {result.metadata.name}")
            print(f"Status: {result.metadata.status.value}")
            print(f"Rows: {result.metadata.row_count:,}")
            print(f"Columns: {result.metadata.column_count}")
            print(f"Time column: {result.metadata.time_column}")
            print(f"Dimensions: {', '.join(result.metadata.dimensions)}")
            print(f"Quality score: {result.metadata.quality_score:.2%}")

            if result.validation_report:
                vr = result.validation_report
                print(f"\nValidation Report:")
                print(f"  Overall status: {vr.overall_status}")
                print(f"  Total rows: {vr.quality_metrics.total_rows:,}")
                print(f"  Missing values: {vr.quality_metrics.missing_values_percentage:.1f}%")
                print(f"  Duplicates: {vr.quality_metrics.duplicate_rows_percentage:.1f}%")
                print(f"  Columns with high nulls: {len(vr.quality_metrics.columns_high_null_threshold)}")

            if result.cleaning_report:
                cr = result.cleaning_report
                print(f"\nCleaning Report:")
                print(f"  Rows before: {cr['rows_before']:,}")
                print(f"  Rows after: {cr['rows_after']:,}")
                print(f"  Duplicates removed: {cr['duplicates_removed']:,}")
                print(f"  Missing values filled: {cr['missing_values_filled']:,}")
                print(f"  Columns removed: {len(cr['columns_removed'])}")
                if 'scaler_params' in cr:
                    print(f"  Normalized columns: {len(cr['scaler_params'])}")

            # Show pipeline statistics
            stats = pipeline.get_stats()
            print(f"\nPipeline Statistics:")
            print(f"  Datasets processed: {stats['datasets_processed']}")
            print(f"  Total rows ingested: {stats['total_rows_ingested']:,}")
            print(f"  Avg processing time: {stats['avg_processing_time_sec']:.2f}s")

            # List all datasets
            print("\n" + "-" * 60)
            print("Dataset Summary")
            print("-" * 60)
            datasets = pipeline.list_datasets(org_id="demo-org-001")
            for ds in datasets:
                print(f"  - {ds.name} ({ds.status.value}, {ds.row_count:,} rows)")

        else:
            print("\n✗ UPLOAD FAILED")
            print(f"\nError: {result.error}")
            if result.metadata and result.metadata.error_message:
                print(f"Details: {result.metadata.error_message}")

        print("\n" + "=" * 60)
        print("Example complete!")
        print("=" * 60)


if __name__ == "__main__":
    main()
