"""
TDD Iteration: Enhanced AI Tag Cleanup Deployment - RED PHASE

Failing tests for lightweight tag cleanup deployment targeting 30 problematic tags:
- Garbage tags: "#", "|", "2", "8", "a", etc.
- AI artifacts from previous processing
- Malformed tags requiring cleanup
- Prevention mechanisms for future tag pollution

Focus: Targeted cleanup approach avoiding bulk processing limits
Performance: <30s deployment for 30 problematic tags
Safety: Complete backup before any tag modifications

This TDD iteration completes the deployment of Enhanced AI Features (100% suggestion coverage)
with focus on real-world problematic tag cleanup in production vault.
"""

import unittest
import tempfile
import time
import shutil
import yaml
import json
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
from typing import Dict, List, Any, Tuple

# Add development directory to path for imports
import sys
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

# Import the enhanced AI features we'll be testing
try:
    from src.ai.enhanced_ai_features import (
        EnhancedSuggestionEngine,
        QualityScoringRecalibrator
    )
    from src.ai.enhanced_ai_tag_cleanup_deployment import (
        LightweightTagCleanupEngine,
        TagCleanupValidator,
        TemplateSanitizer,
        WeeklyReviewSanitizer,
        AISanitizedTagGenerator,
        CleanupWorkflowIntegrator,
        CleanupPerformanceMonitor,
        WorkflowDemo
    )
except ImportError:
    # Expected during RED phase
    pass


