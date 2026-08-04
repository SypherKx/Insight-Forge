# InsightForge AI - Ingestion Service

## Overview

The Ingestion Service is the entry point for data into the InsightForge AI platform. It handles CSV file uploads, schema inference, data quality validation, cleaning, and preprocessing before storing raw data and metadata.

## Architecture

```
┌─────────────────┐
│   API Layer     │  FastAPI endpoint
│  POST /upload   │──────────────┐
└─────────────────┘              │
                                ▼
┌────────────────────────────────────────────────────┐
│           IngestionPipeline                        │
│  ┌────────┐  ┌─────────┐  ┌──────────┐          │
│  │ Parser  │ │ Validator│ │ Cleaner  │          │
│  └────────┘  └─────────┘  └──────────┘          │
└────────────────────────────────────────────────────┘
                                │
               ┌────────────────┼────────────────┐
               │                │                │
               ▼                ▼                ▼
        ┌────────────┐  ┌────────────┐  ┌──────────────────┐
        │  Storage   │  │PostgreSQL  │  │ Message Queue    │
        │    S3/     │  │ Metadata   │  │ (async events)   │
        │   Local    │  │            │  │                  │
        └────────────┘  └────────────┘  └──────────────────┘
```

## Components

### 1. IngestionPipeline (`pipeline.py`)

Main orchestrator that coordinates all pipeline stages.

**Key methods:**
- `process_upload()`: Execute complete ingestion workflow
- `get_dataset_status()`: Retrieve dataset processing status
- `list_datasets()`: List datasets for an organization
- `delete_dataset()`: Delete dataset and associated files

**Pipeline stages:**
1. **File validation**: Size, type, structure checks
2. **Schema inference**: Auto-detect column types (datetime, numeric, categorical, text)
3. **Time/Dimension identification**: Identify time column and categorical dimensions
4. **Data loading**: Full CSV read with proper type conversions
5. **Quality validation**: Comprehensive data quality checks
6. **Data cleaning**: Handle missing values, outliers, duplicates, normalization
7. **Storage**: Upload to S3/local filesystem and save metadata to PostgreSQL
8. **Event publishing**: Notify downstream services (async mode)

### 2. CSVParser (`parser.py`)

Handles CSV parsing with intelligent type inference.

**Features:**
- Automatic encoding detection (with chardet)
- Chunked reading for large files
- Time column auto-detection (by name patterns)
- Type inference: datetime, integer, float, boolean, categorical, text
- Validation of CSV structure (duplicate columns, empty files)

**Key methods:**
- `infer_schema()`: Detect column types from data sample
- `read_csv()`: Read CSV with proper dtypes and datetime parsing
- `validate_csv_structure()`: Basic structural validation
- `_detect_encoding()`: Automatic encoding detection with fallback

### 3. DataCleaner (`cleaner.py`)

Data cleaning and preprocessing operations.

**Operations:**
- **Missing value handling**: Fill with mean/median/mode/zero/forward-fill
- **Duplicate removal**: Remove exact duplicate rows
- **Constant column removal**: Drop columns with no variance
- **High-null removal**: Drop columns with >80% missing values
- **Outlier detection**: IQR and Z-score methods with capping/removal
- **Normalization**: Standard, MinMax, Robust scaling
- **Time feature extraction**: Year, month, day, hour, dayofweek, is_weekend, etc.
- **Categorical encoding**: Label encoding, one-hot encoding, ordinal encoding

**Configuration:** Driven by `PreprocessingConfig` model.

**Key methods:**
```python
cleaner = DataCleaner(config)
df_clean, report = cleaner.clean_dataset(df, column_schemas, time_column="date")
```

### 4. DataValidator (`validator.py`)

Comprehensive data quality validation.

**Built-in validation rules:**
- Minimum row count
- Missing value percentage threshold
- Duplicate row percentage threshold
- Constant column detection
- Type consistency checking

**Custom validation support:**
- Range validation (min/max)
- Pattern matching (regex)
- Expression validation (pandas eval)

**Key methods:**
```python
validator = DataValidator()
report = validator.validate_dataset(df, column_schemas)
```

**Report includes:**
- `overall_status`: passed / warning / failed
- `quality_metrics`: Missing %, duplicates %, low-variance columns, etc.
- `validation_results`: Individual rule results with severity
- `warnings` and `errors`: Aggregated messages

### 5. StorageEngine (`storage.py`)

Unified storage interface for files and metadata.

**Storage backends:**
- **Local filesystem**: Configurable base directory
- **S3/MinIO**: Compatible with AWS S3 and self-hosted MinIO

**Database operations:**
- PostgreSQL/SQLite via SQLAlchemy
- Dataset record CRUD
- Automatic table creation

