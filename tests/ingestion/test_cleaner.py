"""
Tests for Data Cleaner module.
"""

import pytest
import pandas as pd
import numpy as np

from src.ingestion.cleaner import DataCleaner
from src.ingestion.models import ColumnSchema, ColumnType, PreprocessingConfig


@pytest.fixture
def sample_schemas():
    """Create sample column schemas for testing."""
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
            is_dimension=True
        ),
        ColumnSchema(
            name="product_category",
            inferred_type=ColumnType.CATEGORICAL,
            nullable_count=0,
            unique_count=5,
            is_time_column=False,
            is_dimension=True
        ),
        ColumnSchema(
            name="quantity",
            inferred_type=ColumnType.INTEGER,
            nullable_count=0,
            unique_count=20,
            is_time_column=False,
            is_dimension=False
        ),
        ColumnSchema(
            name="constant_col",
            inferred_type=ColumnType.CATEGORICAL,
            nullable_count=0,
            unique_count=1,
            is_time_column=False,
            is_dimension=False
        )
    ]


@pytest.fixture
def sample_dataframe(sample_schemas):
    """Create a sample DataFrame with various data quality issues."""
    data = {
        'date': pd.date_range('2025-01-01', periods=100, freq='D'),
        'revenue': np.random.uniform(1000, 10000, 100),
        'region': np.random.choice(['US-East', 'US-West', 'EU-West'], 100),
        'product_category': np.random.choice(['Electronics', 'Furniture', 'Clothing'], 100),
        'quantity': np.random.randint(1, 100, 100),
        'constant_col': ['A'] * 100
    }

    df = pd.DataFrame(data)

    # Introduce missing values
    df.loc[5, 'revenue'] = np.nan
    df.loc[10, 'revenue'] = np.nan
    df.loc[15, 'region'] = None
    df.loc[20, 'product_category'] = np.nan

    # Introduce duplicates (first 5 rows will be duplicated later)
    df_duplicates = pd.concat([df, df.head(5)]).reset_index(drop=True)

    # Introduce outliers in revenue
    df_duplicates.loc[0, 'revenue'] = 1000000  # Very high outlier
    df_duplicates.loc[50, 'revenue'] = 1  # Very low outlier

    return df_duplicates


