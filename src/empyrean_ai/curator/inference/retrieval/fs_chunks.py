from __future__ import annotations

from pathlib import Path
from typing import Literal


def chunk_file(path: Path, mode: Literal["chars", "lines"] = "chars", max_size: int = 2000) -> list[str]:
    text = Path(path).read_text(encoding="utf-8")
    if not text:
        return []
    if max_size <= 0:
        raise ValueError("max_size must be > 0")

    if mode == "lines":
        lines = text.splitlines(keepends=False)
        chunks: list[str] = []
        buf: list[str] = []
        size = 0
        for ln in lines:
            # Wrap single long line to respect max_size
            if len(ln) > max_size:
                if buf:
                    chunks.append("\n".join(buf))
                    buf, size = [], 0
                for i in range(0, len(ln), max_size):
                    chunks.append(ln[i : i + max_size])
                continue
            sep = 1 if buf else 0
            if size + sep + len(ln) > max_size and buf:
                chunks.append("\n".join(buf))
                buf, size = [], 0
                sep = 0
            buf.append(ln)
            size += sep + len(ln)
        if buf:
            chunks.append("\n".join(buf))
        return chunks

    # Char mode
    return [text[i : i + max_size] for i in range(0, len(text), max_size)]

