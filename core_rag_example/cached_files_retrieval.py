#!/usr/bin/env python3
"""
Cached FilesRetrieval Implementation

This is an enhanced version of FilesRetrieval that caches embeddings to disk
and only re-computes them when files have changed.
"""

from __future__ import annotations

import logging
import hashlib
import json
import os
from pathlib import Path
from typing import Optional

from llama_index.core import SimpleDirectoryReader, VectorStoreIndex, StorageContext, load_index_from_storage
from google.adk.tools.retrieval.llama_index_retrieval import LlamaIndexRetrieval

logger = logging.getLogger("google_adk." + __name__)


class CachedFilesRetrieval(LlamaIndexRetrieval):
    """
    An enhanced FilesRetrieval that caches embeddings to disk for better performance.
    
    Features:
    - Caches embeddings to disk to avoid re-computation
    - Detects file changes and updates cache accordingly
    - Configurable cache directory
    - Automatic cache invalidation based on file modifications
    """

    def __init__(
        self, 
        *, 
        name: str, 
        description: str, 
        input_dir: str,
        cache_dir: Optional[str] = None,
        force_rebuild: bool = False
    ):
        """
        Initialize CachedFilesRetrieval.
        
        Args:
            name: Tool name
            description: Tool description
            input_dir: Directory containing documents to index
            cache_dir: Directory to store cached embeddings (default: input_dir/.embeddings_cache)
            force_rebuild: If True, force rebuild of cache even if it exists
        """
        self.input_dir = Path(input_dir)
        self.cache_dir = Path(cache_dir) if cache_dir else self.input_dir / ".embeddings_cache"
        self.force_rebuild = force_rebuild
        
        # Ensure directories exist
        self.input_dir.mkdir(parents=True, exist_ok=True)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        
        logger.info("Setting up cached retrieval for %s", input_dir)
        logger.info("Cache directory: %s", self.cache_dir)
        
        # Build or load the retriever
        retriever = self._get_or_build_retriever()
        
        super().__init__(name=name, description=description, retriever=retriever)

    def _get_files_info(self) -> dict[str, dict]:
        """
        Get information about all files in the input directory.
        
        Returns:
            Dictionary mapping file paths to their metadata (size, mtime, hash)
        """
        files_info = {}
        
        for file_path in self.input_dir.glob("**/*"):
            if file_path.is_file() and file_path.suffix.lower() in ['.txt', '.md', '.pdf', '.docx']:
                try:
                    stat = file_path.stat()
                    # Calculate file hash for content verification
                    with open(file_path, 'rb') as f:
                        file_hash = hashlib.md5(f.read()).hexdigest()
                    
                    files_info[str(file_path.relative_to(self.input_dir))] = {
                        'size': stat.st_size,
                        'mtime': stat.st_mtime,
                        'hash': file_hash
                    }
                except Exception as e:
                    logger.warning("Error reading file %s: %s", file_path, e)
        
        return files_info

    def _save_cache_metadata(self, files_info: dict[str, dict]) -> None:
        """Save metadata about cached files."""
        metadata_path = self.cache_dir / "cache_metadata.json"
        with open(metadata_path, 'w') as f:
            json.dump(files_info, f, indent=2)

    def _load_cache_metadata(self) -> Optional[dict[str, dict]]:
        """Load metadata about cached files."""
        metadata_path = self.cache_dir / "cache_metadata.json"
        if not metadata_path.exists():
            return None
        
        try:
            with open(metadata_path, 'r') as f:
                return json.load(f)
        except Exception as e:
            logger.warning("Error loading cache metadata: %s", e)
            return None

    def _is_cache_valid(self) -> bool:
        """
        Check if the cache is still valid by comparing file metadata.
        
        Returns:
            True if cache is valid, False if it needs to be rebuilt
        """
        if self.force_rebuild:
            logger.info("Force rebuild requested, cache invalid")
            return False
        
        # Check if cache directory has required files
        storage_files = ['docstore.json', 'index_store.json', 'vector_store.json']
        if not all((self.cache_dir / f).exists() for f in storage_files):
            logger.info("Cache files missing, cache invalid")
            return False
        
        # Get current files info
        current_files = self._get_files_info()
        
        # Load cached files info
        cached_files = self._load_cache_metadata()
        if cached_files is None:
            logger.info("No cache metadata found, cache invalid")
            return False
        
        # Compare file information
        if current_files != cached_files:
            logger.info("Files have changed, cache invalid")
            logger.debug("Current files: %s", current_files)
            logger.debug("Cached files: %s", cached_files)
            return False
        
        logger.info("Cache is valid, loading from disk")
        return True

    def _build_index(self) -> VectorStoreIndex:
        """Build a new vector index from documents."""
        logger.info("Building new vector index from %s", self.input_dir)
        
        # Load documents
        documents = SimpleDirectoryReader(str(self.input_dir)).load_data()
        logger.info("Loaded %d documents", len(documents))
        
        if not documents:
            raise ValueError(f"No documents found in {self.input_dir}")
        
        # Create index
        index = VectorStoreIndex.from_documents(documents)
        
        # Persist to cache
        logger.info("Persisting index to cache at %s", self.cache_dir)
        index.storage_context.persist(persist_dir=str(self.cache_dir))
        
        # Save metadata
        files_info = self._get_files_info()
        self._save_cache_metadata(files_info)
        
        return index

    def _load_index(self) -> VectorStoreIndex:
        """Load vector index from cache."""
        logger.info("Loading vector index from cache at %s", self.cache_dir)
        
        try:
            storage_context = StorageContext.from_defaults(persist_dir=str(self.cache_dir))
            index = load_index_from_storage(storage_context)
            logger.info("Successfully loaded index from cache")
            return index
        except Exception as e:
            logger.error("Error loading index from cache: %s", e)
            logger.info("Falling back to building new index")
            return self._build_index()

    def _get_or_build_retriever(self):
        """Get retriever, either from cache or by building new index."""
        if self._is_cache_valid():
            index = self._load_index()
        else:
            index = self._build_index()
        
        return index.as_retriever()

    def invalidate_cache(self) -> None:
        """Manually invalidate the cache and rebuild on next use."""
        logger.info("Manually invalidating cache")
        
        # Remove cache files
        cache_files = ['docstore.json', 'index_store.json', 'vector_store.json', 'cache_metadata.json']
        for filename in cache_files:
            cache_file = self.cache_dir / filename
            if cache_file.exists():
                cache_file.unlink()
        
        # Rebuild retriever
        self.retriever = self._get_or_build_retriever()

    def get_cache_info(self) -> dict:
        """Get information about the cache status."""
        cache_files = ['docstore.json', 'index_store.json', 'vector_store.json', 'cache_metadata.json']
        cache_exists = all((self.cache_dir / f).exists() for f in cache_files)
        
        cache_size = 0
        if cache_exists:
            for filename in cache_files:
                cache_file = self.cache_dir / filename
                if cache_file.exists():
                    cache_size += cache_file.stat().st_size
        
        files_info = self._get_files_info()
        
        return {
            'cache_dir': str(self.cache_dir),
            'cache_exists': cache_exists,
            'cache_size_bytes': cache_size,
            'cache_size_mb': round(cache_size / (1024 * 1024), 2),
            'documents_count': len(files_info),
            'documents': list(files_info.keys()),
            'cache_valid': self._is_cache_valid() if cache_exists else False
        }