class TestDataCleaner:
    """Test cases for DataCleaner."""

    def test_remove_duplicates(self, sample_dataframe):
        """Test duplicate removal."""
        cleaner = DataCleaner()
        initial_rows = len(sample_dataframe)

        df_clean = cleaner.remove_duplicates(sample_dataframe)

        assert len(df_clean) < initial_rows
        assert cleaner.report['duplicates_removed'] == initial_rows - len(df_clean)
        assert df_clean.duplicated().sum() == 0

    def test_remove_constant_columns(self, sample_dataframe, sample_schemas):
        """Test constant column removal."""
        cleaner = DataCleaner()

        df_clean, removed = cleaner.remove_constant_columns(sample_dataframe, sample_schemas)

        assert 'constant_col' in removed
        assert 'constant_col' not in df_clean.columns
        assert 'constant_col' in cleaner.report['columns_removed']

    def test_remove_high_null_columns(self, sample_dataframe, sample_schemas):
        """Test high null column removal."""
        # Create a column with >80% nulls (matching DataFrame index length)
        n = len(sample_dataframe)
        sample_dataframe['high_null_col'] = [np.nan] * int(n * 0.8) + [1] * int(n * 0.2)
        sample_schemas.append(ColumnSchema(
            name='high_null_col',
            inferred_type=ColumnType.FLOAT,
            nullable_count=80,
            unique_count=1,
            is_time_column=False,
            is_dimension=False
        ))

        cleaner = DataCleaner()
        df_clean, removed = cleaner.remove_high_null_columns(
            sample_dataframe,
            sample_schemas,
            threshold=0.7
        )

        assert 'high_null_col' in removed
        assert 'high_null_col' not in df_clean.columns

    def test_handle_missing_values_median(self, sample_dataframe, sample_schemas):
        """Test missing value imputation with median."""
        cleaner = DataCleaner(PreprocessingConfig(fill_missing_numeric='median'))

        initial_missing = sample_dataframe['revenue'].isna().sum()
        assert initial_missing > 0

        df_clean = cleaner.handle_missing_values(sample_dataframe, sample_schemas)

        assert df_clean['revenue'].isna().sum() == 0
        assert cleaner.report['missing_values_filled'] > 0

    def test_handle_missing_values_zero(self, sample_dataframe, sample_schemas):
        """Test missing value imputation with zero."""
        cleaner = DataCleaner(PreprocessingConfig(fill_missing_numeric='zero'))

        df_clean = cleaner.handle_missing_values(sample_dataframe, sample_schemas)

        assert df_clean['revenue'].isna().sum() == 0
        # Check that missing values were filled with 0
        assert (df_clean['revenue'] == 0).sum() == 2

    def test_handle_outliers_iqr(self, sample_dataframe, sample_schemas):
        """Test outlier handling with IQR method."""
        cleaner = DataCleaner()

        initial_max = sample_dataframe['revenue'].max()
        initial_min = sample_dataframe['revenue'].min()

        df_clean = cleaner.handle_outliers(
            sample_dataframe,
            sample_schemas,
            method='iqr',
            treatment='cap'
        )

        # After capping, max should be lower and min should be higher
        assert df_clean['revenue'].max() <= initial_max
        assert df_clean['revenue'].min() >= initial_min
        assert cleaner.report['outliers_handled'] > 0

    def test_create_time_features(self, sample_schemas):
        """Test time feature extraction."""
        cleaner = DataCleaner(PreprocessingConfig(create_time_features=True))

        df = pd.DataFrame({
            'date': pd.date_range('2025-01-01', periods=10, freq='D'),
            'value': range(10)
        })

        df_features = cleaner.create_time_features(df, 'date')

        assert f'date_year' in df_features.columns
        assert f'date_month' in df_features.columns
        assert f'date_dayofweek' in df_features.columns
        assert f'date_is_weekend' in df_features.columns

    def test_encode_categorical_label(self, sample_schemas):
        """Test label encoding for categorical variables."""
        cleaner = DataCleaner()

        df = pd.DataFrame({
            'region': ['US-East', 'US-West', 'EU-West', 'US-East', 'US-West'] * 4
        })

        df_encoded, enc_maps = cleaner.encode_categorical(
            df,
            sample_schemas,
            method='label'
        )

        assert 'region_encoded' in df_encoded.columns
        assert 'region' in enc_maps
        assert 'mapping' in enc_maps['region']

    def test_encode_categorical_onehot(self, sample_schemas):
        """Test one-hot encoding for categorical variables."""
        cleaner = DataCleaner()

        df = pd.DataFrame({
            'region': ['US-East', 'US-West', 'EU-West'] * 5
        })

        df_encoded, enc_maps = cleaner.encode_categorical(
            df,
            sample_schemas,
            method='onehot'
        )

        assert 'region_US-East' in df_encoded.columns or any(
            col.startswith('region_') for col in df_encoded.columns
        )
        assert 'region' in enc_maps
        assert 'columns' in enc_maps['region']

    def test_normalize_numeric_standard(self, sample_schemas):
        """Test standard normalization."""
        cleaner = DataCleaner()

        df = pd.DataFrame({
            'revenue': [1000, 2000, 3000, 4000, 5000] * 20,
            'region': ['A'] * 100
        })

        # Update schema for revenue
        revenue_schema = ColumnSchema(
            name='revenue',
            inferred_type=ColumnType.FLOAT,
            nullable_count=0,
            unique_count=5,
            is_time_column=False,
            is_dimension=False
        )

        schemas = [revenue_schema]

        df_norm, params = cleaner.normalize_numeric(df, schemas, method='standard')

        assert 'revenue_normalized' in df_norm.columns
        assert 'revenue' in params
        assert 'mean' in params['revenue']
        assert 'std' in params['revenue']

        # Check that normalized data has mean ~0 and std ~1
        mean = df_norm['revenue_normalized'].mean()
        std = df_norm['revenue_normalized'].std()
        assert abs(mean) < 0.1  # Close to 0
        assert abs(std - 1) < 0.1  # Close to 1

    def test_full_cleaning_pipeline(self, sample_dataframe, sample_schemas):
        """Test complete cleaning pipeline."""
        config = PreprocessingConfig(
            drop_duplicate_rows=True,
            drop_constant_columns=True,
            drop_high_null_columns=True,
            fill_missing_numeric='median',
            create_time_features=False  # date column not actually datetime in sample
        )

        cleaner = DataCleaner(config)

        df_clean, report = cleaner.clean_dataset(
            sample_dataframe,
            sample_schemas,
            time_column='date'
        )

        assert 'constant_col' not in df_clean.columns
        assert len(df_clean) < len(sample_dataframe)
        assert report['rows_before'] == len(sample_dataframe)
        assert report['rows_after'] == len(df_clean)
        assert 'columns_final' in report


class TestPreprocessingConfig:
    """Test preprocessing configuration."""

    def test_default_config(self):
        """Test default configuration values."""
        from src.ingestion.models import PreprocessingConfig

        config = PreprocessingConfig()

        assert config.normalize_numeric is True
        assert config.normalization_method == 'standard'
        assert config.drop_duplicate_rows is True
        assert config.fill_missing_numeric == 'median'
