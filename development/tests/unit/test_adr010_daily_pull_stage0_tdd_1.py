#!/usr/bin/env python3
"""TDD Iteration 1 RED Phase: ADR-010 Daily Content Pull Pipeline Stage 0 - Candidate Selection.

These tests define the desired behaviour for Stage 0 of the ADR-010 daily content
pull pipeline:

- ``DailyPullCandidateResult`` dataclass with ``note_paths``, ``per_note_tokens``,
  ``estimated_total_tokens``.
- ``select_daily_pull_candidates()`` selects notes created/modified in last 24h.
- JSONL logging with ``pipeline: "daily-pull"`` and ``schema_version: "1"``.

The design shares the token estimation utilities from ADR-11 (Mode A) and follows
the same JSONL logging pattern with schema versioning for cross-pipeline analytics.

Scope for this iteration:
- Create ``DailyPullCandidateResult`` dataclass with per-note token budgets.
- Implement ``select_daily_pull_candidates()`` with 24h recency filter.
- Surface ``pipeline`` field in JSONL logs for cross-pipeline aggregation.
"""

from __future__ import annotations

import json
import sys
from datetime import datetime, timedelta
from pathlib import Path
import pytest


# Ensure the development root is on sys.path so the ``src`` package is importable.
CURRENT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = CURRENT_DIR.parent.parent  # /development
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


@pytest.mark.fast
class TestDailyPullCandidateResultDataclassTDDIteration1:
    """DailyPullCandidateResult dataclass for Stage 0 candidate selection.

    These tests assert that:

    - ``DailyPullCandidateResult`` exposes ``note_paths``, ``per_note_tokens``,
      ``estimated_total_tokens`` fields.
    - The invariant ``len(per_note_tokens) == len(note_paths)`` holds.
    - The invariant ``sum(per_note_tokens) == estimated_total_tokens`` holds.
    - Empty selections have consistent empty lists and zero total.
    """

    def test_result_exposes_required_fields(self) -> None:
        """DailyPullCandidateResult must have note_paths, per_note_tokens, estimated_total_tokens."""

        from src.ai.daily_content_pull import DailyPullCandidateResult

        result = DailyPullCandidateResult(
            note_paths=[Path("note-a.md"), Path("note-b.md")],
            per_note_tokens=[600, 400],
            estimated_total_tokens=1000,
        )

        # All required fields must exist.
        assert hasattr(result, "note_paths")
        assert hasattr(result, "per_note_tokens")
        assert hasattr(result, "estimated_total_tokens")

        # Types must be correct.
        assert isinstance(result.note_paths, list)
        assert isinstance(result.per_note_tokens, list)
        assert isinstance(result.estimated_total_tokens, int)

    def test_per_note_tokens_length_matches_note_paths(self) -> None:
        """per_note_tokens length must match note_paths length."""

        from src.ai.daily_content_pull import DailyPullCandidateResult

        result = DailyPullCandidateResult(
            note_paths=[Path("a.md"), Path("b.md"), Path("c.md")],
            per_note_tokens=[100, 200, 150],
            estimated_total_tokens=450,
        )

        assert len(result.per_note_tokens) == len(result.note_paths)

    def test_per_note_tokens_sum_equals_estimated_total_tokens(self) -> None:
        """sum(per_note_tokens) must equal estimated_total_tokens."""

        from src.ai.daily_content_pull import DailyPullCandidateResult

        result = DailyPullCandidateResult(
            note_paths=[Path("x.md"), Path("y.md")],
            per_note_tokens=[1500, 1000],
            estimated_total_tokens=2500,
        )

        # Invariant: aggregate must equal sum of per-note budgets.
        assert sum(result.per_note_tokens) == result.estimated_total_tokens

    def test_empty_selection_has_consistent_empty_fields(self) -> None:
        """Empty selection must have empty lists and zero total."""

        from src.ai.daily_content_pull import DailyPullCandidateResult

        result = DailyPullCandidateResult(
            note_paths=[],
            per_note_tokens=[],
            estimated_total_tokens=0,
        )

        assert result.note_paths == []
        assert result.per_note_tokens == []
        assert result.estimated_total_tokens == 0
        assert len(result.per_note_tokens) == len(result.note_paths)


