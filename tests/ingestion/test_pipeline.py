"""
Tests for Ingestion Pipeline.
"""

import pytest
import tempfile
import os
from pathlib import Path
from datetime import datetime
import uuid

from src.ingestion.pipeline import IngestionPipeline, PipelineResult
from src.ingestion.models import IngestionRequest, PreprocessingConfig, DatasetStatus
from src.ingestion.storage import StorageEngine


@pytest.fixture
def temp_storage():
    """Create temporary storage for testing."""
    with tempfile.TemporaryDirectory() as tmpdir:
        # Use SQLite for testing
        db_path = os.path.join(tmpdir, "test_metadata.db")
        storage = StorageEngine(
            storage_type="local",
            base_path=tmpdir,
            database_url=f"sqlite:///{db_path}"
        )
        yield storage
        # Dispose SQLAlchemy engine to release file locks on Windows
        storage.dispose()


@pytest.fixture
def sample_csv(tmp_path):
    """Create sample CSV file."""
    csv_content = """date,revenue,region,product_category,quantity
2025-01-01,15000.50,US-East,Electronics,100
2025-01-02,18000.00,US-West,Electronics,120
2025-01-03,12000.75,US-East,Furniture,80
2025-01-04,20000.00,EU-West,Electronics,150
2025-01-05,16500.25,US-East,Furniture,90
2025-01-06,19000.00,US-West,Electronics,130
"""
    csv_path = tmp_path / "sample.csv"
    csv_path.write_text(csv_content)
    return csv_path


@pytest.fixture
def sample_invalid_csv(tmp_path):
    """Create invalid CSV file."""
    csv_path = tmp_path / "invalid.csv"
    csv_path.write_text("a,b,c,d\n1,2,3,4\n5,6,7,8")  # Simple but valid
    return csv_path


