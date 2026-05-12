"""
Unit tests for Ollama AI client initialization and basic functionality.
These tests follow TDD principles - write failing test first, then implement.
"""

from unittest.mock import Mock, patch
import requests


class TestOllamaClient:
    """Test suite for Ollama client initialization and health checks."""

    def test_client_initialization_with_default_config(self):
        """Test that Ollama client initializes with default configuration."""
        # This test will fail until we implement the OllamaClient class
        from src.ai.ollama_client import OllamaClient

        client = OllamaClient()
        assert client.base_url == "http://localhost:11434"
        assert client.timeout == 30
        assert client.model == "gemma4:latest"

    def test_client_initialization_with_custom_config(self):
        """Test that Ollama client accepts custom configuration."""
        from src.ai.ollama_client import OllamaClient

        config = {
            "base_url": "http://custom-host:11434",
            "timeout": 60,
            "model": "custom-model",
        }

        client = OllamaClient(config=config)
        assert client.base_url == "http://custom-host:11434"
        assert client.timeout == 60
        assert client.model == "custom-model"

    def test_health_check_success(self):
        """Test successful health check against Ollama API."""
        from src.ai.ollama_client import OllamaClient

        with patch("requests.get") as mock_get:
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = {"status": "ok"}
            mock_get.return_value = mock_response

            client = OllamaClient()
            result = client.health_check()

            assert result is True
            mock_get.assert_called_once_with(
                "http://localhost:11434/api/tags", timeout=30
            )

    def test_health_check_failure_connection_error(self):
        """Test health check handles connection errors gracefully."""
        from src.ai.ollama_client import OllamaClient

        with patch("requests.get") as mock_get:
            mock_get.side_effect = requests.ConnectionError("Connection failed")

            client = OllamaClient()
            result = client.health_check()

            assert result is False

    def test_health_check_failure_timeout(self):
        """Test health check handles timeout errors gracefully."""
        from src.ai.ollama_client import OllamaClient

        with patch("requests.get") as mock_get:
            mock_get.side_effect = requests.Timeout("Request timed out")

            client = OllamaClient()
            result = client.health_check()

            assert result is False

    def test_model_availability_check(self):
        """Test checking if specific model is available."""
        from src.ai.ollama_client import OllamaClient

        with patch("requests.get") as mock_get:
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = {
                "models": [{"name": "llama3.1:8b"}, {"name": "mistral:7b"}]
            }
            mock_get.return_value = mock_response

            client = OllamaClient()
            result = client.is_model_available("llama3.1:8b")

            assert result is True

    def test_model_unavailability_check(self):
        """Test checking for unavailable model."""
        from src.ai.ollama_client import OllamaClient

        with patch("requests.get") as mock_get:
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = {"models": [{"name": "mistral:7b"}]}
            mock_get.return_value = mock_response

            client = OllamaClient()
            result = client.is_model_available("llama3.1:8b")

            assert result is False

    def test_generate_completion_success(self):
        """Test successful text generation returns response content."""
        from src.ai.ollama_client import OllamaClient

        with patch("requests.post") as mock_post:
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = {"response": "  hello world  "}
            mock_post.return_value = mock_response

            client = OllamaClient()
            result = client.generate_completion("say hello")

            assert result == "hello world"

    def test_generate_completion_omits_num_predict_by_default(self):
        """Test that num_predict is not sent when max_tokens=-1.

        Thinking models like gemma4 consume their entire num_predict budget on
        internal reasoning, returning an empty visible response when the cap is
        too low. Omitting num_predict lets the model run to its natural stop.
        """
        from src.ai.ollama_client import OllamaClient

        with patch("requests.post") as mock_post:
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = {"response": "ok"}
            mock_post.return_value = mock_response

            client = OllamaClient()
            client.generate_completion("prompt")

            _, kwargs = mock_post.call_args
            sent_options = kwargs["json"]["options"]
            assert "num_predict" not in sent_options

    def test_generate_completion_sends_num_predict_when_cap_set(self):
        """Test that num_predict is included when caller explicitly sets max_tokens."""
        from src.ai.ollama_client import OllamaClient

        with patch("requests.post") as mock_post:
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = {"response": "ok"}
            mock_post.return_value = mock_response

            client = OllamaClient()
            client.generate_completion("prompt", max_tokens=512)

            _, kwargs = mock_post.call_args
            sent_options = kwargs["json"]["options"]
            assert sent_options["num_predict"] == 512
