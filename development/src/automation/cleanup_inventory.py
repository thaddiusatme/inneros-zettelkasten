"""Knowledge base cleanup inventory generator.

This module supports the P0 housekeeping initiative by analyzing documentation
sources and emitting a YAML inventory describing the destination for each
misplaced artifact. The implementation intentionally keeps the GREEN phase
minimal: it only understands project documents living in ``Projects/ACTIVE/``
that should be archived into the October 2025 completion folder. Future
iterations will expand the ruleset and add filesystem scanning utilities and a
dedicated CLI entry point (tracked in project manifest).
"""

from __future__ import annotations

from pathlib import Path
from dataclasses import dataclass
from typing import Iterable, Iterator, Mapping, Sequence
from fnmatch import fnmatch

ARCHIVE_BUCKET = Path("Projects/COMPLETED-2025-10")

# Patterns of source files to exclude from cleanup inventory.
# Use Unix shell-style wildcards (fnmatch). Adjust as needed.
EXCLUDE_PATTERNS = [
    "Projects/ACTIVE/project-todo-v3.md",
    "Projects/ACTIVE/cleanup-inventory-2025-10-lessons-learned.md",
]

REFERENCE_BUCKET = Path("Projects/REFERENCE")
AUTOMATION_DESTINATION = Path("development/src/automation/tools")
AUTOMATION_DEFAULT_MONITOR = "cron-log"
AUTOMATION_DEFAULT_TRIGGER = "schedule"


def generate_inventory(
    *,
    vault_root: Path,
    inventory_path: Path,
    sources: Iterable[str],
) -> None:
    """Write a YAML inventory describing cleanup move recommendations.

    Parameters
    ----------
    vault_root:
        Absolute path to the current vault. Present for compatibility with the
        daemon integration pattern; unused in the GREEN implementation.
    inventory_path:
        Destination for the generated YAML file.
    sources:
        Iterable of source paths (relative to the vault) that require
        classification. Only ``Projects/ACTIVE`` entries are handled today.
    """

    inventory_path = _coerce_path(inventory_path)
    inventory_path.parent.mkdir(parents=True, exist_ok=True)

    records = list(_build_records(sources))

    yaml_lines = ["items:"]
    for record in records:
        yaml_lines.extend(record.to_yaml_lines())

    if len(yaml_lines) == 1:
        yaml_lines.append("  - source: none")
        yaml_lines.append("    destination: none")
        yaml_lines.append("    rationale: no-applicable-moves")

    inventory_path.write_text("\n".join(yaml_lines) + "\n")


def _build_records(sources: Iterable[str]) -> Iterator["InventoryRecord"]:
    for source in sources:
        # Skip any source matching exclusion patterns
        if any(fnmatch(source, pat) for pat in EXCLUDE_PATTERNS):
            continue
        path = Path(source)
        record = _build_record(path)
        if record is not None:
            yield record


def _build_record(source_path: Path) -> "InventoryRecord" | None:
    """Return a minimal inventory record for ACTIVE project artifacts."""

    if _is_projects_active_path(source_path):
        return _build_active_project_record(source_path)

    if _is_development_docs_path(source_path):
        return _build_development_docs_record(source_path)

    if _is_automation_script_path(source_path):
        return _build_automation_script_record(source_path)

    return None


def _is_projects_active_path(path: Path) -> bool:
    try:
        active_index = path.parts.index("ACTIVE")
    except ValueError:
        return False

    return path.parts[: active_index + 1] == ("Projects", "ACTIVE")


def _build_active_project_record(source_path: Path) -> "InventoryRecord":
    year_month = _infer_year_month(source_path)
    archive_bucket = Path(f"Projects/COMPLETED-{year_month}")
    relative_tail = source_path.parts[source_path.parts.index("ACTIVE") + 1 :]
    destination = archive_bucket.joinpath(*relative_tail)

    return InventoryRecord(
        source=str(source_path),
        destination=str(destination),
        rationale="Archive project documentation into monthly completion folder.",
    )


def _is_development_docs_path(path: Path) -> bool:
    return path.parts[:2] == ("development", "docs")


def _build_development_docs_record(source_path: Path) -> "InventoryRecord":
    filename = source_path.name.lower()
    destination = REFERENCE_BUCKET / filename

    return InventoryRecord(
        source=str(source_path),
        destination=str(destination),
        rationale="Promote development documentation into reference library.",
    )


def _is_automation_script_path(path: Path) -> bool:
    return path.parts[:2] == (".automation", "scripts")


def _build_automation_script_record(source_path: Path) -> "InventoryRecord":
    destination = AUTOMATION_DESTINATION / source_path.name

    return InventoryRecord(
        source=str(source_path),
        destination=str(destination),
        rationale="Promote vetted automation script into callable tooling bundle for CLI reuse.",
        metadata=_automation_metadata(),
    )


def _automation_metadata() -> Mapping[str, str]:
    return {
        "trigger": AUTOMATION_DEFAULT_TRIGGER,
        "monitoring": AUTOMATION_DEFAULT_MONITOR,
    }


def _infer_year_month(source_path: Path) -> str:
    """Infer Year-Month archive bucket from filename.

    Simple heuristic for GREEN phase: if filename contains "november", route to
    2025-11. Otherwise default to October (current cleanup sprint)."""

    filename = source_path.name.lower()
    if "november" in filename:
        return "2025-11"
    return "2025-10"


@dataclass(frozen=True)
class InventoryRecord:
    """Simple container for cleanup move recommendations."""

    source: str
    destination: str
    rationale: str
    metadata: Mapping[str, str] | None = None

    def to_yaml_lines(self) -> Sequence[str]:
        lines = [
            f"  - source: {self.source}",
            f"    destination: {self.destination}",
            f"    rationale: {self.rationale}",
        ]

        if self.metadata:
            for key, value in sorted(self.metadata.items()):
                lines.append(f"    {key}: {value}")

        return lines


def _coerce_path(path: Path | str) -> Path:
    return path if isinstance(path, Path) else Path(path)
