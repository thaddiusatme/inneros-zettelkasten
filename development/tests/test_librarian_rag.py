import unittest
from unittest.mock import MagicMock, patch
from development.src.ai.agents.librarian import LibrarianAgent


class TestLibrarianAgentRAG(unittest.TestCase):
    @patch("development.src.ai.agent.core.OpenAI")
    @patch("development.src.ai.agents.librarian.search_vault", autospec=True)
    def test_librarian_uses_search(self, mock_search, mock_openai):
        # Configure mock name and doc for registry/schema generation
        mock_search.__name__ = "search_vault"
        mock_search.__doc__ = "Search the vault."

        # Setup mock OpenAI
        mock_client = MagicMock()
        mock_openai.return_value = mock_client

        # Setup mock LLM response that calls search
        mock_message_tool_call = MagicMock()
        mock_message_tool_call.content = None

        # Define a tool call
        tool_call = MagicMock()
        tool_call.id = "call_123"
        tool_call.function.name = "search_vault"
        tool_call.function.arguments = '{"query": "AI Agents"}'
        mock_message_tool_call.tool_calls = [tool_call]

        # Setup mock LLM response that gives final answer
        mock_message_final = MagicMock()
        mock_message_final.content = "I searched the vault."
        mock_message_final.tool_calls = None

        # Chain responses: Tool Call -> Final Answer
        # Note: We must construct the response structure correctly (response.choices[0].message)
        mock_client.chat.completions.create.side_effect = [
            MagicMock(choices=[MagicMock(message=mock_message_tool_call)]),
            MagicMock(choices=[MagicMock(message=mock_message_final)]),
        ]

        # Initialize agent
        agent = LibrarianAgent()

        # Mock the search tool implementation to return a string
        mock_search.return_value = "Found note: agents.md"

        # Run agent
        result = agent.run("Check for AI Agents")

        # Verify result
        self.assertEqual(result, "I searched the vault.")

        # Check if LLM was called twice
        self.assertEqual(mock_client.chat.completions.create.call_count, 2)

        # Verify tool was called
        mock_search.assert_called_with(query="AI Agents")


if __name__ == "__main__":
    unittest.main()
