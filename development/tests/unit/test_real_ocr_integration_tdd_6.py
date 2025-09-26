#!/usr/bin/env python3
"""
TDD Iteration 6 RED Phase: Real OCR Integration Tests

Comprehensive failing tests for real llama_vision_ocr.py integration 
replacing mock OCR content with actual AI vision analysis.

Testing Strategy:
- Real LlamaVisionOCR integration in RichContextAnalyzer
- Actual text extraction from screenshots
- Detailed AI vision descriptions (>100 words)
- Source context analysis with app-specific intelligence
- Enhanced filename generation using real OCR content
- Performance and error handling validation

Following proven TDD patterns from Advanced Tag Enhancement and Smart Link Management.
"""

import unittest
from unittest.mock import Mock, patch, MagicMock
from pathlib import Path
import tempfile
import os
import sys

# Add development directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.ai.llama_vision_ocr import VisionAnalysisResult, LlamaVisionOCR
from src.cli.individual_screenshot_utils import RichContextAnalyzer, ContextualFilenameGenerator


class TestRealOCRIntegration(unittest.TestCase):
    """
    RED Phase tests for real OCR integration in RichContextAnalyzer
    
    These tests MUST FAIL initially since mock OCR is still being used.
    """
    
    def setUp(self):
        """Set up test fixtures"""
        self.analyzer = RichContextAnalyzer()
        self.filename_generator = ContextualFilenameGenerator()
        
        # Create mock screenshot file
        self.temp_dir = tempfile.mkdtemp()
        self.screenshot_path = Path(self.temp_dir) / "Screenshot_20250925_092059_Messenger.jpg"
        self.screenshot_path.touch()
    
    def tearDown(self):
        """Clean up test fixtures"""
        if self.screenshot_path.exists():
            self.screenshot_path.unlink()
        os.rmdir(self.temp_dir)
    
    def test_real_llama_vision_ocr_integration(self):
        """
        Test that RichContextAnalyzer uses real LlamaVisionOCR instead of mock content
        
        MUST FAIL: Current implementation uses mock OCR content
        """
        with patch.object(LlamaVisionOCR, 'analyze_screenshot') as mock_analyze:
            # Real OCR result with actual content
            mock_analyze.return_value = VisionAnalysisResult(
                extracted_text="John: Hey, can we discuss the machine learning project? Sarah: Sure! I found some great resources on neural networks and deep learning.",
                content_summary="Messenger conversation between John and Sarah discussing machine learning project resources, specifically neural networks and deep learning materials.",
                main_topics=["machine learning", "neural networks", "project collaboration"],
                key_insights=["Active project collaboration", "Resource sharing discussion", "Technical topic focus"],
                suggested_connections=["AI Development MOC", "Machine Learning Notes"],
                content_type="messaging_app",
                confidence_score=0.92,
                processing_time=2.3
            )
            
            # Analyze screenshot with real OCR
            result = self.analyzer.analyze_screenshot_with_rich_context(self.screenshot_path)
            
            # Verify real OCR integration - THESE WILL FAIL with mock implementation
            self.assertIn("John: Hey, can we discuss", result['basic_ocr'])
            self.assertIn("Messenger conversation between John and Sarah", result['content_summary'])
            self.assertIn("machine learning", result['key_topics'])
            self.assertIn("Active project collaboration", result['contextual_insights'])
            
            # Verify LlamaVisionOCR was actually called
            mock_analyze.assert_called_once_with(self.screenshot_path)
    
    def test_detailed_ai_vision_description_requirement(self):
        """
        Test that AI vision descriptions are detailed (>100 words) with visual elements
        
        MUST FAIL: Current implementation uses generic mock descriptions
        """
        with patch.object(LlamaVisionOCR, 'analyze_screenshot') as mock_analyze:
            # Detailed AI vision description with visual elements
            detailed_description = """Messenger conversation interface showing a clean, modern chat layout with white background and blue message bubbles. The conversation is between John and Sarah discussing machine learning projects. Visual elements include user profile pictures on the left side of messages, timestamp indicators showing recent activity, and the characteristic Messenger blue color scheme. The interface shows typical mobile messaging app UI components including message bubbles with rounded corners, clear typography for readability, and proper spacing between conversation threads. At the bottom, there's a text input field with placeholder text visible."""
            
            mock_analyze.return_value = VisionAnalysisResult(
                extracted_text="John: Hey Sarah! Sarah: Hi John, what's up?",
                content_summary=detailed_description,  # >100 words with visual elements
                main_topics=["messaging", "conversation", "ui"],
                key_insights=["Mobile interface design", "User conversation flow", "Visual accessibility"],
                suggested_connections=["UI Design MOC", "Conversation Analysis"],
                content_type="messaging_app",
                confidence_score=0.88,
                processing_time=1.9
            )
            
            result = self.analyzer.analyze_screenshot_with_rich_context(self.screenshot_path)
            
            # Verify detailed description requirements - WILL FAIL with current mock
            description = result['content_summary']
            self.assertGreater(len(description), 100, "AI vision description must be >100 words")
            self.assertIn("visual", description.lower(), "Must describe visual elements")
            self.assertIn("interface", description.lower(), "Must describe UI components")
            self.assertIn("color", description.lower(), "Must describe color scheme")
    
    def test_source_context_analysis_with_app_detection(self):
        """
        Test source context analysis with app-specific content understanding
        
        MUST FAIL: Current implementation doesn't analyze app-specific context
        """
        with patch.object(LlamaVisionOCR, 'analyze_screenshot') as mock_analyze:
            mock_analyze.return_value = VisionAnalysisResult(
                extracted_text="Latest thread about AI automation tools...",
                content_summary="Threads social media post discussing AI automation tools and best practices",
                main_topics=["ai automation", "social media", "tools"],
                key_insights=["Social engagement", "Tool recommendations", "Community discussion"],
                suggested_connections=["Social Media Strategy", "AI Tools MOC"],
                content_type="social_media",
                confidence_score=0.85,
                processing_time=2.1
            )
            
            # Test with Threads screenshot
            threads_screenshot = Path(self.temp_dir) / "Screenshot_20250925_143021_Threads.jpg"
            threads_screenshot.touch()
            
            result = self.analyzer.analyze_screenshot_with_rich_context(threads_screenshot)
            
            # Verify app-specific analysis - WILL FAIL without real OCR
            self.assertEqual(result['device_metadata']['app_name'], 'Threads')
            self.assertIn("social media", result['content_summary'].lower())
            self.assertIn("Social engagement", result['contextual_insights'])
            
            threads_screenshot.unlink()
    
    def test_enhanced_filename_generation_with_real_ocr_content(self):
        """
        Test enhanced filename generation using real OCR content keywords
        
        MUST FAIL: Current implementation uses mock content for filename generation
        """
        with patch.object(LlamaVisionOCR, 'analyze_screenshot') as mock_analyze:
            mock_analyze.return_value = VisionAnalysisResult(
                extracted_text="GitHub Repository: Advanced AI Automation Tools for React Native Development",
                content_summary="GitHub repository page showing advanced AI automation tools specifically designed for React Native development workflows",
                main_topics=["github", "ai automation", "react native", "development"],
                key_insights=["Repository discovery", "Development tools", "Automation workflow"],
                suggested_connections=["Development MOC", "AI Tools"],
                content_type="code_repository",
                confidence_score=0.91,
                processing_time=1.8
            )
            
            # Generate filename with real OCR content
            timestamp = "20250925-1430"
            filename = self.filename_generator.generate_contextual_filename(
                self.screenshot_path, 
                mock_analyze.return_value, 
                timestamp
            )
            
            # Verify enhanced filename from real content - WILL FAIL with mock keywords
            self.assertEqual(filename, "capture-20250925-1430-github-ai-automation-tools.md")
            
            # Verify real content was used for generation
            description = self.filename_generator.extract_intelligent_description(
                mock_analyze.return_value.extracted_text,
                mock_analyze.return_value.content_summary
            )
            self.assertIn("github", description)
            self.assertIn("ai", description)
            self.assertIn("automation", description)
    
    def test_ocr_confidence_scoring_and_quality_assessment(self):
        """
        Test OCR confidence scoring and content quality assessment
        
        MUST FAIL: Current implementation doesn't use real OCR confidence scores
        """
        with patch.object(LlamaVisionOCR, 'analyze_screenshot') as mock_analyze:
            # High confidence OCR result
            mock_analyze.return_value = VisionAnalysisResult(
                extracted_text="Clear, readable text from high-quality screenshot",
                content_summary="High-quality screenshot with excellent text clarity",
                main_topics=["quality", "clarity"],
                key_insights=["Excellent OCR conditions", "High readability"],
                suggested_connections=["Quality Assessment"],
                content_type="article",
                confidence_score=0.95,  # High confidence
                processing_time=1.2
            )
            
            result = self.analyzer.analyze_screenshot_with_rich_context(self.screenshot_path)
            
            # Verify confidence scoring integration - WILL FAIL without real OCR
            self.assertIn('ocr_confidence', result)
            self.assertEqual(result['ocr_confidence'], 0.95)
            self.assertIn('quality_assessment', result)
            self.assertEqual(result['quality_assessment'], 'high')
    
    def test_app_specific_conversation_analysis(self):
        """
        Test app-specific conversation analysis for Messenger/Threads content
        
        MUST FAIL: Current implementation doesn't perform conversation-specific analysis
        """
        with patch.object(LlamaVisionOCR, 'analyze_screenshot') as mock_analyze:
            mock_analyze.return_value = VisionAnalysisResult(
                extracted_text="Alice: What do you think about the new AI tools? Bob: They're amazing for productivity! Alice: I agree, especially for content creation.",
                content_summary="Messenger conversation discussing AI tools and productivity benefits",
                main_topics=["ai tools", "productivity", "conversation"],
                key_insights=["Positive sentiment about AI tools", "Focus on productivity gains", "Collaborative discussion"],
                suggested_connections=["AI Tools MOC", "Productivity Notes"],
                content_type="messaging_app",
                confidence_score=0.89,
                processing_time=2.0
            )
            
            result = self.analyzer.analyze_screenshot_with_rich_context(self.screenshot_path)
            
            # Verify conversation-specific analysis - WILL FAIL with generic mock
            self.assertIn('conversation_participants', result)
            self.assertEqual(set(result['conversation_participants']), {'Alice', 'Bob'})
            self.assertIn('conversation_topic', result)
            self.assertEqual(result['conversation_topic'], 'ai tools productivity')
            self.assertIn('sentiment_analysis', result)
            self.assertEqual(result['sentiment_analysis'], 'positive')
    
    def test_error_handling_and_fallback_strategies(self):
        """
        Test comprehensive error handling when OCR processing fails
        
        MUST FAIL: Current implementation doesn't handle real OCR failures
        """
        with patch.object(LlamaVisionOCR, 'analyze_screenshot') as mock_analyze:
            # Simulate OCR failure
            mock_analyze.return_value = None
            
            result = self.analyzer.analyze_screenshot_with_rich_context(self.screenshot_path)
            
            # Verify fallback handling - WILL FAIL without real OCR error handling
            self.assertIn('ocr_status', result)
            self.assertEqual(result['ocr_status'], 'failed')
            self.assertIn('fallback_content', result)
            self.assertIn('Visual content captured but OCR processing failed', result['fallback_content'])
            
            # Verify graceful degradation
            self.assertIsNotNone(result['basic_ocr'])
            self.assertIsNotNone(result['content_summary'])
    
    def test_performance_targets_with_real_ocr_processing(self):
        """
        Test that real OCR processing maintains <30s performance target
        
        MUST FAIL: Current implementation doesn't measure real OCR performance
        """
        with patch.object(LlamaVisionOCR, 'analyze_screenshot') as mock_analyze:
            # Simulate realistic OCR processing time
            mock_analyze.return_value = VisionAnalysisResult(
                extracted_text="Sample text",
                content_summary="Sample summary",
                main_topics=["sample"],
                key_insights=["Sample insight"],
                suggested_connections=["Sample connection"],
                content_type="screenshot",
                confidence_score=0.8,
                processing_time=8.5  # Realistic OCR processing time
            )
            
            import time
            start_time = time.time()
            result = self.analyzer.analyze_screenshot_with_rich_context(self.screenshot_path)
            end_time = time.time()
            
            total_time = end_time - start_time
            
            # Verify performance targets - WILL FAIL without real timing
            self.assertIn('processing_metrics', result)
            self.assertIn('ocr_processing_time', result['processing_metrics'])
            self.assertEqual(result['processing_metrics']['ocr_processing_time'], 8.5)
            self.assertLess(total_time, 30.0, "Total processing must be <30 seconds")


