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

"""CLI for Cognee-based memory indexing and retrieval."""

from __future__ import annotations

import argparse
import asyncio
import os
import sys
from pathlib import Path

# Configure environment before importing cognee to suppress warnings
os.environ.setdefault("ENABLE_BACKEND_ACCESS_CONTROL", "false")
# Set log level to ERROR to suppress info/warning messages during CLI usage
os.environ.setdefault("LOG_LEVEL", "ERROR")

from cognee_openspec.memory.indexer import CogneeMemoryIndexer
from cognee_openspec.memory.retriever import CogneeMemoryRetriever


def setup_cognee_env():
  """Setup Cognee environment variables if not already set."""
  if not os.getenv("LLM_API_KEY"):
    print("⚠️  Warning: LLM_API_KEY not set in environment")
    print("   Set it with: export LLM_API_KEY='your-api-key'")
    print("   Or create a .env file in the cognee directory")


async def index_command_async(args):
  """Index memory documents using Cognee."""
  setup_cognee_env()
  
  print(f"📚 Indexing memories with Cognee from: {args.memory_dir}")
  print(f"   Building knowledge graph...")
  
  indexer = CogneeMemoryIndexer(
    memory_dir=args.memory_dir,
    dataset_name=args.dataset_name,
    chunk_size=args.chunk_size
  )
  
  result = await indexer.index_memories(
    force_reindex=args.force,
    temporal_cognify=args.temporal
  )
  
  if result["status"] == "success":
    print(f"✅ Successfully built knowledge graph:")
    print(f"   Files: {result['files_indexed']}")
    print(f"   Dataset: {result['dataset_name']}")
    print(f"   Graph: {result['graph_built']}")
    
    # Generate visualization if requested
    if args.visualize:
      viz_path = args.viz_output or "openspec_graph.html"
      print(f"\n📊 Generating graph visualization...")
      viz_file = await indexer.visualize_graph(viz_path)
      print(f"   Saved to: {viz_file}")
  else:
    print(f"⚠️  {result.get('message', 'Indexing failed')}")
    sys.exit(1)


def index_command(args):
  """Synchronous wrapper for index command."""
  asyncio.run(index_command_async(args))


async def stats_command_async(args):
  """Show indexing statistics."""
  setup_cognee_env()
  
  indexer = CogneeMemoryIndexer(
    memory_dir=args.memory_dir,
    dataset_name=args.dataset_name
  )
  
  stats = await indexer.get_stats()
  
  print("📊 Cognee Knowledge Graph Statistics:")
  print(f"   Dataset: {stats.get('dataset_name', 'N/A')}")
  print(f"   Status: {stats.get('status', 'unknown')}")
  print(f"   Message: {stats.get('message', 'N/A')}")


def stats_command(args):
  """Synchronous wrapper for stats command."""
  asyncio.run(stats_command_async(args))


async def search_command_async(args):
  """Search memory documents using Cognee."""
  setup_cognee_env()
  
  print(f"🔍 Searching with Cognee: {args.query}")
  print(f"   Search type: {args.search_type}")
  
  retriever = CogneeMemoryRetriever(
    dataset_name=args.dataset_name,
    search_type=args.search_type,
    top_k=args.k
  )
  
  result = await retriever.search_with_context(
    query=args.query,
    category=args.category
  )
  
  if result["passages"]:
    print(f"\n✅ Found {result['count']} relevant results:\n")
    for i, passage in enumerate(result["passages"], 1):
      print(f"--- Result {i} ---")
      print(passage[:500] + ("..." if len(passage) > 500 else ""))
      print()
  else:
    print("❌ No relevant results found")


def search_command(args):
  """Synchronous wrapper for search command."""
  asyncio.run(search_command_async(args))


async def visualize_command_async(args):
  """Generate graph visualization."""
  setup_cognee_env()
  
  print(f"📊 Generating knowledge graph visualization...")
  
  indexer = CogneeMemoryIndexer(
    memory_dir=args.memory_dir,
    dataset_name=args.dataset_name
  )
  
  viz_file = await indexer.visualize_graph(args.output)
  
  print(f"✅ Visualization saved to: {viz_file}")
  print(f"   Open in browser to explore the knowledge graph")


def visualize_command(args):
  """Synchronous wrapper for visualize command."""
  asyncio.run(visualize_command_async(args))


def main():
  """Main CLI entry point."""
  parser = argparse.ArgumentParser(
    description="Cognee-based OpenSpec Memory Indexing and Retrieval CLI"
  )
  
  subparsers = parser.add_subparsers(
    dest="command",
    help="Command to execute"
  )
  
  # Index command
  index_parser = subparsers.add_parser(
    "index",
    help="Index memory documents and build knowledge graph"
  )
  index_parser.add_argument(
    "memory_dir",
    help="Directory containing memory markdown files"
  )
  index_parser.add_argument(
    "--dataset-name",
    default="openspec_memories",
    help="Dataset name (default: openspec_memories)"
  )
  index_parser.add_argument(
    "--chunk-size",
    type=int,
    help="Chunk size for document processing"
  )
  index_parser.add_argument(
    "--force",
    action="store_true",
    help="Force reindexing even if already indexed"
  )
  index_parser.add_argument(
    "--temporal",
    action="store_true",
    help="Enable temporal graph features"
  )
  index_parser.add_argument(
    "--visualize",
    action="store_true",
    help="Generate graph visualization after indexing"
  )
  index_parser.add_argument(
    "--viz-output",
    help="Output path for visualization (default: openspec_graph.html)"
  )
  
  # Stats command
  stats_parser = subparsers.add_parser(
    "stats",
    help="Show knowledge graph statistics"
  )
  stats_parser.add_argument(
    "--memory-dir",
    default="openspec-memories",
    help="Memory directory (default: openspec-memories)"
  )
  stats_parser.add_argument(
    "--dataset-name",
    default="openspec_memories",
    help="Dataset name (default: openspec_memories)"
  )
  
  # Search command
  search_parser = subparsers.add_parser(
    "search",
    help="Search memory documents using knowledge graph"
  )
  search_parser.add_argument(
    "query",
    help="Search query"
  )
  search_parser.add_argument(
    "--dataset-name",
    default="openspec_memories",
    help="Dataset name (default: openspec_memories)"
  )
  search_parser.add_argument(
    "--search-type",
    choices=[
      "GRAPH_COMPLETION",
      "CHUNKS",
      "SUMMARIES",
      "GRAPH_COMPLETION_COT",
      "TEMPORAL"
    ],
    default="GRAPH_COMPLETION",
    help="Search strategy (default: GRAPH_COMPLETION)"
  )
  search_parser.add_argument(
    "--category",
    choices=["DML", "Test", "General"],
    help="Filter by category"
  )
  search_parser.add_argument(
    "--k",
    type=int,
    default=5,
    help="Number of results to return (default: 5)"
  )
  
  # Visualize command
  viz_parser = subparsers.add_parser(
    "visualize",
    help="Generate knowledge graph visualization"
  )
  viz_parser.add_argument(
    "--memory-dir",
    default="openspec-memories",
    help="Memory directory (default: openspec-memories)"
  )
  viz_parser.add_argument(
    "--dataset-name",
    default="openspec_memories",
    help="Dataset name (default: openspec_memories)"
  )
  viz_parser.add_argument(
    "--output",
    default="openspec_graph.html",
    help="Output file path (default: openspec_graph.html)"
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
  elif args.command == "visualize":
    visualize_command(args)


if __name__ == "__main__":
  main()
