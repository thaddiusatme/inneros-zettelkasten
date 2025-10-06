"""
LegacyWorkflowManagerAdapter - Backward-compatible bridge to refactored architecture.

This adapter wraps the 4 refactored managers (Core, Analytics, AI, Connection) and
exposes the same public API as the old WorkflowManager god class. Enables zero-breaking-
change integration while maintaining full backward compatibility with existing code.

Design Pattern: Adapter Pattern
- Wraps: CoreWorkflowManager, AnalyticsManager, AIEnhancementManager, ConnectionManager
- Exposes: Original WorkflowManager public API (26 methods)
- Maintains: Exact same return types and behaviors
- Handles: Parameter differences transparently

Week 4 P0.2: Simple Delegations (5 methods)
- detect_orphaned_notes() → AnalyticsManager
- detect_stale_notes() → AnalyticsManager  
- generate_workflow_report() → AnalyticsManager
- scan_review_candidates() → AnalyticsManager
- process_inbox_note() → CoreWorkflowManager (drops 'fast' parameter)
"""

from pathlib import Path
from typing import Dict, Any, List, Optional

from src.ai.types import WorkflowResult, AnalyticsResult, ReviewCandidate, WorkflowReport
from src.ai.core_workflow_manager import CoreWorkflowManager
from src.ai.analytics_manager import AnalyticsManager
from src.ai.ai_enhancement_manager import AIEnhancementManager
from src.ai.connection_manager import ConnectionManager
from src.utils.vault_path import get_default_vault_path


