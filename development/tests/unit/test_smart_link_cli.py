#!/usr/bin/env python3
"""
Test suite for Smart Link Management CLI Integration - TDD Iteration 2
Tests CLI argument parsing, LinkSuggestionEngine integration, and interactive workflow
"""

import pytest
import tempfile
import json
import os
import sys
from pathlib import Path
from unittest.mock import patch, MagicMock, call
from io import StringIO
import argparse

# Add development directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../src'))

from ai.link_suggestion_engine import LinkSuggestionEngine, LinkSuggestion
from ai.link_suggestion_utils import QualityScore

class TestSmartLinkCLIIntegration:
    """Test suite for CLI integration with LinkSuggestionEngine"""
    
    @pytest.fixture
    def temp_vault(self):
        """Create temporary vault structure with test notes for CLI testing"""
        with tempfile.TemporaryDirectory() as temp_dir:
            vault_path = Path(temp_dir)
            
            # Create directory structure
            (vault_path / "Permanent Notes").mkdir()
            (vault_path / "Fleeting Notes").mkdir()
            
            # Create test notes with realistic content
            ai_note = vault_path / "Permanent Notes" / "ai-concepts.md"
            ai_note.write_text("""---
type: permanent
tags: [ai, machine-learning, concepts]
---
# AI Concepts

This note covers fundamental artificial intelligence concepts including
machine learning algorithms and neural networks.

## Core Concepts
- Deep learning fundamentals  
- Neural network architectures
""")
            
            ml_note = vault_path / "Permanent Notes" / "machine-learning-basics.md"
            ml_note.write_text("""---
type: permanent
tags: [machine-learning, algorithms]  
---
# Machine Learning Basics

Introduction to machine learning algorithms and their applications.

## Key Topics
- Supervised learning
- Unsupervised learning
- Deep neural networks
""")
            
            yield vault_path
    
    @pytest.fixture
    def mock_suggestions(self):
        """Mock LinkSuggestion objects for testing display and interaction"""
        return [
            LinkSuggestion(
                source_note="ai-concepts.md",
                target_note="machine-learning-basics.md",
                suggested_link_text="[[Machine Learning Basics]]",
                similarity_score=0.85,
                quality_score=0.87,
                confidence="high", 
                explanation="Strong semantic similarity (85%) with shared AI/ML concepts",
                insertion_context="## Core Concepts",
                suggested_location="related_concepts"
            ),
            LinkSuggestion(
                source_note="ai-concepts.md", 
                target_note="neural-networks.md",
                suggested_link_text="[[Neural Networks]]",
                similarity_score=0.72,
                quality_score=0.75,
                confidence="medium",
                explanation="Moderate semantic relationship (72%) with neural network concepts",
                insertion_context="## Related Topics", 
                suggested_location="see_also"
            ),
            LinkSuggestion(
                source_note="ai-concepts.md",
                target_note="data-science.md", 
                suggested_link_text="[[Data Science]]",
                similarity_score=0.45,
                quality_score=0.48,
                confidence="low",
                explanation="Weak connection (45%) - manual review recommended",
                insertion_context="## See Also",
                suggested_location="see_also"
            )
        ]

class TestCLIArgumentParsing:
    """Test CLI argument parsing for suggest-links command"""
    
    def test_suggest_links_command_parsing(self):
        """Test parsing of suggest-links command with required arguments"""
        # This test should fail initially - suggest-links command doesn't exist yet
        from cli.connections_demo import create_parser
        
        parser = create_parser()
        
        # Test basic command parsing
        args = parser.parse_args(['suggest-links', 'test-note.md', 'knowledge/'])
        assert args.command == 'suggest-links'
        assert args.target == 'test-note.md'
        assert args.corpus_dir == 'knowledge/'
    
    def test_suggest_links_optional_arguments(self):
        """Test parsing of optional arguments for suggest-links command"""
        from cli.connections_demo import create_parser
        
        parser = create_parser()
        
        # Test with all optional arguments
        args = parser.parse_args([
            'suggest-links', 'test-note.md', 'knowledge/',
            '--interactive',
            '--min-quality', '0.7',
            '--max-results', '10', 
            '--dry-run'
        ])
        
        assert args.interactive is True
        assert args.min_quality == 0.7
        assert args.max_results == 10
        assert args.dry_run is True
    
    def test_suggest_links_default_values(self):
        """Test default values for optional CLI arguments"""
        from cli.connections_demo import create_parser
        
        parser = create_parser()
        args = parser.parse_args(['suggest-links', 'test.md', 'vault/'])
        
        # Should use sensible defaults
        assert args.interactive is False
        assert args.min_quality == 0.6  # Default quality threshold
        assert args.max_results == 5     # Default max results
        assert args.dry_run is False
    
    def test_invalid_suggest_links_arguments(self):
        """Test error handling for invalid CLI arguments"""
        from cli.connections_demo import create_parser
        
        parser = create_parser()
        
        # Test invalid quality threshold
        with pytest.raises(SystemExit):
            parser.parse_args(['suggest-links', 'test.md', 'vault/', '--min-quality', '1.5'])
        
        # Test negative max results
        with pytest.raises(SystemExit):
            parser.parse_args(['suggest-links', 'test.md', 'vault/', '--max-results', '-5'])


