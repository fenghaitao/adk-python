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

"""Tests for Cognee-based memory indexing and retrieval."""

from __future__ import annotations

import pytest
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

from cognee_openspec.memory.indexer import CogneeMemoryIndexer
from cognee_openspec.memory.retriever import CogneeMemoryRetriever


@pytest.fixture
def mock_cognee():
  """Mock cognee module."""
  with patch("cognee_openspec.memory.indexer.cognee") as mock:
    mock.add = AsyncMock()
    mock.cognify = AsyncMock(return_value={"status": "success"})
    mock.memify = AsyncMock()
    mock.search = AsyncMock(return_value=["result1", "result2"])
    mock.visualize_graph = AsyncMock()
    mock.prune.prune_data = AsyncMock()
    mock.prune.prune_system = AsyncMock()
    yield mock


@pytest.fixture
def temp_memory_dir(tmp_path):
  """Create temporary memory directory with test files."""
  memory_dir = tmp_path / "test_memories"
  memory_dir.mkdir()
  
  # Create test markdown files
  (memory_dir / "dml_basics.md").write_text(
    "# DML Basics\n\nThis is a test DML document."
  )
  (memory_dir / "test_guide.md").write_text(
    "# Test Guide\n\nThis is a test guide document."
  )
  (memory_dir / "general.md").write_text(
    "# General Info\n\nThis is a general document."
  )
  
  return memory_dir


class TestCogneeMemoryIndexer:
  """Tests for CogneeMemoryIndexer."""
  
  def test_init(self, temp_memory_dir):
    """Test indexer initialization."""
    indexer = CogneeMemoryIndexer(
      memory_dir=temp_memory_dir,
      dataset_name="test_dataset"
    )
    
    assert indexer.memory_dir == temp_memory_dir
    assert indexer.dataset_name == "test_dataset"
  
  def test_categorize_document(self, temp_memory_dir):
    """Test document categorization."""
    indexer = CogneeMemoryIndexer(memory_dir=temp_memory_dir)
    
    assert indexer._categorize_document("dml_basics.md") == "DML"
    assert indexer._categorize_document("test_guide.md") == "Test"
    assert indexer._categorize_document("general.md") == "General"
  
  @pytest.mark.asyncio
  async def test_index_memories_success(
      self,
      temp_memory_dir,
      mock_cognee
  ):
    """Test successful memory indexing."""
    indexer = CogneeMemoryIndexer(
      memory_dir=temp_memory_dir,
      dataset_name="test_dataset"
    )
    
    result = await indexer.index_memories(force_reindex=False)
    
    assert result["status"] == "success"
    assert result["files_indexed"] == 3
    assert result["dataset_name"] == "test_dataset"
    assert result["graph_built"] is True
    
    # Verify cognee calls
    mock_cognee.add.assert_called_once()
    mock_cognee.cognify.assert_called_once()
    mock_cognee.memify.assert_called_once()
  
  @pytest.mark.asyncio
  async def test_index_memories_force_reindex(
      self,
      temp_memory_dir,
      mock_cognee
  ):
    """Test force reindexing."""
    indexer = CogneeMemoryIndexer(memory_dir=temp_memory_dir)
    
    await indexer.index_memories(force_reindex=True)
    
    # Verify prune calls
    mock_cognee.prune.prune_data.assert_called_once()
    mock_cognee.prune.prune_system.assert_called_once()
  
  @pytest.mark.asyncio
  async def test_index_memories_no_files(self, tmp_path, mock_cognee):
    """Test indexing with no markdown files."""
    empty_dir = tmp_path / "empty"
    empty_dir.mkdir()
    
    indexer = CogneeMemoryIndexer(memory_dir=empty_dir)
    result = await indexer.index_memories()
    
    assert result["status"] == "no_files"
    assert "No markdown files found" in result["message"]
  
  @pytest.mark.asyncio
  async def test_index_memories_missing_dir(self, tmp_path, mock_cognee):
    """Test indexing with missing directory."""
    missing_dir = tmp_path / "missing"
    
    indexer = CogneeMemoryIndexer(memory_dir=missing_dir)
    
    with pytest.raises(FileNotFoundError):
      await indexer.index_memories()
  
  @pytest.mark.asyncio
  async def test_get_stats(self, temp_memory_dir, mock_cognee):
    """Test getting statistics."""
    indexer = CogneeMemoryIndexer(memory_dir=temp_memory_dir)
    
    stats = await indexer.get_stats()
    
    assert stats["status"] == "success"
    assert stats["dataset_name"] == "openspec_memories"
    mock_cognee.search.assert_called_once()
  
  @pytest.mark.asyncio
  async def test_visualize_graph(self, temp_memory_dir, mock_cognee):
    """Test graph visualization."""
    indexer = CogneeMemoryIndexer(memory_dir=temp_memory_dir)
    
    viz_path = await indexer.visualize_graph("test_graph.html")
    
    assert viz_path == "test_graph.html"
    mock_cognee.visualize_graph.assert_called_once_with("test_graph.html")


