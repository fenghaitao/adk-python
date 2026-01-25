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

"""Cognee-based memory indexer for OpenSpec knowledge base.

This module provides graph-based indexing using Cognee's ECL pipeline
(Extract, Cognify, Load) to build a knowledge graph from OpenSpec memories.
"""

from __future__ import annotations

import asyncio
from pathlib import Path
from typing import Dict, Any, List

try:
  import cognee
  COGNEE_AVAILABLE = True
except ImportError:
  COGNEE_AVAILABLE = False


class CogneeMemoryIndexer:
  """Index OpenSpec memory documents using Cognee knowledge graphs.
  
  Uses Cognee's ECL pipeline to transform memory documents into a
  structured knowledge graph with entities, relationships, and semantic
  connections for enhanced search and reasoning.
  """
  
  def __init__(
      self,
      memory_dir: str | Path,
      dataset_name: str = "openspec_memories",
      chunk_size: int | None = None,
  ):
    """Initialize the Cognee memory indexer.
    
    Args:
      memory_dir: Directory containing memory markdown files
      dataset_name: Name for the Cognee dataset
      chunk_size: Optional chunk size for document processing
      
    Raises:
      ImportError: If cognee is not installed
    """
    if not COGNEE_AVAILABLE:
      raise ImportError(
        "cognee is required for graph-based memory indexing. "
        "Install with: pip install cognee"
      )
    
    self.memory_dir = Path(memory_dir)
    self.dataset_name = dataset_name
    self.chunk_size = chunk_size
  
  async def index_memories(
      self,
      force_reindex: bool = False,
      temporal_cognify: bool = False
  ) -> Dict[str, Any]:
    """Index all memory documents using Cognee's ECL pipeline.
    
    Args:
      force_reindex: If True, clear existing data and reindex
      temporal_cognify: If True, enable temporal graph features
      
    Returns:
      Dictionary with indexing statistics
    """
    if not self.memory_dir.exists():
      raise FileNotFoundError(
        f"Memory directory not found: {self.memory_dir}"
      )
    
    # Find all markdown files
    md_files = list(self.memory_dir.glob("*.md"))
    
    if not md_files:
      return {
        "status": "no_files",
        "message": f"No markdown files found in {self.memory_dir}"
      }
    
    # Clear existing data if force reindex
    if force_reindex:
      await cognee.prune.prune_data()
      await cognee.prune.prune_system(metadata=True)
    
    # Prepare documents with metadata
    documents = []
    for md_file in md_files:
      content = md_file.read_text(encoding='utf-8')
      category = self._categorize_document(md_file.name)
      
      # Add metadata as context
      doc_with_metadata = (
        f"# {md_file.name}\n"
        f"Category: {category}\n\n"
        f"{content}"
      )
      documents.append(doc_with_metadata)
    
    # Add documents to Cognee
    # Don't pass dataset_id to avoid permission checks when access control is disabled
    await cognee.add(
      data=documents,
      dataset_name=self.dataset_name
    )
    
    # Run cognify to build knowledge graph
    cognify_params = {
      "datasets": [self.dataset_name],
      "temporal_cognify": temporal_cognify,
    }
    
    if self.chunk_size:
      cognify_params["chunk_size"] = self.chunk_size
    
    cognify_result = await cognee.cognify(**cognify_params)
    
    # Run memify to add enrichments
    await cognee.memify(dataset=self.dataset_name)
    
    return {
      "status": "success",
      "files_indexed": len(md_files),
      "dataset_name": self.dataset_name,
      "cognify_result": str(cognify_result),
      "graph_built": True
    }
  
  def _categorize_document(self, filename: str) -> str:
    """Determine document category from filename.
    
    Args:
      filename: Name of the markdown file
      
    Returns:
      Category string (DML, Test, or General)
    """
    filename_lower = filename.lower()
    
    if "dml" in filename_lower:
      return "DML"
    elif "test" in filename_lower:
      return "Test"
    else:
      return "General"
  
  async def get_stats(self) -> Dict[str, Any]:
    """Get statistics about the indexed knowledge graph.
    
    Returns:
      Dictionary with graph statistics
    """
    try:
      # Search for all documents to get stats
      results = await cognee.search(
        query_text="OpenSpec memory documents",
        query_type=cognee.SearchType.CHUNKS
      )
      
      return {
        "status": "success",
        "dataset_name": self.dataset_name,
        "results_available": len(results) > 0,
        "message": "Knowledge graph indexed successfully"
      }
    except Exception as e:
      return {
        "status": "error",
        "message": f"Error getting stats: {str(e)}"
      }
  
  async def visualize_graph(self, output_path: str | None = None) -> str:
    """Generate visualization of the knowledge graph.
    
    Args:
      output_path: Optional path for the visualization HTML file
      
    Returns:
      Path to the generated visualization file
    """
    if output_path is None:
      output_path = "openspec_graph_visualization.html"
    
    await cognee.visualize_graph(output_path)
    
    return output_path


def index_memories_sync(
    memory_dir: str | Path,
    dataset_name: str = "openspec_memories",
    force_reindex: bool = False,
    temporal_cognify: bool = False,
    chunk_size: int | None = None,
) -> Dict[str, Any]:
  """Synchronous wrapper for indexing memories.
  
  Args:
    memory_dir: Directory containing memory markdown files
    dataset_name: Name for the Cognee dataset
    force_reindex: If True, clear existing data and reindex
    temporal_cognify: If True, enable temporal graph features
    chunk_size: Optional chunk size for document processing
    
  Returns:
    Dictionary with indexing statistics
  """
  indexer = CogneeMemoryIndexer(
    memory_dir=memory_dir,
    dataset_name=dataset_name,
    chunk_size=chunk_size
  )
  
  return asyncio.run(
    indexer.index_memories(
      force_reindex=force_reindex,
      temporal_cognify=temporal_cognify
    )
  )
