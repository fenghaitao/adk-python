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

"""CLI for memory indexing and retrieval."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from dspy_openspec.memory.indexer import MemoryIndexer
from dspy_openspec.memory.retriever import MemoryRetriever


def index_command(args):
  """Index memory documents."""
  print(f"📚 Indexing memories from: {args.memory_dir}")
  
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
  
  result = retriever.forward(
    task_description=args.query,
    category=args.category
  )
  
  if result.passages:
    print(f"\n✅ Found {len(result.passages)} relevant passages:\n")
    for i, passage in enumerate(result.passages, 1):
      print(f"--- Passage {i} ---")
      print(passage[:500] + ("..." if len(passage) > 500 else ""))
      print()
  else:
    print("❌ No relevant passages found")


def main():
  """Main CLI entry point."""
  parser = argparse.ArgumentParser(
    description="OpenSpec Memory Indexing and Retrieval CLI"
  )
  
  subparsers = parser.add_subparsers(dest="command", help="Command to execute")
  
  # Index command
  index_parser = subparsers.add_parser("index", help="Index memory documents")
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
  stats_parser = subparsers.add_parser("stats", help="Show index statistics")
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
  search_parser = subparsers.add_parser("search", help="Search memory documents")
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
  if args.command == "index":
    index_command(args)
  elif args.command == "stats":
    stats_command(args)
  elif args.command == "search":
    search_command(args)


if __name__ == "__main__":
  main()
