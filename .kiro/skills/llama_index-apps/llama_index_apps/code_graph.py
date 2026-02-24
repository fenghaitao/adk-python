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

"""Code graph CLI using LlamaIndex CodeHierarchyNodeParser (tree-sitter).

Parses source code into a scope hierarchy without requiring an LLM.
Supports repo map generation and keyword-based code lookup.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path


# Language to file extension mapping for SimpleDirectoryReader filtering.
_LANGUAGE_EXTENSIONS: dict[str, list[str]] = {
    "python": [".py"],
    "javascript": [".js", ".mjs"],
    "typescript": [".ts", ".tsx"],
    "java": [".java"],
    "go": [".go"],
    "rust": [".rs"],
    "c": [".c", ".h"],
    "cpp": [".cpp", ".cc", ".cxx", ".hpp"],
    "ruby": [".rb"],
    "c_sharp": [".cs"],
}


def _load_nodes(root: str, language: str):
    """Load and parse source files into code hierarchy nodes.

    Uses SimpleDirectoryReader to discover files and
    CodeHierarchyNodeParser to build the scope tree via tree-sitter.
    """
    from llama_index.core import SimpleDirectoryReader
    from llama_index.packs.code_hierarchy import CodeHierarchyNodeParser

    extensions = _LANGUAGE_EXTENSIONS.get(language)
    if not extensions:
        print(
            f"Unsupported language: {language}. "
            f"Supported: {', '.join(_LANGUAGE_EXTENSIONS)}"
        )
        sys.exit(1)

    root_path = Path(root).resolve()
    if not root_path.exists():
        print(f"Path not found: {root_path}")
        sys.exit(1)

    # Collect all matching files recursively.
    input_files = [
        str(p)
        for p in root_path.rglob("*")
        if p.suffix in extensions and p.is_file()
    ]

    if not input_files:
        print(f"No {language} files found in {root_path}")
        sys.exit(1)

    print(f"Found {len(input_files)} {language} file(s) in {root_path}")

    # filepath metadata is required by CodeHierarchyNodeParser to build
    # the repo map hierarchy keyed by file path segments.
    documents = SimpleDirectoryReader(
        input_files=input_files,
        file_metadata=lambda x: {"filepath": x},
    ).load_data()

    nodes = CodeHierarchyNodeParser(
        language=language,
        skeleton=True,
    ).get_nodes_from_documents(documents)

    print(f"Parsed into {len(nodes)} scope node(s)")
    return nodes


def cmd_map(args: argparse.Namespace) -> None:
    """Generate a markdown repo map of the codebase scope hierarchy."""
    from llama_index.packs.code_hierarchy import CodeHierarchyNodeParser

    nodes = _load_nodes(args.root, args.language)
    _, markdown = CodeHierarchyNodeParser.get_code_hierarchy_from_nodes(
        nodes, max_depth=args.depth
    )

    if args.output:
        Path(args.output).write_text(markdown)
        print(f"Repo map saved to {args.output}")
    else:
        print("\n" + "=" * 60)
        print("REPO MAP")
        print("=" * 60)
        print(markdown)


def cmd_query(args: argparse.Namespace) -> None:
    """Query the code hierarchy by function/class name or node UUID."""
    from llama_index.packs.code_hierarchy import CodeHierarchyKeywordQueryEngine

    nodes = _load_nodes(args.root, args.language)
    engine = CodeHierarchyKeywordQueryEngine(nodes=nodes)

    result = engine.custom_query(args.name)
    if result is None:
        print(f"No node found for: {args.name}")
        print("\nTip: run 'code-graph map' to see available names.")
        sys.exit(1)

    print("\n" + "=" * 60)
    print(f"RESULT: {args.name}")
    print("=" * 60)
    print(result)


def cmd_inspect(args: argparse.Namespace) -> None:
    """Inspect metadata of all parsed scope nodes."""
    nodes = _load_nodes(args.root, args.language)

    print(f"\n{'='*60}")
    print(f"NODES ({len(nodes)} total)")
    print("=" * 60)
    for node in nodes:
        scopes = node.metadata.get("inclusive_scopes", [])
        scope_path = " > ".join(s["name"] for s in scopes) if scopes else "<module>"
        print(f"  [{node.node_id[:8]}]  {scope_path}")
        print(f"           file: {node.metadata.get('filepath', '?')}")
        print(
            f"           bytes: {node.metadata.get('start_byte', '?')}"
            f" - {node.metadata.get('end_byte', '?')}"
        )
        print()


def main() -> None:
    """Entry point for the code-graph CLI."""
    parser = argparse.ArgumentParser(
        prog="code-graph",
        description=(
            "Code graph using LlamaIndex CodeHierarchyNodeParser (tree-sitter). "
            "Parses source code into a navigable scope hierarchy."
        ),
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    # Shared arguments across subcommands.
    shared = argparse.ArgumentParser(add_help=False)
    shared.add_argument(
        "--root",
        default=".",
        help="Root directory to parse (default: current directory)",
    )
    shared.add_argument(
        "--language",
        default="python",
        help=(
            f"Programming language (default: python). "
            f"Supported: {', '.join(_LANGUAGE_EXTENSIONS)}"
        ),
    )

    # map subcommand
    p_map = subparsers.add_parser(
        "map",
        parents=[shared],
        help="Generate a markdown repo map of the scope hierarchy",
    )
    p_map.add_argument(
        "--output",
        "-o",
        default=None,
        help="Save repo map to this file (default: print to stdout)",
    )
    p_map.add_argument(
        "--depth",
        "-d",
        type=int,
        default=-1,
        help="Max depth of the hierarchy (-1 for unlimited, default: -1)",
    )
    p_map.set_defaults(func=cmd_map)

    # query subcommand
    p_query = subparsers.add_parser(
        "query",
        parents=[shared],
        help="Look up a scope by name or UUID",
    )
    p_query.add_argument(
        "name",
        help="Function/class name or node UUID to look up",
    )
    p_query.set_defaults(func=cmd_query)

    # inspect subcommand
    p_inspect = subparsers.add_parser(
        "inspect",
        parents=[shared],
        help="List all parsed scope nodes with metadata",
    )
    p_inspect.set_defaults(func=cmd_inspect)

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
