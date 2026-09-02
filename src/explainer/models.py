"""
Explanation module data models.

Pydantic models for explanation requests, responses, and configuration.
"""

from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
from datetime import datetime
from enum import Enum


class ExplanationConfig(BaseModel):
    """Configuration for explanation generation."""
    llm_provider: str = "ollama"
    llm_model: str = "llama3.2:3b"
    api_key: Optional[str] = None
    api_base_url: Optional[str] = "http://localhost:11434"
    temperature: float = 0.3
    max_tokens: int = 800
    timeout_seconds: int = 30
    max_retries: int = 2
    fallback_to_template: bool = True


class AnomalyContext(BaseModel):
    """Structured anomaly data for explanation input."""
    anomaly_id: str
    timestamp: datetime
    metric: str
    value: float
    expected_min: float
    expected_max: float
    anomaly_type: str  # spike, drop, deviation
    severity: float  # 0-1
    confidence: float  # 0-100
    dimensions: Dict[str, str] = Field(default_factory=dict)


class RootCauseContext(BaseModel):
    """Root cause analysis results for explanation input."""
    primary_drivers: List[Dict[str, Any]] = Field(default_factory=list)
    correlations: List[Dict[str, Any]] = Field(default_factory=list)
    change_point: Optional[Dict[str, Any]] = None
    hypothesis: str = ""
    confidence: float = 0.0


class RAGContext(BaseModel):
    """Retrieved context documents."""
    documents: List[Dict[str, Any]] = Field(default_factory=list)


class ExplanationRequest(BaseModel):
    """Complete request for explanation generation."""
    anomaly: AnomalyContext
    root_cause: RootCauseContext
    rag_context: Optional[RAGContext] = None
    audience: str = "business"  # business, technical, executive
    include_recommendations: bool = True


class ExplanationResponse(BaseModel):
    """Generated explanation response."""
    anomaly_id: str
    explanation_text: str
    summary: str  # One-line summary
    recommendations: List[str] = Field(default_factory=list)
    confidence: float  # 0-1
    evidence_citations: List[str] = Field(default_factory=list)
    generated_at: datetime = Field(default_factory=datetime.utcnow)
    llm_model: Optional[str] = None
    tokens_input: int = 0
    tokens_output: int = 0
    latency_ms: int = 0
    used_fallback: bool = False

    def to_dict(self) -> Dict[str, Any]:
        return self.model_dump(mode="json")
