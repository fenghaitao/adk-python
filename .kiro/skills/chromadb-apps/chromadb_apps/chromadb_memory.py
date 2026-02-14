#!/usr/bin/env python3
"""
ChromaDB Memory - Knowledge Indexing and Retrieval

Index markdown documents into ChromaDB and retrieve them with semantic search.

Usage:
    # First time: Create .venv (required)
    uv sync --directory /path/to/chromadb-apps
    
    # Index memories
    uv run --directory /path/to/chromadb-apps chromadb-memory index openspec-memories
    
    # Search memories
    uv run --directory /path/to/chromadb-apps chromadb-memory search "How to implement timer?"
    
    # Show statistics
    uv run --directory /path/to/chromadb-apps chromadb-memory stats

Features:
- ChromaDB vector storage with persistence
- Category-aware retrieval (DML, Test, General)
- Semantic search with configurable k results
- Lightweight dependencies (only chromadb + pyyaml)
- Markdown with frontmatter support
"""

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

from __future__ import annotations

import argparse
import sys
import re
from pathlib import Path
from typing import List, Dict, Any, Optional

try:
    import chromadb
    from chromadb.config import Settings
    import yaml
except ImportError as e:
    print(f"❌ Missing dependency: {e}")
    print("Run with: uv run chromadb_memory.py")
    sys.exit(1)


# ============================================================================
# Memory Indexer
# ============================================================================

