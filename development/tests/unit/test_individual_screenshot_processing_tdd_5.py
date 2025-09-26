#!/usr/bin/env python3
"""
TDD Iteration 5: Samsung Screenshot Individual Processing System - RED Phase Tests

Comprehensive failing tests driving individual note generation with rich OCR context.
Following proven TDD patterns from previous Samsung Screenshot iterations.

RED Phase Requirements:
- Individual note generation per screenshot with contextual descriptions
- Rich OCR/vision analysis context with content summaries
- Template-based note structure matching capture-* format
- Smart description generation from OCR content
- Enhanced metadata with device and capture context

Individual Processing Paradigm:
- Transform from daily aggregation to individual capture notes
- Format: capture-YYYYMMDD-HHMM-description.md
- Rich context analysis per screenshot
- Structured template with comprehensive metadata
"""

import unittest
import tempfile
import shutil
from pathlib import Path
from datetime import datetime, date
from unittest.mock import Mock, patch, MagicMock
import sys
import os

# Add development directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.ai.llama_vision_ocr import VisionAnalysisResult
from src.cli.evening_screenshot_processor import EveningScreenshotProcessor


class TestIndividualScreenshotProcessingTDD5(unittest.TestCase):
    """RED Phase: Failing tests for Individual Screenshot Processing System"""
    
    def setUp(self):
        """Set up test environment"""
        self.temp_dir = tempfile.mkdtemp()
        self.knowledge_dir = Path(self.temp_dir) / "knowledge"
        self.knowledge_dir.mkdir(parents=True)
        (self.knowledge_dir / "Inbox").mkdir()
        
        # Mock OneDrive screenshot directory
        self.onedrive_dir = Path(self.temp_dir) / "OneDrive" / "Screenshots"
        self.onedrive_dir.mkdir(parents=True)
        
        # Create sample Samsung screenshots for testing
        self.sample_screenshots = []
        screenshot_names = [
            "Screenshot_20250925_143022_Chrome.jpg",
            "Screenshot_20250925_143045_Obsidian.jpg", 
            "Screenshot_20250925_143118_Twitter.jpg"
        ]
        
        for name in screenshot_names:
            screenshot_path = self.onedrive_dir / name
            screenshot_path.write_text("mock screenshot content")
            self.sample_screenshots.append(screenshot_path)
        
        self.processor = EveningScreenshotProcessor(
            str(self.onedrive_dir), 
            str(self.knowledge_dir)
        )
        
        # Set test-friendly timestamp for consistent testing
        self.processor._test_timestamp = "20250925-1430"
    
    def tearDown(self):
        """Clean up test environment"""
        shutil.rmtree(self.temp_dir)
    
    # =================================================================
    # P0 CRITICAL: Individual Note Generation Tests
    # =================================================================
    
    def test_generate_individual_capture_notes_method_exists(self):
        """Test that generate_individual_capture_notes method exists and is callable"""
        # Should fail - method doesn't exist yet
        self.assertTrue(hasattr(self.processor, 'generate_individual_capture_notes'))
        self.assertTrue(callable(getattr(self.processor, 'generate_individual_capture_notes')))
    
    def test_individual_capture_note_generation_core_functionality(self):
        """Test core individual note generation functionality"""
        # Mock OCR results for individual processing
        mock_ocr_results = {
            str(self.sample_screenshots[0]): VisionAnalysisResult(
                extracted_text="Chrome browser showing AI development article",
                content_summary="Technical article about AI development workflows",
                main_topics=["ai-development", "workflow-automation", "chrome-browser"],
                key_insights=["AI enhances development speed", "Workflow automation is critical"],
                suggested_connections=["AI Development MOC", "Workflow Engineering"],
                content_type="web-article",
                confidence_score=0.92,
                processing_time=1.5
            )
        }
        
        # Should fail - method doesn't exist yet
        result = self.processor.generate_individual_capture_notes(
            screenshots=[self.sample_screenshots[0]],
            ocr_results=mock_ocr_results
        )
        
        # Expected return structure for individual processing
        expected_structure = {
            'individual_notes_created': 1,
            'note_paths': [str],  # List of generated note file paths
            'processing_summary': dict,  # Summary of individual processing
            'description_extraction_success': bool
        }
        
        self.assertIsInstance(result, dict)
        self.assertEqual(result['individual_notes_created'], 1)
        self.assertEqual(len(result['note_paths']), 1)
        # Should contain generated filename based on OCR content
        self.assertIn('capture-20250925-1430-', result['note_paths'][0])
        self.assertIn('.md', result['note_paths'][0])
    
    def test_contextual_filename_generation_from_ocr_content(self):
        """Test intelligent filename generation from OCR content analysis"""
        # Mock OCR result with rich content for description extraction
        mock_ocr_result = VisionAnalysisResult(
            extracted_text="Machine Learning Tutorial - Advanced Neural Networks",
            content_summary="Comprehensive tutorial covering deep learning architectures",
            main_topics=["machine-learning", "neural-networks", "tutorial"],
            key_insights=["Advanced architectures improve accuracy"],
            suggested_connections=["ML MOC"],
            content_type="tutorial",
            confidence_score=0.95,
            processing_time=2.1
        )
        
        # Should fail - method doesn't exist yet
        filename = self.processor.generate_contextual_filename(
            screenshot_path=self.sample_screenshots[0],
            ocr_result=mock_ocr_result,
            timestamp="20250925-1430"
        )
        
        # Expected format: capture-YYYYMMDD-HHMM-description.md
        expected_pattern = "capture-20250925-1430-machine-learning-neural-networks.md"
        self.assertEqual(filename, expected_pattern)
    
    def test_rich_ocr_context_analysis_structure(self):
        """Test rich OCR analysis with content summaries and contextual descriptions"""
        # Should fail - method doesn't exist yet
        rich_context = self.processor.analyze_screenshot_with_rich_context(
            screenshot_path=self.sample_screenshots[0]
        )
        
        # Expected rich context structure
        expected_keys = [
            'basic_ocr',           # Standard OCR text extraction
            'content_summary',     # AI-generated content summary
            'key_topics',         # Extracted main topics
            'contextual_insights', # Key insights and takeaways
            'description_keywords',# Keywords for filename generation
            'device_metadata',    # Samsung S23 device detection
            'capture_context'     # Timestamp, app, session info
        ]
        
        for key in expected_keys:
            self.assertIn(key, rich_context)
        
        # Validate rich content structure
        self.assertIsInstance(rich_context['content_summary'], str)
        self.assertIsInstance(rich_context['key_topics'], list)
        self.assertIsInstance(rich_context['contextual_insights'], list)
        self.assertIsInstance(rich_context['description_keywords'], list)
        self.assertIn('device_type', rich_context['device_metadata'])
        self.assertEqual(rich_context['device_metadata']['device_type'], 'Samsung Galaxy S23')
    
    def test_template_based_individual_note_structure(self):
        """Test structured template for individual screenshot notes"""
        mock_rich_context = {
            'basic_ocr': 'Sample OCR text from screenshot',
            'content_summary': 'AI-generated summary of screenshot content',
            'key_topics': ['topic1', 'topic2'],
            'contextual_insights': ['insight1', 'insight2'],
            'description_keywords': ['keyword1', 'keyword2'],
            'device_metadata': {'device_type': 'Samsung Galaxy S23', 'app_name': 'Chrome'},
            'capture_context': {'timestamp': '2025-09-25 14:30', 'session_id': 'evening_batch_001'}
        }
        
        # Should fail - method doesn't exist yet
        note_content = self.processor.generate_template_based_note_content(
            screenshot_path=self.sample_screenshots[0],
            rich_context=mock_rich_context,
            filename="capture-20250925-1430-sample-content.md"
        )
        
        # Validate template structure matches capture-* format standards
        expected_sections = [
            "# ",  # Title with contextual description
            "## Screenshot Reference",
            "## Capture Metadata", 
            "## AI Vision Analysis",
            "## Key Topics",
            "---",  # YAML frontmatter
            "type: fleeting",
            "status: inbox",
            "created: 2025-09-25 14:30",
            "tags: [screenshot, visual-capture",
            "device_type: Samsung Galaxy S23"
        ]
        
        for section in expected_sections:
            self.assertIn(section, note_content)
    
    # =================================================================  
    # P1 ENHANCED: Smart Description Generation Tests
    # =================================================================
    
    def test_intelligent_description_extraction_from_content(self):
        """Test smart description generation from OCR content analysis"""
        test_cases = [
            {
                'ocr_text': 'GitHub Repository: Advanced AI Automation Tools',
                'content_summary': 'Open source repository for AI automation',
                'expected_description': 'github-ai-automation-tools'
            },
            {
                'ocr_text': 'Tutorial: React Native Development Best Practices',
                'content_summary': 'Development tutorial for mobile applications',
                'expected_description': 'react-native-development-tutorial'
            },
            {
                'ocr_text': 'Email Dashboard - Inbox Management System',
                'content_summary': 'Email application interface screenshot',
                'expected_description': 'email-dashboard-inbox-management'
            }
        ]
        
        for case in test_cases:
            # Should fail - method doesn't exist yet
            description = self.processor.extract_intelligent_description(
                ocr_text=case['ocr_text'],
                content_summary=case['content_summary']
            )
            
            self.assertEqual(description, case['expected_description'])
    
    def test_fallback_description_strategies(self):
        """Test fallback naming strategies for unclear content"""
        # Test app-based fallback
        app_fallback = self.processor.generate_fallback_description(
            screenshot_path=Path("Screenshot_20250925_143022_Chrome.jpg"),
            strategy="app-based"
        )
        self.assertEqual(app_fallback, "chrome-screenshot")
        
        # Test timestamp-based fallback
        timestamp_fallback = self.processor.generate_fallback_description(
            screenshot_path=Path("Screenshot_20250925_143022_Chrome.jpg"),
            strategy="timestamp-based"
        )
        self.assertEqual(timestamp_fallback, "screenshot-20250925-1430")
        
        # Test generic fallback
        generic_fallback = self.processor.generate_fallback_description(
            screenshot_path=Path("Screenshot_20250925_143022_Chrome.jpg"),
            strategy="generic"
        )
        self.assertEqual(generic_fallback, "visual-capture")
    
    def test_smart_link_integration_for_individual_notes(self):
        """Test Smart Link system integration for individual capture notes"""
        mock_note_path = self.knowledge_dir / "Inbox" / "capture-20250925-1430-ai-development.md"
        mock_note_path.write_text("""---
type: fleeting
status: inbox
created: 2025-09-25 14:30
tags: [screenshot, ai-development, visual-capture]
---

# AI Development Article Screenshot

## AI Vision Analysis
OCR extracted content about machine learning workflows...
""")
        
        # Should fail - enhanced method doesn't exist yet
        link_suggestions = self.processor.suggest_smart_links_for_individual_note(
            note_path=mock_note_path
        )
        
        # Expected link suggestions for individual notes
        expected_suggestions = [
            {'target': 'AI Development MOC', 'reason': 'Content relates to AI development workflows'},
            {'target': 'Machine Learning Notes', 'reason': 'ML topic keywords detected'},
            {'target': 'Visual Knowledge MOC', 'reason': 'Screenshot-based knowledge capture'}
        ]
        
        self.assertIsInstance(link_suggestions, list)
        self.assertGreaterEqual(len(link_suggestions), 2)
        for suggestion in link_suggestions:
            self.assertIn('target', suggestion)
            self.assertIn('reason', suggestion)
    
    # =================================================================
    # P1 ENHANCED: Batch Processing Optimization Tests  
    # =================================================================
    
    def test_optimized_individual_processing_pipeline(self):
        """Test optimized batch processing for individual file generation"""
        # Should fail - optimized method doesn't exist yet
        batch_result = self.processor.process_screenshots_individually_optimized(
            screenshots=self.sample_screenshots
        )
        
        # Expected optimization results
        expected_structure = {
            'total_processed': 3,
            'individual_notes_created': 3,
            'processing_time_per_screenshot': float,  # Average processing time
            'parallel_processing_used': bool,
            'optimization_metrics': {
                'description_generation_time': float,
                'template_rendering_time': float,
                'file_io_time': float
            }
        }
        
        self.assertIsInstance(batch_result, dict)
        self.assertEqual(batch_result['total_processed'], 3)
        self.assertEqual(batch_result['individual_notes_created'], 3)
        self.assertIn('optimization_metrics', batch_result)
    
    def test_enhanced_progress_reporting_individual_creation(self):
        """Test enhanced progress reporting for individual note creation"""
        progress_updates = []
        
        def capture_progress(stage, current, total, eta, details=None):
            progress_updates.append({
                'stage': stage,
                'current': current,
                'total': total,
                'eta': eta,
                'details': details
            })
        
        # Should fail - enhanced progress method doesn't exist yet
        result = self.processor.process_with_individual_progress_reporting(
            screenshots=self.sample_screenshots,
            progress_callback=capture_progress
        )
        
        # Validate progress reporting stages for individual processing
        expected_stages = [
            'initialization',
            'rich_context_analysis',
            'description_generation', 
            'template_rendering',
            'note_creation',
            'smart_link_integration',
            'completion'
        ]
        
        reported_stages = [update['stage'] for update in progress_updates]
        for stage in expected_stages:
            self.assertIn(stage, reported_stages)
    
    def test_individual_screenshot_error_handling_recovery(self):
        """Test error handling and recovery for individual screenshot failures"""
        # Create scenarios with processing failures
        problematic_screenshots = self.sample_screenshots + [
            Path("corrupted_screenshot.jpg"),  # File doesn't exist
            Path("invalid_format.txt")         # Wrong format
        ]
        
        # Should fail - enhanced error handling doesn't exist yet  
        recovery_result = self.processor.process_individual_with_error_recovery(
            screenshots=problematic_screenshots
        )
        
        # Expected error recovery structure
        expected_recovery = {
            'successful_individual_notes': 3,  # Original 3 screenshots
            'failed_screenshots': 2,          # 2 problematic files
            'error_details': [
                {'file': 'corrupted_screenshot.jpg', 'error': 'File not found'},
                {'file': 'invalid_format.txt', 'error': 'Unsupported format'}
            ],
            'recovery_actions_taken': [
                'Skipped corrupted files',
                'Continued processing remaining screenshots', 
                'Generated individual notes for successful items'
            ],
            'continuation_successful': True
        }
        
        self.assertEqual(recovery_result['successful_individual_notes'], 3)
        self.assertEqual(recovery_result['failed_screenshots'], 2) 
        self.assertTrue(recovery_result['continuation_successful'])


if __name__ == '__main__':
    unittest.main()
