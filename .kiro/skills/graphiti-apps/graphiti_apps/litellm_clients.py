"""
Custom LiteLLM clients for Graphiti.

These allow Graphiti to use GitHub Copilot (and other LiteLLM-supported
providers) without requiring a direct OpenAI API key.  The implementation
follows the pattern established in the simics-mcp-server knowledge_graphs
module and the upstream Graphiti PR #601.
"""

from __future__ import annotations

import asyncio
import logging
import random
from typing import Any

import litellm
from graphiti_core.embedder.client import EmbedderClient

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Retry helper
# ---------------------------------------------------------------------------


async def _retry_with_backoff(
    func,
    max_retries: int = 5,
    initial_delay: float = 1.0,
    max_delay: float = 60.0,
    base: float = 2.0,
):
  """Retry an async callable with exponential back-off on rate-limit errors."""
  delay = initial_delay
  last_exc: Exception | None = None

  for attempt in range(max_retries + 1):
    try:
      return await func()
    except Exception as exc:  # pylint: disable=broad-except
      last_exc = exc
      is_rate_limit = (
          (hasattr(litellm, "RateLimitError") and isinstance(exc, litellm.RateLimitError))
          or any(
              kw in str(exc).lower()
              for kw in ("rate", "limit", "too many requests", "429")
          )
      )
      if is_rate_limit and attempt < max_retries:
        jitter = random.uniform(0, 0.1 * delay)
        wait = min(delay + jitter, max_delay)
        logger.warning(
            "Rate limit hit (attempt %d/%d). Retrying in %.2fs.",
            attempt + 1,
            max_retries + 1,
            wait,
        )
        await asyncio.sleep(wait)
        delay *= base
      else:
        raise

  raise last_exc  # type: ignore[misc]


# ---------------------------------------------------------------------------
# LLM client
# ---------------------------------------------------------------------------


class LiteLLMGraphitiClient:
  """Async LLM client that wraps LiteLLM for use with Graphiti.

  Graphiti calls ``client.chat.completions.create()``.  This class satisfies
  that interface by routing through ``litellm.acompletion``.
  """

  def __init__(self, model: str) -> None:
    self.model = model
    # Graphiti accesses client.chat.completions.create – wire self up.
    self.chat = self
    self.completions = self

  async def create(self, messages, **kwargs) -> Any:
    """Implement the OpenAI chat-completions interface expected by Graphiti."""

    async def _call():
      formatted: list[dict[str, str]] = []
      for msg in messages:
        if hasattr(msg, "role") and hasattr(msg, "content"):
          formatted.append({"role": msg.role, "content": msg.content})
        elif isinstance(msg, dict):
          formatted.append(msg)

      temperature = kwargs.get("temperature", 0.0)
      # GPT-5 only supports temperature=1.
      if "gpt-5" in self.model.lower():
        temperature = 1.0

      response = await litellm.acompletion(
          model=self.model,
          messages=formatted,
          temperature=temperature,
          response_format=kwargs.get("response_format", {"type": "json_object"}),
      )
      return response

    return await _retry_with_backoff(_call)


# ---------------------------------------------------------------------------
# Embedder client
# ---------------------------------------------------------------------------


class LiteLLMGraphitiEmbedder(EmbedderClient):
  """Embedding client that routes through LiteLLM for Graphiti."""

  def __init__(self, model: str, dimensions: int = 1536) -> None:
    self.model = model
    self.dimensions = dimensions

  async def create(self, input_data) -> list[float]:
    """Return a single embedding vector (EmbedderClient interface)."""
    if isinstance(input_data, str):
      return await self._embed_single(input_data)
    if isinstance(input_data, list) and input_data:
      results = await self._embed_batch(input_data)
      return results[0] if results else []
    return await self._embed_single(str(input_data))

  async def create_batch(self, texts: list[str]) -> list[list[float]]:
    """Return a list of embedding vectors."""
    return await self._embed_batch(texts)

  async def _embed_single(self, text: str) -> list[float]:
    async def _call():
      response = await litellm.aembedding(model=self.model, input=[text])
      return response.data[0]["embedding"]

    return await _retry_with_backoff(_call)

  async def _embed_batch(self, texts: list[str]) -> list[list[float]]:
    async def _call():
      response = await litellm.aembedding(model=self.model, input=texts)
      return [item["embedding"] for item in response.data]

    return await _retry_with_backoff(_call)
