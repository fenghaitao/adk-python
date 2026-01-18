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

"""Tests for memory indexing and retrieval."""

from __future__ import annotations

import tempfile
from pathlib import Path

import pytest

# Check if chromadb is available
try:
  import chromadb
  CHROMADB_AVAILABLE = True
except ImportError:
  CHROMADB_AVAILABLE = False

if CHROMADB_AVAILABLE:
  from dspy_openspec.memory.indexer import MemoryIndexer
  from dspy_openspec.memory.retriever import MemoryRetriever


@pytest.mark.skipif(not CHROMADB_AVAILABLE, reason="chromadb not installed")
def test_memory_indexer():
  """Test memory indexing."""
  with tempfile.TemporaryDirectory() as tmpdir:
    # Create test memory files
    memory_dir = Path(tmpdir) / "memories"
    memory_dir.mkdir()
    
    (memory_dir / "01_DML_Basics.md").write_text(
      "# DML Basics\n\nDML is a device modeling language."
    )
    (memory_dir / "02_Test_Patterns.md").write_text(
      "# Test Patterns\n\nPython tests for Simics devices."
    )
    
    # Create indexer
    persist_dir = Path(tmpdir) / "chromadb"
    indexer = MemoryIndexer(
      memory_dir=memory_dir,
      persist_directory=str(persist_dir)
    )
    
    # Index memories
    result = indexer.index_memories()
    
    assert result["status"] == "success"
    assert result["files_indexed"] == 2
    assert result["chunks_created"] > 0
    
    # Get stats
    stats = indexer.get_stats()
    assert stats["total_chunks"] > 0
    assert stats["unique_files"] == 2


@pytest.mark.skipif(not CHROMADB_AVAILABLE, reason="chromadb not installed")
def test_memory_retriever():
  """Test memory retrieval."""
  with tempfile.TemporaryDirectory() as tmpdir:
    # Create and index test memories
    memory_dir = Path(tmpdir) / "memories"
    memory_dir.mkdir()
    
    (memory_dir / "01_DML_Timers.md").write_text(
      "# DML Timers\n\n"
      "Use the `after` statement for timer implementation. "
      "Never use cycle-by-cycle updates as they cause performance issues."
    )
    
    persist_dir = Path(tmpdir) / "chromadb"
    indexer = MemoryIndexer(
      memory_dir=memory_dir,
      persist_directory=str(persist_dir)
    )
    indexer.index_memories()
    
    # Create retriever
    retriever = MemoryRetriever(
      persist_directory=str(persist_dir),
      k=1
    )
    
    # Retrieve memories
    result = retriever.forward(
      task_description="how to implement timer device",
      category="DML"
    )
    
    assert len(result.passages) > 0
    assert "after" in result.passages[0].lower()


@pytest.mark.skipif(not CHROMADB_AVAILABLE, reason="chromadb not installed")
def test_category_filtering():
  """Test category-based filtering."""
  with tempfile.TemporaryDirectory() as tmpdir:
    # Create memories with different categories
    memory_dir = Path(tmpdir) / "memories"
    memory_dir.mkdir()
    
    (memory_dir / "01_DML_Content.md").write_text("DML specific content")
    (memory_dir / "02_Test_Content.md").write_text("Test specific content")
    
    persist_dir = Path(tmpdir) / "chromadb"
    indexer = MemoryIndexer(
      memory_dir=memory_dir,
      persist_directory=str(persist_dir)
    )
    indexer.index_memories()
    
    # Test DML retrieval
    retriever = MemoryRetriever(persist_directory=str(persist_dir), k=1)
    dml_result = retriever.retrieve_for_dml("DML implementation")
    
    assert len(dml_result) > 0
    
    # Test Test retrieval
    test_result = retriever.retrieve_for_test("test creation")
    
    assert len(test_result) > 0
