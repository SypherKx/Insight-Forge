"""
Pydantic models for the Ingestion Service.

Defines schemas for dataset metadata, column information,
validation reports, and quality metrics.
"""

from datetime import datetime
from typing import List, Optional, Dict, Any
from enum import Enum

from pydantic import BaseModel, Field, validator


class ColumnType(str, Enum):
    """Supported column data types."""
    INTEGER = "integer"
    FLOAT = "float"
    BOOLEAN = "boolean"
    DATETIME = "datetime"
    CATEGORICAL = "categorical"
    TEXT = "text"
    UNKNOWN = "unknown"


class ColumnSchema(BaseModel):
    """Schema for a single column."""
    name: str = Field(..., description="Column name")
    inferred_type: ColumnType = Field(..., description="Inferred data type")
    user_provided_type: Optional[ColumnType] = Field(None, description="User-provided type override")
    nullable_count: int = Field(0, description="Count of null values")
    unique_count: int = Field(0, description="Count of unique values")
    sample_values: List[Any] = Field([], description="Sample values from column")
    is_time_column: bool = Field(False, description="Whether this is the time column")
    is_dimension: bool = Field(False, description="Whether this is a dimension/categorical column")

    @property
    def effective_type(self) -> ColumnType:
        """Get the effective type (user override takes precedence)."""
        return self.user_provided_type if self.user_provided_type else self.inferred_type

    class Config:
        """Pydantic config."""
        json_encoders = {
            # Custom encoding if needed
        }


class DataQualityMetrics(BaseModel):
    """Data quality metrics for a dataset."""
    total_rows: int = Field(..., description="Total number of rows")
    total_columns: int = Field(..., description="Total number of columns")
    missing_values_total: int = Field(0, description="Total missing values across all columns")
    missing_values_percentage: float = Field(0.0, ge=0.0, le=100.0, description="Percentage of missing values")
    duplicate_rows: int = Field(0, description="Number of duplicate rows")
    duplicate_rows_percentage: float = Field(0.0, ge=0.0, le=100.0, description="Percentage of duplicate rows")
    columns_with_missing: List[str] = Field([], description="List of columns with missing values")
    columns_high_null_threshold: List[str] = Field([], description="Columns with >50% null values")
    constant_columns: List[str] = Field([], description="Columns with only one unique value")
    low_variance_columns: List[str] = Field([], description="Columns with very low variance")

    @validator('missing_values_percentage', 'duplicate_rows_percentage', pre=True)
    @classmethod
    def round_percentages(cls, v: float) -> float:
        """Round percentages to 2 decimal places."""
        return round(v, 2)


class ValidationRule(BaseModel):
    """A validation rule definition."""
    rule_type: str = Field(..., description="Type of validation rule")
    column: Optional[str] = Field(None, description="Target column (if applicable)")
    parameters: Dict[str, Any] = Field({}, description="Rule parameters")
    threshold: Optional[float] = Field(None, description="Threshold for the rule")
    severity: str = Field("medium", description="Severity level: low, medium, high, critical")

    class Config:
        """Pydantic config."""
        json_schema_extra = {  # Updated for Pydantic v2
            "example": {
                "rule_type": "missing_values",
                "column": "revenue",
                "parameters": {"max_percentage": 10.0},
                "threshold": 10.0,
                "severity": "high"
            }
        }


class ValidationResult(BaseModel):
    """Result of a validation check."""
    rule: ValidationRule = Field(..., description="Rule that was checked")
    passed: bool = Field(..., description="Whether validation passed")
    severity: str = Field("medium", description="Severity: low, medium, high, critical")
    message: str = Field(..., description="Human-readable message")
    details: Optional[Dict[str, Any]] = Field(None, description="Additional details")

    class Config:
        """Pydantic config."""
        json_schema_extra = {
            "example": {
                "rule": {
                    "rule_type": "missing_values",
                    "column": "revenue",
                    "parameters": {"max_percentage": 10.0}
                },
                "passed": False,
                "severity": "high",
                "message": "Column 'revenue' has 15.2% missing values, exceeding threshold of 10%",
                "details": {"actual_percentage": 15.2, "threshold": 10.0}
            }
        }


class ValidationReport(BaseModel):
    """Complete validation report for a dataset."""
    dataset_id: Optional[str] = Field(None, description="Dataset identifier")
    overall_status: str = Field(..., description="Overall status: passed, warning, failed")
    quality_metrics: DataQualityMetrics = Field(..., description="Data quality metrics")
    validation_results: List[ValidationResult] = Field([], description="Individual validation results")
    warnings: List[str] = Field([], description="Warning messages")
    errors: List[str] = Field([], description="Error messages")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Report creation timestamp")

    @property
    def passed(self) -> bool:
        """Check if all critical validations passed."""
        for result in self.validation_results:
            if result.severity in ["high", "critical"] and not result.passed:
                return False
        return True

    @property
    def has_warnings(self) -> bool:
        """Check if there are any warnings."""
        return len(self.warnings) > 0 or any(not r.passed and r.severity == "low" for r in self.validation_results)


class DatasetStatus(str, Enum):
    """Dataset processing status."""
    UPLOADING = "uploading"
    UPLOADED = "uploaded"
    PARSING = "parsing"
    LOADING = "loading"
    VALIDATING = "validating"
    CLEANING = "cleaning"
    STORING = "storing"
    COMPLETED = "completed"
    FAILED = "failed"


