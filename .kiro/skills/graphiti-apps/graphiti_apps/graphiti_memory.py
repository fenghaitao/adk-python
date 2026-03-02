"""
Graphiti Memory - Knowledge graph indexing and retrieval using Graphiti + Neo4j.

Supports:
- Ingesting text files, directories, and raw text into a Neo4j knowledge graph
- LLM-powered entity and relationship extraction via Graphiti
- Semantic search and natural language querying
- Group-scoped entity isolation for multi-domain graphs
- Community detection (intra-group and inter-group)
- Graph statistics and management
"""

from __future__ import annotations

import asyncio
import hashlib
import json
import logging
import os
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Optional

import typer
from dotenv import load_dotenv
from rich.console import Console
from rich.table import Table

load_dotenv(override=True)

app = typer.Typer(
    name="graphiti-memory",
    help="Knowledge graph indexing and retrieval using Graphiti + Neo4j.",
    no_args_is_help=True,
)
console = Console()

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _get_neo4j_creds() -> tuple[str, str, str]:
  """Return (uri, user, password) from environment, respecting NEO4J_PROFILE."""
  profile = os.getenv("NEO4J_PROFILE", "local").lower()
  if profile == "cloud":
    uri = os.getenv("NEO4J_URI_CLOUD", "")
    user = os.getenv("NEO4J_USERNAME_CLOUD", "neo4j")
    pwd = os.getenv("NEO4J_PASSWORD_CLOUD", "")
  elif profile == "docker":
    uri = os.getenv(
        "NEO4J_URI_DOCKER", "bolt://host.docker.internal:7687"
    )
    user = os.getenv("NEO4J_USERNAME_DOCKER", "neo4j")
    pwd = os.getenv("NEO4J_PASSWORD_DOCKER", "password")
  else:
    uri = os.getenv("NEO4J_URI_LOCAL", "bolt://localhost:7687")
    user = os.getenv("NEO4J_USERNAME_LOCAL", "neo4j")
    pwd = os.getenv("NEO4J_PASSWORD_LOCAL", "password")
  return uri, user, pwd


def _build_graphiti_client():
  """Construct and return an initialised GraphitiClient."""
  # Import here so the module can be imported without graphiti installed.
  from graphiti_core import Graphiti
  from graphiti_core.cross_encoder.openai_reranker_client import (
      OpenAIRerankerClient,
  )
  from graphiti_core.embedder.openai import OpenAIEmbedder, OpenAIEmbedderConfig
  from graphiti_core.llm_client.config import LLMConfig
  from graphiti_core.llm_client.openai_client import OpenAIClient
  from graphiti_core.llm_client.openai_generic_client import OpenAIGenericClient

  uri, user, pwd = _get_neo4j_creds()
  if not pwd:
    console.print(
        "[red]NEO4J_PASSWORD not set. Configure NEO4J_PASSWORD_LOCAL (or"
        " _DOCKER / _CLOUD) in your .env file.[/red]"
    )
    raise typer.Exit(1)

  llm_choice = os.getenv("LLM_CHOICE", "gpt-4o-mini")
  embedding_model = os.getenv(
      "EMBEDDING_MODEL_CHOICE", "text-embedding-3-small"
  )
  llm_api_key = os.getenv("LLM_API_KEY", "not-needed")
  embedding_api_key = os.getenv("EMBEDDING_API_KEY", llm_api_key)
  embedding_dims = int(os.getenv("VECTOR_DIMENSION", "1536"))

  # GitHub Copilot / LiteLLM path uses custom async clients to avoid
  # needing a direct OpenAI key while still satisfying Graphiti's interface.
  if llm_choice.startswith("github_copilot/"):
    from graphiti_apps.litellm_clients import (
        LiteLLMGraphitiClient,
        LiteLLMGraphitiEmbedder,
    )

    llm_config = LLMConfig(
        api_key="litellm-direct",
        model=llm_choice,
        small_model=llm_choice,
        base_url="https://api.openai.com/v1",
    )
    llm_client = OpenAIGenericClient(
        config=llm_config, client=LiteLLMGraphitiClient(model=llm_choice)
    )
    if embedding_model.startswith("github_copilot/"):
      embedder = LiteLLMGraphitiEmbedder(
          model=embedding_model, dimensions=embedding_dims
      )
    else:
      embedder = OpenAIEmbedder(
          config=OpenAIEmbedderConfig(
              api_key=embedding_api_key,
              embedding_model=embedding_model,
              embedding_dim=embedding_dims,
          )
      )
  else:
    llm_config = LLMConfig(
        api_key=llm_api_key,
        model=llm_choice,
        small_model=llm_choice,
        base_url=os.getenv("LLM_BASE_URL", "https://api.openai.com/v1"),
    )
    llm_client = OpenAIClient(config=llm_config)
    embedder = OpenAIEmbedder(
        config=OpenAIEmbedderConfig(
            api_key=embedding_api_key,
            embedding_model=embedding_model,
            embedding_dim=embedding_dims,
        )
    )

  graphiti = Graphiti(
      uri,
      user,
      pwd,
      llm_client=llm_client,
      embedder=embedder,
      cross_encoder=OpenAIRerankerClient(
          client=llm_client, config=llm_config
      ),
  )
  return graphiti


