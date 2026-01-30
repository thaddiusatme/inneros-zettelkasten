import unittest
import shutil
from pathlib import Path
from unittest.mock import MagicMock, patch
import tempfile
import os

from development.src.automation.daemon import AutomationDaemon
from development.src.automation.config import (
    DaemonConfig,
    AgentHandlerConfig,
    FileWatchConfig,
)
from development.src.automation.agent_handler import AgentEventHandler


class TestSystemIntegration(unittest.TestCase):
    def setUp(self):
        # Create a temporary directory for the vault
        self.test_dir = tempfile.mkdtemp()
        self.inbox_dir = Path(self.test_dir) / "knowledge" / "Inbox"
        self.inbox_dir.mkdir(parents=True, exist_ok=True)

    def tearDown(self):
        shutil.rmtree(self.test_dir)

    @patch("development.src.automation.daemon.PIDLock")
    @patch("development.src.automation.daemon.BackgroundScheduler")
    @patch("development.src.automation.daemon.FileWatcher")
    def test_daemon_initializes_agent_handler(
        self, mock_watcher, mock_scheduler, mock_pid
    ):
        # Configure Daemon with Agent Handler enabled
        config = DaemonConfig(
            pid_file=str(Path(self.test_dir) / "daemon.pid"),
            file_watching=FileWatchConfig(enabled=True, watch_path=str(self.inbox_dir)),
            agent_handler=AgentHandlerConfig(
                enabled=True, watch_path=str(self.inbox_dir)
            ),
        )

        daemon = AutomationDaemon(config=config)

        # Start daemon (mocks prevent actual execution)
        daemon.start()

        # Verify AgentHandler is initialized
        self.assertIsNotNone(daemon.agent_handler)
        self.assertIsInstance(daemon.agent_handler, AgentEventHandler)

        # Verify callback registration
        # We need to check if registser_callback was called with daemon.agent_handler.process
        # The mock_watcher instance is created inside start()
        watcher_instance = daemon.file_watcher
        self.assertTrue(watcher_instance.register_callback.called)

        # Check if one of the calls was with our handler
        calls = watcher_instance.register_callback.call_args_list
        # We might have other handlers (event_handler, etc)
        # Check if any call argument matches
        found = False
        for call in calls:
            callback = call[0][0]
            if callback == daemon.agent_handler.process:
                found = True
                break
        self.assertTrue(
            found, "AgentHandler.process was not registered with FileWatcher"
        )

        daemon.stop()

    @patch("development.src.ai.agent.core.OpenAI")
    @patch("development.src.ai.agents.librarian.LibrarianAgent.run")
    def test_agent_handler_process_flow(self, mock_agent_run, mock_openai):
        # Setup test file
        test_file = self.inbox_dir / "Librarian: Organize Me.md"
        test_file.write_text("# Request\nPlease organize this.", encoding="utf-8")

        # Mock Agent response
        mock_agent_run.return_value = "I have organized it."

        # Initialize handler
        config = {"enabled": True, "watch_path": str(self.inbox_dir)}
        handler = AgentEventHandler(config=config)

        # Simulate file creation event
        handler.process(test_file, "created")

        # Verify Agent was run
        mock_agent_run.assert_called_once()

        # Verify file content updated
        content = test_file.read_text(encoding="utf-8")
        self.assertIn("## Agent Response (Librarian)", content)
        self.assertIn("I have organized it.", content)


if __name__ == "__main__":
    unittest.main()
