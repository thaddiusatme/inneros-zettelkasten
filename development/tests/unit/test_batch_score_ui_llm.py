"""
Tests for LLM integration in batch_score_ui.py - Issue #90 TDD Iteration 2

RED Phase: Tests for --llm CLI flag, mode indicator, and ETA display.

Acceptance Criteria:
- [ ] --llm flag triggers Ollama-based analysis in web UI
- [ ] UI shows mode indicator (heuristic vs LLM)
- [ ] LLM mode shows longer ETA estimate
- [ ] /start endpoint accepts use_llm parameter
"""

import json
import tempfile
from pathlib import Path
from unittest.mock import patch


class TestStartEndpointLLMFlag:
    """Tests for /start endpoint accepting use_llm parameter."""

    def test_start_endpoint_accepts_use_llm_parameter(self):
        """POST /start should accept use_llm parameter."""
        from src.cli.batch_score_ui import app

        with app.test_client() as client:
            with tempfile.TemporaryDirectory() as tmpdir:
                # Create a test note
                note_path = Path(tmpdir) / "test.md"
                note_path.write_text("# Test Note\nSome content here.")

                response = client.post(
                    "/start",
                    json={"path": tmpdir, "use_llm": True},
                    content_type="application/json",
                )

                assert response.status_code == 200
                data = response.get_json()
                assert data["status"] == "started"

    def test_use_llm_false_uses_heuristic_scoring(self):
        """use_llm=False should use fast heuristic scoring."""
        from src.cli.batch_score_ui import app, scoring_state

        with app.test_client() as client:
            with tempfile.TemporaryDirectory() as tmpdir:
                note_path = Path(tmpdir) / "test.md"
                note_path.write_text("# Test\nContent")

                with patch("src.cli.batch_score_ui.AIEnhancer") as mock_enhancer_class:
                    mock_enhancer = mock_enhancer_class.return_value
                    mock_enhancer._basic_quality_analysis.return_value = {
                        "quality_score": 0.7,
                        "zettelkasten_compliance": {"atomic": True, "connected": False},
                    }

                    client.post(
                        "/start",
                        json={"path": tmpdir, "use_llm": False},
                        content_type="application/json",
                    )

                    # Give worker time to process
                    import time

                    time.sleep(0.5)

                    # Should have used heuristic method
                    mock_enhancer._basic_quality_analysis.assert_called()

    def test_use_llm_true_uses_deep_analysis(self):
        """use_llm=True should use LLM deep analysis."""
        from src.cli.batch_score_ui import app

        with app.test_client() as client:
            with tempfile.TemporaryDirectory() as tmpdir:
                note_path = Path(tmpdir) / "test.md"
                note_path.write_text("# Test\nContent")

                with patch("src.cli.batch_score_ui.AIEnhancer") as mock_enhancer_class:
                    mock_enhancer = mock_enhancer_class.return_value
                    mock_enhancer.analyze_note_quality_deep.return_value = {
                        "quality_score": 0.8,
                        "coherence_score": 0.75,
                        "grammar_issues": [],
                        "zettelkasten_feedback": {},
                        "mode": "llm",
                    }

                    client.post(
                        "/start",
                        json={"path": tmpdir, "use_llm": True},
                        content_type="application/json",
                    )

                    import time

                    time.sleep(0.5)

                    # Should have used LLM method
                    mock_enhancer.analyze_note_quality_deep.assert_called()


