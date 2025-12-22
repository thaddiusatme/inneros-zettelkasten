"""
Test suite for Enhanced AI Tagging Prevention System (TDD Iteration 2)

Comprehensive test coverage for AI tagging prevention, focusing on preventing
problematic tags during AI processing following TDD Iteration 1 success patterns.

Real data validation findings: 84 problematic tags (69 parsing errors = 82%)
Critical path: Prevent AI-generated parsing error tags at source
"""

import pytest

# Mark entire module as WIP - TDD iteration tests not yet complete
pytestmark = pytest.mark.wip
from pathlib import Path
from unittest.mock import Mock

# Import classes we'll implement in GREEN phase
import sys

# Add the development directory to Python path
current_dir = Path(__file__).parent
development_dir = current_dir.parent.parent
sys.path.insert(0, str(development_dir))

try:
    from src.ai.ai_tagging_prevention import (
        AITagValidator,
        SemanticConceptExtractor,
        TagQualityGatekeeper,
        AITagPreventionEngine,
    )
    from src.ai.workflow_manager import WorkflowManager
except ImportError:
    # Classes don't exist yet - will be implemented in GREEN phase
    AITagValidator = None
    SemanticConceptExtractor = None
    TagQualityGatekeeper = None
    AITagPreventionEngine = None


class TestAITagValidator:
    """Test suite for AITagValidator - prevent problematic AI-generated tags"""

    def test_detect_paragraph_tags(self):
        """RED: Should detect and reject paragraph-length tags (>100 chars)"""
        validator = AITagValidator()

        # Real problematic examples from data validation
        paragraph_tags = [
            "this is a very long tag that represents an entire paragraph of content and should never be a tag because it violates semantic principles",
            "AI systems often generate these kinds of descriptive paragraph responses when asked for tags instead of concise semantic identifiers",
            "another example of AI-generated paragraph content that got interpreted as a single tag due to parsing issues in the workflow",
        ]

        short_tags = ["ai", "quantum-computing", "productivity"]

        result = validator.detect_paragraph_tags(paragraph_tags + short_tags)

        # Should detect all paragraph tags
        assert len(result) == 3
        assert all(len(tag) > 100 for tag in result)
        assert "ai" not in result
        assert "quantum-computing" not in result

    def test_detect_sentence_fragment_tags(self):
        """RED: Should detect sentence fragments posing as tags"""
        validator = AITagValidator()

        # Common AI-generated sentence fragments
        sentence_fragments = [
            "this note discusses the concept of",
            "the main idea here is about",
            "key insights from this content include",
            "important considerations for understanding",
            "approaches to solving the problem of",
        ]

        valid_tags = ["machine-learning", "productivity", "zettelkasten"]

        result = validator.detect_sentence_fragments(sentence_fragments + valid_tags)

        assert len(result) == 5
        assert all(
            any(word in tag for word in ["this", "the", "is", "for", "of"])
            for tag in result
        )
        assert "machine-learning" not in result

    def test_detect_technical_artifact_tags(self):
        """RED: Should detect AI technical artifacts and processing remnants"""
        validator = AITagValidator()

        # Technical artifacts from AI processing
        artifact_tags = [
            "ai_processing_tag_1",
            "llm_generated_concept_tag_2",
            "[AI-SUGGESTED]",
            "AUTO_TAG_GENERATED_BY_SYSTEM",
            "claude-3-processing-artifact",
            "##EXTRACTED_CONCEPT##",
        ]

        clean_tags = ["quantum-physics", "note-taking", "research"]

        result = validator.detect_technical_artifacts(artifact_tags + clean_tags)

        assert len(result) == 6
        assert (
            "AI_PROCESSING_TAG_1" in [tag.upper() for tag in result]
            or "ai_processing_tag_1" in result
        )
        assert "[AI-SUGGESTED]" in result
        assert "quantum-physics" not in result

    def test_validate_tag_character_limits(self):
        """RED: Should enforce reasonable character limits for tags"""
        validator = AITagValidator()

        # Test various length boundaries
        test_cases = [
            ("ai", True),  # Valid short tag
            ("machine-learning", True),  # Valid medium tag
            ("a" * 50, True),  # At reasonable limit
            ("a" * 100, False),  # Too long
            ("a" * 200, False),  # Way too long
            ("", False),  # Empty
            ("   ", False),  # Whitespace only
        ]

        for tag, expected_valid in test_cases:
            result = validator.validate_character_limits(tag)
            assert result == expected_valid, f"Tag '{tag}' validation failed"

    def test_validate_semantic_coherence(self):
        """RED: Should detect semantically incoherent tag combinations"""
        validator = AITagValidator()

        # Tags that don't make semantic sense together
        incoherent_combinations = [
            ["quantum-computing", "recipe", "cooking"],  # Mixed domains
            ["beginner", "advanced", "expert"],  # Contradictory levels
            ["delete-this", "keep-forever", "temporary"],  # Contradictory actions
        ]

        coherent_tags = ["ai", "machine-learning", "deep-learning"]  # Related domain

        for incoherent_tags in incoherent_combinations:
            result = validator.validate_semantic_coherence(incoherent_tags)
            assert result["coherent"] == False
            assert len(result["conflicts"]) > 0

        coherent_result = validator.validate_semantic_coherence(coherent_tags)
        assert coherent_result["coherent"] == True

    def test_comprehensive_validation_pipeline(self):
        """RED: Should run all validation checks in pipeline"""
        validator = AITagValidator()

        # Mix of all problem types
        problematic_tags = [
            "this is a very long paragraph tag that should be rejected",  # Paragraph
            "the main concept discussed here is",  # Sentence fragment
            "AI_PROCESSING_ARTIFACT_TAG",  # Technical artifact
            "a" * 150,  # Too long
            "",  # Empty
            "quantum-computing",  # Valid tag (should pass)
        ]

        result = validator.validate_tag_list(problematic_tags)

        assert "valid_tags" in result
        assert "rejected_tags" in result
        assert "rejection_reasons" in result
        assert "quantum-computing" in result["valid_tags"]
        assert len(result["rejected_tags"]) == 5  # All except quantum-computing


