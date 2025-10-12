#!/usr/bin/env python3
"""
Integration tests for Dashboard + Real Vault
Ensures dashboard correctly finds and displays actual vault data
"""

import sys
import json
from pathlib import Path

# Add development directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

import pytest
from src.cli.workflow_dashboard import WorkflowDashboard


class TestDashboardVaultIntegration:
    """
    Integration tests to prevent vault path issues.
    
    These tests verify:
    1. Dashboard can find the actual vault
    2. Inbox status reflects real note counts
    3. CLI integration returns valid data
    """
    
    @pytest.fixture
    def actual_vault_path(self):
        """Return path to actual vault (knowledge/ directory)."""
        test_dir = Path(__file__).parent.parent.parent
        vault_path = test_dir.parent / 'knowledge'
        
        # Verify vault exists
        assert vault_path.exists(), f"Vault not found at {vault_path}"
        assert vault_path.is_dir(), f"Vault path is not a directory: {vault_path}"
        
        return str(vault_path)
    
    @pytest.fixture
    def dashboard(self, actual_vault_path):
        """Create dashboard with actual vault path."""
        return WorkflowDashboard(vault_path=actual_vault_path)
    
    def test_dashboard_finds_actual_vault(self, dashboard, actual_vault_path):
        """
        CRITICAL: Verify dashboard is pointed to correct vault.
        
        Prevents regression where dashboard looked at repo root (..)
        instead of actual vault (../knowledge).
        """
        # Dashboard should store the vault path
        assert dashboard.vault_path == actual_vault_path
        
        # Vault should exist
        vault_path_obj = Path(actual_vault_path)
        assert vault_path_obj.exists()
        assert vault_path_obj.is_dir()
    
    def test_inbox_directory_exists_and_has_notes(self, actual_vault_path):
        """
        CRITICAL: Verify Inbox/ directory exists and contains notes.
        
        Prevents false negatives where dashboard shows 0 notes
        when Inbox actually has content.
        """
        inbox_path = Path(actual_vault_path) / 'Inbox'
        
        # Inbox directory must exist
        assert inbox_path.exists(), f"Inbox not found at {inbox_path}"
        assert inbox_path.is_dir(), "Inbox is not a directory"
        
        # Count markdown files in Inbox
        md_files = list(inbox_path.glob('*.md'))
        
        # This test will fail if Inbox is truly empty, which is fine
        # It alerts us to unexpected state changes
        assert len(md_files) > 0, (
            f"Inbox has 0 markdown files. Expected some notes. "
            f"If Inbox is legitimately empty, update this test. "
            f"Inbox path: {inbox_path}"
        )
    
    def test_vault_has_expected_directory_structure(self, actual_vault_path):
        """
        Verify vault has expected Zettelkasten directory structure.
        
        Expected directories:
        - Inbox/
        - Fleeting Notes/
        - Permanent Notes/ (or similar)
        - Archive/
        """
        vault_path = Path(actual_vault_path)
        
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
    
    def test_inbox_count_matches_actual_files(self, dashboard, actual_vault_path):
        """
        CRITICAL: Verify reported inbox count matches actual file count.
        
        Prevents dashboard showing 0 when there are actually files.
        """
        # Get dashboard's reported count
        status = dashboard.fetch_inbox_status()
        reported_count = status.get('inbox_count', -1)
        
        # Count actual markdown files in Inbox
        inbox_path = Path(actual_vault_path) / 'Inbox'
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
    
    def test_cli_integrator_vault_path_is_correct(self, dashboard, actual_vault_path):
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
        assert integrator.vault_path == actual_vault_path
    
    def test_vault_path_not_pointing_to_repo_root(self, dashboard, actual_vault_path):
        """
        CRITICAL: Ensure vault path is NOT the repo root.
        
        Prevents the original bug where dashboard pointed to
        inneros-zettelkasten/ instead of inneros-zettelkasten/knowledge/
        """
        vault_path = Path(actual_vault_path)
        
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