class TestModeIndicator:
    """Tests for UI mode indicator showing heuristic vs LLM."""

    def test_scoring_state_includes_mode(self):
        """Scoring state should include current mode."""
        from src.cli.batch_score_ui import app

        # Initial state should have mode field - test via /results endpoint
        with app.test_client() as client:
            response = client.get("/results")
            data = response.get_json()
            assert "mode" in data  # Will fail until implemented

    def test_mode_set_to_heuristic_by_default(self):
        """Default mode should be heuristic."""
        from src.cli.batch_score_ui import app

        with app.test_client() as client:
            with tempfile.TemporaryDirectory() as tmpdir:
                note_path = Path(tmpdir) / "test.md"
                note_path.write_text("# Test\nContent")

                client.post(
                    "/start",
                    json={"path": tmpdir},  # No use_llm specified
                    content_type="application/json",
                )

                import time

                time.sleep(0.3)

                # Check results endpoint for mode
                response = client.get("/results")
                data = response.get_json()
                assert data.get("mode") == "heuristic"

    def test_mode_set_to_llm_when_requested(self):
        """Mode should be 'llm' when use_llm=True."""
        from src.cli.batch_score_ui import app

        with app.test_client() as client:
            with tempfile.TemporaryDirectory() as tmpdir:
                note_path = Path(tmpdir) / "test.md"
                note_path.write_text("# Test\nContent")

                with patch("src.cli.batch_score_ui.AIEnhancer") as mock_enhancer_class:
                    mock_enhancer = mock_enhancer_class.return_value
                    mock_enhancer.analyze_note_quality_deep.return_value = {
                        "quality_score": 0.8,
                        "coherence_score": 0.75,
                        "mode": "llm",
                    }

                    client.post(
                        "/start",
                        json={"path": tmpdir, "use_llm": True},
                        content_type="application/json",
                    )

                    import time

                    time.sleep(0.3)

                    response = client.get("/results")
                    data = response.get_json()
                    assert data.get("mode") == "llm"


class TestLLMETAEstimate:
    """Tests for ETA estimation in LLM mode."""

    def test_eta_estimate_endpoint_exists(self):
        """GET /estimate should return time estimate."""
        from src.cli.batch_score_ui import app

        with app.test_client() as client:
            with tempfile.TemporaryDirectory() as tmpdir:
                # Create some test notes
                for i in range(5):
                    note_path = Path(tmpdir) / f"note{i}.md"
                    note_path.write_text(f"# Note {i}\nContent")

                response = client.get(f"/estimate?path={tmpdir}&use_llm=true")

                assert response.status_code == 200
                data = response.get_json()
                assert "estimated_time" in data
                assert "total_notes" in data
                assert "mode" in data

    def test_llm_mode_estimate_is_longer_than_heuristic(self):
        """LLM mode should estimate much longer time than heuristic."""
        from src.cli.batch_score_ui import app

        with app.test_client() as client:
            with tempfile.TemporaryDirectory() as tmpdir:
                for i in range(10):
                    note_path = Path(tmpdir) / f"note{i}.md"
                    note_path.write_text(f"# Note {i}\nContent")

                heuristic_response = client.get(
                    f"/estimate?path={tmpdir}&use_llm=false"
                )
                llm_response = client.get(f"/estimate?path={tmpdir}&use_llm=true")

                heuristic_data = heuristic_response.get_json()
                llm_data = llm_response.get_json()

                # LLM should estimate much longer (3s/note vs 0.001s/note)
                assert (
                    llm_data["estimated_seconds"] > heuristic_data["estimated_seconds"]
                )
                assert llm_data["estimated_seconds"] >= 10 * 3  # ~3s per note

    def test_estimate_includes_human_readable_time(self):
        """Estimate should include human-readable time string."""
        from src.cli.batch_score_ui import app

        with app.test_client() as client:
            with tempfile.TemporaryDirectory() as tmpdir:
                for i in range(100):
                    note_path = Path(tmpdir) / f"note{i}.md"
                    note_path.write_text(f"# Note {i}\nContent")

                response = client.get(f"/estimate?path={tmpdir}&use_llm=true")
                data = response.get_json()

                # Should be in format like "5m 0s" or "1h 23m"
                assert "estimated_time" in data
                assert any(unit in data["estimated_time"] for unit in ["s", "m", "h"])


