#!/usr/bin/env python3.12
# /// script
# requires-python = ">=3.12"
# dependencies = [
#     "cognee @ git+https://github.com/fenghaitao/cognee.git",
#     "litellm @ git+https://github.com/fenghaitao/litellm.git",
#     "pyyaml>=6.0",
#     "python-dotenv>=1.0.0",
# ]
# ///
"""
Cognee Memory - Index and search current directory using Cognee knowledge graphs

A self-contained script for indexing and searching code repositories using
the forked Cognee installation with GitHub Copilot support.

Usage:
    # Index current directory
    uv run cognee_memory.py index
    
    # Index specific directory
    uv run cognee_memory.py index --root /path/to/project
    
    # Search indexed content
    uv run cognee_memory.py search "What is DML?"
    
    # Search with specific strategy
    uv run cognee_memory.py search "Find code" --type CHUNKS

Features:
- Uses forked Cognee from github.com/fenghaitao/cognee
- Knowledge graph construction with entity/relationship extraction
- Multiple search strategies (INSIGHTS, CHUNKS, GRAPH_COMPLETION)
- GitHub Copilot LLM support
- Automatic rate limiting
- Self-contained with inline dependencies

Note:
    This script uses the forked Cognee from github.com/fenghaitao/cognee
    to ensure compatibility with GitHub Copilot and custom configurations.
    
Performance Note:
    First run will be slow (~15-25 seconds) due to:
    - Cognee import overhead (5-10 seconds)
    - Database initialization (2-3 seconds)
    - uv environment setup (2-3 seconds)
    Subsequent runs in the same session will be faster.
"""

import argparse
import asyncio
import os
import sys
import subprocess
from pathlib import Path
from typing import Optional, Set, Tuple
from dataclasses import dataclass, field
from datetime import datetime

# Set critical environment variables BEFORE any other imports
# This prevents importing fastapi_users/bcrypt which causes issues
os.environ.setdefault("ENABLE_BACKEND_ACCESS_CONTROL", "false")
os.environ.setdefault("REQUIRE_AUTHENTICATION", "false")
os.environ.setdefault("LOG_LEVEL", "ERROR")  # Reduce noise
os.environ.setdefault("TELEMETRY_DISABLED", "1")

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

