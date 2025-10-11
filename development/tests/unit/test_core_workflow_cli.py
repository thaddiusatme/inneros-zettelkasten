#!/usr/bin/env python3
"""
Test suite for Core Workflow CLI (TDD RED Phase - Iteration 4)

Tests the extraction of core workflow commands from workflow_demo.py:
- --status: Show workflow status
- --process-inbox: Process all inbox notes  
- --promote: Promote a note
- --report: Generate comprehensive workflow report

Manager: WorkflowManager (has all core methods)
"""

import unittest
import sys
from pathlib import Path
from unittest.mock import Mock, patch
import tempfile
import shutil


class TestCoreWorkflowCLI(unittest.TestCase):
    """Test suite for core workflow CLI commands"""
    
    def setUp(self):
        """Set up test environment with temp directory"""
        self.test_dir = Path(tempfile.mkdtemp())
        self.inbox_dir = self.test_dir / "Inbox"
        self.inbox_dir.mkdir()
        
        # Create test note
        self.test_note = self.inbox_dir / "test-note.md"
        self.test_note.write_text("""---
title: Test Note
type: fleeting
---

# Test Content
""")
    
    def tearDown(self):
        """Clean up test environment"""
        if self.test_dir.exists():
            shutil.rmtree(self.test_dir)
    
    def test_core_workflow_cli_import(self):
        """TEST 1: Verify core_workflow_cli module can be imported"""
        try:
            from src.cli.core_workflow_cli import CoreWorkflowCLI
            self.assertIsNotNone(CoreWorkflowCLI)
        except ImportError as e:
            self.fail(f"Failed to import CoreWorkflowCLI: {e}")
    
    def test_status_command_execution(self):
        """TEST 2: Verify status command executes successfully"""
        from src.cli.core_workflow_cli import CoreWorkflowCLI
        
        cli = CoreWorkflowCLI(vault_path=str(self.test_dir))
        
        # Execute status command
        exit_code = cli.status(output_format='normal')
        
        # Should execute without errors
        self.assertEqual(exit_code, 0)
    
    def test_process_inbox_command_execution(self):
        """TEST 3: Verify process-inbox command executes successfully"""
        from src.cli.core_workflow_cli import CoreWorkflowCLI
        
        cli = CoreWorkflowCLI(vault_path=str(self.test_dir))
        
        # Execute process-inbox command
        exit_code = cli.process_inbox(output_format='normal')
        
        # Should execute without errors
        self.assertEqual(exit_code, 0)
    
    def test_promote_command_execution(self):
        """TEST 4: Verify promote command executes successfully"""
        from src.cli.core_workflow_cli import CoreWorkflowCLI
        
        cli = CoreWorkflowCLI(vault_path=str(self.test_dir))
        
        # Execute promote command
        exit_code = cli.promote(
            note_path=str(self.test_note),
            target_type='permanent',
            output_format='normal'
        )
        
        # Should execute without errors
        self.assertEqual(exit_code, 0)
    
    def test_report_command_execution(self):
        """TEST 5: Verify report command executes successfully"""
        from src.cli.core_workflow_cli import CoreWorkflowCLI
        
        cli = CoreWorkflowCLI(vault_path=str(self.test_dir))
        
        # Execute report command
        exit_code = cli.report(output_format='normal', export_path=None)
        
        # Should execute without errors
        self.assertEqual(exit_code, 0)
    
    def test_json_output_format(self):
        """TEST 6: Verify JSON output format works for all commands"""
        from src.cli.core_workflow_cli import CoreWorkflowCLI
        
        cli = CoreWorkflowCLI(vault_path=str(self.test_dir))
        
        # Test status with JSON
        with patch('builtins.print') as mock_print:
            exit_code = cli.status(output_format='json')
            self.assertEqual(exit_code, 0)
            # Should have printed JSON output
            self.assertTrue(mock_print.called)
    
    def test_workflow_manager_integration(self):
        """TEST 7: Verify CLI integrates with WorkflowManager correctly"""
        from src.cli.core_workflow_cli import CoreWorkflowCLI
        
        cli = CoreWorkflowCLI(vault_path=str(self.test_dir))
        
        # Verify WorkflowManager is initialized
        self.assertIsNotNone(cli.workflow_manager)
        
        # Verify manager has required methods
        self.assertTrue(hasattr(cli.workflow_manager, 'generate_workflow_report'))
        self.assertTrue(hasattr(cli.workflow_manager, 'batch_process_inbox'))
        self.assertTrue(hasattr(cli.workflow_manager, 'promote_note'))


if __name__ == "__main__":
    unittest.main()
