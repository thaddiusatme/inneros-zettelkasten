"""
Template Loader Utility for Test Fixtures

Provides centralized template discovery and loading for test suite.
Templates are stored in fixtures/templates/ directory to avoid depending
on knowledge/ directory which was removed from public repo.

Usage:
    from tests.fixtures.template_loader import get_template_path, TEMPLATES_DIR

    # Get path to specific template
    template_path = get_template_path("youtube-video.md")

    # List all available templates
    templates = list_available_templates()
"""

from pathlib import Path
from typing import List

# Constants
FIXTURES_DIR = Path(__file__).parent
TEMPLATES_DIR = FIXTURES_DIR / "templates"


def get_template_path(template_name: str) -> Path:
    """
    Get absolute path to a template fixture

    Args:
        template_name: Name of template file (e.g., "youtube-video.md")

    Returns:
        Absolute Path to template file

    Raises:
        FileNotFoundError: If template doesn't exist in fixtures

    Example:
        >>> path = get_template_path("daily.md")
        >>> assert path.exists()
    """
    template_path = TEMPLATES_DIR / template_name

    if not template_path.exists():
        # Try finding it recursively if simple path fails
        found = list(TEMPLATES_DIR.rglob(template_name))
        if found:
            return found[0]

        available = list_available_templates()
        raise FileNotFoundError(
            f"Template '{template_name}' not found in fixtures.\n"
            f"Available templates: {', '.join(available)}"
        )

    return template_path


def list_available_templates() -> List[str]:
    """
    List all available template files in fixtures (recursive)

    Returns:
        List of template filenames (relative to templates dir)

    Example:
        >>> templates = list_available_templates()
        >>> assert "Utility/youtube.md" in templates
    """
    if not TEMPLATES_DIR.exists():
        return []

    return sorted(
        [str(f.relative_to(TEMPLATES_DIR)) for f in TEMPLATES_DIR.rglob("*.md")]
    )


def get_template_content(template_name: str) -> str:
    """
    Load and return template content

    Args:
        template_name: Name of template file

    Returns:
        Template content as string

    Raises:
        FileNotFoundError: If template doesn't exist

    Example:
        >>> content = get_template_content("daily.md")
        >>> assert content.startswith("---")
    """
    template_path = get_template_path(template_name)
    return template_path.read_text(encoding="utf-8")
