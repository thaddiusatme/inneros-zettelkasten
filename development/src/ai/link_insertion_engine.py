#!/usr/bin/env python3
"""
Link Insertion Engine - TDD Iteration 4 (REFACTOR Phase)
Production-ready link insertion with modular utility architecture
"""

from pathlib import Path
from typing import List, Optional, Callable, Any

from .link_insertion_utils import (
    InsertionResult,
    SafetyBackupManager,
    SmartInsertionProcessor, 
    ContentValidator,
    BatchInsertionOrchestrator,
    LocationDetectionEnhancer
)

class LinkInsertionEngine:
    """
    Engine for safely inserting link suggestions into actual note files
    with comprehensive backup and rollback capabilities
    """
    
    def __init__(self, vault_path: str, backup_enabled: bool = True):
        """Initialize LinkInsertionEngine with modular utility architecture"""
        self.vault_path = str(vault_path)  # Keep as string for test compatibility
        self._vault_path_obj = Path(vault_path)
        self.backup_enabled = backup_enabled
        
        # Initialize modular utilities
        self.backup_manager = SafetyBackupManager(self._vault_path_obj)
        self.content_validator = ContentValidator(self._vault_path_obj)
        self.insertion_processor = SmartInsertionProcessor()
        self.location_enhancer = LocationDetectionEnhancer()
        self.batch_orchestrator = BatchInsertionOrchestrator()
        
        # Legacy compatibility
        self.insertion_validator = self._create_validator()
    
    def _create_validator(self):
        """Create insertion validator - compatibility wrapper"""
        return lambda x: self.content_validator.validate_markdown_structure(str(x))
    
    def insert_suggestions_into_note(self, note_path: str, suggestions: List[Any], 
                                   validate_targets: bool = False,
                                   check_duplicates: bool = False,
                                   atomic: bool = False,
                                   auto_detect_location: bool = False,
                                   create_sections: bool = False) -> InsertionResult:
        """
        Insert link suggestions into a note file with safety checks
        
        Args:
            note_path: Path to note file relative to vault
            suggestions: List of LinkSuggestion objects
            validate_targets: Check if target notes exist
            check_duplicates: Skip duplicate links
            atomic: All-or-nothing insertion
            auto_detect_location: Use InsertionContextDetector for placement
            create_sections: Create sections if they don't exist
            
        Returns:
            InsertionResult with operation details
        """
        full_path = self._vault_path_obj / note_path
        if not full_path.exists():
            return InsertionResult(
                success=False,
                insertions_made=0,
                error_message=f"Note not found: {note_path}"
            )
        
        # Create backup if enabled
        backup_path = None
        if self.backup_enabled:
            try:
                backup_path = self.backup_manager.create_timestamped_backup(note_path)
            except Exception as e:
                return InsertionResult(
                    success=False,
                    insertions_made=0,
                    error_message=f"Backup creation failed: {str(e)}"
                )
        
        try:
            original_content = full_path.read_text()
            content = original_content
            insertions_made = 0
            duplicates_skipped = 0
            auto_detected_locations = 0
            
            for suggestion in suggestions:
                # Validate target if requested
                if validate_targets:
                    if not self.content_validator.validate_target_exists(suggestion.target_note):
                        # For any validation failure, rollback and fail 
                        if backup_path:
                            self.backup_manager.restore_from_backup(backup_path, note_path)
                        return InsertionResult(
                            success=False,
                            insertions_made=0,
                            error_message="rollback: target validation failed"
                        )
                
                # Check for duplicates
                if check_duplicates and self.content_validator.check_duplicate_link(content, suggestion.suggested_link_text):
                    duplicates_skipped += 1
                    continue
                
                # Auto-detect location if requested
                if auto_detect_location:
                    suggested_location, insertion_context = self.location_enhancer.auto_detect_insertion_location(
                        content, suggestion
                    )
                    if suggestion.suggested_location == "auto_detect":
                        auto_detected_locations += 1
                else:
                    suggested_location = suggestion.suggested_location
                    insertion_context = suggestion.insertion_context
                
                # Insert the link using utility
                new_content = self.insertion_processor.insert_at_location(
                    content, suggestion.suggested_link_text, 
                    suggested_location, insertion_context, create_sections
                )
                
                if new_content != content:  # Content was modified
                    content = new_content
                    insertions_made += 1
            
            # Write modified content back to file
            if insertions_made > 0:
                full_path.write_text(content)
            
            return InsertionResult(
                success=True,
                insertions_made=insertions_made,
                duplicates_skipped=duplicates_skipped,
                backup_path=str(backup_path) if backup_path else None,
                auto_detected_locations=auto_detected_locations
            )
            
        except Exception as e:
            # Rollback on any error
            if backup_path and full_path.exists():
                self.backup_manager.restore_from_backup(backup_path, note_path)
            
            return InsertionResult(
                success=False,
                insertions_made=0,
                error_message=f"Insertion failed: {str(e)}"
            )
    
    def insert_multiple_suggestions(self, suggestions: List[Any], 
                                  progress_callback: Optional[Callable] = None) -> List[InsertionResult]:
        """
        Insert suggestions into multiple notes with progress tracking using batch orchestrator
        
        Args:
            suggestions: List of suggestions with source_note paths
            progress_callback: Optional callback for progress updates
            
        Returns:
            List of InsertionResult objects
        """
        # Use batch orchestrator for efficient processing
        suggestions_by_note = self.batch_orchestrator.group_suggestions_by_note(suggestions)
        
        # Execute batch insertion with progress tracking
        return self.batch_orchestrator.execute_with_progress(
            suggestions_by_note,
            self.insert_suggestions_into_note,
            progress_callback
        )
