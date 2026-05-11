"""
RED Phase Tests: Issue #90 - LLM-based Deep Quality Scoring

TDD Iteration 1 for LLM integration with checkpoint/resume support.
These tests should ALL FAIL initially until GREEN phase implementation.

Acceptance Criteria:
- [ ] `--llm` flag triggers Ollama-based analysis instead of heuristic
- [ ] Progress persists to disk, resume works after interruption
- [ ] LLM results include grammar, coherence, and Zettelkasten feedback
"""

import json
import tempfile
from pathlib import Path
from unittest.mock import patch

import pytest


class TestLLMDeepScoringFlag:
    """Tests for --llm flag triggering Ollama analysis."""

    def test_llm_flag_triggers_ollama_analysis(self):
        """--llm flag should use Ollama LLM instead of heuristic scoring."""
        from src.ai.enhancer import AIEnhancer

        enhancer = AIEnhancer()
        content = "# Test Note\nThis is a test note for LLM analysis."

        # This method should exist and use LLM when use_llm=True
        result = enhancer.analyze_note_quality_deep(content, use_llm=True)

        assert "quality_score" in result
        assert "coherence_score" in result
        assert "grammar_issues" in result
        assert isinstance(result["grammar_issues"], list)

    def test_heuristic_mode_is_default(self):
        """Default mode should use fast heuristic scoring."""
        from src.ai.enhancer import AIEnhancer

        enhancer = AIEnhancer()
        content = "# Test Note\nThis is a test note."

        # Default should NOT call Ollama
        result = enhancer.analyze_note_quality_deep(content, use_llm=False)

        assert "quality_score" in result
        # Heuristic mode should be fast, no coherence_score required
        assert result.get("mode") == "heuristic"

    def test_llm_mode_returns_structured_feedback(self):
        """LLM mode should return structured Zettelkasten feedback."""
        from src.ai.enhancer import AIEnhancer

        enhancer = AIEnhancer()
        content = """
        # Quantum Computing
        
        Quantum computing uses quantum mechanics for computation.
        
        ## Key Concepts
        - Qubits can exist in superposition
        - Entanglement enables faster processing
        """

        with patch.object(enhancer, "ollama_client") as mock_client:
            mock_client.generate.return_value = json.dumps(
                {
                    "quality_score": 0.72,
                    "coherence_score": 0.85,
                    "grammar_issues": [
                        {"line": 5, "issue": "Consider more detailed explanation"}
                    ],
                    "zettelkasten_feedback": {
                        "atomicity": "Good - focused on single concept",
                        "connections": "Missing links to related notes",
                        "sources": "No source attribution",
                    },
                }
            )

            result = enhancer.analyze_note_quality_deep(content, use_llm=True)

        assert "zettelkasten_feedback" in result
        assert "atomicity" in result["zettelkasten_feedback"]
        assert "connections" in result["zettelkasten_feedback"]


class TestCheckpointSystem:
    """Tests for checkpoint/resume functionality during batch scoring."""

    def test_checkpoint_file_created_during_batch(self):
        """Checkpoint file should be created during batch processing."""
        from src.ai.llm_batch_scorer import LLMBatchScorer

        with tempfile.TemporaryDirectory() as tmpdir:
            vault_path = Path(tmpdir)

            # Create test notes
            (vault_path / "note1.md").write_text("# Note 1\nContent here.")
            (vault_path / "note2.md").write_text("# Note 2\nMore content.")

            scorer = LLMBatchScorer(vault_path)
            checkpoint_path = vault_path / ".llm_scoring_checkpoint.json"

            # Start batch scoring (will create checkpoint)
            scorer.score_batch(use_llm=True, checkpoint_dir=vault_path)

            assert checkpoint_path.exists(), "Checkpoint file should be created"

    def test_checkpoint_contains_scored_notes(self):
        """Checkpoint should track which notes have been scored."""
        from src.ai.llm_batch_scorer import LLMBatchScorer

        with tempfile.TemporaryDirectory() as tmpdir:
            vault_path = Path(tmpdir)

            # Create test note
            (vault_path / "note1.md").write_text("# Note 1\nContent.")

            scorer = LLMBatchScorer(vault_path)
            scorer.score_batch(use_llm=True, checkpoint_dir=vault_path)

            checkpoint_path = vault_path / ".llm_scoring_checkpoint.json"
            checkpoint = json.loads(checkpoint_path.read_text())

            assert "scored_notes" in checkpoint
            assert "note1.md" in checkpoint["scored_notes"]
            assert "timestamp" in checkpoint

    def test_resume_skips_already_scored_notes(self):
        """Resume should skip notes that were already scored."""
        from src.ai.llm_batch_scorer import LLMBatchScorer

        with tempfile.TemporaryDirectory() as tmpdir:
            vault_path = Path(tmpdir)

            # Create test notes
            (vault_path / "note1.md").write_text("# Note 1\nContent.")
            (vault_path / "note2.md").write_text("# Note 2\nContent.")

            # Create existing checkpoint with note1 already scored
            checkpoint = {
                "scored_notes": {"note1.md": {"quality_score": 0.8}},
                "timestamp": "2025-02-04T17:00:00",
            }
            checkpoint_path = vault_path / ".llm_scoring_checkpoint.json"
            checkpoint_path.write_text(json.dumps(checkpoint))

            scorer = LLMBatchScorer(vault_path)

            # Track which notes are actually scored
            scored_notes = []

            def mock_score(note_path, use_llm):
                scored_notes.append(note_path.name)
                return {"quality_score": 0.7}

            scorer._score_single_note = mock_score

            scorer.score_batch(use_llm=True, checkpoint_dir=vault_path, resume=True)

            # Only note2 should be scored (note1 was already in checkpoint)
            assert "note2.md" in scored_notes
            assert "note1.md" not in scored_notes

    def test_checkpoint_updated_after_each_note(self):
        """Checkpoint should be updated after each note is scored."""
        from src.ai.llm_batch_scorer import LLMBatchScorer

        with tempfile.TemporaryDirectory() as tmpdir:
            vault_path = Path(tmpdir)

            # Create test notes
            (vault_path / "note1.md").write_text("# Note 1")
            (vault_path / "note2.md").write_text("# Note 2")

            scorer = LLMBatchScorer(vault_path)

            # Track checkpoint writes
            checkpoint_writes = []
            original_save = scorer._save_checkpoint

            def mock_save(checkpoint, path):
                checkpoint_writes.append(dict(checkpoint))
                original_save(checkpoint, path)

            scorer._save_checkpoint = mock_save

            scorer.score_batch(use_llm=True, checkpoint_dir=vault_path)

            # Should have checkpoint update after each note
            assert len(checkpoint_writes) >= 2