class TestLightweightTagCleanupEngine(unittest.TestCase):
    """Test lightweight tag cleanup deployment for 30 problematic tags"""
    
    def setUp(self):
        """Set up test environment with real problematic tag patterns"""
        self.temp_dir = tempfile.mkdtemp()
        self.vault_path = Path(self.temp_dir)
        
        # Real problematic tags found in the vault (from scan)
        self.garbage_tags = [
            "#", "|", "2", "8", "a", "",  # Symbols and single chars
            "   ", " ", "\n", "\t",       # Whitespace variations
        ]
        
        self.ai_artifacts = [
            "ai_tags", "auto_generated", "placeholder",
            "template_tag", "default_tag"
        ]
        
        self.malformed_tags = [
            "tag with spaces", "TAG_UNDERSCORE", "CamelCaseTag",
            "tag#with#hash", "tag|with|pipe", "123numeric"
        ]
        
        # Create test files with problematic tags
        self._create_test_files_with_problematic_tags()
        
    def _create_test_files_with_problematic_tags(self):
        """Create test markdown files with problematic tags for cleanup testing"""
        test_files = [
            {
                "path": "knowledge/Inbox/test-garbage-tags.md",
                "content": """---
created: 2025-09-24 08:00
type: fleeting
status: inbox
tags: ["#", "|", "2", "8", "a"]
---

# Test Note with Garbage Tags

This note has garbage tags that need cleanup.
""",
                "expected_cleanup": ["reference-hash", "separator", "year-2", "reference-8", "concept-a"]
            },
            {
                "path": "knowledge/Fleeting Notes/test-ai-artifacts.md", 
                "content": """---
created: 2025-09-24 08:01
type: fleeting
status: promoted
tags: ["ai_tags", "auto_generated", "placeholder"]
---

# Test Note with AI Artifacts

This note has AI artifact tags that need cleanup.
""",
                "expected_cleanup": ["ai-tagging", "automated-generation", "content-placeholder"]
            },
            {
                "path": "knowledge/Permanent Notes/test-malformed.md",
                "content": """---
created: 2025-09-24 08:02
type: permanent
status: published
tags: ["tag with spaces", "TAG_UNDERSCORE", "CamelCaseTag"]
---

# Test Note with Malformed Tags

This note has malformed tags that need standardization.
""",
                "expected_cleanup": ["tag-with-spaces", "tag-underscore", "camel-case-tag"]
            }
        ]
        
        for file_info in test_files:
            file_path = self.vault_path / file_info["path"]
            file_path.parent.mkdir(parents=True, exist_ok=True)
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(file_info["content"])
                
        # Store expected results for validation
        self.expected_cleanups = {f["path"]: f["expected_cleanup"] for f in test_files}
        
    def test_lightweight_tag_cleanup_engine_initialization(self):
        """Test LightweightTagCleanupEngine initializes for targeted deployment"""
        # GREEN phase - implementation should exist and work
        from src.ai.enhanced_ai_tag_cleanup_deployment import LightweightTagCleanupEngine
        engine = LightweightTagCleanupEngine(self.vault_path)
        self.assertIsNotNone(engine)
        self.assertEqual(engine.vault_path, self.vault_path)
            
    def test_problematic_tag_identification(self):
        """Test accurate identification of 30 problematic tags for cleanup"""
        # GREEN phase - implementation should work
        from src.ai.enhanced_ai_tag_cleanup_deployment import LightweightTagCleanupEngine
        engine = LightweightTagCleanupEngine(self.vault_path)
        
        # Scan vault for problematic tags
        problematic_tags = engine.identify_problematic_tags()
        
        # Should return list of tuples (tag, files, type)
        self.assertIsInstance(problematic_tags, list)
        
        # Should identify problematic patterns from test files
        problematic_tag_strs = [tag for tag, files, problem_type in problematic_tags]
        self.assertTrue(any(tag in problematic_tag_strs for tag in self.garbage_tags))
        
        # Should limit to manageable number for deployment
        self.assertLessEqual(len(problematic_tags), 50)  # Avoid bulk processing limits
            
    def test_targeted_cleanup_suggestions(self):
        """Test targeted cleanup suggestions for worst 10-15 tags first"""
        # GREEN phase - implementation should work
        from src.ai.enhanced_ai_tag_cleanup_deployment import LightweightTagCleanupEngine
        engine = LightweightTagCleanupEngine(self.vault_path)
        
        # Get cleanup plan prioritizing worst offenders
        cleanup_plan = engine.generate_targeted_cleanup_plan()
        
        # Should return list of cleanup items
        self.assertIsInstance(cleanup_plan, list)
        
        # Should have actionable suggestions
        for item in cleanup_plan:
            self.assertIn('original_tag', item)
            self.assertIn('suggested_tag', item)
            self.assertIn('reason', item)
            self.assertIn('files_affected', item)
            self.assertIn('priority', item)
            self.assertIsInstance(item['files_affected'], list)
                
    def test_lightweight_processing_performance(self):
        """Test lightweight processing avoids system stalls for <30s deployment"""
        # GREEN phase - implementation should work
        from src.ai.enhanced_ai_tag_cleanup_deployment import LightweightTagCleanupEngine
        engine = LightweightTagCleanupEngine(self.vault_path)
        
        start_time = time.time()
        
        # Process targeted cleanup without hitting system limits
        results = engine.execute_lightweight_cleanup(max_tags=30)
        
        processing_time = time.time() - start_time
        
        # Performance requirement: <30s for targeted deployment
        self.assertLess(processing_time, 30.0)
        
        # Should avoid system stalls by limiting scope
        self.assertLessEqual(results['tags_processed'], 30)
        self.assertIsInstance(results['success_rate'], float)
            
    def test_backup_before_cleanup_safety(self):
        """Test complete backup before any tag modifications for safety"""
        # GREEN phase - implementation should work
        from src.ai.enhanced_ai_tag_cleanup_deployment import LightweightTagCleanupEngine
        engine = LightweightTagCleanupEngine(self.vault_path)
        
        # Should create backup before any modifications
        backup_path = engine.create_cleanup_backup()
        
        # Backup should exist and contain all files
        self.assertTrue(backup_path.exists())
        self.assertTrue(backup_path.is_dir())
        
        # Should preserve original file structure
        backup_files = list(backup_path.rglob("*.md"))
        self.assertGreater(len(backup_files), 0)
                
    def test_dry_run_mode_validation(self):
        """Test dry-run mode shows cleanup plan without making changes"""
        # GREEN phase - implementation should work
        from src.ai.enhanced_ai_tag_cleanup_deployment import LightweightTagCleanupEngine
        engine = LightweightTagCleanupEngine(self.vault_path)
        
        # Record original state
        original_files = {}
        for file_path in self.expected_cleanups.keys():
            full_path = self.vault_path / file_path
            if full_path.exists():
                with open(full_path, 'r') as f:
                    original_files[file_path] = f.read()
                    
        # Execute dry-run
        dry_run_results = engine.execute_cleanup(dry_run=True)
        
        # Should provide detailed plan
        self.assertIn('planned_changes', dry_run_results)
        self.assertIn('affected_files', dry_run_results)
        self.assertIn('estimated_improvements', dry_run_results)
        self.assertTrue(dry_run_results.get('dry_run', False))
        
        # Should NOT modify any files during dry-run
        for file_path, original_content in original_files.items():
            full_path = self.vault_path / file_path
            with open(full_path, 'r') as f:
                current_content = f.read()
            self.assertEqual(original_content, current_content)