# Configuration
@dataclass
class Config:
    """Cognee configuration"""
    
    # Paths
    root_path: Path = Path(".")  # Root directory to index
    working_dir: Path = Path("./cognee_storage")
    output_dir: Path = Path("./wiki_docs")
    dataset_name: str = "main"
    
    # Repository metadata (auto-detected from git if available)
    repo_name: Optional[str] = None  # Auto-detected from git or directory name
    
    # LLM settings - Use GitHub Copilot by default
    llm_model: str = "github_copilot/gpt-4o"
    llm_provider: str = "custom"
    embedding_model: str = "github_copilot/text-embedding-3-small"
    embedding_dimensions: int = 1536
    api_key: str = "oauth2"  # For GitHub Copilot
    
    # Indexing settings
    code_extensions: Set[str] = field(default_factory=lambda: {
        '.py', '.md', '.txt', '.dml', '.c', '.h', '.cpp', '.hpp', '.java', '.js', '.ts'
    })
    min_file_size: int = 50
    max_file_size: int = 1024 * 1024  # 1MB
    batch_report_interval: int = 10
    
    # Rate limiting for GitHub Copilot
    embedding_rate_limit_enabled: bool = True
    embedding_rate_limit_requests: int = 30
    embedding_rate_limit_interval: int = 60
    llm_rate_limit_enabled: bool = True
    llm_rate_limit_requests: int = 30
    llm_rate_limit_interval: int = 60
    
    # Search settings
    search_type: str = "CHUNKS"  # INSIGHTS, CHUNKS, GRAPH_COMPLETION (CHUNKS is faster)
    
    @classmethod
    def from_env(cls, **overrides) -> "Config":
        """Create config from environment variables"""
        config_dict = {}
        
        if working_dir := os.getenv("WORKING_DIR"):
            config_dict["working_dir"] = Path(working_dir)
        
        if output_dir := os.getenv("OUTPUT_DIR"):
            config_dict["output_dir"] = Path(output_dir)
        
        if dataset_name := os.getenv("DATASET_NAME"):
            config_dict["dataset_name"] = dataset_name
        
        if repo_name := os.getenv("REPO_NAME"):
            config_dict["repo_name"] = repo_name
        
        if llm_model := os.getenv("LLM_MODEL"):
            config_dict["llm_model"] = llm_model
        
        if embed_model := os.getenv("EMBEDDING_MODEL"):
            config_dict["embedding_model"] = embed_model
        
        if api_key := os.getenv("API_KEY"):
            config_dict["api_key"] = api_key
        
        if min_size := os.getenv("MIN_FILE_SIZE"):
            config_dict["min_file_size"] = int(min_size)
        
        # Apply overrides
        config_dict.update(overrides)
        
        return cls(**config_dict)
    
    def validate(self):
        """Validate configuration"""
        # Validate root path exists
        if not self.root_path.exists():
            raise ValueError(f"Root path does not exist: {self.root_path}")
        
        # Auto-detect repo name if not set
        if self.repo_name is None:
            self.repo_name = self._detect_repo_name()
        
        # Create directories if they don't exist
        self.working_dir.mkdir(parents=True, exist_ok=True)
        self.output_dir.mkdir(parents=True, exist_ok=True)
    
    def _detect_repo_name(self) -> str:
        """Auto-detect repository name from git or directory name"""
        # Try to get from git remote
        try:
            result = subprocess.run(
                ["git", "remote", "get-url", "origin"],
                cwd=self.root_path,
                capture_output=True,
                text=True,
                timeout=5
            )
            if result.returncode == 0:
                url = result.stdout.strip()
                # Extract repo name from URL
                name = url.rstrip('/').split('/')[-1]
                if name.endswith('.git'):
                    name = name[:-4]
                return name
        except Exception:
            pass
        
        # Fallback to directory name
        return self.root_path.resolve().name
    
    def apply_to_env(self):
        """Apply configuration to environment variables for Cognee"""
        # Critical: Set these FIRST to avoid importing fastapi_users/bcrypt
        os.environ["ENABLE_BACKEND_ACCESS_CONTROL"] = "false"
        os.environ["REQUIRE_AUTHENTICATION"] = "false"
        
        # LLM configuration
        os.environ["LLM_MODEL"] = self.llm_model
        os.environ["LLM_PROVIDER"] = self.llm_provider
        os.environ["LLM_API_KEY"] = self.api_key
        
        # Embedding configuration
        os.environ["EMBEDDING_MODEL"] = self.embedding_model
        os.environ["EMBEDDING_DIMENSIONS"] = str(self.embedding_dimensions)
        
        # Storage paths (must be absolute for Cognee)
        os.environ["SYSTEM_ROOT_DIRECTORY"] = str(self.working_dir.resolve() / "system")
        os.environ["DATA_ROOT_DIRECTORY"] = str(self.working_dir.resolve() / "data")
        
        # Rate limiting
        os.environ["EMBEDDING_RATE_LIMIT_ENABLED"] = str(self.embedding_rate_limit_enabled).lower()
        os.environ["EMBEDDING_RATE_LIMIT_REQUESTS"] = str(self.embedding_rate_limit_requests)
        os.environ["EMBEDDING_RATE_LIMIT_INTERVAL"] = str(self.embedding_rate_limit_interval)
        os.environ["LLM_RATE_LIMIT_ENABLED"] = str(self.llm_rate_limit_enabled).lower()
        os.environ["LLM_RATE_LIMIT_REQUESTS"] = str(self.llm_rate_limit_requests)
        os.environ["LLM_RATE_LIMIT_INTERVAL"] = str(self.llm_rate_limit_interval)
        
        # Other settings
        os.environ["LOG_LEVEL"] = "ERROR"  # Reduce noise
        os.environ["TELEMETRY_DISABLED"] = "1"


