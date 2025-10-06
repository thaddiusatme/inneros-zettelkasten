#!/usr/bin/env python3
"""
Debug test to see what Ollama is returning
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from ai.ollama_client import OllamaClient

# Create client with explicit model
client = OllamaClient(config={"model": "llama3:latest"})

# Simple test
test_prompt = "Extract quotes from this: [00:15] AI is transforming everything"

print("Testing Ollama connection...")
print(f"Model: {client.model}")
print(f"Health check: {client.health_check()}")
print()

try:
    response = client.generate_completion(
        prompt=test_prompt,
        system_prompt="You are a helpful assistant.",
        max_tokens=100
    )
    print(f"Response received: {len(response)} characters")
    print(f"Response: {response[:200] if len(response) > 200 else response}")
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