class TestLinkSuggestionEngineIntegration:
    """Test integration between CLI and LinkSuggestionEngine"""
    
    @patch('cli.connections_demo.LinkSuggestionEngine')
    @patch('cli.connections_demo.load_single_note')
    @patch('cli.connections_demo.load_note_corpus')
    def test_engine_initialization_from_cli(self, mock_corpus, mock_note, mock_engine, temp_vault):
        """Test LinkSuggestionEngine initialization from CLI command"""
        from cli.connections_demo import handle_suggest_links_command
        
        # Mock data
        mock_note.return_value = "test note content"
        mock_corpus.return_value = {"note1.md": "content1", "note2.md": "content2"}
        
        # Mock engine instance and methods
        mock_engine_instance = MagicMock()
        mock_engine.return_value = mock_engine_instance
        
        # Create mock args
        mock_args = MagicMock()
        mock_args.target = "test-note.md"
        mock_args.corpus_dir = str(temp_vault)
        mock_args.min_quality = 0.7
        mock_args.max_results = 5
        mock_args.interactive = False
        mock_args.dry_run = False
        
        # Execute CLI command
        handle_suggest_links_command(mock_args)
        
        # Verify LinkSuggestionEngine was initialized correctly
        mock_engine.assert_called_once_with(
            vault_path=str(temp_vault),
            quality_threshold=0.7,
            max_suggestions=5
        )
    
    @patch('cli.connections_demo.LinkSuggestionEngine')
    def test_suggestion_generation_integration(self, mock_engine, mock_suggestions):
        """Test integration between CLI and suggestion generation"""
        from cli.connections_demo import handle_suggest_links_command
        
        # Mock engine instance with suggestions
        mock_engine_instance = MagicMock()
        mock_engine_instance.generate_link_suggestions.return_value = mock_suggestions
        mock_engine.return_value = mock_engine_instance
        
        # Mock other dependencies
        with patch('cli.connections_demo.load_single_note') as mock_note, \
             patch('cli.connections_demo.load_note_corpus') as mock_corpus:
            
            mock_note.return_value = "target content"
            mock_corpus.return_value = {"note1.md": "content1"}
            
            mock_args = MagicMock()
            mock_args.target = "test.md"
            mock_args.corpus_dir = "vault/"
            mock_args.interactive = False
            mock_args.dry_run = False
            
            result = handle_suggest_links_command(mock_args)
            
            # Verify suggestions were generated
            mock_engine_instance.generate_link_suggestions.assert_called_once()
            assert result is not None