class TestCogneeMemoryRetriever:
  """Tests for CogneeMemoryRetriever."""
  
  def test_init(self):
    """Test retriever initialization."""
    retriever = CogneeMemoryRetriever(
      dataset_name="test_dataset",
      search_type="CHUNKS",
      top_k=10
    )
    
    assert retriever.dataset_name == "test_dataset"
    assert retriever.top_k == 10
  
  def test_get_search_type(self):
    """Test search type conversion."""
    retriever = CogneeMemoryRetriever()
    
    # Test valid search types
    from cognee import SearchType
    
    assert retriever._get_search_type("GRAPH_COMPLETION") == \
      SearchType.GRAPH_COMPLETION
    assert retriever._get_search_type("CHUNKS") == SearchType.CHUNKS
    assert retriever._get_search_type("SUMMARIES") == SearchType.SUMMARIES
    
    # Test case insensitivity
    assert retriever._get_search_type("chunks") == SearchType.CHUNKS
    
    # Test invalid type defaults to GRAPH_COMPLETION
    assert retriever._get_search_type("INVALID") == \
      SearchType.GRAPH_COMPLETION
  
  @pytest.mark.asyncio
  async def test_search(self, mock_cognee):
    """Test basic search."""
    with patch("cognee_openspec.memory.retriever.cognee", mock_cognee):
      retriever = CogneeMemoryRetriever(top_k=2)
      
      results = await retriever.search("test query")
      
      assert len(results) == 2
      assert results == ["result1", "result2"]
      mock_cognee.search.assert_called_once()
  
  @pytest.mark.asyncio
  async def test_search_with_category(self, mock_cognee):
    """Test search with category filter."""
    with patch("cognee_openspec.memory.retriever.cognee", mock_cognee):
      retriever = CogneeMemoryRetriever()
      
      await retriever.search("test query", category="DML")
      
      # Verify category was added to query
      call_args = mock_cognee.search.call_args
      assert "[Category: DML]" in call_args.kwargs["query_text"]
  
  @pytest.mark.asyncio
  async def test_search_with_context(self, mock_cognee):
    """Test search with context."""
    with patch("cognee_openspec.memory.retriever.cognee", mock_cognee):
      retriever = CogneeMemoryRetriever(
        search_type="CHUNKS",
        top_k=2
      )
      
      result = await retriever.search_with_context(
        "test query",
        category="Test"
      )
      
      assert result["query"] == "test query"
      assert result["category"] == "Test"
      assert result["search_type"] == "CHUNKS"
      assert result["count"] == 2
      assert len(result["passages"]) == 2
  
  def test_extract_passages_string(self):
    """Test extracting passages from string results."""
    retriever = CogneeMemoryRetriever()
    
    results = ["passage1", "passage2"]
    passages = retriever._extract_passages(results)
    
    assert passages == ["passage1", "passage2"]
  
  def test_extract_passages_dict(self):
    """Test extracting passages from dict results."""
    retriever = CogneeMemoryRetriever()
    
    results = [
      {"text": "passage1"},
      {"content": "passage2"},
      {"answer": "passage3"},
      {"other": "passage4"}
    ]
    passages = retriever._extract_passages(results)
    
    assert passages[0] == "passage1"
    assert passages[1] == "passage2"
    assert passages[2] == "passage3"
    assert "other" in passages[3]


class TestSyncWrappers:
  """Tests for synchronous wrapper functions."""
  
  @patch("cognee_openspec.memory.indexer.asyncio.run")
  def test_index_memories_sync(self, mock_run, temp_memory_dir):
    """Test synchronous indexing wrapper."""
    from cognee_openspec.memory.indexer import index_memories_sync
    
    mock_run.return_value = {"status": "success"}
    
    result = index_memories_sync(
      memory_dir=temp_memory_dir,
      force_reindex=True
    )
    
    assert result["status"] == "success"
    mock_run.assert_called_once()
  
  @patch("cognee_openspec.memory.retriever.asyncio.run")
  def test_search_memories_sync(self, mock_run):
    """Test synchronous search wrapper."""
    from cognee_openspec.memory.retriever import search_memories_sync
    
    mock_run.return_value = ["result1", "result2"]
    
    results = search_memories_sync(
      query="test query",
      search_type="CHUNKS",
      top_k=2
    )
    
    assert len(results) == 2
    mock_run.assert_called_once()