class MemoryIndexer:
    """Index markdown documents into ChromaDB."""
    
    def __init__(
        self,
        memory_dir: str = "openspec-memories",
        persist_directory: str = ".chromadb",
        collection_name: str = "openspec_memories"
    ):
        """Initialize the indexer.
        
        Args:
            memory_dir: Directory containing markdown files
            persist_directory: ChromaDB persistence directory
            collection_name: Name of the ChromaDB collection
        """
        self.memory_dir = Path(memory_dir)
        self.persist_directory = persist_directory
        self.collection_name = collection_name
        
        # Initialize ChromaDB with PersistentClient for better performance
        self.client = chromadb.PersistentClient(
            path=persist_directory,
            settings=Settings(anonymized_telemetry=False)
        )
    
    def parse_frontmatter(self, content: str) -> tuple[Dict[str, Any], str]:
        """Parse YAML frontmatter from markdown content.
        
        Args:
            content: Markdown content
            
        Returns:
            Tuple of (metadata dict, content without frontmatter)
        """
        if not content.startswith("---"):
            return {}, content
        
        parts = content.split("---", 2)
        if len(parts) < 3:
            return {}, content
        
        try:
            metadata = yaml.safe_load(parts[1]) or {}
        except yaml.YAMLError:
            metadata = {}
        
        return metadata, parts[2].strip()
    
    def detect_category(self, filepath: Path, metadata: Dict) -> str:
        """Detect document category.
        
        Args:
            filepath: Path to the markdown file
            metadata: Parsed frontmatter metadata
            
        Returns:
            Category: "DML", "Test", or "General"
        """
        # Check frontmatter first
        if "category" in metadata:
            return metadata["category"]
        
        # Check filename patterns
        filename = filepath.name.upper()
        if "DML" in filename:
            return "DML"
        elif "TEST" in filename:
            return "Test"
        
        return "General"
    
    def chunk_text(
        self,
        text: str,
        chunk_size: int = 500,
        overlap: int = 50
    ) -> List[str]:
        """Chunk text into smaller pieces with overlap.
        
        Args:
            text: Text to chunk
            chunk_size: Maximum characters per chunk
            overlap: Characters to overlap between chunks
            
        Returns:
            List of text chunks
        """
        # Split by paragraphs first
        paragraphs = text.split("\n\n")
        
        chunks = []
        current_chunk = ""
        
        for para in paragraphs:
            para = para.strip()
            if not para:
                continue
            
            # If paragraph fits in current chunk, add it
            if len(current_chunk) + len(para) + 2 <= chunk_size:
                current_chunk += "\n\n" + para if current_chunk else para
            else:
                # Save current chunk and start new one
                if current_chunk:
                    chunks.append(current_chunk)
                
                # If paragraph is too long, split it
                if len(para) > chunk_size:
                    words = para.split()
                    temp_chunk = ""
                    for word in words:
                        if len(temp_chunk) + len(word) + 1 <= chunk_size:
                            temp_chunk += " " + word if temp_chunk else word
                        else:
                            if temp_chunk:
                                chunks.append(temp_chunk)
                            temp_chunk = word
                    current_chunk = temp_chunk
                else:
                    current_chunk = para
        
        # Add last chunk
        if current_chunk:
            chunks.append(current_chunk)
        
        return chunks
    
    def index_memories(
        self,
        force_reindex: bool = False
    ) -> Dict[str, Any]:
        """Index all markdown files from memory directory.
        
        Args:
            force_reindex: Force reindexing even if collection exists
            
        Returns:
            Dictionary with indexing results
        """
        # Check if collection exists
        try:
            collection = self.client.get_collection(self.collection_name)
            if not force_reindex and collection.count() > 0:
                return {
                    "status": "already_indexed",
                    "message": "Collection already exists. Use --force to reindex.",
                    "document_count": collection.count()
                }
            # Delete existing collection if force reindex
            if force_reindex:
                self.client.delete_collection(self.collection_name)
        except Exception:
            pass
        
        # Create new collection
        collection = self.client.create_collection(
            name=self.collection_name,
            metadata={"hnsw:space": "cosine"}
        )
        
        # Find all markdown files
        md_files = list(self.memory_dir.glob("**/*.md"))
        
        if not md_files:
            return {
                "status": "error",
                "message": f"No markdown files found in {self.memory_dir}"
            }
        
        # Collect all documents first (batch processing for speed)
        print(f"Found {len(md_files)} markdown files to index...")
        print("Collecting documents...")
        
        all_documents = []
        all_metadatas = []
        all_ids = []
        
        for file_idx, filepath in enumerate(md_files, 1):
            try:
                content = filepath.read_text(encoding="utf-8")
                metadata, text = self.parse_frontmatter(content)
                category = self.detect_category(filepath, metadata)
                
                # Chunk the text
                chunks = self.chunk_text(text)
                print(f"  [{file_idx}/{len(md_files)}] {filepath.name}: {len(chunks)} chunks")
                
                # Collect chunks for batch processing
                for i, chunk in enumerate(chunks):
                    # Use relative path to avoid ID collisions in subdirectories
                    relative_path = str(filepath.relative_to(self.memory_dir)).replace('/', '_').replace('\\', '_')
                    doc_id = f"{relative_path}_chunk_{i}"
                    all_documents.append(chunk)
                    all_metadatas.append({
                        "file": str(filepath.relative_to(self.memory_dir)),
                        "category": category,
                        "chunk_index": i,
                        "title": metadata.get("title", filepath.stem)
                    })
                    all_ids.append(doc_id)
            
            except Exception as e:
                print(f"  ⚠️  Error indexing {filepath}: {e}")
                continue
        
        # Add all documents in one batch (MUCH faster!)
        if all_documents:
            print(f"\nAdding {len(all_documents)} chunks to ChromaDB...")
            collection.add(
                documents=all_documents,
                metadatas=all_metadatas,
                ids=all_ids
            )
        
        total_chunks = len(all_documents)
        
        return {
            "status": "success",
            "files_indexed": len(md_files),
            "chunks_created": total_chunks,
            "collection_name": self.collection_name
        }
    
    def get_stats(self) -> Dict[str, Any]:
        """Get indexing statistics.
        
        Returns:
            Dictionary with statistics
        """
        try:
            collection = self.client.get_collection(self.collection_name)
            count = collection.count()
            
            if count == 0:
                return {
                    "total_chunks": 0,
                    "message": "Collection is empty. Run 'index' command first."
                }
            
            # Get all metadata to compute stats
            results = collection.get(include=["metadatas"])
            metadatas = results.get("metadatas", [])
            
            # Count by category
            categories = {}
            files = set()
            for meta in metadatas:
                cat = meta.get("category", "Unknown")
                categories[cat] = categories.get(cat, 0) + 1
                files.add(meta.get("file", ""))
            
            return {
                "total_chunks": count,
                "unique_files": len(files),
                "categories": categories
            }
        
        except Exception as e:
            return {
                "total_chunks": 0,
                "message": f"Error getting stats: {e}"
            }


