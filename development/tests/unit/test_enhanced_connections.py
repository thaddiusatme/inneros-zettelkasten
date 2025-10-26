#!/usr/bin/env python3
"""
TDD Iteration 7: Enhanced Connection Discovery System Tests
RED Phase - Comprehensive failing tests for relationship type detection, 
connection strength scoring, and cross-domain discovery.

Building on proven TDD patterns from Iterations 1-6.
"""

import unittest
import tempfile
import os
from datetime import datetime
import sys
from unittest.mock import patch

# Add development directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

# Import will fail initially - this is expected RED phase behavior
try:
    from src.ai.enhanced_connections import EnhancedConnectionsEngine
    from src.ai.workflow_manager import WorkflowManager
except ImportError:
    # Expected during RED phase
    EnhancedConnectionsEngine = None
    WorkflowManager = None


class TestEnhancedConnectionsEngine(unittest.TestCase):
    """
    TDD Test Suite for Enhanced Connection Discovery Engine
    
    P0 Features:
    - Semantic relationship type detection (builds_on, contradicts, bridges, examples)
    - Connection strength scoring with confidence intervals  
    - Cross-domain connection discovery (analogies between knowledge areas)
    
    P1 Features:
    - Real-time connection suggestions during capture processing
    - Connection preview integration with voice note pipeline
    - Connection validation and user feedback loop
    """

    def setUp(self):
        """Set up test environment for enhanced connections testing"""
        self.temp_dir = tempfile.mkdtemp()
        self.sample_capture_notes = self._create_sample_capture_notes()

        # Initialize enhanced connections engine
        if EnhancedConnectionsEngine:
            self.enhanced_engine = EnhancedConnectionsEngine()

    def tearDown(self):
        """Clean up test environment"""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def _create_sample_capture_notes(self):
        """Create sample capture notes for testing cross-domain connections"""
        return {
            "machine-learning-fundamentals.md": {
                "content": """
                Machine learning algorithms learn patterns from data to make predictions.
                Neural networks are inspired by biological brain structures.
                Training requires large datasets and computational resources.
                """,
                "domain": "technology",
                "concepts": ["machine learning", "neural networks", "pattern recognition"]
            },
            "cooking-flavor-chemistry.md": {
                "content": """
                Cooking is about understanding how ingredients interact chemically.
                Heat transforms proteins and creates new flavor compounds.
                Experience teaches pattern recognition in taste combinations.
                """,
                "domain": "culinary",
                "concepts": ["chemistry", "pattern recognition", "experience"]
            },
            "zettelkasten-knowledge-building.md": {
                "content": """
                Zettelkasten method builds knowledge through connected ideas.
                Each note should be atomic and linked to related concepts.
                Knowledge networks emerge from individual building blocks.
                """,
                "domain": "knowledge_management",
                "concepts": ["knowledge networks", "atomic ideas", "building blocks"]
            },
            "music-harmony-theory.md": {
                "content": """
                Musical harmony follows mathematical patterns and ratios.
                Chord progressions create tension and resolution cycles.
                Musicians develop pattern recognition through practice.
                """,
                "domain": "music",
                "concepts": ["mathematical patterns", "tension resolution", "pattern recognition"]
            }
        }

    # RED PHASE - P0 Critical Features Tests

    def test_detect_relationship_types_builds_on(self):
        """RED: Test detection of 'builds_on' relationship type"""
        if not EnhancedConnectionsEngine:
            self.fail("EnhancedConnectionsEngine not implemented yet")

        # Test case: One note builds conceptually on another
        base_note = "Supervised learning uses labeled data for training."
        extending_note = "Deep learning is a subset of supervised learning using neural networks."

        result = self.enhanced_engine.detect_relationship_type(base_note, extending_note)

        self.assertEqual(result["relationship_type"], "builds_on")
        self.assertGreater(result["confidence"], 0.8)
        self.assertIn("extends", result["explanation"].lower())

    def test_detect_relationship_types_contradicts(self):
        """RED: Test detection of 'contradicts' relationship type"""
        if not EnhancedConnectionsEngine:
            self.fail("EnhancedConnectionsEngine not implemented yet")

        # Test case: Contradictory statements about same concept
        note_a = "Unsupervised learning requires no labeled data for training."
        note_b = "All machine learning algorithms require labeled training data."

        result = self.enhanced_engine.detect_relationship_type(note_a, note_b)

        self.assertEqual(result["relationship_type"], "contradicts")
        self.assertGreater(result["confidence"], 0.7)
        self.assertIn("contradict", result["explanation"].lower())

    def test_detect_relationship_types_bridges(self):
        """RED: Test detection of 'bridges' relationship type"""
        if not EnhancedConnectionsEngine:
            self.fail("EnhancedConnectionsEngine not implemented yet")

        # Test case: Note that connects two different domains
        domain_a = "Neural networks process information in layers."
        bridge_note = "The brain's visual cortex processes images hierarchically, similar to CNN layers."
        domain_b = "Human vision recognizes objects through feature detection."

        result = self.enhanced_engine.detect_relationship_type_triple(domain_a, bridge_note, domain_b)

        self.assertEqual(result["relationship_type"], "bridges")
        self.assertGreater(result["confidence"], 0.7)
        self.assertIn("connect", result["explanation"].lower())

    def test_detect_relationship_types_examples(self):
        """RED: Test detection of 'examples' relationship type"""
        if not EnhancedConnectionsEngine:
            self.fail("EnhancedConnectionsEngine not implemented yet")

        # Test case: Specific example of general concept
        general_note = "Reinforcement learning agents learn through trial and error."
        example_note = "AlphaGo mastered Go by playing millions of games against itself."

        result = self.enhanced_engine.detect_relationship_type(general_note, example_note)

        self.assertEqual(result["relationship_type"], "examples")
        self.assertGreater(result["confidence"], 0.8)
        self.assertIn("example", result["explanation"].lower())

    def test_connection_strength_scoring_with_confidence(self):
        """RED: Test connection strength scoring with confidence intervals"""
        if not EnhancedConnectionsEngine:
            self.fail("EnhancedConnectionsEngine not implemented yet")

        # Test various connection strengths
        strong_connection = ("Machine learning", "Deep learning algorithms")
        weak_connection = ("Machine learning", "Italian cooking recipes")

        strong_result = self.enhanced_engine.calculate_connection_strength(*strong_connection)
        weak_result = self.enhanced_engine.calculate_connection_strength(*weak_connection)

        # Strong connection should have high score and narrow confidence interval
        self.assertGreater(strong_result["strength_score"], 0.8)
        self.assertLess(strong_result["confidence_interval_width"], 0.2)

        # Weak connection should have low score and wider confidence interval
        self.assertLess(weak_result["strength_score"], 0.3)
        self.assertGreater(weak_result["confidence_interval_width"], 0.3)

    def test_cross_domain_connection_discovery(self):
        """RED: Test cross-domain analogical connection discovery"""
        if not EnhancedConnectionsEngine:
            self.fail("EnhancedConnectionsEngine not implemented yet")

        # Test finding analogies between different knowledge domains
        result = self.enhanced_engine.discover_cross_domain_connections(self.sample_capture_notes)

        # Should find pattern recognition connection across domains
        cross_domain_connections = [conn for conn in result if conn["connection_type"] == "cross_domain"]
        self.assertGreater(len(cross_domain_connections), 0)

        # Verify specific cross-domain connection exists
        pattern_recognition_connection = next(
            (conn for conn in cross_domain_connections
             if "pattern recognition" in conn["shared_concept"].lower()),
            None
        )
        self.assertIsNotNone(pattern_recognition_connection)
        self.assertGreater(pattern_recognition_connection["analogy_strength"], 0.6)

    # RED PHASE - P1 Integration Features Tests

    def test_real_time_connection_suggestions_during_capture(self):
        """RED: Test real-time connection suggestions during capture processing"""
        if not EnhancedConnectionsEngine:
            self.fail("EnhancedConnectionsEngine not implemented yet")

        # Simulate processing a new capture note
        new_capture_content = """
        Voice note about neural network architecture patterns.
        Discussing how convolution layers detect features hierarchically.
        """

        existing_notes = self.sample_capture_notes

        suggestions = self.enhanced_engine.suggest_connections_realtime(
            new_capture_content, existing_notes
        )

        # Should provide immediate connection suggestions
        self.assertGreater(len(suggestions), 0)
        self.assertTrue(any(s["confidence"] > 0.7 for s in suggestions))

        # Should include relationship type and explanation
        for suggestion in suggestions:
            self.assertIn("relationship_type", suggestion)
            self.assertIn("explanation", suggestion)
            self.assertIn("target_note", suggestion)

    def test_connection_preview_integration(self):
        """RED: Test connection preview during capture note generation"""
        if not EnhancedConnectionsEngine:
            self.fail("EnhancedConnectionsEngine not implemented yet")

        # Test preview functionality for capture workflow integration
        capture_data = {
            "content": "New insight about pattern recognition in cooking",
            "timestamp": datetime.now(),
            "domain": "culinary"
        }

        preview = self.enhanced_engine.generate_connection_preview(
            capture_data, self.sample_capture_notes
        )

        # Preview should include potential connections with context
        self.assertIn("potential_connections", preview)
        self.assertIn("preview_explanation", preview)
        self.assertGreater(len(preview["potential_connections"]), 0)

        # Should indicate processing time for real-time feedback
        self.assertIn("processing_time_ms", preview)
        self.assertLess(preview["processing_time_ms"], 5000)  # <5 seconds target

    def test_connection_validation_and_feedback(self):
        """RED: Test connection validation and user feedback loop"""
        if not EnhancedConnectionsEngine:
            self.fail("EnhancedConnectionsEngine not implemented yet")

        # Test validation of suggested connections
        suggested_connection = {
            "source_note": "machine-learning-fundamentals.md",
            "target_note": "cooking-flavor-chemistry.md",
            "relationship_type": "bridges",
            "shared_concept": "pattern recognition",
            "confidence": 0.75
        }

        # Simulate user feedback (accept/reject)
        validation_result = self.enhanced_engine.validate_connection_with_feedback(
            suggested_connection, user_feedback="accept"
        )

        self.assertTrue(validation_result["accepted"])
        self.assertIn("feedback_processed", validation_result)

        # Test rejection feedback
        rejection_result = self.enhanced_engine.validate_connection_with_feedback(
            suggested_connection, user_feedback="reject",
            rejection_reason="too_abstract"
        )

        self.assertFalse(rejection_result["accepted"])
        self.assertEqual(rejection_result["rejection_reason"], "too_abstract")

    # RED PHASE - Integration with Existing Systems Tests

    def test_integration_with_workflow_manager(self):
        """RED: Test integration with existing WorkflowManager"""
        if not EnhancedConnectionsEngine or not WorkflowManager:
            self.fail("Integration classes not implemented yet")

        # Test that enhanced connections integrates with existing AI workflow
        with patch('src.ai.workflow_manager.WorkflowManager') as mock_workflow:
            mock_workflow.return_value.process_inbox_note.return_value = {
                "quality_score": 0.8,
                "ai_tags": ["machine-learning", "neural-networks"],
                "summary": "Note about ML fundamentals"
            }

            enhanced_result = self.enhanced_engine.process_with_workflow_integration(
                "Test note content", mock_workflow.return_value
            )

            # Should combine existing workflow results with enhanced connections
            self.assertIn("workflow_result", enhanced_result)
            self.assertIn("enhanced_connections", enhanced_result)
            self.assertIn("processing_stats", enhanced_result)

    def test_performance_targets_compliance(self):
        """RED: Test that enhanced features meet performance targets"""
        if not EnhancedConnectionsEngine:
            self.fail("EnhancedConnectionsEngine not implemented yet")

        import time

        # Test processing 5+ capture notes within 30 seconds
        start_time = time.time()

        results = []
        for i, (note_name, note_data) in enumerate(list(self.sample_capture_notes.items())[:5]):
            result = self.enhanced_engine.discover_cross_domain_connections({
                note_name: note_data
            })
            results.append(result)

        processing_time = time.time() - start_time

        # Performance target: <30 seconds for 5+ captures with enhanced analysis
        self.assertLess(processing_time, 30.0)

        # Verify quality: >85% accuracy for relationship type detection
        accuracy_scores = [r.get("accuracy_score", 0) for r in results if r]
        if accuracy_scores:
            avg_accuracy = sum(accuracy_scores) / len(accuracy_scores)
            self.assertGreater(avg_accuracy, 0.85)

    def test_zettelkasten_3a_formula_integration(self):
        """RED: Test integration with 3-A Formula voice prompt system"""
        if not EnhancedConnectionsEngine:
            self.fail("EnhancedConnectionsEngine not implemented yet")

        # Test processing of 3-A Formula structured voice note
        voice_note_3a = {
            "atomic_concept": "Backpropagation algorithm in neural networks",
            "associate_connections": ["gradient descent", "chain rule", "optimization"],
            "advance_insights": "Similar to how water flows downhill, gradients flow towards minimum error"
        }

        enhanced_result = self.enhanced_engine.process_3a_formula_note(voice_note_3a)

        # Should extract structured connections from 3-A format
        self.assertIn("atomic_connections", enhanced_result)
        self.assertIn("associative_links", enhanced_result)
        self.assertIn("advancement_bridges", enhanced_result)

        # Should identify the analogy in advancement section
        advancement_connections = enhanced_result["advancement_bridges"]
        water_analogy = next(
            (conn for conn in advancement_connections if "analogy" in conn["connection_type"]),
            None
        )
        self.assertIsNotNone(water_analogy)


if __name__ == '__main__':
    # Run tests with verbose output for TDD development
    unittest.main(verbosity=2)
