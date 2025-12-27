#!/usr/bin/env python3
"""
TDD Iteration 1: Test inneros wrapper routes workflow commands to ADR-004 CLIs

RED Phase Tests:
- Verify `inneros workflow --status` routes to core_workflow_cli, NOT workflow_demo
- Verify `inneros workflow --enhanced-metrics` routes to weekly_review_cli
- Verify `inneros workflow --weekly-review` routes to weekly_review_cli
- Verify `inneros workflow --process-inbox` routes to core_workflow_cli

Issue #78: Route inneros workflow to ADR-004 dedicated CLIs
"""

import sys
import pytest
from pathlib import Path
from unittest.mock import patch, MagicMock
import argparse
import importlib.util
import importlib.machinery

# Add project root to path for imports
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / "development"))


def load_inneros_module():
    """Load the inneros script as a module from repo root."""
    # Check if already loaded to avoid re-execution
    if "inneros" in sys.modules:
        return sys.modules["inneros"]

    inneros_path = project_root / "inneros"
    # Use SourceFileLoader for scripts without .py extension
    loader = importlib.machinery.SourceFileLoader("inneros", str(inneros_path))
    spec = importlib.util.spec_from_loader("inneros", loader)
    inneros = importlib.util.module_from_spec(spec)
    sys.modules["inneros"] = inneros
    spec.loader.exec_module(inneros)
    return inneros


class TestInnerosWrapperRouting:
    """Test that inneros wrapper routes to dedicated CLIs, not workflow_demo"""

    def test_workflow_status_routes_to_core_workflow_cli(self):
        """
        RED: inneros workflow --status should route to core_workflow_cli.status()

        Currently fails because run_workflow() imports workflow_demo instead.
        """
        # Load the wrapper module from repo root
        wrapper = load_inneros_module()

        # Create mock args simulating: inneros workflow --status
        args = argparse.Namespace(
            path="knowledge/",
            status=True,
            process_inbox=False,
            report=False,
            interactive=False,
            weekly_review=False,
            enhanced_metrics=False,
            format="text",
            export=None,
            export_checklist=None,
            dry_run=False,
        )

        # Mock the core_workflow_cli to verify it's called
        # Patch at the actual import location since imports are inside run_workflow()
        with patch("src.cli.core_workflow_cli.CoreWorkflowCLI") as mock_cli_class:
            mock_cli = MagicMock()
            mock_cli.status.return_value = 0
            mock_cli_class.return_value = mock_cli

            # Run the workflow command
            result = wrapper.run_workflow(args)

            # ASSERTION: core_workflow_cli.status() should be called
            mock_cli_class.assert_called_once()
            mock_cli.status.assert_called_once()
            assert result == 0

    def test_workflow_enhanced_metrics_routes_to_weekly_review_cli(self):
        """
        RED: inneros workflow --enhanced-metrics should route to weekly_review_cli.enhanced_metrics()

        Currently fails because run_workflow() imports workflow_demo instead.
        """
        wrapper = load_inneros_module()

        args = argparse.Namespace(
            path="knowledge/",
            status=False,
            process_inbox=False,
            report=False,
            interactive=False,
            weekly_review=False,
            enhanced_metrics=True,
            format="text",
            export=None,
            export_checklist=None,
            dry_run=False,
        )

        # Patch at the actual import location
        with patch("src.cli.weekly_review_cli.WeeklyReviewCLI") as mock_cli_class:
            mock_cli = MagicMock()
            mock_cli.enhanced_metrics.return_value = 0
            mock_cli_class.return_value = mock_cli

            result = wrapper.run_workflow(args)

            # ASSERTION: weekly_review_cli.enhanced_metrics() should be called
            mock_cli_class.assert_called_once()
            mock_cli.enhanced_metrics.assert_called_once()
            assert result == 0

    def test_workflow_weekly_review_routes_to_weekly_review_cli(self):
        """
        RED: inneros workflow --weekly-review should route to weekly_review_cli.weekly_review()
        """
        wrapper = load_inneros_module()

        args = argparse.Namespace(
            path="knowledge/",
            status=False,
            process_inbox=False,
            report=False,
            interactive=False,
            weekly_review=True,
            enhanced_metrics=False,
            format="text",
            export=None,
            export_checklist=None,
            dry_run=False,
        )

        # Patch at the actual import location
        with patch("src.cli.weekly_review_cli.WeeklyReviewCLI") as mock_cli_class:
            mock_cli = MagicMock()
            mock_cli.weekly_review.return_value = 0
            mock_cli_class.return_value = mock_cli

            result = wrapper.run_workflow(args)

            # ASSERTION: weekly_review_cli.weekly_review() should be called
            mock_cli_class.assert_called_once()
            mock_cli.weekly_review.assert_called_once()
            assert result == 0

    def test_workflow_process_inbox_routes_to_core_workflow_cli(self):
        """
        RED: inneros workflow --process-inbox should route to core_workflow_cli.process_inbox()
        """
        wrapper = load_inneros_module()

        args = argparse.Namespace(
            path="knowledge/",
            status=False,
            process_inbox=True,
            report=False,
            interactive=False,
            weekly_review=False,
            enhanced_metrics=False,
            format="text",
            export=None,
            export_checklist=None,
            dry_run=False,
        )

        # Patch at the actual import location
        with patch("src.cli.core_workflow_cli.CoreWorkflowCLI") as mock_cli_class:
            mock_cli = MagicMock()
            mock_cli.process_inbox.return_value = 0
            mock_cli_class.return_value = mock_cli

            result = wrapper.run_workflow(args)

            # ASSERTION: core_workflow_cli.process_inbox() should be called
            mock_cli_class.assert_called_once()
            mock_cli.process_inbox.assert_called_once()
            assert result == 0

    def test_workflow_does_not_import_workflow_demo(self):
        """
        RED: run_workflow() should NOT import or call workflow_demo

        This is the critical test - verifies we've removed the deprecated dependency.
        """
        wrapper = load_inneros_module()

        args = argparse.Namespace(
            path="knowledge/",
            status=True,
            process_inbox=False,
            report=False,
            interactive=False,
            weekly_review=False,
            enhanced_metrics=False,
            format="text",
            export=None,
            export_checklist=None,
            dry_run=False,
        )

        # Mock both CLIs to prevent actual execution
        # Patch at the actual import location
        with patch("src.cli.core_workflow_cli.CoreWorkflowCLI") as mock_core:
            mock_core.return_value.status.return_value = 0

            # Patch workflow_demo to raise an error if imported
            with patch.dict("sys.modules", {"src.cli.workflow_demo": None}):
                # This should NOT try to import workflow_demo
                # If it does, the test will fail with ImportError
                try:
                    wrapper.run_workflow(args)
                except (ImportError, AttributeError) as e:
                    if "workflow_demo" in str(e):
                        pytest.fail(
                            "run_workflow() still imports workflow_demo - "
                            "should route to dedicated CLIs instead"
                        )
                    raise

    def test_exit_code_propagates_from_dedicated_cli(self):
        """
        RED: Exit codes from dedicated CLIs should propagate through wrapper
        """
        wrapper = load_inneros_module()

        args = argparse.Namespace(
            path="knowledge/",
            status=True,
            process_inbox=False,
            report=False,
            interactive=False,
            weekly_review=False,
            enhanced_metrics=False,
            format="text",
            export=None,
            export_checklist=None,
            dry_run=False,
        )

        # Test that non-zero exit code propagates
        # Patch at the actual import location
        with patch("src.cli.core_workflow_cli.CoreWorkflowCLI") as mock_cli_class:
            mock_cli = MagicMock()
            mock_cli.status.return_value = 1  # Error exit code
            mock_cli_class.return_value = mock_cli

            result = wrapper.run_workflow(args)

            assert result == 1, "Exit code should propagate from dedicated CLI"