class TestLLMGrammarAndCoherence:
    """Tests for grammar/coherence analysis in LLM mode."""

    def test_grammar_issues_detected(self):
        """LLM should detect grammar issues in notes."""
        from src.ai.enhancer import AIEnhancer

        enhancer = AIEnhancer()
        content_with_errors = """
        # Bad Grammer Note
        
        This note have bad grammar and spelling erors.
        The sentense structure is also being poor.
        """

        with patch.object(enhancer, "ollama_client") as mock_client:
            mock_client.generate.return_value = json.dumps(
                {
                    "quality_score": 0.45,
                    "coherence_score": 0.6,
                    "grammar_issues": [
                        {"line": 1, "issue": "'Grammer' should be 'Grammar'"},
                        {"line": 3, "issue": "'have' should be 'has'"},
                        {"line": 3, "issue": "'erors' should be 'errors'"},
                        {"line": 4, "issue": "'sentense' should be 'sentence'"},
                    ],
                    "zettelkasten_feedback": {},
                }
            )

            result = enhancer.analyze_note_quality_deep(
                content_with_errors, use_llm=True
            )

        assert len(result["grammar_issues"]) >= 3
        assert any(
            "Grammar" in issue.get("issue", "") for issue in result["grammar_issues"]
        )

    def test_coherence_score_reflects_logical_flow(self):
        """Coherence score should reflect logical flow of content."""
        from src.ai.enhancer import AIEnhancer

        enhancer = AIEnhancer()

        # Well-structured coherent note
        coherent_content = """
        # Machine Learning Pipeline
        
        A machine learning pipeline consists of sequential steps that transform raw data into predictions.
        
        ## Data Collection
        First, gather relevant data from various sources.
        
        ## Preprocessing
        Then, clean and normalize the data for consistency.
        
        ## Training
        Finally, train the model on the prepared dataset.
        """

        with patch.object(enhancer, "ollama_client") as mock_client:
            mock_client.generate.return_value = json.dumps(
                {
                    "quality_score": 0.85,
                    "coherence_score": 0.92,
                    "grammar_issues": [],
                    "zettelkasten_feedback": {"atomicity": "Good"},
                }
            )

            result = enhancer.analyze_note_quality_deep(coherent_content, use_llm=True)

        assert result["coherence_score"] >= 0.8

    def test_incoherent_note_gets_low_coherence_score(self):
        """Incoherent notes should get low coherence scores."""
        from src.ai.enhancer import AIEnhancer

        enhancer = AIEnhancer()

        # Incoherent content - random topics mixed together
        incoherent_content = """
        # Random Thoughts
        
        Cats are fluffy. Python is a programming language.
        The sun is hot. Docker containers are useful.
        I like pizza. Machine learning is complex.
        """

        with patch.object(enhancer, "ollama_client") as mock_client:
            mock_client.generate.return_value = json.dumps(
                {
                    "quality_score": 0.35,
                    "coherence_score": 0.25,
                    "grammar_issues": [],
                    "zettelkasten_feedback": {
                        "atomicity": "Poor - covers multiple unrelated topics",
                    },
                }
            )

            result = enhancer.analyze_note_quality_deep(
                incoherent_content, use_llm=True
            )

        assert result["coherence_score"] < 0.5


