"""
Unit tests for Fleeting Note Lifecycle Management (Phase 5.6 Extension)
Tests for US-1: Fleeting Note Age Detection functionality
"""

import unittest
from datetime import datetime, timedelta
from pathlib import Path
import tempfile
import shutil
import os

import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")))

from src.ai.workflow_manager import WorkflowManager


class TestFleetingLifecycle(unittest.TestCase):
    """Test suite for fleeting note lifecycle management features"""

    def setUp(self):
        """Set up test fixtures"""
        # Create temporary directory for test notes
        self.test_dir = tempfile.mkdtemp()
        self.fleeting_dir = Path(self.test_dir) / "Fleeting Notes"
        self.fleeting_dir.mkdir(parents=True, exist_ok=True)

        # Initialize WorkflowManager
        self.workflow = WorkflowManager(self.test_dir)

    def tearDown(self):
        """Clean up test fixtures"""
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)

    def _create_test_note(self, name: str, days_old: int, content: str = None) -> Path:
        """Helper to create a test fleeting note with specific age"""
        note_path = self.fleeting_dir / name

        # Calculate timestamp for note age
        created_time = datetime.now() - timedelta(days=days_old)
        created_str = created_time.strftime("%Y-%m-%d %H:%M")

        # Default content with YAML frontmatter
        if content is None:
            content = f"""---
type: fleeting
created: {created_str}
status: inbox
tags: [test-note]
---

# Test Note

This is a test fleeting note created {days_old} days ago.
"""

        note_path.write_text(content)

        # Set file modification time to match created date
        mod_time = created_time.timestamp()
        os.utime(note_path, (mod_time, mod_time))

        return note_path

    # ============= RED PHASE: Tests for FleetingAnalysis Data Structure =============

    def test_fleeting_analysis_data_structure(self):
        """Test that FleetingAnalysis data structure exists and contains required fields"""
        # Create test notes of various ages
        self._create_test_note("new-note.md", 3)  # New (0-7 days)
        self._create_test_note("recent-note.md", 15)  # Recent (8-30 days)
        self._create_test_note("stale-note.md", 45)  # Stale (31-90 days)
        self._create_test_note("old-note.md", 120)  # Old (90+ days)

        # This should fail in RED phase - method doesn't exist yet
        analysis = self.workflow.analyze_fleeting_notes()

        # Verify FleetingAnalysis structure
        self.assertIsNotNone(analysis)
        self.assertTrue(hasattr(analysis, "total_count"))
        self.assertTrue(hasattr(analysis, "age_distribution"))
        self.assertTrue(hasattr(analysis, "oldest_note"))
        self.assertTrue(hasattr(analysis, "newest_note"))
        self.assertTrue(hasattr(analysis, "notes_by_age"))

        # Verify age distribution categories
        self.assertIn("new", analysis.age_distribution)  # 0-7 days
        self.assertIn("recent", analysis.age_distribution)  # 8-30 days
        self.assertIn("stale", analysis.age_distribution)  # 31-90 days
        self.assertIn("old", analysis.age_distribution)  # 90+ days

    # ============= RED PHASE: Tests for analyze_fleeting_notes() Method =============

    def test_analyze_fleeting_notes_empty_directory(self):
        """Test analysis when no fleeting notes exist"""
        # This should fail in RED phase - method doesn't exist yet
        analysis = self.workflow.analyze_fleeting_notes()

        self.assertEqual(analysis.total_count, 0)
        self.assertEqual(analysis.age_distribution["new"], 0)
        self.assertEqual(analysis.age_distribution["recent"], 0)
        self.assertEqual(analysis.age_distribution["stale"], 0)
        self.assertEqual(analysis.age_distribution["old"], 0)
        self.assertIsNone(analysis.oldest_note)
        self.assertIsNone(analysis.newest_note)

    def test_analyze_fleeting_notes_age_categorization(self):
        """Test correct categorization of notes by age"""
        # Create notes in each age category
        self._create_test_note("new1.md", 2)
        self._create_test_note("new2.md", 5)
        self._create_test_note("recent1.md", 10)
        self._create_test_note("recent2.md", 25)
        self._create_test_note("stale1.md", 35)
        self._create_test_note("stale2.md", 60)
        self._create_test_note("old1.md", 95)
        self._create_test_note("old2.md", 150)

        # This should fail in RED phase - method doesn't exist yet
        analysis = self.workflow.analyze_fleeting_notes()

        # Verify counts
        self.assertEqual(analysis.total_count, 8)
        self.assertEqual(analysis.age_distribution["new"], 2)
        self.assertEqual(analysis.age_distribution["recent"], 2)
        self.assertEqual(analysis.age_distribution["stale"], 2)
        self.assertEqual(analysis.age_distribution["old"], 2)

    def test_analyze_fleeting_notes_identifies_oldest_newest(self):
        """Test identification of oldest and newest fleeting notes"""
        # Create notes with specific ages
        self._create_test_note("newest.md", 1)
        self._create_test_note("middle.md", 30)
        self._create_test_note("oldest.md", 180)

        # This should fail in RED phase - method doesn't exist yet
        analysis = self.workflow.analyze_fleeting_notes()

        # Verify oldest and newest detection
        self.assertIsNotNone(analysis.oldest_note)
        self.assertIsNotNone(analysis.newest_note)
        self.assertEqual(analysis.oldest_note["name"], "oldest.md")
        self.assertEqual(analysis.oldest_note["days_old"], 180)
        self.assertEqual(analysis.newest_note["name"], "newest.md")
        self.assertEqual(analysis.newest_note["days_old"], 1)

    def test_analyze_fleeting_notes_performance(self):
        """Test performance meets <3 second target for 100+ notes"""
        import time

        # Create 100 test notes with varying ages
        for i in range(100):
            age = i % 120  # Distribute ages from 0-119 days
            self._create_test_note(f"note-{i:03d}.md", age)

        # Measure execution time
        start_time = time.time()

        # This should fail in RED phase - method doesn't exist yet
        analysis = self.workflow.analyze_fleeting_notes()

        execution_time = time.time() - start_time

        # Verify performance target
        self.assertLess(
            execution_time,
            3.0,
            f"Analysis took {execution_time:.2f}s, exceeding 3s target",
        )
        self.assertEqual(analysis.total_count, 100)

    # ============= RED PHASE: Tests for generate_fleeting_health_report() Method =============

    def test_generate_fleeting_health_report_structure(self):
        """Test health report generation with proper structure"""
        # Create diverse test data
        self._create_test_note("new.md", 3)
        self._create_test_note("stale.md", 45)
        self._create_test_note("old.md", 120)

        # This should fail in RED phase - method doesn't exist yet
        report = self.workflow.generate_fleeting_health_report()

        # Verify report structure
        self.assertIsInstance(report, dict)
        self.assertIn("summary", report)
        self.assertIn("health_status", report)
        self.assertIn("age_distribution", report)
        self.assertIn("recommendations", report)
        self.assertIn("oldest_notes", report)
        self.assertIn("newest_notes", report)

        # Verify health status calculation
        self.assertIn(report["health_status"], ["HEALTHY", "ATTENTION", "CRITICAL"])

    def test_fleeting_health_report_healthy_status(self):
        """Test health report shows HEALTHY when most notes are new/recent"""
        # Create mostly new and recent notes
        for i in range(5):
            self._create_test_note(f"new-{i}.md", i + 1)  # 5 new notes
        for i in range(3):
            self._create_test_note(f"recent-{i}.md", i + 10)  # 3 recent notes
        self._create_test_note("stale.md", 45)  # 1 stale note

        # This should fail in RED phase - method doesn't exist yet
        report = self.workflow.generate_fleeting_health_report()

        # Should be healthy with majority new/recent
        self.assertEqual(report["health_status"], "HEALTHY")
        self.assertIn("healthy", report["summary"].lower())

    def test_fleeting_health_report_attention_status(self):
        """Test health report shows ATTENTION when many notes are stale"""
        # Create mix with many stale notes
        self._create_test_note("new.md", 3)
        self._create_test_note("recent.md", 15)
        for i in range(5):
            self._create_test_note(f"stale-{i}.md", 35 + i * 10)  # 5 stale notes
        self._create_test_note("old.md", 100)

        # This should fail in RED phase - method doesn't exist yet
        report = self.workflow.generate_fleeting_health_report()

        # Should need attention with many stale notes
        self.assertEqual(report["health_status"], "ATTENTION")
        self.assertIn("attention", report["summary"].lower())

    def test_fleeting_health_report_critical_status(self):
        """Test health report shows CRITICAL when majority are old"""
        # Create mostly old notes
        self._create_test_note("new.md", 5)
        for i in range(10):
            self._create_test_note(f"old-{i}.md", 95 + i * 10)  # 10 old notes

        # This should fail in RED phase - method doesn't exist yet
        report = self.workflow.generate_fleeting_health_report()

        # Should be critical with majority old
        self.assertEqual(report["health_status"], "CRITICAL")
        self.assertIn("critical", report["summary"].lower())

    def test_fleeting_health_report_recommendations(self):
        """Test that health report provides actionable recommendations"""
        # Create notes requiring different actions
        self._create_test_note("new.md", 3)
        for i in range(3):
            self._create_test_note(f"stale-{i}.md", 40 + i * 5)
        for i in range(2):
            self._create_test_note(f"old-{i}.md", 100 + i * 20)

        # This should fail in RED phase - method doesn't exist yet
        report = self.workflow.generate_fleeting_health_report()

        # Verify recommendations exist and are actionable
        self.assertIsInstance(report["recommendations"], list)
        self.assertGreater(len(report["recommendations"]), 0)

        # Should recommend processing stale/old notes
        recommendations_text = " ".join(report["recommendations"]).lower()
        self.assertIn("process", recommendations_text)
        self.assertIn("old", recommendations_text)

    def test_fleeting_health_report_lists_oldest_notes(self):
        """Test that health report lists the oldest notes for priority processing"""
        # Create notes with clear age ordering
        notes = [
            ("oldest.md", 200),
            ("second-oldest.md", 150),
            ("third-oldest.md", 100),
            ("middle.md", 50),
            ("newer.md", 20),
            ("newest.md", 5),
        ]

        for name, age in notes:
            self._create_test_note(name, age)

        # This should fail in RED phase - method doesn't exist yet
        report = self.workflow.generate_fleeting_health_report()

        # Should list oldest notes (top 5)
        self.assertIsInstance(report["oldest_notes"], list)
        self.assertLessEqual(len(report["oldest_notes"]), 5)

        # Verify ordering (oldest first)
        if len(report["oldest_notes"]) > 1:
            first = report["oldest_notes"][0]
            second = report["oldest_notes"][1]
            self.assertGreater(first["days_old"], second["days_old"])


if __name__ == "__main__":
    unittest.main()
