"""
RED PHASE: Tests for improved semantic quality scoring (Issue #88)

These tests verify that quality scoring considers:
1. Grammar/spelling quality
2. Template placeholder detection
3. Zettelkasten compliance (atomic, connected, sourced)
4. Semantic coherence

Tests are designed to FAIL initially, driving implementation of improved LLM prompts.
"""

import pytest


class TestNewScoringFields:
    """RED: Tests that new scoring fields exist in analysis output."""

    def test_analysis_returns_grammar_issues_field(self):
        """
        RED: Analysis should include grammar_issues field.

        Current implementation does NOT return this field.
        """
        from src.ai.enhancer import AIEnhancer

        note_content = """
        # Test Note
        
        This is a test note with some content to analyze.
        """

        enhancer = AIEnhancer()

        # Use the fallback (basic) analysis to test current behavior
        result = enhancer._basic_quality_analysis(note_content)

        assert "grammar_issues" in result, (
            "Analysis should include grammar_issues field. "
            "Current _basic_quality_analysis doesn't return this."
        )

    def test_analysis_returns_zettelkasten_compliance_field(self):
        """
        RED: Analysis should include zettelkasten_compliance field.

        Current implementation does NOT return this field.
        """
        from src.ai.enhancer import AIEnhancer

        note_content = """
        # Test Note
        
        This is a test note with some content to analyze.
        """

        enhancer = AIEnhancer()
        result = enhancer._basic_quality_analysis(note_content)

        assert "zettelkasten_compliance" in result, (
            "Analysis should include zettelkasten_compliance field with "
            "{atomic, connected, sourced} assessment."
        )

    def test_analysis_returns_score_breakdown_field(self):
        """
        RED: Analysis should include score_breakdown for explainability.

        Current implementation does NOT return this field.
        """
        from src.ai.enhancer import AIEnhancer

        note_content = """
        # Test Note
        
        This is a test note with some content to analyze.
        """

        enhancer = AIEnhancer()
        result = enhancer._basic_quality_analysis(note_content)

        assert "score_breakdown" in result, (
            "Analysis should include score_breakdown field showing "
            "structural (30%), content_quality (40%), zettelkasten (30%) scores."
        )

    def test_analysis_returns_has_placeholders_field(self):
        """
        RED: Analysis should detect template placeholders.

        Current implementation does NOT check for placeholders.
        """
        from src.ai.enhancer import AIEnhancer

        note_with_placeholder = """
        # Test Note
        
        ## Source
        Where did this come from?
        
        ## Content
        TODO: Fill this in
        """

        enhancer = AIEnhancer()
        result = enhancer._basic_quality_analysis(note_with_placeholder)

        assert (
            "has_placeholders" in result
        ), "Analysis should include has_placeholders field."
        assert (
            result.get("has_placeholders") is True
        ), "Should detect 'Where did this come from?' and 'TODO:' as placeholders."


class TestPlaceholderDetectionInFallback:
    """RED: Tests that fallback scoring detects template placeholders."""

    def test_placeholder_reduces_score(self):
        """
        RED: Notes with 'TODO:' or 'Where did this come from?' should score lower.

        Current _basic_quality_analysis doesn't check for placeholders.
        """
        from src.ai.enhancer import AIEnhancer

        note_with_placeholder = """
        # Test Note
        
        ## Source
        Where did this come from?
        
        ## Content
        TODO: Fill this in later
        
        ## Links
        - [[some-link]]
        """

        complete_note = """
        # Test Note
        
        ## Source
        From "Deep Work" by Cal Newport, Chapter 2.
        
        ## Content
        Deep work is the ability to focus without distraction on cognitively demanding tasks.
        This skill is increasingly valuable in our economy.
        
        ## Links
        - [[focus]]
        - [[productivity]]
        """

        enhancer = AIEnhancer()

        placeholder_result = enhancer._basic_quality_analysis(note_with_placeholder)
        complete_result = enhancer._basic_quality_analysis(complete_note)

        assert placeholder_result["quality_score"] < complete_result["quality_score"], (
            f"Note with placeholders ({placeholder_result['quality_score']}) should score "
            f"lower than complete note ({complete_result['quality_score']}). "
            "Current implementation doesn't detect placeholders."
        )


