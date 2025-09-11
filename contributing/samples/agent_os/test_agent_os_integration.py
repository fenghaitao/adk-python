#!/usr/bin/env python3
"""Tests for Agent OS integration with ADK."""

import asyncio
import tempfile
from pathlib import Path

# Import from the ADK source directory
import sys
from pathlib import Path as PathLib

# Add the src directory to Python path for imports
current_dir = PathLib(__file__).parent
src_dir = current_dir.parent.parent.parent / "src"
sys.path.insert(0, str(src_dir))

from google.adk.agents.llm_agent import LlmAgent
try:
    from .agent_os_tools import create_agent_os_toolset
    from .agent_os_agent import AgentOsAgent
except ImportError:
    from agent_os_tools import create_agent_os_toolset
    from agent_os_agent import AgentOsAgent


class TestAgentOsIntegration:
    """Test cases for Agent OS integration."""

    def test_create_agent_os_toolset(self):
        """Test creating Agent OS toolset."""
        toolset = create_agent_os_toolset()
        assert toolset is not None
        assert len(toolset.tools) == 5  # 5 tools in the toolset

    def test_agent_os_agent_creation(self):
        """Test creating Agent OS Agent."""
        agent = AgentOsAgent(
            name="test_agent",
            model="gemini-2.0-flash",
        )
        assert agent.name == "test_agent"
        assert agent.model == "gemini-2.0-flash"
        assert len(agent.tools) == 1  # Should have Agent OS toolset

    def test_agent_os_agent_with_agent_os_config(self):
        """Test creating Agent OS Agent with Agent OS config."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create mock Agent OS structure
            agent_os_path = Path(temp_dir) / "agent-os"
            agent_os_path.mkdir()
            config_file = agent_os_path / "config.yml"
            config_file.write_text("agent_os_version: 1.4.1\n")
            
            agent = AgentOsAgent.create_with_agent_os_config(
                agent_os_path=str(agent_os_path),
                project_path=".",
            )
            assert agent is not None
            assert "Agent OS" in agent.instruction

    def test_add_agent_os_subagents(self):
        """Test adding Agent OS subagents."""
        agent = AgentOsAgent(name="test_agent")
        
        with tempfile.TemporaryDirectory() as temp_dir:
            agent_os_path = Path(temp_dir) / "agent-os"
            agent_os_path.mkdir()
            
            agent.add_agent_os_subagents(str(agent_os_path))
            
            # Should have 6 subagents
            assert len(agent.sub_agents) == 6
            subagent_names = [sub.name for sub in agent.sub_agents]
            assert "context_fetcher" in subagent_names
            assert "file_creator" in subagent_names
            assert "project_manager" in subagent_names
            assert "git_workflow" in subagent_names
            assert "test_runner" in subagent_names
            assert "date_checker" in subagent_names

    async def test_agent_os_tools(self):
        """Test Agent OS tools functionality."""
        toolset = create_agent_os_toolset()
        
        # Test read_file tool
        read_tool = toolset.tools[0]
        
        with tempfile.NamedTemporaryFile(mode='w', delete=False) as f:
            f.write("Hello, World!")
            temp_file = f.name
        
        try:
            # Mock tool context
            class MockToolContext:
                pass
            
            result = await read_tool.run_async(
                args={"file_path": temp_file},
                tool_context=MockToolContext()
            )
            
            assert "content" in result
            assert result["content"] == "Hello, World!"
            assert result["file_path"] == temp_file
            
        finally:
            Path(temp_file).unlink()

    async def test_write_file_tool(self):
        """Test write_file tool functionality."""
        toolset = create_agent_os_toolset()
        write_tool = toolset.tools[1]  # AgentOsWriteTool
        
        with tempfile.TemporaryDirectory() as temp_dir:
            test_file = Path(temp_dir) / "test.txt"
            
            # Mock tool context
            class MockToolContext:
                pass
            
            result = await write_tool.run_async(
                args={
                    "file_path": str(test_file),
                    "content": "Test content",
                    "overwrite": False
                },
                tool_context=MockToolContext()
            )
            
            assert result["success"] is True
            assert test_file.exists()
            assert test_file.read_text() == "Test content"

    async def test_grep_tool(self):
        """Test grep tool functionality."""
        toolset = create_agent_os_toolset()
        grep_tool = toolset.tools[2]  # AgentOsGrepTool
        
        with tempfile.TemporaryDirectory() as temp_dir:
            test_file = Path(temp_dir) / "test.txt"
            test_file.write_text("Hello, World!\nThis is a test.\nAnother line.")
            
            # Mock tool context
            class MockToolContext:
                pass
            
            result = await grep_tool.run_async(
                args={
                    "pattern": "test",
                    "file_path": str(test_file),
                    "case_sensitive": False
                },
                tool_context=MockToolContext()
            )
            
            assert "matches" in result
            assert len(result["matches"]) > 0
            assert "test" in result["matches"][0].lower()

    async def test_glob_tool(self):
        """Test glob tool functionality."""
        toolset = create_agent_os_toolset()
        glob_tool = toolset.tools[3]  # AgentOsGlobTool
        
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create some test files
            (Path(temp_dir) / "test1.txt").touch()
            (Path(temp_dir) / "test2.txt").touch()
            (Path(temp_dir) / "other.py").touch()
            
            # Mock tool context
            class MockToolContext:
                pass
            
            result = await glob_tool.run_async(
                args={
                    "pattern": "*.txt",
                    "directory": temp_dir
                },
                tool_context=MockToolContext()
            )
            
            assert "files" in result
            assert len(result["files"]) == 2
            assert all(f.endswith(".txt") for f in result["files"])


async def run_async_tests():
    """Run async tests."""
    test = TestAgentOsIntegration()
    
    # Test agent OS tools
    await test.test_agent_os_tools()
    print("✓ Agent OS tools test passed")
    
    # Test write file tool
    await test.test_write_file_tool()
    print("✓ Write file tool test passed")
    
    # Test grep tool
    await test.test_grep_tool()
    print("✓ Grep tool test passed")
    
    # Test glob tool
    await test.test_glob_tool()
    print("✓ Glob tool test passed")


if __name__ == "__main__":
    # Run basic tests
    test = TestAgentOsIntegration()
    
    print("Testing Agent OS Integration...")
    
    # Test toolset creation
    test.test_create_agent_os_toolset()
    print("✓ Toolset creation test passed")
    
    # Test agent creation
    test.test_agent_os_agent_creation()
    print("✓ Agent creation test passed")
    
    # Test with Agent OS config
    test.test_agent_os_agent_with_agent_os_config()
    print("✓ Agent OS config test passed")
    
    # Test subagents
    test.test_add_agent_os_subagents()
    print("✓ Subagents test passed")
    
    # Run async tests
    print("\nRunning async tests...")
    asyncio.run(run_async_tests())
    
    print("\n🎉 All tests passed!")
