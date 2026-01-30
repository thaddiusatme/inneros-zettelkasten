import unittest
from unittest.mock import MagicMock, patch
from development.src.ai.agents.librarian import LibrarianAgent


class TestLibrarianAgent(unittest.TestCase):
    @patch("development.src.ai.agent.core.OpenAI")
    def test_librarian_initialization_and_run(self, mock_openai):
        # Setup mock response
        mock_client = MagicMock()
        mock_openai.return_value = mock_client

        # Mock the chat completion response
        mock_response = MagicMock()
        mock_message = MagicMock()
        mock_message.content = "I have organized the inbox."
        mock_message.tool_calls = None

        mock_response.choices = [MagicMock(message=mock_message)]
        mock_client.chat.completions.create.return_value = mock_response

        # Initialize agent
        agent = LibrarianAgent()

        # Run agent
        result = agent.run("Organize the inbox")

        # Verify
        self.assertEqual(result, "I have organized the inbox.")
        # Check that OpenAI was called
        mock_client.chat.completions.create.assert_called()

        # Check that tools were registered (Librarian should have specific tools)
        self.assertIsNotNone(agent.registry.get_tool("list_inbox_files"))
        self.assertIsNotNone(agent.registry.get_tool("read_note"))


if __name__ == "__main__":
    unittest.main()