# Repository Indexer
class RepositoryIndexer:
    """Index repository into Cognee knowledge graph"""
    
    def __init__(self, config: Config):
        self.config = config
        self.cognee = None
    
    async def index_repository(self) -> Tuple[int, int, int]:
        """Index all files in repository"""
        # Apply config to environment before importing cognee
        self.config.apply_to_env()
        
        # Import cognee after setting environment
        import cognee
        self.cognee = cognee
        
        print(f"\n📚 Indexing: {self.config.repo_name}")
        print(f"   Root: {self.config.root_path}")
        print(f"   Dataset: {self.config.dataset_name}")
        print(f"   Working directory: {self.config.working_dir}")
        print(f"   LLM: {self.config.llm_model}")
        print(f"   Embedding: {self.config.embedding_model}")
        print(f"   Rate Limiting: {self.config.embedding_rate_limit_requests}/min")
        
        # Step 1: Prune system (optional - ask user)
        print(f"\n🧹 Checking existing data...")
        system_dir = self.config.working_dir / "system"
        if system_dir.exists() and any(system_dir.iterdir()):
            response = input("   Existing data found. Prune before indexing? (yes/no): ").strip().lower()
            if response in ['yes', 'y']:
                print("   Pruning system...")
                await cognee.prune.prune_system(metadata=True)
                print("   ✅ System pruned")
            else:
                print("   Keeping existing data (incremental indexing)")
        else:
            print("   No existing data found")
        
        # Step 2: Find all files
        print(f"\n📁 Finding files to index...")
        files_to_index = []
        for ext in self.config.code_extensions:
            files_to_index.extend(self.config.root_path.rglob(f"*{ext}"))
        
        # Filter by size and sort
        files_to_index = [
            f for f in files_to_index 
            if f.is_file() 
            and self.config.min_file_size <= f.stat().st_size <= self.config.max_file_size
        ]
        files_to_index.sort()
        
        print(f"   Found {len(files_to_index)} files to index")
        
        # Step 3: Add files
        print(f"\n📄 Adding files to Cognee...")
        indexed = 0
        skipped = 0
        errors = 0
        
        import time
        start_time = time.time()
        
        for i, file_path in enumerate(files_to_index, 1):
            try:
                # Add file to cognee
                await cognee.add(
                    data=str(file_path),
                    dataset_name=self.config.dataset_name
                )
                indexed += 1
                
                # Progress report
                if i % self.config.batch_report_interval == 0:
                    elapsed = time.time() - start_time
                    rate = i / elapsed if elapsed > 0 else 0
                    print(f"   Progress: {i}/{len(files_to_index)} files ({rate:.1f} files/sec)")
                
            except Exception as e:
                print(f"   ⚠️  Error adding {file_path}: {e}")
                errors += 1
        
        add_time = time.time() - start_time
        print(f"   ✅ Files added in {add_time:.1f}s")
        
        # Step 4: Cognify (build knowledge graph)
        print(f"\n🧠 Building knowledge graph...")
        print(f"   (This may take several minutes with rate limiting...)")
        start_time = time.time()
        
        await cognee.cognify(dataset_name=self.config.dataset_name)
        
        cognify_time = time.time() - start_time
        print(f"   ✅ Knowledge graph built in {cognify_time:.1f}s")
        
        print(f"\n✅ Indexing complete!")
        print(f"   Indexed: {indexed} files")
        print(f"   Skipped: {skipped} files")
        print(f"   Errors: {errors} files")
        print(f"   Total time: {(add_time + cognify_time):.1f}s")
        
        return indexed, skipped, errors


# Search Interface
class RepositorySearch:
    """Search indexed repository using Cognee"""
    
    def __init__(self, config: Config):
        self.config = config
        self.cognee = None
    
    async def search(self, query: str) -> list:
        """Search the knowledge graph"""
        import time
        
        print(f"\n🔍 Searching: {query}")
        print(f"   Dataset: {self.config.dataset_name}")
        print(f"   Search type: {self.config.search_type}")
        
        # Apply config to environment
        self.config.apply_to_env()
        
        # Import cognee and search types
        if self.cognee is None:
            print(f"\n   [1/3] ⏳ Loading Cognee library...")
            import_start = time.time()
            
            import cognee
            from cognee.modules.search.types.SearchType import SearchType
            
            self.cognee = cognee
            self._SearchType = SearchType
            
            import_time = time.time() - import_start
            print(f"   [1/3] ✅ Cognee loaded ({import_time:.2f}s)")
        else:
            from cognee.modules.search.types.SearchType import SearchType
            self._SearchType = SearchType
            print(f"   [1/3] ✅ Cognee already loaded (cached)")
        
        # Initialize search
        print(f"   [2/3] ⏳ Initializing database...")
        init_start = time.time()
        
        # Map search type string to enum
        search_type_map = {
            "SUMMARIES": self._SearchType.SUMMARIES,
            "CHUNKS": self._SearchType.CHUNKS,
            "CHUNKS_LEXICAL": self._SearchType.CHUNKS_LEXICAL,
            "GRAPH_COMPLETION": self._SearchType.GRAPH_COMPLETION,
            "CODING_RULES": self._SearchType.CODING_RULES,
        }
        
        search_type = search_type_map.get(self.config.search_type, self._SearchType.GRAPH_COMPLETION)
        
        init_time = time.time() - init_start
        print(f"   [2/3] ✅ Database ready ({init_time:.2f}s)")
        
        # Perform search
        print(f"   [3/3] ⏳ Executing {self.config.search_type} search...")
        search_start = time.time()
        
        results = await self.cognee.search(
            query_text=query,
            query_type=search_type
        )
        
        search_time = time.time() - search_start
        print(f"   [3/3] ✅ Search complete ({search_time:.2f}s)")
        
        print(f"\n📊 Results:")
        print(f"   Found: {len(results)} results")
        
        return results