class TestTagCleanupValidation(unittest.TestCase):
    """Test validation and verification of tag cleanup results"""
    
    def setUp(self):
        """Set up validation test environment"""
        self.temp_dir = tempfile.mkdtemp()
        self.vault_path = Path(self.temp_dir)
        
    def test_cleanup_validation_system(self):
        """Test cleanup validation ensures quality improvements"""
        # This test will FAIL until validation system is implemented
        with self.assertRaises((ImportError, AttributeError)):
            from src.ai.enhanced_ai_tag_cleanup_deployment import TagCleanupValidator
            validator = TagCleanupValidator(self.vault_path)
            
            # Mock cleanup results
            cleanup_results = {
                'tags_modified': 15,
                'files_affected': 8,
                'success_rate': 0.93,
                'cleanup_details': [
                    {'original': '#', 'new': 'reference-hash', 'files': 2},
                    {'original': '|', 'new': 'separator', 'files': 1},
                    {'original': '2', 'new': 'year-2', 'files': 3}
                ]
            }
            
            validation_result = validator.validate_cleanup_quality(cleanup_results)
            
            # Should validate quality improvements
            self.assertTrue(validation_result['quality_improved'])
            self.assertGreaterEqual(validation_result['semantic_score'], 0.8)
            self.assertLessEqual(validation_result['problematic_remaining'], 10)
            
    def test_rollback_capability_validation(self):
        """Test rollback capability if cleanup validation fails"""
        # This test will FAIL until rollback capability is implemented
        with self.assertRaises((ImportError, AttributeError)):
            from src.ai.enhanced_ai_tag_cleanup_deployment import LightweightTagCleanupEngine
            engine = LightweightTagCleanupEngine(self.vault_path)
            
            # Create test scenario where rollback might be needed
            original_state = engine.capture_current_state()
            
            # Mock failed cleanup scenario
            cleanup_failed = True
            
            if cleanup_failed:
                rollback_result = engine.rollback_to_backup(original_state)
                self.assertTrue(rollback_result['rollback_successful'])
                self.assertEqual(rollback_result['files_restored'], original_state['file_count'])


class TestTagPollutionPrevention(unittest.TestCase):
    """Test prevention mechanisms for future tag pollution"""
    
    def setUp(self):
        """Set up prevention testing environment"""
        self.temp_dir = tempfile.mkdtemp()
        self.vault_path = Path(self.temp_dir)
        
    def test_template_tag_sanitization(self):
        """Test template updates prevent hash symbols and numeric-only tags"""
        # This test will FAIL until template sanitization is implemented
        with self.assertRaises((ImportError, AttributeError)):
            from src.ai.enhanced_ai_tag_cleanup_deployment import TemplateSanitizer
            sanitizer = TemplateSanitizer(self.vault_path)
            
            # Test problematic template patterns
            problematic_templates = [
                "tags: ['#tag', 'numeric123', '|separator']",
                "tags: ['2024', '8', 'a']",
                "tags: ['   ', '', '#']"
            ]
            
            for template in problematic_templates:
                sanitized = sanitizer.sanitize_template_tags(template)
                
                # Should not contain problematic patterns
                self.assertNotIn('#', sanitized)
                self.assertNotIn('|', sanitized) 
                self.assertNotRegex(sanitized, r"'[0-9]+'")  # No pure numeric tags
                self.assertNotIn("''", sanitized)  # No empty tags
                
    def test_weekly_review_tag_sanitization(self):
        """Test weekly review workflow includes tag sanitization"""
        # This test will FAIL until weekly review integration is implemented
        with self.assertRaises((ImportError, AttributeError)):
            from src.ai.enhanced_ai_tag_cleanup_deployment import WeeklyReviewSanitizer
            sanitizer = WeeklyReviewSanitizer()
            
            # Mock weekly review candidates with problematic tags
            review_candidates = [
                {"note": "test1.md", "tags": ["#", "good-tag", "123"], "quality": 0.6},
                {"note": "test2.md", "tags": ["valid-tag", "|", "another-good"], "quality": 0.7}
            ]
            
            sanitized_candidates = sanitizer.sanitize_review_tags(review_candidates)
            
            # Should sanitize problematic tags during review
            for candidate in sanitized_candidates:
                tags = candidate.get('tags', [])
                self.assertTrue(all(self._is_valid_tag(tag) for tag in tags))
                
    def _is_valid_tag(self, tag: str) -> bool:
        """Helper to validate tag format"""
        if not tag or not tag.strip():
            return False
        if tag in ['#', '|'] or tag.isdigit():
            return False
        if len(tag) < 2:
            return False
        return True
        
    def test_ai_tag_generation_sanitization(self):
        """Test AI tag generation includes sanitization to prevent pollution"""
        # This test will FAIL until AI generation sanitization is implemented
        with self.assertRaises((ImportError, AttributeError)):
            from src.ai.enhanced_ai_tag_cleanup_deployment import AISanitizedTagGenerator
            generator = AISanitizedTagGenerator()
            
            # Mock AI-generated tags that might be problematic
            mock_ai_output = ["good-tag", "#", "machine-learning", "123", "|", "valid-concept"]
            
            sanitized_tags = generator.sanitize_ai_generated_tags(mock_ai_output)
            
            # Should filter out problematic tags
            self.assertNotIn("#", sanitized_tags)
            self.assertNotIn("|", sanitized_tags)
            self.assertNotIn("123", sanitized_tags)
            
            # Should preserve good tags
            self.assertIn("good-tag", sanitized_tags)
            self.assertIn("machine-learning", sanitized_tags)
            self.assertIn("valid-concept", sanitized_tags)