class TestInnerosWrapperFlagMapping:
    """Test that wrapper flags map correctly to dedicated CLI parameters"""

    def test_dry_run_maps_to_weekly_review_preview(self):
        """
        RED: --dry-run flag should map to weekly_review_cli preview parameter
        """
        wrapper = load_inneros_module()

        args = argparse.Namespace(
            path="knowledge/",
            status=False,
            process_inbox=False,
            report=False,
            interactive=False,
            weekly_review=True,
            enhanced_metrics=False,
            format="text",
            export=None,
            export_checklist=None,
            dry_run=True,  # This should map to preview=True
        )

        # Patch at the actual import location
        with patch("src.cli.weekly_review_cli.WeeklyReviewCLI") as mock_cli_class:
            mock_cli = MagicMock()
            mock_cli.weekly_review.return_value = 0
            mock_cli_class.return_value = mock_cli

            wrapper.run_workflow(args)

            # Verify preview=True was passed
            mock_cli.weekly_review.assert_called_once()
            call_kwargs = mock_cli.weekly_review.call_args
            # Check if preview=True is in the call
            assert call_kwargs is not None
            # Get the kwargs from the call
            if call_kwargs.kwargs:
                assert call_kwargs.kwargs.get("preview") == True
            else:
                # May be positional arg
                assert True in call_kwargs.args

    def test_export_checklist_maps_to_weekly_review_export(self):
        """
        RED: --export-checklist should map to weekly_review_cli export_path
        """
        wrapper = load_inneros_module()

        args = argparse.Namespace(
            path="knowledge/",
            status=False,
            process_inbox=False,
            report=False,
            interactive=False,
            weekly_review=True,
            enhanced_metrics=False,
            format="text",
            export=None,
            export_checklist="review.md",
            dry_run=False,
        )

        # Patch at the actual import location
        with patch("src.cli.weekly_review_cli.WeeklyReviewCLI") as mock_cli_class:
            mock_cli = MagicMock()
            mock_cli.weekly_review.return_value = 0
            mock_cli_class.return_value = mock_cli

            wrapper.run_workflow(args)

            # Verify export_path was passed
            mock_cli.weekly_review.assert_called_once()
            call_kwargs = mock_cli.weekly_review.call_args
            assert call_kwargs is not None
            if call_kwargs.kwargs:
                assert call_kwargs.kwargs.get("export_path") == "review.md"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