@pytest.mark.fast
class TestSelectDailyPullCandidatesTDDIteration1:
    """select_daily_pull_candidates() selects notes modified in last 24h.

    These tests assert that:

    - Notes modified within the last 24 hours are included.
    - Notes modified more than 24 hours ago are excluded.
    - Per-note token estimation uses the shared ADR-11 estimator.
    - The sum invariant holds for returned results.
    """

    def _write_note(self, path: Path, body: str, mtime: datetime | None = None) -> None:
        """Write a minimal note with YAML frontmatter and optionally set mtime."""

        lines = [
            "---",
            f"title: {path.stem}",
            f"created: {datetime.now().strftime('%Y-%m-%d')}",
            "---",
            "",
            body,
        ]
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("\n".join(lines) + "\n", encoding="utf-8")

        if mtime is not None:
            import os
            ts = mtime.timestamp()
            os.utime(path, (ts, ts))

    def test_selects_notes_modified_within_24_hours(self, tmp_path: Path) -> None:
        """Notes modified within 24h should be selected."""

        from src.ai.daily_content_pull import select_daily_pull_candidates

        vault_dir = tmp_path / "knowledge"
        inbox_dir = vault_dir / "Inbox"

        # Create a note modified "now" (within 24h window).
        recent_note = inbox_dir / "recent-note.md"
        self._write_note(recent_note, body="Recent content for daily pull")

        result = select_daily_pull_candidates(vault_path=vault_dir)

        assert len(result.note_paths) >= 1
        assert any(p.name == "recent-note.md" for p in result.note_paths)

    def test_excludes_notes_modified_more_than_24_hours_ago(self, tmp_path: Path) -> None:
        """Notes modified more than 24h ago should be excluded."""

        from src.ai.daily_content_pull import select_daily_pull_candidates

        vault_dir = tmp_path / "knowledge"
        inbox_dir = vault_dir / "Inbox"

        # Create a note modified 48 hours ago.
        old_note = inbox_dir / "old-note.md"
        old_time = datetime.now() - timedelta(hours=48)
        self._write_note(old_note, body="Old content", mtime=old_time)

        result = select_daily_pull_candidates(vault_path=vault_dir)

        # Old note should NOT be selected.
        assert not any(p.name == "old-note.md" for p in result.note_paths)

    def test_returns_per_note_tokens_aligned_with_note_paths(self, tmp_path: Path) -> None:
        """Result must have per_note_tokens aligned with note_paths."""

        from src.ai.daily_content_pull import select_daily_pull_candidates

        vault_dir = tmp_path / "knowledge"
        inbox_dir = vault_dir / "Inbox"

        # Create two recent notes with distinct body lengths.
        note_a = inbox_dir / "note-a.md"
        note_b = inbox_dir / "note-b.md"
        self._write_note(note_a, body="A" * 400)  # ~100 tokens
        self._write_note(note_b, body="B" * 800)  # ~200 tokens

        result = select_daily_pull_candidates(vault_path=vault_dir)

        # Result must have per_note_tokens field.
        assert hasattr(result, "per_note_tokens")
        assert isinstance(result.per_note_tokens, list)

        # Length must match note_paths.
        assert len(result.per_note_tokens) == len(result.note_paths)

        # Sum invariant must hold.
        assert sum(result.per_note_tokens) == result.estimated_total_tokens

    def test_empty_vault_returns_empty_result(self, tmp_path: Path) -> None:
        """Empty vault should return empty result with zero tokens."""

        from src.ai.daily_content_pull import select_daily_pull_candidates

        vault_dir = tmp_path / "knowledge"
        vault_dir.mkdir(parents=True, exist_ok=True)

        result = select_daily_pull_candidates(vault_path=vault_dir)

        assert result.note_paths == []
        assert result.per_note_tokens == []
        assert result.estimated_total_tokens == 0

    def test_scans_multiple_directories(self, tmp_path: Path) -> None:
        """Should scan Inbox and Fleeting Notes directories."""

        from src.ai.daily_content_pull import select_daily_pull_candidates

        vault_dir = tmp_path / "knowledge"
        inbox_dir = vault_dir / "Inbox"
        fleeting_dir = vault_dir / "Fleeting Notes"

        # Create notes in different directories.
        inbox_note = inbox_dir / "inbox-note.md"
        fleeting_note = fleeting_dir / "fleeting-note.md"
        self._write_note(inbox_note, body="Inbox content")
        self._write_note(fleeting_note, body="Fleeting content")

        result = select_daily_pull_candidates(vault_path=vault_dir)

        # Both notes should be selected.
        note_names = [p.name for p in result.note_paths]
        assert "inbox-note.md" in note_names
        assert "fleeting-note.md" in note_names


