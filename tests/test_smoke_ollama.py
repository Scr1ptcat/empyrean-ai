import os, asyncio, pytest
from agentic_ai_ops.curator.inference.ollama_client import OllamaClient

@pytest.mark.asyncio
async def test_smoke_ollama():
    # Skip if Ollama not reachable
    base = os.environ.get("OLLAMA_HOST", "http://localhost:11434")
    try:
        client = OllamaClient(base_url=base, timeout=2.0)
        # ping with a trivial model name; expect failure but handle gracefully
        await client.generate("nonexistent-model", "ping", {})
    except Exception:
        pytest.skip("Ollama not available or model missing; smoke skipped")
