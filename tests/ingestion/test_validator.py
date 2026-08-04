"""
Tests for Data Validator module.
"""

import pytest
import pandas as pd
import numpy as np

from src.ingestion.validator import DataValidator, validate_dataset, create_default_validation_rules
from src.ingestion.models import ColumnSchema, ColumnType, ValidationRule


@pytest.fixture
def sample_schemas():
    """Create sample column schemas."""
    return [
        ColumnSchema(
            name="date",
            inferred_type=ColumnType.DATETIME,
            nullable_count=0,
            unique_count=10,
            is_time_column=True,
            is_dimension=False
        ),
        ColumnSchema(
            name="revenue",
            inferred_type=ColumnType.FLOAT,
            nullable_count=2,
            unique_count=50,
            is_time_column=False,
            is_dimension=False
        ),
        ColumnSchema(
            name="region",
            inferred_type=ColumnType.CATEGORICAL,
            nullable_count=1,
            unique_count=3,
            is_time_column=False,
            is_dimension=False
        )
    ]


@pytest.fixture
def valid_dataframe():
    """Create a valid sample DataFrame."""
    np.random.seed(42)
    n = 100

    return pd.DataFrame({
        'date': pd.date_range('2025-01-01', periods=n, freq='D'),
        'revenue': np.random.uniform(1000, 10000, n),
        'region': np.random.choice(['US-East', 'US-West', 'EU-West'], n)
    })


@pytest.fixture
def invalid_dataframe():
    """Create an invalid DataFrame with quality issues."""
    np.random.seed(42)
    n = 100

    df = pd.DataFrame({
        'date': pd.date_range('2025-01-01', periods=n, freq='D'),
        'revenue': np.random.uniform(1000, 10000, n),
        'region': ['US-East'] * n,  # Constant column
        'high_null': [np.nan if i < 80 else i for i in range(n)]  # 80% nulls
    })

    # Introduce duplicates (make first 5 rows appear again)
    df = pd.concat([df, df.head(5)]).reset_index(drop=True)

    # Add many missing values to revenue
    df.loc[:50, 'revenue'] = np.nan

    return df


