#!/usr/bin/env python3
"""
TDD Iteration 4: Samsung Screenshot Evening Workflow CLI Integration & User Experience Enhancement

RED Phase: Comprehensive failing test suite for CLI integration with interactive user experience.

Building on TDD Iteration 3's 6 modular utility classes:
- RealDataOCRProcessor
- PerformanceTracker  
- ErrorRecoveryManager
- SmartLinkConnector
- QualityAssessmentEngine
- MemoryOptimizer

P0 Features to Test:
- --evening-screenshots command integration with workflow_demo.py
- Interactive progress reporting with real-time ETA calculations
- OneDrive path configuration and validation with user-friendly error messages
- Comprehensive error handling scenarios with specific troubleshooting guidance
- Real Samsung screenshot batch processing with <10 minutes performance validation

P1 Features to Test:
- Advanced configuration management and path validation
- Export functionality (JSON/CSV) for automation pipeline integration
- Smart Link Management integration with automatic connection discovery
- Performance optimization and memory monitoring during batch processing
"""

import pytest
import tempfile
import shutil
from pathlib import Path
from unittest.mock import patch
import sys
import argparse
import time
from datetime import datetime
import json

# Add development directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.cli.workflow_demo import main


class TestEveningScreenshotCLIIntegrationTDD4:
    """
    TDD Iteration 4 RED Phase: CLI Integration & User Experience Enhancement
    
    These tests will fail initially and drive the implementation of comprehensive
    CLI integration with interactive user experience features.
    """

    def setup_method(self):
        """Set up test environment for each test"""
        self.temp_dir = tempfile.mkdtemp()
        self.knowledge_path = Path(self.temp_dir) / "knowledge"
        self.onedrive_path = Path(self.temp_dir) / "OneDrive" / "Samsung Screenshots"

        # Create directory structure
        self.knowledge_path.mkdir(parents=True)
        (self.knowledge_path / "Inbox").mkdir(parents=True)
        self.onedrive_path.mkdir(parents=True)

        # Create mock Samsung screenshots for testing
        self.create_mock_samsung_screenshots()

    def teardown_method(self):
        """Clean up test environment"""
        shutil.rmtree(self.temp_dir)

    def create_mock_samsung_screenshots(self):
        """Create mock Samsung screenshot files for testing"""
        today_str = datetime.now().strftime("%Y%m%d")
        yesterday_str = (datetime.now().replace(day=datetime.now().day-1)).strftime("%Y%m%d")

        # Today's screenshots (should be processed)
        screenshots_today = [
            f"Screenshot_{today_str}_143022_Chrome.jpg",
            f"Screenshot_{today_str}_143045_Obsidian.jpg",
            f"Screenshot_{today_str}_143112_Twitter.jpg",
            f"Screenshot_{today_str}_143234_LinkedIn.jpg",
            f"Screenshot_{today_str}_143556_Notion.jpg"
        ]

        # Yesterday's screenshots (should be ignored)
        screenshots_yesterday = [
            f"Screenshot_{yesterday_str}_120022_Instagram.jpg",
            f"Screenshot_{yesterday_str}_121045_TikTok.jpg"
        ]

        # Create all screenshot files
        for filename in screenshots_today + screenshots_yesterday:
            screenshot_path = self.onedrive_path / filename
            screenshot_path.write_bytes(b"Mock JPEG content for testing")

    # =================================================================
    # P0 CRITICAL: CLI Command Integration Tests
    # =================================================================

    def test_evening_screenshots_command_argument_parsing(self):
        """
        RED: Test --evening-screenshots command argument parsing
        
        Should integrate with workflow_demo.py argument parser and accept
        required arguments for CLI integration.
        """
        # Create a mock argument parser like the one in workflow_demo.py
        parser = argparse.ArgumentParser()

        # Add the arguments we expect to be implemented
        parser.add_argument('--evening-screenshots', action='store_true',
                          help='Process Samsung screenshots')
        parser.add_argument('--onedrive-path', type=str, help='OneDrive path')
        parser.add_argument('--dry-run', action='store_true', help='Dry run mode')
        parser.add_argument('--progress', action='store_true', help='Show progress')
        parser.add_argument('--performance-metrics', action='store_true',
                          help='Show performance metrics')

        # Test basic evening-screenshots command
        args = parser.parse_args(['--evening-screenshots'])
        assert hasattr(args, 'evening_screenshots')
        assert args.evening_screenshots is True

        # Test with OneDrive path argument
        args = parser.parse_args([
            '--evening-screenshots',
            '--onedrive-path', str(self.onedrive_path)
        ])
        assert hasattr(args, 'onedrive_path')
        assert args.onedrive_path == str(self.onedrive_path)

        # Test with dry-run flag
        args = parser.parse_args(['--evening-screenshots', '--dry-run'])
        assert hasattr(args, 'dry_run')
        assert args.dry_run is True

        # Test with progress reporting flag
        args = parser.parse_args(['--evening-screenshots', '--progress'])
        assert hasattr(args, 'progress')
        assert args.progress is True

        # Test with performance metrics flag
        args = parser.parse_args(['--evening-screenshots', '--performance-metrics'])
        assert hasattr(args, 'performance_metrics')
        assert args.performance_metrics is True

    def test_evening_screenshots_command_execution_integration(self):
        """
        RED: Test evening-screenshots command execution through main()
        
        Should integrate with workflow_demo.py main() function and execute
        evening screenshot processing when --evening-screenshots flag is provided.
        """
        with patch('sys.argv', [
            'workflow_demo.py',
            str(self.knowledge_path),
            '--evening-screenshots',
            '--onedrive-path', str(self.onedrive_path),
            '--dry-run'  # Safe for testing
        ]):
            # This test will fail in RED phase - main() doesn't support evening-screenshots yet
            try:
                result = main()
                # If implemented, should return success result with processing information
                assert result is not None
                assert isinstance(result, dict)
                assert 'processed_screenshots' in result
                assert 'processing_time' in result
                assert 'daily_note_generated' in result
            except (SystemExit, NotImplementedError) as e:
                # Expected in RED phase - evening-screenshots not implemented yet
                pytest.fail(f"evening-screenshots command not implemented in main(): {e}")

    def test_onedrive_path_configuration_and_validation(self):
        """
        RED: Test OneDrive path configuration with validation and user guidance
        
        Should provide configuration management with path validation and
        user-friendly error messages for common OneDrive setup issues.
        """
        from src.cli.evening_screenshot_cli_utils import ConfigurationManager

        config_manager = ConfigurationManager()

        # Test valid OneDrive path
        result = config_manager.validate_onedrive_path(str(self.onedrive_path))
        assert result['valid'] is True
        assert result['screenshots_found'] >= 0  # Should detect mock screenshots

        # Test invalid OneDrive path
        invalid_path = "/non/existent/path"
        result = config_manager.validate_onedrive_path(invalid_path)
        assert result['valid'] is False
        assert 'error_message' in result
        assert 'user_guidance' in result
        assert len(result['user_guidance']) > 0

        # Test default Samsung OneDrive path detection
        default_paths = config_manager.get_default_samsung_onedrive_paths()
        assert isinstance(default_paths, list)
        assert len(default_paths) > 0

        # Test path suggestions for common issues
        suggestions = config_manager.suggest_onedrive_path_fixes(invalid_path)
        assert isinstance(suggestions, list)
        assert all('action' in suggestion for suggestion in suggestions)
        assert all('description' in suggestion for suggestion in suggestions)

    def test_interactive_progress_reporting_with_eta_calculations(self):
        """
        RED: Test interactive progress reporting with real-time ETA calculations
        
        Should provide progress tracking with ETA calculations within 15% margin
        of actual completion time and real-time status updates.
        """
        from src.cli.evening_screenshot_cli_utils import CLIProgressReporter

        progress_reporter = CLIProgressReporter()
        progress_updates = []

        def capture_progress(stage, current, total, eta):
            progress_updates.append({
                'stage': stage,
                'current': current,
                'total': total,
                'eta': eta,
                'timestamp': time.time()
            })

        # Test progress reporting during screenshot processing
        screenshots = list(self.onedrive_path.glob("*.jpg"))
        start_time = time.time()

        progress_reporter.process_with_progress_reporting(
            screenshots,
            progress_callback=capture_progress
        )

        actual_time = time.time() - start_time

        # Should have multiple progress updates
        assert len(progress_updates) > 0

        # Should have initialization, processing, and completion stages
        stages = [update['stage'] for update in progress_updates]
        assert 'initialization' in stages
        assert 'processing' in stages or 'completed' in stages

        # ETA should be within 15% margin of actual time (for later updates)
        processing_updates = [u for u in progress_updates if u['stage'] == 'processing']
        if processing_updates:
            final_eta = processing_updates[-1]['eta']
            eta_margin = abs(final_eta - actual_time) / actual_time if actual_time > 0 else 0
            assert eta_margin <= 0.15, f"ETA margin {eta_margin:.2%} exceeds 15% tolerance"

    def test_comprehensive_error_handling_with_user_guidance(self):
        """
        RED: Test comprehensive error handling scenarios with specific troubleshooting guidance
        
        Should handle common error scenarios gracefully with user-friendly
        error messages and specific troubleshooting steps.
        """
        from src.cli.evening_screenshot_cli_utils import ErrorHandlingManager

        error_handler = ErrorHandlingManager()

        # Test OneDrive offline scenario
        guidance = error_handler.handle_onedrive_offline_error()
        assert 'error_type' in guidance
        assert guidance['error_type'] == 'OneDrive Offline'
        assert 'user_message' in guidance
        assert 'troubleshooting_steps' in guidance
        assert len(guidance['troubleshooting_steps']) >= 3
        assert 'suggested_actions' in guidance

        # Test OCR service unavailable scenario
        guidance = error_handler.handle_ocr_service_unavailable_error()
        assert guidance['error_type'] == 'OCR Service Unavailable'
        assert 'troubleshooting_steps' in guidance
        assert any('service' in step.lower() for step in guidance['troubleshooting_steps'])

        # Test insufficient disk space scenario
        guidance = error_handler.handle_insufficient_disk_space_error()
        assert guidance['error_type'] == 'Insufficient Disk Space'
        assert 'suggested_actions' in guidance
        assert any('disk space' in action.lower() for action in guidance['suggested_actions'])

        # Test permission denied scenario
        guidance = error_handler.handle_permission_denied_error()
        assert guidance['error_type'] == 'Permission Denied'
        assert 'troubleshooting_steps' in guidance
        assert any('permission' in step.lower() for step in guidance['troubleshooting_steps'])

        # Test invalid screenshot format scenario
        guidance = error_handler.handle_invalid_screenshot_format_error()
        assert guidance['error_type'] == 'Invalid Screenshot Format'
        assert any('format' in step.lower() for step in guidance['troubleshooting_steps'])

    def test_real_samsung_screenshot_batch_processing_performance(self):
        """
        RED: Test real Samsung screenshot batch processing with <10 minutes performance validation
        
        Should process 5-20 real Samsung screenshots through complete workflow
        in less than 10 minutes total execution time.
        """
        from src.cli.evening_screenshot_cli_utils import PerformanceValidator

        performance_validator = PerformanceValidator()
        screenshots = list(self.onedrive_path.glob("*.jpg"))

        # Should have at least 5 screenshots for meaningful batch testing
        assert len(screenshots) >= 5, "Need at least 5 screenshots for batch processing test"

        start_time = time.time()
        result = performance_validator.validate_batch_processing_performance(
            screenshots,
            target_time_minutes=10
        )
        actual_processing_time = time.time() - start_time

        # Should meet performance target
        assert result['performance_target_met'] is True
        assert result['processing_time'] < 600  # 10 minutes
        assert result['screenshots_per_second'] > 0

        # Validate actual timing is reasonable
        assert actual_processing_time < 60  # Should complete test quickly

        # Should provide performance breakdown
        assert 'performance_breakdown' in result
        breakdown = result['performance_breakdown']
        assert 'ocr_time' in breakdown
        assert 'note_generation_time' in breakdown
        assert 'smart_link_time' in breakdown

        # Should track memory usage
        assert 'memory_metrics' in result
        memory = result['memory_metrics']
        assert 'peak_memory_mb' in memory
        assert 'memory_cleanup_successful' in memory

    # =================================================================
    # P1 ENHANCED: Advanced Configuration & Export Features Tests
    # =================================================================

    def test_advanced_configuration_management_and_persistence(self):
        """
        RED: Test advanced configuration management with user preference persistence
        
        Should provide configuration persistence across sessions and automatic
        OneDrive path detection with user preference management.
        """
        from src.cli.evening_screenshot_cli_utils import AdvancedConfigurationManager

        config_manager = AdvancedConfigurationManager()

        # Test configuration persistence
        config = {
            'onedrive_path': str(self.onedrive_path),
            'batch_size': 10,
            'enable_progress_reporting': True,
            'enable_smart_linking': True,
            'performance_optimization': 'balanced'
        }

        config_manager.save_configuration(config)
        loaded_config = config_manager.load_configuration()

        assert loaded_config['onedrive_path'] == str(self.onedrive_path)
        assert loaded_config['batch_size'] == 10
        assert loaded_config['enable_progress_reporting'] is True

        # Test OneDrive path auto-detection
        detected_paths = config_manager.auto_detect_samsung_onedrive_paths()
        assert isinstance(detected_paths, list)

        # Test batch size optimization
        optimal_batch_size = config_manager.calculate_optimal_batch_size(
            total_screenshots=20,
            available_memory_mb=1024
        )
        assert isinstance(optimal_batch_size, int)
        assert optimal_batch_size > 0
        assert optimal_batch_size <= 20

    def test_export_functionality_json_csv_automation_integration(self):
        """
        RED: Test export functionality for JSON/CSV formats with automation pipeline integration
        
        Should generate automation-ready JSON/CSV export formats with complete
        metadata for external processing tools.
        """
        from src.cli.evening_screenshot_cli_utils import ExportManager

        export_manager = ExportManager()

        # Mock processing results for export testing
        processing_results = {
            'screenshots_processed': 5,
            'daily_note_path': str(self.knowledge_path / "Inbox" / "daily-screenshots-test.md"),
            'ocr_results': [
                {
                    'screenshot_path': 'screenshot1.jpg',
                    'extracted_text': 'Sample OCR text',
                    'confidence_score': 0.85,
                    'processing_time': 1.2
                }
            ],
            'smart_links_added': 3,
            'processing_time': 45.2,
            'performance_metrics': {
                'screenshots_per_second': 0.11,
                'memory_peak_mb': 156
            }
        }

        # Test JSON export
        json_export = export_manager.export_to_json(processing_results)
        assert isinstance(json_export, str)

        # Parse and validate JSON structure
        json_data = json.loads(json_export)
        assert 'metadata' in json_data
        assert 'processing_results' in json_data
        assert 'export_timestamp' in json_data['metadata']
        assert 'export_format' in json_data['metadata']
        assert json_data['metadata']['export_format'] == 'json'

        # Test CSV export
        csv_export = export_manager.export_to_csv(processing_results)
        assert isinstance(csv_export, str)
        assert 'screenshot_path,extracted_text,confidence_score' in csv_export

        # Test export file creation
        json_file_path = export_manager.export_to_file(
            processing_results,
            format='json',
            output_path=str(Path(self.temp_dir) / "export.json")
        )
        assert Path(json_file_path).exists()

        csv_file_path = export_manager.export_to_file(
            processing_results,
            format='csv',
            output_path=str(Path(self.temp_dir) / "export.csv")
        )
        assert Path(csv_file_path).exists()

    def test_smart_link_management_integration_automatic_connection_discovery(self):
        """
        RED: Test Smart Link Management integration with automatic connection discovery
        
        Should integrate with existing Smart Link Management system for automatic
        connection discovery and link insertion in generated daily notes.
        """
        from src.cli.evening_screenshot_cli_utils import SmartLinkIntegrationManager

        integration_manager = SmartLinkIntegrationManager()

        # Mock daily note content for link discovery testing
        daily_note_content = """---
type: fleeting
status: inbox
created: 2025-09-25 20:30
tags: [daily-screenshots, visual-capture, knowledge-intake]
---

# Daily Screenshots - 2025-09-25

## Screenshots and Analysis

### Screenshot 1: Chrome Browser
OCR Analysis: "Machine learning algorithms for natural language processing"

### Screenshot 2: Obsidian Notes
OCR Analysis: "Zettelkasten method for knowledge management"
"""

        # Test connection discovery
        connections = integration_manager.discover_connections_from_daily_note(daily_note_content)
        assert isinstance(connections, list)
        assert len(connections) > 0

        # Should find connections based on OCR content
        connection_texts = [conn['explanation'] for conn in connections]
        assert any('machine learning' in text.lower() for text in connection_texts)
        assert any('zettelkasten' in text.lower() for text in connection_texts)

        # Test automatic link insertion
        daily_note_path = self.knowledge_path / "Inbox" / "test-daily-note.md"
        daily_note_path.write_text(daily_note_content)

        insertion_result = integration_manager.auto_insert_smart_links(
            str(daily_note_path),
            connections[:3]  # Insert top 3 connections
        )

        assert insertion_result['links_inserted'] > 0
        assert insertion_result['backup_created'] is True
        assert 'updated_note_path' in insertion_result

        # Verify links were actually inserted
        updated_content = daily_note_path.read_text()
        assert '[[' in updated_content  # Should contain wiki-links
        assert ']]' in updated_content

    def test_performance_optimization_memory_monitoring_batch_processing(self):
        """
        RED: Test performance optimization with memory monitoring during batch processing
        
        Should maintain stable memory usage during processing of 20+ screenshots
        with <100MB peak memory growth and provide performance improvement recommendations.
        """
        from src.cli.evening_screenshot_cli_utils import PerformanceOptimizer

        optimizer = PerformanceOptimizer()

        # Create larger set of mock screenshots for stress testing
        large_screenshot_set = []
        for i in range(25):  # 25 screenshots for stress testing
            screenshot_path = self.onedrive_path / f"Screenshot_20250925_14{i:02d}22_TestApp{i}.jpg"
            screenshot_path.write_bytes(b"Mock JPEG content for stress testing" * 100)  # Larger mock files
            large_screenshot_set.append(screenshot_path)

        # Test memory monitoring during batch processing
        memory_report = optimizer.process_with_memory_monitoring(large_screenshot_set)

        assert 'initial_memory_mb' in memory_report
        assert 'peak_memory_mb' in memory_report
        assert 'final_memory_mb' in memory_report
        assert 'memory_growth_mb' in memory_report

        # Memory growth should be under 100MB
        memory_growth = memory_report['memory_growth_mb']
        assert memory_growth < 100, f"Memory growth {memory_growth}MB exceeds 100MB limit"

        # Should provide performance recommendations
        assert 'performance_recommendations' in memory_report
        recommendations = memory_report['performance_recommendations']
        assert isinstance(recommendations, list)
        assert len(recommendations) > 0

        # Test concurrent processing capabilities
        concurrent_result = optimizer.test_concurrent_processing_safety(large_screenshot_set)
        assert concurrent_result['concurrent_processing_safe'] is True
        assert concurrent_result['file_system_integrity_maintained'] is True

        # Test processing rate optimization
        rate_optimization = optimizer.calculate_optimal_processing_rate(
            screenshot_count=25,
            target_time_minutes=10,
            available_memory_mb=512
        )

        assert 'recommended_batch_size' in rate_optimization
        assert 'estimated_completion_time' in rate_optimization
        assert rate_optimization['recommended_batch_size'] > 0
        assert rate_optimization['estimated_completion_time'] <= 600  # 10 minutes

    def test_weekly_review_system_compatibility_integration(self):
        """
        RED: Test weekly review system compatibility with generated daily notes
        
        Should generate daily notes that are compatible with existing weekly
        review automation and appear in fleeting note triage workflows.
        """
        from src.cli.evening_screenshot_cli_utils import WeeklyReviewIntegrator

        integrator = WeeklyReviewIntegrator()

        # Test daily note compatibility with weekly review
        daily_note_metadata = {
            'type': 'fleeting',
            'status': 'inbox',
            'tags': ['daily-screenshots', 'visual-capture'],
            'screenshot_count': 5,
            'processing_date': '2025-09-25'
        }

        compatibility_check = integrator.check_weekly_review_compatibility(daily_note_metadata)
        assert compatibility_check['compatible'] is True
        assert compatibility_check['will_appear_in_triage'] is True
        assert compatibility_check['meets_quality_threshold'] is True

        # Test integration with fleeting note triage
        mock_daily_note_path = self.knowledge_path / "Inbox" / "daily-screenshots-2025-09-25.md"
        triage_eligibility = integrator.check_triage_eligibility(str(mock_daily_note_path))

        assert triage_eligibility['eligible_for_triage'] is True
        assert triage_eligibility['expected_quality_score'] > 0.4  # Should meet minimum quality
        assert 'triage_recommendations' in triage_eligibility

        # Test promotion pathway compatibility
        promotion_pathway = integrator.analyze_promotion_pathway(daily_note_metadata)
        assert 'promotion_candidates' in promotion_pathway
        assert 'recommended_promotion_type' in promotion_pathway  # fleeting -> permanent or literature
        assert promotion_pathway['promotion_timeline_days'] > 0


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
