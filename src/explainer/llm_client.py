"""
LLM Client — Thin API wrapper for explanation generation.

Supports OpenAI-compatible APIs (OpenAI, Groq, Together, etc.).
Includes retry logic, timeout handling, and token tracking.
"""

import os
import time
import json
import logging
from typing import Dict, Any, Optional, Tuple

import httpx

from .models import ExplanationConfig

logger = logging.getLogger(__name__)

# Default API endpoints
API_ENDPOINTS = {
    "groq": "https://api.groq.com/openai/v1/chat/completions",
    "openai": "https://api.openai.com/v1/chat/completions",
    "together": "https://api.together.xyz/v1/chat/completions",
}


class LLMClient:
    """
    OpenAI-compatible LLM API client.

    Supports Groq, OpenAI, Together, and any OpenAI-compatible endpoint.
    """

    def __init__(self, config: Optional[ExplanationConfig] = None):
        """
        Initialize LLM client.

        Args:
            config: ExplanationConfig with API settings
        """
        self.config = config or ExplanationConfig()

        # Resolve API key
        self.api_key = self.config.api_key or os.getenv(
            f"{self.config.llm_provider.upper()}_API_KEY", ""
        )

        # Resolve base URL
        if self.config.api_base_url:
            self.base_url = self.config.api_base_url
        else:
            self.base_url = API_ENDPOINTS.get(
                self.config.llm_provider,
                API_ENDPOINTS["groq"]
            )

        self._available = bool(self.api_key)

        if not self._available:
            logger.warning(
                f"No API key found for {self.config.llm_provider}. "
                f"Set {self.config.llm_provider.upper()}_API_KEY environment variable. "
                f"Template fallback will be used."
            )

    @property
    def is_available(self) -> bool:
        """Check if LLM client has valid credentials."""
        return self._available

    def generate(
        self,
        system_prompt: str,
        user_prompt: str,
    ) -> Tuple[str, Dict[str, Any]]:
        """
        Generate LLM completion.

        Args:
            system_prompt: System instruction
            user_prompt: User message with data

        Returns:
            Tuple of (response_text, usage_metadata)

        Raises:
            LLMError: If all retries fail
        """
        if not self.is_available:
            raise LLMUnavailableError("No API key configured")

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ]

        payload = {
            "model": self.config.llm_model,
            "messages": messages,
            "temperature": self.config.temperature,
            "max_tokens": self.config.max_tokens,
        }

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

        last_error = None

        for attempt in range(self.config.max_retries + 1):
            try:
                start_time = time.time()

                with httpx.Client(timeout=self.config.timeout_seconds) as client:
                    response = client.post(
                        self.base_url,
                        json=payload,
                        headers=headers,
                    )

                latency_ms = int((time.time() - start_time) * 1000)

                if response.status_code == 200:
                    data = response.json()
                    text = data["choices"][0]["message"]["content"]
                    usage = data.get("usage", {})

                    metadata = {
                        "model": data.get("model", self.config.llm_model),
                        "tokens_input": usage.get("prompt_tokens", 0),
                        "tokens_output": usage.get("completion_tokens", 0),
                        "latency_ms": latency_ms,
                    }

                    logger.info(
                        f"LLM response ({latency_ms}ms, "
                        f"{metadata['tokens_input']}+{metadata['tokens_output']} tokens)"
                    )
                    return text, metadata

                elif response.status_code == 429:
                    # Rate limited — wait and retry
                    wait = 2 ** attempt
                    logger.warning(f"Rate limited, retrying in {wait}s...")
                    time.sleep(wait)
                    continue

                else:
                    error_body = response.text[:200]
                    last_error = f"API error {response.status_code}: {error_body}"
                    logger.error(last_error)

            except httpx.TimeoutException:
                last_error = f"Timeout after {self.config.timeout_seconds}s"
                logger.warning(f"Attempt {attempt + 1}: {last_error}")

            except Exception as e:
                last_error = str(e)
                logger.error(f"Attempt {attempt + 1} failed: {e}")

            if attempt < self.config.max_retries:
                time.sleep(1)

        raise LLMError(f"All {self.config.max_retries + 1} attempts failed: {last_error}")


class LLMError(Exception):
    """LLM API call failed."""
    pass


class LLMUnavailableError(LLMError):
    """LLM not configured / no API key."""
    pass
