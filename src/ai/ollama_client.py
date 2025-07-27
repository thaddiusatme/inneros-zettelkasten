"""
Ollama AI client for local LLM integration.
Provides health checks and basic API interactions.
"""

import requests
from typing import Dict, Any, Optional


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
        self.model = config.get("model", "llama3.1:8b")
    
    def health_check(self) -> bool:
        """
        Check if Ollama service is running and responsive.
        
        Returns:
            bool: True if service is healthy, False otherwise
        """
        try:
            response = requests.get(
                f"{self.base_url}/api/tags",
                timeout=self.timeout
            )
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
            response = requests.get(
                f"{self.base_url}/api/tags",
                timeout=self.timeout
            )
            if response.status_code == 200:
                models = response.json().get("models", [])
                return any(model.get("name") == model_name for model in models)
            return False
        except (requests.ConnectionError, requests.Timeout):
            return False
