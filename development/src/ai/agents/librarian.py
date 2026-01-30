import os
from pathlib import Path
from typing import List

from ..agent.core import Agent, AgentConfig
from ..agent.tools import ToolRegistry
from ..agent.rag_tools import search_vault

# Define the tools for the librarian


def list_inbox_files() -> List[str]:
    """Lists all markdown files currently in the Inbox."""
    inbox_path = Path("knowledge/Inbox")
    if not inbox_path.exists():
        return []
    return [f.name for f in inbox_path.glob("*.md")]


def read_note(filename: str) -> str:
    """Reads the content of a note from the Inbox or Vault."""
    # check inbox first
    path = Path("knowledge/Inbox") / filename
    if not path.exists():
        path = Path("knowledge") / filename

    if not path.exists():
        return f"Error: File '{filename}' not found."

    try:
        with open(path, "r", encoding="utf-8") as f:
            return f.read()
    except Exception as e:
        return f"Error reading file: {str(e)}"


def suggest_rename(filename: str, new_name: str, reasoning: str) -> str:
    """
    Proposes a rename for a file.
    In a real system, this might perform the move.
    For safety, we'll just log the suggestion for now.
    """
    return f"SUGGESTION: Rename '{filename}' to '{new_name}'. Reason: {reasoning}"


def suggest_archive(filename: str, reasoning: str) -> str:
    """Proposes moving a file to the Archive."""
    return f"SUGGESTION: Archive '{filename}'. Reason: {reasoning}"


class LibrarianAgent(Agent):
    """
    The Librarian Agent organizes the Inbox.
    It looks at files, reads them, and suggests renames or filing locations.
    """

    def __init__(self):
        registry = ToolRegistry()
        registry.register(list_inbox_files)
        registry.register(read_note)
        registry.register(suggest_rename)
        registry.register(suggest_archive)
        registry.register(search_vault)

        system_prompt = """
        You are the Librarian of the InnerOS Zettelkasten.
        Your goal is to keep the Inbox clean and organized.
        
        You have tools to:
        1. List files in the Inbox.
        2. Read the content of notes.
        3. Suggest renaming notes to follow the 'kebab-case' convention (lowercase, hyphens).
        4. Suggest archiving notes that are processed or irrelevant.
        5. Search the vault for related notes (to avoid duplicates or find connections).
        
        When asked to 'organize the inbox', you should:
        1. List the files.
        2. For each file, read it to understand the context.
        3. Search the vault to see if similar notes exist.
        4. Make a suggestion (rename or archive) if necessary.
        5. Provide a summary of your actions.
        """

        config = AgentConfig(
            name="Librarian", model="gpt-4o", system_prompt=system_prompt
        )

        super().__init__(config, registry)


if __name__ == "__main__":
    # Test run
    # Ensure OPENAI_API_KEY is set
    if not os.getenv("OPENAI_API_KEY"):
        print("Please set OPENAI_API_KEY to run the agent.")
    else:
        agent = LibrarianAgent()
        print("Librarian is starting...")
        result = agent.run("Please organize the inbox.")
        print("\n--- Final Result ---")
        print(result)
