# Context Management for ADK-Python

This directory contains a comprehensive context management solution for ADK-Python that provides intelligent conversation history management, similar to OpenHands' condenser system.

## 🎯 Features

- **Automatic Context Condensation**: Automatically manages conversation history when approaching token limits
- **LLM-Powered Summarization**: Uses intelligent summarization to preserve important context
- **Smart Preservation**: Keeps system messages and recent conversation turns intact
- **Memory Storage**: Stores conversation summaries for debugging and analysis
- **Production Ready**: Configurable, monitored, and transparent operation

## 📁 Files

### Core Implementation
- **`advanced_context_manager.py`** - Main implementation (located in this directory)
  - `AdvancedContextManager` - Core context management logic
  - `SmartAgent` - Wrapper that adds context management to any ADK agent
  - `ContextConfig` - Configuration options

### Examples and Documentation
- **`agent.py`** - Complete example agent with context management
- **`context_manager_example.py`** - Detailed usage examples and demonstrations
- **`integration_guide.py`** - Step-by-step integration instructions

## 🚀 Quick Start

### 1. Basic Usage (3 lines of code)

```python
from google.adk.agents.llm_agent import LlmAgent
from advanced_context_manager import SmartAgent, ContextConfig

# Your existing agent  
base_agent = LlmAgent(model="gemini-2.0-flash", tools=[])

# Add context management
smart_agent = SmartAgent(base_agent, ContextConfig(max_tokens=8000))

# Use exactly as before - now with unlimited context!
response = await smart_agent.send_message("Long conversation...")
```

### 2. Run the Example

```bash
cd contributing/samples/context_management
python agent.py
```

### 3. Advanced Configuration

```python
config = ContextConfig(
    max_tokens=8000,                    # When to trigger condensation
    keep_system_messages=3,             # Preserve system context
    keep_recent_turns=10,               # Keep recent conversation
    summarization_model="gemini-2.0-flash",  # Model for summaries
    enable_memory_storage=True          # Store for debugging
)

smart_agent = SmartAgent(base_agent, config)
```

## 🔧 How It Works

1. **Monitors** conversation token count automatically
2. **Detects** when approaching the configured limit (e.g., 8000 tokens)
3. **Preserves** system messages and recent conversation turns
4. **Summarizes** middle conversation using LLM intelligence
5. **Reconstructs** context as: `[System] + [Summary] + [Recent]`
6. **Logs** the process transparently

## 📊 Benefits

| Feature | Without Context Management | With Smart Context Management |
|---------|---------------------------|-------------------------------|
| **Conversation Length** | ❌ Limited by token window | ✅ Unlimited |
| **Context Preservation** | ❌ Abrupt truncation | ✅ Intelligent summarization |
| **Important Info** | ❌ Can be lost | ✅ Preserved in summaries |
| **Setup Effort** | ⚠️ Manual implementation | ✅ 3-line integration |
| **Transparency** | ❌ Silent failures | ✅ Logged operations |

## 🆚 Comparison with Other Approaches

### vs. OpenHands Condenser
- ✅ **More configurable** - Fine-tune all parameters
- ✅ **Manual control** - Can implement custom logic
- ✅ **Transparent** - See exactly what's happening
- ⚠️ **Setup required** - Not built-in (but minimal)

### vs. Simple Truncation
- ✅ **Intelligent** - LLM-powered vs crude cutting
- ✅ **Context-aware** - Preserves important information
- ✅ **Transparent** - Shows what was condensed
- ✅ **Configurable** - Customize preservation logic

## 📋 Integration Options

# Wrapper (Recommended)
```python
from advanced_context_manager import SmartAgent, ContextConfig
smart_agent = SmartAgent(existing_agent, config)
```

### Option 2: Manual Callback
```python
context_manager = AdvancedContextManager(config)

async def callback(callback_context, llm_request):
    await context_manager.condense_context(llm_request, callback_context.agent)

agent = Agent(before_model_callback=callback)
```

### Option 3: Custom Implementation
Extend `AdvancedContextManager` for custom summarization logic.

## 🧪 Testing

Comprehensive test suite included with multiple testing approaches:

### **Test Files:**
- **`test_context_management.py`** - Complete test suite with async tests
- **`test_simple.py`** - Focused unit tests (pytest compatible)
- **`conftest.py`** - Pytest fixtures and configuration

### **Run Tests:**
```bash
# Run simple unit tests
python test_simple.py

# Run with pytest (recommended)
pip install pytest
pytest test_simple.py -v

# Run comprehensive test suite
python test_context_management.py
```

### **Test Coverage:**
- ✅ Configuration validation
- ✅ Token counting accuracy
- ✅ Conversation turn identification
- ✅ Context condensation logic
- ✅ Memory preservation
- ✅ Error handling and edge cases
- ✅ Smart agent integration
- ✅ Long conversation scenarios (20+ turns)
- ✅ Context recovery after condensation
- ✅ Fallback mechanisms

## 🔍 Monitoring and Debugging

### View Condensation Events
```python
# Real-time monitoring
print("Context condensed: 12000 → 4000 tokens")

# Memory inspection
memory_summary = smart_agent.get_memory_summary()
print(memory_summary)
```

### Production Monitoring
- Token usage tracking
- Condensation frequency
- Memory bank analysis
- Performance metrics

## 📚 Further Reading

- `context_manager_example.py` - Detailed examples and use cases
- `integration_guide.py` - Complete integration documentation
- `agent.py` - Production-ready example implementation

## 🤝 Contributing

This context management system is designed to be:
- **Extensible** - Easy to add custom summarization strategies
- **Configurable** - All behavior can be tuned
- **Observable** - Full transparency into operations
- **Testable** - Comprehensive test scenarios included

Feel free to extend and customize for your specific use cases!