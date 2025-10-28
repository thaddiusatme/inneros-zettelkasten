"""
TDD RED PHASE: YouTube Template Approval System Tests

Tests validate that the YouTube template includes:
1. ready_for_processing: false in frontmatter
2. status: draft (not inbox)
3. Checkbox approval section
4. User instructions banner
"""

import re
from pathlib import Path
import pytest


class TestYouTubeTemplateApproval:
    """Test suite for YouTube template approval workflow integration."""

    @pytest.fixture
    def template_path(self):
        """Path to YouTube video template."""
        return (
            Path(__file__).parent.parent.parent.parent
            / "knowledge"
            / "Templates"
            / "youtube-video.md"
        )

    @pytest.fixture
    def template_content(self, template_path):
        """Load template content."""
        return template_path.read_text()

    def test_template_has_ready_for_processing_field(self, template_content):
        """RED: Template should include ready_for_processing: false in frontmatter."""
        # Template uses Templater syntax, so check for the field in frontmatter output
        assert (
            "ready_for_processing: false" in template_content
        ), "Template must include 'ready_for_processing: false' in frontmatter"

    def test_template_uses_draft_status(self, template_content):
        """RED: Template should use status: draft instead of status: inbox."""
        # Check that status: draft exists in frontmatter
        assert (
            "status: draft" in template_content
        ), "Template must use 'status: draft' for new YouTube notes"

        # Verify the status line contains draft (accounting for Templater format)
        import re

        status_match = re.search(r"status:\s*(\w+)", template_content)
        assert status_match, "Template must have status field in frontmatter"
        assert (
            status_match.group(1) == "draft"
        ), f"Status must be 'draft', not '{status_match.group(1)}'"

    def test_template_has_approval_checkbox_section(self, template_content):
        """RED: Template should include checkbox approval section."""
        # Check for checkbox with #youtube-process tag
        checkbox_pattern = r"- \[ \] Ready for AI processing #youtube-process"
        assert re.search(
            checkbox_pattern, template_content
        ), "Template must include '- [ ] Ready for AI processing #youtube-process' checkbox"

    def test_approval_section_appears_after_related_notes(self, template_content):
        """RED: Approval checkbox should appear after 'Related Notes' section."""
        related_notes_idx = template_content.find("## Related Notes")
        checkbox_idx = template_content.find("- [ ] Ready for AI processing")

        assert related_notes_idx > 0, "Template must have 'Related Notes' section"
        assert (
            checkbox_idx > related_notes_idx
        ), "Approval checkbox must appear after 'Related Notes' section"

    def test_template_has_user_instructions_banner(self, template_content):
        """RED: Template should include visual instructions explaining approval workflow."""
        # Look for instructions about checking the box to trigger processing
        instruction_keywords = ["check", "box", "processing", "trigger"]

        # Check for instruction section (should be near checkbox)
        checkbox_idx = template_content.find("- [ ] Ready for AI processing")
        if checkbox_idx > 0:
            # Look in surrounding 500 characters
            context = template_content[
                max(0, checkbox_idx - 200) : min(
                    len(template_content), checkbox_idx + 300
                )
            ]

            keyword_found = any(
                keyword in context.lower() for keyword in instruction_keywords
            )
            assert (
                keyword_found
            ), "Template should include instructions near checkbox explaining how to trigger processing"

    def test_frontmatter_fields_order(self, template_content):
        """RED: Verify frontmatter fields are in logical order."""
        # Extract frontmatter section
        frontmatter_match = re.search(
            r"tR \+= `---\n(.*?)\n---", template_content, re.DOTALL
        )
        assert frontmatter_match, "Could not find frontmatter in template"

        frontmatter = frontmatter_match.group(1)
        lines = [line.strip() for line in frontmatter.split("\n") if line.strip()]

        # Expected order: type, created, status, ready_for_processing, tags, visibility, source, author, video_id, channel
        expected_fields = [
            "type:",
            "created:",
            "status:",
            "ready_for_processing:",
            "tags:",
            "visibility:",
            "source:",
            "author:",
            "video_id:",
            "channel:",
        ]

        actual_fields = [line.split(":")[0] + ":" for line in lines if ":" in line]

        # Check that all expected fields are present
        for field in expected_fields:
            assert field in actual_fields, f"Missing required field: {field}"

    def test_ready_for_processing_comes_after_status(self, template_content):
        """RED: ready_for_processing field should come after status field."""
        frontmatter_match = re.search(
            r"tR \+= `---\n(.*?)\n---", template_content, re.DOTALL
        )
        assert frontmatter_match, "Could not find frontmatter in template"

        frontmatter = frontmatter_match.group(1)

        status_idx = frontmatter.find("status:")
        ready_idx = frontmatter.find("ready_for_processing:")

        assert status_idx > 0, "Must have status field"
        assert (
            ready_idx > status_idx
        ), "ready_for_processing must come after status field in frontmatter"


class TestTemplateStateTransitions:
    """Test that template sets up proper initial state for state machine."""

    @pytest.fixture
    def template_path(self):
        return (
            Path(__file__).parent.parent.parent.parent
            / "knowledge"
            / "Templates"
            / "youtube-video.md"
        )

    @pytest.fixture
    def template_content(self, template_path):
        return template_path.read_text()

    def test_initial_state_is_draft(self, template_content):
        """RED: New notes should start in 'draft' state."""
        assert "status: draft" in template_content

    def test_initial_approval_is_false(self, template_content):
        """RED: New notes should have ready_for_processing: false."""
        assert "ready_for_processing: false" in template_content

    def test_template_preserves_other_fields(self, template_content):
        """RED: Template should preserve all existing functionality."""
        # Check that essential fields still exist
        essential_fields = [
            "type: literature",
            "tags:",
            "visibility:",
            "source: youtube",
            "video_id:",
            "channel:",
        ]

        for field in essential_fields:
            assert field in template_content, f"Template must preserve field: {field}"
