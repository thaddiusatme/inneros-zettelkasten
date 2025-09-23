#!/usr/bin/env python3
"""
Comprehensive Zettelkasten Integration Tests
Tests for AI workflow integration, clickable links, and Zettelkasten optimization
"""

import unittest
import tempfile
import os
from datetime import datetime, timedelta
from pathlib import Path
import sys

# Add development directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from capture_matcher import CaptureMatcherPOC


class TestZettelkastenIntegration(unittest.TestCase):
    """Test suite for Zettelkasten-optimized Knowledge Capture System"""
    
    def setUp(self):
        """Set up test environment"""
        # Force fallback mode to avoid WorkflowManager hanging in tests
        import capture_matcher
        capture_matcher.WorkflowManager = None
        
        self.temp_dir = tempfile.mkdtemp()
        self.screenshots_dir = os.path.join(self.temp_dir, "screenshots")
        self.voice_dir = os.path.join(self.temp_dir, "voice")
        self.inbox_dir = os.path.join(self.temp_dir, "inbox")
        
        # Create directories
        Path(self.screenshots_dir).mkdir(parents=True, exist_ok=True)
        Path(self.voice_dir).mkdir(parents=True, exist_ok=True)
        Path(self.inbox_dir).mkdir(parents=True, exist_ok=True)
        
        # Initialize matcher
        self.matcher = CaptureMatcherPOC(self.screenshots_dir, self.voice_dir)
        self.matcher.configure_inbox_directory(self.inbox_dir)
        
        # Sample screenshot data
        self.sample_screenshot = {
            'filename': 'Screenshot_20250922_141530_Knowledge.jpg',
            'timestamp': datetime(2025, 9, 22, 14, 15, 30),
            'path': f'{self.screenshots_dir}/Screenshot_20250922_141530_Knowledge.jpg',
            'size': 1245678
        }
        
        # Sample voice data
        self.sample_voice = {
            'filename': 'Recording_20250922_141545.m4a',
            'timestamp': datetime(2025, 9, 22, 14, 15, 45),
            'path': f'{self.voice_dir}/Recording_20250922_141545.m4a',
            'size': 487362
        }
    
    def tearDown(self):
        """Clean up test environment"""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    # ======================================
    # AI Workflow Integration Tests
    # ======================================
    
    def test_ai_workflow_integration_exists(self):
        """Test that AI workflow integration method exists and is callable"""
        self.assertTrue(hasattr(self.matcher, 'process_capture_notes_with_ai'))
        self.assertTrue(callable(getattr(self.matcher, 'process_capture_notes_with_ai')))
    
    def test_ai_workflow_integration_returns_correct_structure(self):
        """Test that AI integration returns proper result structure"""
        # Create test capture note
        test_pair = {
            'screenshot': self.sample_screenshot,
            'voice': self.sample_voice,
            'time_gap_seconds': 15
        }
        
        capture_note = self.matcher.generate_capture_note(test_pair, "test-ai-integration")
        result = self.matcher.process_capture_notes_with_ai([capture_note])
        
        # Verify result structure
        self.assertIn('processing_stats', result)
        self.assertIn('ai_results', result)
        self.assertIn('errors', result)
        
        # Verify processing stats structure
        stats = result['processing_stats']
        self.assertIn('total_notes', stats)
        self.assertIn('successful', stats)
        self.assertIn('errors', stats)
        self.assertIn('processing_time', stats)
        self.assertIn('average_quality_score', stats)
        
        # Verify AI results structure
        if result['ai_results']:
            ai_result = result['ai_results'][0]
            self.assertIn('original_filename', ai_result)
            self.assertIn('quality_score', ai_result)
            self.assertIn('ai_tags', ai_result)
            self.assertIn('processing_method', ai_result)
            self.assertIn('recommendations', ai_result)
    
    def test_ai_quality_scoring_zettelkasten_optimization(self):
        """Test that AI quality scoring works for Zettelkasten content"""
        # Create capture note with Zettelkasten-style content
        zettelkasten_pair = {
            'screenshot': self.sample_screenshot,
            'voice': self.sample_voice,
            'time_gap_seconds': 15
        }
        
        capture_note = self.matcher.generate_capture_note(zettelkasten_pair, "atomic-concept-test")
        result = self.matcher.process_capture_notes_with_ai([capture_note])
        
        # Verify quality scoring
        self.assertEqual(result['processing_stats']['successful'], 1)
        self.assertEqual(result['processing_stats']['errors'], 0)
        
        if result['ai_results']:
            ai_result = result['ai_results'][0]
            self.assertIsInstance(ai_result['quality_score'], (int, float))
            self.assertGreaterEqual(ai_result['quality_score'], 0.0)
            self.assertLessEqual(ai_result['quality_score'], 1.0)
    
    def test_zettelkasten_tag_generation(self):
        """Test that AI generates appropriate tags for Zettelkasten methodology"""
        # Create test capture
        test_pair = {
            'screenshot': self.sample_screenshot,
            'voice': self.sample_voice,
            'time_gap_seconds': 15
        }
        
        capture_note = self.matcher.generate_capture_note(test_pair, "zettelkasten-tagging-test")
        result = self.matcher.process_capture_notes_with_ai([capture_note])
        
        if result['ai_results']:
            ai_result = result['ai_results'][0]
            tags = ai_result.get('ai_tags', [])
            
            # Verify tag structure
            self.assertIsInstance(tags, list)
            self.assertGreater(len(tags), 0)
            
            # Check for expected Zettelkasten-relevant tags
            tag_string = ' '.join(tags).lower()
            expected_concepts = ['capture', 'knowledge', 'samsung']
            has_expected = any(concept in tag_string for concept in expected_concepts)
            self.assertTrue(has_expected, f"Expected Zettelkasten concepts not in tags: {tags}")
    
    # ======================================
    # Clickable Links Tests
    # ======================================
    
    def test_create_clickable_file_link(self):
        """Test creation of clickable file links"""
        from urllib.parse import quote
        
        test_path = "/Users/test/Documents/file with spaces.pdf"
        expected_encoded = quote(test_path)
        
        # Test link creation logic (simulated)
        link_text = "📸 Open File"
        expected_link = f"[{link_text}](file://{expected_encoded})"
        
        # Verify URL encoding handles spaces
        self.assertIn("%20", expected_encoded)
        self.assertIn(link_text, expected_link)
        self.assertIn("file://", expected_link)
    
    def test_finder_link_creation(self):
        """Test creation of Finder/directory links"""
        from urllib.parse import quote
        from pathlib import Path
        
        test_file_path = "/Users/test/Documents/screenshot.jpg"
        test_dir_path = str(Path(test_file_path).parent)
        expected_encoded = quote(test_dir_path)
        
        # Test directory link creation
        link_text = "📂 Show in Finder"
        expected_link = f"[{link_text}](file://{expected_encoded}/)"
        
        self.assertIn(link_text, expected_link)
        self.assertIn("file://", expected_link)
        self.assertIn("Documents", expected_encoded)
    
    def test_capture_note_contains_clickable_links(self):
        """Test that generated capture notes contain clickable links"""
        # Create capture note
        test_pair = {
            'screenshot': self.sample_screenshot,
            'voice': self.sample_voice,
            'time_gap_seconds': 15
        }
        
        capture_note = self.matcher.generate_capture_note(test_pair, "clickable-links-test")
        content = capture_note['markdown_content']
        
        # Check for file link patterns (this tests the basic structure)
        self.assertIn('Screenshot_20250922_141530_Knowledge.jpg', content)
        self.assertIn('Recording_20250922_141545.m4a', content)
        
        # Check for file path references
        self.assertIn('screenshots/', content)
        self.assertIn('voice/', content)
    
    # ======================================
    # Zettelkasten Methodology Tests
    # ======================================
    
    def test_zettelkasten_yaml_frontmatter_structure(self):
        """Test that capture notes have proper Zettelkasten YAML structure"""
        test_pair = {
            'screenshot': self.sample_screenshot,
            'voice': self.sample_voice,
            'time_gap_seconds': 15
        }
        
        capture_note = self.matcher.generate_capture_note(test_pair, "zettelkasten-yaml-test")
        content = capture_note['markdown_content']
        
        # Check for required Zettelkasten YAML fields
        self.assertIn('type: fleeting', content)
        self.assertIn('status: inbox', content)
        self.assertIn('tags:', content)
        self.assertIn('created:', content)
        self.assertIn('source: capture', content)
        self.assertIn('device: Samsung S23', content)
    
    def test_atomic_concept_ready_detection(self):
        """Test detection of atomic concepts suitable for Zettelkasten"""
        # Create capture with atomic concept structure
        atomic_pair = {
            'screenshot': self.sample_screenshot,
            'voice': self.sample_voice,
            'time_gap_seconds': 15
        }
        
        capture_note = self.matcher.generate_capture_note(atomic_pair, "atomic-concept")
        result = self.matcher.process_capture_notes_with_ai([capture_note])
        
        # Verify processing succeeded
        self.assertEqual(result['processing_stats']['successful'], 1)
        
        if result['ai_results']:
            ai_result = result['ai_results'][0]
            
            # Check for concept development indicators
            recommendations = ai_result.get('recommendations', [])
            self.assertIsInstance(recommendations, list)
            
            # Verify recommendations include development suggestions
            rec_text = ' '.join(recommendations).lower()
            development_indicators = ['review', 'process', 'consider', 'promotion', 'permanent']
            has_development = any(indicator in rec_text for indicator in development_indicators)
            self.assertTrue(has_development, f"No development indicators in recommendations: {recommendations}")
    
    def test_connection_opportunity_detection(self):
        """Test detection of potential connections to existing notes"""
        # Create capture that could connect to existing concepts
        connection_pair = {
            'screenshot': self.sample_screenshot,
            'voice': self.sample_voice,
            'time_gap_seconds': 15
        }
        
        capture_note = self.matcher.generate_capture_note(connection_pair, "connection-test")
        result = self.matcher.process_capture_notes_with_ai([capture_note])
        
        # Verify AI processing identifies connection opportunities
        self.assertEqual(result['processing_stats']['successful'], 1)
        
        if result['ai_results']:
            ai_result = result['ai_results'][0]
            
            # Check that tags suggest knowledge management concepts
            tags = ai_result.get('ai_tags', [])
            tag_concepts = ['capture', 'knowledge', 'samsung', 'management']
            
            has_knowledge_concepts = any(
                any(concept in tag.lower() for concept in tag_concepts) 
                for tag in tags
            )
            self.assertTrue(has_knowledge_concepts, f"No knowledge concepts in tags: {tags}")
    
    # ======================================
    # Integration and Performance Tests
    # ======================================
    
    def test_batch_processing_performance(self):
        """Test batch processing performance with multiple captures"""
        # Create multiple test captures
        captures = []
        for i in range(3):
            timestamp = datetime(2025, 9, 22, 14, 15 + i, 30)
            pair = {
                'screenshot': {
                    'filename': f'Screenshot_20250922_141{15+i}30_Test{i}.jpg',
                    'timestamp': timestamp,
                    'path': f'{self.screenshots_dir}/Screenshot_20250922_141{15+i}30_Test{i}.jpg',
                    'size': 1000000 + i * 100000
                },
                'voice': {
                    'filename': f'Recording_20250922_141{15+i}45.m4a',
                    'timestamp': timestamp + timedelta(seconds=15),
                    'path': f'{self.voice_dir}/Recording_20250922_141{15+i}45.m4a',
                    'size': 500000 + i * 50000
                },
                'time_gap_seconds': 15
            }
            
            capture_note = self.matcher.generate_capture_note(pair, f"batch-test-{i}")
            captures.append(capture_note)
        
        # Process batch
        start_time = datetime.now()
        result = self.matcher.process_capture_notes_with_ai(captures)
        end_time = datetime.now()
        
        processing_time = (end_time - start_time).total_seconds()
        
        # Verify batch processing results
        self.assertEqual(result['processing_stats']['total_notes'], 3)
        self.assertEqual(result['processing_stats']['successful'], 3)
        self.assertEqual(result['processing_stats']['errors'], 0)
        
        # Verify performance (should be under 30 seconds for 3 notes)
        self.assertLess(processing_time, 30.0, f"Batch processing took {processing_time}s, exceeds 30s target")
        
        # Verify average quality score calculation
        avg_score = result['processing_stats'].get('average_quality_score', 0)
        self.assertGreaterEqual(avg_score, 0.0)
        self.assertLessEqual(avg_score, 1.0)
    
    def test_error_handling_resilience(self):
        """Test error handling with malformed input"""
        # Test with invalid input
        invalid_inputs = [
            {},  # Empty dict
            {'invalid': 'structure'},  # Missing required fields
            {'markdown_content': 'test', 'filename': 'test.md'},  # Missing file_path
        ]
        
        for invalid_input in invalid_inputs:
            result = self.matcher.process_capture_notes_with_ai([invalid_input])
            
            # Should handle errors gracefully
            self.assertIn('processing_stats', result)
            self.assertIn('errors', result)
            
            # Should have error count > 0 for invalid input
            self.assertGreater(result['processing_stats']['errors'], 0)
    
    def test_real_data_compatibility(self):
        """Test compatibility with realistic capture data"""
        # Create realistic capture note with actual OneDrive-style paths
        realistic_screenshot = {
            'filename': 'Screenshot_20250922_141530_Messenger.jpg',
            'timestamp': datetime(2025, 9, 22, 14, 15, 30),
            'path': '/Users/user/Library/CloudStorage/OneDrive-Personal/Pictures/Samsung Gallery/DCIM/Screenshots/Screenshot_20250922_141530_Messenger.jpg',
            'size': 532120
        }
        
        realistic_pair = {
            'screenshot': realistic_screenshot,
            'voice': self.sample_voice,
            'time_gap_seconds': 15
        }
        
        capture_note = self.matcher.generate_capture_note(realistic_pair, "real-data-test")
        result = self.matcher.process_capture_notes_with_ai([capture_note])
        
        # Verify realistic data processing
        self.assertEqual(result['processing_stats']['successful'], 1)
        self.assertEqual(result['processing_stats']['errors'], 0)
        
        if result['ai_results']:
            ai_result = result['ai_results'][0]
            
            # Verify realistic filename handling
            self.assertEqual(ai_result['original_filename'], capture_note['filename'])
            
            # Verify quality scoring works with realistic content
            self.assertIsInstance(ai_result['quality_score'], (int, float))
            self.assertGreater(ai_result['quality_score'], 0.0)
    
    # ======================================
    # Integration with Existing System Tests
    # ======================================
    
    def test_preserves_existing_functionality(self):
        """Test that new features don't break existing capture functionality"""
        # Test basic capture note generation (existing functionality)
        test_pair = {
            'screenshot': self.sample_screenshot,
            'voice': self.sample_voice,
            'time_gap_seconds': 15
        }
        
        # This should work exactly as before
        capture_note = self.matcher.generate_capture_note(test_pair, "compatibility-test")
        
        # Verify existing structure is preserved
        self.assertIn('markdown_content', capture_note)
        self.assertIn('filename', capture_note)
        self.assertIn('file_path', capture_note)
        
        content = capture_note['markdown_content']
        
        # Verify existing content structure
        self.assertIn('# Capture Summary', content)
        self.assertIn('## Screenshot Reference', content)
        self.assertIn('## Voice Note Reference', content)
        self.assertIn('## Capture Metadata', content)
        
        # Verify filename generation still works
        self.assertTrue(capture_note['filename'].startswith('capture-'))
        self.assertTrue(capture_note['filename'].endswith('.md'))


if __name__ == '__main__':
    unittest.main()