# ============================================================================
# Memory Retriever
# ============================================================================

class MemoryRetriever:
    """Retrieve relevant passages from memory using ChromaDB."""
    
    def __init__(
        self,
        persist_directory: str = ".chromadb",
        collection_name: str = "openspec_memories",
        k: int = 3
    ):
        """Initialize the retriever.
        
        Args:
            persist_directory: ChromaDB persistence directory
            collection_name: Name of the ChromaDB collection
            k: Number of passages to retrieve
        """
        self.persist_directory = persist_directory
        self.collection_name = collection_name
        self.k = k
        
        # Initialize ChromaDB with PersistentClient
        self.client = chromadb.PersistentClient(
            path=persist_directory,
            settings=Settings(anonymized_telemetry=False)
        )
        
        try:
            self.collection = self.client.get_collection(collection_name)
        except Exception as e:
            print(f"⚠️  Collection not found: {e}")
            print("Run 'index' command first to create the collection.")
            self.collection = None
    
    def __call__(
        self,
        task_description: str,
        category: Optional[str] = None
    ) -> Dict[str, List[str]]:
        """Retrieve relevant passages for the given task.
        
        Args:
            task_description: Query or task description
            category: Optional category filter (DML, Test, General)
            
        Returns:
            Dictionary with 'passages' key containing list of retrieved texts
        """
        if not self.collection:
            return {"passages": []}
        
        # Build query filter
        where = {}
        if category:
            where["category"] = category
        
        # Query ChromaDB
        try:
            results = self.collection.query(
                query_texts=[task_description],
                n_results=self.k,
                where=where if where else None
            )
            
            passages = results.get("documents", [[]])[0]
            return {"passages": passages}
        
        except Exception as e:
            print(f"⚠️  Error during retrieval: {e}")
            return {"passages": []}


# ============================================================================
# CLI Commands
# ============================================================================

def test_command(args):
    """Test if all dependencies are available."""
    print("🧪 Testing ChromaDB Memory Skill...")
    
    # Test imports
    try:
        import chromadb
        print("✅ ChromaDB import: OK")
    except ImportError:
        print("❌ ChromaDB import: FAILED")
        return False
    
    try:
        import yaml
        print("✅ YAML import: OK")
    except ImportError:
        print("❌ YAML import: FAILED")
        return False
    
    print("\n✅ All dependencies available!")
    print("\nNext steps:")
    print("  1. Index memories: uv run chromadb_memory.py index openspec-memories")
    print("  2. Search: uv run chromadb_memory.py search 'your query'")
    return True


def index_command(args):
    """Index memory documents."""
    print(f"📚 Indexing memories from: {args.memory_dir}")
    print("ℹ️  First run will download embedding model (~500MB, one-time)")
    print()
    
    if not Path(args.memory_dir).exists():
        print(f"❌ Directory not found: {args.memory_dir}")
        sys.exit(1)
    
    indexer = MemoryIndexer(
        memory_dir=args.memory_dir,
        persist_directory=args.persist_dir
    )
    
    result = indexer.index_memories(force_reindex=args.force)
    
    if result["status"] == "success":
        print(f"✅ Successfully indexed memories:")
        print(f"   Files: {result['files_indexed']}")
        print(f"   Chunks: {result['chunks_created']}")
        print(f"   Collection: {result['collection_name']}")
    elif result["status"] == "already_indexed":
        print(f"ℹ️  {result['message']}")
        print(f"   Documents: {result['document_count']}")
    else:
        print(f"⚠️  {result.get('message', 'Indexing failed')}")
        sys.exit(1)