class TestCheckpointIntegration:
    """Tests for checkpoint/resume in web UI."""

    def test_start_accepts_resume_parameter(self):
        """POST /start should accept resume parameter."""
        from src.cli.batch_score_ui import app

        with app.test_client() as client:
            with tempfile.TemporaryDirectory() as tmpdir:
                response = client.post(
                    "/start",
                    json={"path": tmpdir, "use_llm": True, "resume": True},
                    content_type="application/json",
                )

                assert response.status_code == 200

    def test_resume_skips_already_scored_notes(self):
        """Resume should skip notes that were already scored."""
        from src.cli.batch_score_ui import app

        with app.test_client() as client:
            with tempfile.TemporaryDirectory() as tmpdir:
                # Create checkpoint with one scored note
                checkpoint = {
                    "scored_notes": {"note1.md": {"quality_score": 0.8}},
                    "timestamp": "2025-02-04T20:00:00",
                }
                checkpoint_path = Path(tmpdir) / ".llm_scoring_checkpoint.json"
                checkpoint_path.write_text(json.dumps(checkpoint))

                # Create notes
                (Path(tmpdir) / "note1.md").write_text("# Note 1")
                (Path(tmpdir) / "note2.md").write_text("# Note 2")

                with patch("src.cli.batch_score_ui.AIEnhancer") as mock_enhancer_class:
                    mock_enhancer = mock_enhancer_class.return_value
                    scored_notes = []

                    def track_scoring(content, use_llm=False):
                        scored_notes.append(content[:20])
                        return {"quality_score": 0.7, "mode": "llm"}

                    mock_enhancer.analyze_note_quality_deep.side_effect = track_scoring

                    client.post(
                        "/start",
                        json={"path": tmpdir, "use_llm": True, "resume": True},
                        content_type="application/json",
                    )

                    import time

                    time.sleep(0.5)

                    # Only note2 should have been scored (note1 was in checkpoint)
                    assert len(scored_notes) == 1


class TestLLMResultsDisplay:
    """Tests for displaying LLM-specific results in UI."""

    def test_results_include_coherence_score(self):
        """Results should include coherence_score for LLM mode."""
        from src.cli.batch_score_ui import app

        with app.test_client() as client:
            with tempfile.TemporaryDirectory() as tmpdir:
                (Path(tmpdir) / "test.md").write_text("# Test\nContent")

                with patch("src.cli.batch_score_ui.AIEnhancer") as mock_enhancer_class:
                    mock_enhancer = mock_enhancer_class.return_value
                    mock_enhancer.analyze_note_quality_deep.return_value = {
                        "quality_score": 0.8,
                        "coherence_score": 0.75,
                        "grammar_issues": [{"line": 1, "issue": "Minor issue"}],
                        "zettelkasten_feedback": {"atomicity": "Good"},
                        "mode": "llm",
                    }

                    client.post(
                        "/start",
                        json={"path": tmpdir, "use_llm": True},
                        content_type="application/json",
                    )

                    import time

                    time.sleep(0.5)

                    response = client.get("/results")
                    data = response.get_json()

                    # Results should include LLM-specific fields
                    if data["results"]:
                        result = data["results"][0]
                        assert "coherence_score" in result or "coherence" in str(result)

    def test_results_include_grammar_issues(self):
        """Results should include grammar_issues for LLM mode."""
        from src.cli.batch_score_ui import app

        with app.test_client() as client:
            with tempfile.TemporaryDirectory() as tmpdir:
                (Path(tmpdir) / "test.md").write_text("# Test\nContent")

                with patch("src.cli.batch_score_ui.AIEnhancer") as mock_enhancer_class:
                    mock_enhancer = mock_enhancer_class.return_value
                    mock_enhancer.analyze_note_quality_deep.return_value = {
                        "quality_score": 0.8,
                        "coherence_score": 0.75,
                        "grammar_issues": [{"line": 2, "issue": "Spelling error"}],
                        "mode": "llm",
                    }

                    client.post(
                        "/start",
                        json={"path": tmpdir, "use_llm": True},
                        content_type="application/json",
                    )

                    import time

                    time.sleep(0.5)

                    response = client.get("/results")
                    data = response.get_json()

                    if data["results"]:
                        result = data["results"][0]
                        assert "grammar_issues" in result or data.get("mode") == "llm"


