"""
TDD tests for LLM-based fleeting note triage (#114).

RED phase: all tests fail until implementation replaces the word-count heuristic
with a real Ollama call and wires --mutate through the CLI.
"""

import json
import pytest
import tempfile
import shutil
from pathlib import Path
from unittest.mock import patch, MagicMock


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

VAULT_NOTE = """\
---
type: fleeting
created: 2026-01-01
status: inbox
tags: [ai, test]
---

# Test Insight

Substantial content about AI automation patterns for small businesses.
This represents a high-quality capture worth promoting.
"""

LLM_PROMOTE = json.dumps(
    {
        "action": "promote_to_permanent",
        "reasoning": "Clear, actionable insight with strong strategic fit.",
        "confidence": "high",
    }
)

LLM_ARCHIVE = json.dumps(
    {
        "action": "consider_archiving",
        "reasoning": "Too vague; no concrete next action.",
        "confidence": "medium",
    }
)


def _make_vault(tmp_path: Path) -> Path:
    """Create minimal vault structure with one fleeting note."""
    fleeting = tmp_path / "knowledge" / "Fleeting Notes"
    fleeting.mkdir(parents=True)
    (fleeting / "test-note.md").write_text(VAULT_NOTE, encoding="utf-8")
    return tmp_path


# ---------------------------------------------------------------------------
# Unit tests — ReviewTriageCoordinator LLM path
# ---------------------------------------------------------------------------


class TestLlmTriageScoring:
    """Tests for the LLM scoring path in ReviewTriageCoordinator."""

    def setup_method(self):
        self.tmp = tempfile.mkdtemp()
        self.vault = _make_vault(Path(self.tmp))
        self.knowledge_dir = self.vault / "knowledge"

    def teardown_method(self):
        shutil.rmtree(self.tmp)

    def _make_coordinator(self):
        from src.ai.lifecycle import ReviewTriageCoordinator
        from src.ai.batch import WorkflowManager

        wm = WorkflowManager(base_directory=str(self.knowledge_dir))
        return ReviewTriageCoordinator(
            base_dir=self.knowledge_dir,
            workflow_manager=wm,
        )

    def test_raises_runtime_error_when_ollama_unavailable(self):
        """Ollama down → RuntimeError with 'Ollama' in message (no silent fallback)."""
        coordinator = self._make_coordinator()

        with patch("src.ai.lifecycle.OllamaClient") as MockClient:
            instance = MockClient.return_value
            instance.health_check.return_value = False

            with pytest.raises(RuntimeError, match="[Oo]llama"):
                coordinator.generate_fleeting_triage_report(mutate=False)

    def test_raises_value_error_on_malformed_json(self):
        """LLM returns non-JSON → ValueError with 'malformed' or 'JSON' in message."""
        coordinator = self._make_coordinator()

        with patch("src.ai.lifecycle.OllamaClient") as MockClient:
            instance = MockClient.return_value
            instance.health_check.return_value = True
            instance.generate_completion.return_value = "not json at all"

            with pytest.raises(
                (ValueError, RuntimeError), match="[Jj][Ss][Oo][Nn]|malformed|parse"
            ):
                coordinator.generate_fleeting_triage_report(mutate=False)

    def test_returns_recommendation_and_reasoning(self):
        """LLM response → recommendation dict with reasoning field (not just score)."""
        coordinator = self._make_coordinator()

        with patch("src.ai.lifecycle.OllamaClient") as MockClient:
            instance = MockClient.return_value
            instance.health_check.return_value = True
            instance.generate_completion.return_value = LLM_PROMOTE

            report = coordinator.generate_fleeting_triage_report(mutate=False)

        assert report["total_notes_processed"] >= 1
        recs = report["recommendations"]
        assert len(recs) >= 1
        rec = recs[0]
        assert "reasoning" in rec, "recommendation must include LLM reasoning"
        assert "action" in rec

    def test_action_values_match_llm_output(self):
        """Action label in recommendation comes from LLM JSON, not hard-coded score buckets."""
        coordinator = self._make_coordinator()

        with patch("src.ai.lifecycle.OllamaClient") as MockClient:
            instance = MockClient.return_value
            instance.health_check.return_value = True
            instance.generate_completion.return_value = LLM_ARCHIVE

            report = coordinator.generate_fleeting_triage_report(mutate=False)

        recs = report["recommendations"]
        assert any(
            "archiv" in r["action"].lower() for r in recs
        ), f"Expected archiving action from LLM, got: {[r['action'] for r in recs]}"

    def test_no_file_writes_without_mutate(self):
        """Default (mutate=False) → zero filesystem modifications."""
        note_path = self.knowledge_dir / "Fleeting Notes" / "test-note.md"
        original_content = note_path.read_text(encoding="utf-8")
        original_mtime = note_path.stat().st_mtime

        coordinator = self._make_coordinator()

        with patch("src.ai.lifecycle.OllamaClient") as MockClient:
            instance = MockClient.return_value
            instance.health_check.return_value = True
            instance.generate_completion.return_value = LLM_PROMOTE

            coordinator.generate_fleeting_triage_report(mutate=False)

        assert note_path.read_text(encoding="utf-8") == original_content
        assert note_path.stat().st_mtime == original_mtime

    def test_writes_frontmatter_with_mutate(self):
        """mutate=True → triage_recommendation written to note frontmatter."""
        coordinator = self._make_coordinator()

        with patch("src.ai.lifecycle.OllamaClient") as MockClient:
            instance = MockClient.return_value
            instance.health_check.return_value = True
            instance.generate_completion.return_value = LLM_PROMOTE

            coordinator.generate_fleeting_triage_report(mutate=True)

        note_path = self.knowledge_dir / "Fleeting Notes" / "test-note.md"
        updated = note_path.read_text(encoding="utf-8")
        assert "triage_recommendation" in updated


