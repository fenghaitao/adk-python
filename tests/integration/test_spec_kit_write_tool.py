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

"""
Integration tests for SpecKitWriteTool improvements.

These tests verify the new append/overwrite behavior that prevents
catastrophic code deletion (wdt_dbg10 bug).
"""

import os
import tempfile
import shutil
from pathlib import Path
import pytest

# Import the tool to test
import sys
spec_kit_path = Path(__file__).parent.parent.parent / "contributing" / "samples" / "spec_kit_integration"
sys.path.insert(0, str(spec_kit_path))

from spec_kit_tools import SpecKitWriteTool
from unittest.mock import Mock


@pytest.fixture
def temp_dir():
    """Create a temporary directory for test files."""
    tmpdir = tempfile.mkdtemp()
    yield tmpdir
    # Cleanup
    shutil.rmtree(tmpdir)


@pytest.fixture
def write_tool():
    """Create a SpecKitWriteTool instance."""
    return SpecKitWriteTool()


@pytest.fixture
def tool_context():
    """Create a mock tool context for testing."""
    # For these tests, we don't need a real tool context
    # The write_tool doesn't actually use it for file operations
    return Mock()


class TestWriteFileAppendMode:
    """Test append mode (overwrite=False) behavior."""

    @pytest.mark.anyio
    async def test_append_to_existing_file(self, write_tool, tool_context, temp_dir):
        """Test that overwrite=False appends content to existing file."""
        test_file = os.path.join(temp_dir, "test.txt")
        
        # Create initial file
        with open(test_file, "w") as f:
            f.write("Hello")
        
        # Append content
        result = await write_tool.run_async(
            args={
                "file_path": test_file,
                "content": " World",
                "overwrite": False
            },
            tool_context=tool_context
        )
        
        # Verify result
        assert result["success"] is True
        assert result["mode"] == "append"
        assert result["original_size"] == 5  # "Hello"
        assert result["new_size"] == 11  # "Hello World"
        assert result["bytes_written"] == 6  # " World"
        
        # Verify file content
        with open(test_file, "r") as f:
            content = f.read()
        assert content == "Hello World"

    @pytest.mark.anyio
    async def test_append_default_behavior(self, write_tool, tool_context, temp_dir):
        """Test that default behavior (no overwrite param) appends."""
        test_file = os.path.join(temp_dir, "test.txt")
        
        # Create initial file
        with open(test_file, "w") as f:
            f.write("Line 1\\n")
        
        # Append without specifying overwrite (should default to False)
        result = await write_tool.run_async(
            args={
                "file_path": test_file,
                "content": "Line 2\\n"
            },
            tool_context=tool_context
        )
        
        assert result["success"] is True
        assert result["mode"] == "append"
        
        # Verify content
        with open(test_file, "r") as f:
            content = f.read()
        assert content == "Line 1\\nLine 2\\n"


class TestWriteFileBugPrevention:
    """Tests that verify the wdt_dbg10 catastrophic deletion bug is prevented."""

    @pytest.mark.anyio
    async def test_prevents_wdt_dbg10_bug_scenario(
        self, write_tool, tool_context, temp_dir
    ):
        """
        Reproduce the wdt_dbg10 bug scenario and verify it's now prevented.
        
        Original bug:
        - File had 537 lines of DML code
        - Agent wanted to ADD 2 helper methods
        - Agent called write_file with only the 2 helpers and overwrite=False
        - Old behavior: ERROR "file exists"
        - Agent retried with overwrite=True
        - Result: 537 lines → 47 lines (catastrophic deletion)
        
        New behavior:
        - Agent calls write_file with helpers and overwrite=False
        - Content is APPENDED to end of file
        - Original 537 lines preserved + 47 new lines = 584 lines ✅
        """
        test_file = os.path.join(temp_dir, "test_dev.dml")
        
        # Simulate original 537-line DML file
        original_content = "dml 1.4;\\ndevice test_dev;\\n\\n" + ("// Original implementation\\n" * 534)
        with open(test_file, "w") as f:
            f.write(original_content)
        
        original_size = os.path.getsize(test_file)
        
        # Simulate agent wanting to add helper methods (like in wdt_dbg10)
        helper_methods = """
// Helper method to return current WDOGVALUE
method get_current_wdogvalue() -> (uint64) {
    return 0;
}
"""
        
        # Agent calls write_file with overwrite=False (default)
        result = await write_tool.run_async(
            args={
                "file_path": test_file,
                "content": helper_methods,
                "overwrite": False
            },
            tool_context=tool_context
        )
        
        # Verify success
        assert result["success"] is True
        assert result["mode"] == "append"
        
        # Verify file grew (not shrunk!)
        assert result["new_size"] > result["original_size"]
        
        # Verify original content is preserved
        with open(test_file, "r") as f:
            final_content = f.read()
        
        assert "dml 1.4;" in final_content
        assert "device test_dev;" in final_content
        assert "get_current_wdogvalue" in final_content
