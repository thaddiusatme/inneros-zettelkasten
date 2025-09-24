#!/usr/bin/env python3
"""
Test suite for LinkInsertionEngine - TDD Iteration 4 (RED Phase)
Comprehensive failing tests for actual note modification with backup/rollback safety
"""

import pytest
import tempfile
import shutil
import json
from pathlib import Path
from dataclasses import dataclass
from typing import List, Dict, Any
import sys
import os

# Add development directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../src'))

from ai.link_suggestion_engine import LinkSuggestion
# Import the engine we created - should work now after GREEN phase completion!
from ai.link_insertion_engine import LinkInsertionEngine
from ai.link_insertion_utils import InsertionResult, SafetyBackupManager as BackupManager

@dataclass
class MockSuggestionForInsertion:
    """Mock LinkSuggestion for insertion testing"""
    source_note: str
    target_note: str
    suggested_link_text: str
    suggested_location: str
    insertion_context: str
    quality_score: float = 0.8
    confidence: str = "high"

class TestLinkInsertionEngine:
    """Test suite for LinkInsertionEngine - actual note modification with safety"""
    
    @pytest.fixture
    def temp_vault(self):
        """Create temporary vault with realistic note structure"""
        with tempfile.TemporaryDirectory() as temp_dir:
            vault_path = Path(temp_dir)
            
            # Create directory structure
            (vault_path / "Permanent Notes").mkdir()
            (vault_path / "Fleeting Notes").mkdir()  
            (vault_path / "Literature Notes").mkdir()
            (vault_path / "backups").mkdir()
            
            # Create test notes with realistic content
            ai_note = vault_path / "Permanent Notes" / "ai-concepts.md"
            ai_note.write_text("""---
type: permanent
tags: [ai, machine-learning, concepts]
created: 2025-09-24 10:00
---
# AI Concepts

This note covers fundamental artificial intelligence concepts including
machine learning algorithms and neural networks.

## Core Concepts
- Deep learning fundamentals
- Neural network architectures
- Pattern recognition systems

## Applications
Machine learning has many practical applications in modern technology.

## Related Concepts
""")
            
            ml_note = vault_path / "Permanent Notes" / "machine-learning-basics.md"
            ml_note.write_text("""---
type: permanent
tags: [machine-learning, algorithms]
created: 2025-09-24 09:30
---
# Machine Learning Basics

Introduction to machine learning algorithms and their applications.

## Key Topics
- Supervised learning
- Unsupervised learning  
- Deep neural networks

## See Also
""")
            
            # Create note without structure for testing fallback insertion
            simple_note = vault_path / "Fleeting Notes" / "simple-note.md"
            simple_note.write_text("""---
type: fleeting
---
# Simple Note

Just some basic content without special sections.
""")
            
            yield vault_path
    
    @pytest.fixture
    def insertion_engine(self, temp_vault):
        """Create LinkInsertionEngine instance"""
        return LinkInsertionEngine(vault_path=str(temp_vault))
    
    def test_insertion_engine_initialization_fails(self, temp_vault):
        """TEST 1: LinkInsertionEngine initializes with backup configuration - WILL FAIL"""
        # This will fail because LinkInsertionEngine doesn't exist yet
        engine = LinkInsertionEngine(vault_path=str(temp_vault))
        assert engine.vault_path == str(temp_vault)
        assert hasattr(engine, 'backup_manager')
        assert hasattr(engine, 'insertion_validator')
        assert engine.backup_enabled is True
    
    def test_insert_single_suggestion_into_structured_note_fails(self, insertion_engine, temp_vault):
        """TEST 2: Insert single link suggestion into note with Related Concepts section - WILL FAIL"""
        # Arrange - Create suggestion for structured note
        suggestion = MockSuggestionForInsertion(
            source_note="Permanent Notes/ai-concepts.md",
            target_note="Permanent Notes/machine-learning-basics.md",
            suggested_link_text="[[Machine Learning Basics]]",
            suggested_location="related_concepts",
            insertion_context="## Related Concepts"
        )
        
        # Act - Insert suggestion (will fail - method doesn't exist)
        result = insertion_engine.insert_suggestions_into_note(
            note_path="Permanent Notes/ai-concepts.md",
            suggestions=[suggestion]
        )
        
        # Assert - Should successfully insert with backup created
        assert isinstance(result, InsertionResult)
        assert result.success is True
        assert result.insertions_made == 1
        assert result.backup_path is not None
        
        # Verify actual file modification
        note_path = temp_vault / "Permanent Notes" / "ai-concepts.md"
        content = note_path.read_text()
        assert "[[Machine Learning Basics]]" in content
        assert content.count("## Related Concepts") == 1  # Section should still exist
    
    def test_backup_creation_before_insertion_fails(self, insertion_engine, temp_vault):
        """TEST 3: Backup system creates timestamped backup before any modifications - WILL FAIL"""
        # Arrange - Note to modify
        note_path = "Permanent Notes/ai-concepts.md"
        original_content = (temp_vault / note_path).read_text()
        
        suggestion = MockSuggestionForInsertion(
            source_note=note_path,
            target_note="Permanent Notes/machine-learning-basics.md", 
            suggested_link_text="[[ML Basics]]",
            suggested_location="related_concepts",
            insertion_context="## Related Concepts"
        )
        
        # Act - Insert with backup
        result = insertion_engine.insert_suggestions_into_note(note_path, [suggestion])
        
        # Assert - Backup should be created
        assert result.backup_path is not None
        backup_path = Path(result.backup_path)
        assert backup_path.exists()
        assert backup_path.name.startswith("ai-concepts_backup_")
        
        # Backup should contain original content
        backup_content = backup_path.read_text()
        assert backup_content == original_content
    
    def test_rollback_on_insertion_failure_fails(self, insertion_engine, temp_vault):
        """TEST 4: Automatic rollback when insertion fails - WILL FAIL"""
        # Arrange - Create invalid suggestion that should cause failure
        note_path = "Permanent Notes/ai-concepts.md"
        original_content = (temp_vault / note_path).read_text()
        
        invalid_suggestion = MockSuggestionForInsertion(
            source_note=note_path,
            target_note="nonexistent-note.md",  # Invalid target
            suggested_link_text="[[Nonexistent Note]]",
            suggested_location="invalid_section",  # Invalid location
            insertion_context="## Nonexistent Section"
        )
        
        # Act - Attempt insertion (should fail and rollback)
        result = insertion_engine.insert_suggestions_into_note(
            note_path, 
            [invalid_suggestion],
            validate_targets=True
        )
        
        # Assert - Should fail with rollback
        assert result.success is False
        assert result.insertions_made == 0
        assert "rollback" in result.error_message.lower()
        
        # Original file should be unchanged (rolled back)
        current_content = (temp_vault / note_path).read_text()
        assert current_content == original_content
    
    def test_markdown_syntax_preservation_fails(self, insertion_engine, temp_vault):
        """TEST 5: Insertion preserves markdown syntax and structure - WILL FAIL"""
        suggestion = MockSuggestionForInsertion(
            source_note="Permanent Notes/machine-learning-basics.md",
            target_note="Permanent Notes/ai-concepts.md",
            suggested_link_text="[[AI Concepts]]",
            suggested_location="see_also", 
            insertion_context="## See Also"
        )
        
        # Act
        result = insertion_engine.insert_suggestions_into_note(
            "Permanent Notes/machine-learning-basics.md",
            [suggestion]
        )
        
        # Assert - Markdown syntax should be preserved
        assert result.success is True
        note_content = (temp_vault / "Permanent Notes" / "machine-learning-basics.md").read_text()
        
        # Should maintain YAML frontmatter
        assert note_content.startswith("---")
        assert "type: permanent" in note_content
        
        # Should maintain heading structure
        assert "# Machine Learning Basics" in note_content
        assert "## Key Topics" in note_content
        assert "## See Also" in note_content
        
        # Should properly insert under See Also section
        lines = note_content.split('\n')
        see_also_index = next(i for i, line in enumerate(lines) if line.strip() == "## See Also")
        see_also_lines = lines[see_also_index + 1:see_also_index + 5]
        assert any("[[AI Concepts]]" in line for line in see_also_lines)
    
    def test_duplicate_link_prevention_fails(self, insertion_engine, temp_vault):
        """TEST 6: Prevent insertion of duplicate links - WILL FAIL"""
        # Arrange - Pre-insert a link manually
        note_path = temp_vault / "Permanent Notes" / "ai-concepts.md"
        content = note_path.read_text()
        content = content.replace("## Related Concepts", "## Related Concepts\n- [[Machine Learning Basics]]")
        note_path.write_text(content)
        
        # Try to insert the same link again
        duplicate_suggestion = MockSuggestionForInsertion(
            source_note="Permanent Notes/ai-concepts.md",
            target_note="Permanent Notes/machine-learning-basics.md",
            suggested_link_text="[[Machine Learning Basics]]",
            suggested_location="related_concepts",
            insertion_context="## Related Concepts"
        )
        
        # Act
        result = insertion_engine.insert_suggestions_into_note(
            "Permanent Notes/ai-concepts.md",
            [duplicate_suggestion],
            check_duplicates=True
        )
        
        # Assert - Should detect duplicate and skip
        assert result.success is True
        assert result.insertions_made == 0
        assert result.duplicates_skipped == 1
        
        # Should not have duplicate links in content
        final_content = note_path.read_text()
        assert final_content.count("[[Machine Learning Basics]]") == 1
    
    def test_batch_insertion_with_progress_tracking_fails(self, insertion_engine, temp_vault):
        """TEST 7: Batch insertion of multiple suggestions with progress tracking - WILL FAIL"""
        suggestions = [
            MockSuggestionForInsertion(
                source_note="Permanent Notes/ai-concepts.md",
                target_note="Permanent Notes/machine-learning-basics.md",
                suggested_link_text="[[ML Basics]]",
                suggested_location="related_concepts",
                insertion_context="## Related Concepts"
            ),
            MockSuggestionForInsertion(
                source_note="Permanent Notes/machine-learning-basics.md", 
                target_note="Permanent Notes/ai-concepts.md",
                suggested_link_text="[[AI Concepts]]",
                suggested_location="see_also",
                insertion_context="## See Also"
            )
        ]
        
        # Act - Batch insert
        results = insertion_engine.insert_multiple_suggestions(
            suggestions,
            progress_callback=lambda x: None  # Mock progress callback
        )
        
        # Assert - Should process all suggestions
        assert len(results) == 2
        assert all(result.success for result in results)
        assert sum(result.insertions_made for result in results) == 2
        
        # Both notes should be modified
        ai_content = (temp_vault / "Permanent Notes" / "ai-concepts.md").read_text()
        ml_content = (temp_vault / "Permanent Notes" / "machine-learning-basics.md").read_text()
        assert "[[ML Basics]]" in ai_content
        assert "[[AI Concepts]]" in ml_content
    
    def test_insertion_into_note_without_structure_fails(self, insertion_engine, temp_vault):
        """TEST 8: Handle insertion into notes without predefined sections - WILL FAIL"""
        suggestion = MockSuggestionForInsertion(
            source_note="Fleeting Notes/simple-note.md",
            target_note="Permanent Notes/ai-concepts.md", 
            suggested_link_text="[[AI Concepts]]",
            suggested_location="main_content",  # Will need to create structure
            insertion_context="# Simple Note"
        )
        
        # Act
        result = insertion_engine.insert_suggestions_into_note(
            "Fleeting Notes/simple-note.md",
            [suggestion],
            create_sections=True
        )
        
        # Assert - Should create appropriate section and insert
        assert result.success is True
        assert result.insertions_made == 1
        
        content = (temp_vault / "Fleeting Notes" / "simple-note.md").read_text()
        # Should create a Related section
        assert "## Related" in content or "## See Also" in content
        assert "[[AI Concepts]]" in content
    
    def test_atomic_file_operations_fails(self, insertion_engine, temp_vault):
        """TEST 9: File operations are atomic - either complete success or complete failure - WILL FAIL"""
        suggestions = [
            MockSuggestionForInsertion(  # Valid suggestion
                source_note="Permanent Notes/ai-concepts.md",
                target_note="Permanent Notes/machine-learning-basics.md",
                suggested_link_text="[[ML Basics]]",
                suggested_location="related_concepts",
                insertion_context="## Related Concepts"
            ),
            MockSuggestionForInsertion(  # Invalid suggestion to cause failure
                source_note="Permanent Notes/ai-concepts.md",
                target_note="nonexistent.md",
                suggested_link_text="[[Nonexistent]]", 
                suggested_location="related_concepts",
                insertion_context="## Related Concepts"
            )
        ]
        
        original_content = (temp_vault / "Permanent Notes" / "ai-concepts.md").read_text()
        
        # Act - Should fail atomically
        result = insertion_engine.insert_suggestions_into_note(
            "Permanent Notes/ai-concepts.md",
            suggestions,
            atomic=True,
            validate_targets=True
        )
        
        # Assert - Complete failure with rollback
        assert result.success is False
        assert result.insertions_made == 0
        
        # File should be unchanged (atomic rollback)
        current_content = (temp_vault / "Permanent Notes" / "ai-concepts.md").read_text()
        assert current_content == original_content
    
    def test_insertion_context_detector_integration_fails(self, insertion_engine, temp_vault):
        """TEST 10: Integration with existing InsertionContextDetector for smart placement - WILL FAIL"""
        # Create suggestion without specifying location (should auto-detect)
        suggestion = MockSuggestionForInsertion(
            source_note="Permanent Notes/ai-concepts.md",
            target_note="Permanent Notes/machine-learning-basics.md",
            suggested_link_text="[[Machine Learning Basics]]",
            suggested_location="auto_detect",  # Trigger auto-detection
            insertion_context="auto_detect"
        )
        
        # Act - Should use InsertionContextDetector to find best location
        result = insertion_engine.insert_suggestions_into_note(
            "Permanent Notes/ai-concepts.md",
            [suggestion],
            auto_detect_location=True
        )
        
        # Assert - Should successfully detect and insert in Related Concepts section
        assert result.success is True
        assert result.insertions_made == 1
        assert result.auto_detected_locations == 1
        
        content = (temp_vault / "Permanent Notes" / "ai-concepts.md").read_text()
        assert "[[Machine Learning Basics]]" in content
        
        # Should be inserted in the Related Concepts section
        lines = content.split('\n')
        related_index = next(i for i, line in enumerate(lines) if "## Related Concepts" in line)
        assert any("[[Machine Learning Basics]]" in line for line in lines[related_index:related_index + 5])