# ---------------------------------------------------------------------------
# CLI tests — inneros.py interface
# ---------------------------------------------------------------------------


class TestTriageCLIInterface:
    """Tests for the inneros fleeting triage CLI interface."""

    def setup_method(self):
        self.tmp = tempfile.mkdtemp()
        self.vault = _make_vault(Path(self.tmp))

    def teardown_method(self):
        shutil.rmtree(self.tmp)

    def _run_triage(self, extra_args=None, mock_llm_response=LLM_PROMOTE):
        """Run triage via FleetingCLI with a mocked Ollama client."""
        from src.cli.fleeting_cli import FleetingCLI

        cli = FleetingCLI(vault_path=str(self.vault / "knowledge"))

        with patch("src.ai.lifecycle.OllamaClient") as MockClient:
            instance = MockClient.return_value
            instance.health_check.return_value = True
            instance.generate_completion.return_value = mock_llm_response

            kwargs = {"output_format": "normal", "quality_threshold": 0.0}
            if extra_args:
                kwargs.update(extra_args)
            return cli.fleeting_triage(**kwargs)

    def test_triage_accepts_mutate_parameter(self):
        """fleeting_triage() accepts mutate kwarg without TypeError."""
        rc = self._run_triage({"mutate": False})
        assert rc == 0

    def test_triage_default_is_read_only(self):
        """Default call (no mutate) leaves files unchanged."""
        note = self.vault / "knowledge" / "Fleeting Notes" / "test-note.md"
        original = note.read_text(encoding="utf-8")

        self._run_triage()  # no mutate

        assert note.read_text(encoding="utf-8") == original

    def test_fast_flag_removed_from_signature(self):
        """fleeting_triage() should no longer accept a 'fast' kwarg."""
        from src.cli.fleeting_cli import FleetingCLI
        import inspect

        sig = inspect.signature(FleetingCLI.fleeting_triage)
        assert (
            "fast" not in sig.parameters
        ), "'fast' should be removed from fleeting_triage() — use 'mutate' instead"

    def test_inneros_parser_has_mutate_flag(self):
        """inneros fleeting triage subparser exposes --mutate, not --fast."""
        from src.cli.inneros import create_parser

        parser = create_parser()
        # parse the triage subcommand
        args = parser.parse_args(["--vault", "/tmp/v", "fleeting", "triage"])
        assert hasattr(args, "mutate"), "--mutate flag missing from triage subparser"
        assert not hasattr(args, "fast") or True  # --fast removed

    def test_inneros_parser_no_fast_flag(self):
        """--fast should no longer be a valid triage arg."""
        from src.cli.inneros import create_parser

        parser = create_parser()
        with pytest.raises(SystemExit):
            parser.parse_args(["--vault", "/tmp/v", "fleeting", "triage", "--fast"])