class TestInteractiveReviewWorkflow:
    """Test interactive review workflow with user input handling"""
    
    @patch('builtins.input')
    @patch('sys.stdout', new_callable=StringIO)
    def test_interactive_suggestion_display(self, mock_stdout, mock_input, mock_suggestions):
        """Test formatted display of suggestions in interactive mode"""
        from cli.smart_link_cli_utils import display_suggestion_interactively
        
        # Mock user accepting first suggestion
        mock_input.return_value = 'a'
        
        suggestion = mock_suggestions[0]  # High quality suggestion
        result = display_suggestion_interactively(suggestion, 1, 3)
        
        output = mock_stdout.getvalue()
        
        # Verify suggestion display includes key information
        assert "🟢" in output  # High quality emoji indicator
        assert "Machine Learning Basics" in output  # Link text
        assert "85%" in output  # Similarity score
        assert "Strong semantic similarity" in output  # Explanation
        assert "[A]ccept" in output  # Accept option
        assert "[R]eject" in output  # Reject option
        assert "[S]kip" in output    # Skip option
        
        # Verify user choice is returned
        assert result == 'accept'
    
    @patch('builtins.input')  
    @patch('sys.stdout', new_callable=StringIO)
    def test_quality_indicator_display(self, mock_stdout, mock_input, mock_suggestions):
        """Test quality indicators for different confidence levels"""
        from cli.smart_link_cli_utils import display_suggestion_interactively
        
        mock_input.return_value = 's'
        
        # Test high quality (green)
        high_quality = mock_suggestions[0]
        display_suggestion_interactively(high_quality, 1, 3)
        output_high = mock_stdout.getvalue()
        assert "🟢" in output_high
        
        mock_stdout.seek(0)
        mock_stdout.truncate(0)
        
        # Test medium quality (yellow)  
        medium_quality = mock_suggestions[1]
        display_suggestion_interactively(medium_quality, 1, 3)
        output_medium = mock_stdout.getvalue()
        assert "🟡" in output_medium
        
        mock_stdout.seek(0)
        mock_stdout.truncate(0)
        
        # Test low quality (red)
        low_quality = mock_suggestions[2]
        display_suggestion_interactively(low_quality, 1, 3)
        output_low = mock_stdout.getvalue()
        assert "🔴" in output_low
    
    @patch('builtins.input')
    def test_user_input_validation(self, mock_input):
        """Test validation and handling of user input during interactive review"""
        from cli.smart_link_cli_utils import get_user_choice_for_suggestion
        
        # Test valid inputs
        mock_input.return_value = 'a'
        assert get_user_choice_for_suggestion() == 'accept'
        
        mock_input.return_value = 'r'  
        assert get_user_choice_for_suggestion() == 'reject'
        
        mock_input.return_value = 's'
        assert get_user_choice_for_suggestion() == 'skip'
        
        # Test case insensitive
        mock_input.return_value = 'A'
        assert get_user_choice_for_suggestion() == 'accept'
    
    @patch('builtins.input')
    def test_invalid_input_handling(self, mock_input):
        """Test handling of invalid user input with re-prompting"""
        from cli.smart_link_cli_utils import get_user_choice_for_suggestion
        
        # First invalid, then valid input
        mock_input.side_effect = ['x', 'invalid', 'a']
        result = get_user_choice_for_suggestion()
        
        # Should eventually return valid choice after invalid attempts
        assert result == 'accept'
        assert mock_input.call_count == 3  # Two invalid attempts, one valid


class TestBatchProcessingCLI:
    """Test batch processing functionality in CLI"""
    
    @patch('cli.connections_demo.LinkSuggestionEngine')
    def test_batch_suggestion_processing(self, mock_engine, mock_suggestions):
        """Test processing multiple suggestions with progress indicators"""
        from cli.connections_demo import process_suggestions_batch
        
        # Mock engine with multiple suggestions
        mock_engine_instance = MagicMock()
        mock_engine_instance.generate_link_suggestions.return_value = mock_suggestions
        mock_engine.return_value = mock_engine_instance
        
        suggestions = mock_suggestions
        
        with patch('cli.smart_link_cli_utils.display_progress') as mock_progress:
            result = process_suggestions_batch(suggestions, interactive=False)
            
            # Verify progress display was called
            mock_progress.assert_called()
            
            # Verify all suggestions were processed
            assert len(result) == len(suggestions)
    
    @patch('sys.stdout', new_callable=StringIO)
    def test_batch_progress_display(self, mock_stdout):
        """Test progress display during batch processing"""
        from cli.smart_link_cli_utils import display_batch_progress
        
        # Test progress display
        display_batch_progress(current=3, total=10, current_note="test-note.md")
        
        output = mock_stdout.getvalue()
        assert "3/10" in output
        assert "test-note.md" in output
        assert "%" in output  # Progress percentage
    
    def test_batch_filtering_integration(self, mock_suggestions):
        """Test quality filtering during batch processing"""
        from cli.smart_link_cli_utils import filter_suggestions_by_quality
        
        # Filter with high quality threshold
        high_quality = filter_suggestions_by_quality(mock_suggestions, min_quality=0.8)
        assert len(high_quality) == 1  # Only high quality suggestion
        assert high_quality[0].confidence == "high"
        
        # Filter with lower threshold
        medium_quality = filter_suggestions_by_quality(mock_suggestions, min_quality=0.5)
        assert len(medium_quality) == 2  # High and medium quality suggestions


