#!/usr/bin/env python3
# /// script
# requires-python = ">=3.10,<3.13"
# dependencies = [
#     "graphrag>=2.7.0",
#     "pyyaml>=6.0.0",
#     "typer>=0.16.0",
# ]
# ///
"""
GraphRAG Memory - Knowledge Graph Indexing and Retrieval

A self-contained script for building knowledge graphs from markdown documents
and querying them with GraphRAG.

Usage:
    # Initialize GraphRAG project
    uv run graphrag_memory.py init
    
    # Index documents
    uv run graphrag_memory.py index --input openspec-memories
    
    # Query with local search
    uv run graphrag_memory.py query "How to implement timer?" --method local
    
    # Query with global search
    uv run graphrag_memory.py query "What are the main concepts?" --method global

Features:
- GraphRAG knowledge graph construction
- Multiple query methods (local, global, drift)
- GitHub Copilot and OpenAI LLM support
- Automatic prompt management
- Self-contained with inline dependencies
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

import sys
import os
import shutil
import subprocess
from pathlib import Path
from typing import Optional
import typer
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn

console = Console()
app = typer.Typer(
    help="GraphRAG Memory - Knowledge Graph Indexing and Retrieval",
    add_completion=False,
)


# ============================================================================
# Helper Functions
# ============================================================================

def run_graphrag_command(
    command: list[str],
    cwd: Optional[Path] = None,
    verbose: bool = False
) -> tuple[int, str, str]:
    """Run a graphrag CLI command and return results."""
    # Use python -m graphrag to ensure it runs in the same environment
    cmd = [sys.executable, "-m", "graphrag"] + command
    
    if verbose:
        console.print(f"[dim]Running: {' '.join(cmd)}[/dim]")
    
    try:
        result = subprocess.run(
            cmd,
            cwd=cwd or Path.cwd(),
            capture_output=True,
            text=True,
            check=False
        )
        return result.returncode, result.stdout, result.stderr
    except Exception as e:
        return 1, "", str(e)


def check_graphrag_installed() -> bool:
    """Check if graphrag is importable."""
    try:
        import graphrag
        return True
    except ImportError:
        return False


def find_root_dir() -> Optional[Path]:
    """Find GraphRAG root directory (contains settings.yaml)."""
    current = Path.cwd()
    
    # Check current directory
    if (current / "settings.yaml").exists():
        return current
    
    # Check common locations
    for subdir in [".", ".graphrag", "graphrag_data"]:
        path = current / subdir
        if (path / "settings.yaml").exists():
            return path
    
    return None


def create_minimal_prompts(prompts_dir: Path):
    """Create minimal default prompts for GraphRAG."""
    
    # Entity extraction prompt
    (prompts_dir / "extract_graph.txt").write_text("""
-Target activity-
You are an intelligent assistant that helps a human analyst perform information discovery.
Information discovery is the process of identifying and assessing relevant information from text.

-Goal-
Given a text document, identify all entities and relationships between them.
For each entity, extract:
- entity_name: Name of the entity
- entity_type: One of [organization, person, location, event, concept]
- description: Comprehensive description of the entity

For each relationship, extract:
- source: Source entity name
- target: Target entity name
- relationship: Description of the relationship
- strength: Numeric weight of relationship (1-10)

Return JSON format.
""".strip())
    
    # Community report prompt
    (prompts_dir / "community_report_text.txt").write_text("""
You are an AI assistant that helps analysts understand communities detected in a knowledge graph.

-Goal-
Write a comprehensive report on a community, given a list of entities in it.
The report should include:
- Title: Short descriptive title
- Summary: Overview of the community's main theme
- Key entities: Most important entities and their roles
- Relationships: How entities are connected
- Significance: Why this community is important

Return markdown format.
""".strip())
    
    # Local search prompt
    (prompts_dir / "local_search_system_prompt.txt").write_text("""
You are an AI assistant helping answer questions based on a knowledge graph.

Use the provided entities, relationships, and text chunks to answer the question.
Cite sources when possible.
If information is not in the provided data, say so.
""".strip())
    
    # Global search prompts
    (prompts_dir / "global_search_map_system_prompt.txt").write_text("""
You are an AI assistant helping with global search over communities.

Given community summaries, extract relevant points that help answer the question.
Return concise key points from each community.
""".strip())
    
    (prompts_dir / "global_search_reduce_system_prompt.txt").write_text("""
You are an AI assistant helping synthesize information from multiple communities.

Given points from different communities, synthesize them into a comprehensive answer.
Organize information logically and cite community sources.
""".strip())
    
    # Summarize descriptions
    (prompts_dir / "summarize_descriptions.txt").write_text("""