async def _init_graphiti(graphiti) -> None:
  """Build indices and constraints (idempotent)."""
  await graphiti.build_indices_and_constraints()


def _doc_id(path: str) -> str:
  return hashlib.md5(path.encode()).hexdigest()[:12]


def _chunk_text(text: str, size: int, overlap: int) -> list[str]:
  """Split text into overlapping chunks."""
  chunks = []
  start = 0
  while start < len(text):
    end = start + size
    chunks.append(text[start:end])
    start += size - overlap
  return chunks


# ---------------------------------------------------------------------------
# Commands
# ---------------------------------------------------------------------------


@app.command()
def test():
  """Verify dependencies and Neo4j connectivity."""
  console.print("[bold]Checking graphiti-memory setup...[/bold]")

  # Dependency check
  missing = []
  for pkg in ("graphiti_core", "neo4j", "litellm", "dotenv", "pydantic"):
    try:
      __import__(pkg)
      console.print(f"  [green]✓[/green] {pkg}")
    except ImportError:
      console.print(f"  [red]✗[/red] {pkg}")
      missing.append(pkg)

  if missing:
    console.print(
        f"\n[red]Missing packages: {', '.join(missing)}[/red]\n"
        "Run: uv run --directory {baseDir} <command>"
    )
    raise typer.Exit(1)

  # Neo4j connectivity
  uri, user, pwd = _get_neo4j_creds()
  console.print(f"\nNeo4j URI : {uri}")
  console.print(f"Profile   : {os.getenv('NEO4J_PROFILE', 'local')}")

  if not pwd:
    console.print("[yellow]⚠  NEO4J_PASSWORD not set – skipping connection test[/yellow]")
  else:
    try:
      from neo4j import GraphDatabase

      driver = GraphDatabase.driver(uri, auth=(user, pwd))
      driver.verify_connectivity()
      driver.close()
      console.print("[green]✓ Neo4j connection successful[/green]")
    except Exception as exc:  # pylint: disable=broad-except
      console.print(f"[red]✗ Neo4j connection failed: {exc}[/red]")
      raise typer.Exit(1)

  console.print("\n[green]Setup looks good.[/green]")


@app.command("ingest-text")
def ingest_text(
    content: str = typer.Argument(..., help="Text content to ingest"),
    document_id: str = typer.Option(
        None, "--document-id", "-d", help="Unique document ID"
    ),
    group_id: str = typer.Option(
        "generic", "--group-id", "-g", help="Group ID for content categorisation"
    ),
    chunk_size: int = typer.Option(1000, "--chunk-size", help="Chunk size in chars"),
    overlap: int = typer.Option(100, "--overlap", help="Chunk overlap in chars"),
):
  """Ingest raw text content into the knowledge graph."""
  doc_id = document_id or _doc_id(content[:64])
  asyncio.run(_ingest_chunks(content, doc_id, group_id, chunk_size, overlap))


@app.command("ingest-file")
def ingest_file(
    file_path: str = typer.Argument(..., help="Path to file"),
    group_id: str = typer.Option(
        None, "--group-id", "-g", help="Group ID (auto-detected if omitted)"
    ),
    chunk_size: int = typer.Option(1000, "--chunk-size"),
    overlap: int = typer.Option(100, "--overlap"),
):
  """Ingest a single file into the knowledge graph."""
  path = Path(file_path)
  if not path.exists():
    console.print(f"[red]File not found: {file_path}[/red]")
    raise typer.Exit(1)

  content = path.read_text(encoding="utf-8", errors="replace")
  gid = group_id or _auto_group_id(path.suffix)
  doc_id = _doc_id(str(path.resolve()))

  console.print(f"Ingesting [cyan]{path.name}[/cyan] → group=[yellow]{gid}[/yellow]")
  asyncio.run(_ingest_chunks(content, doc_id, gid, chunk_size, overlap))


