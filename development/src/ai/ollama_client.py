"""
Ollama AI client for local LLM integration.
Provides health checks and basic API interactions.
"""

import requests
from typing import Dict, Any, Optional, List


class OllamaClient:
    """Client for interacting with Ollama local AI service."""

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize Ollama client with configuration.

        Args:
            config: Optional configuration dictionary
        """
        if config is None:
            config = {}

        self.base_url = config.get("base_url", "http://localhost:11434")
        self.timeout = config.get("timeout", 30)
        self.model = config.get("model", "llama3:latest")

    def health_check(self) -> bool:
        """
        Check if Ollama service is running and responsive.

        Returns:
            bool: True if service is healthy, False otherwise
        """
        try:
            response = requests.get(f"{self.base_url}/api/tags", timeout=self.timeout)
            return response.status_code == 200
        except (requests.ConnectionError, requests.Timeout):
            return False

    def is_model_available(self, model_name: str) -> bool:
        """
        Check if a specific model is available locally.

        Args:
            model_name: Name of the model to check

        Returns:
            bool: True if model is available, False otherwise
        """
        try:
            response = requests.get(f"{self.base_url}/api/tags", timeout=self.timeout)
            if response.status_code == 200:
                models = response.json().get("models", [])
                return any(model.get("name") == model_name for model in models)
            return False
        except (requests.ConnectionError, requests.Timeout):
            return False

    def generate_completion(
        self, prompt: str, system_prompt: str = "", max_tokens: int = 150
    ) -> str:
        """
        Generate text completion using Ollama API.

        Args:
            prompt: The user prompt to complete
            system_prompt: Optional system prompt for context
            max_tokens: Maximum tokens in response

        Returns:
            str: Generated text response

        Raises:
            Exception: If API call fails
        """
        try:
            payload = {
                "model": self.model,
                "prompt": prompt,
                "system": system_prompt,
                "stream": False,
                "options": {
                    "temperature": 0.3,
                    "num_predict": max_tokens,  # Ollama uses num_predict, not max_tokens
                },
            }

            response = requests.post(
                f"{self.base_url}/api/generate", json=payload, timeout=self.timeout
            )

            if response.status_code == 200:
                result = response.json()
                return result.get("response", "").strip()
            else:
                raise Exception(f"API error: {response.status_code} - {response.text}")

        except requests.ConnectionError:
            raise Exception("Failed to connect to Ollama service")
        except requests.Timeout:
            raise Exception("Request to Ollama service timed out")
        except Exception as e:
            raise Exception(f"Unexpected error: {str(e)}")

    def generate(
        self, prompt: str, system_prompt: str = "", max_tokens: int = 150
    ) -> str:
        """Alias for generate_completion for backward compatibility."""
        return self.generate_completion(prompt, system_prompt, max_tokens)

    def generate_embedding(self, text: str) -> List[float]:
        """
        Generate embedding vector for text using Ollama API.

        Args:
            text: Text to generate embedding for

        Returns:
            List[float]: Embedding vector

        Raises:
            Exception: If API call fails
        """
        try:
            payload = {"model": self.model, "prompt": text}

            response = requests.post(
                f"{self.base_url}/api/embeddings", json=payload, timeout=self.timeout
            )

            if response.status_code == 200:
                result = response.json()
                return result.get("embedding", [])
            else:
                raise Exception(
                    f"Embedding API error: {response.status_code} - {response.text}"
                )

        except requests.ConnectionError:
            raise Exception("Failed to connect to Ollama service")
        except requests.Timeout:
            raise Exception("Request to Ollama service timed out")
        except Exception as e:
            if (
                "Embedding API error" in str(e)
                or "Failed to connect" in str(e)
                or "timed out" in str(e)
            ):
                raise e
            raise Exception(f"Unexpected error generating embedding: {str(e)}")