class TestIngestionPipeline:
    """Test cases for IngestionPipeline."""

    def test_pipeline_initialization(self, temp_storage):
        """Test pipeline initialization."""
        config = PreprocessingConfig(drop_duplicate_rows=True)
        pipeline = IngestionPipeline(
            storage_engine=temp_storage,
            preprocessing_config=config,
            max_file_size_mb=1000
        )

        assert pipeline.storage == temp_storage
        assert pipeline.preprocessing_config == config
        assert pipeline.max_file_size_mb == 1000

    def test_process_valid_upload(self, temp_storage, sample_csv):
        """Test processing a valid CSV upload."""
        config = PreprocessingConfig(
            drop_duplicate_rows=True,
            fill_missing_numeric='median'
        )

        pipeline = IngestionPipeline(
            storage_engine=temp_storage,
            preprocessing_config=config
        )

        # Create ingestion request
        request = IngestionRequest(
            name="Test Dataset",
            time_column="date",
            dimensions=["region", "product_category"]
        )

        # Process upload
        result = pipeline.process_upload(
            file_path=sample_csv,
            request=request,
            org_id="test-org-123",
            user_id="test-user-456"
        )

        # Check results
        assert result.success is True
        assert result.dataset_id is not None
        assert result.metadata is not None
        assert result.validation_report is not None

        # Check metadata
        metadata = result.metadata
        assert metadata.name == "Test Dataset"
        assert metadata.org_id == "test-org-123"
        assert metadata.status == DatasetStatus.COMPLETED
        assert metadata.row_count == 6
        assert metadata.column_count > 0
        assert metadata.time_column == "date"
        assert len(metadata.dimensions) == 2
        assert metadata.file_path != ""

        # Check validation
        validation = result.validation_report
        assert validation.quality_metrics.total_rows == 6
        assert validation.overall_status in ['passed', 'warning']

    def test_process_upload_with_missing_values(self, temp_storage):
        """Test processing CSV with missing values."""
        # Create CSV with missing values
        csv_content = """date,revenue,region
2025-01-01,15000.50,US-East
2025-01-02,,US-West
2025-01-03,12000.75,
2025-01-04,20000.00,EU-West
"""
        csv_path = Path(temp_storage.base_path) / "missing.csv"
        csv_path.write_text(csv_content)

        config = PreprocessingConfig(
            fill_missing_numeric='median',
            fill_missing_categorical='mode'
        )

        pipeline = IngestionPipeline(
            storage_engine=temp_storage,
            preprocessing_config=config
        )

        request = IngestionRequest(
            name="Missing Values Test",
            time_column="date"
        )

        result = pipeline.process_upload(
            file_path=csv_path,
            request=request,
            org_id="test-org",
            user_id="test-user"
        )

        assert result.success is True
        assert result.cleaning_report is not None
        assert result.cleaning_report['missing_values_filled'] > 0

    def test_process_upload_with_duplicates(self, temp_storage):
        """Test processing CSV with duplicate rows."""
        csv_content = """a,b
1,2
3,4
1,2
5,6
"""
        csv_path = Path(temp_storage.base_path) / "duplicates.csv"
        csv_path.write_text(csv_content)

        config = PreprocessingConfig(drop_duplicate_rows=True)

        pipeline = IngestionPipeline(
            storage_engine=temp_storage,
            preprocessing_config=config
        )

        request = IngestionRequest(name="Duplicates Test")

        result = pipeline.process_upload(
            file_path=csv_path,
            request=request,
            org_id="test-org",
            user_id="test-user"
        )

        assert result.success is True
        assert result.cleaning_report['duplicates_removed'] == 1

    def test_reject_oversized_file(self, tmp_path, temp_storage):
        """Test rejection of file exceeding size limit."""
        # Create a file with specified size
        large_csv = tmp_path / "large.csv"
        # Write more than max_file_size_mb (100MB default, but we set 1MB for test)
        pipeline = IngestionPipeline(
            storage_engine=temp_storage,
            max_file_size_mb=1
        )

        # Create a file just over 1MB
        with open(large_csv, 'w') as f:
            f.write("a,b,c\n")
            f.write("x" * 1024 * 1024 + "\n")  # 1MB plus header

        request = IngestionRequest()

        result = pipeline.process_upload(
            file_path=large_csv,
            request=request,
            org_id="test-org",
            user_id="test-user"
        )

        assert result.success is False
        assert "File size" in result.error

    def test_get_dataset_status(self, temp_storage, sample_csv):
        """Test retrieving dataset status."""
        pipeline = IngestionPipeline(storage_engine=temp_storage)

        request = IngestionRequest(name="Status Test")

        result = pipeline.process_upload(
            file_path=sample_csv,
            request=request,
            org_id="test-org",
            user_id="test-user"
        )

        # Get status
        status = pipeline.get_dataset_status(result.dataset_id)

        assert status is not None
        assert status.id == result.dataset_id
        assert status.status == DatasetStatus.COMPLETED

    def test_list_datasets(self, temp_storage, sample_csv):
        """Test listing datasets for an organization."""
        pipeline = IngestionPipeline(storage_engine=temp_storage)

        # Upload multiple datasets
        for i in range(3):
            request = IngestionRequest(name=f"Dataset {i}")
            pipeline.process_upload(
                file_path=sample_csv,
                request=request,
                org_id="org-1",
                user_id="user-1"
            )

        # List datasets
        datasets = pipeline.list_datasets(org_id="org-1", limit=10)

        assert len(datasets) == 3
        assert all(isinstance(ds, object) for ds in datasets)
        assert all(ds.org_id == "org-1" for ds in datasets)

    def test_delete_dataset(self, temp_storage, sample_csv):
        """Test dataset deletion."""
        pipeline = IngestionPipeline(storage_engine=temp_storage)

        request = IngestionRequest(name="Delete Test")

        result = pipeline.process_upload(
            file_path=sample_csv,
            request=request,
            org_id="test-org",
            user_id="test-user"
        )

        # Delete dataset
        success = pipeline.delete_dataset(result.dataset_id, org_id="test-org")

        assert success is True

        # Verify deletion
        status = pipeline.get_dataset_status(result.dataset_id)
        assert status is None

    def test_delete_dataset_unauthorized(self, temp_storage, sample_csv):
        """Test dataset deletion with wrong org."""
        pipeline = IngestionPipeline(storage_engine=temp_storage)

        request = IngestionRequest(name="Auth Test")

        result = pipeline.process_upload(
            file_path=sample_csv,
            request=request,
            org_id="org-A",
            user_id="user-A"
        )

        # Try to delete with different org
        success = pipeline.delete_dataset(result.dataset_id, org_id="org-B")

        assert success is False

    def test_pipeline_stats(self, temp_storage, sample_csv):
        """Test pipeline statistics tracking."""
        pipeline = IngestionPipeline(storage_engine=temp_storage)

        # Initial stats
        initial_stats = pipeline.get_stats()
        assert initial_stats['datasets_processed'] == 0

        # Process upload
        request = IngestionRequest(name="Stats Test")
        pipeline.process_upload(
            file_path=sample_csv,
            request=request,
            org_id="test-org",
            user_id="test-user"
        )

        # Check updated stats
        stats = pipeline.get_stats()
        assert stats['datasets_processed'] == 1
        assert stats['total_rows_ingested'] == 6
        assert stats['avg_processing_time_sec'] > 0

    def test_empty_file_error(self, temp_storage, tmp_path):
        """Test handling of empty CSV file."""
        empty_csv = tmp_path / "empty.csv"
        empty_csv.write_text("")

        pipeline = IngestionPipeline(storage_engine=temp_storage)
        request = IngestionRequest()

        result = pipeline.process_upload(
            file_path=empty_csv,
            request=request,
            org_id="test-org",
            user_id="test-user"
        )

        assert result.success is False
        assert "empty" in result.error.lower()

    def test_time_column_detection(self, temp_storage):
        """Test automatic time column detection."""
        csv_content = """timestamp,value,category
2025-01-01 00:00:00,100,A
2025-01-01 01:00:00,110,B
2025-01-01 02:00:00,120,A
"""
        csv_path = Path(temp_storage.base_path) / "time.csv"
        csv_path.write_text(csv_content)

        pipeline = IngestionPipeline(storage_engine=temp_storage)

        # Test without explicit time_column - should auto-detect
        request = IngestionRequest()
        result = pipeline.process_upload(
            file_path=csv_path,
            request=request,
            org_id="test-org",
            user_id="test-user"
        )

        assert result.success is True
        # Should auto-detect 'timestamp' as time column
        assert result.metadata.time_column == 'timestamp'

    def test_validation_report_preserved(self, temp_storage, sample_csv):
        """Test that validation report is properly stored."""
        pipeline = IngestionPipeline(storage_engine=temp_storage)

        request = IngestionRequest()
        result = pipeline.process_upload(
            file_path=sample_csv,
            request=request,
            org_id="test-org",
            user_id="test-user"
        )

        assert result.validation_report is not None
        assert hasattr(result.validation_report, 'overall_status')
        assert hasattr(result.validation_report, 'quality_metrics')
        assert hasattr(result.validation_report, 'validation_results')


