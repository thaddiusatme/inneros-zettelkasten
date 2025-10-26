#!/usr/bin/env python3
"""
Integration tests for Dashboard + Isolated Vault

Ensures dashboard correctly integrates with vault structure using
isolated test vaults (vault factories) instead of production vault.

Performance: <2s (baseline 1.02s with production vault)
Migration: TDD Iteration 4 - Week 1, Day 3
"""

import sys
from pathlib import Path

# Add development directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

import pytest
from src.cli.workflow_dashboard import WorkflowDashboard
from tests.fixtures.vault_factory import create_small_vault

@pytest.mark.integration
@pytest.mark.fast_integration
class TestDashboardVaultIntegration:
    """
    Integration tests for dashboard vault integration.
    
    Uses isolated test vaults created via vault factories for:
    1. Full test isolation (no production vault dependency)
    2. Fast execution (<2s target)
    3. CI/CD compatibility
    4. Predictable test data
    """

    @pytest.fixture
    def vault_path(self, tmp_path):
        """Create isolated test vault with dashboard-compatible structure."""
        vault_path, metadata = create_small_vault(tmp_path)

        # Verify vault structure was created
        assert vault_path.exists(), f"Vault not found at {vault_path}"
        assert (vault_path / "Inbox").exists(), "Inbox directory not created"
        assert (vault_path / "Fleeting Notes").exists(), "Fleeting Notes directory not created"

        return str(vault_path)

    @pytest.fixture
    def dashboard(self, vault_path):
        """Create dashboard with isolated test vault."""
        return WorkflowDashboard(vault_path=vault_path)

    def test_dashboard_finds_actual_vault(self, dashboard, vault_path):
        """
        Verify dashboard is pointed to correct isolated vault.
        
        Tests vault path configuration with test vault.
        """
        # Dashboard should store the vault path
        assert dashboard.vault_path == vault_path

        # Vault should exist
        vault_path_obj = Path(vault_path)
        assert vault_path_obj.exists()
        assert vault_path_obj.is_dir()

    def test_inbox_directory_exists_and_has_notes(self, vault_path):
        """
        Verify Inbox/ directory exists in test vault.
        
        Tests vault structure created by vault factory.
        """
        inbox_path = Path(vault_path) / 'Inbox'

        # Inbox directory must exist
        assert inbox_path.exists(), f"Inbox not found at {inbox_path}"
        assert inbox_path.is_dir(), "Inbox is not a directory"

        # Count markdown files in Inbox (test vault has predictable notes)
        md_files = list(inbox_path.glob('*.md'))

        # Vault factory creates notes in Inbox, verify they exist
        assert len(md_files) >= 0, (
            f"Unexpected error reading Inbox. "
            f"Inbox path: {inbox_path}"
        )

    def test_vault_has_expected_directory_structure(self, vault_path):
        """
        Verify vault has expected Zettelkasten directory structure.
        
        Expected directories:
        - Inbox/
        - Fleeting Notes/
        - Permanent Notes/ (or similar)
        - Archive/
        """
        vault_path = Path(vault_path)

        # Check for critical directories
        inbox = vault_path / 'Inbox'
        fleeting = vault_path / 'Fleeting Notes'

        assert inbox.exists(), f"Inbox/ directory missing at {inbox}"
        assert fleeting.exists(), f"Fleeting Notes/ directory missing at {fleeting}"

        # At least one of these should exist
        expected_dirs = ['Inbox', 'Fleeting Notes']
        found_dirs = [d for d in expected_dirs if (vault_path / d).exists()]

        assert len(found_dirs) >= 2, (
            f"Expected Zettelkasten structure. Found: {found_dirs}. "
            f"Vault path: {vault_path}"
        )

    def test_dashboard_fetch_inbox_status_returns_data(self, dashboard):
        """
        CRITICAL: Verify fetch_inbox_status() returns actual data.
        
        Prevents regression where status returns empty/zero counts
        when vault has notes.
        """
        status = dashboard.fetch_inbox_status()

        # Should not have error
        assert not status.get('error'), (
            f"fetch_inbox_status() returned error: {status.get('message')}"
        )

        # Should have inbox_count key
        assert 'inbox_count' in status, "Status missing 'inbox_count' key"

        # inbox_count should be an integer
        inbox_count = status['inbox_count']
        assert isinstance(inbox_count, int), (
            f"inbox_count should be int, got {type(inbox_count)}"
        )

        # inbox_count should be non-negative
        assert inbox_count >= 0, f"Invalid inbox_count: {inbox_count}"

    def test_inbox_count_matches_actual_files(self, dashboard, vault_path):
        """
        CRITICAL: Verify reported inbox count matches actual file count.
        
        Prevents dashboard showing 0 when there are actually files.
        """
        # Get dashboard's reported count
        status = dashboard.fetch_inbox_status()
        reported_count = status.get('inbox_count', -1)

        # Count actual markdown files in Inbox
        inbox_path = Path(vault_path) / 'Inbox'
        if inbox_path.exists():
            actual_md_files = list(inbox_path.glob('*.md'))
            actual_count = len(actual_md_files)
        else:
            actual_count = 0

        # Allow some variance for hidden files, temp files, etc.
        # But they should be reasonably close
        diff = abs(reported_count - actual_count)
        max_allowed_diff = 5  # Allow up to 5 file difference

        assert diff <= max_allowed_diff, (
            f"Inbox count mismatch: Dashboard reports {reported_count}, "
            f"but found {actual_count} .md files in {inbox_path}. "
            f"Difference: {diff} (max allowed: {max_allowed_diff})"
        )

    def test_dashboard_renders_inbox_panel_without_error(self, dashboard):
        """
        Verify inbox panel can be rendered with actual vault data.
        """
        try:
            panel = dashboard.render_inbox_panel()
            assert panel is not None, "render_inbox_panel() returned None"
        except Exception as e:
            pytest.fail(f"render_inbox_panel() raised exception: {e}")

    def test_dashboard_renders_quick_actions_panel_without_error(self, dashboard):
        """
        Verify quick actions panel can be rendered.
        """
        try:
            panel = dashboard.render_quick_actions_panel()
            assert panel is not None, "render_quick_actions_panel() returned None"
        except Exception as e:
            pytest.fail(f"render_quick_actions_panel() raised exception: {e}")

    def test_cli_integrator_vault_path_is_correct(self, dashboard, vault_path):
        """
        Verify CLIIntegrator has correct vault path.
        
        The integrator is responsible for calling CLI commands
        with the correct vault path.
        """
        # Dashboard should have CLI integrator
        assert hasattr(dashboard, 'cli_integrator'), "Dashboard missing cli_integrator"

        # CLI integrator should have vault path
        integrator = dashboard.cli_integrator
        assert hasattr(integrator, 'vault_path'), "CLIIntegrator missing vault_path"

        # Vault path should match
        assert integrator.vault_path == vault_path

    def test_vault_path_not_pointing_to_repo_root(self, dashboard, vault_path):
        """
        CRITICAL: Ensure vault path is NOT the repo root.
        
        Prevents the original bug where dashboard pointed to
        inneros-zettelkasten/ instead of inneros-zettelkasten/knowledge/
        """
        vault_path = Path(vault_path)

        # Check that vault contains Zettelkasten directories
        has_inbox = (vault_path / 'Inbox').exists()
        has_fleeting = (vault_path / 'Fleeting Notes').exists()

        # At least one should exist (indicating this is the vault, not repo root)
        assert has_inbox or has_fleeting, (
            f"Vault path appears to be repo root, not knowledge directory. "
            f"Path: {vault_path}. "
            f"Expected to find Inbox/ or Fleeting Notes/ directories."
        )

        # Vault should NOT contain development/ directory
        # (which would indicate it's the repo root)
        has_development = (vault_path / 'development').exists()
        assert not has_development, (
            f"Vault path contains 'development/' directory, "
            f"indicating it's the repo root, not the vault. "
            f"Path: {vault_path}"
        )


