"""
Test suite for Issue #87: Quality Score Display Fix
TDD RED Phase - These tests SHOULD FAIL initially

Problem: Web UI displays hardcoded 50% (0.5) and 40% (0.4) quality scores
         instead of reading actual quality_score from note frontmatter.

Acceptance Criteria:
- [ ] Web UI displays actual quality_score from frontmatter
- [ ] Notes without quality_score show appropriate fallback
- [ ] Unit tests cover both cases
"""

import sys
from pathlib import Path
import pytest

# Add src to path for imports
current_dir = Path(__file__).parent
project_root = current_dir.parent.parent.parent.parent
src_dir = project_root / "development" / "src"
sys.path.insert(0, str(src_dir))

# Import Flask app
web_ui_dir = project_root / "web_ui"
sys.path.insert(0, str(web_ui_dir))


@pytest.fixture
def client():
    """Create test Flask client."""
    from app import app

    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client


@pytest.fixture
def temp_vault_with_scored_notes(tmp_path):
    """Create a temporary vault with notes that have quality_score in frontmatter."""
    inbox = tmp_path / "Inbox"
    inbox.mkdir()
    fleeting = tmp_path / "Fleeting Notes"
    fleeting.mkdir()

    # Create inbox note WITH quality_score (0.85 - should display as 85%)
    scored_inbox_note = inbox / "scored-inbox-note.md"
    scored_inbox_note.write_text(
        """---
title: Scored Inbox Note
type: fleeting
quality_score: 0.85
created: 2025-02-01
---

This note has an AI-generated quality score of 0.85.
"""
    )

    # Create inbox note WITHOUT quality_score (should show fallback)
    unscored_inbox_note = inbox / "unscored-inbox-note.md"
    unscored_inbox_note.write_text(
        """---
title: Unscored Inbox Note
type: fleeting
created: 2025-02-01
---

This note has no quality score in frontmatter.
"""
    )

    # Create fleeting note WITH quality_score (0.72 - should display as 72%)
    scored_fleeting_note = fleeting / "scored-fleeting-note.md"
    scored_fleeting_note.write_text(
        """---
title: Scored Fleeting Note
type: fleeting
quality_score: 0.72
created: 2025-02-01
---

This fleeting note has quality score 0.72.
"""
    )

    # Create fleeting note WITHOUT quality_score
    unscored_fleeting_note = fleeting / "unscored-fleeting-note.md"
    unscored_fleeting_note.write_text(
        """---
title: Unscored Fleeting Note
type: fleeting
created: 2025-02-01
---

This fleeting note has no quality score.
"""
    )

    return tmp_path


class TestQualityScoreFromFrontmatter:
    """RED PHASE: Tests that quality scores are read from frontmatter, not hardcoded."""

    def test_inbox_note_displays_actual_quality_score(
        self, client, temp_vault_with_scored_notes
    ):
        """
        CRITICAL TEST - Issue #87

        Given: An inbox note with quality_score: 0.85 in frontmatter
        When: Weekly review page is loaded
        Then: The displayed quality should be 85%, NOT the hardcoded 50%

        This test SHOULD FAIL initially because app.py uses hardcoded 0.5
        """
        vault_path = str(temp_vault_with_scored_notes)
        response = client.get(f"/weekly-review?path={vault_path}")

        assert response.status_code == 200
        html = response.data.decode()

        # The note has quality_score: 0.85, so we should see "85%" in the output
        # Currently this FAILS because app.py hardcodes 0.5 (displays as "50%")
        assert "85%" in html, (
            "Expected quality score 85% from frontmatter, but got hardcoded value. "
            "Bug: app.py line 157 hardcodes quality_score: 0.5"
        )

    def test_fleeting_note_displays_actual_quality_score(
        self, client, temp_vault_with_scored_notes
    ):
        """
        CRITICAL TEST - Issue #87

        Given: A fleeting note with quality_score: 0.72 in frontmatter
        When: Weekly review page is loaded
        Then: The displayed quality should be 72%, NOT the hardcoded 40%

        This test SHOULD FAIL initially because app.py uses hardcoded 0.4
        """
        vault_path = str(temp_vault_with_scored_notes)
        response = client.get(f"/weekly-review?path={vault_path}")

        assert response.status_code == 200
        html = response.data.decode()

        # The note has quality_score: 0.72, so we should see "72%" in the output
        # Currently this FAILS because app.py hardcodes 0.4 (displays as "40%")
        assert "72%" in html, (
            "Expected quality score 72% from frontmatter, but got hardcoded value. "
            "Bug: app.py line 167 hardcodes quality_score: 0.4"
        )