class TestOCRUtilityExtraction(unittest.TestCase):
    """
    RED Phase tests for OCR utility classes that will be extracted in REFACTOR phase
    
    These tests define the modular architecture needed for production OCR integration.
    """
    
    def test_real_ocr_processor_utility_class(self):
        """
        Test RealOCRProcessor utility class for modular OCR integration
        
        Now passes with extracted utility class
        """
        from src.cli.individual_screenshot_utils import RealOCRProcessor
        
        processor = RealOCRProcessor()
        
        # Test with non-existent file (should return None gracefully)
        result = processor.process_screenshot_with_vision(Path("test.jpg"))
        self.assertIsNone(result)  # Expected since file doesn't exist
        
        # Test statistics tracking
        stats = processor.get_processing_statistics()
        self.assertIn('total_processed', stats)
        self.assertIn('success_rate', stats)
        self.assertEqual(stats['total_processed'], 1)
        self.assertEqual(stats['failed'], 1)
    
    def test_content_intelligence_analyzer_utility_class(self):
        """
        Test ContentIntelligenceAnalyzer for app-specific analysis
        
        MUST FAIL: Class doesn't exist yet
        """
        from src.cli.individual_screenshot_utils import ContentIntelligenceAnalyzer
        
        analyzer = ContentIntelligenceAnalyzer()
        intelligence = analyzer.analyze_app_specific_content("messaging_app", "conversation text")
        
        self.assertIn('participants', intelligence)
        self.assertIn('topic', intelligence)
        self.assertIn('sentiment', intelligence)
    
    def test_ocr_performance_optimizer_utility_class(self):
        """
        Test OCRPerformanceOptimizer for caching and optimization
        
        MUST FAIL: Class doesn't exist yet
        """
        from src.cli.individual_screenshot_utils import OCRPerformanceOptimizer
        
        optimizer = OCRPerformanceOptimizer()
        result = optimizer.optimize_ocr_processing(Path("test.jpg"))
        
        self.assertIn('cache_hit', result)
        self.assertIn('processing_time', result)


if __name__ == '__main__':
    unittest.main()