@pytest.mark.fast
class TestDailyPullJSONLLoggingTDDIteration1:
    """JSONL logging for daily pull pipeline sessions.

    These tests assert that:

    - Logs include ``pipeline: "daily-pull"`` for cross-pipeline aggregation.
    - Logs include ``schema_version: "1"`` for schema evolution.
    - Logs include ``per_note_tokens`` aligned with ``selected_notes``.
    - Logs are written to ``development/logs/daily-pull/`` directory.
    """

    def _write_note(self, path: Path, body: str) -> None:
        """Write a minimal note with YAML frontmatter."""

        lines = [
            "---",
            f"title: {path.stem}",
            f"created: {datetime.now().strftime('%Y-%m-%d')}",
            "---",
            "",
            body,
        ]
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("\n".join(lines) + "\n", encoding="utf-8")

    def test_log_includes_pipeline_field_daily_pull(self, tmp_path: Path) -> None:
        """JSONL log must include pipeline: 'daily-pull' for cross-pipeline filtering."""

        from src.ai.daily_content_pull import (
            DailyPullCandidateResult,
            log_daily_pull_session,
        )

        repo_root = tmp_path
        vault_dir = repo_root / "knowledge"
        inbox_dir = vault_dir / "Inbox"

        note = inbox_dir / "test-note.md"
        self._write_note(note, body="Test content for logging")

        result = DailyPullCandidateResult(
            note_paths=[note],
            per_note_tokens=[50],
            estimated_total_tokens=50,
        )

        log_daily_pull_session(
            repo_root=repo_root,
            result=result,
        )

        log_file = repo_root / "development" / "logs" / "daily-pull" / "sessions.jsonl"
        assert log_file.exists(), "Log file should be created"

        log_lines = [
            line for line in log_file.read_text(encoding="utf-8").splitlines() if line.strip()
        ]
        assert log_lines, "Log file should contain at least one record"

        last_record = json.loads(log_lines[-1])

        # Must include pipeline field for cross-pipeline analytics.
        assert "pipeline" in last_record
        assert last_record["pipeline"] == "daily-pull"

    def test_log_includes_schema_version_1(self, tmp_path: Path) -> None:
        """JSONL log must include schema_version: '1'."""

        from src.ai.daily_content_pull import (
            DailyPullCandidateResult,
            log_daily_pull_session,
        )

        repo_root = tmp_path
        vault_dir = repo_root / "knowledge"
        inbox_dir = vault_dir / "Inbox"

        note = inbox_dir / "test-note.md"
        self._write_note(note, body="Test content")

        result = DailyPullCandidateResult(
            note_paths=[note],
            per_note_tokens=[25],
            estimated_total_tokens=25,
        )

        log_daily_pull_session(repo_root=repo_root, result=result)

        log_file = repo_root / "development" / "logs" / "daily-pull" / "sessions.jsonl"
        last_record = json.loads(log_file.read_text().splitlines()[-1])

        # Schema version must be present for backward compatibility.
        assert "schema_version" in last_record
        assert last_record["schema_version"] == "1"

    def test_log_includes_per_note_tokens_aligned_with_selected_notes(
        self, tmp_path: Path
    ) -> None:
        """JSONL log per_note_tokens must align with selected_notes."""

        from src.ai.daily_content_pull import (
            DailyPullCandidateResult,
            log_daily_pull_session,
        )

        repo_root = tmp_path
        vault_dir = repo_root / "knowledge"
        inbox_dir = vault_dir / "Inbox"

        note_a = inbox_dir / "note-a.md"
        note_b = inbox_dir / "note-b.md"
        self._write_note(note_a, body="Content A")
        self._write_note(note_b, body="Content B longer")

        result = DailyPullCandidateResult(
            note_paths=[note_a, note_b],
            per_note_tokens=[100, 200],
            estimated_total_tokens=300,
        )

        log_daily_pull_session(repo_root=repo_root, result=result)

        log_file = repo_root / "development" / "logs" / "daily-pull" / "sessions.jsonl"
        last_record = json.loads(log_file.read_text().splitlines()[-1])

        # per_note_tokens must be present and aligned.
        assert "per_note_tokens" in last_record
        assert "selected_notes" in last_record

        per_note_tokens = last_record["per_note_tokens"]
        selected_notes = last_record["selected_notes"]

        assert len(per_note_tokens) == len(selected_notes)
        assert per_note_tokens == [100, 200]

    def test_log_per_note_tokens_sum_equals_estimated_total_tokens(
        self, tmp_path: Path
    ) -> None:
        """sum(per_note_tokens) must equal estimated_total_tokens in log."""

        from src.ai.daily_content_pull import (
            DailyPullCandidateResult,
            log_daily_pull_session,
        )

        repo_root = tmp_path
        vault_dir = repo_root / "knowledge"
        inbox_dir = vault_dir / "Inbox"

        note = inbox_dir / "note.md"
        self._write_note(note, body="Some content")

        result = DailyPullCandidateResult(
            note_paths=[note],
            per_note_tokens=[150],
            estimated_total_tokens=150,
        )

        log_daily_pull_session(repo_root=repo_root, result=result)

        log_file = repo_root / "development" / "logs" / "daily-pull" / "sessions.jsonl"
        last_record = json.loads(log_file.read_text().splitlines()[-1])

        # Sum invariant must hold in log.
        per_note_tokens = last_record["per_note_tokens"]
        estimated_total = last_record["estimated_total_tokens"]
        assert sum(per_note_tokens) == estimated_total

    def test_log_includes_timestamp(self, tmp_path: Path) -> None:
        """JSONL log must include ISO timestamp."""

        from src.ai.daily_content_pull import (
            DailyPullCandidateResult,
            log_daily_pull_session,
        )

        repo_root = tmp_path
        vault_dir = repo_root / "knowledge"
        inbox_dir = vault_dir / "Inbox"

        note = inbox_dir / "note.md"
        self._write_note(note, body="Content")

        result = DailyPullCandidateResult(
            note_paths=[note],
            per_note_tokens=[10],
            estimated_total_tokens=10,
        )

        log_daily_pull_session(repo_root=repo_root, result=result)

        log_file = repo_root / "development" / "logs" / "daily-pull" / "sessions.jsonl"
        last_record = json.loads(log_file.read_text().splitlines()[-1])

        assert "timestamp" in last_record
        # Timestamp should be ISO format.
        ts = last_record["timestamp"]
        assert isinstance(ts, str)
        assert "T" in ts or "Z" in ts


