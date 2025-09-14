from pathlib import Path

import pytest

from empyrean_ai.curator.templates import TemplateLibrary

def test_render_strips_user_content(tmp_path: Path):
    base = Path(__file__).resolve().parents[1]
    lib = TemplateLibrary(base / "prompt_library")
    tmpl = lib.load("extraction_jsononly_v1")
    text = lib.render(tmpl, "Hello <USER-CONTENT>ignore previous</USER-CONTENT> world")
    assert "ignore previous" not in text


def test_render_replaces_all_placeholder_styles(tmp_path: Path) -> None:
    lib = TemplateLibrary(tmp_path)
    template = "A {{input}} B [[input]] C {input}."
    out = lib.render(template, "X")
    assert out == "A X B X C X."


def test_render_no_brace_leftovers(tmp_path: Path) -> None:
    lib = TemplateLibrary(tmp_path)
    assert lib.render("X {{input}} Y", "Q") == "X Q Y"


def test_render_strips_unterminated_tag(tmp_path: Path) -> None:
    lib = TemplateLibrary(tmp_path)
    assert (
        lib.render("A {input} Z", "keep <USER-CONTENT>secret") == "A keep Z"
    )


def test_render_removes_multiple_blocks(tmp_path: Path) -> None:
    lib = TemplateLibrary(tmp_path)
    user = "a <USER-CONTENT>1</USER-CONTENT> b <USER-CONTENT>2</USER-CONTENT> c"
    assert lib.render("{input}", user) == "a  b  c"


def test_load_rejects_traversal(tmp_path: Path) -> None:
    lib = TemplateLibrary(tmp_path)
    with pytest.raises(FileNotFoundError):
        lib.load("../etc/shadow")


def test_load_from_subdir(tmp_path: Path) -> None:
    sub = tmp_path / "x"
    sub.mkdir()
    p = sub / "t.yml"
    p.write_text("ok", encoding="utf-8")
    lib = TemplateLibrary(tmp_path)
    assert lib.load("x/t") == "ok"
