from __future__ import annotations

import logging
import os

_configured = False


def setup_logging(default_level: int = logging.INFO) -> None:
    """Configure root logging once with concise formatting.

    Honors EMPYREAN_LOG_LEVEL environment variable when present.
    """
    global _configured
    if _configured:
        return
    level_name = os.environ.get("EMPYREAN_LOG_LEVEL", "")
    level = getattr(logging, level_name.upper(), default_level) if level_name else default_level
    logging.basicConfig(level=level, format="%(asctime)s %(levelname)s %(name)s: %(message)s")
    for noisy in ("httpx", "uvicorn", "asyncio"):
        logging.getLogger(noisy).setLevel(logging.WARNING)
    os.environ.setdefault("EMPYREAN_LOG_PROMPTS", "0")
    _configured = True


