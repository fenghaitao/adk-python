"""Configuration for LightRAG OpenSpec."""

import os
from dataclasses import dataclass
from typing import Optional


def _get_default_storage_dir() -> str:
    """Get default storage directory."""
    return os.path.abspath(
        os.path.join(os.path.dirname(__file__), "../../lightrag_openspec_storage")
    )


@dataclass
class LightRAGConfig:
    """Configuration for LightRAG."""

    # Model configuration
    llm_model: str = "github_copilot/gpt-4o-mini"
    embedding_model: str = "github_copilot/text-embedding-3-small"
    embedding_dim: int = 1536
    api_key: str = "oauth2"
    
    # Storage configuration
    working_dir: Optional[str] = None
    
    # Processing configuration
    chunk_token_size: int = 1200
    chunk_overlap_token_size: int = 100
    llm_model_max_async: int = 4
    embedding_func_max_async: int = 4
    max_parallel_insert: int = 1
    
    # Query configuration
    default_search_mode: str = "hybrid"
    top_k: int = 60
    max_token_for_text_unit: int = 4000
    max_token_for_local_context: int = 4000
    max_token_for_global_context: int = 4000
    
    def __post_init__(self):
        """Initialize computed fields."""
        if self.working_dir is None:
            self.working_dir = _get_default_storage_dir()
    
    @classmethod
    def from_env(cls) -> "LightRAGConfig":
        """Create configuration from environment variables."""
        return cls(
            llm_model=os.getenv("LIGHTRAG_LLM_MODEL", "github_copilot/gpt-4o-mini"),
            embedding_model=os.getenv("LIGHTRAG_EMBEDDING_MODEL", "github_copilot/text-embedding-3-small"),
            working_dir=os.getenv("LIGHTRAG_WORKING_DIR"),
        )


def _get_default_memories_dir() -> str:
    """Get default OpenSpec memories directory."""
    return os.path.abspath(
        os.path.join(os.path.dirname(__file__), "../../../openspec-memories")
    )


@dataclass
class OpenSpecConfig:
    """Configuration for OpenSpec memories."""

    # Source configuration
    memories_dir: Optional[str] = None
    file_pattern: str = "*.md"
    
    # Indexing configuration
    skip_empty_files: bool = True
    min_content_length: int = 50
    
    def __post_init__(self):
        """Initialize computed fields."""
        if self.memories_dir is None:
            self.memories_dir = _get_default_memories_dir()
    
    @classmethod
    def from_env(cls) -> "OpenSpecConfig":
        """Create configuration from environment variables."""
        return cls(
            memories_dir=os.getenv("OPENSPEC_MEMORIES_DIR"),
        )