@app.command("ingest-directory")
def ingest_directory(
    directory: str = typer.Argument(..., help="Directory path"),
    pattern: str = typer.Option("*.md", "--pattern", "-p", help="File glob pattern"),
    recursive: bool = typer.Option(True, "--recursive/--no-recursive"),
    group_id: str = typer.Option(
        None, "--group-id", "-g", help="Override group ID for all files"
    ),
    chunk_size: int = typer.Option(1000, "--chunk-size"),
    overlap: int = typer.Option(100, "--overlap"),
):
  """Ingest all matching files in a directory."""
  base = Path(directory)
  if not base.is_dir():
    console.print(f"[red]Directory not found: {directory}[/red]")
    raise typer.Exit(1)

  glob_fn = base.rglob if recursive else base.glob
  files = list(glob_fn(pattern))

  if not files:
    console.print(f"[yellow]No files matching '{pattern}' in {directory}[/yellow]")
    raise typer.Exit(0)

  console.print(f"Found [cyan]{len(files)}[/cyan] files – ingesting...")
  asyncio.run(
      _ingest_files_batch(files, group_id, chunk_size, overlap)
  )


@app.command()
def query(
    query_text: str = typer.Argument(..., help="Natural language query"),
    max_results: int = typer.Option(10, "--max-results", "-n"),
    group_id: str = typer.Option(
        None, "--group-id", "-g", help="Restrict search to a group"
    ),
    output_format: str = typer.Option(
        "text", "--format", "-f", help="Output format: text | json"
    ),
):
  """Query the knowledge graph with natural language."""
  asyncio.run(_run_query(query_text, max_results, group_id, output_format))


@app.command()
def stats():
  """Show knowledge graph statistics."""
  asyncio.run(_show_stats())


@app.command("clear-graph")
def clear_graph(
    confirm: bool = typer.Option(
        False, "--confirm", help="Required to actually clear the graph"
    ),
    group_id: str = typer.Option(
        None, "--group-id", "-g", help="Clear only a specific group"
    ),
):
  """Clear graph data (requires --confirm)."""
  if not confirm:
    console.print(
        "[yellow]Add --confirm to actually clear the graph.[/yellow]"
    )
    raise typer.Exit(0)
  asyncio.run(_clear(group_id))


@app.command()
def info():
  """Display current configuration."""
  uri, user, _ = _get_neo4j_creds()
  table = Table(title="graphiti-memory configuration")
  table.add_column("Setting", style="cyan")
  table.add_column("Value")
  table.add_row("LLM model", os.getenv("LLM_CHOICE", "(not set)"))
  table.add_row(
      "Embedding model", os.getenv("EMBEDDING_MODEL_CHOICE", "(not set)")
  )
  table.add_row("Neo4j profile", os.getenv("NEO4J_PROFILE", "local"))
  table.add_row("Neo4j URI", uri)
  table.add_row("Neo4j user", user)
  table.add_row("Chunk size", os.getenv("CHUNK_SIZE", "1000"))
  table.add_row("Chunk overlap", os.getenv("CHUNK_OVERLAP", "100"))
  table.add_row(
      "Confidence threshold", os.getenv("CONFIDENCE_THRESHOLD", "0.5")
  )
  console.print(table)


# ---------------------------------------------------------------------------
# Async implementation helpers
# ---------------------------------------------------------------------------


def _auto_group_id(suffix: str) -> str:
  """Map a file extension to a group ID."""
  mapping = {
      ".md": "doc_markdown",
      ".txt": "doc_text",
      ".rst": "doc_rst",
      ".py": "code_python",
      ".c": "code_c",
      ".cpp": "code_cpp",
      ".h": "code_c",
      ".json": "config_json",
      ".yaml": "config_yaml",
      ".yml": "config_yaml",
  }
  return mapping.get(suffix.lower(), "generic")


async def _ingest_chunks(
    content: str,
    doc_id: str,
    group_id: str,
    chunk_size: int,
    overlap: int,
) -> None:
  """Core ingestion: chunk text and add each chunk as a Graphiti episode."""
  graphiti = _build_graphiti_client()
  await _init_graphiti(graphiti)

  chunks = _chunk_text(content, chunk_size, overlap)
  console.print(
      f"  {len(chunks)} chunk(s) → doc_id=[dim]{doc_id}[/dim]"
      f" group=[yellow]{group_id}[/yellow]"
  )

  start = time.time()
  for i, chunk in enumerate(chunks):
    episode_name = f"{doc_id}_chunk_{i}"
    await graphiti.add_episode(
        name=episode_name,
        episode_body=chunk,
        source_description=f"document:{doc_id}",
        reference_time=datetime.now(timezone.utc),
        group_id=group_id,
    )

  elapsed = time.time() - start
  console.print(
      f"  [green]✓[/green] Ingested {len(chunks)} chunk(s) in {elapsed:.1f}s"
  )
  await graphiti.close()


