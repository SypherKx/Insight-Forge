#!/usr/bin/env python3
"""
Verification script for InsightForge Ingestion Service.

Checks that all modules can be imported correctly and
basic functionality works as expected.
"""

import sys
from pathlib import Path
import traceback

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

def test_imports():
    """Test that all modules can be imported."""
    print("Testing imports...")

    try:
        import src.ingestion
        print("  [OK] src.ingestion")
    except Exception as e:
        print(f"  [FAIL] src.ingestion: {e}")
        return False

    try:
        from src.ingestion import pipeline
        print("  [OK] pipeline")
    except Exception as e:
        print(f"  [FAIL] pipeline: {e}")
        return False

    try:
        from src.ingestion import parser
        print("  [OK] parser")
    except Exception as e:
        print(f"  [FAIL] parser: {e}")
        return False

    try:
        from src.ingestion import cleaner
        print("  [OK] cleaner")
    except Exception as e:
        print(f"  [FAIL] cleaner: {e}")
        return False

    try:
        from src.ingestion import validator
        print("  [OK] validator")
    except Exception as e:
        print(f"  [FAIL] validator: {e}")
        return False

    try:
        from src.ingestion import storage
        print("  [OK] storage")
    except Exception as e:
        print(f"  [FAIL] storage: {e}")
        return False

    try:
        from src.ingestion import models
        print("  [OK] models")
    except Exception as e:
        print(f"  [FAIL] models: {e}")
        return False

    return True


def test_model_validation():
    """Test Pydantic model creation and validation."""
    print("\nTesting model validation...")

    try:
        from src.ingestion.models import (
            ColumnSchema,
            ColumnType,
            DatasetMetadata,
            IngestionRequest,
            PreprocessingConfig
        )

        # Test ColumnSchema
        col = ColumnSchema(
            name="test_column",
            inferred_type=ColumnType.FLOAT,
            nullable_count=0,
            unique_count=100
        )
        assert col.name == "test_column"
        assert col.inferred_type == ColumnType.FLOAT
        print("  [OK] ColumnSchema validation")

        # Test DatasetMetadata
        metadata = DatasetMetadata(
            id="test-id-123",
            name="Test Dataset",
            org_id="org-123",
            file_path="/path/to/file.csv",
            file_hash="abc123",
            row_count=1000,
            column_count=5,
            column_schema=[col],
            status="completed",
            uploaded_by="user-456"
        )
        assert metadata.id == "test-id-123"
        assert metadata.row_count == 1000
        print("  [OK] DatasetMetadata validation")

        # Test PreprocessingConfig
        config = PreprocessingConfig(
            drop_duplicate_rows=True,
            fill_missing_numeric="median"
        )
        assert config.drop_duplicate_rows is True
        assert config.fill_missing_numeric == "median"
        print("  [OK] PreprocessingConfig validation")

        return True

    except Exception as e:
        print(f"  [FAIL] Model validation failed: {e}")
        traceback.print_exc()
        return False


def test_storage_engine():
    """Test StorageEngine initialization."""
    print("\nTesting StorageEngine...")

    try:
        from src.ingestion.storage import StorageEngine
        import tempfile

        with tempfile.TemporaryDirectory() as tmpdir:
            storage = StorageEngine(
                storage_type="local",
                base_path=tmpdir,
                database_url="sqlite:///:memory:"
            )
            print("  [OK] StorageEngine initialization (local)")

            # Test hash computation
            test_file = Path(tmpdir) / "test.txt"
            test_file.write_text("Hello, World!")
            file_hash = storage.compute_file_hash(test_file)
            # Check that hash is computed (not checking exact value)
            assert file_hash is not None
            assert len(file_hash) == 64  # SHA-256 is 64 hex chars
            print("  [OK] File hash computation")

        return True

    except Exception as e:
        print(f"  [FAIL] StorageEngine test failed: {e}")
        traceback.print_exc()
        return False


def test_parser():
    """Test CSVParser initialization."""
    print("\nTesting CSVParser...")

    try:
        from src.ingestion.parser import CSVParser

        parser = CSVParser()
        print("  [OK] CSVParser initialization")

        return True

    except Exception as e:
        print(f"  [FAIL] CSVParser test failed: {e}")
        traceback.print_exc()
        return False


def test_cleaner():
    """Test DataCleaner initialization."""
    print("\nTesting DataCleaner...")

    try:
        from src.ingestion.cleaner import DataCleaner, clean_data
        from src.ingestion.models import PreprocessingConfig

        config = PreprocessingConfig()
        cleaner = DataCleaner(config)
        print("  [OK] DataCleaner initialization")

        # Test clean_data function
        import pandas as pd
        df = pd.DataFrame({"a": [1, 2, 3], "b": [4, 5, 6]})
        cleaned, report = clean_data(df, [])
        print("  [OK] clean_data function")

        return True

    except Exception as e:
        print(f"  [FAIL] DataCleaner test failed: {e}")
        traceback.print_exc()
        return False


def test_validator():
    """Test DataValidator initialization."""
    print("\nTesting DataValidator...")

    try:
        from src.ingestion.validator import DataValidator, validate_dataset

        validator = DataValidator()
        print("  [OK] DataValidator initialization")

        # Test validate_dataset function
        import pandas as pd
        df = pd.DataFrame({"a": [1, 2, 3], "b": [4, 5, 6]})
        report = validate_dataset(df, [])
        print("  [OK] validate_dataset function")

        return True

    except Exception as e:
        print(f"  [FAIL] DataValidator test failed: {e}")
        traceback.print_exc()
        return False


def test_pipeline():
    """Test IngestionPipeline initialization."""
    print("\nTesting IngestionPipeline...")

    try:
        from src.ingestion.pipeline import IngestionPipeline
        from src.ingestion.storage import StorageEngine
        from src.ingestion.models import PreprocessingConfig
        import tempfile

        with tempfile.TemporaryDirectory() as tmpdir:
            storage = StorageEngine(
                storage_type="local",
                base_path=tmpdir,
                database_url="sqlite:///:memory:"
            )

            config = PreprocessingConfig()
            pipeline = IngestionPipeline(
                storage_engine=storage,
                preprocessing_config=config
            )

            print("  [OK] IngestionPipeline initialization")

        return True

    except Exception as e:
        print(f"  [FAIL] IngestionPipeline test failed: {e}")
        traceback.print_exc()
        return False


def main():
    """Run all verification tests."""
    print("=" * 70)
    print("InsightForge Ingestion Service - Verification")
    print("=" * 70)

    results = []

    results.append(("Imports", test_imports()))
    results.append(("Model Validation", test_model_validation()))
    results.append(("StorageEngine", test_storage_engine()))
    results.append(("CSVParser", test_parser()))
    results.append(("DataCleaner", test_cleaner()))
    results.append(("DataValidator", test_validator()))
    results.append(("IngestionPipeline", test_pipeline()))

    print("\n" + "=" * 70)
    print("Results:")
    print("=" * 70)

    for name, success in results:
        status = "[PASS]" if success else "[FAIL]"
        print(f"  {status}: {name}")

    all_passed = all(success for _, success in results)

    if all_passed:
        print("\n[SUCCESS] All tests passed!")
        print("The Ingestion Service is ready to use.")
        return 0
    else:
        print("\n[ERROR] Some tests failed.")
        print("Please check the error messages above.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