You are an AI assistant that helps summarize entity descriptions.

Given multiple descriptions of the same entity, create a single comprehensive summary.
Preserve key information and remove redundancies.
""".strip())
    
    console.print(f"[dim]Created 6 minimal prompt templates[/dim]")


# ============================================================================
# CLI Commands
# ============================================================================

@app.command()
def test():
    """Test if GraphRAG dependencies are available."""
    console.print("🧪 [bold]Testing GraphRAG Memory Skill...[/bold]\n")
    
    # Test imports
    try:
        import graphrag
        console.print("✅ GraphRAG import: [green]OK[/green]")
    except ImportError:
        console.print("❌ GraphRAG import: [red]FAILED[/red]")
        console.print("\n[yellow]Tip:[/yellow] Run with 'uv run' to auto-install dependencies")
        raise typer.Exit(1)
    
    try:
        import yaml
        console.print("✅ YAML import: [green]OK[/green]")
    except ImportError:
        console.print("❌ YAML import: [red]FAILED[/red]")
        raise typer.Exit(1)
    
    try:
        import typer as _typer
        console.print("✅ Typer import: [green]OK[/green]")
    except ImportError:
        console.print("❌ Typer import: [red]FAILED[/red]")
        raise typer.Exit(1)
    
    console.print("\n✅ [bold green]All dependencies available![/bold green]")
    console.print("\n[bold]Next steps:[/bold]")
    console.print("  1. Initialize: uv run graphrag_memory.py init")
    console.print("  2. Index: uv run graphrag_memory.py index --input openspec-memories")
    console.print("  3. Query: uv run graphrag_memory.py query 'your question'")


@app.command()
def init(
    root: Path = typer.Option(
        Path.cwd(),
        "--root",
        "-r",
        help="Root directory for GraphRAG project"
    ),
    force: bool = typer.Option(
        False,
        "--force",
        "-f",
        help="Force reinitialization"
    ),
):
    """Initialize a GraphRAG project with default settings."""
    console.print("📚 [bold]Initializing GraphRAG Project...[/bold]\n")
    
    root = root.resolve()
    settings_file = root / "settings.yaml"
    prompts_dir = root / "prompts"
    
    # Check if already initialized
    if settings_file.exists() and not force:
        console.print(f"⚠️  [yellow]Project already initialized at {root}[/yellow]")
        console.print("   Use --force to reinitialize")
        raise typer.Exit(0)
    
    # Create directories
    root.mkdir(parents=True, exist_ok=True)
    (root / "input").mkdir(parents=True, exist_ok=True)
    (root / "output").mkdir(parents=True, exist_ok=True)
    (root / "cache").mkdir(parents=True, exist_ok=True)
    prompts_dir.mkdir(parents=True, exist_ok=True)
    
    # Copy settings.yaml from skill references
    console.print("[dim]Creating settings.yaml...[/dim]")
    
    script_path = Path(__file__).resolve()
    ref_settings = script_path.parent.parent / "references" / "settings.yaml"
    
    if ref_settings.exists():
        import shutil
        shutil.copy2(ref_settings, settings_file)
        console.print("[dim]Copied settings from references[/dim]")
    else:
        # Fallback to embedded default
        console.print("[dim]Creating default settings.yaml...[/dim]")
        default_settings = """### GraphRAG Configuration with GitHub Copilot
### Edit this file to configure your LLM and embedding models

### LLM settings ###
completion_models:
  default_completion_model:
    type: chat
    model_provider: github_copilot
    auth_type: api_key
    api_key: copilot
    model: gpt-4o
    model_supports_json: true
    concurrent_requests: 5
    async_mode: threaded
    max_retries: 10
    tokens_per_minute: 60000
    requests_per_minute: 30
    
embedding_models:
  default_embedding_model:
    type: embedding
    model_provider: github_copilot
    auth_type: api_key
    api_key: copilot
    model: text-embedding-3-small
    concurrent_requests: 5
    async_mode: threaded
    max_retries: 10
    tokens_per_minute: 60000
    requests_per_minute: 30

### Input settings ###
input:
  storage:
    type: file
    base_dir: "input"
  file_type: text
  file_pattern: ".*\\\\.md"

chunks:
  size: 1500
  overlap: 150
  group_by_columns: [id]

### Output/storage settings ###
output:
  type: file
  base_dir: "output"
    
cache:
  type: none

reporting:
  type: file
  base_dir: "logs"

vector_store:
  default_vector_store:
    type: lancedb
    db_uri: output/lancedb
    container_name: default

### Workflow settings ###
embed_text:
  model_id: default_embedding_model
  vector_store_id: default_vector_store

