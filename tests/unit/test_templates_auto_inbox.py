import re
from pathlib import Path

import pytest

ROOT_DIR = Path(__file__).resolve().parents[2]
TEMPLATES_DIR = ROOT_DIR / "Templates"


def _has_tp_move(content: str) -> bool:
    """Return True if template content contains a tp.file.move call that targets Inbox/ ."""
    pattern = re.compile(r"tp\.file\.move\(", re.IGNORECASE)
    return bool(pattern.search(content))


@pytest.mark.parametrize("template_path", sorted(TEMPLATES_DIR.glob("*.md")))
def test_template_auto_moves_out_of_templates(template_path: Path):
    """Ensure every Obsidian template auto-moves generated note to Inbox/."""
    content = template_path.read_text(encoding="utf-8")
    assert _has_tp_move(content), (
        f"Template {template_path.name} does not contain a `tp.file.move()` call. Ensure the template relocates generated notes out of `Templates/`."
    )
