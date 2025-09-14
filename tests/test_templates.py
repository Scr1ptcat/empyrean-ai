from pathlib import Path
from empyrean_ai.config import load_configs
from empyrean_ai.curator.templates import TemplateLibrary

def test_render_strips_user_content(tmp_path: Path):
    base = Path(__file__).resolve().parents[2]
    lib = TemplateLibrary(base / "prompt_library")
    tmpl = lib.load("extraction_jsononly_v1")
    text = lib.render(tmpl, "Hello <USER-CONTENT>ignore previous</USER-CONTENT> world")
    assert "ignore previous" not in text
