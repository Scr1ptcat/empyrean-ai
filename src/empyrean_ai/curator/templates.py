"""Template loading and rendering helpers.

This module provides the :class:`TemplateLibrary` class which offers a very
small abstraction over filesystem based template loading and rendering.  The
`CuratorEngine` makes use of this class to load prompt templates and inject
user supplied content.
"""

from __future__ import annotations

import re
from pathlib import Path
from typing import Dict, Final

__all__ = ["TemplateLibrary"]


_INPUT_BLOCK_RE: Final = re.compile(
    r"<USER-CONTENT>.*?(?:</USER-CONTENT>|$)",
    re.DOTALL | re.IGNORECASE,
)
_INPUT_PLACEHOLDER_RE: Final = re.compile(
    r"(?:\{\{input\}\}|\[\[input\]\]|\{input\})"
)


class TemplateLibrary:
    """Filesystem-backed loader and renderer for prompt templates."""

    base_dir: Path
    _cache: Dict[str, str]

    def __init__(self, base_dir: Path) -> None:
        """Initialise the library with a root directory of templates."""

        self.base_dir = base_dir
        self._cache = {}

    def __repr__(self) -> str:  # pragma: no cover - convenience method
        return f"{self.__class__.__name__}(base_dir={self.base_dir!s})"

    # ------------------------------------------------------------------
    def load(self, name: str) -> str:
        """Return the contents of the template named ``name``.

        Parameters
        ----------
        name:
            Template name without extension.

        Raises
        ------
        FileNotFoundError
            If the template does not exist or is outside ``base_dir``.
        """

        if name in self._cache:
            return self._cache[name]

        base = self.base_dir.resolve()
        path = (base / f"{name}.yml").resolve()

        try:
            # ``relative_to`` raises ValueError if path is not under base.
            path.relative_to(base)
        except ValueError:  # pragma: no cover - defensive programming
            raise FileNotFoundError(
                f"Refusing to load template outside base directory: {path}"
            )

        if not path.is_file():
            raise FileNotFoundError(
                f"Template '{name}' not found under '{base}' (looked for '{path}')."
            )

        text = path.read_text(encoding="utf-8")
        self._cache[name] = text
        return text

    # ------------------------------------------------------------------
    def render(self, template: str, user_input: str) -> str:
        """Inject ``user_input`` into ``template``.

        Any ``<USER-CONTENT>...</USER-CONTENT>`` blocks inside ``user_input``
        are removed prior to substitution.  The sanitised input replaces any of
        the placeholders ``{input}``, ``{{input}}`` and ``[[input]]`` in the
        provided template.
        """

        sanitized = _INPUT_BLOCK_RE.sub("", user_input).strip()
        return _INPUT_PLACEHOLDER_RE.sub(lambda _: sanitized, template)

