# Hello World Gemini CLI CodeAssist Agent

This sample demonstrates a comprehensive ADK agent that uses the Gemini CLI CodeAssist model with full tool functionality. The agent can roll dice and check prime numbers, showcasing function calling capabilities with the CodeAssist-backed Gemini provider.

## Features

- **Dice Rolling**: Roll dice with any number of sides using tools
- **Prime Number Checking**: Check if numbers are prime using tools
- **File Operations**: Read, write, and list files using MCP filesystem tools
- **Tool State Management**: Maintains state of previous dice rolls
- **Interactive Mode**: Command-line interface for testing
- **Function Calling**: Demonstrates parallel and sequential tool usage
- **Safety Settings**: Configured to work properly with dice rolling content
- **Streaming Support**: Full streaming capability with Server-Sent Events (SSE)

## Files

- `agent.py`: Main agent implementation with full tool functionality ✅
- `main.py`: Interactive runner for the agent ✅
- `filesystem_server.py`: MCP filesystem server for file operations ✅
- `simple_agent.py`: Simplified version without tools (for comparison)
- `test_validation.py`: Basic validation test suite
- `test_tools_working.py`: Comprehensive tool functionality tests ✅
- `test_streaming.py`: Streaming behavior validation ✅
- `test_direct_streaming.py`: Direct streaming API tests ✅

## Usage

### Start the Filesystem Server (Required for File Operations)
```bash
python filesystem_server.py
```
This starts the MCP filesystem server at http://localhost:3000/sse that enables file operations.

### Interactive Mode
```bash
python main.py
```

### Run Tool Functionality Tests
```bash
python test_tools_working.py
```

### Run Streaming Tests
```bash
python test_direct_streaming.py
```

### Run Basic Validation Tests
```bash
python test_validation.py
```

### Test File Operations
```bash
python tmp_rovodev_test_file_ops.py
```
Note: Requires the filesystem server to be running first.

## Example Interactions

```
You: Roll a 6-sided die and check if the result is prime
Agent: I rolled a 6-sided die and got a 3.

3 is a prime number.

You: Roll a 20-sided die
Agent: I rolled a 20-sided die and got a 15.

You: Check if 7 is prime
Agent: 7 is a prime number.

You: what were my previous rolls?
Agent: You previously rolled: 3, 15

You: List the files in the current directory
Agent: Here are the files in the current directory:
- agent.py
- main.py
- filesystem_server.py
- README.md
- ...

You: Read the contents of README.md
Agent: [Shows the contents of the README.md file]
```

## Tool Functionality

✅ **Fully Working**: Tools are now fully functional with Gemini CLI CodeAssist thanks to improved JSON serialization handling in the ADK framework.

The agent demonstrates:
1. Function calling with state management
2. Sequential tool execution (roll then check)
3. Parallel tool execution capabilities
4. Error handling and user interaction
5. Safety settings for content generation

## Requirements

- Gemini CLI CodeAssist access configured
- ADK Python package installed

## Validation

Run the comprehensive test suite to verify all functionality:
```bash
python test_tools_working.py
```

This validates:
1. Dice rolling tool functionality
2. Prime checking tool functionality
3. Tool state management
4. Response accuracy and consistency

For streaming functionality testing:
```bash
python test_direct_streaming.py
```

This validates:
1. Multi-chunk streaming responses (12+ chunks for long content)
2. Single-chunk non-streaming responses
3. Server-Sent Events (SSE) parsing
4. Streaming endpoint switching (`streamGenerateContent` vs `generateContent`)

For basic conversation testing:
```bash
python test_validation.py
```