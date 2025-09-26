#!/usr/bin/env python3
"""
TDD ITERATION 2 REFACTOR: Samsung Screenshot Evening Workflow CLI Utilities

Extracted utility classes following established patterns from:
- Smart Link Management CLI utilities
- Advanced Tag Enhancement CLI utilities  
- Safe Workflow CLI utilities

These classes provide modular architecture for evening screenshot CLI operations
with comprehensive error handling, progress reporting, and configuration management.
"""

import json
import logging
from pathlib import Path
from typing import Dict, Any, Optional, List
from datetime import datetime

from .evening_screenshot_processor import EveningScreenshotProcessor

logger = logging.getLogger(__name__)


class EveningScreenshotCLIOrchestrator:
    """
    Main orchestrator for Samsung Screenshot Evening Workflow CLI operations
    
    Coordinates all CLI functionality including processor initialization,
    execution management, and result formatting.
    """
    
    def __init__(self, knowledge_path: str, onedrive_path: str):
        """Initialize CLI orchestrator with paths"""
        self.knowledge_path = knowledge_path
        self.onedrive_path = onedrive_path
        self.processor = None
        
    def initialize_processor(self) -> bool:
        """
        Initialize EveningScreenshotProcessor with error handling
        
        Returns:
            True if initialization successful, False otherwise
        """
        try:
            self.processor = EveningScreenshotProcessor(
                onedrive_path=self.onedrive_path,
                knowledge_path=self.knowledge_path
            )
            logger.info(f"Initialized processor for {self.knowledge_path}")
            return True
        except Exception as e:
            logger.error(f"Failed to initialize processor: {e}")
            return False
    
    def execute_command(self, command: str, options: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute evening screenshot command with comprehensive error handling
        
        Args:
            command: Command to execute ('dry-run', 'process', 'scan')
            options: Command options and parameters
            
        Returns:
            Execution results with success status and data
        """
        if not self.processor:
            if not self.initialize_processor():
                return {
                    "success": False,
                    "error": "Failed to initialize screenshot processor"
                }
        
        try:
            if command == "dry-run":
                return self._execute_dry_run(options)
            elif command == "process":
                return self._execute_processing(options)
            elif command == "scan":
                return self._execute_scan(options)
            else:
                return {
                    "success": False,
                    "error": f"Unknown command: {command}"
                }
        except Exception as e:
            logger.error(f"Command execution failed: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def _execute_dry_run(self, options: Dict[str, Any]) -> Dict[str, Any]:
        """Execute dry-run command"""
        screenshots = self.processor.scan_todays_screenshots()
        return {
            "success": True,
            "result": {
                "dry_run": True,
                "screenshots_found": len(screenshots),
                "screenshot_paths": [str(p) for p in screenshots],
                "onedrive_path": self.onedrive_path
            }
        }
    
    def _execute_processing(self, options: Dict[str, Any]) -> Dict[str, Any]:
        """Execute main processing command"""
        result = self.processor.process_evening_batch()
        return {
            "success": True,
            "result": result
        }
    
    def _execute_scan(self, options: Dict[str, Any]) -> Dict[str, Any]:
        """Execute screenshot scanning command"""
        screenshots = self.processor.scan_todays_screenshots()
        return {
            "success": True,
            "result": {
                "screenshots": [str(p) for p in screenshots],
                "count": len(screenshots)
            }
        }


class CLIProgressReporter:
    """
    Progress reporting utility for evening screenshot CLI operations
    
    Provides progress indicators, ETA calculations, and performance metrics
    following established CLI patterns.
    """
    
    def __init__(self):
        self.start_time = None
        self.current_step = 0
        self.total_steps = 0
        
    def start_progress(self, total_steps: int, description: str = "Processing"):
        """Start progress tracking"""
        self.start_time = datetime.now()
        self.total_steps = total_steps
        self.current_step = 0
        print(f"🔄 {description} ({total_steps} items)...")
    
    def update_progress(self, step: int, item_description: str = ""):
        """Update progress with current step"""
        self.current_step = step
        if self.total_steps > 0:
            percentage = (step / self.total_steps) * 100
            print(f"   📊 Progress: {step}/{self.total_steps} ({percentage:.1f}%) {item_description}")
    
    def complete_progress(self) -> Dict[str, Any]:
        """Complete progress tracking and return metrics"""
        if self.start_time:
            duration = (datetime.now() - self.start_time).total_seconds()
            return {
                "duration": duration,
                "items_processed": self.current_step,
                "rate": self.current_step / duration if duration > 0 else 0
            }
        return {}
    
    def report_performance_metrics(self, result: Dict[str, Any]) -> None:
        """Report performance metrics following established patterns"""
        processing_time = result.get('processing_time', 0)
        target_met = processing_time < 600  # 10 minutes
        
        print(f"\n📊 Performance Metrics:")
        print(f"   ⏱️ Processing time: {processing_time:.2f}s")
        print(f"   🎯 <10min target met: {'✅' if target_met else '❌'}")
        
        if result.get('processed_count', 0) > 0:
            rate = result['processed_count'] / processing_time if processing_time > 0 else 0
            print(f"   📈 Processing rate: {rate:.2f} screenshots/second")


class ConfigurationManager:
    """
    Configuration management utility for evening screenshot CLI
    
    Handles OneDrive path validation, screenshot limits, quality thresholds,
    and other configuration options.
    """
    
    def __init__(self):
        self.default_onedrive_path = "/Users/thaddius/Library/CloudStorage/OneDrive-Personal/backlog/Pictures/Samsung Galaxy/DCIM/Screenshots/"
        self.max_screenshots_default = 50
        self.quality_threshold_default = 0.5
    
    def validate_onedrive_path(self, path: str) -> Dict[str, Any]:
        """
        Validate OneDrive path exists and is accessible
        
        Returns:
            Validation result with status and details
        """
        path_obj = Path(path)
        
        if not path_obj.exists():
            return {
                "valid": False,
                "error": f"OneDrive path does not exist: {path}",
                "suggestion": f"Check if OneDrive is syncing or use default: {self.default_onedrive_path}"
            }
        
        if not path_obj.is_dir():
            return {
                "valid": False,
                "error": f"OneDrive path is not a directory: {path}",
                "suggestion": "Ensure path points to the Screenshots directory"
            }
        
        # Check for Samsung screenshots
        screenshot_files = list(path_obj.glob("Screenshot_*.jpg"))
        
        return {
            "valid": True,
            "path": str(path_obj),
            "screenshot_count": len(screenshot_files),
            "recent_screenshots": [f.name for f in screenshot_files[-5:]]  # Last 5
        }
    
    def apply_configuration(self, args) -> Dict[str, Any]:
        """
        Apply and validate CLI configuration arguments
        
        Returns:
            Processed configuration with validated values
        """
        config = {
            "onedrive_path": getattr(args, 'onedrive_path', self.default_onedrive_path),
            "max_screenshots": getattr(args, 'max_screenshots', self.max_screenshots_default),
            "quality_threshold": getattr(args, 'quality_threshold', self.quality_threshold_default),
            "dry_run": getattr(args, 'dry_run', False),
            "performance_metrics": getattr(args, 'performance_metrics', False),
            "progress": getattr(args, 'progress', False)
        }
        
        # Validate OneDrive path
        path_validation = self.validate_onedrive_path(config["onedrive_path"])
        config["path_validation"] = path_validation
        
        # Validate numeric thresholds
        if config["max_screenshots"] and config["max_screenshots"] <= 0:
            config["max_screenshots"] = self.max_screenshots_default
            
        if config["quality_threshold"] and (config["quality_threshold"] < 0 or config["quality_threshold"] > 1):
            config["quality_threshold"] = self.quality_threshold_default
        
        return config


class CLIOutputFormatter:
    """
    Output formatting utility for evening screenshot CLI results
    
    Provides consistent formatting for different output modes (text, JSON)
    following established CLI patterns.
    """
    
    def __init__(self, format_type: str = "text"):
        self.format_type = format_type
    
    def format_dry_run_results(self, result: Dict[str, Any]) -> str:
        """Format dry-run results for display"""
        if self.format_type == "json":
            return json.dumps(result, indent=2, default=str)
        
        # Text formatting
        output = []
        output.append("============================================================")
        output.append("  EVENING SCREENSHOTS DRY RUN")
        output.append("============================================================")
        output.append(f"   OneDrive Path: {result.get('onedrive_path', 'Unknown')}")
        output.append(f"   Screenshots Found: {result.get('screenshots_found', 0)}")
        
        # Show first 5 screenshots
        screenshots = result.get('screenshot_paths', [])
        for i, screenshot in enumerate(screenshots[:5], 1):
            path_obj = Path(screenshot)
            output.append(f"   {i}. {path_obj.name}")
        
        if len(screenshots) > 5:
            output.append(f"   ... and {len(screenshots) - 5} more")
        
        return "\n".join(output)
    
    def format_processing_results(self, result: Dict[str, Any]) -> str:
        """Format processing results for display"""
        if self.format_type == "json":
            return json.dumps(result, indent=2, default=str)
        
        # Text formatting
        output = []
        output.append("============================================================")
        output.append("  EVENING SCREENSHOT PROCESSING COMPLETE")
        output.append("============================================================")
        output.append(f"   ✅ Screenshots processed: {result.get('processed_count', 0)}")
        output.append(f"   📝 Daily note created: {result.get('daily_note_path', 'None')}")
        output.append(f"   ⏱️ Processing time: {result.get('processing_time', 0):.2f}s")
        output.append(f"   🔍 OCR results: {result.get('ocr_results', 0)}")
        output.append(f"   🔗 Smart links added: {result.get('suggested_links', 0)}")
        output.append(f"   💾 Backup created: {result.get('backup_path', 'None')}")
        
        return "\n".join(output)
    
    def format_error(self, error: str, suggestions: Optional[List[str]] = None) -> str:
        """Format error messages with suggestions"""
        if self.format_type == "json":
            return json.dumps({
                "error": error,
                "suggestions": suggestions or []
            }, indent=2)
        
        output = [f"❌ Error: {error}"]
        if suggestions:
            output.append("\n💡 Suggestions:")
            for suggestion in suggestions:
                output.append(f"   • {suggestion}")
        
        return "\n".join(output)


class CLIExportManager:
    """
    Export management utility for evening screenshot CLI results
    
    Handles JSON/CSV export functionality with proper file handling
    and error management.
    """
    
    def __init__(self):
        self.supported_formats = ["json", "csv"]
    
    def export_results(self, result: Dict[str, Any], export_path: str, format_type: str = "json") -> bool:
        """
        Export results to file with comprehensive error handling
        
        Returns:
            True if export successful, False otherwise
        """
        try:
            export_file = Path(export_path)
            
            # Ensure directory exists
            export_file.parent.mkdir(parents=True, exist_ok=True)
            
            if format_type == "json":
                with open(export_file, 'w') as f:
                    json.dump(result, f, indent=2, default=str)
            elif format_type == "csv":
                # CSV export for screenshot processing results
                self._export_csv(result, export_file)
            else:
                logger.error(f"Unsupported export format: {format_type}")
                return False
            
            logger.info(f"Results exported to: {export_path}")
            return True
            
        except Exception as e:
            logger.error(f"Export failed: {e}")
            return False
    
    def _export_csv(self, result: Dict[str, Any], export_file: Path) -> None:
        """Export results in CSV format"""
        import csv
        
        with open(export_file, 'w', newline='') as f:
            writer = csv.writer(f)
            
            # Write header
            writer.writerow([
                'timestamp', 'processed_count', 'processing_time', 
                'ocr_results', 'suggested_links', 'daily_note_path'
            ])
            
            # Write data
            writer.writerow([
                datetime.now().isoformat(),
                result.get('processed_count', 0),
                result.get('processing_time', 0),
                result.get('ocr_results', 0),
                result.get('suggested_links', 0),
                result.get('daily_note_path', '')
            ])


# =================================================================
# TDD ITERATION 4: CLI Integration & User Experience Enhancement
# Additional Utility Classes for Advanced CLI Features
# =================================================================

class ConfigurationManager:
    """
    Utility for OneDrive path configuration and validation with user guidance
    
    Provides configuration management with path validation and user-friendly
    error messages for common OneDrive setup issues.
    """
    
    def __init__(self):
        """Initialize configuration manager"""
        self.logger = logging.getLogger(__name__)
    
    def validate_onedrive_path(self, path: str) -> Dict[str, Any]:
        """
        Validate OneDrive path with user guidance
        
        Args:
            path: OneDrive path to validate
            
        Returns:
            Validation result with guidance
        """
        # Placeholder for TDD RED phase - will fail
        raise NotImplementedError("ConfigurationManager.validate_onedrive_path not implemented")
    
    def get_default_samsung_onedrive_paths(self) -> List[str]:
        """Get default Samsung OneDrive paths for auto-detection"""
        raise NotImplementedError("ConfigurationManager.get_default_samsung_onedrive_paths not implemented")
    
    def suggest_onedrive_path_fixes(self, invalid_path: str) -> List[Dict[str, str]]:
        """Suggest fixes for invalid OneDrive paths"""
        raise NotImplementedError("ConfigurationManager.suggest_onedrive_path_fixes not implemented")


class CLIProgressReporter:
    """
    Utility for interactive progress reporting with real-time ETA calculations
    
    Provides progress tracking with ETA calculations within 15% margin of
    actual completion time and real-time status updates.
    """
    
    def __init__(self):
        """Initialize progress reporter"""
        self.logger = logging.getLogger(__name__)
    
    def process_with_progress_reporting(self, screenshots: List[Path], 
                                      progress_callback=None) -> Dict[str, Any]:
        """
        Process with interactive progress reporting
        
        Args:
            screenshots: List of screenshot paths to process
            progress_callback: Function to call with progress updates
            
        Returns:
            Processing results with progress tracking
        """
        # Placeholder for TDD RED phase - will fail
        raise NotImplementedError("CLIProgressReporter.process_with_progress_reporting not implemented")


class ErrorHandlingManager:
    """
    Utility for comprehensive error handling scenarios with user guidance
    
    Handles common error scenarios gracefully with user-friendly error
    messages and specific troubleshooting steps.
    """
    
    def __init__(self):
        """Initialize error handling manager"""
        self.logger = logging.getLogger(__name__)
    
    def handle_onedrive_offline_error(self) -> Dict[str, Any]:
        """Handle OneDrive offline scenario"""
        raise NotImplementedError("ErrorHandlingManager.handle_onedrive_offline_error not implemented")
    
    def handle_ocr_service_unavailable_error(self) -> Dict[str, Any]:
        """Handle OCR service unavailable scenario"""
        raise NotImplementedError("ErrorHandlingManager.handle_ocr_service_unavailable_error not implemented")
    
    def handle_insufficient_disk_space_error(self) -> Dict[str, Any]:
        """Handle insufficient disk space scenario"""
        raise NotImplementedError("ErrorHandlingManager.handle_insufficient_disk_space_error not implemented")
    
    def handle_permission_denied_error(self) -> Dict[str, Any]:
        """Handle permission denied scenario"""
        raise NotImplementedError("ErrorHandlingManager.handle_permission_denied_error not implemented")
    
    def handle_invalid_screenshot_format_error(self) -> Dict[str, Any]:
        """Handle invalid screenshot format scenario"""
        raise NotImplementedError("ErrorHandlingManager.handle_invalid_screenshot_format_error not implemented")


class PerformanceValidator:
    """
    Utility for performance validation with <10 minutes batch processing
    
    Validates real Samsung screenshot batch processing performance and
    provides comprehensive performance breakdown and memory metrics.
    """
    
    def __init__(self):
        """Initialize performance validator"""
        self.logger = logging.getLogger(__name__)
    
    def validate_batch_processing_performance(self, screenshots: List[Path], 
                                            target_time_minutes: int = 10) -> Dict[str, Any]:
        """
        Validate batch processing performance
        
        Args:
            screenshots: List of screenshot paths to process
            target_time_minutes: Target processing time in minutes
            
        Returns:
            Performance validation results
        """
        raise NotImplementedError("PerformanceValidator.validate_batch_processing_performance not implemented")


class AdvancedConfigurationManager:
    """
    Utility for advanced configuration management with persistence
    
    Provides configuration persistence across sessions and automatic
    OneDrive path detection with user preference management.
    """
    
    def __init__(self):
        """Initialize advanced configuration manager"""
        self.logger = logging.getLogger(__name__)
    
    def save_configuration(self, config: Dict[str, Any]) -> bool:
        """Save configuration with persistence"""
        raise NotImplementedError("AdvancedConfigurationManager.save_configuration not implemented")
    
    def load_configuration(self) -> Dict[str, Any]:
        """Load persisted configuration"""
        raise NotImplementedError("AdvancedConfigurationManager.load_configuration not implemented")
    
    def auto_detect_samsung_onedrive_paths(self) -> List[str]:
        """Auto-detect Samsung OneDrive paths"""
        raise NotImplementedError("AdvancedConfigurationManager.auto_detect_samsung_onedrive_paths not implemented")
    
    def calculate_optimal_batch_size(self, total_screenshots: int, 
                                   available_memory_mb: int) -> int:
        """Calculate optimal batch size for performance"""
        raise NotImplementedError("AdvancedConfigurationManager.calculate_optimal_batch_size not implemented")


class ExportManager:
    """
    Utility for export functionality with JSON/CSV automation integration
    
    Generates automation-ready JSON/CSV export formats with complete
    metadata for external processing tools.
    """
    
    def __init__(self):
        """Initialize export manager"""
        self.logger = logging.getLogger(__name__)
    
    def export_to_json(self, processing_results: Dict[str, Any]) -> str:
        """Export processing results to JSON format"""
        raise NotImplementedError("ExportManager.export_to_json not implemented")
    
    def export_to_csv(self, processing_results: Dict[str, Any]) -> str:
        """Export processing results to CSV format"""
        raise NotImplementedError("ExportManager.export_to_csv not implemented")
    
    def export_to_file(self, processing_results: Dict[str, Any], 
                      format: str, output_path: str) -> str:
        """Export processing results to file"""
        raise NotImplementedError("ExportManager.export_to_file not implemented")


class SmartLinkIntegrationManager:
    """
    Utility for Smart Link Management integration with automatic connection discovery
    
    Integrates with existing Smart Link Management system for automatic
    connection discovery and link insertion in generated daily notes.
    """
    
    def __init__(self):
        """Initialize Smart Link integration manager"""
        self.logger = logging.getLogger(__name__)
    
    def discover_connections_from_daily_note(self, daily_note_content: str) -> List[Dict[str, Any]]:
        """Discover connections from daily note content"""
        raise NotImplementedError("SmartLinkIntegrationManager.discover_connections_from_daily_note not implemented")
    
    def auto_insert_smart_links(self, daily_note_path: str, 
                               connections: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Auto-insert smart links into daily note"""
        raise NotImplementedError("SmartLinkIntegrationManager.auto_insert_smart_links not implemented")


class PerformanceOptimizer:
    """
    Utility for performance optimization with memory monitoring
    
    Maintains stable memory usage during processing with <100MB peak memory
    growth and provides performance improvement recommendations.
    """
    
    def __init__(self):
        """Initialize performance optimizer"""
        self.logger = logging.getLogger(__name__)
    
    def process_with_memory_monitoring(self, screenshots: List[Path]) -> Dict[str, Any]:
        """Process with comprehensive memory monitoring"""
        raise NotImplementedError("PerformanceOptimizer.process_with_memory_monitoring not implemented")
    
    def test_concurrent_processing_safety(self, screenshots: List[Path]) -> Dict[str, Any]:
        """Test concurrent processing capabilities"""
        raise NotImplementedError("PerformanceOptimizer.test_concurrent_processing_safety not implemented")
    
    def calculate_optimal_processing_rate(self, screenshot_count: int, 
                                        target_time_minutes: int,
                                        available_memory_mb: int) -> Dict[str, Any]:
        """Calculate optimal processing rate"""
        raise NotImplementedError("PerformanceOptimizer.calculate_optimal_processing_rate not implemented")


class WeeklyReviewIntegrator:
    """
    Utility for weekly review system compatibility integration
    
    Ensures generated daily notes are compatible with existing weekly
    review automation and appear in fleeting note triage workflows.
    """
    
    def __init__(self):
        """Initialize weekly review integrator"""
        self.logger = logging.getLogger(__name__)
    
    def check_weekly_review_compatibility(self, daily_note_metadata: Dict[str, Any]) -> Dict[str, Any]:
        """Check daily note compatibility with weekly review"""
        raise NotImplementedError("WeeklyReviewIntegrator.check_weekly_review_compatibility not implemented")
    
    def check_triage_eligibility(self, daily_note_path: str) -> Dict[str, Any]:
        """Check if daily note is eligible for triage"""
        raise NotImplementedError("WeeklyReviewIntegrator.check_triage_eligibility not implemented")
    
    def analyze_promotion_pathway(self, daily_note_metadata: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze promotion pathway compatibility"""
        raise NotImplementedError("WeeklyReviewIntegrator.analyze_promotion_pathway not implemented")
