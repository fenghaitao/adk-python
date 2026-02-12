#!/usr/bin/env python3
"""
LangChain Knowledge Graph - Document to Knowledge Graph

Build knowledge graphs from documents using LangChain and NetworkX.

Usage:
    # One-time setup
    cd adk-python/skills/langchain-apps
    uv sync
    
    # Test installation
    uv run langchain-memory test
    
    # Build graph from documents
    uv run langchain-memory build docs/ --output knowledge_graph.gml
    
    # Query the graph
    uv run langchain-memory query knowledge_graph.gml --entity "Python"
    
    # Visualize the graph
    uv run langchain-memory visualize knowledge_graph.gml --output graph.png

Features:
- LLM-based knowledge triple extraction
- NetworkX graph storage with persistence
- Entity-centric queries with depth traversal
- Graph visualization with matplotlib
- Support for multiple document formats
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
import os
import sys
from pathlib import Path
from typing import List, Dict, Any, Optional

try:
  from langchain_community.graphs import NetworkxEntityGraph
  from langchain_community.graphs.networkx_graph import (
    KnowledgeTriple,
    KG_TRIPLE_DELIMITER,
    parse_triples,
  )
  from langchain_core.output_parsers import StrOutputParser
  from langchain_core.prompts import PromptTemplate
  from langchain_openai import ChatOpenAI
except ImportError as e:
  print(f"❌ Missing dependency: {e}")
  print("Run 'uv sync' first to install dependencies")
  sys.exit(1)


# ============================================================================
# Knowledge Graph Builder
# ============================================================================

# Knowledge triple extraction prompt template
_KNOWLEDGE_TRIPLE_EXTRACTION_TEMPLATE = (
  "You are a networked intelligence helping a human track knowledge triples"
  " about all relevant people, things, concepts, etc. and integrating"
  " them with your knowledge stored within your weights"
  " as well as that stored in a knowledge graph."
  " Extract all of the knowledge triples from the text."
  " A knowledge triple is a clause that contains a subject, a predicate,"
  " and an object. The subject is the entity being described,"
  " the predicate is the property of the subject that is being"
  " described, and the object is the value of the property.\n\n"
  "EXAMPLE\n"
  "It's a state in the US. It's also the number 1 producer of gold in the US.\n\n"
  f"Output: (Nevada, is a, state){KG_TRIPLE_DELIMITER}(Nevada, is in, US)"
  f"{KG_TRIPLE_DELIMITER}(Nevada, is the number 1 producer of, gold)\n"
  "END OF EXAMPLE\n\n"
  "EXAMPLE\n"
  "I'm going to the store.\n\n"
  "Output: NONE\n"
  "END OF EXAMPLE\n\n"
  "EXAMPLE\n"
  "Oh huh. I know Descartes likes to drive antique scooters and play the mandolin.\n"
  f"Output: (Descartes, likes to drive, antique scooters){KG_TRIPLE_DELIMITER}"
  "(Descartes, plays, mandolin)\n"
  "END OF EXAMPLE\n\n"
  "EXAMPLE\n"
  "{text}"
  "Output:"
)


class KnowledgeGraphBuilder:
  """Build knowledge graphs from documents using LangChain.
  
  Uses modern LCEL (LangChain Expression Language) patterns instead of
  deprecated LLMChain.
  """
  
  def __init__(self, model: str = "gpt-4o-mini", temperature: float = 0.0):
    """Initialize the builder.
    
    Args:
      model: OpenAI model to use for extraction
      temperature: LLM temperature for extraction
    """
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
      raise ValueError(
        "OPENAI_API_KEY environment variable not set. "
        "Set it with: export OPENAI_API_KEY='your-key-here'"
      )
    
    self.llm = ChatOpenAI(model=model, temperature=temperature, api_key=api_key)
    
    # Create extraction chain using LCEL (modern pattern)
    self.extraction_chain = (
      PromptTemplate(
        input_variables=["text"],
        template=_KNOWLEDGE_TRIPLE_EXTRACTION_TEMPLATE
      )
      | self.llm
      | StrOutputParser()
    )
  
  def build_from_text(self, text: str) -> NetworkxEntityGraph:
    """Build a knowledge graph from a single text.
    
    Args:
      text: Input text to extract knowledge from
      
    Returns:
      NetworkxEntityGraph with extracted triples
    """
    graph = NetworkxEntityGraph()
    
    # Extract triples using LCEL chain
    output = self.extraction_chain.invoke({"text": text})
    
    # Parse and add triples to graph
    triples = parse_triples(output)
    for triple in triples:
      graph.add_triple(triple)
    
    return graph
  
  def build_from_documents(
    self,
    doc_paths: List[Path]
  ) -> NetworkxEntityGraph:
    """Build a knowledge graph from multiple documents.
    
    Args:
      doc_paths: List of document paths to process
      
    Returns:
      NetworkxEntityGraph with all extracted triples
    """
    graph = NetworkxEntityGraph()
    
    for doc_path in doc_paths:
      print(f"  Processing: {doc_path.name}")
      
      try:
        text = doc_path.read_text(encoding="utf-8")
        
        # Extract triples using LCEL chain
        output = self.extraction_chain.invoke({"text": text})
        triples = parse_triples(output)
        
        # Add all triples to main graph
        for triple in triples:
          graph.add_triple(triple)
        
        print(f"    Extracted {len(triples)} triples")
        
      except Exception as e:
        print(f"    ⚠ Error processing {doc_path.name}: {e}")
        continue
    
    return graph
  
  def build_from_directory(
    self,
    directory: Path,
    extensions: List[str] = [".md", ".txt"]
  ) -> NetworkxEntityGraph:
    """Build a knowledge graph from all documents in a directory.
    
    Args:
      directory: Directory containing documents
      extensions: File extensions to process
      
    Returns:
      NetworkxEntityGraph with all extracted triples
    """
    doc_paths = []
    for ext in extensions:
      doc_paths.extend(directory.glob(f"**/*{ext}"))
    
    if not doc_paths:
      print(f"⚠ No documents found in {directory}")
      return NetworkxEntityGraph()
    
    print(f"📚 Found {len(doc_paths)} documents")
    return self.build_from_documents(doc_paths)


# ============================================================================
# Knowledge Graph Query
# ============================================================================

class KnowledgeGraphQuery:
  """Query knowledge graphs."""
  
  def __init__(self, graph: NetworkxEntityGraph):
    """Initialize the query interface.
    
    Args:
      graph: NetworkxEntityGraph to query
    """
    self.graph = graph
  
  def get_entity_info(
    self,
    entity: str,
    depth: int = 1
  ) -> List[str]:
    """Get information about an entity.
    
    Args:
      entity: Entity name to query
      depth: Traversal depth
      
    Returns:
      List of relationship strings
    """
    if not self.graph.has_node(entity):
      return []
    
    return self.graph.get_entity_knowledge(entity, depth=depth)
  
  def get_all_entities(self) -> List[str]:
    """Get all entities in the graph.
    
    Returns:
      List of entity names
    """
    triples = self.graph.get_triples()
    entities = set()
    for subject, obj, _ in triples:
      entities.add(subject)
      entities.add(obj)
    return sorted(entities)
  
  def get_statistics(self) -> Dict[str, Any]:
    """Get graph statistics.
    
    Returns:
      Dictionary with graph statistics
    """
    triples = self.graph.get_triples()
    entities = self.get_all_entities()
    
    return {
      "total_nodes": self.graph.get_number_of_nodes(),
      "total_triples": len(triples),
      "total_entities": len(entities),
    }
  
  def search_entity(self, query: str) -> List[str]:
    """Search for entities matching a query.
    
    Args:
      query: Search query (case-insensitive substring match)
      
    Returns:
      List of matching entity names
    """
    entities = self.get_all_entities()
    query_lower = query.lower()
    return [e for e in entities if query_lower in e.lower()]


# ============================================================================
# Visualization
# ============================================================================

def visualize_graph(
  graph: NetworkxEntityGraph,
  output_path: Path,
  figsize: tuple = (12, 8)
) -> None:
  """Visualize the knowledge graph.
  
  Args:
    graph: NetworkxEntityGraph to visualize
    output_path: Output file path for the image
    figsize: Figure size (width, height)
  """
  try:
    import matplotlib.pyplot as plt
    import networkx as nx
  except ImportError:
    print("⚠ matplotlib not installed. Cannot visualize.")
    return
  
  # Access internal NetworkX graph
  nx_graph = graph._graph
  
  # Create visualization
  plt.figure(figsize=figsize)
  pos = nx.spring_layout(nx_graph, k=2, iterations=50)
  
  # Draw nodes
  nx.draw_networkx_nodes(
    nx_graph, pos,
    node_color='lightblue',
    node_size=3000,
    alpha=0.9
  )
  
  # Draw edges
  nx.draw_networkx_edges(
    nx_graph, pos,
    edge_color='gray',
    arrows=True,
    arrowsize=20,
    width=2
  )
  
  # Draw labels
  nx.draw_networkx_labels(nx_graph, pos, font_size=10, font_weight='bold')
  
  # Draw edge labels (relationships)
  edge_labels = nx.get_edge_attributes(nx_graph, 'relation')
  nx.draw_networkx_edge_labels(nx_graph, pos, edge_labels, font_size=8)
  
  plt.title("Knowledge Graph", fontsize=16, fontweight='bold')
  plt.axis('off')
  plt.tight_layout()
  
  plt.savefig(output_path, dpi=300, bbox_inches='tight')
  print(f"✅ Graph visualization saved to {output_path}")


# ============================================================================
# CLI Commands
# ============================================================================

def cmd_test(args: argparse.Namespace) -> int:
  """Test command - verify dependencies."""
  print("🧪 Testing LangChain Knowledge Graph Skill...")
  
  try:
    from langchain_community.graphs import NetworkxEntityGraph
    print("✅ LangChain Community import: OK")
  except ImportError as e:
    print(f"❌ LangChain Community import failed: {e}")
    return 1
  
  try:
    from langchain_openai import ChatOpenAI
    print("✅ LangChain OpenAI import: OK")
  except ImportError as e:
    print(f"❌ LangChain OpenAI import failed: {e}")
    return 1
  
  try:
    import networkx
    print("✅ NetworkX import: OK")
  except ImportError as e:
    print(f"❌ NetworkX import failed: {e}")
    return 1
  
  try:
    import matplotlib
    print("✅ Matplotlib import: OK")
  except ImportError as e:
    print(f"❌ Matplotlib import failed: {e}")
    return 1
  
  # Check API key
  if not os.getenv("OPENAI_API_KEY"):
    print("⚠ OPENAI_API_KEY not set (required for building graphs)")
    print("  Set it with: export OPENAI_API_KEY='your-key-here'")
  else:
    print("✅ OPENAI_API_KEY is set")
  
  print("\n✅ All dependencies available!")
  return 0


def cmd_build(args: argparse.Namespace) -> int:
  """Build command - create knowledge graph from documents."""
  input_path = Path(args.input)
  output_path = Path(args.output)
  
  if not input_path.exists():
    print(f"❌ Input path does not exist: {input_path}")
    return 1
  
  print(f"📚 Building knowledge graph from: {input_path}")
  
  try:
    builder = KnowledgeGraphBuilder(
      model=args.model,
      temperature=args.temperature
    )
    
    if input_path.is_file():
      text = input_path.read_text(encoding="utf-8")
      graph = builder.build_from_text(text)
    else:
      graph = builder.build_from_directory(
        input_path,
        extensions=args.extensions.split(",")
      )
    
    # Save graph
    graph.write_to_gml(str(output_path))
    
    # Show statistics
    query = KnowledgeGraphQuery(graph)
    stats = query.get_statistics()
    
    print(f"\n✅ Knowledge graph built successfully:")
    print(f"   Nodes: {stats['total_nodes']}")
    print(f"   Triples: {stats['total_triples']}")
    print(f"   Saved to: {output_path}")
    
    return 0
    
  except Exception as e:
    print(f"❌ Error building graph: {e}")
    import traceback
    traceback.print_exc()
    return 1


def cmd_query(args: argparse.Namespace) -> int:
  """Query command - query the knowledge graph."""
  graph_path = Path(args.graph)
  
  if not graph_path.exists():
    print(f"❌ Graph file does not exist: {graph_path}")
    return 1
  
  try:
    # Load graph
    graph = NetworkxEntityGraph.from_gml(str(graph_path))
    query_interface = KnowledgeGraphQuery(graph)
    
    if args.entity:
      # Query specific entity
      print(f"🔍 Querying entity: {args.entity}")
      info = query_interface.get_entity_info(args.entity, depth=args.depth)
      
      if not info:
        print(f"⚠ Entity '{args.entity}' not found in graph")
        
        # Suggest similar entities
        similar = query_interface.search_entity(args.entity)
        if similar:
          print(f"\nDid you mean one of these?")
          for entity in similar[:5]:
            print(f"  • {entity}")
        return 1
      
      print(f"\n✅ Found {len(info)} relationships:")
      for relationship in info:
        print(f"  • {relationship}")
    
    elif args.search:
      # Search for entities
      print(f"🔍 Searching for: {args.search}")
      results = query_interface.search_entity(args.search)
      
      if not results:
        print("⚠ No matching entities found")
        return 1
      
      print(f"\n✅ Found {len(results)} matching entities:")
      for entity in results:
        print(f"  • {entity}")
    
    elif args.stats:
      # Show statistics
      stats = query_interface.get_statistics()
      print("📊 Knowledge Graph Statistics:")
      print(f"   Total nodes: {stats['total_nodes']}")
      print(f"   Total triples: {stats['total_triples']}")
      print(f"   Total entities: {stats['total_entities']}")
      
      # Show sample entities
      entities = query_interface.get_all_entities()
      print(f"\n   Sample entities:")
      for entity in entities[:10]:
        print(f"     • {entity}")
      if len(entities) > 10:
        print(f"     ... and {len(entities) - 10} more")
    
    else:
      print("❌ Please specify --entity, --search, or --stats")
      return 1
    
    return 0
    
  except Exception as e:
    print(f"❌ Error querying graph: {e}")
    import traceback
    traceback.print_exc()
    return 1


def cmd_visualize(args: argparse.Namespace) -> int:
  """Visualize command - create graph visualization."""
  graph_path = Path(args.graph)
  output_path = Path(args.output)
  
  if not graph_path.exists():
    print(f"❌ Graph file does not exist: {graph_path}")
    return 1
  
  try:
    # Load graph
    graph = NetworkxEntityGraph.from_gml(str(graph_path))
    
    print(f"🎨 Creating visualization...")
    visualize_graph(graph, output_path, figsize=args.figsize)
    
    return 0
    
  except Exception as e:
    print(f"❌ Error visualizing graph: {e}")
    import traceback
    traceback.print_exc()
    return 1


# ============================================================================
# Main CLI
# ============================================================================

def main() -> int:
  """Main entry point."""
  parser = argparse.ArgumentParser(
    description="LangChain Knowledge Graph - Build and query knowledge graphs"
  )
  subparsers = parser.add_subparsers(dest="command", help="Command to run")
  
  # Test command
  subparsers.add_parser("test", help="Test dependencies")
  
  # Build command
  build_parser = subparsers.add_parser("build", help="Build knowledge graph")
  build_parser.add_argument(
    "input",
    help="Input file or directory"
  )
  build_parser.add_argument(
    "--output", "-o",
    default="knowledge_graph.gml",
    help="Output graph file (default: knowledge_graph.gml)"
  )
  build_parser.add_argument(
    "--model",
    default="gpt-4o-mini",
    help="OpenAI model to use (default: gpt-4o-mini)"
  )
  build_parser.add_argument(
    "--temperature",
    type=float,
    default=0.0,
    help="LLM temperature (default: 0.0)"
  )
  build_parser.add_argument(
    "--extensions",
    default=".md,.txt",
    help="File extensions to process (default: .md,.txt)"
  )
  
  # Query command
  query_parser = subparsers.add_parser("query", help="Query knowledge graph")
  query_parser.add_argument(
    "graph",
    help="Graph file to query"
  )
  query_parser.add_argument(
    "--entity", "-e",
    help="Entity to query"
  )
  query_parser.add_argument(
    "--search", "-s",
    help="Search for entities"
  )
  query_parser.add_argument(
    "--stats",
    action="store_true",
    help="Show graph statistics"
  )
  query_parser.add_argument(
    "--depth", "-d",
    type=int,
    default=1,
    help="Traversal depth for entity queries (default: 1)"
  )
  
  # Visualize command
  viz_parser = subparsers.add_parser("visualize", help="Visualize graph")
  viz_parser.add_argument(
    "graph",
    help="Graph file to visualize"
  )
  viz_parser.add_argument(
    "--output", "-o",
    default="knowledge_graph.png",
    help="Output image file (default: knowledge_graph.png)"
  )
  viz_parser.add_argument(
    "--figsize",
    type=lambda s: tuple(map(int, s.split(","))),
    default=(12, 8),
    help="Figure size as width,height (default: 12,8)"
  )
  
  args = parser.parse_args()
  
  if not args.command:
    parser.print_help()
    return 1
  
  # Dispatch to command
  commands = {
    "test": cmd_test,
    "build": cmd_build,
    "query": cmd_query,
    "visualize": cmd_visualize,
  }
  
  return commands[args.command](args)


if __name__ == "__main__":
  sys.exit(main())