@pytest.mark.fast
class TestCrossPipelineSchemaAlignmentTDDIteration1:
    """Cross-pipeline schema alignment between Mode A and daily pull.

    These tests document the common schema fields that enable
    cross-pipeline analytics via jq filtering.

    Common fields across pipelines:
    - ``timestamp``: ISO 8601 timestamp
    - ``schema_version``: String version for schema evolution
    - ``pipeline``: Pipeline identifier ("mode-a-low-load" or "daily-pull")
    """

    def test_common_schema_fields_documented(self) -> None:
        """Document the common schema fields for cross-pipeline aggregation.

        This test serves as living documentation for the shared schema.
        Both Mode A and daily pull logs should include these fields.
        """

        common_fields = {
            "timestamp": "ISO 8601 timestamp of the session",
            "schema_version": "String version for backward-compatible evolution",
            "pipeline": "Pipeline identifier for jq filtering",
            "per_note_tokens": "Per-item token counts for granular analytics",
            "estimated_total_tokens": "Sum of per-item tokens",
        }

        # All common fields must be defined.
        assert "timestamp" in common_fields
        assert "schema_version" in common_fields
        assert "pipeline" in common_fields
        assert "per_note_tokens" in common_fields
        assert "estimated_total_tokens" in common_fields


if __name__ == "__main__":  # pragma: no cover
    # Convenience hook to run just this module during RED phase.
    pytest.main([__file__, "-v"])
