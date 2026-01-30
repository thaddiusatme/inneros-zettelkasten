import os
import json
import logging
from typing import List, Any, Optional
from dataclasses import dataclass

# We'll support OpenAI initially as the primary driver for tool use due to reliability
from openai import OpenAI

from .tools import ToolRegistry

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class AgentConfig:
    name: str
    model: str = "gpt-4o"  # Default to a capable model
    system_prompt: str = "You are a helpful assistant."
    temperature: float = 0.0
    max_steps: int = 10


class Agent:
    """
    Base Agent class implementing the ReAct loop using OpenAI's tool calling.
    """

    def __init__(
        self, config: AgentConfig, tool_registry: Optional[ToolRegistry] = None
    ):
        self.config = config
        self.registry = tool_registry or ToolRegistry()
        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        self.messages: List[Any] = [
            {"role": "system", "content": self.config.system_prompt}
        ]

    def add_tool(self, func):
        """Register a tool directly to this agent's registry."""
        self.registry.register(func)

    def run(self, user_input: str) -> str:
        """
        Main execution loop.
        1. Add user message.
        2. Loop:
           - Call LLM.
           - If text content, return it (done).
           - If tool call, execute tool and add result to history.
           - Repeat.
        """
        self.messages.append({"role": "user", "content": user_input})

        steps = 0
        while steps < self.config.max_steps:
            steps += 1

            # Prepare tools argument if we have tools
            tools_schema = self.registry.get_schemas()
            kwargs = {}
            if tools_schema:
                kwargs["tools"] = tools_schema
                kwargs["tool_choice"] = "auto"

            try:
                response = self.client.chat.completions.create(
                    model=self.config.model,
                    messages=self.messages,
                    temperature=self.config.temperature,
                    **kwargs,
                )
            except Exception as e:
                return f"LLM Error: {str(e)}"

            message = response.choices[0].message
            self.messages.append(message)  # Add assistant message to history

            # Check if we have tool calls
            if message.tool_calls:
                logger.info(f"Agent decided to call {len(message.tool_calls)} tools.")

                for tool_call in message.tool_calls:
                    func_name = tool_call.function.name
                    arguments_str = tool_call.function.arguments
                    tool_call_id = tool_call.id

                    try:
                        arguments = json.loads(arguments_str)
                        logger.info(
                            f"Executing tool: {func_name} with args: {arguments}"
                        )

                        result = self.registry.execute(func_name, arguments)
                        result_str = str(result)

                    except Exception as e:
                        result_str = f"Error executing tool: {str(e)}"
                        logger.error(result_str)

                    # Append tool result to history
                    self.messages.append(
                        {
                            "role": "tool",
                            "tool_call_id": tool_call_id,
                            "content": result_str,
                        }
                    )

                # Loop continues to let LLM see the tool output and respond
                continue

            # If no tool calls, we have our final answer
            if message.content:
                return message.content

            return "Agent finished but returned no content."

        return "Max steps reached without a final answer."