class LegacyWorkflowManagerAdapter:
    """
    Backward-compatible adapter for old WorkflowManager API.
    
    Wraps 4 refactored managers and delegates method calls while maintaining
    exact same public API as original WorkflowManager. Enables gradual migration
    from god class to clean architecture without breaking existing code.
    
    Architecture:
        Old: WorkflowManager (2,374 LOC god class)
        New: 4 focused managers with clear separation of concerns
        Bridge: This adapter (delegation pattern)
    
    Example:
        # Drop-in replacement for old WorkflowManager
        workflow = LegacyWorkflowManagerAdapter(base_directory="/path/to/vault")
        
        # All old methods work identically
        orphans = workflow.detect_orphaned_notes()
        report = workflow.generate_workflow_report()
        result = workflow.process_inbox_note("Inbox/test.md")
    """
    
    def __init__(self, base_directory: str | None = None) -> None:
        """
        Initialize adapter with 4 refactored managers.
        
        Args:
            base_directory: Explicit path to Zettelkasten root. If None,
                resolves via INNEROS_VAULT_PATH or .inneros config files.
        
        Raises:
            ValueError: If base_directory is None and no vault path can be resolved.
        """
        # Resolve vault path (maintains old WorkflowManager behavior)
        if base_directory is None:
            resolved = get_default_vault_path()
            if resolved is None:
                raise ValueError(
                    "No vault path supplied and none could be resolved via "
                    "INNEROS_VAULT_PATH or .inneros.* config files."
                )
            self.base_dir = resolved
        else:
            self.base_dir = Path(base_directory).expanduser()
        
        # Define workflow directories (legacy compatibility)
        self.inbox_dir = self.base_dir / "Inbox"
        self.fleeting_dir = self.base_dir / "Fleeting Notes"
        self.permanent_dir = self.base_dir / "Permanent Notes"
        self.archive_dir = self.base_dir / "Archive"
        
        # Load configuration (centralized for all managers)
        self.config = self._load_config()
        
        # Initialize 4 refactored managers
        self.analytics = AnalyticsManager(self.base_dir, self.config)
        self.ai_enhancement = AIEnhancementManager(self.base_dir, self.config)
        self.connections = ConnectionManager(self.base_dir, self.config)
        
        # CoreWorkflowManager requires manager dependencies
        self.core = CoreWorkflowManager(
            base_dir=self.base_dir,
            config=self.config,
            analytics_manager=self.analytics,
            ai_enhancement_manager=self.ai_enhancement,
            connection_manager=self.connections
        )
    
    def _load_config(self) -> Dict[str, Any]:
        """
        Load workflow configuration from file or use defaults.
        
        Maintains backward compatibility with old WorkflowManager config format.
        """
        config_file = self.base_dir / ".ai_workflow_config.json"
        
        default_config = {
            # Old WorkflowManager config keys
            "auto_tag_inbox": True,
            "auto_summarize_long_notes": True,
            "auto_enhance_permanent_notes": False,
            "min_words_for_summary": 500,
            "max_tags_per_note": 8,
            "similarity_threshold": 0.7,
            "archive_after_days": 90,
            
            # New manager config keys
            "quality_threshold": 0.7,
            "stale_days_threshold": 90,
            "min_quality_for_promotion": 0.7
        }
        
        if config_file.exists():
            try:
                import json
                with open(config_file, 'r') as f:
                    user_config = json.load(f)
                default_config.update(user_config)
            except Exception:
                pass  # Use defaults on error
        
        return default_config
    
    # =========================================================================
    # Analytics Delegations (Pure passthrough - no transformation needed)
    # =========================================================================
    
    def detect_orphaned_notes(self) -> List[Dict[str, Any]]:
        """
        Detect notes with no incoming or outgoing links.
        
        Delegates to: AnalyticsManager.detect_orphaned_notes()
        
        Returns:
            List of orphaned notes with metadata:
            [{
                'note': str (filename),
                'title': str,
                'incoming_links': int (always 0),
                'outgoing_links': int (always 0)
            }]
        """
        return self.analytics.detect_orphaned_notes()
    
    def detect_stale_notes(self, days_threshold: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        Detect notes not modified within threshold period.
        
        Delegates to: AnalyticsManager.detect_stale_notes()
        
        Args:
            days_threshold: Days since modification (default: None, uses config default)
        
        Returns:
            List of stale notes sorted by staleness (oldest first):
            [{
                'note': str (filename),
                'title': str,
                'last_modified': datetime,
                'days_since_modified': int
            }]
        """
        return self.analytics.detect_stale_notes(days_threshold=days_threshold)
    
    def generate_workflow_report(self) -> Dict[str, Any]:
        """
        Generate aggregated workflow metrics across the vault.
        
        Delegates to: AnalyticsManager.generate_workflow_report()
        
        Returns:
            Dict with comprehensive workflow statistics:
            {
                'total_notes': int,
                'by_type': {'permanent': int, 'fleeting': int, 'literature': int},
                'by_status': {'inbox': int, 'draft': int, 'published': int},
                'quality_distribution': {'>0.7': int, '0.4-0.7': int, '<0.4': int},
                'orphaned_count': int,
                'stale_count': int
            }
        """
        return self.analytics.generate_workflow_report()
    
    def scan_review_candidates(self) -> List[Dict[str, Any]]:
        """
        Identify high-quality fleeting notes ready for promotion.
        
        Delegates to: AnalyticsManager.scan_review_candidates()
        
        Returns:
            List of promotion candidates:
            [{
                'note': str (path),
                'quality_score': float (0-1),
                'rationale': str (promotion reason),
                'metadata': dict
            }]
        """
        return self.analytics.scan_review_candidates()
    
    # =========================================================================
    # Core Workflow Delegation (Parameter transformation: drop 'fast')
    # =========================================================================
    
    def process_inbox_note(
        self,
        note_path: str,
        dry_run: bool = False,
        fast: bool | None = None
    ) -> Dict[str, Any]:
        """
        Process a note in the inbox with AI assistance.
        
        Delegates to: CoreWorkflowManager.process_inbox_note()
        
        Note: The 'fast' parameter from old WorkflowManager is dropped.
        New architecture handles performance optimization internally.
        
        Args:
            note_path: Path to the note in inbox
            dry_run: If True, do not write any changes to disk
            fast: (DEPRECATED) Ignored for backward compatibility
        
        Returns:
            Processing results and recommendations:
            {
                'original_file': str,
                'processing': {
                    'quality': dict,
                    'ai_tags': list,
                    'summary': str (optional)
                },
                'recommendations': [
                    {
                        'action': str (promote_to_permanent|move_to_fleeting|improve_or_archive),
                        'reason': str,
                        'confidence': str (high|medium|low)
                    }
                ],
                'quality_score': float (0-1)
            }
        """
        # Drop 'fast' parameter - new architecture doesn't use it
        # CoreWorkflowManager handles optimization internally
        return self.core.process_inbox_note(note_path, dry_run=dry_run)


# Export for backward compatibility
__all__ = ['LegacyWorkflowManagerAdapter']
