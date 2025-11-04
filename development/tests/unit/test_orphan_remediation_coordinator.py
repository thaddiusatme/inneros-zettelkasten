"""
TDD Iteration for OrphanRemediationCoordinator extraction from WorkflowManager.

ADR-002 Phase 8: Extract orphan remediation logic (~242 LOC) from WorkflowManager.

Tests cover:
- Orphan detection and filtering by scope (permanent/fleeting/all)
- Target note resolution (explicit path, Home Note, MOC fallback)
- Bidirectional link insertion with backups
- Wiki-link detection and duplicate prevention
- Checklist mode generation
- Section appending logic for structured link insertion
- Error handling (missing files, broken links, permission errors)
- Dry-run mode (no file modifications)
- Integration with AnalyticsCoordinator for orphan detection
"""

import pytest
from pathlib import Path
from unittest.mock import Mock
import tempfile
import shutil

from src.config.vault_config_loader import get_vault_config


class TestOrphanRemediationCoordinator:
    """Test suite for OrphanRemediationCoordinator extraction."""

    @pytest.fixture
    def temp_vault(self):
        """
        Create temporary vault structure for testing with vault config.

        Updated for GitHub Issue #45 to use vault config paths (knowledge/ subdirectories).
        """
        temp_dir = tempfile.mkdtemp()
        vault_path = Path(temp_dir)

        # Get vault config to create proper directory structure
        config = get_vault_config(str(vault_path))

        # Create vault config directories
        config.permanent_dir.mkdir(parents=True, exist_ok=True)
        config.fleeting_dir.mkdir(parents=True, exist_ok=True)
        config.inbox_dir.mkdir(parents=True, exist_ok=True)

        # Create test files using vault config paths
        (vault_path / "Home Note.md").write_text("# Home Note\n\n## Linked Notes\n")
        (config.permanent_dir / "test-permanent.md").write_text(
            "---\ntitle: Test Permanent\ntype: permanent\n---\n\nContent"
        )
        (config.fleeting_dir / "test-fleeting.md").write_text(
            "---\ntitle: Test Fleeting\ntype: fleeting\n---\n\nContent"
        )

        yield vault_path

        # Cleanup
        shutil.rmtree(temp_dir)

    @pytest.fixture
    def mock_analytics_coordinator(self, temp_vault):
        """
        Mock AnalyticsCoordinator for orphan detection.

        Updated for GitHub Issue #45 to return vault config paths.
        """
        # Get vault config to use correct paths
        config = get_vault_config(str(temp_vault))

        coordinator = Mock()
        coordinator.detect_orphaned_notes_comprehensive.return_value = [
            {
                "path": str(config.permanent_dir / "orphan1.md"),
                "title": "Orphan 1",
                "last_modified": "2024-10-01",
            },
            {
                "path": str(config.fleeting_dir / "orphan2.md"),
                "title": "Orphan 2",
                "last_modified": "2024-10-02",
            },
            {
                "path": str(config.permanent_dir / "orphan3.md"),
                "title": "Orphan 3",
                "last_modified": "2024-10-03",
            },
        ]
        return coordinator

    # Test 1: Coordinator initialization with dependencies
    def test_coordinator_initialization(self, mock_analytics_coordinator, temp_vault):
        """Test OrphanRemediationCoordinator initializes with required dependencies."""
        from src.ai.orphan_remediation_coordinator import OrphanRemediationCoordinator

        coordinator = OrphanRemediationCoordinator(
            base_dir=str(temp_vault), analytics_coordinator=mock_analytics_coordinator
        )

        assert coordinator.base_dir == str(temp_vault)
        assert coordinator.analytics_coordinator == mock_analytics_coordinator

    # Test 2: Orphan filtering by scope - permanent only
    def test_list_orphans_by_scope_permanent(
        self, mock_analytics_coordinator, temp_vault
    ):
        """Test filtering orphans by scope='permanent'."""
        from src.ai.orphan_remediation_coordinator import OrphanRemediationCoordinator

        coordinator = OrphanRemediationCoordinator(
            base_dir=str(temp_vault), analytics_coordinator=mock_analytics_coordinator
        )

        orphans = coordinator.list_orphans_by_scope("permanent")

        # Should only return orphans from Permanent Notes directory
        assert len(orphans) == 2
        assert all("Permanent Notes" in o["path"] for o in orphans)

    # Test 3: Orphan filtering by scope - fleeting only
    def test_list_orphans_by_scope_fleeting(
        self, mock_analytics_coordinator, temp_vault
    ):
        """Test filtering orphans by scope='fleeting'."""
        from src.ai.orphan_remediation_coordinator import OrphanRemediationCoordinator

        coordinator = OrphanRemediationCoordinator(
            base_dir=str(temp_vault), analytics_coordinator=mock_analytics_coordinator
        )

        orphans = coordinator.list_orphans_by_scope("fleeting")

        # Should only return orphans from Fleeting Notes directory
        assert len(orphans) == 1
        assert "Fleeting Notes" in orphans[0]["path"]

    # Test 4: Orphan filtering by scope - all notes
    def test_list_orphans_by_scope_all(self, mock_analytics_coordinator, temp_vault):
        """Test filtering orphans by scope='all'."""
        from src.ai.orphan_remediation_coordinator import OrphanRemediationCoordinator

        coordinator = OrphanRemediationCoordinator(
            base_dir=str(temp_vault), analytics_coordinator=mock_analytics_coordinator
        )

        orphans = coordinator.list_orphans_by_scope("all")

        # Should return all orphans from both directories
        assert len(orphans) == 3

    # Test 5: Target note resolution - explicit path
    def test_find_target_explicit_path(self, mock_analytics_coordinator, temp_vault):
        """Test target resolution with explicit path provided."""
        from src.ai.orphan_remediation_coordinator import OrphanRemediationCoordinator

        coordinator = OrphanRemediationCoordinator(
            base_dir=str(temp_vault), analytics_coordinator=mock_analytics_coordinator
        )

        target_path = temp_vault / "Home Note.md"
        result = coordinator.resolve_target_note(target=str(target_path))

        assert result == target_path
        assert result.exists()

    # Test 6: Target note resolution - Home Note fallback
    def test_find_target_home_note_fallback(
        self, mock_analytics_coordinator, temp_vault
    ):
        """Test target resolution defaults to Home Note when no target specified."""
        from src.ai.orphan_remediation_coordinator import OrphanRemediationCoordinator

        coordinator = OrphanRemediationCoordinator(
            base_dir=str(temp_vault), analytics_coordinator=mock_analytics_coordinator
        )

        result = coordinator.resolve_target_note(target=None)

        assert result.name == "Home Note.md"
        assert result.exists()

    # Test 7: Target note resolution - MOC fallback
    def test_find_target_moc_fallback(self, mock_analytics_coordinator, temp_vault):
        """Test target resolution falls back to MOC when Home Note doesn't exist."""
        from src.ai.orphan_remediation_coordinator import OrphanRemediationCoordinator

        # Remove Home Note
        (temp_vault / "Home Note.md").unlink()

        # Create MOC using vault config path
        config = get_vault_config(str(temp_vault))
        (config.permanent_dir / "Test MOC.md").write_text("# MOC\n")

        coordinator = OrphanRemediationCoordinator(
            base_dir=str(temp_vault), analytics_coordinator=mock_analytics_coordinator
        )

        result = coordinator.resolve_target_note(target=None)

        assert "MOC" in result.name
        assert result.exists()

    # Test 8: Wiki-link detection - basic format
    def test_has_wikilink_basic_format(self, mock_analytics_coordinator, temp_vault):
        """Test wiki-link detection with basic [[note]] format."""
        from src.ai.orphan_remediation_coordinator import OrphanRemediationCoordinator

        coordinator = OrphanRemediationCoordinator(
            base_dir=str(temp_vault), analytics_coordinator=mock_analytics_coordinator
        )

        text = "Some content with [[test-note]] link."
        assert coordinator.has_wikilink(text, "test-note") is True
        assert coordinator.has_wikilink(text, "other-note") is False

    # Test 9: Wiki-link detection - alias format
    def test_has_wikilink_alias_format(self, mock_analytics_coordinator, temp_vault):
        """Test wiki-link detection with [[note|alias]] format."""
        from src.ai.orphan_remediation_coordinator import OrphanRemediationCoordinator

        coordinator = OrphanRemediationCoordinator(
            base_dir=str(temp_vault), analytics_coordinator=mock_analytics_coordinator
        )

        text = "Content with [[test-note|Custom Alias]] link."
        assert coordinator.has_wikilink(text, "test-note") is True

    # Test 10: Section appending - existing section
    def test_append_to_existing_section(self, mock_analytics_coordinator, temp_vault):
        """Test appending link to existing ## Linked Notes section."""
        from src.ai.orphan_remediation_coordinator import OrphanRemediationCoordinator

        coordinator = OrphanRemediationCoordinator(
            base_dir=str(temp_vault), analytics_coordinator=mock_analytics_coordinator
        )

        text = "# Note\n\n## Linked Notes\n\n- [[existing-link]]\n"
        result = coordinator.append_to_section(text, "[[new-link]]")

        assert "[[new-link]]" in result
        assert "## Linked Notes" in result
        assert "[[existing-link]]" in result

    # Test 11: Section appending - create new section
    def test_append_to_new_section(self, mock_analytics_coordinator, temp_vault):
        """Test creating new ## Linked Notes section when it doesn't exist."""
        from src.ai.orphan_remediation_coordinator import OrphanRemediationCoordinator

        coordinator = OrphanRemediationCoordinator(
            base_dir=str(temp_vault), analytics_coordinator=mock_analytics_coordinator
        )

        text = "# Note\n\nSome content without linked section."
        result = coordinator.append_to_section(text, "[[new-link]]")

        assert "## Linked Notes" in result
        assert "[[new-link]]" in result

    # Test 12: Bidirectional link insertion - both files modified
    def test_insert_bidirectional_links_both_modified(
        self, mock_analytics_coordinator, temp_vault
    ):
        """Test bidirectional link insertion modifies both orphan and target."""
        from src.ai.orphan_remediation_coordinator import OrphanRemediationCoordinator

        # Use vault config path
        config = get_vault_config(str(temp_vault))
        orphan_path = config.permanent_dir / "orphan.md"
        target_path = temp_vault / "Home Note.md"

        orphan_path.write_text("# Orphan\n\nContent")

        coordinator = OrphanRemediationCoordinator(
            base_dir=str(temp_vault), analytics_coordinator=mock_analytics_coordinator
        )

        result = coordinator.insert_bidirectional_links(
            orphan_path=orphan_path, target_path=target_path, dry_run=False
        )

        assert result["modified_target"] is True
        assert result["modified_orphan"] is True
        assert "backups" in result

    # Test 13: Bidirectional link insertion - skip duplicates
    def test_insert_bidirectional_links_skip_duplicates(
        self, mock_analytics_coordinator, temp_vault
    ):
        """Test link insertion skips when links already exist."""
        from src.ai.orphan_remediation_coordinator import OrphanRemediationCoordinator

        # Use vault config path
        config = get_vault_config(str(temp_vault))
        orphan_path = config.permanent_dir / "orphan.md"
        target_path = temp_vault / "Home Note.md"

        orphan_path.write_text("# Orphan\n\n[[Home Note]]")
        (temp_vault / "Home Note.md").write_text("# Home\n\n[[orphan]]")

        coordinator = OrphanRemediationCoordinator(
            base_dir=str(temp_vault), analytics_coordinator=mock_analytics_coordinator
        )

        result = coordinator.insert_bidirectional_links(
            orphan_path=orphan_path, target_path=target_path, dry_run=False
        )

        # No modifications needed - links already exist
        assert result["modified_target"] is False
        assert result["modified_orphan"] is False

    # Test 14: Backup creation on file modification
    def test_backup_file_creation(self, mock_analytics_coordinator, temp_vault):
        """Test backup files are created before modifications."""
        from src.ai.orphan_remediation_coordinator import OrphanRemediationCoordinator

        test_file = temp_vault / "test.md"
        test_file.write_text("Original content")

        coordinator = OrphanRemediationCoordinator(
            base_dir=str(temp_vault), analytics_coordinator=mock_analytics_coordinator
        )

        backup_path = coordinator.backup_file(test_file)

        assert backup_path is not None
        assert backup_path.exists()
        assert ".bak." in backup_path.name
        assert backup_path.read_text() == "Original content"

    # Test 15: Dry-run mode - no file modifications
    def test_remediate_dry_run_no_modifications(
        self, mock_analytics_coordinator, temp_vault
    ):
        """Test dry-run mode doesn't modify any files."""
        from src.ai.orphan_remediation_coordinator import OrphanRemediationCoordinator

        coordinator = OrphanRemediationCoordinator(
            base_dir=str(temp_vault), analytics_coordinator=mock_analytics_coordinator
        )

        original_home_content = (temp_vault / "Home Note.md").read_text()

        result = coordinator.remediate_orphaned_notes(
            mode="link",
            scope="permanent",
            limit=1,
            target=str(temp_vault / "Home Note.md"),
            dry_run=True,
        )

        # No files should be modified in dry-run
        assert (temp_vault / "Home Note.md").read_text() == original_home_content
        assert result["dry_run"] is True
        assert result["summary"]["processed"] >= 0

    # Test 16: Checklist mode generation
    def test_remediate_checklist_mode(self, mock_analytics_coordinator, temp_vault):
        """Test checklist mode generates markdown checklist."""
        from src.ai.orphan_remediation_coordinator import OrphanRemediationCoordinator

        coordinator = OrphanRemediationCoordinator(
            base_dir=str(temp_vault), analytics_coordinator=mock_analytics_coordinator
        )

        result = coordinator.remediate_orphaned_notes(
            mode="checklist",
            scope="permanent",
            limit=5,
            target=str(temp_vault / "Home Note.md"),
            dry_run=True,
        )

        assert result["mode"] == "checklist"
        assert "checklist_markdown" in result
        assert "# Orphan Remediation Checklist" in result["checklist_markdown"]
        assert "- [ ]" in result["checklist_markdown"]

    # Test 17: Link mode with limit
    def test_remediate_link_mode_with_limit(
        self, mock_analytics_coordinator, temp_vault
    ):
        """Test link mode respects limit parameter."""
        from src.ai.orphan_remediation_coordinator import OrphanRemediationCoordinator

        coordinator = OrphanRemediationCoordinator(
            base_dir=str(temp_vault), analytics_coordinator=mock_analytics_coordinator
        )

        result = coordinator.remediate_orphaned_notes(
            mode="link",
            scope="all",
            limit=2,  # Limit to 2 orphans
            target=str(temp_vault / "Home Note.md"),
            dry_run=True,
        )

        assert result["limit"] == 2
        assert result["summary"]["considered"] >= 2
        # With dry_run, processed count reflects attempted operations

    # Test 18: Error handling - missing target note
    def test_remediate_error_missing_target(
        self, mock_analytics_coordinator, temp_vault
    ):
        """Test error handling when target note doesn't exist."""
        from src.ai.orphan_remediation_coordinator import OrphanRemediationCoordinator

        coordinator = OrphanRemediationCoordinator(
            base_dir=str(temp_vault), analytics_coordinator=mock_analytics_coordinator
        )

        result = coordinator.remediate_orphaned_notes(
            mode="link",
            scope="permanent",
            limit=10,
            target="/nonexistent/path.md",
            dry_run=True,
        )

        assert "error" in result
        assert "not found" in result["error"].lower()


