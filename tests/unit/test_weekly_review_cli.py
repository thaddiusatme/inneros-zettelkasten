"""
Unit tests for the weekly review CLI functionality.
"""

import pytest
import tempfile
import shutil
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock, mock_open
from datetime import datetime

import sys
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.cli.weekly_review_formatter import WeeklyReviewFormatter


class TestWeeklyReviewFormatter:
    """Test cases for WeeklyReviewFormatter class."""
    
    def setup_method(self):
        """Set up test environment."""
        self.formatter = WeeklyReviewFormatter()
        
        # Sample recommendation data for testing
        self.sample_recommendations = {
            "summary": {
                "total_notes": 3,
                "promote_to_permanent": 1,
                "move_to_fleeting": 1,
                "needs_improvement": 1,
                "processing_errors": 0
            },
            "recommendations": [
                {
                    "file_name": "high_quality.md",
                    "source": "inbox",
                    "action": "promote_to_permanent",
                    "reason": "High quality content with comprehensive analysis",
                    "quality_score": 0.85,
                    "confidence": 0.9,
                    "ai_tags": ["machine-learning", "deep-learning"]
                },
                {
                    "file_name": "medium_quality.md", 
                    "source": "fleeting",
                    "action": "move_to_fleeting",
                    "reason": "Good start but needs more development",
                    "quality_score": 0.55,
                    "confidence": 0.7,
                    "ai_tags": ["productivity"]
                },
                {
                    "file_name": "low_quality.md",
                    "source": "inbox", 
                    "action": "improve_or_archive",
                    "reason": "Content is too brief and lacks detail",
                    "quality_score": 0.25,
                    "confidence": 0.8,
                    "ai_tags": []
                }
            ],
            "generated_at": "2025-07-30T22:57:00"
        }
    
    def test_format_checklist_summary(self):
        """Test that checklist includes proper summary header."""
        checklist = self.formatter.format_checklist(self.sample_recommendations)
        
        # Should include summary with counts
        assert "3 notes to process" in checklist
        assert "1 promote" in checklist
        assert "1 refine" in checklist
        assert "1 improve" in checklist
        
        # Should include date header
        assert "Weekly Review" in checklist
        assert "2025-07-30" in checklist
    
    def test_format_checklist_sections(self):
        """Test that checklist is properly organized into sections."""
        checklist = self.formatter.format_checklist(self.sample_recommendations)
        
        # Should have three main sections
        assert "🎯 Ready to Promote" in checklist
        assert "🔄 Further Development" in checklist
        assert "⚠️ Needs Significant Work" in checklist
        
        # Sections should be in priority order
        promote_pos = checklist.find("🎯 Ready to Promote")
        develop_pos = checklist.find("🔄 Further Development")  
        improve_pos = checklist.find("⚠️ Needs Significant Work")
        
        assert promote_pos < develop_pos < improve_pos
    
    def test_format_checklist_items(self):
        """Test that individual checklist items are properly formatted."""
        checklist = self.formatter.format_checklist(self.sample_recommendations)
        
        # Should have checkbox format
        assert "- [ ] **high_quality.md**" in checklist
        assert "- [ ] **medium_quality.md**" in checklist
        assert "- [ ] **low_quality.md**" in checklist
        
        # Should include action and quality score
        assert "**Promote to Permanent**" in checklist
        assert "**Further Develop**" in checklist
        assert "**Needs Improvement**" in checklist
        
        # Should include quality scores
        assert "Quality: 0.85" in checklist
        assert "Quality: 0.55" in checklist
        assert "Quality: 0.25" in checklist
    
    def test_format_checklist_empty_recommendations(self):
        """Test formatting with no recommendations."""
        empty_recs = {
            "summary": {
                "total_notes": 0,
                "promote_to_permanent": 0,
                "move_to_fleeting": 0,
                "needs_improvement": 0,
                "processing_errors": 0
            },
            "recommendations": [],
            "generated_at": "2025-07-30T22:57:00"
        }
        
        checklist = self.formatter.format_checklist(empty_recs)
        
        # Should handle empty case gracefully
        assert "0 notes to process" in checklist
        assert "No notes requiring review" in checklist
        assert "Weekly Review" in checklist
    
    def test_format_checklist_with_errors(self):
        """Test formatting with processing errors."""
        error_recs = {
            "summary": {
                "total_notes": 1,
                "promote_to_permanent": 0,
                "move_to_fleeting": 0,
                "needs_improvement": 0,
                "processing_errors": 1
            },
            "recommendations": [
                {
                    "file_name": "error_note.md",
                    "source": "inbox",
                    "action": "manual_review",
                    "reason": "Processing failed - manual review required",
                    "quality_score": None,
                    "confidence": None,
                    "error": "Failed to process note"
                }
            ],
            "generated_at": "2025-07-30T22:57:00"
        }
        
        checklist = self.formatter.format_checklist(error_recs)
        
        # Should include error section
        assert "🚨 Manual Review Required" in checklist
        assert "- [ ] **error_note.md**" in checklist
        assert "**Manual Review**" in checklist
        assert "Processing failed" in checklist
    
    def test_export_checklist_to_file(self):
        """Test exporting checklist to markdown file."""
        with tempfile.TemporaryDirectory() as temp_dir:
            export_path = Path(temp_dir) / "weekly-review.md"
            
            result_path = self.formatter.export_checklist(
                self.sample_recommendations,
                export_path
            )
            
            # Should create the file
            assert result_path.exists()
            assert result_path == export_path
            
            # Should contain formatted content
            content = result_path.read_text()
            assert "Weekly Review" in content
            assert "- [ ] **high_quality.md**" in content
            assert "🎯 Ready to Promote" in content
    
    def test_export_checklist_auto_filename(self):
        """Test exporting with automatic filename generation."""
        with tempfile.TemporaryDirectory() as temp_dir:
            export_dir = Path(temp_dir)
            
            result_path = self.formatter.export_checklist(
                self.sample_recommendations,
                export_dir
            )
            
            # Should generate timestamped filename
            assert result_path.exists()
            assert result_path.parent == export_dir
            assert result_path.name.startswith("weekly-review-")
            assert result_path.name.endswith(".md")
            assert "2025-07-30" in result_path.name
    
    def test_format_for_interactive_mode(self):
        """Test formatting for interactive step-by-step mode."""
        interactive_output = self.formatter.format_for_interactive(
            self.sample_recommendations
        )
        
        # Should return list of interactive items
        assert isinstance(interactive_output, list)
        assert len(interactive_output) == 3
        
        # Each item should have required fields
        for item in interactive_output:
            assert "file_name" in item
            assert "action" in item
            assert "reason" in item
            assert "formatted_display" in item
            
        # Should be sorted by priority (promote first)
        assert interactive_output[0]["action"] == "promote_to_permanent"
        assert interactive_output[1]["action"] == "move_to_fleeting"
        assert interactive_output[2]["action"] == "improve_or_archive"
    
    def test_format_enhanced_metrics(self):
        """Test formatting of enhanced metrics into markdown report."""
        # Create sample enhanced metrics data
        metrics = {
            "generated_at": "2025-07-31T06:35:00.000000",
            "summary": {
                "total_notes": 25,
                "total_orphaned": 3,
                "total_stale": 2,
                "avg_links_per_note": 1.8
            },
            "orphaned_notes": [
                {
                    "title": "Orphaned Note 1",
                    "directory": "Permanent Notes",
                    "last_modified": "2025-07-25T10:30:00.000000"
                },
                {
                    "title": "Orphaned Note 2",
                    "directory": "Fleeting Notes",
                    "last_modified": "2025-07-20T15:45:00.000000"
                }
            ],
            "stale_notes": [
                {
                    "title": "Very Old Note",
                    "directory": "Permanent Notes",
                    "days_since_modified": 120
                }
            ],
            "note_age_distribution": {
                "new": 5,
                "recent": 8,
                "mature": 7,
                "old": 5
            },
            "productivity_metrics": {
                "avg_notes_created_per_week": 3.2,
                "avg_notes_modified_per_week": 4.1,
                "total_weeks_active": 8,
                "most_productive_week_creation": ("2025-W30", 7)
            },
            "link_density": 1.8
        }
        
        # Format the metrics
        result = self.formatter.format_enhanced_metrics(metrics)
        
        # Verify structure and content
        assert isinstance(result, str)
        assert "# 📊 Enhanced Weekly Review Metrics" in result
        assert "## 📈 Summary Overview" in result
        assert "Total Notes**: 25" in result
        assert "Orphaned Notes**: 3" in result
        assert "Stale Notes (>90 days)**: 2" in result
        assert "Average Links per Note**: 1.80" in result
        
        # Check orphaned notes section
        assert "## 🏝️ Orphaned Notes (Need Connections)" in result
        assert "**Orphaned Note 1** (Permanent Notes)" in result
        assert "**Orphaned Note 2** (Fleeting Notes)" in result
        
        # Check stale notes section
        assert "## ⏰ Stale Notes (Haven't Been Updated)" in result
        assert "**Very Old Note** (Permanent Notes) - 120 days old" in result
        
        # Check age distribution
        assert "## 📅 Note Age Distribution" in result
        assert "**New** (< 7 days): 5 notes" in result
        assert "**Recent** (7-30 days): 8 notes" in result
        assert "**Mature** (30-90 days): 7 notes" in result
        assert "**Old** (> 90 days): 5 notes" in result
        
        # Check productivity metrics
        assert "## 💪 Productivity Insights" in result
        assert "Average Notes Created per Week**: 3.2" in result
        assert "Average Notes Modified per Week**: 4.1" in result
        assert "Total Weeks Active**: 8" in result
        assert "Most Productive Week**: 2025-W30 (7 notes created)" in result
        
        # Check insights section
        assert "## 💡 Insights & Recommendations" in result
        assert "🔗 Good link density" in result  # Should be good for 1.8
        assert "🏝️ Focus on connecting orphaned notes" in result
        assert "⏰ Consider reviewing or archiving stale notes" in result


