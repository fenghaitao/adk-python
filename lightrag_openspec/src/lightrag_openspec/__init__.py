"""
LightRAG OpenSpec Integration

Knowledge graph-based RAG system for OpenSpec memories with GitHub Copilot support.
"""

from .indexer import OpenSpecIndexer
from .query import OpenSpecQuery
from .memory import LightRAGMemory

__version__ = "1.0.0"
__all__ = ["OpenSpecIndexer", "OpenSpecQuery", "LightRAGMemory"]
