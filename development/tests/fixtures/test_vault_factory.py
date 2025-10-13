"""
RED PHASE: Test Vault Factory - Week 1, Day 2, TDD Iteration 2

Tests for vault factory functions that create test fixtures with controlled content.
All tests should FAIL until vault_factory.py is implemented.

Performance Targets:
- create_minimal_vault(): <1 second
- create_small_vault(): <5 seconds
- Integration test suite: <30 seconds (down from 5-10 minutes)
"""

import pytest
import time
from pathlib import Path


def test_create_minimal_vault_exists():
    """RED: vault_factory module should exist with create_minimal_vault function."""
    from tests.fixtures import vault_factory
    
    assert hasattr(vault_factory, 'create_minimal_vault'), \
        "vault_factory should have create_minimal_vault function"


def test_create_minimal_vault_creates_structure(tmp_path):
    """RED: create_minimal_vault should create proper directory structure."""
    from tests.fixtures.vault_factory import create_minimal_vault
    
    vault_path, metadata = create_minimal_vault(tmp_path)
    
    # Verify vault directory exists
    assert vault_path.exists(), "Vault path should exist"
    assert vault_path.is_dir(), "Vault path should be a directory"
    
    # Verify standard Zettelkasten directory structure
    assert (vault_path / "Inbox").exists(), "Inbox directory should exist"
    assert (vault_path / "Permanent Notes").exists(), "Permanent Notes directory should exist"
    assert (vault_path / "Fleeting Notes").exists(), "Fleeting Notes directory should exist"
    assert (vault_path / "Literature Notes").exists(), "Literature Notes directory should exist"


def test_create_minimal_vault_creates_notes(tmp_path):
    """RED: create_minimal_vault should create exactly 3 notes."""
    from tests.fixtures.vault_factory import create_minimal_vault
    
    vault_path, metadata = create_minimal_vault(tmp_path)
    
    # Should create exactly 3 notes (1 permanent, 1 fleeting, 1 literature)
    all_notes = list(vault_path.rglob("*.md"))
    assert len(all_notes) == 3, f"Should create exactly 3 notes, found {len(all_notes)}"
    
    # Verify metadata reflects created notes
    assert metadata['note_count'] == 3, "Metadata should reflect 3 notes created"
    assert 'permanent_notes' in metadata, "Metadata should include permanent notes count"
    assert 'fleeting_notes' in metadata, "Metadata should include fleeting notes count"
    assert 'literature_notes' in metadata, "Metadata should include literature notes count"


def test_create_minimal_vault_has_valid_frontmatter(tmp_path):
    """RED: Created notes should have valid YAML frontmatter."""
    from tests.fixtures.vault_factory import create_minimal_vault
    import yaml
    
    vault_path, metadata = create_minimal_vault(tmp_path)
    
    # Check each note has valid frontmatter
    for note_file in vault_path.rglob("*.md"):
        content = note_file.read_text()
        
        # Should start with YAML frontmatter
        assert content.startswith('---\n'), f"{note_file.name} should start with YAML frontmatter"
        
        # Extract frontmatter
        parts = content.split('---\n')
        assert len(parts) >= 3, f"{note_file.name} should have complete frontmatter block"
        
        # Parse YAML
        frontmatter = yaml.safe_load(parts[1])
        assert isinstance(frontmatter, dict), f"{note_file.name} frontmatter should be valid YAML dict"
        
        # Should have required fields
        assert 'type' in frontmatter, f"{note_file.name} should have 'type' field"
        assert frontmatter['type'] in ['permanent', 'fleeting', 'literature'], \
            f"{note_file.name} type should be valid note type"


def test_create_minimal_vault_performance(tmp_path):
    """RED: create_minimal_vault should complete in <1 second."""
    from tests.fixtures.vault_factory import create_minimal_vault
    
    start_time = time.time()
    vault_path, metadata = create_minimal_vault(tmp_path)
    elapsed = time.time() - start_time
    
    assert elapsed < 1.0, f"create_minimal_vault took {elapsed:.2f}s, should be <1s"
    
    # Verify metadata includes timing
    assert 'creation_time_seconds' in metadata, "Metadata should include creation time"


def test_create_small_vault_exists():
    """RED: vault_factory should have create_small_vault function."""
    from tests.fixtures import vault_factory
    
    assert hasattr(vault_factory, 'create_small_vault'), \
        "vault_factory should have create_small_vault function"


def test_create_small_vault_creates_15_notes(tmp_path):
    """RED: create_small_vault should create exactly 15 notes."""
    from tests.fixtures.vault_factory import create_small_vault
    
    vault_path, metadata = create_small_vault(tmp_path)
    
    # Should create exactly 15 notes
    all_notes = list(vault_path.rglob("*.md"))
    assert len(all_notes) == 15, f"Should create exactly 15 notes, found {len(all_notes)}"
    
    # Should have diverse note types
    assert metadata['permanent_notes'] >= 3, "Should have at least 3 permanent notes"
    assert metadata['fleeting_notes'] >= 3, "Should have at least 3 fleeting notes"
    assert metadata['literature_notes'] >= 3, "Should have at least 3 literature notes"


def test_create_small_vault_performance(tmp_path):
    """RED: create_small_vault should complete in <5 seconds."""
    from tests.fixtures.vault_factory import create_small_vault
    
    start_time = time.time()
    vault_path, metadata = create_small_vault(tmp_path)
    elapsed = time.time() - start_time
    
    assert elapsed < 5.0, f"create_small_vault took {elapsed:.2f}s, should be <5s"


def test_vault_factory_returns_tuple(tmp_path):
    """RED: Factory functions should return (vault_path, metadata) tuple."""
    from tests.fixtures.vault_factory import create_minimal_vault
    
    result = create_minimal_vault(tmp_path)
    
    assert isinstance(result, tuple), "Should return tuple"
    assert len(result) == 2, "Should return (vault_path, metadata)"
    
    vault_path, metadata = result
    assert isinstance(vault_path, Path), "First element should be Path object"
    assert isinstance(metadata, dict), "Second element should be dict"


def test_vault_factory_creates_isolated_vaults(tmp_path):
    """RED: Each factory call should create isolated vault in tmp_path subdirectory."""
    from tests.fixtures.vault_factory import create_minimal_vault
    
    vault1_path, _ = create_minimal_vault(tmp_path)
    vault2_path, _ = create_minimal_vault(tmp_path)
    
    # Should create different directories
    assert vault1_path != vault2_path, "Multiple calls should create different vault paths"
    
    # Both should be subdirectories of tmp_path
    assert vault1_path.parent == tmp_path or tmp_path in vault1_path.parents
    assert vault2_path.parent == tmp_path or tmp_path in vault2_path.parents
