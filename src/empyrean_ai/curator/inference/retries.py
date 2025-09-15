from __future__ import annotations

import asyncio
import random
from typing import Iterable, Type


async def with_retry(
    coro_fn,
    *args,
    retries: int = 2,
    backoff: float = 0.2,
    retry_on: Iterable[Type[BaseException]] | None = None,
    cap: float = 2.0,
    **kwargs,
):
    """Run ``coro_fn`` with limited retries.

    By default, no retries are performed unless ``retry_on`` is provided.
    When provided, only exceptions matching the types in ``retry_on`` are retried.
    Uses exponential backoff with a small jitter and caps the sleep.
    """

    if retries < 0:
        retries = 0

    if retry_on is None:
        # Safety: require explicit types for retries
        return await coro_fn(*args, **kwargs)

    last: BaseException | None = None
    for i in range(retries + 1):
        try:
            return await coro_fn(*args, **kwargs)
        except BaseException as exc:  # noqa: BLE001 - deliberate broad catch with filter
            # Never retry control-flow exceptions
            if isinstance(exc, (KeyboardInterrupt, SystemExit, GeneratorExit)):
                raise
            if not isinstance(exc, tuple(retry_on)):
                raise
            last = exc
            if i == retries:
                break
            sleep = min(backoff * (2 ** i), cap)
            sleep *= 1.0 + (random.random() * 0.2)  # +0..+20% jitter
            await asyncio.sleep(sleep)

    assert last is not None
    raise last