class TestEdgeCases:
    """Edge case tests for pipeline."""

    def test_non_ascii_filename(self, temp_storage, tmp_path):
        """Test handling of non-ASCII characters in filename."""
        csv_content = "a,b\n1,2\n"
        csv_path = tmp_path / "test_café_naïve_日本語.csv"
        csv_path.write_text(csv_content)

        pipeline = IngestionPipeline(storage_engine=temp_storage)
        request = IngestionRequest()

        result = pipeline.process_upload(
            file_path=csv_path,
            request=request,
            org_id="org",
            user_id="user"
        )

        assert result.success is True

    def test_single_column_csv(self, temp_storage, tmp_path):
        """Test handling of single column CSV."""
        csv_content = """value
1
2
3
4
5
"""
        csv_path = tmp_path / "single_column.csv"
        csv_path.write_text(csv_content)

        pipeline = IngestionPipeline(storage_engine=temp_storage)
        request = IngestionRequest()

        result = pipeline.process_upload(
            file_path=csv_path,
            request=request,
            org_id="org",
            user_id="user"
        )

        assert result.success is True
        assert result.metadata.column_count == 1

    def test_very_wide_csv(self, temp_storage, tmp_path):
        """Test handling of very wide CSV (many columns)."""
        # Create CSV with 200 columns
        headers = [f"col_{i}" for i in range(200)]
        rows = []
        for i in range(10):
            row = [i * j for j in range(200)]
            rows.append(','.join(str(x) for x in row))

        csv_content = ','.join(headers) + '\n' + '\n'.join(rows)
        csv_path = tmp_path / "wide.csv"
        csv_path.write_text(csv_content)

        pipeline = IngestionPipeline(storage_engine=temp_storage)
        request = IngestionRequest()

        result = pipeline.process_upload(
            file_path=csv_path,
            request=request,
            org_id="org",
            user_id="user"
        )

        assert result.success is True
        assert result.metadata.column_count == 200
