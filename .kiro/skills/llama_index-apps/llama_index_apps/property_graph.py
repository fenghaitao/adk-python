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

"""Property graph CLI using LlamaIndex PropertyGraphIndex.

Extracts typed entities and relations from documents using an LLM,
persists the graph as JSON, and supports natural language querying.
No external graph database required — uses SimplePropertyGraphStore.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

# Default storage directory for the persisted property graph.
DEFAULT_STORAGE_DIR = "./pg_storage"

# Default LLM model — GitHub Copilot via litellm requires no API key setup.
DEFAULT_MODEL = "github_copilot/gpt-4o"

# Default embedding model — GitHub Copilot text-embedding-3-small via litellm.
DEFAULT_EMBED_MODEL = "github_copilot/text-embedding-3-small"
EMBED_DIM = 1536


def _build_llm(model: str):
  """Build a LlamaIndex LLM backed by litellm.

  Routes all model calls through litellm, which handles GitHub Copilot
  oauth2 token exchange automatically for github_copilot/* models.
  OpenAI models require OPENAI_API_KEY in the environment.
  """
  from llama_index.llms.litellm import LiteLLM

  return LiteLLM(model=model)


def _build_embed_model(embed_model: str = DEFAULT_EMBED_MODEL):
  """Build a LlamaIndex embedding model backed by litellm.

  Routes embedding calls through litellm so GitHub Copilot oauth2
  token exchange is handled automatically, same as the LLM path.
  """
  from llama_index.embeddings.litellm import LiteLLMEmbedding

  return LiteLLMEmbedding(model_name=embed_model)


def _get_persist_path(storage_dir: str) -> str:
    """Return the JSON file path for the persisted property graph."""
    return str(Path(storage_dir) / "property_graph.json")


def cmd_build(args: argparse.Namespace) -> None:
    """Build a property graph from documents and persist it to disk."""
    from llama_index.core import Settings, SimpleDirectoryReader
    from llama_index.core.graph_stores.simple_labelled import (
        SimplePropertyGraphStore,
    )
    from llama_index.core.indices.property_graph import PropertyGraphIndex
    from llama_index.core.indices.property_graph.transformations import (
        DynamicLLMPathExtractor,
        ImplicitPathExtractor,
        SimpleLLMPathExtractor,
    )

    input_path = Path(args.input).resolve()
    if not input_path.exists():
        print(f"Input path not found: {input_path}")
        sys.exit(1)

    llm = _build_llm(args.model)
    embed_model = _build_embed_model()
    Settings.llm = llm
    Settings.embed_model = embed_model

    # Load documents from file or directory.
    if input_path.is_file():
        documents = SimpleDirectoryReader(input_files=[str(input_path)]).load_data()
    else:
        documents = SimpleDirectoryReader(str(input_path)).load_data()

    if not documents:
        print(f"No documents found in {input_path}")
        sys.exit(1)

    print(f"Loaded {len(documents)} document(s) from {input_path}")
    print(f"Building property graph with extractor: {args.extractor}")
    print(f"LLM: {args.model}")

    # Select extractor based on user choice.
    # simple: fast, extracts (subject, relation, object) triples.
    # implicit: no LLM calls, uses noun chunks and co-occurrence.
    # dynamic: LLM infers entity types and relation types dynamically.
    if args.extractor == "simple":
        extractors = [SimpleLLMPathExtractor(llm=llm)]
    elif args.extractor == "implicit":
        extractors = [ImplicitPathExtractor()]
    elif args.extractor == "dynamic":
        extractors = [DynamicLLMPathExtractor(llm=llm)]
    else:
        print(f"Unknown extractor: {args.extractor}. Use: simple, implicit, dynamic")
        sys.exit(1)

    # Disable KG node embedding when using implicit extractor since
    # it requires no LLM/embedding calls — embeddings are only useful
    # when a vector sub-retriever is also configured.
    embed_kg_nodes = args.extractor != "implicit"

    graph_store = SimplePropertyGraphStore()
    index = PropertyGraphIndex.from_documents(
        documents,
        kg_extractors=extractors,
        property_graph_store=graph_store,
        embed_kg_nodes=embed_kg_nodes,
        show_progress=True,
    )

    # Persist the graph to JSON.
    storage_dir = Path(args.output)
    storage_dir.mkdir(parents=True, exist_ok=True)
    persist_path = _get_persist_path(args.output)
    index.property_graph_store.persist(persist_path)

    # Report what was extracted.
    nodes = index.property_graph_store.get(ids=None, properties=None)
    triplets = index.property_graph_store.get_triplets(
        entity_names=[n.id for n in nodes if hasattr(n, "name")]
    )
    print(f"\nGraph built successfully:")
    print(f"  Nodes:    {len(nodes)}")
    print(f"  Saved to: {persist_path}")


def cmd_query(args: argparse.Namespace) -> None:
    """Query the persisted property graph with natural language."""
    from llama_index.core import Settings
    from llama_index.core.graph_stores.simple_labelled import (
        SimplePropertyGraphStore,
    )
    from llama_index.core.indices.property_graph import PropertyGraphIndex

    persist_path = _get_persist_path(args.storage_dir)
    if not Path(persist_path).exists():
        print(f"No graph found at {persist_path}")
        print(f"Run 'property-graph build' first.")
        sys.exit(1)

    llm = _build_llm(args.model)
    embed_model = _build_embed_model()
    Settings.llm = llm
    Settings.embed_model = embed_model

    graph_store = SimplePropertyGraphStore.from_persist_path(persist_path)
    index = PropertyGraphIndex.from_existing(
        property_graph_store=graph_store,
    )

    retriever = index.as_retriever(
        include_text=True,
    )

    print(f"\nQuerying: {args.query}")
    print("=" * 60)

    nodes = retriever.retrieve(args.query)
    if not nodes:
        print("No results found.")
        return

    for i, node in enumerate(nodes, 1):
        print(f"\n--- Result {i} ---")
        print(node.get_content())


def cmd_inspect(args: argparse.Namespace) -> None:
    """Inspect nodes and triplets in the persisted property graph."""
    from llama_index.core.graph_stores.simple_labelled import (
        SimplePropertyGraphStore,
    )
    from llama_index.core.graph_stores.types import EntityNode

    persist_path = _get_persist_path(args.storage_dir)
    if not Path(persist_path).exists():
        print(f"No graph found at {persist_path}")
        print(f"Run 'property-graph build' first.")
        sys.exit(1)

    graph_store = SimplePropertyGraphStore.from_persist_path(persist_path)
    all_nodes = graph_store.get(ids=None, properties=None)

    entity_nodes = [n for n in all_nodes if isinstance(n, EntityNode)]

    # Retrieve triplets for all entity nodes.
    triplets = graph_store.get_triplets(
        entity_names=[n.id for n in entity_nodes]
    ) if entity_nodes else []

    print(f"\n{'='*60}")
    print(f"PROPERTY GRAPH SUMMARY")
    print(f"{'='*60}")
    print(f"  Total nodes:    {len(all_nodes)}")
    print(f"  Entity nodes:   {len(entity_nodes)}")
    print(f"  Triplets:       {len(triplets)}")

    if entity_nodes:
        print(f"\n{'='*60}")
        print("ENTITY NODES")
        print("=" * 60)
        for node in entity_nodes:
            label = getattr(node, "label", "")
            props = node.properties or {}
            print(f"  [{node.id}]  label={label}  props={props}")

    if triplets:
        print(f"\n{'='*60}")
        print("TRIPLETS (subject, relation, object)")
        print("=" * 60)
        for subj, rel, obj in triplets:
            print(f"  ({subj.id})  --[{rel.id}]-->  ({obj.id})")


def main() -> None:
    """Entry point for the property-graph CLI."""
    parser = argparse.ArgumentParser(
        prog="property-graph",
        description=(
            "Property graph using LlamaIndex PropertyGraphIndex. "
            "Extracts typed entities and relations from documents via LLM."
        ),
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    # build subcommand
    p_build = subparsers.add_parser(
        "build",
        help="Build a property graph from documents",
    )
    p_build.add_argument(
        "input",
        help="Input file or directory containing documents",
    )
    p_build.add_argument(
        "--output",
        "-o",
        default=DEFAULT_STORAGE_DIR,
        help=f"Storage directory for the graph (default: {DEFAULT_STORAGE_DIR})",
    )
    p_build.add_argument(
        "--extractor",
        "-e",
        default="simple",
        choices=["simple", "implicit", "dynamic"],
        help=(
            "Extractor to use: simple (LLM triples), "
            "implicit (no LLM, noun chunks), "
            "dynamic (LLM with inferred types). Default: simple"
        ),
    )
    p_build.add_argument(
        "--model",
        "-m",
        default=DEFAULT_MODEL,
        help=f"LLM model (default: {DEFAULT_MODEL})",
    )
    p_build.set_defaults(func=cmd_build)

    # query subcommand
    p_query = subparsers.add_parser(
        "query",
        help="Query the property graph with natural language",
    )
    p_query.add_argument(
        "query",
        help="Natural language query",
    )
    p_query.add_argument(
        "--storage-dir",
        "-s",
        default=DEFAULT_STORAGE_DIR,
        help=f"Storage directory of the graph (default: {DEFAULT_STORAGE_DIR})",
    )
    p_query.add_argument(
        "--model",
        "-m",
        default=DEFAULT_MODEL,
        help=f"LLM model (default: {DEFAULT_MODEL})",
    )
    p_query.set_defaults(func=cmd_query)

    # inspect subcommand
    p_inspect = subparsers.add_parser(
        "inspect",
        help="Inspect nodes and triplets in the persisted graph",
    )
    p_inspect.add_argument(
        "--storage-dir",
        "-s",
        default=DEFAULT_STORAGE_DIR,
        help=f"Storage directory of the graph (default: {DEFAULT_STORAGE_DIR})",
    )
    p_inspect.set_defaults(func=cmd_inspect)

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
