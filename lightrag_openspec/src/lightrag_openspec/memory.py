"""LightRAG memory for ADK agents."""

from typing import Optional

from .config import LightRAGConfig
from .indexer import OpenSpecIndexer
from .query import OpenSpecQuery


class LightRAGMemory:
    """
    Memory system for ADK agents using LightRAG's knowledge graph.

    This can be used as a custom memory backend for ADK agents to provide:
    - Graph-based context retrieval
    - Entity and relationship tracking
    - Multi-hop reasoning capabilities
    """

    def __init__(
        self,
        working_dir: str,
        config: Optional[LightRAGConfig] = None,
    ):
        """Initialize LightRAG memory.

        Args:
            working_dir: Directory to store knowledge graph
            config: LightRAG configuration. If None, uses defaults.
        """
        if config is None:
            config = LightRAGConfig(working_dir=working_dir)
        else:
            config.working_dir = working_dir

        self.config = config
        self.indexer = OpenSpecIndexer(lightrag_config=config)
        self.query_interface = OpenSpecQuery(config=config)
        self._initialized = False

    async def initialize(self):
        """Initialize the memory system."""
        if not self._initialized:
            await self.indexer.initialize()
            await self.query_interface.initialize()
            self._initialized = True

    async def add_memory(self, content: str, doc_id: Optional[str] = None):
        """
        Add content to the knowledge graph memory.

        Args:
            content: Text content to add
            doc_id: Optional document ID for tracking
        """
        if not self._initialized:
            raise RuntimeError("Memory not initialized. Call initialize() first.")

        if self.indexer.rag:
            await self.indexer.rag.ainsert(content, ids=doc_id)

    async def query_memory(self, query: str, mode: str = "hybrid") -> str:
        """
        Query the knowledge graph memory.

        Args:
            query: Question or query string
            mode: Search mode (naive, local, global, hybrid)

        Returns:
            Retrieved context and answer
        """
        if not self._initialized:
            raise RuntimeError("Memory not initialized. Call initialize() first.")

        return await self.query_interface.query(query, mode=mode)

    async def get_context(self, query: str, mode: str = "hybrid") -> str:
        """
        Get only the context without generating an answer.

        Useful for passing context to ADK agents.

        Args:
            query: Question or query string
            mode: Search mode (naive, local, global, hybrid)

        Returns:
            Retrieved context only
        """
        if not self._initialized:
            raise RuntimeError("Memory not initialized. Call initialize() first.")

        return await self.query_interface.query(query, mode=mode, only_context=True)

    async def get_entities(self) -> list:
        """Get all entities in the knowledge graph."""
        if not self._initialized:
            raise RuntimeError("Memory not initialized. Call initialize() first.")

        return await self.query_interface.get_entities()

    async def finalize(self):
        """Clean up resources."""
        if self._initialized:
            await self.indexer.finalize()
            await self.query_interface.finalize()
            self._initialized = False
