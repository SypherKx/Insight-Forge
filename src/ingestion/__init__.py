"""
InsightForge AI - Ingestion Service Module

Provides CSV ingestion pipeline with parsing, validation, cleaning,
and storage capabilities.

Key Components:
- IngestionPipeline: Main orchestrator
- CSVParser: Schema inference and CSV reading
- DataCleaner: Data cleaning and preprocessing
- DataValidator: Data quality validation
- StorageEngine: File and metadata persistence
"""

from .pipeline import IngestionPipeline, PipelineResult
from .parser import CSVParser
from .cleaner import DataCleaner, clean_data
from .validator import (
    DataValidator,
    validate_dataset,
    create_default_validation_rules,
    ValidationRule,
    ValidationResult,
    ValidationReport
)
from .storage import StorageEngine, DatasetRecord
from .models import (
    ColumnSchema,
    ColumnType,
    DatasetMetadata,
    DatasetStatus,
    DataQualityMetrics,
    IngestionRequest,
    IngestionResponse,
    PreprocessingConfig,
    ValidationRule as ModelValidationRule,
    ValidationResult as ModelValidationResult,
    ValidationReport as ModelValidationReport
)

__version__ = "1.0.0"
__author__ = "InsightForge AI"

__all__ = [
    # Pipeline
    "IngestionPipeline",
    "PipelineResult",

    # Parser
    "CSVParser",

    # Cleaner
    "DataCleaner",
    "clean_data",

    # Validator
    "DataValidator",
    "validate_dataset",
    "create_default_validation_rules",
    "ValidationRule",
    "ValidationResult",
    "ValidationReport",

    # Storage
    "StorageEngine",
    "DatasetRecord",

    # Models
    "ColumnSchema",
    "ColumnType",
    "DatasetMetadata",
    "DatasetStatus",
    "DataQualityMetrics",
    "IngestionRequest",
    "IngestionResponse",
    "PreprocessingConfig",
    "ModelValidationRule",
    "ModelValidationResult",
    "ModelValidationReport"
]
