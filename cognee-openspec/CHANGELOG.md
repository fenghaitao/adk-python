# Changelog

## 2025-01-19 - Model Configuration Updates

### Changed
- **Default iflow model**: Changed from `qwen-turbo` to `qwen3-coder-plus`
  - Reason: Better optimized for code-related tasks (DML, test code, etc.)
  - Performance: Excellent quality for code generation and understanding
  - Cost: Similar pricing to qwen-turbo (~$0.10/$0.30 per 1M tokens)

### Updated Files
- `setup_iflow.sh` - Default model now `qwen3-coder-plus`
- `examples/memory_example.py` - Uses `qwen3-coder-plus` for iflow
- `test_model_config.py` - Recommends `qwen3-coder-plus` first
- `MODEL_SETUP.md` - Updated all examples and recommendations
- `QUICKSTART.md` - Updated quick start examples
- `SETUP_COMPLETE.md` - Updated configuration examples
- `IMPLEMENTATION_SUMMARY.md` - Updated technical details
- `README.md` - Updated quick setup section

### Model Recommendations

#### For OpenSpec (Code-Focused Tasks)
1. **iflow qwen3-coder-plus** (recommended) - Code-optimized, fast, cost-effective
2. **GitHub Copilot GPT-4o** - Excellent quality, included with subscription
3. **OpenAI GPT-4o** - Industry standard, excellent quality

#### For General Tasks
1. **iflow qwen-max** - Best quality from iflow
2. **OpenAI GPT-4o** - Industry standard
3. **iflow qwen-turbo** - Fast and cost-effective

### Usage

```bash
# Quick setup with qwen3-coder-plus (default)
./setup_iflow.sh your-iflow-api-key

# Or specify a different model
./setup_iflow.sh your-iflow-api-key dashscope/qwen-max

# Manual configuration
export LLM_API_KEY="your-iflow-api-key"
export LLM_MODEL="dashscope/qwen3-coder-plus"
export LLM_ENDPOINT="https://apis.iflow.cn/v1/"
export LLM_PROVIDER="custom"
```

### Available iflow Models

| Model | Best For | Speed | Cost | Quality |
|-------|----------|-------|------|---------|
| qwen3-coder-plus | Code tasks (DML, tests) | ⚡⚡⚡⚡ | 💰 | ⭐⭐⭐⭐⭐ |
| qwen-turbo | High-volume, general | ⚡⚡⚡⚡ | 💰 | ⭐⭐⭐ |
| qwen-plus | Balanced tasks | ⚡⚡⚡ | 💰 | ⭐⭐⭐⭐ |
| qwen-max | Best quality | ⚡⚡ | 💰 | ⭐⭐⭐⭐⭐ |
| qwen-vl-plus | Vision + language | ⚡⚡ | 💰💰 | ⭐⭐⭐⭐ |

### Why qwen3-coder-plus?

1. **Code-Optimized**: Specifically trained for code understanding and generation
2. **OpenSpec Focus**: Better at understanding DML syntax, test patterns, and device modeling
3. **Performance**: Excellent quality for code-related tasks
4. **Cost-Effective**: Similar pricing to qwen-turbo but better for code
5. **Speed**: Very fast response times

### Backward Compatibility

All existing configurations continue to work. If you're using `qwen-turbo` or other models, no changes are required. This update only changes the default recommendation.