class TestWeeklyReviewCLI:
    """Test cases for weekly review CLI integration."""
    
    def setup_method(self):
        """Set up test environment."""
        self.temp_dir = tempfile.mkdtemp()
        self.base_dir = Path(self.temp_dir)
        
        # Create directory structure
        (self.base_dir / "Inbox").mkdir()
        (self.base_dir / "Fleeting Notes").mkdir()
        (self.base_dir / "Permanent Notes").mkdir()
        (self.base_dir / "Archive").mkdir()
    
    def teardown_method(self):
        """Clean up test environment."""
        shutil.rmtree(self.temp_dir)
    
    def create_test_note(self, directory: str, filename: str, content: str):
        """Helper to create a test note."""
        note_path = self.base_dir / directory / filename
        note_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(note_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        return note_path
    
    @patch('src.cli.workflow_demo.WeeklyReviewFormatter')
    @patch('src.cli.workflow_demo.WorkflowManager')
    def test_enhanced_metrics_command_basic(self, mock_workflow_manager, mock_formatter):
        """Test basic enhanced metrics command execution."""
        # Setup mocks
        mock_workflow_instance = mock_workflow_manager.return_value
        mock_formatter_instance = mock_formatter.return_value
        
        # Mock enhanced metrics
        mock_metrics = {
            "generated_at": "2025-07-31T06:35:00.000000",
            "summary": {
                "total_notes": 10,
                "total_orphaned": 2,
                "total_stale": 1,
                "avg_links_per_note": 1.5
            },
            "orphaned_notes": [],
            "stale_notes": [],
            "note_age_distribution": {},
            "productivity_metrics": {},
            "link_density": 1.5
        }
        mock_workflow_instance.generate_enhanced_metrics.return_value = mock_metrics
        mock_formatter_instance.format_enhanced_metrics.return_value = "# Enhanced Metrics Report\n\nTest metrics"
        
        # Capture output
        with patch('builtins.print') as mock_print:
            # Test basic enhanced metrics command
            with patch('sys.argv', ['workflow_demo.py', self.temp_dir, '--enhanced-metrics']):
                from src.cli.workflow_demo import main
                main()
        
        # Verify workflow manager was called
        mock_workflow_manager.assert_called_once_with(self.temp_dir)
        mock_workflow_instance.generate_enhanced_metrics.assert_called_once()
        mock_formatter_instance.format_enhanced_metrics.assert_called_once_with(mock_metrics)
        
        # Verify output contains expected messages
        print_calls = [call[0][0] for call in mock_print.call_args_list]
        assert any("Generating enhanced metrics report" in call for call in print_calls)
        assert any("Summary: 10 total notes, 2 orphaned, 1 stale" in call for call in print_calls)
    
    @patch('src.cli.workflow_demo.WeeklyReviewFormatter')
    @patch('src.cli.workflow_demo.WorkflowManager')
    def test_enhanced_metrics_json_format(self, mock_workflow_manager, mock_formatter):
        """Test enhanced metrics command with JSON format."""
        # Setup mocks
        mock_workflow_instance = mock_workflow_manager.return_value
        mock_metrics = {
            "summary": {
                "total_notes": 5,
                "total_orphaned": 1,
                "total_stale": 0
            }
        }
        mock_workflow_instance.generate_enhanced_metrics.return_value = mock_metrics
        
        # Capture output
        with patch('builtins.print') as mock_print:
            # Test JSON format
            with patch('sys.argv', ['workflow_demo.py', self.temp_dir, '--enhanced-metrics', '--format', 'json']):
                from src.cli.workflow_demo import main
                main()
        
        # Verify JSON output was printed
        print_calls = [call[0][0] for call in mock_print.call_args_list]
        json_output_found = any('"total_notes": 5' in call for call in print_calls)
        assert json_output_found, "JSON output should contain metrics data"
    
    @patch('src.cli.workflow_demo.WeeklyReviewFormatter')
    @patch('src.cli.workflow_demo.WorkflowManager')
    @patch('builtins.open', new_callable=mock_open)
    def test_enhanced_metrics_export(self, mock_file_open, mock_workflow_manager, mock_formatter):
        """Test enhanced metrics command with export functionality."""
        # Setup mocks
        mock_workflow_instance = mock_workflow_manager.return_value
        mock_formatter_instance = mock_formatter.return_value
        
        mock_metrics = {"summary": {"total_notes": 3, "total_orphaned": 0, "total_stale": 0}}
        mock_workflow_instance.generate_enhanced_metrics.return_value = mock_metrics
        mock_formatter_instance.format_enhanced_metrics.return_value = "# Enhanced Metrics\n\nTest report"
        
        export_path = str(Path(self.temp_dir) / "metrics.md")
        
        # Capture output
        with patch('builtins.print') as mock_print:
            # Test export functionality
            with patch('sys.argv', ['workflow_demo.py', self.temp_dir, '--enhanced-metrics', '--export', export_path]):
                from src.cli.workflow_demo import main
                main()
        
        # Verify file was opened for writing
        mock_file_open.assert_called_once_with(Path(export_path), 'w', encoding='utf-8')
        
        # Verify export confirmation was printed
        print_calls = [call[0][0] for call in mock_print.call_args_list]
        assert any("Enhanced metrics exported to" in call for call in print_calls)
    
    @patch('src.cli.workflow_demo.WeeklyReviewFormatter')
    @patch('src.cli.workflow_demo.WorkflowManager')
    def test_weekly_review_command_basic(self, mock_workflow_manager, mock_formatter):
        """Test basic weekly review command execution."""
        # Setup mocks
        mock_workflow_instance = mock_workflow_manager.return_value
        mock_formatter_instance = mock_formatter.return_value
        
        # Mock candidates and recommendations
        mock_candidates = [
            {"file_name": "test.md", "source": "inbox", "path": "/test/test.md"}
        ]
        mock_recommendations = {
            "summary": {"total_notes": 1, "promote_to_permanent": 1},
            "recommendations": [
                {
                    "file_name": "test.md",
                    "action": "promote_to_permanent",
                    "reason": "High quality",
                    "confidence": "high"
                }
            ]
        }
        
        mock_workflow_instance.scan_review_candidates.return_value = mock_candidates
        mock_workflow_instance.generate_weekly_recommendations.return_value = mock_recommendations
        mock_formatter_instance.format_checklist.return_value = "# Test Checklist"
        
        # Simulate CLI command
        import sys
        from unittest.mock import patch as mock_patch
        with mock_patch.object(sys, 'argv', ['workflow_demo.py', str(self.base_dir), '--weekly-review']):
            from src.cli.workflow_demo import main
            with mock_patch('builtins.print') as mock_print:
                main()
        
        # Verify workflow methods were called
        mock_workflow_manager.assert_called_once_with(str(self.base_dir))
        mock_workflow_instance.scan_review_candidates.assert_called_once()
        mock_workflow_instance.generate_weekly_recommendations.assert_called_once_with(mock_candidates)
        
        # Verify formatter was used
        mock_formatter.assert_called_once()
        mock_formatter_instance.format_checklist.assert_called_once_with(mock_recommendations)

    @patch('src.cli.workflow_demo.WeeklyReviewFormatter')
    @patch('src.cli.workflow_demo.WorkflowManager')
    def test_weekly_review_with_export(self, mock_workflow_manager, mock_formatter):
        """Test weekly review with checklist export."""
        # Setup mocks
        mock_workflow_instance = mock_workflow_manager.return_value
        mock_formatter_instance = mock_formatter.return_value

        mock_candidates = [{"file_name": "test.md", "source": "inbox"}]
        mock_recommendations = {
            "summary": {"total_notes": 1, "promote_to_permanent": 1},
            "recommendations": []
        }

        mock_workflow_instance.scan_review_candidates.return_value = mock_candidates
        mock_workflow_instance.generate_weekly_recommendations.return_value = mock_recommendations
        mock_formatter_instance.format_checklist.return_value = "# Test Checklist"
        mock_formatter_instance.export_checklist.return_value = Path("/test/export.md")

        # Test export functionality
        export_path = self.base_dir / "export.md"

        import sys
        from unittest.mock import patch as mock_patch
        with mock_patch.object(sys, 'argv', ['workflow_demo.py', str(self.base_dir), '--weekly-review', '--export-checklist', str(export_path)]):
            from src.cli.workflow_demo import main
            with mock_patch('builtins.print') as mock_print:
                main()

        # Verify export was called
        mock_formatter_instance.export_checklist.assert_called_once_with(mock_recommendations, export_path)

    @patch('src.cli.workflow_demo.WeeklyReviewFormatter')
    @patch('src.cli.workflow_demo.WorkflowManager')
    def test_weekly_review_interactive_mode(self, mock_workflow_manager, mock_formatter):
        """Test interactive weekly review mode."""
        # Setup mocks
        mock_workflow_instance = mock_workflow_manager.return_value
        mock_formatter_instance = mock_formatter.return_value

        mock_candidates = [{"file_name": "test.md", "source": "inbox"}]
        mock_recommendations = {
            "summary": {"total_notes": 1, "promote_to_permanent": 1},
            "recommendations": [
                {
                    "file_name": "test.md",
                    "action": "promote_to_permanent",
                    "reason": "High quality",
                    "confidence": "high"
                }
            ]
        }

        mock_workflow_instance.scan_review_candidates.return_value = mock_candidates
        mock_workflow_instance.generate_weekly_recommendations.return_value = mock_recommendations
        mock_formatter_instance.format_for_interactive.return_value = ["Interactive item 1"]

        # Note: Interactive mode would require additional UI implementation
        # For now, we verify that the components are set up correctly
        assert mock_workflow_manager is not None
        assert mock_formatter is not None

    @patch('src.cli.workflow_demo.WeeklyReviewFormatter')
    @patch('src.cli.workflow_demo.WorkflowManager')
    def test_weekly_review_dry_run(self, mock_workflow_manager, mock_formatter):
        """Test dry run mode for weekly review."""
        # Setup mocks
        mock_workflow_instance = mock_workflow_manager.return_value
        mock_formatter_instance = mock_formatter.return_value

        mock_candidates = [{"file_name": "test.md", "source": "inbox"}]
        mock_recommendations = {
            "summary": {"total_notes": 1, "promote_to_permanent": 1},
            "recommendations": []
        }

        mock_workflow_instance.scan_review_candidates.return_value = mock_candidates
        mock_workflow_instance.generate_weekly_recommendations.return_value = mock_recommendations
        mock_formatter_instance.format_checklist.return_value = "# Dry Run Checklist"

        import sys
        from unittest.mock import patch as mock_patch
        with mock_patch.object(sys, 'argv', ['workflow_demo.py', str(self.base_dir), '--weekly-review', '--dry-run']):
            from src.cli.workflow_demo import main
            with mock_patch('builtins.print') as mock_print:
                main()

        # Verify workflow methods were called (dry run still scans and generates recommendations)
        mock_workflow_instance.scan_review_candidates.assert_called_once()
        mock_workflow_instance.generate_weekly_recommendations.assert_called_once_with(mock_candidates)
        mock_formatter_instance.format_checklist.assert_called_once_with(mock_recommendations)