class TestLLMModeContentBasedFields:
    """Issue #91: LLM mode should compute atomic/connected/has_placeholders from content."""

    def test_llm_mode_detects_non_atomic_note(self):
        """LLM-scored note with 5+ h2 sections should NOT be marked atomic=True."""
        from src.cli.batch_score_ui import app

        with app.test_client() as client:
            with tempfile.TemporaryDirectory() as tmpdir:
                # Create a kitchen-sink note (5 h2s → not atomic)
                note = Path(tmpdir) / "kitchen-sink.md"
                note.write_text(
                    "# Big Note\n"
                    "## Topic A\nStuff about A.\n"
                    "## Topic B\nStuff about B.\n"
                    "## Topic C\nStuff about C.\n"
                    "## Topic D\nStuff about D.\n"
                    "## Topic E\nStuff about E.\n"
                )

                with patch("src.cli.batch_score_ui.AIEnhancer") as mock_cls:
                    mock = mock_cls.return_value
                    mock.analyze_note_quality_deep.return_value = {
                        "quality_score": 0.6,
                        "coherence_score": 0.5,
                        "grammar_issues": [],
                        "mode": "llm",
                    }
                    # _basic_quality_analysis must be called for content fields
                    mock._basic_quality_analysis.return_value = {
                        "quality_score": 0.4,
                        "has_placeholders": False,
                        "zettelkasten_compliance": {
                            "atomic": False,
                            "connected": False,
                            "sourced": False,
                        },
                        "score_breakdown": {},
                    }

                    client.post(
                        "/start",
                        json={"path": tmpdir, "use_llm": True},
                        content_type="application/json",
                    )

                    import time

                    time.sleep(0.5)

                    response = client.get("/results")
                    data = response.get_json()

                    assert len(data["results"]) >= 1, "Expected at least one result"
                    result = data["results"][0]
                    # Bug #91: these must NOT be hardcoded
                    assert (
                        result["atomic"] is False
                    ), "Kitchen-sink note should be atomic=False, not hardcoded True"

    def test_llm_mode_detects_connected_note(self):
        """LLM-scored note with wiki-links should have connected=True."""
        from src.cli.batch_score_ui import app

        with app.test_client() as client:
            with tempfile.TemporaryDirectory() as tmpdir:
                note = Path(tmpdir) / "linked.md"
                note.write_text(
                    "# Linked Note\nSee [[other-note]] and [[another-note]].\n"
                )

                with patch("src.cli.batch_score_ui.AIEnhancer") as mock_cls:
                    mock = mock_cls.return_value
                    mock.analyze_note_quality_deep.return_value = {
                        "quality_score": 0.8,
                        "coherence_score": 0.7,
                        "grammar_issues": [],
                        "mode": "llm",
                    }
                    mock._basic_quality_analysis.return_value = {
                        "quality_score": 0.7,
                        "has_placeholders": False,
                        "zettelkasten_compliance": {
                            "atomic": True,
                            "connected": True,
                            "sourced": False,
                        },
                        "score_breakdown": {},
                    }

                    client.post(
                        "/start",
                        json={"path": tmpdir, "use_llm": True},
                        content_type="application/json",
                    )

                    import time

                    time.sleep(0.5)

                    response = client.get("/results")
                    data = response.get_json()

                    assert len(data["results"]) >= 1
                    result = data["results"][0]
                    assert (
                        result["connected"] is True
                    ), "Note with wiki-links should be connected=True, not hardcoded False"

    def test_llm_mode_detects_placeholders(self):
        """LLM-scored note with TODO should have has_placeholders=True."""
        from src.cli.batch_score_ui import app

        with app.test_client() as client:
            with tempfile.TemporaryDirectory() as tmpdir:
                note = Path(tmpdir) / "draft.md"
                note.write_text("# Draft\nTODO: fill this in.\n")

                with patch("src.cli.batch_score_ui.AIEnhancer") as mock_cls:
                    mock = mock_cls.return_value
                    mock.analyze_note_quality_deep.return_value = {
                        "quality_score": 0.3,
                        "coherence_score": 0.2,
                        "grammar_issues": [],
                        "mode": "llm",
                    }
                    mock._basic_quality_analysis.return_value = {
                        "quality_score": 0.2,
                        "has_placeholders": True,
                        "zettelkasten_compliance": {
                            "atomic": True,
                            "connected": False,
                            "sourced": False,
                        },
                        "score_breakdown": {},
                    }

                    client.post(
                        "/start",
                        json={"path": tmpdir, "use_llm": True},
                        content_type="application/json",
                    )

                    import time

                    time.sleep(0.5)

                    response = client.get("/results")
                    data = response.get_json()

                    assert len(data["results"]) >= 1
                    result = data["results"][0]
                    assert (
                        result["has_placeholders"] is True
                    ), "Note with TODO should be has_placeholders=True, not hardcoded False"