async def _ingest_files_batch(
    files: list[Path],
    group_id: Optional[str],
    chunk_size: int,
    overlap: int,
) -> None:
  """Ingest multiple files sequentially, sharing one Graphiti connection."""
  graphiti = _build_graphiti_client()
  await _init_graphiti(graphiti)

  total_chunks = 0
  start = time.time()

  for path in files:
    try:
      content = path.read_text(encoding="utf-8", errors="replace")
      gid = group_id or _auto_group_id(path.suffix)
      doc_id = _doc_id(str(path.resolve()))
      chunks = _chunk_text(content, chunk_size, overlap)

      for i, chunk in enumerate(chunks):
        await graphiti.add_episode(
            name=f"{doc_id}_chunk_{i}",
            episode_body=chunk,
            source_description=f"file:{path.name}",
            reference_time=datetime.now(timezone.utc),
            group_id=gid,
        )
      total_chunks += len(chunks)
      console.print(
          f"  [green]✓[/green] {path.name} ({len(chunks)} chunks,"
          f" group={gid})"
      )
    except Exception as exc:  # pylint: disable=broad-except
      console.print(f"  [red]✗[/red] {path.name}: {exc}")

  elapsed = time.time() - start
  console.print(
      f"\n[green]Done.[/green] {len(files)} files,"
      f" {total_chunks} total chunks in {elapsed:.1f}s"
  )
  await graphiti.close()


async def _run_query(
    query_text: str,
    max_results: int,
    group_id: Optional[str],
    output_format: str,
) -> None:
  """Execute a Graphiti search and display results."""
  graphiti = _build_graphiti_client()
  await _init_graphiti(graphiti)

  console.print(f"Searching: [cyan]{query_text}[/cyan]")
  start = time.time()

  results = await graphiti.search(
      query=query_text,
      num_results=max_results,
      group_ids=[group_id] if group_id else None,
  )

  elapsed = time.time() - start
  console.print(
      f"Found [bold]{len(results)}[/bold] result(s) in {elapsed:.2f}s\n"
  )

  if output_format == "json":
    output = []
    for r in results:
      output.append({
          "fact": getattr(r, "fact", str(r)),
          "uuid": str(getattr(r, "uuid", "")),
          "created_at": str(getattr(r, "created_at", "")),
      })
    console.print_json(json.dumps(output, indent=2))
  else:
    for i, r in enumerate(results, 1):
      fact = getattr(r, "fact", str(r))
      console.print(f"[bold]{i}.[/bold] {fact}")

  await graphiti.close()


async def _show_stats() -> None:
  """Query Neo4j directly for graph statistics."""
  from neo4j import AsyncGraphDatabase

  uri, user, pwd = _get_neo4j_creds()
  if not pwd:
    console.print("[red]NEO4J_PASSWORD not configured.[/red]")
    raise typer.Exit(1)

  driver = AsyncGraphDatabase.driver(uri, auth=(user, pwd))
  async with driver.session() as session:
    entity_result = await session.run("MATCH (e:Entity) RETURN count(e) AS n")
    entity_record = await entity_result.single()
    entity_count = entity_record["n"] if entity_record else 0

    rel_result = await session.run(
        "MATCH ()-[r:RELATES_TO]->() RETURN count(r) AS n"
    )
    rel_record = await rel_result.single()
    rel_count = rel_record["n"] if rel_record else 0

    ep_result = await session.run(
        "MATCH (ep:Episodic) RETURN count(ep) AS n"
    )
    ep_record = await ep_result.single()
    ep_count = ep_record["n"] if ep_record else 0

    group_result = await session.run(
        "MATCH (e:Entity) WHERE e.group_id IS NOT NULL"
        " RETURN e.group_id AS g, count(e) AS n ORDER BY n DESC"
    )
    groups: list[dict[str, Any]] = []
    async for record in group_result:
      groups.append({"group": record["g"], "entities": record["n"]})

  await driver.close()

  table = Table(title="Knowledge Graph Statistics")
  table.add_column("Metric", style="cyan")
  table.add_column("Count", justify="right")
  table.add_row("Entities", str(entity_count))
  table.add_row("Relationships", str(rel_count))
  table.add_row("Episodes", str(ep_count))
  console.print(table)

  if groups:
    gtable = Table(title="Entities by Group")
    gtable.add_column("Group ID", style="yellow")
    gtable.add_column("Entities", justify="right")
    for g in groups:
      gtable.add_row(g["group"], str(g["entities"]))
    console.print(gtable)


async def _clear(group_id: Optional[str]) -> None:
  """Delete graph data, optionally scoped to a group."""
  from neo4j import AsyncGraphDatabase

  uri, user, pwd = _get_neo4j_creds()
  driver = AsyncGraphDatabase.driver(uri, auth=(user, pwd))

  async with driver.session() as session:
    if group_id:
      await session.run(
          "MATCH (e:Entity {group_id: $g}) DETACH DELETE e",
          g=group_id,
      )
      console.print(
          f"[green]Cleared entities for group:[/green] {group_id}"
      )
    else:
      await session.run("MATCH (n) DETACH DELETE n")
      console.print("[green]Graph cleared.[/green]")

  await driver.close()


if __name__ == "__main__":
  app()
