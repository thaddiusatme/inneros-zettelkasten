"""
Tests for the collapsed llm_client module.

Covers OllamaClient, EmbeddingCache, and shared type aliases — all now
living in src.ai.llm_client as the single base-layer module.
"""

from unittest.mock import Mock, patch, MagicMock
from pathlib import Path
import pytest
import requests


# ---------------------------------------------------------------------------
# OllamaClient — imported from the new module location
# ---------------------------------------------------------------------------


class TestOllamaClientFromLLMClient:

    def test_imports_from_llm_client(self):
        from src.ai.llm_client import OllamaClient

        assert OllamaClient is not None

    def test_default_config(self):
        from src.ai.llm_client import OllamaClient

        client = OllamaClient()
        assert client.base_url == "http://localhost:11434"
        assert client.timeout == 30
        assert client.model == "gemma4:latest"

    def test_custom_config(self):
        from src.ai.llm_client import OllamaClient

        client = OllamaClient(
            {"base_url": "http://other:11434", "timeout": 60, "model": "llama3"}
        )
        assert client.base_url == "http://other:11434"
        assert client.timeout == 60
        assert client.model == "llama3"

    def test_health_check_success(self):
        from src.ai.llm_client import OllamaClient

        with patch("requests.get") as mock_get:
            mock_get.return_value = Mock(status_code=200)
            assert OllamaClient().health_check() is True

    def test_health_check_connection_error(self):
        from src.ai.llm_client import OllamaClient

        with patch("requests.get", side_effect=requests.ConnectionError()):
            assert OllamaClient().health_check() is False

    def test_generate_completion_strips_whitespace(self):
        from src.ai.llm_client import OllamaClient

        with patch("requests.post") as mock_post:
            mock_post.return_value = Mock(
                status_code=200, json=lambda: {"response": "  hi  "}
            )
            assert OllamaClient().generate_completion("prompt") == "hi"

    def test_generate_completion_omits_num_predict_by_default(self):
        from src.ai.llm_client import OllamaClient

        with patch("requests.post") as mock_post:
            mock_post.return_value = Mock(
                status_code=200, json=lambda: {"response": "ok"}
            )
            OllamaClient().generate_completion("prompt")
            options = mock_post.call_args[1]["json"]["options"]
            assert "num_predict" not in options

    def test_generate_completion_sends_num_predict_when_set(self):
        from src.ai.llm_client import OllamaClient

        with patch("requests.post") as mock_post:
            mock_post.return_value = Mock(
                status_code=200, json=lambda: {"response": "ok"}
            )
            OllamaClient().generate_completion("prompt", max_tokens=512)
            options = mock_post.call_args[1]["json"]["options"]
            assert options["num_predict"] == 512


# ---------------------------------------------------------------------------
# EmbeddingCache — imported from the new module location
# ---------------------------------------------------------------------------


class TestEmbeddingCacheFromLLMClient:

    def test_imports_from_llm_client(self):
        from src.ai.llm_client import EmbeddingCache

        assert EmbeddingCache is not None

    def test_init_creates_cache_dir(self, tmp_path):
        from src.ai.llm_client import EmbeddingCache

        cache = EmbeddingCache(cache_dir=str(tmp_path / "cache"))
        assert (tmp_path / "cache").exists()

    def test_cache_miss_returns_none(self, tmp_path):
        from src.ai.llm_client import EmbeddingCache

        cache = EmbeddingCache(cache_dir=str(tmp_path / "cache"))
        assert cache.get_embedding("not cached text") is None

    def test_store_and_retrieve_embedding(self, tmp_path):
        from src.ai.llm_client import EmbeddingCache

        cache = EmbeddingCache(cache_dir=str(tmp_path / "cache"))
        vec = [0.1, 0.2, 0.3]
        cache.store_embedding("hello", vec)
        assert cache.get_embedding("hello") == vec

    def test_cache_stats_returns_dict(self, tmp_path):
        from src.ai.llm_client import EmbeddingCache

        cache = EmbeddingCache(cache_dir=str(tmp_path / "cache"))
        stats = cache.get_cache_stats()
        assert "total_entries" in stats
        assert "max_size" in stats

    def test_clear_cache_empties_entries(self, tmp_path):
        from src.ai.llm_client import EmbeddingCache

        cache = EmbeddingCache(cache_dir=str(tmp_path / "cache"))
        cache.store_embedding("text", [0.1])
        cache.clear_cache()
        assert cache.get_embedding("text") is None


# ---------------------------------------------------------------------------
# Type aliases — all re-exported from llm_client
# ---------------------------------------------------------------------------


class TestTypeAliasesFromLLMClient:

    def test_all_aliases_importable(self):
        from src.ai.llm_client import (
            AnalyticsResult,
            AIEnhancementResult,
            ConnectionResult,
            WorkflowResult,
            ConfigDict,
            QualityMetrics,
            LinkSuggestion,
            LinkFeedback,
            NoteMetadata,
            NoteInfo,
            WorkflowReport,
            EnhancedMetrics,
            PromotionCandidate,
            ReviewCandidate,
        )

        # All are type aliases — just verify they exist
        assert AnalyticsResult is not None
        assert WorkflowResult is not None
        assert ConfigDict is not None
