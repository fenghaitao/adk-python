# Copyright 2025 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Cognee-based memory retriever for OpenSpec knowledge base.

This module provides graph-based retrieval using Cognee's multiple
search strategies including graph completion, chunks, and summaries.
"""

from __future__ import annotations

import asyncio
from typing import List, Dict, Any

try:
  import cognee
  from cognee import SearchType
  COGNEE_AVAILABLE = True
except ImportError:
  COGNEE_AVAILABLE = False


class CogneeMemoryRetriever:
  """Retrieve OpenSpec memory using Cognee's graph-based search.
  
  Supports multiple search strategies:
  - GRAPH_COMPLETION: LLM completion with graph context
  - CHUNKS: Semantic chunk retrieval
  - SUMMARIES: Document summary retrieval
  - GRAPH_COMPLETION_COT: Chain-of-thought reasoning over graphs
  """
  
  def __init__(
      self,
      dataset_name: str = "openspec_memories",
      search_type: str = "GRAPH_COMPLETION",
      top_k: int = 5,
  ):
    """Initialize the Cognee memory retriever.
    
    Args:
      dataset_name: Name of the Cognee dataset to search
      search_type: Type of search (GRAPH_COMPLETION, CHUNKS, SUMMARIES, etc.)
      top_k: Number of results to return
      
    Raises:
      ImportError: If cognee is not installed
    """
    if not COGNEE_AVAILABLE:
      raise ImportError(
        "cognee is required for graph-based memory retrieval. "
        "Install with: pip install cognee"
      )
    
    self.dataset_name = dataset_name
    self.top_k = top_k
    
    # Map string to SearchType enum
    self.search_type = self._get_search_type(search_type)
  
  def _get_search_type(self, search_type_str: str) -> SearchType:
    """Convert string to SearchType enum.
    
    Args:
      search_type_str: String representation of search type
      
    Returns:
      SearchType enum value
    """
    search_type_map = {
      "GRAPH_COMPLETION": SearchType.GRAPH_COMPLETION,
      "CHUNKS": SearchType.CHUNKS,
      "SUMMARIES": SearchType.SUMMARIES,
      "GRAPH_COMPLETION_COT": SearchType.GRAPH_COMPLETION_COT,
      "GRAPH_SUMMARY_COMPLETION": SearchType.GRAPH_SUMMARY_COMPLETION,
      "TRIPLET_COMPLETION": SearchType.TRIPLET_COMPLETION,
      "NATURAL_LANGUAGE": SearchType.NATURAL_LANGUAGE,
      "TEMPORAL": SearchType.TEMPORAL,
    }
    
    return search_type_map.get(
      search_type_str.upper(),
      SearchType.GRAPH_COMPLETION
    )
  
  async def search(
      self,
      query: str,
      category: str | None = None,
  ) -> List[str]:
    """Search for relevant memory passages.
    
    Args:
      query: Search query
      category: Optional category filter (DML, Test, General)
      
    Returns:
      List of relevant passages
    """
    # Enhance query with category if provided
    enhanced_query = query
    if category:
      enhanced_query = f"[Category: {category}] {query}"
    
    # Perform search using Cognee
    results = await cognee.search(
      query_text=enhanced_query,
      query_type=self.search_type,
    )
    
    # Extract passages from results
    passages = self._extract_passages(results)
    
    return passages[:self.top_k]
  
  def _extract_passages(self, results: List[Any]) -> List[str]:
    """Extract text passages from Cognee search results.
    
    Args:
      results: Raw results from Cognee search
      
    Returns:
      List of text passages
    """
    passages = []
    
    for result in results:
      if isinstance(result, str):
        passages.append(result)
      elif isinstance(result, dict):
        # Extract text from various possible fields
        text = (
          result.get("text") or
          result.get("content") or
          result.get("answer") or
          str(result)
        )
        passages.append(text)
      else:
        passages.append(str(result))
    
    return passages
  
  async def search_with_context(
      self,
      query: str,
      category: str | None = None,
  ) -> Dict[str, Any]:
    """Search with additional context and metadata.
    
    Args:
      query: Search query
      category: Optional category filter
      
    Returns:
      Dictionary with passages and metadata
    """
    passages = await self.search(query, category)
    
    return {
      "query": query,
      "category": category,
      "search_type": self.search_type.value,
      "passages": passages,
      "count": len(passages)
    }


def search_memories_sync(
    query: str,
    dataset_name: str = "openspec_memories",
    search_type: str = "GRAPH_COMPLETION",
    category: str | None = None,
    top_k: int = 5,
) -> List[str]:
  """Synchronous wrapper for searching memories.
  
  Args:
    query: Search query
    dataset_name: Name of the Cognee dataset
    search_type: Type of search strategy
    category: Optional category filter
    top_k: Number of results to return
    
  Returns:
    List of relevant passages
  """
  retriever = CogneeMemoryRetriever(
    dataset_name=dataset_name,
    search_type=search_type,
    top_k=top_k
  )
  
  return asyncio.run(retriever.search(query, category))