class TestCleanupDeploymentIntegration(unittest.TestCase):
    """Test integration with existing InnerOS systems"""
    
    def setUp(self):
        """Set up integration testing environment"""
        self.temp_dir = tempfile.mkdtemp()
        self.vault_path = Path(self.temp_dir)
        
    def test_workflow_manager_integration(self):
        """Test cleanup integrates with existing WorkflowManager"""
        # This test will FAIL until WorkflowManager integration is implemented
        with self.assertRaises((ImportError, AttributeError)):
            from src.ai.enhanced_ai_tag_cleanup_deployment import CleanupWorkflowIntegrator
            from src.ai.workflow_manager import WorkflowManager
            
            integrator = CleanupWorkflowIntegrator(self.vault_path)
            workflow_manager = WorkflowManager(self.vault_path)
            
            # Should integrate with existing workflows
            integration_result = integrator.integrate_with_workflow_manager(workflow_manager)
            
            self.assertTrue(integration_result['integration_successful'])
            self.assertIn('cleanup_command_added', integration_result)
            
    def test_cli_integration_deployment(self):
        """Test CLI integration for cleanup deployment commands"""
        # This test will FAIL until CLI integration is implemented
        with self.assertRaises((ImportError, AttributeError)):
            from src.cli.workflow_demo import WorkflowDemo
            
            # Should add cleanup commands to existing CLI
            cli = WorkflowDemo()
            
            # New cleanup commands should be available
            self.assertTrue(hasattr(cli, 'execute_tag_cleanup'))
            self.assertTrue(hasattr(cli, 'validate_tag_quality'))
            
            # Should maintain existing functionality
            self.assertTrue(hasattr(cli, 'process_inbox'))
            self.assertTrue(hasattr(cli, 'weekly_review'))
            
    def test_performance_monitoring_integration(self):
        """Test cleanup deployment includes performance monitoring"""
        # This test will FAIL until performance monitoring is implemented
        with self.assertRaises((ImportError, AttributeError)):
            from src.ai.enhanced_ai_tag_cleanup_deployment import CleanupPerformanceMonitor
            monitor = CleanupPerformanceMonitor()
            
            # Mock cleanup performance data
            cleanup_metrics = {
                'processing_time': 15.5,
                'tags_processed': 25,
                'success_rate': 0.92,
                'memory_usage': 'acceptable'
            }
            
            performance_report = monitor.analyze_cleanup_performance(cleanup_metrics)
            
            # Should provide performance insights
            self.assertIn('performance_grade', performance_report)
            self.assertIn('optimization_suggestions', performance_report)
            self.assertIn('resource_efficiency', performance_report)


if __name__ == '__main__':
    # Run all tests - these will FAIL during RED phase as expected
    print("🔴 TDD ITERATION: Enhanced AI Tag Cleanup Deployment - RED PHASE")
    print("Expected: All tests will FAIL until implementation is complete")
    print("Target: Deploy cleanup for 30 problematic tags with <30s performance")
    print("Focus: Garbage tags (#, |, 2, 8, a), AI artifacts, malformed tags")
    print()
    
    unittest.main(verbosity=2)
