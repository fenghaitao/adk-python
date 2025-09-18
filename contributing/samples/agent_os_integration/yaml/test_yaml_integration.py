#!/usr/bin/env python3
"""Test script for Agent OS YAML integration."""

import asyncio
import tempfile
from pathlib import Path

# Add the parent directory to Python path
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))

from yaml_loader import AgentOsYamlLoader, load_agent_from_yaml


async def test_basic_functionality():
    """Test basic YAML functionality."""
    print("🧪 Testing Basic YAML Functionality")
    print("=" * 40)
    
    try:
        # Test 1: Load agent from YAML
        print("1. Testing agent loading...")
        agent = load_agent_from_yaml()
        assert agent.name == "agent_os_agent"
        assert agent.model == "iflow/Qwen3-Coder"
        assert len(agent.tools) == 1
        assert len(agent.sub_agents) == 6
        print("✅ Agent loading test passed")
        
        # Test 2: Test YAML loader functionality
        print("2. Testing YAML loader...")
        loader = AgentOsYamlLoader()
        
        # Test configuration access
        workflows = loader.get_workflows()
        assert len(workflows) == 4
        assert "product_planning" in workflows
        assert "spec_creation" in workflows
        print("✅ YAML loader test passed")
        
        # Test 3: Test tools functionality
        print("3. Testing tools functionality...")
        toolset = agent.tools[0]
        assert toolset.name == "agent_os_toolset"
        assert len(toolset.tools) == 5
        
        # Test individual tools
        tool_names = [tool.name for tool in toolset.tools]
        expected_tools = ['read_file', 'write_file', 'grep_search', 'glob_search', 'bash_command']
        for expected_tool in expected_tools:
            assert expected_tool in tool_names
        print("✅ Tools functionality test passed")
        
        # Test 4: Test subagents
        print("4. Testing subagents...")
        subagent_names = [sub.name for sub in agent.sub_agents]
        expected_subagents = ['context_fetcher', 'file_creator', 'project_manager', 'git_workflow', 'test_runner', 'date_checker']
        for expected_subagent in expected_subagents:
            assert expected_subagent in subagent_names
        print("✅ Subagents test passed")
        
        # Test 5: Test file operations
        print("5. Testing file operations...")
        write_tool = toolset.tools[1]  # AgentOsWriteTool
        read_tool = toolset.tools[0]   # AgentOsReadTool
        
        class MockToolContext:
            pass
        
        # Test write file
        with tempfile.TemporaryDirectory() as temp_dir:
            test_file = Path(temp_dir) / "test_yaml.txt"
            test_content = "Hello from YAML configuration!"
            
            write_result = await write_tool.run_async(
                args={
                    "file_path": str(test_file),
                    "content": test_content,
                    "overwrite": False
                },
                tool_context=MockToolContext()
            )
            
            assert write_result["success"] is True
            assert test_file.exists()
            
            # Test read file
            read_result = await read_tool.run_async(
                args={"file_path": str(test_file)},
                tool_context=MockToolContext()
            )
            
            assert "content" in read_result
            assert read_result["content"] == test_content
        print("✅ File operations test passed")
        
        # Test 6: Test bash operations
        print("6. Testing bash operations...")
        bash_tool = toolset.tools[4]  # AgentOsBashTool
        
        bash_result = await bash_tool.run_async(
            args={
                "command": "echo 'YAML test successful'",
                "working_directory": ".",
                "timeout": 10
            },
            tool_context=MockToolContext()
        )
        
        assert "stdout" in bash_result
        assert "YAML test successful" in bash_result["stdout"]
        assert bash_result["return_code"] == 0
        print("✅ Bash operations test passed")
        
        print("\n🎉 All basic functionality tests passed!")
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_configuration_validation():
    """Test configuration validation."""
    print("\n🔍 Testing Configuration Validation")
    print("=" * 40)
    
    try:
        loader = AgentOsYamlLoader()
        
        # Test configuration summary
        print("1. Testing configuration summary...")
        loader.print_config_summary()
        print("✅ Configuration summary test passed")
        
        # Test environment validation
        print("2. Testing environment validation...")
        env_valid = loader.validate_environment()
        print(f"Environment validation result: {env_valid}")
        print("✅ Environment validation test passed")
        
        # Test workflow access
        print("3. Testing workflow access...")
        workflows = loader.get_workflows()
        for workflow_name, workflow_config in workflows.items():
            assert "name" in workflow_config
            assert "description" in workflow_config
            assert "steps" in workflow_config
            assert isinstance(workflow_config["steps"], list)
        print("✅ Workflow access test passed")
        
        # Test runner configuration
        print("4. Testing runner configuration...")
        runner_config = loader.get_runner_config()
        assert "type" in runner_config
        print("✅ Runner configuration test passed")
        
        # Test logging configuration
        print("5. Testing logging configuration...")
        logging_config = loader.get_logging_config()
        assert "level" in logging_config
        print("✅ Logging configuration test passed")
        
        print("\n🎉 All configuration validation tests passed!")
        return True
        
    except Exception as e:
        print(f"❌ Configuration validation test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


async def main():
    """Main test function."""
    print("🤖 Agent OS YAML Integration Test Suite")
    print("=" * 50)
    
    # Run tests
    basic_test_passed = await test_basic_functionality()
    config_test_passed = test_configuration_validation()
    
    # Summary
    print("\n📊 Test Results Summary")
    print("=" * 30)
    print(f"Basic Functionality: {'✅ PASSED' if basic_test_passed else '❌ FAILED'}")
    print(f"Configuration Validation: {'✅ PASSED' if config_test_passed else '❌ FAILED'}")
    
    if basic_test_passed and config_test_passed:
        print("\n🎉 All tests passed! YAML integration is working correctly.")
        return True
    else:
        print("\n❌ Some tests failed. Please check the errors above.")
        return False


if __name__ == "__main__":
    success = asyncio.run(main())
    exit(0 if success else 1)