class TestRateLimiting:
    """Tests for rate limiting to avoid overwhelming Ollama."""

    def test_rate_limiter_respects_delay(self):
        """Rate limiter should enforce minimum delay between requests."""
        from src.ai.llm_batch_scorer import OllamaRateLimiter

        limiter = OllamaRateLimiter(requests_per_minute=30)

        import time

        start = time.time()
        limiter.wait_if_needed()
        limiter.wait_if_needed()
        elapsed = time.time() - start

        # With 30 req/min, minimum 2 seconds between requests
        assert elapsed >= 2.0

    def test_rate_limiter_tracks_request_count(self):
        """Rate limiter should track request counts."""
        from src.ai.llm_batch_scorer import OllamaRateLimiter

        limiter = OllamaRateLimiter(requests_per_minute=60)

        assert limiter.request_count == 0
        limiter.record_request()
        assert limiter.request_count == 1
        limiter.record_request()
        assert limiter.request_count == 2

    def test_batch_scorer_uses_rate_limiter(self):
        """Batch scorer should use rate limiter for LLM calls."""
        from src.ai.llm_batch_scorer import LLMBatchScorer

        with tempfile.TemporaryDirectory() as tmpdir:
            vault_path = Path(tmpdir)

            # Create test notes
            (vault_path / "note1.md").write_text("# Note 1")
            (vault_path / "note2.md").write_text("# Note 2")

            scorer = LLMBatchScorer(vault_path, requests_per_minute=30)

            assert hasattr(scorer, "rate_limiter")
            assert scorer.rate_limiter.requests_per_minute == 30


class TestBatchScorerIntegration:
    """Integration tests for LLM batch scoring."""

    def test_batch_scorer_estimates_completion_time(self):
        """Batch scorer should estimate completion time for LLM mode."""
        from src.ai.llm_batch_scorer import LLMBatchScorer

        with tempfile.TemporaryDirectory() as tmpdir:
            vault_path = Path(tmpdir)

            # Create 10 test notes
            for i in range(10):
                (vault_path / f"note{i}.md").write_text(f"# Note {i}\nContent.")

            scorer = LLMBatchScorer(vault_path)
            estimate = scorer.estimate_completion_time(use_llm=True)

            # 10 notes at ~3s each = ~30 seconds minimum
            assert estimate["total_notes"] == 10
            assert estimate["estimated_seconds"] >= 30
            assert "estimated_time" in estimate  # Human readable string

    def test_batch_scorer_returns_aggregate_stats(self):
        """Batch scorer should return aggregate statistics."""
        from src.ai.llm_batch_scorer import LLMBatchScorer

        with tempfile.TemporaryDirectory() as tmpdir:
            vault_path = Path(tmpdir)

            (vault_path / "note1.md").write_text("# Note 1\nGood content here.")
            (vault_path / "note2.md").write_text("# Note 2\nMore good content.")

            scorer = LLMBatchScorer(vault_path)

            with patch.object(scorer, "_score_single_note") as mock_score:
                mock_score.side_effect = [
                    {"quality_score": 0.8, "coherence_score": 0.9},
                    {"quality_score": 0.6, "coherence_score": 0.7},
                ]

                results = scorer.score_batch(use_llm=True)

            assert "total_scored" in results
            assert results["total_scored"] == 2
            assert "average_quality" in results
            assert results["average_quality"] == pytest.approx(0.7, rel=0.1)
            assert "average_coherence" in results


class TestLLMPromptEnhancement:
    """Tests for enhanced Ollama prompt with grammar/coherence instructions."""

    def test_llm_prompt_includes_grammar_instructions(self):
        """LLM prompt should include grammar analysis instructions."""
        from src.ai.enhancer import AIEnhancer

        enhancer = AIEnhancer()

        # Access the prompt generation method
        prompt = enhancer._build_deep_analysis_prompt("# Test content")

        assert "grammar" in prompt.lower()
        assert "spelling" in prompt.lower() or "coherence" in prompt.lower()

    def test_llm_prompt_includes_zettelkasten_criteria(self):
        """LLM prompt should include Zettelkasten-specific criteria."""
        from src.ai.enhancer import AIEnhancer

        enhancer = AIEnhancer()

        prompt = enhancer._build_deep_analysis_prompt("# Test content")

        assert "atomic" in prompt.lower() or "zettelkasten" in prompt.lower()
        assert "link" in prompt.lower() or "connection" in prompt.lower()

    def test_llm_response_parsed_correctly(self):
        """LLM JSON response should be parsed correctly."""
        from src.ai.enhancer import AIEnhancer

        enhancer = AIEnhancer()

        mock_response = """
        Here's my analysis:
        
        ```json
        {
            "quality_score": 0.78,
            "coherence_score": 0.82,
            "grammar_issues": [
                {"line": 3, "issue": "Missing comma"}
            ],
            "zettelkasten_feedback": {
                "atomicity": "Good",
                "connections": "Needs more links"
            }
        }
        ```
        """

        result = enhancer._parse_deep_analysis_response(mock_response)

        assert result["quality_score"] == 0.78
        assert result["coherence_score"] == 0.82
        assert len(result["grammar_issues"]) == 1


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