class TestAtomicityInFallback:
    """RED: Tests that fallback scoring penalizes kitchen-sink notes."""

    def test_kitchen_sink_note_scores_lower(self):
        """
        RED: Notes covering many unrelated topics should score lower.

        Current _basic_quality_analysis rewards more sections, which is backwards
        for Zettelkasten (atomic notes are better).
        """
        from src.ai.enhancer import AIEnhancer

        # Atomic note - single focused topic with good content
        atomic_note = """
        # Compound Interest
        
        Compound interest is interest calculated on both the initial principal 
        and the accumulated interest from previous periods. This creates 
        exponential growth over time.
        
        ## Formula
        The formula is: A = P(1 + r/n)^(nt)
        
        Where:
        - A = final amount
        - P = principal
        - r = annual interest rate
        - n = compounding frequency
        - t = time in years
        
        This concept is fundamental to understanding long-term investing.
        
        - [[time-value-of-money]]
        - [[exponential-growth]]
        """

        # Kitchen sink - many unrelated topics (should score lower due to lack of atomicity)
        kitchen_sink = """
        # Random Notes
        
        ## Finance
        Money stuff is important.
        
        ## Cooking
        Food stuff is tasty.
        
        ## Gardening
        Plant stuff grows well.
        
        ## Travel
        Trip stuff is fun.
        
        ## Health
        Body stuff matters.
        
        ## Technology
        Tech stuff is cool.
        
        - [[random]]
        """

        enhancer = AIEnhancer()

        atomic_result = enhancer._basic_quality_analysis(atomic_note)
        kitchen_result = enhancer._basic_quality_analysis(kitchen_sink)

        # Atomic note should score higher than kitchen-sink
        assert atomic_result["quality_score"] >= kitchen_result["quality_score"], (
            f"Atomic note ({atomic_result['quality_score']}) should score at least as high "
            f"as kitchen-sink note ({kitchen_result['quality_score']}). "
            "Current implementation rewards quantity over atomicity."
        )


class TestScoreWeighting:
    """RED: Tests that score breakdown uses correct weighting."""

    def test_score_breakdown_weights_sum_to_one(self):
        """
        RED: Score breakdown weights should sum to 1.0.

        Issue #88 specifies: structural (30%), content_quality (40%), zettelkasten (30%)
        """
        from src.ai.enhancer import AIEnhancer

        note_content = """
        # Test Note
        
        Some content here.
        """

        enhancer = AIEnhancer()
        result = enhancer._basic_quality_analysis(note_content)

        breakdown = result.get("score_breakdown", {})

        assert breakdown, "score_breakdown should exist"

        total_weight = sum(
            cat.get("weight", 0) for cat in breakdown.values() if isinstance(cat, dict)
        )

        assert (
            abs(total_weight - 1.0) < 0.01
        ), f"Score breakdown weights should sum to 1.0, got {total_weight}"


class TestPerformanceRequirements:
    """Tests for performance requirements from issue #88."""

    def test_fallback_scoring_is_fast(self):
        """
        The fallback (non-LLM) scoring should be nearly instant.
        """
        import time
        from src.ai.enhancer import AIEnhancer

        note_content = """
        # Performance Test Note
        
        This note has enough content to require real analysis.
        It includes multiple sections and detailed information.
        
        ## Section One
        Detailed content about the first topic with examples and explanations.
        
        ## Section Two
        More detailed content with links to [[related-concept]] and [[another-note]].
        
        ## Conclusion
        Summary of key points.
        """

        enhancer = AIEnhancer()

        start = time.time()
        result = enhancer._basic_quality_analysis(note_content)
        elapsed = time.time() - start

        assert elapsed < 0.1, f"Fallback scoring took {elapsed:.3f}s, should be <0.1s"
        assert result is not None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