class TestVaultConfigIntegration:
    """Test OrphanRemediationCoordinator integration with vault configuration (GitHub Issue #45)."""

    @pytest.fixture
    def vault_with_config(self, tmp_path):
        """
        Fixture providing vault structure with vault configuration.

        Creates knowledge/ subdirectory structure as per vault_config.yaml.
        Used for vault config integration tests (GitHub Issue #45 Phase 2 Priority 3).

        Copied pattern from test_batch_processing_coordinator.py for consistency.
        """
        vault = tmp_path / "vault"
        vault.mkdir()

        # Get vault config (creates knowledge/ subdirectory structure)
        config = get_vault_config(str(vault))

        # Ensure vault config directories exist
        config.fleeting_dir.mkdir(parents=True, exist_ok=True)
        config.permanent_dir.mkdir(parents=True, exist_ok=True)
        config.inbox_dir.mkdir(parents=True, exist_ok=True)

        # Create test orphan notes using vault config paths
        (config.permanent_dir / "orphan1.md").write_text("# Orphan 1\n\nContent")
        (config.permanent_dir / "orphan2.md").write_text("# Orphan 2\n\nContent")
        (config.fleeting_dir / "orphan3.md").write_text("# Orphan 3\n\nContent")

        # Create Home Note at vault root
        (vault / "Home Note.md").write_text("# Home Note\n\n## Linked Notes\n")

        return {
            "vault": vault,
            "config": config,
            "fleeting_dir": config.fleeting_dir,
            "permanent_dir": config.permanent_dir,
            "inbox_dir": config.inbox_dir,
        }

    def test_coordinator_uses_vault_config_for_directory_paths(self, vault_with_config):
        """
        RED PHASE: Verify coordinator uses vault config for directory paths.

        This test validates that OrphanRemediationCoordinator uses the centralized
        vault configuration (knowledge/Permanent Notes, knowledge/Fleeting Notes)
        instead of hardcoded paths (Permanent Notes/, Fleeting Notes/).

        Expected to FAIL until GREEN phase:
        1. Updates constructor to accept base_dir and workflow_manager parameters
        2. Loads directory paths from get_vault_config() internally
        3. Uses vault config paths in list_orphans_by_scope() method
        4. Uses vault config paths in _find_default_link_target() method

        Part of GitHub Issue #45 Phase 2 Priority 3 (P1-VAULT-11).
        Duration target: ~35 minutes (proven pattern from P1-VAULT-10).
        """
        from src.ai.orphan_remediation_coordinator import OrphanRemediationCoordinator

        vault = vault_with_config["vault"]
        config = vault_with_config["config"]

        # Create mock analytics coordinator
        mock_analytics = Mock()
        mock_analytics.detect_orphaned_notes_comprehensive.return_value = [
            {
                "path": str(config.permanent_dir / "orphan1.md"),
                "title": "Orphan 1",
                "last_modified": "2024-10-01",
            },
            {
                "path": str(config.permanent_dir / "orphan2.md"),
                "title": "Orphan 2",
                "last_modified": "2024-10-02",
            },
            {
                "path": str(config.fleeting_dir / "orphan3.md"),
                "title": "Orphan 3",
                "last_modified": "2024-10-03",
            },
        ]

        # Initialize coordinator with base_dir (will fail in RED - no base_dir parameter yet)
        coordinator = OrphanRemediationCoordinator(
            base_dir=vault, analytics_coordinator=mock_analytics
        )

        # Verify coordinator loads vault config and exposes directory attributes
        # These attributes don't exist yet - will fail in RED phase
        assert hasattr(
            coordinator, "permanent_dir"
        ), "Coordinator should have permanent_dir attribute from vault config"
        assert hasattr(
            coordinator, "fleeting_dir"
        ), "Coordinator should have fleeting_dir attribute from vault config"

        # Verify coordinator uses vault config paths (should use knowledge/ subdirectories)
        assert (
            coordinator.permanent_dir == config.permanent_dir
        ), f"Expected permanent_dir={config.permanent_dir}, got {coordinator.permanent_dir}"
        assert (
            coordinator.fleeting_dir == config.fleeting_dir
        ), f"Expected fleeting_dir={config.fleeting_dir}, got {coordinator.fleeting_dir}"

        # Verify paths contain knowledge/ subdirectory structure
        assert "knowledge" in str(
            coordinator.permanent_dir
        ), f"Expected 'knowledge' in permanent_dir path: {coordinator.permanent_dir}"
        assert "knowledge" in str(
            coordinator.fleeting_dir
        ), f"Expected 'knowledge' in fleeting_dir path: {coordinator.fleeting_dir}"
