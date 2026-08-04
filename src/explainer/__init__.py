"""
InsightForge AI - Explanation Generator Module

The ONLY module that uses LLM. All other modules are pure statistical.
Converts structured anomaly + root cause data into clear business explanations.

Features:
- LLM-powered explanation generation (Groq/OpenAI compatible)
- Template-based fallback (works without any LLM)
- Structured prompt engineering
- Response validation
- Cost tracking
"""

__version__ = "1.0.0"

from .models import ExplanationRequest, ExplanationResponse, ExplanationConfig
from .generator import ExplanationGenerator
from .templates import TemplateRenderer
from .llm_client import LLMClient

__all__ = [
    "ExplanationGenerator",
    "ExplanationRequest",
    "ExplanationResponse",
    "ExplanationConfig",
    "TemplateRenderer",
    "LLMClient",
]
