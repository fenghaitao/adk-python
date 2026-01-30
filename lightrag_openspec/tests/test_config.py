"""Tests for configuration module."""

import os
import pytest
from lightrag_openspec.config import LightRAGConfig, OpenSpecConfig


class TestLightRAGConfig:
    """Tests for LightRAGConfig."""

    def test_default_config(self):
        """Test default configuration."""
        config = LightRAGConfig()
        
        assert config.llm_model == "github_copilot/gpt-4o-mini"
        assert config.embedding_model == "github_copilot/text-embedding-3-small"
        assert config.embedding_dim == 1536
        assert config.api_key == "oauth2"
        assert config.working_dir is not None

    def test_custom_config(self):
        """Test custom configuration."""
        config = LightRAGConfig(
            llm_model="custom/model",
            working_dir="/custom/path",
            embedding_dim=768
        )
        
        assert config.llm_model == "custom/model"
        assert config.working_dir == "/custom/path"
        assert config.embedding_dim == 768

    def test_from_env(self, monkeypatch):
        """Test configuration from environment variables."""
        monkeypatch.setenv("LIGHTRAG_LLM_MODEL", "env/model")
        monkeypatch.setenv("LIGHTRAG_WORKING_DIR", "/env/path")
        
        config = LightRAGConfig.from_env()
        
        assert config.llm_model == "env/model"
        assert config.working_dir == "/env/path"

    def test_post_init_sets_working_dir(self):
        """Test that __post_init__ sets working_dir if None."""
        config = LightRAGConfig(working_dir=None)
        assert config.working_dir is not None
        assert isinstance(config.working_dir, str)


class TestOpenSpecConfig:
    """Tests for OpenSpecConfig."""

    def test_default_config(self):
        """Test default configuration."""
        config = OpenSpecConfig()
        
        assert config.memories_dir is not None
        assert config.file_pattern == "*.md"
        assert config.skip_empty_files is True
        assert config.min_content_length == 50

    def test_custom_config(self):
        """Test custom configuration."""
        config = OpenSpecConfig(
            memories_dir="/custom/docs",
            file_pattern="*.txt",
            skip_empty_files=False
        )
        
        assert config.memories_dir == "/custom/docs"
        assert config.file_pattern == "*.txt"
        assert config.skip_empty_files is False

    def test_from_env(self, monkeypatch):
        """Test configuration from environment variables."""
        monkeypatch.setenv("OPENSPEC_MEMORIES_DIR", "/env/docs")
        
        config = OpenSpecConfig.from_env()
        
        assert config.memories_dir == "/env/docs"