# CLI Functions
async def run_index(config: Config):
    """Run the indexing step"""
    print("\n" + "=" * 80)
    print("INDEXING REPOSITORY")
    print("=" * 80)
    
    indexer = RepositoryIndexer(config)
    indexed, skipped, errors = await indexer.index_repository()
    
    return indexed > 0


async def run_search(config: Config, query: str, output: Optional[Path] = None):
    """Run a search query"""
    import time
    total_start = time.time()
    
    print("\n" + "=" * 80)
    print("SEARCHING REPOSITORY")
    print("=" * 80)
    print(f"\n⏱️  Performance Note:")
    print(f"   This search involves multiple steps:")
    print(f"   1. Loading Cognee library (~5-10s)")
    print(f"   2. Initializing database (~2-3s)")
    print(f"   3. Executing search (~3-8s)")
    print(f"   Total expected time: ~10-20 seconds\n")

    searcher = RepositorySearch(config)
    results = await searcher.search(query)
    
    total_time = time.time() - total_start
    print(f"\n⏱️  Total search time: {total_time:.2f}s")
    
    # Display results
    print("\n" + "=" * 80)
    print("SEARCH RESULTS")
    print("=" * 80)
    
    if not results:
        print("\n❌ No results found")
        return False
    
    for i, result in enumerate(results, 1):
        print(f"\n--- Result {i} ---")
        print(str(result)[:500])
        if len(str(result)) > 500:
            print("... (truncated)")
    
    # Save to file if requested
    if output:
        print(f"\n💾 Saving results to {output}...")
        output.parent.mkdir(parents=True, exist_ok=True)
        
        content = f"# Search Results\n\n"
        content += f"**Query:** {query}\n\n"
        content += f"**Dataset:** {config.dataset_name}\n\n"
        content += f"**Results:** {len(results)}\n\n"
        content += f"**Generated:** {datetime.now().isoformat()}\n\n"
        content += "---\n\n"
        
        for i, result in enumerate(results, 1):
            content += f"## Result {i}\n\n"
            content += f"{result}\n\n"
            content += "---\n\n"
        
        output.write_text(content)
        print(f"   ✅ Results saved to {output}")
    
    return True




def main():
    """Main CLI entry point"""
    parser = argparse.ArgumentParser(
        description="Index and search current directory using Cognee knowledge graphs"
    )
    
    subparsers = parser.add_subparsers(dest="command", help="Command to run")
    
    # Index command
    index_parser = subparsers.add_parser("index", help="Index directory")
    index_parser.add_argument(
        "--root",
        type=Path,
        help="Root directory to index (default: current directory)"
    )
    index_parser.add_argument(
        "--working-dir",
        type=Path,
        help="Working directory for storage (default: ./cognee_storage)"
    )
    index_parser.add_argument(
        "--dataset",
        type=str,
        help="Dataset name (default: main)"
    )
    index_parser.add_argument(
        "--model",
        type=str,
        help="LLM model to use (default: github_copilot/gpt-4o)"
    )
    
    # Search command
    search_parser = subparsers.add_parser("search", help="Search indexed content")
    search_parser.add_argument(
        "query",
        type=str,
        help="Search query"
    )
    search_parser.add_argument(
        "--working-dir",
        type=Path,
        help="Working directory with indexed data (default: ./cognee_storage)"
    )
    search_parser.add_argument(
        "--dataset",
        type=str,
        help="Dataset name (default: main)"
    )
    search_parser.add_argument(
        "--type",
        type=str,
        choices=["SUMMARIES", "CHUNKS", "CHUNKS_LEXICAL", "GRAPH_COMPLETION", "CODING_RULES"],
        help="Search type (default: GRAPH_COMPLETION)"
    )
    search_parser.add_argument(
        "--output",
        type=Path,
        help="Save results to file"
    )
    
    args = parser.parse_args()
    
    # Build config from args
    config_kwargs = {}
    if hasattr(args, 'root') and args.root:
        config_kwargs['root_path'] = args.root
    if hasattr(args, 'working_dir') and args.working_dir:
        config_kwargs['working_dir'] = args.working_dir
    if hasattr(args, 'dataset') and args.dataset:
        config_kwargs['dataset_name'] = args.dataset
    if hasattr(args, 'model') and args.model:
        config_kwargs['llm_model'] = args.model
    if hasattr(args, 'type') and args.type:
        config_kwargs['search_type'] = args.type
    
    config = Config.from_env(**config_kwargs)
    
    try:
        config.validate()
    except Exception as e:
        print(f"❌ Configuration error: {e}")
        sys.exit(1)
    
    # Run command
    if args.command == "index":
        asyncio.run(run_index(config))
    elif args.command == "search":
        output = getattr(args, 'output', None)
        asyncio.run(run_search(config, args.query, output))
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()