class TestInsertionResult:
    """Test InsertionResult dataclass - WILL FAIL"""
    
    def test_insertion_result_structure_fails(self):
        """TEST 11: InsertionResult dataclass has all required fields - WILL FAIL"""
        result = InsertionResult(
            success=True,
            insertions_made=3,
            duplicates_skipped=1,
            backup_path="/path/to/backup.md",
            error_message=None,
            auto_detected_locations=2
        )
        
        assert result.success is True
        assert result.insertions_made == 3
        assert result.duplicates_skipped == 1
        assert result.backup_path == "/path/to/backup.md"
        assert result.error_message is None
        assert result.auto_detected_locations == 2

class TestBackupManager:
    """Test BackupManager utility class - WILL FAIL"""
    
    def test_backup_manager_creation_fails(self):
        """TEST 12: BackupManager creates timestamped backups - WILL FAIL"""
        with tempfile.TemporaryDirectory() as temp_dir:
            vault_path = Path(temp_dir)
            backup_manager = BackupManager(vault_path)
            
            # Create test file
            test_file = vault_path / "test-note.md"
            test_file.write_text("Original content")
            
            # Create backup using correct method name
            backup_path = backup_manager.create_timestamped_backup("test-note.md")
            
            assert backup_path.exists()
            assert backup_path.read_text() == "Original content"
            assert "backup" in backup_path.name.lower()

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
