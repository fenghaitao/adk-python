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

"""Memory retriever using DSPy and ChromaDB."""

from __future__ import annotations

from typing import List, Dict, Any, Optional

import dspy

try:
  import chromadb
  from chromadb.config import Settings
  CHROMADB_AVAILABLE = True
except ImportError:
  CHROMADB_AVAILABLE = False


class ChromaDBRM(dspy.Retrieve):
  """ChromaDB retrieval model for DSPy.
  
  Integrates ChromaDB with DSPy's Retrieve interface for
  semantic search over OpenSpec memory documents.
  """
  
  def __init__(
      self,
      collection_name: str = "openspec_memories",
      persist_directory: str = ".chromadb",
      k: int = 3
  ):
    """Initialize ChromaDB retrieval model.
    
    Args:
      collection_name: Name of the ChromaDB collection
      persist_directory: Directory where ChromaDB is persisted
      k: Number of documents to retrieve
      
    Raises:
      ImportError: If chromadb is not installed
    """
    if not CHROMADB_AVAILABLE:
      raise ImportError(
        "chromadb is required for memory retrieval. "
        "Install with: pip install chromadb"
      )
    
    super().__init__(k=k)
    
    # Initialize ChromaDB client
    self.client = chromadb.PersistentClient(
      path=persist_directory,
      settings=Settings(anonymized_telemetry=False)
    )
    
    # Get collection
    try:
      self.collection = self.client.get_collection(name=collection_name)
    except Exception:
      raise ValueError(
        f"Collection '{collection_name}' not found. "
        "Please index memories first using MemoryIndexer."
      )
  
  def forward(
      self,
      query: str,
      k: Optional[int] = None,
      category: Optional[str] = None
  ) -> List[str]:
    """Retrieve relevant memory chunks.
    
    Args:
      query: Search query
      k: Number of results to return (overrides default)
      category: Filter by category (DML, Test, or General)
      
    Returns:
      List of relevant text chunks
    """
    k = k if k is not None else self.k
    
    # Build where filter if category specified
    where_filter = None
    if category:
      where_filter = {"category": category}
    
    # Query ChromaDB
    results = self.collection.query(
      query_texts=[query],
      n_results=k,
      where=where_filter
    )
    
    # Extract documents
    if results and results['documents']:
      return results['documents'][0]
    
    return []


class MemoryRetriever(dspy.Module):
  """Retrieve relevant OpenSpec memory documents.
  
  Uses semantic search to find the most relevant memory documents
  for a given task or error context.
  """
  
  def __init__(
      self,
      collection_name: str = "openspec_memories",
      persist_directory: str = ".chromadb",
      k: int = 3
  ):
    """Initialize memory retriever.
    
    Args:
      collection_name: Name of the ChromaDB collection
      persist_directory: Directory where ChromaDB is persisted
      k: Number of documents to retrieve by default
    """
    super().__init__()
    
    # Initialize ChromaDB retrieval model
    self.retrieve = ChromaDBRM(
      collection_name=collection_name,
      persist_directory=persist_directory,
      k=k
    )
  
  def forward(
      self,
      task_description: str,
      error_context: str = "",
      category: Optional[str] = None,
      k: Optional[int] = None
  ) -> dspy.Prediction:
    """Retrieve relevant memory documents.
    
    Args:
      task_description: Description of what the agent is trying to do
      error_context: Any error messages or failure context
      category: Filter by category (DML, Test, or General)
      k: Number of results to return
      
    Returns:
      Prediction with retrieved memory chunks
    """
    # Combine context for better retrieval
    query_parts = [task_description]
    if error_context:
      query_parts.append(f"Error: {error_context}")
    
    query = "\n".join(query_parts)
    
    # Retrieve relevant passages
    passages = self.retrieve(query, k=k, category=category)
    
    return dspy.Prediction(
      passages=passages,
      query=query
    )
  
  def retrieve_for_dml(
      self,
      task_description: str,
      error_context: str = "",
      k: int = 3
  ) -> List[str]:
    """Retrieve DML-specific memory documents.
    
    Args:
      task_description: Description of DML implementation task
      error_context: Any DML compilation errors
      k: Number of results to return
      
    Returns:
      List of relevant DML memory chunks
    """
    result = self.forward(
      task_description=task_description,
      error_context=error_context,
      category="DML",
      k=k
    )
    return result.passages
  
  def retrieve_for_test(
      self,
      task_description: str,
      error_context: str = "",
      k: int = 3
  ) -> List[str]:
    """Retrieve Test-specific memory documents.
    
    Args:
      task_description: Description of test creation task
      error_context: Any test execution errors
      k: Number of results to return
      
    Returns:
      List of relevant test memory chunks
    """
    result = self.forward(
      task_description=task_description,
      error_context=error_context,
      category="Test",
      k=k
    )
    return result.passages
