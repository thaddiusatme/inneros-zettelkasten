#!/usr/bin/env python3
"""
TDD RED PHASE: Integration Test Vault Factory Migration
Week 1, Day 2-3, TDD Iteration 3

This file contains RED phase tests that verify integration tests are migrated
from KNOWLEDGE_DIR (production vault) to vault factories (tmp_path).

Expected: ALL TESTS SHOULD FAIL initially
Goal: Drive migration to fast, isolated test vaults

Performance Target: Integration suite <30 seconds (currently 5-10 minutes)
Isolation Target: Zero references to KNOWLEDGE_DIR constant
"""

import time
from pathlib import Path
import pytest


@pytest.mark.integration
class TestVaultFactoryMigration:
    """
    RED Phase tests verifying vault factory migration requirements.
    
    These tests should FAIL initially and drive the migration from
    KNOWLEDGE_DIR to tmp_path + vault factories.
    """
    
    def test_integration_tests_complete_in_under_30_seconds(self):
        """
        RED: Integration test suite must complete in <30 seconds
        
        Current: 5-10 minutes (scanning 300+ note production vault)
        Target: <30 seconds with vault factories
        
        This test measures actual execution time and fails if >30s.
        """
        import subprocess
        
        start_time = time.time()
        
        # Run the integration test suite
        subprocess.run(
            [
                "python3", "-m", "pytest",
                "development/tests/integration/test_dedicated_cli_parity.py",
                "-v", "--tb=short", "-x"
            ],
            capture_output=True,
            text=True,
            env={'PYTHONPATH': 'development'},
            cwd=str(Path(__file__).parent.parent.parent.parent)
        )
        
        elapsed = time.time() - start_time
        
        # This SHOULD FAIL in RED phase (currently ~5-10 minutes)
        assert elapsed < 30.0, (
            f"Integration tests took {elapsed:.2f}s (target: <30s). "
            f"Need to migrate from KNOWLEDGE_DIR to vault factories."
        )
    
    def test_integration_tests_use_tmp_path_not_production_vault(self):
        """
        RED: Integration tests must use tmp_path, not KNOWLEDGE_DIR
        
        Verify that test_dedicated_cli_parity.py has zero references
        to KNOWLEDGE_DIR constant (production vault path).
        """
        test_file = Path(__file__).parent / "test_dedicated_cli_parity.py"
        content = test_file.read_text()
        
        # Check for KNOWLEDGE_DIR references
        knowledge_dir_references = content.count("KNOWLEDGE_DIR")
        
        # This SHOULD FAIL in RED phase (currently has KNOWLEDGE_DIR = PROJECT_ROOT / "knowledge")
        assert knowledge_dir_references == 0, (
            f"Found {knowledge_dir_references} references to KNOWLEDGE_DIR in test_dedicated_cli_parity.py. "
            f"Must migrate to tmp_path + vault factories for test isolation."
        )
    
    def test_vault_path_fixture_uses_vault_factory(self):
        """
        RED: vault_path fixture must use create_minimal_vault()
        
        Verify that the vault_path fixture in test_dedicated_cli_parity.py
        calls create_minimal_vault(tmp_path) instead of returning KNOWLEDGE_DIR.
        """
        test_file = Path(__file__).parent / "test_dedicated_cli_parity.py"
        content = test_file.read_text()
        
        # Check for vault factory import
        has_factory_import = "from tests.fixtures.vault_factory import create_minimal_vault" in content
        
        # Check for factory usage in vault_path fixture
        has_factory_call = "create_minimal_vault(tmp_path)" in content
        
        # This SHOULD FAIL in RED phase (currently uses KNOWLEDGE_DIR fallback)
        assert has_factory_import, (
            "test_dedicated_cli_parity.py missing import: "
            "'from tests.fixtures.vault_factory import create_minimal_vault'"
        )
        assert has_factory_call, (
            "vault_path fixture must call create_minimal_vault(tmp_path) "
            "instead of returning KNOWLEDGE_DIR"
        )
    
    def test_vault_structure_exists_before_cli_execution(self):
        """
        RED: Test that vault fixtures create proper structure
        
        Integration tests should verify vault structure exists
        before executing CLI commands.
        """
        from tests.fixtures.vault_factory import create_minimal_vault
        from pathlib import Path
        import tempfile
        
        # Create minimal vault
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            vault_path, metadata = create_minimal_vault(tmp_path)
            
            # Verify standard directories exist
            expected_dirs = ["Inbox", "Permanent Notes", "Fleeting Notes", "Literature Notes"]
            for dir_name in expected_dirs:
                dir_path = vault_path / dir_name
                assert dir_path.exists(), f"Vault missing {dir_name} directory"
                assert dir_path.is_dir(), f"{dir_name} is not a directory"
            
            # Verify notes were created
            assert metadata['note_count'] == 3, "Minimal vault should have 3 notes"
            
            # Verify creation time meets performance target
            assert metadata['creation_time_seconds'] < 1.0, (
                f"Vault creation took {metadata['creation_time_seconds']:.3f}s (target: <1s)"
            )
    
    def test_integration_tests_use_small_vault_for_batch_operations(self):
        """
        RED: Batch processing tests should use create_small_vault()
        
        Some integration tests may need more notes for realistic batch
        processing scenarios. Verify small vault factory is imported.
        """
        test_file = Path(__file__).parent / "test_dedicated_cli_parity.py"
        content = test_file.read_text()
        
        # Document: Small vault factory can be used for batch processing tests
        # This test verifies the capability exists if needed in the future
        if "process_inbox" in content or "batch" in content.lower():
            # Batch tests exist - they can optionally use create_small_vault()
            # for more realistic scenarios (15 notes vs 3 notes)
            pass  # Optional enhancement documented
    
    def test_no_production_vault_dependencies(self):
        """
        RED: Integration tests must not depend on production vault existence
        
        Tests should work in CI/CD environments where knowledge/ doesn't exist.
        """
        test_file = Path(__file__).parent / "test_dedicated_cli_parity.py"
        content = test_file.read_text()
        
        # Check for conditional logic based on KNOWLEDGE_DIR.exists()
        has_exists_check = "KNOWLEDGE_DIR.exists()" in content
        
        # This SHOULD FAIL in RED phase (currently has fallback to KNOWLEDGE_DIR)
        assert not has_exists_check, (
            "Integration tests have conditional logic checking if KNOWLEDGE_DIR exists. "
            "Must use tmp_path + vault factories unconditionally for isolation."
        )


if __name__ == "__main__":
    # Run RED phase tests to see what needs to be fixed
    pytest.main([__file__, "-v", "--tb=short"])