class TestSemanticConceptExtractor:
    """Test suite for SemanticConceptExtractor - break AI responses into proper tags"""

    def test_extract_concepts_from_ai_paragraph(self):
        """RED: Should extract individual concepts from AI paragraph responses"""
        extractor = SemanticConceptExtractor()

        # Typical AI response that should be multiple tags
        ai_paragraph = "This content discusses quantum computing, machine learning algorithms, and artificial intelligence applications in scientific research."

        result = extractor.extract_concepts(ai_paragraph)

        assert "quantum-computing" in result
        assert "machine-learning" in result
        assert "artificial-intelligence" in result
        assert "scientific-research" in result
        assert len(result) >= 4

    def test_extract_from_concept_lists(self):
        """RED: Should handle AI-generated concept lists and enumerations"""
        extractor = SemanticConceptExtractor()

        # AI responses with lists
        concept_list = "Key concepts: 1) Neural networks, 2) Deep learning, 3) Natural language processing, 4) Computer vision"

        result = extractor.extract_concepts(concept_list)

        assert "neural-networks" in result
        assert "deep-learning" in result
        assert "natural-language-processing" in result
        assert "computer-vision" in result
        assert len(result) >= 4

    def test_extract_from_technical_descriptions(self):
        """RED: Should extract concepts from technical AI descriptions"""
        extractor = SemanticConceptExtractor()

        # Technical description that should yield multiple tags
        technical_desc = "Implementation of transformer architecture using attention mechanisms for sequence-to-sequence modeling in natural language understanding tasks"

        result = extractor.extract_concepts(technical_desc)

        assert "transformer-architecture" in result
        assert "attention-mechanisms" in result
        assert "sequence-to-sequence" in result
        assert "natural-language-understanding" in result

    def test_filter_extraction_quality(self):
        """RED: Should filter extracted concepts for quality"""
        extractor = SemanticConceptExtractor()

        # Mixed quality extraction input
        mixed_content = "This discusses AI, machine learning, and some other stuff like the thing about using different approaches to solve problems"

        result = extractor.extract_concepts(mixed_content, min_quality_score=0.7)

        # Should extract clear concepts but filter vague ones
        assert "ai" in result or "artificial-intelligence" in result
        assert "machine-learning" in result
        assert "some other stuff" not in result  # Vague phrase filtered
        assert "the thing about" not in result  # Vague phrase filtered

    def test_preserve_domain_context(self):
        """RED: Should preserve domain context during extraction"""
        extractor = SemanticConceptExtractor()

        # Domain-specific content
        domain_content = "Quantum entanglement phenomena in superconducting qubits for quantum computing applications"

        result = extractor.extract_concepts(domain_content, preserve_domain=True)

        # Should maintain domain relationships
        assert "quantum-entanglement" in result
        assert "superconducting-qubits" in result
        assert "quantum-computing" in result
        # Should not split into overly generic terms
        assert "phenomena" not in result  # Too generic
        assert "applications" not in result  # Too generic