class TestDataValidator:
    """Test cases for DataValidator."""

    def test_validate_high_quality_dataset(self, valid_dataframe, sample_schemas):
        """Test validation on high quality dataset."""
        validator = DataValidator()
        report = validator.validate_dataset(valid_dataframe, sample_schemas)

        assert report.overall_status in ['passed', 'warning']
        assert report.quality_metrics.total_rows == 100
        assert report.quality_metrics.total_columns == 3

    def test_validate_low_quality_dataset(self, invalid_dataframe, sample_schemas):
        """Test validation on low quality dataset."""
        validator = DataValidator()
        report = validator.validate_dataset(invalid_dataframe, sample_schemas)

        # Should have errors or warnings
        assert report.overall_status in ['failed', 'warning']
        assert len(report.validation_results) > 0

    def test_missing_values_validation(self):
        """Test specific missing value validation."""
        validator = DataValidator()

        # Create dataframe with missing values (small % of total)
        df = pd.DataFrame({
            'a': [1 if i % 20 != 0 else np.nan for i in range(100)],  # 5 missing
            'b': range(100)
        })

        schemas = [
            ColumnSchema(
                name='a',
                inferred_type=ColumnType.FLOAT,
                nullable_count=1,
                unique_count=2,
                is_time_column=False,
                is_dimension=False
            ),
            ColumnSchema(
                name='b',
                inferred_type=ColumnType.INTEGER,
                nullable_count=0,
                unique_count=100,
                is_time_column=False,
                is_dimension=False
            )
        ]

        report = validator.validate_dataset(df, schemas)

        # Should have low missing value percentage (1%)
        assert report.quality_metrics.missing_values_percentage < 5

    def test_duplicate_validation(self):
        """Test duplicate row validation."""
        validator = DataValidator()

        df = pd.DataFrame({
            'a': [1, 2, 3, 1, 2],  # First two rows duplicated
            'b': [4, 5, 6, 4, 5]
        })

        schemas = [
            ColumnSchema(
                name='a',
                inferred_type=ColumnType.INTEGER,
                nullable_count=0,
                unique_count=3,
                is_time_column=False,
                is_dimension=False
            ),
            ColumnSchema(
                name='b',
                inferred_type=ColumnType.INTEGER,
                nullable_count=0,
                unique_count=3,
                is_time_column=False,
                is_dimension=False
            )
        ]

        report = validator.validate_dataset(df, schemas)

        assert report.quality_metrics.duplicate_rows == 2
        assert len(report.validation_results) > 0

    def test_constant_column_detection(self):
        """Test constant column detection."""
        validator = DataValidator()

        df = pd.DataFrame({
            'constant': ['A'] * 50,
            'variable': range(50)
        })

        schemas = [
            ColumnSchema(
                name='constant',
                inferred_type=ColumnType.CATEGORICAL,
                nullable_count=0,
                unique_count=1,
                is_time_column=False,
                is_dimension=False
            ),
            ColumnSchema(
                name='variable',
                inferred_type=ColumnType.INTEGER,
                nullable_count=0,
                unique_count=50,
                is_time_column=False,
                is_dimension=False
            )
        ]

        report = validator.validate_dataset(df, schemas)

        constant_cols = report.quality_metrics.constant_columns
        assert 'constant' in constant_cols
        assert 'variable' not in constant_cols

    def test_custom_validation_rule(self):
        """Test custom validation rule."""
        validator = DataValidator()

        df = pd.DataFrame({
            'score': [45, 50, 85, 90, 100],
            'category': ['A', 'B', 'C', 'D', 'E']
        })

        schemas = [
            ColumnSchema(
                name='score',
                inferred_type=ColumnType.INTEGER,
                nullable_count=0,
                unique_count=5,
                is_time_column=False,
                is_dimension=False
            ),
            ColumnSchema(
                name='category',
                inferred_type=ColumnType.CATEGORICAL,
                nullable_count=0,
                unique_count=5,
                is_time_column=False,
                is_dimension=False
            )
        ]

        # Custom rule: score should be >= 50
        custom_rule = ValidationRule(
            rule_type='custom_range',
            column='score',
            parameters={'min': 50, 'max': 100},
            threshold=0,
            severity='high'  # Set high severity to trigger 'failed' status
        )

        report = validator.validate_dataset(df, schemas, custom_rules=[custom_rule])

        # Should fail because there's a score of 45
        assert report.overall_status == 'failed'
        range_results = [
            r for r in report.validation_results
            if r.rule.rule_type == 'custom_range'
        ]
        assert len(range_results) > 0
        assert range_results[0].passed is False

    def test_validate_min_rows(self):
        """Test minimum row count validation."""
        validator = DataValidator()

        # DataFrame with only 5 rows (below default 10)
        df = pd.DataFrame({'a': [1, 2, 3, 4, 5]})

        schemas = [
            ColumnSchema(
                name='a',
                inferred_type=ColumnType.INTEGER,
                nullable_count=0,
                unique_count=5,
                is_time_column=False,
                is_dimension=False
            )
        ]

        report = validator.validate_dataset(df, schemas)

        # Should have a failed min_rows validation
        min_rows_results = [
            r for r in report.validation_results
            if r.rule.rule_type == 'min_rows'
        ]
        assert len(min_rows_results) > 0
        assert min_rows_results[0].passed is False

    def test_type_consistency(self):
        """Test type consistency validation."""
        validator = DataValidator()

        # DataFrame with non-numeric strings in a supposed integer column
        df = pd.DataFrame({
            'integer_col': [1.0, 2.0, 3.0, 'text', 5.0]  # Float mixed with string
        })

        schemas = [
            ColumnSchema(
                name='integer_col',
                inferred_type=ColumnType.FLOAT,  # Treat as float for simplicity
                nullable_count=0,
                unique_count=4,  # 4 unique values
                is_time_column=False,
                is_dimension=False
            )
        ]

        report = validator.validate_dataset(df, schemas)

        type_results = [
            r for r in report.validation_results
            if r.rule.rule_type == 'type_consistency'
        ]
        assert len(type_results) > 0
        # The non-numeric value should be detected
        assert type_results[0].passed is False

    def test_default_validation_rules(self):
        """Test creation of default validation rules."""
        rules = create_default_validation_rules()

        assert len(rules) >= 5
        rule_types = [r.rule_type for r in rules]
        assert 'min_rows' in rule_types
        assert 'missing_values' in rule_types
        assert 'duplicates' in rule_types
        assert 'constant_columns' in rule_types
        assert 'type_consistency' in rule_types

    def test_severity_levels(self):
        """Test severity assignment for different rule types."""
        validator = DataValidator()

        severity_map = validator.severity_thresholds

        assert severity_map['missing_values'] in ['high', 'medium', 'low', 'critical']
        assert severity_map['duplicates'] in ['high', 'medium', 'low', 'critical']
        assert severity_map['constant_column'] in ['high', 'medium', 'low', 'critical']


