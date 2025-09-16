from __future__ import annotations

import os
import time
import uuid
from typing import Any

import httpx

from .retries import with_retry


class OllamaClient:
    """Thin async client for Ollama's /api/generate endpoint.

    Returns a dict compatible with CuratorEngine expectations.
    """

    def __init__(self, base_url: str | None = None, timeout: float = 30.0, client: httpx.AsyncClient | None = None):
        base = base_url or os.environ.get("OLLAMA_HOST", "http://localhost:11434")
        self.base_url = base.rstrip("/")
        self.timeout = timeout
        self._client = client

    async def generate(self, model: str, prompt: str, options: dict | None = None) -> dict:
        body: dict[str, Any] = {"model": model, "prompt": prompt, "stream": False}
        if options:
            body["options"] = options
        url = f"{self.base_url}/api/generate"

        async def _once() -> httpx.Response:
            if self._client is not None:
                r = await self._client.post(url, json=body, timeout=self.timeout)
                r.raise_for_status()
                return r
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                r = await client.post(url, json=body)
                r.raise_for_status()
                return r

        t0 = time.perf_counter()
        # Only retry network exceptions by default
        r = await with_retry(
            _once,
            retries=2,
            backoff=0.25,
            retry_on=(httpx.RequestError, httpx.TimeoutException),
        )
        data = r.json()
        req_id = r.headers.get("X-Request-ID") or uuid.uuid4().hex
        return {
            "text": data.get("response", ""),
            "elapsed": time.perf_counter() - t0,
            "raw": data,
            "model": model,
            "request_id": req_id,
        }


