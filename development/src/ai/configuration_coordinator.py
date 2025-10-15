"""
ConfigurationCoordinator - ADR-002 Phase 12a

Extracts configuration and initialization logic from WorkflowManager.
Responsible for:
- Vault directory path setup and validation
- AI component initialization (tagger, summarizer, enhancer, etc.)
- All coordinator initialization (Phases 1-11)
- Configuration file loading and management
- Legacy compatibility (active_sessions)

Target: Extract ~149 LOC from WorkflowManager (__init__ and _load_config)
"""
import json
from pathlib import Path
from typing import Dict, Optional

# AI components
from src.ai.tagger import AITagger
from src.ai.summarizer import AISummarizer
from src.ai.connections import AIConnections
from src.ai.enhancer import AIEnhancer
from src.ai.analytics import NoteAnalytics

# Safe image processing components (actually exist)
from src.ai.safe_image_processor import SafeImageProcessor
from src.ai.image_integrity_monitor import ImageIntegrityMonitor
from src.ai.workflow_integration_utils import (
    SafeWorkflowProcessor,
    AtomicWorkflowEngine,
    IntegrityMonitoringManager,
    ConcurrentSessionManager,
    PerformanceMetricsCollector
)


class ConfigurationCoordinator:
    """
    Coordinates configuration and initialization for WorkflowManager.
    
    ADR-002 Phase 12a: Extracts configuration management to reduce WorkflowManager complexity.
    """
    
    def __init__(self, base_directory: str | None = None, workflow_manager: Optional[object] = None):
        """
        Initialize configuration coordinator.
        
        Args:
            base_directory: Explicit path to the Zettelkasten root. If None, resolves from config.
            workflow_manager: Optional reference to WorkflowManager for circular dependency resolution.
        """
        # Resolve base directory
        if base_directory is None:
            from src.utils.vault_path import get_default_vault_path
            resolved = get_default_vault_path()
            if resolved is None:
                raise ValueError(
                    "No vault path supplied and none could be resolved via "
                    "INNEROS_VAULT_PATH or .inneros.* config files."
                )
            self.base_dir = Path(resolved)
        else:
            self.base_dir = Path(base_directory).expanduser()
        
        # Define workflow directories
        self.inbox_dir = self.base_dir / "Inbox"
        self.fleeting_dir = self.base_dir / "Fleeting Notes"
        self.literature_dir = self.base_dir / "Literature Notes"
        self.permanent_dir = self.base_dir / "Permanent Notes"
        self.archive_dir = self.base_dir / "Archive"
        
        # Initialize AI components
        self.tagger = AITagger()
        self.summarizer = AISummarizer()
        self.connections = AIConnections()  # Legacy support
        self.enhancer = AIEnhancer()
        self.analytics = NoteAnalytics(str(self.base_dir))
        
        # Initialize image safety components
        self.safe_image_processor = SafeImageProcessor(str(self.base_dir))
        self.image_integrity_monitor = ImageIntegrityMonitor(str(self.base_dir))
        
        # Initialize extracted utility classes for modular architecture
        self.safe_workflow_processor = SafeWorkflowProcessor(
            self.safe_image_processor, 
            self.image_integrity_monitor
        )
        self.atomic_workflow_engine = AtomicWorkflowEngine(self.safe_image_processor)
        self.integrity_monitoring_manager = IntegrityMonitoringManager(
            self.image_integrity_monitor, 
            self.safe_image_processor
        )
        self.concurrent_session_manager = ConcurrentSessionManager(self.safe_workflow_processor)
        self.performance_metrics_collector = PerformanceMetricsCollector(self.safe_image_processor)
        
        # Store reference to workflow_manager for future coordinator initialization
        self._workflow_manager = workflow_manager
        
        # Placeholder for coordinators that will be created by WorkflowManager
        # These will be set after WorkflowManager creates them
        self.lifecycle_manager = None
        self.connection_coordinator = None
        self.analytics_coordinator = None
        self.promotion_engine = None
        self.review_triage_coordinator = None
        self.note_processing_coordinator = None
        self.safe_image_processing_coordinator = None
        self.orphan_remediation_coordinator = None
        self.fleeting_analysis_coordinator = None
        self.reporting_coordinator = None
        self.batch_processing_coordinator = None
        
        # Session management for concurrent processing (legacy compatibility)
        self.active_sessions = {}
        
        # Load workflow configuration
        self.config = self._load_config()
        self.config_file_path = self.base_dir / ".ai_workflow_config.json"
    
    def _load_config(self) -> Dict:
        """
        Load workflow configuration from file or return defaults.
        
        Returns:
            Dict with configuration settings (merged defaults + user config)
        """
        config_file = self.base_dir / ".ai_workflow_config.json"
        
        default_config = {
            "auto_tag_inbox": True,
            "auto_summarize_long_notes": True,
            "auto_enhance_permanent_notes": False,
            "min_words_for_summary": 500,
            "max_tags_per_note": 8,
            "similarity_threshold": 0.7,
            "archive_after_days": 90
        }
        
        if config_file.exists():
            try:
                with open(config_file, 'r') as f:
                    user_config = json.load(f)
                default_config.update(user_config)
            except Exception:
                # Silently fall back to defaults on any error
                pass
        
        return default_config
    
    def get_config(self) -> Dict:
        """
        Get current configuration.
        
        Returns:
            Dict with configuration settings
        """
        return self.config
    
    def get_directory_paths(self) -> Dict[str, Path]:
        """
        Get all workflow directory paths.
        
        Returns:
            Dict mapping directory names to Path objects
        """
        return {
            "inbox": self.inbox_dir,
            "fleeting": self.fleeting_dir,
            "literature": self.literature_dir,
            "permanent": self.permanent_dir,
            "archive": self.archive_dir
        }
    
    def reload_config(self) -> None:
        """
        Reload configuration from file.
        
        Useful when configuration file has been modified externally.
        """
        self.config = self._load_config()
    
    def set_coordinator(self, name: str, coordinator: object) -> None:
        """
        Set a coordinator instance after it's been created.
        
        Args:
            name: Name of the coordinator attribute (e.g., 'lifecycle_manager')
            coordinator: The coordinator instance to set
        """
        setattr(self, name, coordinator)