class TestValidateDatasetFunction:
    """Test the convenience validate_dataset function."""

    def test_validate_function(self, valid_dataframe, sample_schemas):
        """Test the validate_dataset convenience function."""
        report = validate_dataset(valid_dataframe, sample_schemas)

        assert isinstance(report, object)
        assert hasattr(report, 'overall_status')
        assert hasattr(report, 'quality_metrics')
        assert hasattr(report, 'validation_results')

    def test_validate_with_custom_rules(self, valid_dataframe, sample_schemas):
        """Test validation with custom rules."""
        custom_rule = ValidationRule(
            rule_type='custom_expression',
            column=None,
            parameters={'expression': 'revenue > 0'},
            threshold=0
        )

        report = validate_dataset(valid_dataframe, sample_schemas, custom_rules=[custom_rule])

        assert isinstance(report, object)
        # Should have at least one custom expression result
        custom_results = [
            r for r in report.validation_results
            if r.rule.rule_type == 'custom_expression'
        ]
        assert len(custom_results) > 0


class TestEdgeCases:
    """Edge case tests."""

    def test_empty_dataframe(self):
        """Test validation on empty DataFrame."""
        validator = DataValidator()

        df = pd.DataFrame()
        schemas = []

        report = validator.validate_dataset(df, schemas)

        assert report.overall_status == 'failed'
        assert any('empty' in err.lower() for err in report.errors)

    def test_single_row(self):
        """Test validation on single row dataset."""
        df = pd.DataFrame({'a': [1]})
        schemas = [
            ColumnSchema(
                name='a',
                inferred_type=ColumnType.INTEGER,
                nullable_count=0,
                unique_count=1,
                is_time_column=False,
                is_dimension=False
            )
        ]

        # Use validator with min_rows=1 to allow single row
        validator = DataValidator()
        validator.DEFAULT_MIN_ROWS = 1
        report = validator.validate_dataset(df, schemas)

        # Single row should pass with min_rows=1
        assert report.overall_status in ['passed', 'warning']
        min_rows_results = [
            r for r in report.validation_results
            if r.rule.rule_type == 'min_rows'
        ]
        if min_rows_results:
            assert min_rows_results[0].passed is True

    def test_all_missing_column(self):
        """Test column with all missing values."""
        validator = DataValidator()

        df = pd.DataFrame({
            'all_null': [np.nan] * 100,
            'valid': range(100)
        })

        schemas = [
            ColumnSchema(
                name='all_null',
                inferred_type=ColumnType.FLOAT,
                nullable_count=100,
                unique_count=0,
                is_time_column=False,
                is_dimension=False
            ),
            ColumnSchema(
                name='valid',
                inferred_type=ColumnType.INTEGER,
                nullable_count=0,
                unique_count=100,
                is_time_column=False,
                is_dimension=False
            )
        ]

        report = validator.validate_dataset(df, schemas)

        # Should note high nulls in the all_null column
        assert 'all_null' in report.quality_metrics.columns_high_null_threshold