extract_graph:
  model_id: default_completion_model
  entity_types: [organization,person,geo,event]
  max_gleanings: 1

summarize_descriptions:
  model_id: default_completion_model
  max_length: 500

cluster_graph:
  max_cluster_size: 10

extract_claims:
  enabled: false
  model_id: default_completion_model

community_reports:
  model_id: default_completion_model
  max_length: 2000
  max_input_length: 8000

### Query settings ###
local_search:
  completion_model_id: default_completion_model
  embedding_model_id: default_embedding_model

global_search:
  completion_model_id: default_completion_model

drift_search:
  completion_model_id: default_completion_model
  embedding_model_id: default_embedding_model
"""
        settings_file.write_text(default_settings)
    
    # Copy default prompts from the skill's references folder
    console.print("[dim]Creating default prompts...[/dim]")
    
    # Find prompts in the skill's references/prompts directory
    script_path = Path(__file__).resolve()
    skill_prompts = script_path.parent.parent / "references" / "prompts"
    
    if skill_prompts.exists() and list(skill_prompts.glob("*.txt")):
        # Copy prompts from skill references
        import shutil
        copied = 0
        for prompt_file in skill_prompts.glob("*.txt"):
            shutil.copy2(prompt_file, prompts_dir / prompt_file.name)
            copied += 1
        console.print(f"[dim]Copied {copied} prompt templates[/dim]")
    else:
        # Fallback to minimal prompts if references not found
        console.print("[dim]Reference prompts not found, creating minimal defaults[/dim]")
        create_minimal_prompts(prompts_dir)
    
    console.print(f"\n✅ [green]Initialized GraphRAG project at {root}[/green]")
    console.print("\n[bold]Created:[/bold]")
    try:
        console.print(f"  • {settings_file.relative_to(Path.cwd())}")
        console.print(f"  • {prompts_dir.relative_to(Path.cwd())}/")
        console.print(f"  • {(root / 'input').relative_to(Path.cwd())}/")
        console.print(f"  • {(root / 'output').relative_to(Path.cwd())}/")
    except ValueError:
        console.print(f"  • {settings_file}")
        console.print(f"  • {prompts_dir}/")
        console.print(f"  • {root / 'input'}/")
        console.print(f"  • {root / 'output'}/")
    
    console.print("\n[bold]Next steps:[/bold]")
    console.print("  1. Copy markdown files to input/")
    console.print("  2. Edit settings.yaml to configure LLM (GitHub Copilot by default)")
    console.print("  3. Run: uv run graphrag_memory.py index")


@app.command()
def index(
    root: Path = typer.Option(
        None,
        "--root",
        "-r",
        help="Root directory (auto-detected if not specified)"
    ),
    input_dir: Optional[Path] = typer.Option(
        None,
        "--input",
        "-i",
        help="Input directory containing markdown files"
    ),
    verbose: bool = typer.Option(
        False,
        "--verbose",
        "-v",
        help="Verbose output"
    ),
):
    """Index documents to build knowledge graph."""
    console.print("🔨 [bold]Indexing Documents...[/bold]\n")
    
    # Find or use root directory
    if root is None:
        root = find_root_dir()
        if root is None:
            console.print("❌ [red]No GraphRAG project found[/red]")
            console.print("   Run 'init' command first or specify --root")
            raise typer.Exit(1)
    
    root = root.resolve()
    
    if not (root / "settings.yaml").exists():
        console.print(f"❌ [red]No settings.yaml found in {root}[/red]")
        console.print("   Run 'init' command first")
        raise typer.Exit(1)
    
    # Copy input files if specified
    if input_dir:
        input_dir = input_dir.resolve()
        target_input = root / "input"
        
        if not input_dir.exists():
            console.print(f"❌ [red]Input directory not found: {input_dir}[/red]")
            raise typer.Exit(1)
        
        console.print(f"📁 Copying files from {input_dir} to {target_input}")
        
        # Copy markdown files
        md_files = list(input_dir.glob("**/*.md"))
        for md_file in md_files:
            relative_path = md_file.relative_to(input_dir)
            target_file = target_input / relative_path
            target_file.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(md_file, target_file)
        
        console.print(f"   Copied {len(md_files)} markdown files")
    
    # Count input files
    input_files = list((root / "input").glob("**/*.md"))
    console.print(f"📄 Found {len(input_files)} markdown files to index\n")
    
    if len(input_files) == 0:
        console.print("⚠️  [yellow]No markdown files found in input/[/yellow]")
        console.print("   Copy files to input/ directory first")
        raise typer.Exit(0)
    
    # Run indexing
    console.print("[bold]Starting indexing...[/bold]")
    console.print("[dim]This may take several minutes depending on data size[/dim]\n")
    
    cmd = ["index", "--root", str(root)]
    if verbose:
        cmd.append("--verbose")
    
    returncode, stdout, stderr = run_graphrag_command(cmd, cwd=root, verbose=True)
    
    if returncode != 0:
        console.print(f"\n❌ [red]Indexing failed[/red]")
        console.print(f"[dim]{stderr}[/dim]")
        raise typer.Exit(1)
    
    console.print(f"\n✅ [green]Successfully indexed documents![/green]")
    console.print(f"   Output: {root / 'output'}")
    console.print("\n[bold]Next step:[/bold]")
    console.print("  Query: uv run graphrag_memory.py query 'your question'")


@app.command()
def query(
    question: str = typer.Argument(..., help="Question to ask"),
    root: Path = typer.Option(
        None,
        "--root",
        "-r",
        help="Root directory (auto-detected if not specified)"
    ),
    method: str = typer.Option(
        "local",
        "--method",
        "-m",
        help="Search method: local, global, or drift"
    ),
    verbose: bool = typer.Option(
        False,
        "--verbose",
        "-v",
        help="Verbose output"
    ),
):
    """Query the knowledge graph."""
    console.print(f"🔍 [bold]GraphRAG {method.title()} Search[/bold]\n")
    
    # Find or use root directory
    if root is None:
        root = find_root_dir()
        if root is None:
            console.print("❌ [red]No GraphRAG project found[/red]")
            console.print("   Run 'init' command first or specify --root")
            raise typer.Exit(1)
    
    root = root.resolve()
    
    # Check if indexed
    if not (root / "output").exists() or not list((root / "output").iterdir()):
        console.print("❌ [red]No indexed data found[/red]")
        console.print("   Run 'index' command first")
        raise typer.Exit(1)
    
    console.print(f"[dim]Query: {question}[/dim]")
    console.print(f"[dim]Method: {method}[/dim]\n")
    
    # Run query
    cmd = ["query", "--root", str(root), "--method", method, "--query", question]
    if verbose:
        cmd.append("--verbose")
    
    returncode, stdout, stderr = run_graphrag_command(cmd, cwd=root, verbose=True)
    
    if returncode != 0:
        console.print(f"\n❌ [red]Query failed[/red]")
        console.print(f"[dim]{stderr}[/dim]")
        raise typer.Exit(1)
    
    # Print results
    console.print("\n[bold green]Results:[/bold green]")
    console.print(stdout)


@app.command()
def status(
    root: Path = typer.Option(
        None,
        "--root",
        "-r",
        help="Root directory (auto-detected if not specified)"
    ),
):
    """Show GraphRAG project status."""
    console.print("📊 [bold]GraphRAG Project Status[/bold]\n")
    
    # Find or use root directory
    if root is None:
        root = find_root_dir()
        if root is None:
            console.print("❌ [red]No GraphRAG project found[/red]")
            raise typer.Exit(1)
    
    root = root.resolve()
    
    # Check components
    console.print(f"[bold]Project Root:[/bold] {root}\n")
    
    settings_file = root / "settings.yaml"
    if settings_file.exists():
        console.print("✅ settings.yaml: [green]Found[/green]")
    else:
        console.print("❌ settings.yaml: [red]Not found[/red]")
    
    prompts_dir = root / "prompts"
    if prompts_dir.exists() and list(prompts_dir.iterdir()):
        console.print(f"✅ prompts/: [green]Found ({len(list(prompts_dir.iterdir()))} files)[/green]")
    else:
        console.print("❌ prompts/: [red]Not found or empty[/red]")
    
    input_dir = root / "input"
    if input_dir.exists():
        md_files = list(input_dir.glob("**/*.md"))
        console.print(f"✅ input/: [green]Found ({len(md_files)} .md files)[/green]")
    else:
        console.print("❌ input/: [red]Not found[/red]")
    
    output_dir = root / "output"
    if output_dir.exists() and list(output_dir.iterdir()):
        console.print(f"✅ output/: [green]Indexed data present[/green]")
    else:
        console.print("⚠️  output/: [yellow]No indexed data[/yellow]")
    
    cache_dir = root / "cache"
    if cache_dir.exists():
        cache_size = sum(f.stat().st_size for f in cache_dir.rglob("*") if f.is_file())
        cache_mb = cache_size / (1024 * 1024)
        console.print(f"✅ cache/: [green]{cache_mb:.1f} MB[/green]")
    else:
        console.print("⚠️  cache/: [yellow]Not found[/yellow]")


if __name__ == "__main__":
    app()