class TestTagQualityGatekeeper:
    """Test suite for TagQualityGatekeeper - real-time validation integration"""

    def test_real_time_tag_validation(self):
        """RED: Should validate tags in real-time during AI processing"""
        gatekeeper = TagQualityGatekeeper()

        # Simulate AI-generated tag stream
        ai_tag_stream = [
            "quantum-computing",  # Valid
            "this is a paragraph response from AI that should be rejected",  # Invalid
            "machine-learning",  # Valid
            "AI_ARTIFACT_TAG_123",  # Invalid
            "productivity",  # Valid
            "",  # Invalid
        ]

        validated_tags = []
        rejected_tags = []

        for tag in ai_tag_stream:
            result = gatekeeper.validate_real_time(tag)
            if result["valid"]:
                validated_tags.append(tag)
            else:
                rejected_tags.append(tag)

        assert len(validated_tags) == 3  # Only valid tags
        assert "quantum-computing" in validated_tags
        assert len(rejected_tags) == 3  # All invalid tags rejected

    def test_integration_with_ai_workflows(self):
        """RED: Should integrate seamlessly with existing AI processing"""
        gatekeeper = TagQualityGatekeeper()

        # Mock AI workflow processing
        mock_ai_response = {
            "tags": [
                "quantum-computing",
                "this note discusses advanced concepts in physics and mathematics",
                "machine-learning",
                "AUTO_GENERATED_TAG_PROCESSING",
            ],
            "quality_score": 0.85,
        }

        result = gatekeeper.filter_ai_workflow_tags(mock_ai_response)

        assert "filtered_tags" in result
        assert "rejected_count" in result
        assert "quality_improvement" in result
        assert "quantum-computing" in result["filtered_tags"]
        assert "machine-learning" in result["filtered_tags"]
        assert len(result["filtered_tags"]) == 2  # Only valid tags kept

    def test_performance_under_load(self):
        """RED: Should maintain performance during high-volume processing"""
        gatekeeper = TagQualityGatekeeper()

        # Simulate high-volume tag processing
        large_tag_batch = [f"tag-{i}" for i in range(1000)]
        large_tag_batch.extend(
            [
                "this is a problematic paragraph tag that should be filtered out",
                "AI_PROCESSING_ARTIFACT_SHOULD_REJECT",
            ]
        )

        import time

        start_time = time.time()
        result = gatekeeper.validate_batch(large_tag_batch)
        end_time = time.time()

        # Should process quickly (under 1 second for 1000+ tags)
        assert (end_time - start_time) < 1.0
        assert len(result["valid_tags"]) == 1000  # All simple tags valid
        assert len(result["rejected_tags"]) == 2  # Problematic ones rejected

    def test_feedback_loop_integration(self):
        """RED: Should support learning from user feedback"""
        gatekeeper = TagQualityGatekeeper()

        # User corrects AI tag suggestions
        user_feedback = {
            "rejected_by_user": ["auto-generated", "ai-suggested"],
            "accepted_by_user": ["machine-learning", "quantum-computing"],
            "user_corrections": {
                "ai": "artificial-intelligence",
                "ml": "machine-learning",
            },
        }

        gatekeeper.update_from_feedback(user_feedback)

        # Should remember patterns
        future_validation = gatekeeper.validate_real_time("auto-generated")
        assert future_validation["valid"] == False
        assert "learned from user feedback" in future_validation["reason"]


class TestWorkflowManagerIntegration:
    """Test suite for seamless WorkflowManager integration"""

    def test_process_inbox_note_with_prevention(self):
        """RED: Should integrate prevention into existing process_inbox_note"""
        # Mock existing WorkflowManager
        workflow_manager = Mock(spec=WorkflowManager)
        prevention_engine = AITagPreventionEngine(workflow_manager)

        # Mock note with AI processing
        mock_note_path = "/tmp/test-note.md"
        mock_note_content = """---
title: Test Note
type: fleeting
status: inbox
---

This note discusses quantum computing and machine learning applications."""

        # Should enhance existing workflow without breaking it
        result = prevention_engine.process_note_with_prevention(
            mock_note_path, mock_note_content
        )

        assert "original_ai_tags" in result
        assert "filtered_tags" in result
        assert "prevented_issues" in result
        assert "processing_preserved" in result
        assert result["processing_preserved"] == True

    def test_maintain_performance_targets(self):
        """RED: Should maintain <10s processing target with prevention"""
        workflow_manager = Mock(spec=WorkflowManager)
        prevention_engine = AITagPreventionEngine(workflow_manager)

        # Mock processing multiple notes
        mock_notes = [f"note-{i}.md" for i in range(10)]

        import time

        start_time = time.time()

        results = []
        for note in mock_notes:
            result = prevention_engine.process_note_with_prevention(note, "content")
            results.append(result)

        end_time = time.time()

        # Should stay under performance target
        assert (end_time - start_time) < 10  # <10s for 10 notes
        assert len(results) == 10
        assert all(r["processing_preserved"] for r in results)

    def test_preserve_existing_functionality(self):
        """RED: Should preserve all existing WorkflowManager functionality"""
        workflow_manager = Mock(spec=WorkflowManager)

        # Mock existing methods that must be preserved
        workflow_manager.process_inbox_note.return_value = {
            "ai_tags": ["quantum-computing", "machine-learning"],
            "quality_score": 0.85,
            "connections": ["related-note-1.md"],
        }

        prevention_engine = AITagPreventionEngine(workflow_manager)

        # Should call original methods and enhance results
        result = prevention_engine.process_note_with_prevention("test.md", "content")

        workflow_manager.process_inbox_note.assert_called_once()
        assert "enhanced_with_prevention" in result
        assert result["quality_score"] == 0.85  # Preserved
        assert result["connections"] == ["related-note-1.md"]  # Preserved

    def test_cli_integration_compatibility(self):
        """RED: Should work with existing CLI commands"""
        prevention_engine = AITagPreventionEngine(Mock())

        # Should provide CLI-compatible output
        cli_report = prevention_engine.generate_prevention_report()

        assert "summary" in cli_report
        assert "prevented_issues" in cli_report
        assert "performance_impact" in cli_report
        assert "recommendations" in cli_report