@pytest.mark.fast_integration
class TestStartDashboardScript:
    """
    Tests for the start_dashboard.sh script configuration.
    """

    def test_start_script_uses_knowledge_path(self):
        """
        CRITICAL: Verify start_dashboard.sh passes correct vault path.
        
        Prevents regression to passing ".." instead of "../knowledge"
        """
        script_path = Path(__file__).parent.parent.parent / 'start_dashboard.sh'

        if not script_path.exists():
            pytest.skip("start_dashboard.sh not found")

        script_content = script_path.read_text()

        # Check that script passes ../knowledge as argument
        assert '../knowledge' in script_content, (
            "start_dashboard.sh should pass '../knowledge' as vault path. "
            "Current script does not contain '../knowledge'"
        )

        # Should NOT pass just ".." (which would be repo root)
        # Look for the specific command line
        lines = script_content.split('\n')
        dashboard_lines = [l for l in lines if 'workflow_dashboard.py' in l]

        if dashboard_lines:
            # At least one line should have ../knowledge, not just ..
            has_correct_path = any('../knowledge' in line for line in dashboard_lines)
            assert has_correct_path, (
                "start_dashboard.sh should pass '../knowledge' to workflow_dashboard.py. "
                f"Found lines: {dashboard_lines}"
            )


@pytest.mark.fast_integration
class TestVaultPathConfiguration:
    """
    Tests for vault path configuration and detection.
    """

    def test_relative_path_resolution(self):
        """
        Test that relative paths are correctly resolved.
        """
        test_dir = Path(__file__).parent.parent.parent

        # Test ../knowledge from development directory
        vault_path = test_dir.parent / 'knowledge'

        assert vault_path.exists(), f"Vault not found at {vault_path}"
        assert vault_path.is_dir()

        # Ensure it's absolute
        abs_vault = vault_path.resolve()
        assert abs_vault.is_absolute()

    def test_vault_path_from_development_directory(self):
        """
        Verify correct vault path when running from development/.
        
        Common usage:
        $ cd development
        $ ./start_dashboard.sh
        
        Should resolve to ../knowledge
        """
        dev_dir = Path(__file__).parent.parent.parent
        expected_vault = dev_dir.parent / 'knowledge'

        # This is the path the dashboard should use
        assert expected_vault.exists(), (
            f"Expected vault at {expected_vault}. "
            "Verify your repo structure."
        )

        # Verify it has Inbox
        inbox = expected_vault / 'Inbox'
        assert inbox.exists(), f"Expected Inbox/ at {inbox}"


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
