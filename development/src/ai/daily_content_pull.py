"""ADR-010 Daily Content Pull Pipeline - Stage 0: Candidate Selection.

This module implements Stage 0 of the ADR-010 daily content pull pipeline,
which selects notes created or modified within the last 24 hours for
downstream processing (summarization, batch review, content synthesis).

The design shares token estimation utilities with Mode A (ADR-11) and follows
the same JSONL logging pattern with schema versioning for cross-pipeline
analytics.

Architecture (ADR-010 Section 4):
- Stage 0: Candidate Selection (this module)
- Stage 1: Summary Assurance
- Stage 2: Batch Review  
- Stage 3: Blender Synthesis
"""

from __future__ import annotations

import json
import os
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from pathlib import Path
from typing import List

from src.utils.token_estimation import estimate_tokens
from src.utils.frontmatter import parse_frontmatter


@dataclass
class DailyPullCandidateResult:
    """Result container for Stage 0 candidate selection.

    Parameters
    ----------
    note_paths:
        Ordered list of selected note paths.
    per_note_tokens:
        Per-note token counts aligned index-by-index with ``note_paths``.
        The invariant ``sum(per_note_tokens) == estimated_total_tokens`` holds.
    estimated_total_tokens:
        Sum of per-note token estimates.
    """

    note_paths: List[Path]
    per_note_tokens: List[int]
    estimated_total_tokens: int


def select_daily_pull_candidates(
    *,
    vault_path: Path,
    recency_hours: int = 24,
    now: datetime | None = None,
) -> DailyPullCandidateResult:
    """Select notes created or modified within the recency window.

    Parameters
    ----------
    vault_path:
        Root path of the knowledge vault.
    recency_hours:
        Number of hours to look back for recent modifications (default 24).
    now:
        Optional override for current time (useful for testing).

    Returns
    -------
    DailyPullCandidateResult
        Container with selected note paths and per-note token estimates.
    """

    base_dir = Path(vault_path)
    current_time = now or datetime.now()
    cutoff_time = current_time - timedelta(hours=recency_hours)

    # Candidate directories aligned with ADR-010 and existing workflow patterns.
    candidate_dirs = [
        base_dir / "Inbox",
        base_dir / "Fleeting Notes",
    ]

    raw_paths: List[Path] = []
    for directory in candidate_dirs:
        if not directory.exists():
            continue
        for path in directory.rglob("*.md"):
            if path.is_file():
                raw_paths.append(path)

    # Filter by modification time within recency window.
    recent_paths: List[Path] = []
    for path in raw_paths:
        try:
            mtime = datetime.fromtimestamp(os.path.getmtime(path))
            if mtime >= cutoff_time:
                recent_paths.append(path)
        except OSError:
            # Skip files we cannot stat.
            continue

    if not recent_paths:
        return DailyPullCandidateResult(
            note_paths=[],
            per_note_tokens=[],
            estimated_total_tokens=0,
        )

    # Compute per-note token estimates using shared ADR-11 estimator.
    per_note_tokens: List[int] = []
    for path in recent_paths:
        try:
            content = path.read_text(encoding="utf-8")
            _, body = parse_frontmatter(content)
            tokens = estimate_tokens(body)
            per_note_tokens.append(tokens)
        except OSError:
            per_note_tokens.append(0)

    estimated_total = sum(per_note_tokens)

    return DailyPullCandidateResult(
        note_paths=recent_paths,
        per_note_tokens=per_note_tokens,
        estimated_total_tokens=estimated_total,
    )


def log_daily_pull_session(
    *,
    repo_root: Path,
    result: DailyPullCandidateResult,
) -> None:
    """Log a daily pull session to JSONL for cross-pipeline analytics.

    Parameters
    ----------
    repo_root:
        Repository root directory (logs written under development/logs/).
    result:
        Candidate selection result to log.
    """

    log_dir = repo_root / "development" / "logs" / "daily-pull"
    log_dir.mkdir(parents=True, exist_ok=True)
    log_file = log_dir / "sessions.jsonl"

    # Build relative paths for logging.
    vault_path = repo_root / "knowledge"
    selected_notes: List[str] = []
    for path in result.note_paths:
        try:
            rel = str(path.relative_to(vault_path))
        except ValueError:
            rel = str(path)
        selected_notes.append(rel)

    # ISO timestamp with UTC.
    ts = datetime.now(UTC).isoformat()
    if ts.endswith("+00:00"):
        ts = ts[:-6] + "Z"

    record = {
        "timestamp": ts,
        "pipeline": "daily-pull",
        "schema_version": "1",
        "selected_notes": selected_notes,
        "per_note_tokens": list(result.per_note_tokens),
        "estimated_total_tokens": result.estimated_total_tokens,
    }

    with log_file.open("a", encoding="utf-8") as fp:
        fp.write(json.dumps(record, ensure_ascii=False) + "\n")
