"""Command-line interface for LightRAG OpenSpec."""

import argparse
import asyncio
import sys
from pathlib import Path

from .config import LightRAGConfig, OpenSpecConfig
from .indexer import OpenSpecIndexer
from .query import OpenSpecQuery


def index_command(args):
    """CLI command to index OpenSpec memories."""
    print("🚀 LightRAG OpenSpec Indexer")
    print("=" * 70)
    print()

    # Load configuration with optional overrides
    lightrag_config = LightRAGConfig(
        working_dir=args.storage if hasattr(args, 'storage') and args.storage else None,
        llm_model=args.llm_model if hasattr(args, 'llm_model') and args.llm_model else "github_copilot/gpt-4o-mini",
    )
    openspec_config = OpenSpecConfig(
        memories_dir=args.source if hasattr(args, 'source') and args.source else None,
    )

    print(f"Source: {openspec_config.memories_dir}")
    print(f"Storage: {lightrag_config.working_dir}")
    print(f"LLM: {lightrag_config.llm_model}")
    print(f"Embeddings: {lightrag_config.embedding_model}")
    print()

    async def run_indexing():
        indexer = OpenSpecIndexer(lightrag_config, openspec_config)
        await indexer.initialize()

        print("📝 Indexing documents...")
        count = await indexer.index_files()

        await indexer.finalize()
        print()
        print(f"✅ Indexed {count} documents")

    asyncio.run(run_indexing())


def query_command(args):
    """CLI command to query OpenSpec memories."""
    print("🔍 LightRAG OpenSpec Query")
    print("=" * 70)
    print()

    # Load configuration with optional overrides
    config = LightRAGConfig(
        working_dir=args.storage if hasattr(args, 'storage') and args.storage else None,
        llm_model=args.llm_model if hasattr(args, 'llm_model') and args.llm_model else "github_copilot/gpt-4o-mini",
    )

    print(f"Storage: {config.working_dir}")
    print(f"LLM: {config.llm_model}")
    print()

    async def run_query():
        query_interface = OpenSpecQuery(config)
        await query_interface.initialize()

        # Batch mode if query provided
        if hasattr(args, 'query') and args.query:
            result = await query_interface.query(args.query, mode=args.mode)
            print(f"💡 Answer:\n{result}")
        else:
            # Interactive mode
            print("Type your question (or 'quit' to exit):")
            while True:
                try:
                    question = input("\n❓ Query: ").strip()

                    if question.lower() in ["quit", "exit", "q"]:
                        break

                    if not question:
                        continue

                    result = await query_interface.query(question, mode=args.mode)
                    print(f"\n💡 Answer:\n{result}")

                except KeyboardInterrupt:
                    print("\n")
                    break
                except Exception as e:
                    print(f"\n❌ Error: {e}")

        await query_interface.finalize()

    asyncio.run(run_query())


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        prog="lightrag-openspec",
        description="LightRAG OpenSpec - Knowledge graph-based RAG for OpenSpec memories"
    )
    
    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    
    # Index command
    index_parser = subparsers.add_parser(
        "index",
        help="Index OpenSpec markdown files"
    )
    index_parser.add_argument(
        "--source",
        help="Source directory containing markdown files (default: auto-detected)"
    )
    index_parser.add_argument(
        "--storage",
        help="Storage directory for knowledge graph (default: auto-detected)"
    )
    index_parser.add_argument(
        "--llm-model",
        help="LLM model to use (default: github_copilot/gpt-4o-mini)"
    )
    
    # Query command
    query_parser = subparsers.add_parser(
        "query",
        help="Query the knowledge base"
    )
    query_parser.add_argument(
        "query",
        nargs="?",
        help="Question to ask (if not provided, enters interactive mode)"
    )
    query_parser.add_argument(
        "--storage",
        help="Storage directory for knowledge graph (default: auto-detected)"
    )
    query_parser.add_argument(
        "--llm-model",
        help="LLM model to use (default: github_copilot/gpt-4o-mini)"
    )
    query_parser.add_argument(
        "--mode",
        choices=["naive", "local", "global", "hybrid"],
        default="hybrid",
        help="Search mode (default: hybrid)"
    )
    
    args = parser.parse_args()
    
    if args.command == "index":
        index_command(args)
    elif args.command == "query":
        query_command(args)
    else:
        parser.print_help()
        sys.exit(1)


def index_main():
    """Entry point for lightrag-index command."""
    # Inject 'index' as first argument if not present
    if len(sys.argv) == 1 or (len(sys.argv) > 1 and sys.argv[1] in ['--help', '-h']):
        sys.argv.insert(1, 'index')
    elif sys.argv[1] not in ['index', 'query']:
        sys.argv.insert(1, 'index')
    main()


def query_main():
    """Entry point for lightrag-query command."""
    # Inject 'query' as first argument if not present
    if len(sys.argv) == 1 or (len(sys.argv) > 1 and sys.argv[1] in ['--help', '-h']):
        sys.argv.insert(1, 'query')
    elif sys.argv[1] not in ['index', 'query']:
        sys.argv.insert(1, 'query')
    main()


if __name__ == "__main__":
    main()
