"""Indexer for OpenSpec memories."""

import sys
from pathlib import Path
from typing import Optional, List

# Add lightrag to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / "lightrag"))

from lightrag import LightRAG
from lightrag.llm.llama_index_impl import (
    llama_index_complete_if_cache,
    llama_index_embed,
)
from lightrag.utils import EmbeddingFunc
from llama_index.llms.litellm import LiteLLM
from llama_index.embeddings.litellm import LiteLLMEmbedding

from .config import LightRAGConfig, OpenSpecConfig


class OpenSpecIndexer:
    """Indexes OpenSpec memories using LightRAG."""

    def __init__(
        self,
        lightrag_config: Optional[LightRAGConfig] = None,
        openspec_config: Optional[OpenSpecConfig] = None,
    ):
        """Initialize the indexer.

        Args:
            lightrag_config: LightRAG configuration
            openspec_config: OpenSpec configuration
        """
        self.lightrag_config = lightrag_config or LightRAGConfig()
        self.openspec_config = openspec_config or OpenSpecConfig()
        self.rag: Optional[LightRAG] = None

    async def _create_llm_func(self, prompt, system_prompt=None, history_messages=[], **kwargs):
        """Create LLM function."""
        if "llm_instance" not in kwargs:
            kwargs["llm_instance"] = LiteLLM(
                model=self.lightrag_config.llm_model,
                api_key=self.lightrag_config.api_key,
                temperature=0.7,
            )
        return await llama_index_complete_if_cache(
            kwargs["llm_instance"], prompt, system_prompt, history_messages
        )

    async def _create_embedding_func(self, texts):
        """Create embedding function."""
        embed_model = LiteLLMEmbedding(
            model_name=self.lightrag_config.embedding_model,
            api_key=self.lightrag_config.api_key,
        )
        return await llama_index_embed(texts, embed_model=embed_model)

    async def initialize(self):
        """Initialize LightRAG."""
        self.rag = LightRAG(
            working_dir=self.lightrag_config.working_dir,
            llm_model_func=self._create_llm_func,
            embedding_func=EmbeddingFunc(
                embedding_dim=self.lightrag_config.embedding_dim,
                max_token_size=8192,
                func=self._create_embedding_func,
            ),
            llm_model_name=self.lightrag_config.llm_model,
            llm_model_max_async=self.lightrag_config.llm_model_max_async,
            embedding_func_max_async=self.lightrag_config.embedding_func_max_async,
            max_parallel_insert=self.lightrag_config.max_parallel_insert,
            chunk_token_size=self.lightrag_config.chunk_token_size,
            chunk_overlap_token_size=self.lightrag_config.chunk_overlap_token_size,
        )
        await self.rag.initialize_storages()

    async def index_files(self, file_paths: Optional[List[Path]] = None) -> int:
        """Index markdown files.

        Args:
            file_paths: List of file paths to index. If None, indexes all files
                       in memories_dir matching file_pattern.

        Returns:
            Number of files indexed.
        """
        if not self.rag:
            raise RuntimeError("Indexer not initialized. Call initialize() first.")

        if file_paths is None:
            memories_path = Path(self.openspec_config.memories_dir)
            file_paths = sorted(memories_path.glob(self.openspec_config.file_pattern))

        indexed_count = 0
        for file_path in file_paths:
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    content = f.read()

                # Skip empty files
                if self.openspec_config.skip_empty_files:
                    if len(content.strip()) < self.openspec_config.min_content_length:
                        continue

                # Insert with file path for tracking
                await self.rag.ainsert(
                    content, ids=file_path.stem, file_paths=str(file_path)
                )
                indexed_count += 1

            except Exception as e:
                print(f"Error indexing {file_path}: {e}")
                continue

        return indexed_count

    async def finalize(self):
        """Finalize and cleanup."""
        if self.rag:
            await self.rag.finalize_storages()