class TestOutputFormatting:
    """Test CLI output formatting and presentation"""
    
    @patch('sys.stdout', new_callable=StringIO)
    def test_suggestion_summary_display(self, mock_stdout, mock_suggestions):
        """Test formatted display of suggestion summary"""
        from cli.smart_link_cli_utils import display_suggestions_summary
        
        display_suggestions_summary(mock_suggestions, processed=2, accepted=1, rejected=1)
        
        output = mock_stdout.getvalue()
        
        # Verify summary contains key statistics
        assert "3 suggestions" in output or "3" in output
        assert "2 processed" in output or "2" in output
        assert "1 accepted" in output or "1" in output
        assert "1 rejected" in output or "1" in output
    
    @patch('sys.stdout', new_callable=StringIO)  
    def test_dry_run_mode_display(self, mock_stdout, mock_suggestions):
        """Test dry-run mode formatting without actual modifications"""
        from cli.smart_link_cli_utils import display_dry_run_results
        
        display_dry_run_results(mock_suggestions, target_note="ai-concepts.md")
        
        output = mock_stdout.getvalue()
        
        # Verify dry-run indicators
        assert "DRY RUN" in output or "Preview" in output
        assert "ai-concepts.md" in output
        assert "would be added" in output or "would add" in output
        # Should not contain actual modification language
        assert "added" not in output.lower() or "modified" not in output.lower()
    
    @patch('sys.stdout', new_callable=StringIO)
    def test_error_formatting(self, mock_stdout):
        """Test formatted error display in CLI"""
        from cli.smart_link_cli_utils import display_cli_error
        
        display_cli_error("File not found", "test-note.md")
        
        output = mock_stdout.getvalue()
        assert "❌" in output or "Error" in output
        assert "File not found" in output
        assert "test-note.md" in output


class TestCLIIntegrationEndToEnd:
    """End-to-end integration tests for complete CLI workflow"""
    
    @patch('builtins.input')
    @patch('cli.connections_demo.LinkSuggestionEngine')
    def test_complete_interactive_workflow(self, mock_engine, mock_input, mock_suggestions, temp_vault):
        """Test complete interactive workflow from command to suggestion acceptance"""
        from cli.connections_demo import main
        
        # Mock user accepting all suggestions
        mock_input.side_effect = ['a', 'a', 'r']  # Accept, Accept, Reject
        
        # Mock engine
        mock_engine_instance = MagicMock()
        mock_engine_instance.generate_link_suggestions.return_value = mock_suggestions
        mock_engine.return_value = mock_engine_instance
        
        # Mock sys.argv for CLI 
        test_args = [
            'connections_demo.py',
            'suggest-links', 
            str(temp_vault / "Permanent Notes" / "ai-concepts.md"),
            str(temp_vault),
            '--interactive'
        ]
        
        with patch.object(sys, 'argv', test_args), \
             patch('cli.connections_demo.load_single_note') as mock_note, \
             patch('cli.connections_demo.load_note_corpus') as mock_corpus:
            
            mock_note.return_value = "test content"
            mock_corpus.return_value = {"test.md": "content"}
            
            # Should complete without errors
            try:
                main()
            except SystemExit:
                pass  # Expected for successful CLI completion
    
    def test_cli_error_handling(self, temp_vault):
        """Test CLI error handling for invalid inputs"""
        from cli.connections_demo import main
        
        # Test with non-existent target file
        test_args = [
            'connections_demo.py', 
            'suggest-links',
            'nonexistent-file.md',
            str(temp_vault)
        ]
        
        with patch.object(sys, 'argv', test_args):
            with pytest.raises(SystemExit):
                main()
    
    @patch('cli.connections_demo.LinkSuggestionEngine')
    def test_performance_requirements(self, mock_engine, mock_suggestions):
        """Test that CLI meets performance requirements (<2s response time)"""
        import time
        from cli.connections_demo import handle_suggest_links_command
        
        # Mock fast engine
        mock_engine_instance = MagicMock()
        mock_engine_instance.generate_link_suggestions.return_value = mock_suggestions
        mock_engine.return_value = mock_engine_instance
        
        mock_args = MagicMock()
        mock_args.target = "test.md"
        mock_args.corpus_dir = "vault/"
        mock_args.interactive = False
        mock_args.dry_run = False
        
        with patch('cli.connections_demo.load_single_note') as mock_note, \
             patch('cli.connections_demo.load_note_corpus') as mock_corpus:
            
            mock_note.return_value = "content"
            mock_corpus.return_value = {"test.md": "content"}
            
            start_time = time.time()
            handle_suggest_links_command(mock_args)
            end_time = time.time()
            
            # Should complete in under 2 seconds (generous for mocked components)
            assert (end_time - start_time) < 2.0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