def stats_command(args):
    """Show indexing statistics."""
    indexer = MemoryIndexer(
        memory_dir=args.memory_dir,
        persist_directory=args.persist_dir
    )
    
    stats = indexer.get_stats()
    
    print("📊 Memory Index Statistics:")
    print(f"   Total chunks: {stats['total_chunks']}")
    
    if stats['total_chunks'] > 0:
        print(f"   Unique files: {stats['unique_files']}")
        print(f"   Categories:")
        for category, count in stats['categories'].items():
            print(f"     - {category}: {count} chunks")
    else:
        print(f"   {stats['message']}")


def search_command(args):
    """Search memory documents."""
    print(f"🔍 Searching for: {args.query}")
    
    retriever = MemoryRetriever(
        persist_directory=args.persist_dir,
        k=args.k
    )
    
    result = retriever(
        task_description=args.query,
        category=args.category
    )
    
    passages = result.get("passages", [])
    
    if passages:
        print(f"\n✅ Found {len(passages)} relevant passages:\n")
        for i, passage in enumerate(passages, 1):
            print(f"--- Passage {i} ---")
            # Show first 500 chars
            display_text = passage[:500]
            if len(passage) > 500:
                display_text += "..."
            print(display_text)
            print()
    else:
        print("❌ No relevant passages found")
        print("\nTips:")
        print("  - Check if memories are indexed: 'stats' command")
        print("  - Try different search terms")
        print("  - Remove --category filter")


# ============================================================================
# Main CLI
# ============================================================================

def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="ChromaDB Memory - Knowledge Indexing and Retrieval",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Test installation
  uv run chromadb_memory.py test
  
  # Index memories
  uv run chromadb_memory.py index openspec-memories
  
  # Search with category filter
  uv run chromadb_memory.py search "timer implementation" --category DML
  
  # Get more results
  uv run chromadb_memory.py search "test patterns" --k 5
  
  # Show statistics
  uv run chromadb_memory.py stats
        """
    )
    
    subparsers = parser.add_subparsers(dest="command", help="Command to execute")
    
    # Test command
    test_parser = subparsers.add_parser(
        "test",
        help="Test if dependencies are available"
    )
    
    # Index command
    index_parser = subparsers.add_parser(
        "index",
        help="Index memory documents"
    )
    index_parser.add_argument(
        "memory_dir",
        help="Directory containing memory markdown files"
    )
    index_parser.add_argument(
        "--persist-dir",
        default=".chromadb",
        help="Directory to persist ChromaDB (default: .chromadb)"
    )
    index_parser.add_argument(
        "--force",
        action="store_true",
        help="Force reindexing even if already indexed"
    )
    
    # Stats command
    stats_parser = subparsers.add_parser(
        "stats",
        help="Show index statistics"
    )
    stats_parser.add_argument(
        "--memory-dir",
        default="openspec-memories",
        help="Memory directory (default: openspec-memories)"
    )
    stats_parser.add_argument(
        "--persist-dir",
        default=".chromadb",
        help="ChromaDB directory (default: .chromadb)"
    )
    
    # Search command
    search_parser = subparsers.add_parser(
        "search",
        help="Search memory documents"
    )
    search_parser.add_argument(
        "query",
        help="Search query"
    )
    search_parser.add_argument(
        "--category",
        choices=["DML", "Test", "General"],
        help="Filter by category"
    )
    search_parser.add_argument(
        "--k",
        type=int,
        default=3,
        help="Number of results to return (default: 3)"
    )
    search_parser.add_argument(
        "--persist-dir",
        default=".chromadb",
        help="ChromaDB directory (default: .chromadb)"
    )
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        sys.exit(1)
    
    # Execute command
    if args.command == "test":
        success = test_command(args)
        sys.exit(0 if success else 1)
    elif args.command == "index":
        index_command(args)
    elif args.command == "stats":
        stats_command(args)
    elif args.command == "search":
        search_command(args)


if __name__ == "__main__":
    main()
