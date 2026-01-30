"""
Agent Event Handler - Trigger AI Agents from file events.

Monitors for "Magic Files" (e.g., "Request: *.md") in the Inbox and triggers
the appropriate AI Agent to handle the request.
"""

import logging
import time
from pathlib import Path
from typing import Optional, Dict, Any

from ..ai.agent.core import Agent
from ..ai.agents.librarian import LibrarianAgent

# Future: Import other agents here


class AgentEventHandler:
    """
    Handles AI Agent triggers from file events.

    Monitors for specific file naming patterns in the Inbox to trigger
    AI agents.

    Patterns:
    - "Request: <Task>.md" -> Triggers general/router agent (or specific based on content)
    - "Librarian: <Task>.md" -> Triggers LibrarianAgent
    """

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize Agent handler.

        Args:
            config: Configuration dictionary
                Keys: enabled, watch_path, processing_timeout
        """
        if not config:
            raise ValueError("Configuration dictionary is required")

        self.enabled = config.get("enabled", False)
        self.watch_path = Path(config.get("watch_path", "knowledge/Inbox"))
        self.processing_timeout = config.get("processing_timeout", 300)

        self._setup_logging()
        self.logger.info(f"Initialized AgentEventHandler watching: {self.watch_path}")

    def process(self, file_path: Path, event_type: str) -> None:
        """
        Process file events for agent triggers.

        Args:
            file_path: Path to the file
            event_type: Event type ('created', 'modified')
        """
        if not self.enabled:
            return

        if event_type not in ("created", "modified"):
            return

        # Only process markdown files
        if file_path.suffix.lower() != ".md":
            return

        # Check filename pattern
        filename = file_path.name

        # Trigger: Librarian
        if filename.startswith("Librarian:") or filename.startswith("Organize:"):
            self.logger.info(f"Detected Librarian trigger: {filename}")
            self._run_agent(LibrarianAgent(), file_path)

        # Future: Trigger: Request (General/Researcher)
        # elif filename.startswith("Request:"):
        #     self.logger.info(f"Detected Request trigger: {filename}")
        #     self._run_agent(ResearcherAgent(), file_path)

    def _run_agent(self, agent: Agent, request_file: Path) -> None:
        """
        Runs the specified agent with the content of the request file.

        Args:
            agent: The initialized Agent instance
            request_file: The file containing the user's request
        """
        try:
            # Read the request
            request_content = request_file.read_text(encoding="utf-8")

            # Add context about the file itself if needed
            prompt = f"Request from file '{request_file.name}':\n\n{request_content}"

            self.logger.info(f"Running agent {agent.config.name}...")
            start_time = time.time()

            # Execute Agent
            response = agent.run(prompt)
            duration = time.time() - start_time

            self.logger.info(f"Agent finished in {duration:.2f}s")

            # Append response to the request file (or create a new one?)
            # For now, let's append to the file so the user sees the answer.
            with open(request_file, "a", encoding="utf-8") as f:
                f.write(f"\n\n## Agent Response ({agent.config.name})\n")
                f.write(f"> Processed at {time.strftime('%Y-%m-%d %H:%M:%S')}\n\n")
                f.write(response)
                f.write("\n")

            # Rename file to mark as processed?
            # E.g., "Done - Librarian: Organize Inbox.md"
            # For now, let's leave it. The "modified" event might re-trigger if we aren't careful.
            # We should probably check if "Agent Response" is already in the file to avoid loops.

        except Exception as e:
            self.logger.error(f"Error running agent: {e}", exc_info=True)
            # Log error to file too?
            try:
                with open(request_file, "a", encoding="utf-8") as f:
                    f.write(f"\n\n## Agent Error\nError: {str(e)}\n")
            except Exception:
                pass

    def _setup_logging(self) -> None:
        """Setup logging for agent handler."""
        log_dir = Path(".automation/logs")
        log_dir.mkdir(parents=True, exist_ok=True)

        log_file = log_dir / f'agent_handler_{time.strftime("%Y-%m-%d")}.log'

        self.logger = logging.getLogger(f"{__name__}.AgentEventHandler")
        self.logger.setLevel(logging.INFO)

        handler = logging.FileHandler(log_file)
        handler.setFormatter(
            logging.Formatter(
                "%(asctime)s [%(levelname)s] %(name)s: %(message)s",
                datefmt="%Y-%m-%d %H:%M:%S",
            )
        )
        self.logger.addHandler(handler)
