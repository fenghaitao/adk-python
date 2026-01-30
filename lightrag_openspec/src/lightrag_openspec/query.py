"""Query interface for OpenSpec memories."""

import sys
from pathlib import Path
from typing import Optional

# Add lightrag to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / "lightrag"))

from lightrag import LightRAG, QueryParam
from lightrag.llm.llama_index_impl import (
    llama_index_complete_if_cache,
    llama_index_embed,
)
from lightrag.utils import EmbeddingFunc
from llama_index.llms.litellm import LiteLLM
from llama_index.embeddings.litellm import LiteLLMEmbedding

from .config import LightRAGConfig


class OpenSpecQuery:
    """Query interface for OpenSpec knowledge base."""

    def __init__(self, config: Optional[LightRAGConfig] = None):
        """Initialize the query interface.

        Args:
            config: LightRAG configuration
        """
        self.config = config or LightRAGConfig()
        self.rag: Optional[LightRAG] = None

    async def _create_llm_func(self, prompt, system_prompt=None, history_messages=[], **kwargs):
        """Create LLM function."""
        if "llm_instance" not in kwargs:
            kwargs["llm_instance"] = LiteLLM(
                model=self.config.llm_model,
                api_key=self.config.api_key,
                temperature=0.7,
            )
        return await llama_index_complete_if_cache(
            kwargs["llm_instance"], prompt, system_prompt, history_messages
        )

    async def _create_embedding_func(self, texts):
        """Create embedding function."""
        embed_model = LiteLLMEmbedding(
            model_name=self.config.embedding_model,
            api_key=self.config.api_key,
        )
        return await llama_index_embed(texts, embed_model=embed_model)

    async def initialize(self):
        """Initialize LightRAG for querying."""
        self.rag = LightRAG(
            working_dir=self.config.working_dir,
            llm_model_func=self._create_llm_func,
            embedding_func=EmbeddingFunc(
                embedding_dim=self.config.embedding_dim,
                max_token_size=8192,
                func=self._create_embedding_func,
            ),
            llm_model_name=self.config.llm_model,
        )
        await self.rag.initialize_storages()

    async def query(
        self,
        question: str,
        mode: Optional[str] = None,
        top_k: Optional[int] = None,
        only_context: bool = False,
    ) -> str:
        """Query the knowledge base.

        Args:
            question: Question to ask
            mode: Search mode (naive, local, global, hybrid). Defaults to config default.
            top_k: Number of entities/relations to retrieve. Defaults to config default.
            only_context: If True, return only context without LLM generation.

        Returns:
            Answer or context string.
        """
        if not self.rag:
            raise RuntimeError("Query interface not initialized. Call initialize() first.")

        mode = mode or self.config.default_search_mode
        top_k = top_k or self.config.top_k

        result = await self.rag.aquery(
            question,
            param=QueryParam(
                mode=mode,
                only_need_context=only_context,
            ),
        )
        return result

    async def get_entities(self) -> list:
        """Get all entities in the knowledge graph.

        Returns:
            List of entity names.
        """
        if not self.rag:
            raise RuntimeError("Query interface not initialized. Call initialize() first.")

        labels = await self.rag.get_graph_labels()
        return list(labels) if labels else []

    async def get_knowledge_graph(
        self, node_label: str, max_depth: int = 2, max_nodes: int = 50
    ):
        """Get knowledge graph for a specific entity.

        Args:
            node_label: Entity name to explore
            max_depth: Maximum depth to traverse
            max_nodes: Maximum nodes to return

        Returns:
            Knowledge graph with nodes and edges.
        """
        if not self.rag:
            raise RuntimeError("Query interface not initialized. Call initialize() first.")

        return await self.rag.get_knowledge_graph(
            node_label=node_label, max_depth=max_depth, max_nodes=max_nodes
        )

    async def finalize(self):
        """Finalize and cleanup."""
        if self.rag:
            await self.rag.finalize_storages()
