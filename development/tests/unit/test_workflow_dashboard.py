#!/usr/bin/env python3
"""
TDD Iteration 1: Workflow Dashboard - RED Phase Tests

Tests for Interactive Terminal UI Dashboard for Workflow Operations
Focus: P0.1 - Inbox Status Panel Integration
"""

import sys
import json
import unittest
from unittest.mock import Mock, patch
from pathlib import Path

# Add development directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))


class TestWorkflowDashboardInboxStatus(unittest.TestCase):
    """
    RED Phase Tests for Inbox Status Panel
    
    These tests will FAIL until we implement workflow_dashboard.py
    
    Test Coverage:
    1. CLI integration - calling core_workflow_cli.py
    2. JSON parsing - extracting inbox count from status output
    3. Status panel display - rendering inbox metrics
    4. Error handling - graceful failures
    """
    
    def setUp(self):
        """Set up test fixtures"""
        self.vault_path = "/test/vault"
        
        # Mock JSON response from core_workflow_cli.py status --format json
        self.mock_status_json = {
            "workflow_status": {
                "inbox_count": 60,
                "fleeting_count": 0,
                "permanent_count": 142,
                "literature_count": 18
            },
            "ai_features": {
                "summarization": True,
                "connections": True,
                "tagging": True
            },
            "recommendations": [
                "Process 60 inbox notes",
                "All fleeting notes processed"
            ]
        }
    
    @patch('subprocess.run')
    def test_fetch_inbox_status_from_cli(self, mock_run):
        """
        Test fetching inbox status via core_workflow_cli.py
        
        RED: This will fail - workflow_dashboard.py doesn't exist yet
        """
        # Mock CLI response
        mock_run.return_value = Mock(
            returncode=0,
            stdout=json.dumps(self.mock_status_json),
            stderr=""
        )
        
        # Import will fail - that's expected in RED phase
        try:
            from src.cli.workflow_dashboard import WorkflowDashboard
            
            dashboard = WorkflowDashboard(vault_path=self.vault_path)
            status = dashboard.fetch_inbox_status()
            
            # Verify CLI was called correctly
            mock_run.assert_called_once()
            call_args = mock_run.call_args
            # call_args[0][0] is the command list
            cmd_str = ' '.join(call_args[0][0])
            self.assertIn('core_workflow_cli.py', cmd_str)
            self.assertIn('status', cmd_str)
            self.assertIn('--format', cmd_str)
            self.assertIn('json', cmd_str)
            
            # Verify parsed data
            self.assertEqual(status['inbox_count'], 60)
            self.assertEqual(status['fleeting_count'], 0)
            
        except ImportError as e:
            # Expected to fail in RED phase
            self.fail(f"RED Phase: workflow_dashboard.py not implemented yet - {e}")
    
    @patch('subprocess.run')
    def test_parse_inbox_count_from_status(self, mock_run):
        """
        Test parsing inbox count from CLI JSON output
        
        RED: This will fail - WorkflowDashboard doesn't exist yet
        """
        mock_run.return_value = Mock(
            returncode=0,
            stdout=json.dumps(self.mock_status_json),
            stderr=""
        )
        
        try:
            from src.cli.workflow_dashboard import WorkflowDashboard
            
            dashboard = WorkflowDashboard(vault_path=self.vault_path)
            inbox_count = dashboard.get_inbox_count()
            
            self.assertEqual(inbox_count, 60)
            
        except ImportError:
            self.fail("RED Phase: WorkflowDashboard class not implemented")
    
    @patch('subprocess.run')
    def test_render_inbox_status_panel(self, mock_run):
        """
        Test rendering inbox status panel with Rich formatting
        
        RED: This will fail - StatusPanelRenderer doesn't exist yet
        """
        mock_run.return_value = Mock(
            returncode=0,
            stdout=json.dumps(self.mock_status_json),
            stderr=""
        )
        
        try:
            from src.cli.workflow_dashboard import WorkflowDashboard
            
            dashboard = WorkflowDashboard(vault_path=self.vault_path)
            panel_content = dashboard.render_inbox_panel()
            
            # Verify panel contains expected data
            self.assertIsNotNone(panel_content)
            # Panel should be Rich renderable or string
            self.assertTrue(
                hasattr(panel_content, '__rich__') or isinstance(panel_content, str)
            )
            
        except (ImportError, AttributeError) as e:
            self.fail(f"RED Phase: render_inbox_panel not implemented - {e}")
    
    @patch('subprocess.run')
    def test_cli_error_handling(self, mock_run):
        """
        Test graceful handling of CLI errors
        
        RED: This will fail - error handling not implemented yet
        """
        # Mock CLI failure
        mock_run.return_value = Mock(
            returncode=1,
            stdout="",
            stderr="Error: Vault not found"
        )
        
        try:
            from src.cli.workflow_dashboard import WorkflowDashboard
            
            dashboard = WorkflowDashboard(vault_path=self.vault_path)
            status = dashboard.fetch_inbox_status()
            
            # Should return error structure, not raise exception
            self.assertIn('error', status)
            self.assertTrue(status['error'])
            
        except ImportError:
            self.fail("RED Phase: WorkflowDashboard not implemented")
    
    @patch('subprocess.run')
    def test_health_indicator_coloring(self, mock_run):
        """
        Test health indicator color coding based on inbox count
        
        RED: This will fail - health indicator logic doesn't exist yet
        
        Rules:
        - 🟢 Green: 0-20 notes
        - 🟡 Yellow: 21-50 notes
        - 🔴 Red: 51+ notes
        """
        mock_run.return_value = Mock(
            returncode=0,
            stdout=json.dumps(self.mock_status_json),
            stderr=""
        )
        
        try:
            from src.cli.workflow_dashboard import WorkflowDashboard
            
            dashboard = WorkflowDashboard(vault_path=self.vault_path)
            
            # Test red status (60 notes)
            indicator = dashboard.get_inbox_health_indicator(60)
            self.assertIn('🔴', indicator)
            
            # Test yellow status (30 notes)
            indicator = dashboard.get_inbox_health_indicator(30)
            self.assertIn('🟡', indicator)
            
            # Test green status (10 notes)
            indicator = dashboard.get_inbox_health_indicator(10)
            self.assertIn('🟢', indicator)
            
        except (ImportError, AttributeError):
            self.fail("RED Phase: Health indicator not implemented")


