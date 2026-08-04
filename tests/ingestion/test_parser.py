"""
Tests for CSV Parser module.
"""

import pytest
import pandas as pd
from io import StringIO
from pathlib import Path

from src.ingestion.parser import CSVParser
from src.ingestion.models import ColumnType


@pytest.fixture
def sample_csv():
    """Create a sample CSV string for testing."""
    csv_data = """date,revenue,region,product_category,quantity,is_promotion
2025-01-01,15000.50,US-East,Electronics,100,true
2025-01-02,18000.00,US-West,Electronics,120,false
2025-01-03,12000.75,US-East,Furniture,80,false
2025-01-04,20000.00,EU-West,Electronics,150,true
2025-01-05,16500.25,US-East,Furniture,90,false
2025-01-06,19000.00,US-West,Electronics,130,false
"""
    return csv_data


@pytest.fixture
def sample_csv_file(tmp_path, sample_csv):
    """Create a sample CSV file for testing."""
    file_path = tmp_path / "test_data.csv"
    file_path.write_text(sample_csv)
    return file_path


class TestCSVParser:
    """Test cases for CSVParser."""

    def test_infer_schema(self, sample_csv_file):
        """Test schema inference from CSV."""
        parser = CSVParser()

        schemas = parser.infer_schema(sample_csv_file)

        assert len(schemas) == 6

        # Check date column
        date_col = next(cs for cs in schemas if cs.name == 'date')
        assert date_col.inferred_type == ColumnType.DATETIME
        assert date_col.is_time_column is True

        # Check revenue column
        revenue_col = next(cs for cs in schemas if cs.name == 'revenue')
        assert revenue_col.inferred_type == ColumnType.FLOAT

        # Check region column
        region_col = next(cs for cs in schemas if cs.name == 'region')
        assert region_col.inferred_type == ColumnType.CATEGORICAL

        # Check quantity column
        qty_col = next(cs for cs in schemas if cs.name == 'quantity')
        assert qty_col.inferred_type == ColumnType.INTEGER

        # Check boolean column
        promo_col = next(cs for cs in schemas if cs.name == 'is_promotion')
        assert promo_col.inferred_type == ColumnType.BOOLEAN

    def test_read_csv(self, sample_csv_file):
        """Test reading CSV file."""
        parser = CSVParser()

        schemas = parser.infer_schema(sample_csv_file)
        df = parser.read_csv(sample_csv_file, column_schema=schemas)

        assert len(df) == 6
        assert len(df.columns) == 6
        assert 'date' in df.columns

    def test_read_csv_with_time_column(self, sample_csv_file):
        """Test reading CSV with time column as index."""
        parser = CSVParser()

        schemas = parser.infer_schema(sample_csv_file)
        df = parser.read_csv(
            sample_csv_file,
            column_schema=schemas,
            time_column='date'
        )

        # Check that date column is now index
        assert df.index.name == 'date'
        assert len(df) == 6

    def test_validate_csv_structure(self, sample_csv_file):
        """Test CSV structure validation."""
        parser = CSVParser()

        is_valid, errors, metadata = parser.validate_csv_structure(sample_csv_file)

        assert is_valid is True
        assert len(errors) == 0
        assert metadata['row_count'] == 6
        assert metadata['column_count'] == 6

    def test_validate_invalid_csv(self, tmp_path):
        """Test validation of invalid CSV."""
        # Create invalid CSV (with duplicate columns)
        invalid_csv = """a,b,a,c
1,2,3,4
5,6,7,8
"""
        file_path = tmp_path / "invalid.csv"
        file_path.write_text(invalid_csv)

        parser = CSVParser()
        is_valid, errors, metadata = parser.validate_csv_structure(file_path)

        assert is_valid is False
        assert len(errors) > 0
        assert "Duplicate column names" in errors[0]

    def test_encoding_detection(self, tmp_path):
        """Test encoding detection fallback."""
        # Create CSV with non-ASCII characters
        csv_latin1 = """name,value
Café,100
Niño,200
"""
        file_path = tmp_path / "latin1.csv"
        file_path.write_text(csv_latin1, encoding='latin-1')

        parser = CSVParser()
        # Just verify it can read the file (with chardet or fallback)
        try:
            schemas = parser.infer_schema(file_path)
            assert len(schemas) == 2
        except Exception as e:
            pytest.fail(f"Should be able to read latin-1 encoded file: {e}")

    def test_missing_values(self, tmp_path):
        """Test handling of missing values."""
        csv_with_nulls = """date,revenue,region
2025-01-01,10000,US-East
2025-01-02,,US-West
2025-01-03,15000,
2025-01-04,,
"""
        file_path = tmp_path / "nulls.csv"
        file_path.write_text(csv_with_nulls)

        parser = CSVParser()
        schemas = parser.infer_schema(file_path)

        revenue_col = next(cs for cs in schemas if cs.name == 'revenue')
        assert revenue_col.nullable_count == 2  # Two missing values

        region_col = next(cs for cs in schemas if cs.name == 'region')
        assert region_col.nullable_count == 2


class TestEdgeCases:
    """Edge case tests."""

    def test_empty_csv(self, tmp_path):
        """Test empty CSV file."""
        empty_csv = ""
        file_path = tmp_path / "empty.csv"
        file_path.write_text(empty_csv)

        parser = CSVParser()
        with pytest.raises(Exception):  # Should raise pd.errors.EmptyDataError
            parser.infer_schema(file_path)

    def test_single_row_csv(self, tmp_path):
        """Test CSV with single row."""
        single_row = """a,b,c
1,2,3
"""
        file_path = tmp_path / "single.csv"
        file_path.write_text(single_row)

        parser = CSVParser()
        schemas = parser.infer_schema(file_path)
        assert len(schemas) == 3

    def test_large_file_sampling(self, tmp_path):
        """Test that schema inference uses sampling for large files."""
        # Create file with 20,000 rows (more than INFERENCE_SAMPLE_SIZE)
        rows = ["a,b,c"] + [f"{i},{i*2},{i%10}" for i in range(20000)]
        csv_content = "\n".join(rows)

        file_path = tmp_path / "large.csv"
        file_path.write_text(csv_content)

        parser = CSVParser()
        schemas = parser.infer_schema(file_path)

        assert len(schemas) == 3
        # All should be inferred as numeric
        for schema in schemas:
            assert schema.inferred_type in [ColumnType.INTEGER, ColumnType.FLOAT]
