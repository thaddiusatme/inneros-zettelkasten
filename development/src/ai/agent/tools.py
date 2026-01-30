import inspect
from typing import Callable, Dict, Any, List, Optional, get_type_hints
from functools import wraps


class ToolRegistry:
    """
    Registry for agent tools.
    Handles registration, schema generation (for OpenAI/Anthropic), and execution.
    """

    def __init__(self):
        self._tools: Dict[str, Callable] = {}
        self._schemas: List[Dict[str, Any]] = []

    def register(self, func: Callable) -> Callable:
        """Decorator to register a function as a tool."""
        self._tools[func.__name__] = func
        self._schemas.append(self._generate_schema(func))

        @wraps(func)
        def wrapper(*args, **kwargs):
            return func(*args, **kwargs)

        return wrapper

    def get_tool(self, name: str) -> Optional[Callable]:
        return self._tools.get(name)

    def get_schemas(self) -> List[Dict[str, Any]]:
        """Returns the list of tool schemas for the LLM."""
        return self._schemas

    def execute(self, name: str, arguments: Dict[str, Any]) -> Any:
        """Executes a tool by name with provided arguments."""
        tool = self.get_tool(name)
        if not tool:
            raise ValueError(f"Tool '{name}' not found.")
        try:
            return tool(**arguments)
        except Exception as e:
            return f"Error executing tool '{name}': {str(e)}"

    def _generate_schema(self, func: Callable) -> Dict[str, Any]:
        """Generates OpenAI-compatible function schema from type hints and docstrings."""
        sig = inspect.signature(func)
        type_hints = get_type_hints(func)
        doc = inspect.getdoc(func) or "No description provided."

        parameters = {"type": "object", "properties": {}, "required": []}

        for name, param in sig.parameters.items():
            if name == "self":
                continue

            param_type = type_hints.get(name, str)
            param_desc = "Parameter"  # Could parse docstring for more detail if needed

            # Basic type mapping
            json_type = "string"
            if param_type is int:
                json_type = "integer"
            elif param_type is float:
                json_type = "number"
            elif param_type is bool:
                json_type = "boolean"
            elif param_type is dict:
                json_type = "object"
            elif param_type is list:
                json_type = "array"

            parameters["properties"][name] = {
                "type": json_type,
                "description": param_desc,
            }

            if param.default == inspect.Parameter.empty:
                parameters["required"].append(name)

        return {
            "type": "function",
            "function": {
                "name": func.__name__,
                "description": doc,
                "parameters": parameters,
            },
        }
