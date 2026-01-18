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

"""Memory indexer for OpenSpec knowledge base using ChromaDB."""

from __future__ import annotations

import hashlib
from pathlib import Path
from typing import List, Dict, Any

try:
  import chromadb
  from chromadb.config import Settings
  CHROMADB_AVAILABLE = True
except ImportError:
  CHROMADB_AVAILABLE = False


class MemoryIndexer:
  """Index OpenSpec memory documents for efficient retrieval.
  
  Uses ChromaDB to create vector embeddings of memory documents,
  enabling semantic search for relevant knowledge.
  """
  
  def __init__(
      self,
      memory_dir: str | Path,
      collection_name: str = "openspec_memories",
      persist_directory: str = ".chromadb"
  ):
    """Initialize the memory indexer.
    
    Args:
      memory_dir: Directory containing memory markdown files
      collection_name: Name for the ChromaDB collection
      persist_directory: Directory to persist the vector database
      
    Raises:
      ImportError: If chromadb is not installed
    """
    if not CHROMADB_AVAILABLE:
      raise ImportError(
        "chromadb is required for memory indexing. "
        "Install with: pip install chromadb"
      )
    
    self.memory_dir = Path(memory_dir)
    self.collection_name = collection_name
    
    # Initialize ChromaDB client
    self.client = chromadb.PersistentClient(
      path=persist_directory,
      settings=Settings(anonymized_telemetry=False)
    )
    
    # Get or create collection
    self.collection = self.client.get_or_create_collection(
      name=collection_name,
      metadata={"description": "OpenSpec memory documents"}
    )
  
  def index_memories(self, force_reindex: bool = False) -> Dict[str, Any]:
    """Index all memory documents in the directory.
    
    Args:
      force_reindex: If True, clear existing index and reindex all documents
      
    Returns:
      Dictionary with indexing statistics
    """
    if force_reindex:
      self.client.delete_collection(self.collection_name)
      self.collection = self.client.create_collection(
        name=self.collection_name,
        metadata={"description": "OpenSpec memory documents"}
      )
    
    if not self.memory_dir.exists():
      raise FileNotFoundError(f"Memory directory not found: {self.memory_dir}")
    
    # Find all markdown files
    md_files = list(self.memory_dir.glob("*.md"))
    
    if not md_files:
      return {
        "status": "no_files",
        "message": f"No markdown files found in {self.memory_dir}"
      }
    
    # Check if already indexed
    existing_count = self.collection.count()
    if existing_count > 0 and not force_reindex:
      return {
        "status": "already_indexed",
        "document_count": existing_count,
        "message": "Memories already indexed. Use force_reindex=True to reindex."
      }
    
    # Index each document
    documents = []
    metadatas = []
    ids = []
    
    for md_file in md_files:
      content = md_file.read_text(encoding='utf-8')
      
      # Split into chunks for better retrieval
      chunks = self._chunk_document(content, md_file.name)
      
      for i, chunk in enumerate(chunks):
        # Create unique ID
        doc_id = self._create_doc_id(md_file.name, i)
        
        # Determine category
        category = self._categorize_document(md_file.name)
        
        documents.append(chunk)
        metadatas.append({
          "filename": md_file.name,
          "category": category,
          "chunk_index": i,
          "total_chunks": len(chunks)
        })
        ids.append(doc_id)
    
    # Add to ChromaDB
    if documents:
      self.collection.add(
        documents=documents,
        metadatas=metadatas,
        ids=ids
      )
    
    return {
      "status": "success",
      "files_indexed": len(md_files),
      "chunks_created": len(documents),
      "collection_name": self.collection_name
    }
  
  def _chunk_document(
      self,
      content: str,
      filename: str,
      chunk_size: int = 1000,
      overlap: int = 200
  ) -> List[str]:
    """Split document into overlapping chunks.
    
    Args:
      content: Document content
      filename: Name of the file (for context)
      chunk_size: Target size of each chunk in characters
      overlap: Number of characters to overlap between chunks
      
    Returns:
      List of text chunks
    """
    # Add filename as context to each chunk
    header = f"# {filename}\n\n"
    
    # Split by paragraphs first
    paragraphs = content.split('\n\n')
    
    chunks = []
    current_chunk = header
    
    for para in paragraphs:
      # If adding this paragraph exceeds chunk size, start new chunk
      if len(current_chunk) + len(para) > chunk_size and current_chunk != header:
        chunks.append(current_chunk.strip())
        # Start new chunk with overlap
        overlap_text = current_chunk[-overlap:] if len(current_chunk) > overlap else current_chunk
        current_chunk = header + overlap_text + "\n\n" + para
      else:
        current_chunk += "\n\n" + para
    
    # Add final chunk
    if current_chunk.strip() != header.strip():
      chunks.append(current_chunk.strip())
    
    return chunks if chunks else [content]
  
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
  
  def _create_doc_id(self, filename: str, chunk_index: int) -> str:
    """Create unique document ID.
    
    Args:
      filename: Name of the file
      chunk_index: Index of the chunk
      
    Returns:
      Unique document ID
    """
    # Create hash-based ID for consistency
    content = f"{filename}_{chunk_index}"
    return hashlib.md5(content.encode()).hexdigest()
  
  def get_stats(self) -> Dict[str, Any]:
    """Get statistics about the indexed memories.
    
    Returns:
      Dictionary with collection statistics
    """
    count = self.collection.count()
    
    if count == 0:
      return {
        "total_chunks": 0,
        "message": "No documents indexed"
      }
    
    # Get sample to analyze categories
    sample = self.collection.get(limit=count)
    
    categories = {}
    files = set()
    
    for metadata in sample['metadatas']:
      category = metadata.get('category', 'Unknown')
      categories[category] = categories.get(category, 0) + 1
      files.add(metadata.get('filename', 'Unknown'))
    
    return {
      "total_chunks": count,
      "unique_files": len(files),
      "categories": categories,
      "collection_name": self.collection_name
    }