def create_cached_rag_agent(documents_path: str, cache_dir: Optional[str] = None):
    """
    Create a RAG agent using CachedFilesRetrieval.
    
    Args:
        documents_path: Path to documents directory
        cache_dir: Optional custom cache directory
        
    Returns:
        Configured Agent with cached retrieval
    """
    from google.adk.agents.llm_agent import Agent
    from google.adk.tools.google_search_tool import GoogleSearchTool
    
    # Create the cached retrieval tool
    cached_retrieval_tool = CachedFilesRetrieval(
        name="search_local_documents",
        description=(
            "Use this tool to search through local documents and files "
            "to find relevant information. This searches through text files, "
            "documentation, and other local resources. Use this FIRST for "
            "questions that might be answered by the local knowledge base."
        ),
        input_dir=documents_path,
        cache_dir=cache_dir
    )
    
    # Configure the Google Search tool
    google_search_tool = GoogleSearchTool()
    
    # Create the agent
    agent = Agent(
        model="gemini-2.0-flash-001",
        name="cached_rag_agent",
        instruction=(
            "You are a helpful AI assistant with access to both local documents and web search. "
            "You have two main tools for finding information:\n\n"
            
            "1. **search_local_documents**: Local knowledge base with curated documents (cached for performance)\n"
            "2. **google_search**: Web search for current/general information\n\n"
            
            "**Search Strategy:**\n"
            "- Start with local documents for topics covered in the knowledge base\n"
            "- Use web search for current events, recent developments, or topics not in local docs\n"
            "- Combine information from both sources when helpful\n"
            "- Always cite your sources and indicate which tool provided the information\n\n"
            
            "**Response Format:**\n"
            "- Provide comprehensive answers combining relevant information\n"
            "- Clearly indicate information sources (local docs vs. web search)\n"
            "- Mention if information is from local knowledge vs. external sources"
        ),
        tools=[cached_retrieval_tool, google_search_tool],
    )
    
    return agent, cached_retrieval_tool


if __name__ == "__main__":
    # Demo the cached retrieval
    print("🚀 Cached FilesRetrieval Demo")
    print("=" * 50)
    
    # Configure embedding model (you'll need to uncomment and modify based on your setup)
    # from llama_index.core import Settings
    # from llama_index.embeddings.huggingface import HuggingFaceEmbedding
    # Settings.embed_model = HuggingFaceEmbedding(model_name="BAAI/bge-small-en-v1.5")
    
    docs_path = "sample_documents"
    
    print(f"📁 Using documents from: {docs_path}")
    
    # Create first instance (will build cache)
    print("\n🔄 Creating first CachedFilesRetrieval instance...")
    tool1 = CachedFilesRetrieval(
        name="test_retrieval_1",
        description="Test cached retrieval",
        input_dir=docs_path
    )
    
    cache_info = tool1.get_cache_info()
    print(f"📊 Cache info: {cache_info}")
    
    # Create second instance (should use cache)
    print("\n🔄 Creating second CachedFilesRetrieval instance...")
    tool2 = CachedFilesRetrieval(
        name="test_retrieval_2", 
        description="Test cached retrieval",
        input_dir=docs_path
    )
    
    print("✅ Demo completed!")
    print("\n💡 Benefits of CachedFilesRetrieval:")
    print("   - Faster startup after first run")
    print("   - Persistent embeddings across sessions")
    print("   - Automatic cache invalidation when files change")
    print("   - Configurable cache location")