**Key methods:**
- `upload_file()`: Store file to S3 or local
- `download_file()`: Retrieve file from storage
- `create_dataset_record()`: Save metadata to database
- `list_datasets()`: Query datasets with filters

### 6. Models (`models.py`)

Pydantic models for type-safe data structures.

**Core models:**
- `ColumnSchema`: Column metadata (name, type, null count, uniqueness)
- `DatasetMetadata`: Complete dataset metadata
- `DataQualityMetrics`: Quality measurements
- `ValidationRule` / `ValidationResult`: Validation configuration and outcomes
- `ValidationReport`: Complete validation report
- `IngestionRequest`: API request parameters
- `IngestionResponse`: API response
- `PreprocessingConfig`: Cleaning and preprocessing options

**Enums:**
- `ColumnType`: INTEGER, FLOAT, BOOLEAN, DATETIME, CATEGORICAL, TEXT, UNKNOWN
- `DatasetStatus`: UPLOADING, PARSING, VALIDATING, CLEANING, STORING, COMPLETED, FAILED

## Usage

### Basic Usage

```python
from src.ingestion import IngestionPipeline, StorageEngine, PreprocessingConfig

# Initialize storage (local example)
storage = StorageEngine(
    storage_type="local",
    base_path="./data",
    database_url="sqlite:///./data/metadata.db"
)

# Configure preprocessing
config = PreprocessingConfig(
    drop_duplicate_rows=True,
    fill_missing_numeric="median",
    create_time_features=True,
    normalize_numeric=True,
    normalization_method="standard"
)

# Create pipeline
pipeline = IngestionPipeline(
    storage_engine=storage,
    preprocessing_config=config,
    max_file_size_mb=500
)

# Process upload
result = pipeline.process_upload(
    file_path=Path("./sales_data.csv"),
    request=IngestionRequest(
        name="Q1 2025 Sales",
        time_column="transaction_date",
        dimensions=["region", "product_category"]
    ),
    org_id="org-123",
    user_id="user-456"
)

if result.success:
    print(f"Dataset uploaded: {result.dataset_id}")
    print(f"Rows: {result.metadata.row_count}, Columns: {result.metadata.column_count}")
    print(f"Quality score: {result.metadata.quality_score}")
else:
    print(f"Failed: {result.error}")
```

### S3 Storage Configuration

```python
from src.ingestion import StorageEngine

storage = StorageEngine(
    storage_type="s3",
    s3_endpoint="https://s3.amazonaws.com",  # or MinIO endpoint
    s3_access_key="your-access-key",
    s3_secret_key="your-secret-key",
    s3_bucket="insightforge-raw",
    s3_region="us-east-1",
    database_url="postgresql://user:pass@localhost/metadata"
)
```

### Advanced Validation

```python
from src.ingestion import DataValidator, ValidationRule
from src.ingestion.models import ColumnSchema, ColumnType

# Custom validation rules
custom_rules = [
    ValidationRule(
        rule_type="custom_range",
        column="revenue",
        parameters={"min": 0, "max": 1000000},
        threshold=0.01,  # Allow 1% outliers
        severity="medium"
    ),
    ValidationRule(
        rule_type="custom_pattern",
        column="email",
        parameters={"pattern": r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"},
        threshold=0,
        severity="high"
    )
]

validator = DataValidator(custom_rules=custom_rules)
report = validator.validate_dataset(df, column_schemas)

if report.overall_status == "failed":
    for error in report.errors:
        print(f"Error: {error}")

if report.has_warnings:
    for warning in report.warnings:
        print(f"Warning: {warning}")
```

## Testing

Run tests with pytest:

```bash
# Install dependencies
pip install -r requirements.txt

# Run all tests
pytest tests/ingestion/ -v

# Run specific test file
pytest tests/ingestion/test_parser.py -v

# Run with coverage
pytest tests/ingestion/ --cov=src/ingestion --cov-report=html

# Run slow tests
pytest -m slow
```

## Configuration Options

### PreprocessingConfig

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `normalize_numeric` | bool | True | Apply normalization to numeric columns |
| `normalization_method` | str | "standard" | minmax, standard, robust |
| `encode_categorical` | bool | False | Encode categorical variables |
| `categorical_encoding` | str | "onehot" | onehot, label, ordinal |
| `drop_constant_columns` | bool | True | Remove columns with only one unique value |
| `drop_high_null_columns` | bool | True | Remove columns with >80% nulls |
| `drop_duplicate_rows` | bool | True | Remove duplicate rows |
| `fill_missing_numeric` | str | "median" | mean, median, zero, None |
| `fill_missing_categorical` | str | "mode" | mode, missing, None |
| `create_time_features` | bool | False | Extract time-based features |
| `time_features` | List[str] | [...] | Features to extract from datetime |

### StorageEngine Configuration