class TestCLIIntegrator(unittest.TestCase):
    """
    RED Phase Tests for CLI Integration Utility
    
    Tests the utility class for calling dedicated CLIs
    """
    
    @patch('subprocess.run')
    def test_call_core_workflow_status(self, mock_run):
        """
        Test CLIIntegrator can call core_workflow_cli.py
        
        RED: This will fail - CLIIntegrator doesn't exist yet
        """
        mock_run.return_value = Mock(
            returncode=0,
            stdout='{"status": "ok"}',
            stderr=""
        )
        
        try:
            from src.cli.workflow_dashboard_utils import CLIIntegrator
            
            integrator = CLIIntegrator()
            result = integrator.call_cli('core_workflow_cli.py', ['status', '--format', 'json'])
            
            self.assertEqual(result['returncode'], 0)
            self.assertIn('status', result['data'])
            
        except ImportError:
            self.fail("RED Phase: CLIIntegrator not implemented")
    
    @patch('subprocess.run')
    def test_parse_json_output(self, mock_run):
        """
        Test CLIIntegrator parses JSON output correctly
        
        RED: This will fail - JSON parsing not implemented yet
        """
        test_data = {"inbox_count": 42}
        mock_run.return_value = Mock(
            returncode=0,
            stdout=json.dumps(test_data),
            stderr=""
        )
        
        try:
            from src.cli.workflow_dashboard_utils import CLIIntegrator
            
            integrator = CLIIntegrator()
            result = integrator.call_cli('core_workflow_cli.py', ['status', '--format', 'json'])
            
            self.assertEqual(result['data']['inbox_count'], 42)
            
        except ImportError:
            self.fail("RED Phase: CLIIntegrator JSON parsing not implemented")


class TestStatusPanelRenderer(unittest.TestCase):
    """
    RED Phase Tests for Status Panel Rendering
    
    Tests the utility class for rendering Rich panels
    """
    
    def test_create_inbox_panel(self):
        """
        Test creating inbox status panel with Rich
        
        RED: This will fail - StatusPanelRenderer doesn't exist yet
        """
        try:
            from src.cli.workflow_dashboard_utils import StatusPanelRenderer
            
            renderer = StatusPanelRenderer()
            panel = renderer.create_inbox_panel(
                inbox_count=60,
                oldest_age_days=240,
                health_indicator="🔴"
            )
            
            self.assertIsNotNone(panel)
            # Should be Rich Panel object or string fallback
            # Check if it's a Panel by class name or if it's a string
            is_rich_panel = (
                hasattr(panel, '__rich_console__') or 
                hasattr(panel, '__rich__') or
                panel.__class__.__name__ == 'Panel' or
                'rich.panel.Panel' in str(type(panel))
            )
            is_string_fallback = isinstance(panel, str)
            
            self.assertTrue(
                is_rich_panel or is_string_fallback,
                f"Panel should be Rich Panel or string, got {type(panel)}"
            )
            
        except ImportError:
            self.fail("RED Phase: StatusPanelRenderer not implemented")
    
    def test_panel_contains_metrics(self):
        """
        Test panel contains all required metrics
        
        RED: This will fail - panel rendering not implemented yet
        """
        try:
            from src.cli.workflow_dashboard_utils import StatusPanelRenderer
            
            renderer = StatusPanelRenderer()
            panel_text = renderer.format_inbox_metrics(
                inbox_count=60,
                oldest_age_days=240
            )
            
            self.assertIn('60', panel_text)
            self.assertIn('240', panel_text)
            
        except (ImportError, AttributeError):
            self.fail("RED Phase: Panel metrics formatting not implemented")


if __name__ == '__main__':
    # Run tests with verbose output to see RED phase failures
    unittest.main(verbosity=2)