class DatasetMetadata(BaseModel):
    """Metadata for an uploaded dataset."""
    id: str = Field(..., description="Unique dataset identifier")
    name: str = Field(..., description="Dataset name")
    org_id: str = Field(..., description="Organization ID")
    file_path: str = Field(..., description="Storage path (S3 key or local path)")
    file_hash: str = Field(..., description="SHA-256 hash of the file")
    row_count: int = Field(..., description="Number of rows")
    column_count: int = Field(..., description="Number of columns")
    column_schema: List[ColumnSchema] = Field(..., description="Column schemas")
    time_column: Optional[str] = Field(None, description="Name of time column if detected")
    dimensions: List[str] = Field([], description="List of dimension/categorical columns")
    status: DatasetStatus = Field(..., description="Processing status")
    error_message: Optional[str] = Field(None, description="Error message if failed")
    quality_score: Optional[float] = Field(None, ge=0.0, le=1.0, description="Overall quality score")
    uploaded_by: str = Field(..., description="User ID who uploaded")
    uploaded_at: datetime = Field(default_factory=datetime.utcnow, description="Upload timestamp")
    processing_completed_at: Optional[datetime] = Field(None, description="Processing completion timestamp")

    class Config:
        """Pydantic config."""
        json_schema_extra = {
            "example": {
                "id": "550e8400-e29b-41d4-a716-446655440000",
                "name": "sales_data.csv",
                "org_id": "org-123",
                "file_path": "s3://bucket/org-123/dataset-abc/original.csv",
                "file_hash": "a1b2c3d4...",
                "row_count": 150000,
                "column_count": 25,
                "column_schema": [
                    {
                        "name": "date",
                        "inferred_type": "datetime",
                        "nullable_count": 0,
                        "unique_count": 365,
                        "is_time_column": True
                    }
                ],
                "status": "completed",
                "quality_score": 0.95,
                "uploaded_by": "user-456"
            }
        }


class IngestionRequest(BaseModel):
    """Request to upload and process a dataset."""
    name: Optional[str] = Field(None, description="Dataset name (defaults to filename)")
    time_column: Optional[str] = Field(None, description="Column to use as time index")
    dimensions: List[str] = Field([], description="Categorical dimension columns")
    encoding: str = Field("utf-8", description="File encoding")
    delimiter: str = Field(",", description="CSV delimiter")
    quotechar: str = Field('"', description="Quote character")
    escapechar: Optional[str] = Field(None, description="Escape character")

    class Config:
        """Pydantic config."""
        json_schema_extra = {
            "example": {
                "name": "Quarterly Sales Q1 2025",
                "time_column": "transaction_date",
                "dimensions": ["region", "product_category"],
                "delimiter": ",",
                "encoding": "utf-8"
            }
        }


class IngestionResponse(BaseModel):
    """Response after initiating dataset ingestion."""
    dataset_id: str = Field(..., description="Dataset identifier")
    name: str = Field(..., description="Dataset name")
    status: str = Field(..., description="Initial status")
    row_count: int = Field(..., description="Number of rows parsed")
    column_count: int = Field(..., description="Number of columns parsed")
    message: str = Field(..., description="Status message")
    estimated_completion: Optional[datetime] = Field(None, description="Estimated completion time")

    class Config:
        """Pydantic config."""
        json_schema_extra = {
            "example": {
                "dataset_id": "550e8400-e29b-41d4-a716-446655440000",
                "name": "sales_data.csv",
                "status": "parsing",
                "row_count": 150000,
                "column_count": 25,
                "message": "Dataset uploaded successfully, processing started",
                "estimated_completion": "2025-01-15T10:30:00Z"
            }
        }


class PreprocessingConfig(BaseModel):
    """Configuration for data preprocessing."""
    # CSV parsing options
    delimiter: str = Field(",", description="CSV delimiter")
    quotechar: str = Field('"', description="Quote character")
    escapechar: Optional[str] = Field(None, description="Escape character")
    encoding: str = Field("utf-8", description="File encoding")

    # Preprocessing options
    normalize_numeric: bool = Field(True, description="Apply normalization to numeric columns")
    normalization_method: str = Field("standard", description="minmax, standard, robust")
    encode_categorical: bool = Field(False, description="Encode categorical variables")
    categorical_encoding: str = Field("onehot", description="onehot, label, ordinal")
    drop_constant_columns: bool = Field(True, description="Remove columns with constant values")
    drop_high_null_columns: bool = Field(True, description="Remove columns with >80% nulls")
    drop_duplicate_rows: bool = Field(True, description="Remove duplicate rows")
    fill_missing_numeric: Optional[str] = Field("median", description="mean, median, zero, None")
    fill_missing_categorical: Optional[str] = Field("mode", description="mode, missing, None")
    create_time_features: bool = Field(False, description="Extract time-based features")
    time_features: List[str] = Field(["year", "month", "day", "hour", "dayofweek", "is_weekend"], description="Time features to extract")

    class Config:
        """Pydantic config."""
        json_schema_extra = {
            "example": {
                "delimiter": ",",
                "quotechar": '"',
                "encoding": "utf-8",
                "normalize_numeric": True,
                "normalization_method": "standard",
                "drop_duplicate_rows": True,
                "fill_missing_numeric": "median",
                "create_time_features": True
            }
        }