```python
# Local storage
StorageEngine(
    storage_type="local",
    base_path="/path/to/storage"
)

# S3 storage
StorageEngine(
    storage_type="s3",
    s3_endpoint="https://s3.amazonaws.com",
    s3_access_key="...",
    s3_secret_key="...",
    s3_bucket="my-bucket",
    s3_region="us-east-1"
)

# Database
StorageEngine(
    database_url="postgresql://user:pass@host:port/dbname"
    # or SQLite: "sqlite:///path/to/file.db"
)
```

## Database Schema

The `datasets` table stores metadata:

```sql
CREATE TABLE datasets (
    id UUID PRIMARY KEY,
    org_id VARCHAR NOT NULL,
    name VARCHAR(255) NOT NULL,
    file_path VARCHAR(500) NOT NULL,
    file_hash VARCHAR(64) NOT NULL,
    row_count INTEGER NOT NULL,
    column_count INTEGER NOT NULL,
    column_schema JSONB NOT NULL,
    time_column VARCHAR(100),
    dimensions JSONB,
    status VARCHAR(50) DEFAULT 'uploading',
    error_message TEXT,
    quality_score INTEGER,  -- 0-100
    uploaded_by VARCHAR NOT NULL,
    uploaded_at TIMESTAMPTZ DEFAULT NOW(),
    processing_completed_at TIMESTAMPTZ
);

CREATE INDEX idx_datasets_org ON datasets(org_id);
CREATE INDEX idx_datasets_status ON datasets(status);
CREATE INDEX idx_datasets_hash ON datasets(file_hash);  -- For deduplication
```

## Error Handling

The pipeline handles various error conditions:

- **File validation errors**: Size limit, unsupported type, empty file
- **Parsing errors**: Malformed CSV, encoding issues, duplicate columns
- **Memory errors**: Large files (consider chunked processing)
- **Storage errors**: Upload failures, permission issues
- **Database errors**: Connection issues, constraint violations

All errors are logged and returned with structured messages.

## Logging

The module uses Python's standard logging. Configure logging in your application:

```python
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
```

Log levels:
- **INFO**: Normal operations (dataset uploaded, completed)
- **WARNING**: Recoverable issues (missing values detected)
- **ERROR**: Failures, exceptions
- **DEBUG**: Detailed internal state (enable for troubleshooting)

## Performance Considerations

- **Chunked reading**: For files >10,000 rows, use chunked reading
- **Schema inference sampling**: Only samples first 10,000 rows by default
- **Memory efficiency**: Avoids loading full large files into memory during schema inference
- **Type optimization**: Uses pandas nullable types (Int64, boolean) for memory efficiency

## Limitations

- Maximum file size: Configurable (default 500MB)
- Maximum columns: No hard limit, but >10,000 columns may impact performance
- Encoding: UTF-8 primary, with fallback to latin-1; others require explicit setting
- Time parsing: Limited to pandas datetime formats; custom formats not yet supported

## Future Enhancements

- [ ] Support for additional file formats (Parquet, Excel, JSON)
- [ ] Incremental updates (append new data to existing datasets)
- [ ] Schema evolution tracking
- [ ] Distributed processing for very large files
- [ ] Streaming upload support
- [ ] Data lineage tracking
- [ ] PII detection and anonymization

## Production Deployment

### Environment Variables

```bash
# Storage
STORAGE_TYPE=local  # or s3
STORAGE_BASE_PATH=/data
S3_ACCESS_KEY=...
S3_SECRET_KEY=...
S3_BUCKET=insightforge-raw

# Database
DATABASE_URL=postgresql://...

# Application
MAX_FILE_SIZE_MB=500
ENABLE_ASYNC=true
```

### Health Checks

```python
# Check pipeline health
stats = pipeline.get_stats()
print(f"Processed: {stats['datasets_processed']}")
print(f"Errors: {stats['total_errors']}")
print(f"Avg processing time: {stats['avg_processing_time_sec']:.2f}s")
```

### Monitoring

Key metrics to monitor:
- Upload success rate
- Average processing time
- Validation failure rate
- Quality scores distribution
- Storage utilization
- Database connection pool

## API Reference

See method docstrings for detailed signatures.

### IngestionPipeline

```python
def process_upload(
    file_path: Path,
    request: IngestionRequest,
    org_id: str,
    user_id: str
) -> PipelineResult: ...

def get_dataset_status(dataset_id: str) -> Optional[DatasetMetadata]: ...

def list_datasets(
    org_id: str,
    status: Optional[str] = None,
    limit: int = 100,
    offset: int = 0
) -> List[DatasetMetadata]: ...

def delete_dataset(dataset_id: str, org_id: str) -> bool: ...

def get_stats() -> Dict[str, Any]: ...
```

## License

Copyright © 2025 InsightForge AI. All rights reserved.