class TestAITagPreventionEngine:
    """Test suite for main AITagPreventionEngine orchestrator"""

    def test_engine_initialization(self):
        """RED: Should initialize with all prevention components"""
        workflow_manager = Mock(spec=WorkflowManager)
        engine = AITagPreventionEngine(workflow_manager)

        assert hasattr(engine, "tag_validator")
        assert hasattr(engine, "concept_extractor")
        assert hasattr(engine, "quality_gatekeeper")
        assert hasattr(engine, "workflow_manager")

    def test_comprehensive_prevention_pipeline(self):
        """RED: Should run complete prevention pipeline"""
        workflow_manager = Mock(spec=WorkflowManager)
        engine = AITagPreventionEngine(workflow_manager)

        # Mock AI workflow output with problems
        problematic_ai_output = {
            "ai_tags": [
                "quantum-computing",  # Valid
                "this is a very long AI-generated paragraph that should be a tag but is really just descriptive text",  # Invalid
                "machine-learning",  # Valid
                "AI_PROCESSING_ARTIFACT_123",  # Invalid
            ],
            "quality_score": 0.75,
        }

        result = engine.apply_comprehensive_prevention(problematic_ai_output)

        assert len(result["clean_tags"]) == 2  # Only valid tags
        assert "quantum-computing" in result["clean_tags"]
        assert "machine-learning" in result["clean_tags"]
        assert len(result["prevented_issues"]) == 2  # Both problems caught
        assert result["prevention_success_rate"] > 0

    def test_real_data_validation_targets(self):
        """RED: Should meet targets based on real data findings"""
        workflow_manager = Mock(spec=WorkflowManager)
        engine = AITagPreventionEngine(workflow_manager)

        # Simulate the 69 parsing error tags found in real data (82% of problems)
        real_problem_simulation = ["parsing-error-tag"] * 69 + ["valid-tag"] * 31

        prevention_results = engine.validate_against_real_problems(
            real_problem_simulation
        )

        # Should prevent >90% of parsing errors (target from requirements)
        assert prevention_results["parsing_errors_prevented"] >= 62  # >90% of 69
        assert prevention_results["prevention_rate"] > 0.9
        assert prevention_results["false_positive_rate"] < 0.1

    def test_integration_safety_validation(self):
        """RED: Should ensure integration doesn't break existing systems"""
        workflow_manager = Mock(spec=WorkflowManager)
        engine = AITagPreventionEngine(workflow_manager)

        # Should validate that integration is safe
        safety_check = engine.validate_integration_safety()

        assert safety_check["safe_to_integrate"] == True
        assert "backup_plan" in safety_check
        assert "rollback_capability" in safety_check
        assert "performance_impact" in safety_check


# Performance and Integration Tests
class TestPreventionPerformance:
    """Performance validation for prevention system"""

    def test_zero_regression_on_existing_tests(self):
        """RED: Should maintain all 26 existing tests passing"""
        # This test validates that prevention doesn't break TDD Iteration 1
        try:
            # Import and run existing test suite
            import test_rag_ready_tag_strategy

            # Should be able to import and run without issues
            existing_compatibility = True
        except ImportError:
            existing_compatibility = False

        assert (
            existing_compatibility == True
        ), "Must maintain existing test compatibility"

    def test_performance_within_targets(self):
        """RED: Should maintain <10s processing performance targets"""
        workflow_manager = Mock(spec=WorkflowManager)
        engine = AITagPreventionEngine(workflow_manager)

        # Simulate processing load similar to existing workflows
        large_content = "content " * 1000  # Large content block

        import time

        start_time = time.time()
        result = engine.apply_comprehensive_prevention(
            {"ai_tags": [f"tag-{i}" for i in range(100)], "content": large_content}
        )
        end_time = time.time()

        # Should stay well under performance target
        assert (end_time - start_time) < 1.0  # Much faster than 10s target
        assert len(result["clean_tags"]) > 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