class TestQualityScoreFallback:
    """RED PHASE: Tests for graceful fallback when quality_score is missing."""

    def test_unscored_note_shows_fallback_not_hardcoded(
        self, client, temp_vault_with_scored_notes
    ):
        """
        Given: A note WITHOUT quality_score in frontmatter
        When: Weekly review page is loaded
        Then: Should show "Not scored" or similar fallback, not a fake hardcoded value

        This tests that we don't mislead users with fake quality scores.
        """
        vault_path = str(temp_vault_with_scored_notes)
        response = client.get(f"/weekly-review?path={vault_path}")

        assert response.status_code == 200
        html = response.data.decode()

        # We have 2 scored notes (85%, 72%) and 2 unscored notes
        # The unscored notes should NOT show 50% or 40% (the hardcoded values)
        # Instead they should show a fallback indicator

        # Count occurrences of the hardcoded quality score values
        # Be specific: look for "Quality: 50%" pattern, not just "50%" (which appears in CSS)
        hardcoded_50_count = html.count("Quality: 50%")
        hardcoded_40_count = html.count("Quality: 40%")

        # If we're reading from frontmatter correctly:
        # - Scored notes show their actual scores (85%, 72%)
        # - Unscored notes show fallback (not 50% or 40%)
        # So we should see ZERO instances of hardcoded quality scores
        assert hardcoded_50_count == 0, (
            f"Found {hardcoded_50_count} instances of hardcoded 'Quality: 50%'. "
            "Unscored notes should show fallback, not fake scores."
        )
        assert hardcoded_40_count == 0, (
            f"Found {hardcoded_40_count} instances of hardcoded 'Quality: 40%'. "
            "Unscored notes should show fallback, not fake scores."
        )


class TestQualityScoreExtraction:
    """Tests for the quality score extraction utility function."""

    def test_extract_quality_score_from_frontmatter(self, tmp_path):
        """Test that we can extract quality_score from note frontmatter."""
        from app import extract_quality_score_from_note

        # Create a test note with quality_score
        test_note = tmp_path / "test-note.md"
        test_note.write_text(
            """---
title: Test Note
quality_score: 0.85
---

Content here.
"""
        )

        score = extract_quality_score_from_note(test_note)
        assert score == 0.85, f"Expected 0.85, got {score}"

    def test_extract_quality_score_returns_none_for_missing(self, tmp_path):
        """Test that extraction returns None when quality_score is not in frontmatter."""
        from app import extract_quality_score_from_note

        # Create a test note WITHOUT quality_score
        test_note = tmp_path / "unscored-note.md"
        test_note.write_text(
            """---
title: Unscored Note
type: fleeting
---

No quality score here.
"""
        )

        score = extract_quality_score_from_note(test_note)
        assert score is None, f"Expected None for missing quality_score, got {score}"


class TestQualityScoreNoHardcodedValues:
    """RED PHASE: Regression tests to ensure no hardcoded quality scores."""

    def test_no_hardcoded_0_5_in_weekly_review_items(
        self, client, temp_vault_with_scored_notes
    ):
        """
        Regression test: Ensure weekly review doesn't use hardcoded 0.5 quality score.

        The bug in app.py line 157:
            "quality_score": 0.5,  # Default placeholder

        Should be replaced with actual frontmatter reading.
        """
        vault_path = str(temp_vault_with_scored_notes)
        response = client.get(f"/weekly-review?path={vault_path}")

        html = response.data.decode()

        # With our test vault:
        # - scored-inbox-note.md has quality_score: 0.85 -> should show 85%
        # - unscored-inbox-note.md has no score -> should show fallback
        # Neither should show 50% (the hardcoded default)

        # This is a strict test - we expect 0 hardcoded 50% values
        assert "Quality: 50%" not in html, (
            "Found hardcoded 'Quality: 50%' in output. "
            "This indicates app.py is still using hardcoded values."
        )

    def test_no_hardcoded_0_4_in_weekly_review_items(
        self, client, temp_vault_with_scored_notes
    ):
        """
        Regression test: Ensure weekly review doesn't use hardcoded 0.4 quality score.

        The bug in app.py line 167:
            "quality_score": 0.4,  # Default placeholder

        Should be replaced with actual frontmatter reading.
        """
        vault_path = str(temp_vault_with_scored_notes)
        response = client.get(f"/weekly-review?path={vault_path}")

        html = response.data.decode()

        # With our test vault:
        # - scored-fleeting-note.md has quality_score: 0.72 -> should show 72%
        # - unscored-fleeting-note.md has no score -> should show fallback
        # Neither should show 40% (the hardcoded default)

        assert "Quality: 40%" not in html, (
            "Found hardcoded 'Quality: 40%' in output. "
            "This indicates app.py is still using hardcoded values."
        )


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
