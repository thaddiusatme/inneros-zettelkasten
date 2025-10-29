#!/usr/bin/env python3
"""
TDD RED Phase: Template Fixtures Infrastructure (P1-2.1)

Test to verify template fixtures are properly available for test suite.

ROOT CAUSE: Tests reference knowledge/Templates/ which was removed from public repo
IMPACT: Blocks 65+ tests with FileNotFoundError
FIX: Create fixtures/templates/ directory with centralized template loader

This test should FAIL initially, demonstrating the missing infrastructure.
"""

import unittest
import sys
from pathlib import Path

# Add development directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))


class TestTemplateFixturesInfrastructure(unittest.TestCase):
    """
    RED PHASE: Failing tests demonstrating template fixture requirements

    These tests verify that the template fixtures infrastructure exists
    and is properly configured for use by the test suite.
    """

    def test_fixtures_templates_directory_exists(self):
        """
        RED: fixtures/templates/ directory should exist

        Currently FAILS because directory hasn't been created yet
        """
        fixtures_dir = Path(__file__).parent.parent / "fixtures"
        templates_dir = fixtures_dir / "templates"

        self.assertTrue(
            templates_dir.exists(),
            f"Templates directory should exist at: {templates_dir}",
        )
        self.assertTrue(
            templates_dir.is_dir(),
            f"Templates path should be a directory: {templates_dir}",
        )

    def test_all_required_templates_present(self):
        """
        RED: All 13 required templates should be present in fixtures

        Currently FAILS because templates haven't been copied yet
        """
        fixtures_dir = Path(__file__).parent.parent / "fixtures"
        templates_dir = fixtures_dir / "templates"

        # Required templates based on CI failure analysis
        required_templates = [
            "youtube-video.md",  # Primary blocker (65+ failures)
            "daily.md",
            "weekly-review.md",
            "fleeting.md",
            "literature.md",
            "permanent.md",
            "content-idea.md",
            "content-idea-raw.md",
            "chatgpt-prompt.md",
            "simple-youtube-trigger.md",
            "sprint-retro.md",
            "sprint-review.md",
            "permanent Note Morning Check In Template.md",
        ]

        missing_templates = []
        for template_name in required_templates:
            template_path = templates_dir / template_name
            if not template_path.exists():
                missing_templates.append(template_name)

        self.assertEqual(
            [], missing_templates, f"Missing templates: {missing_templates}"
        )

    def test_template_loader_utility_exists(self):
        """
        RED: template_loader.py module should exist with get_template_path()

        Currently FAILS because utility module hasn't been created yet
        """
        try:
            from tests.fixtures import template_loader

            # Verify required function exists
            self.assertTrue(
                hasattr(template_loader, "get_template_path"),
                "template_loader should have get_template_path() function",
            )

            # Verify TEMPLATES_DIR constant exists
            self.assertTrue(
                hasattr(template_loader, "TEMPLATES_DIR"),
                "template_loader should have TEMPLATES_DIR constant",
            )

        except ImportError as e:
            self.fail(f"Failed to import template_loader: {e}")

    def test_templates_have_valid_content(self):
        """
        RED: Each template should be readable and have valid content

        Templates can be either:
        - YAML frontmatter templates (start with ---)
        - Templater templates (start with <%*)

        Currently FAILS because:
        1. Templates don't exist in fixtures yet
        2. Can't read/validate files that aren't there
        """
        fixtures_dir = Path(__file__).parent.parent / "fixtures"
        templates_dir = fixtures_dir / "templates"

        # Sample of critical templates to validate
        critical_templates = [
            "youtube-video.md",  # Templater template
            "daily.md",  # YAML template
            "weekly-review.md",  # YAML template
        ]

        for template_name in critical_templates:
            template_path = templates_dir / template_name

            # Template must exist
            self.assertTrue(
                template_path.exists(), f"Template must exist: {template_name}"
            )

            # Template must be readable
            content = template_path.read_text(encoding="utf-8")
            self.assertGreater(
                len(content), 0, f"Template must have content: {template_name}"
            )

            # Template should have valid format (YAML or Templater)
            has_yaml = content.startswith("---")
            has_templater = content.startswith("<%*")

            self.assertTrue(
                has_yaml or has_templater,
                f"Template should be YAML or Templater format: {template_name}",
            )


if __name__ == "__main__":
    unittest.main()
