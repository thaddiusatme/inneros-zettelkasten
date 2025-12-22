import re
import sys
from pathlib import Path

import pytest

# Add development directory to path for fixtures import
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from tests.fixtures.template_loader import TEMPLATES_DIR


def _has_tp_move(content: str) -> bool:
    """Return True if template content contains a tp.file.move call that targets Inbox/ ."""
    pattern = re.compile(r"tp\.file\.move\(", re.IGNORECASE)
    return bool(pattern.search(content))


# Trigger templates process other notes but don't need to relocate themselves
TRIGGER_TEMPLATES = {"simple-youtube-trigger.md"}


@pytest.mark.parametrize("template_path", sorted(TEMPLATES_DIR.glob("*.md")))
def test_template_auto_moves_out_of_templates(template_path: Path):
    """Ensure every Obsidian template auto-moves generated note to Inbox/."""
    if template_path.name in TRIGGER_TEMPLATES:
        pytest.skip(
            f"Trigger template {template_path.name} processes other notes, doesn't need tp.file.move()"
        )
    content = template_path.read_text(encoding="utf-8")
    assert _has_tp_move(
        content
    ), f"Template {template_path.name} does not contain a `tp.file.move()` call. Ensure the template relocates generated notes out of `Templates/`."
