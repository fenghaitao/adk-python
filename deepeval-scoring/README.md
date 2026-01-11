# DeepEval Scoring System

A standalone DeepEval-based scoring system for evaluating `apply_agent` implementations.

## Quick Start

See [QUICKSTART.md](QUICKSTART.md) for a 5-minute getting started guide.

## Features

- **Pure DeepEval**: No ADK dependencies required
- **Custom Metrics**: Code correctness, test coverage, code style, documentation usage
- **Multiple Formats**: Markdown, JSON, and HTML reports
- **CLI Tool**: Easy to use command-line interface
- **Portable**: Works anywhere Python is installed

## Installation

### Prerequisites

This project requires the local DeepEval installation from the parent directory:

```bash
# First, ensure deepeval is installed from the parent directory
cd ../deepeval
pip install -e .
cd ../deepeval-scoring
```

### Install deepeval-scoring

```bash
# Install in editable mode with all dependencies
pip install -e .
```

### Install with development dependencies

```bash
# Includes testing and linting tools (pytest, black, pylint, mypy)
pip install -e ".[dev]"
```

## Usage

### Basic Usage

```bash
python score.py \
  --workdir /path/to/project \
  --device wdt \
  --model iflow/qwen3-coder-plus
```

This will:
1. Evaluate code quality using LLM-based metrics
2. Evaluate agent behavior (if session logs available)
3. Generate a `score.md` report in the workdir

### Scoring Modes

Choose between different evaluation approaches:

```bash
# LLM-based scoring (default) - Uses AI models for evaluation
python score.py \
  --workdir /path/to/project \
  --device wdt \
  --model iflow/qwen3-coder-plus \
  --scoring-mode llm

# Deterministic scoring - Fast, consistent, no LLM calls
python score.py \
  --workdir /path/to/project \
  --device wdt \
  --scoring-mode deterministic

# Hybrid scoring - Combines both approaches with intelligent weighting
python score.py \
  --workdir /path/to/project \
  --device wdt \
  --model iflow/qwen3-coder-plus \
  --scoring-mode hybrid
```

**Hybrid Mode Weighting:**
- **40% Deterministic** - Objective metrics (register coverage, test coverage, build success)
- **40% LLM Code Quality** - Subjective analysis (code style, correctness, best practices)  
- **20% Agent Behavior** - Process evaluation (documentation usage, efficiency)

This prevents double-counting while combining the strengths of both approaches.

**Scoring Mode Comparison:**

| Mode | Speed | Cost | Consistency | Coverage |
|------|-------|------|-------------|----------|
| `deterministic` | ⚡ Fast | 💰 Free | 🎯 Perfect | 📊 Basic |
| `llm` | 🐌 Slow | 💸 Expensive | 🎲 Variable | 🔍 Deep |
| `hybrid` | ⚖️ Medium | 💵 Moderate | 📈 Good | 🎯 Complete |

### Advanced Options

```bash
# Use different model and specify agent type
python score.py \
  --workdir /path/to/project \
  --device wdt \
  --model github_copilot/gpt-4.1 \
  --agent kiro-cli

# Skip behavior evaluation
python score.py \
  --workdir /path/to/project \
  --device wdt \
  --skip-behavior

# Generate JSON output
python score.py \
  --workdir /path/to/project \
  --device wdt \
  --format json \
  --output results.json

# Generate HTML report
python score.py \
  --workdir /path/to/project \
  --device wdt \
  --format html \
  --output report.html

# Enable MLflow experiment tracking
python score.py \
  --workdir /path/to/project \
  --device wdt \
  --model iflow/qwen3-coder-plus \
  --mlflow

# Use custom MLflow tracking URI
python score.py \
  --workdir /path/to/project \
  --device wdt \
  --model iflow/qwen3-coder-plus \
  --mlflow \
  --mlflow-tracking-uri http://localhost:5000

# Use custom experiment name
python score.py \
  --workdir /path/to/project \
  --device wdt \
  --model iflow/qwen3-coder-plus \
  --mlflow \
  --mlflow-experiment-name "wdt-evaluation-v2"
```

## MLflow Integration

DeepEval Scoring includes MLflow integration for experiment tracking, artifact storage, and seamless integration with the optimization workflow.

### Features

- **Experiment Tracking**: Automatically organize runs by device and configuration
- **Metrics Logging**: Track all evaluation scores and component metrics
- **Artifact Storage**: Store reports, raw results, session logs, and implementation files
- **Session Data for Optimizer**: Automatically log session data in format compatible with optimization tools
- **Run Comparison**: Compare performance across different models and configurations
- **Historical Analysis**: Track performance trends over time

### Quick Start

```bash
# Enable MLflow tracking
python score.py \
  --workdir /path/to/project \
  --device wdt \
  --model iflow/qwen3-coder-plus \
  --mlflow

# View results in MLflow UI
cd deepeval-scoring
mlflow ui
# Open http://localhost:5000
```

### Artifacts Logged

Each MLflow run automatically logs:
- **Session Data**: `session_data/session_data.json` - For use with optimizer tools
- **Implementation Files**: `implementation/{device}/` - DML and test files
- **Session Logs**: `logs/*.session.txt` - Agent session logs
- **Score Report**: `reports/score.md` - Evaluation report
- **Raw Results**: `results/raw_results.json` - Detailed evaluation data
- **Configuration**: `config/mlflow_config.yaml` - MLflow settings

### Integration with Optimizer

Extract session data from MLflow runs for optimization:

```bash
# Extract low-scoring sessions for instruction optimization
python extract_mlflow_sessions.py \
  --experiment wdt-evaluation \
  --max-score 0.8 \
  --output sessions.json

# Optimize instructions using extracted sessions
python optimize_instructions.py \
  --sessions sessions.json \
  --instructions ../contributing/samples/openspec_integration/apply_agent_instruction.md \
  --output optimized_instructions.md

# Optimize memory files
python optimize_memory_file.py \
  --sessions sessions.json \
  --memory-file ../openspec-memories/dml/01_dml_syntax_errors.md \
  --output optimized_memory.md
```

### Configuration

MLflow settings are in `config/mlflow_config.yaml`:

```yaml
mlflow:
  tracking_uri: "file://{{ PROJECT_ROOT }}/deepeval-scoring/mlruns"
  experiment_naming: "{device_name}-evaluation"
  artifacts:
    log_session_data: true  # For optimizer
    log_implementation_files: true  # DML and tests
    log_session_logs: true
    log_score_file: true
```

### Advanced Usage

```bash
# Use custom tracking URI
python score.py \
  --workdir /path/to/project \
  --device wdt \
  --mlflow \
  --mlflow-tracking-uri file:///custom/path/mlruns

# Use custom experiment name
python score.py \
  --workdir /path/to/project \
  --device wdt \
  --mlflow \
  --mlflow-experiment-name my-experiment
```

For complete documentation, see [MLFLOW_INTEGRATION.md](MLFLOW_INTEGRATION.md).

## Scoring Criteria

When using `--scoring-mode deterministic` or `hybrid`:

1. **Build Success** (20% weight)
   - DML file exists and is readable
   - Basic file structure validation

2. **Register Coverage** (25% weight)
   - Percentage of spec-required registers implemented
   - Extracted using DML parser

3. **Test Coverage** (25% weight)
   - Percentage of implemented registers with tests
   - Heuristic matching of test names to registers

4. **Implementation Completeness** (20% weight)
   - Session variables usage
   - Reset logic implementation
   - Interrupt logic implementation
   - Methods and events presence

5. **Code Structure** (10% weight)
   - Import statements
   - Code comments and documentation
   - File size reasonableness
   - Syntax correctness

### LLM-Based Scoring (90 points)

When using `--scoring-mode llm` or `hybrid`:

1. **Code Correctness** (threshold: 0.8)
   - Register implementation
   - Event-based timing
   - Lazy evaluation
   - Interrupt handling
   - Reset logic
   - Session state
   - No anti-patterns

2. **Test Coverage** (threshold: 0.7)
   - Register coverage
   - Edge cases
   - Error handling
   - Integration tests
   - Test quality

3. **Code Style** (threshold: 0.9)
   - Naming conventions
   - Code organization
   - Documentation
   - Best practices
   - Maintainability

### Agent Behavior (90 points)

Available only with LLM-based modes:

1. **Agent Behavior** (threshold: 0.7)
   - Instruction following and workflow adherence
   - Tool usage and task completion
   - Error handling and recovery
   - Documentation usage and best practices applied
   - Problem solving and efficiency
   
   For `--agent kiro-cli`, the evaluation focuses on OpenSpec-specific workflow steps like reading openspec/AGENTS.md, loading DML knowledge, creating proper proposals, and running validation.

## Project Structure

```
deepeval-scoring/
├── metrics/                    # Custom DeepEval metrics
│   ├── code_correctness.py
│   ├── test_coverage.py
│   ├── code_style.py
│   └── documentation_usage.py
├── evaluators/                 # Evaluation orchestrators
│   ├── code_evaluator.py
│   └── behavior_evaluator.py
├── parsers/                    # File parsers
│   ├── dml_parser.py
│   ├── test_parser.py
│   ├── spec_parser.py
│   └── session_parser.py
├── score.py                    # Main CLI tool
├── report_generator.py         # Report generation
├── config.yaml                 # Configuration
└── requirements.txt            # Dependencies
```

## Configuration

Edit `config.yaml` to customize:
- Model settings
- Metric thresholds
- Scoring weights
- Report settings

## Integration with OpenSpec

Add to your `run_openspec.sh` after the apply phase:

```bash
echo "📊 Scoring implementation..."
python deepeval-scoring/score.py \
  --workdir "$PROJECT_NAME" \
  --device "$DEVICE_NAME" \
  --model "$MODEL"

if [ $? -eq 0 ]; then
  echo "✅ Implementation passed quality checks"
else
  echo "❌ Implementation needs improvement"
  echo "📄 See score.md for details"
fi
```

## Environment Variables

For iflow models:
```bash
export IFLOW_API_KEY="your-api-key"
```

For OpenAI models:
```bash
export OPENAI_API_KEY="your-api-key"
```

For detailed LiteLLM session logging:
```bash
export DEEPEVAL_DEBUG=1
```

This will enable detailed logging of all LLM interactions and save them to:
- `.deepeval/litellm_session_YYYYMMDD_HHMMSS.log` - Standard LiteLLM logs
- `.deepeval/litellm_detailed_session_YYYYMMDD_HHMMSS.log` - Detailed request/response logs

Each evaluation run creates new timestamped log files to prevent overwriting previous sessions.

## Exit Codes

- `0`: Overall score >= 70% (pass)
- `1`: Overall score < 70% (fail)

## Example Output

```
🔍 Evaluating code quality...
🔍 Evaluating agent behavior...
📝 Generating report...
✅ Report saved to: /path/to/project/score.md

============================================================
EVALUATION SUMMARY
============================================================

📊 Code Quality: 85.0% (77/90)
  • Code Correctness: 90.0%
  • Test Coverage: 75.0%
  • Code Style: 90.0%

🤖 Agent Behavior: 80.0% (72/90)
  • Documentation Usage: 80.0%

🎯 Overall Score: 82.5% (149/180)
============================================================
```

## Troubleshooting

### Missing Files

If the tool can't find DML files or tests, check:
- Workdir path is correct
- Device name matches directory name
- Files are in expected locations:
  - DML: `simics-project/modules/{device}/{device}.dml`
  - Tests: `simics-project/modules/{device}/test/s-*.py`
  - Spec: `openspec/specs/spec.md`

### API Errors

If you get API errors:
- Check API key is set correctly
- Verify model name is correct
- Check network connectivity
- Try a different model with `--model`

### Low Scores

If scores are unexpectedly low:
- Review the detailed report for specific issues
- Check the "reason" field for each metric
- Verify code follows DML best practices
- Ensure tests cover all requirements

## Development

### Setup Development Environment

```bash
# Clone and install with dev dependencies
cd deepeval-scoring
pip install -e ".[dev]"
```

### Code Quality Tools

The project uses standard Python tools configured in `pyproject.toml`:

```bash
# Format code with black
black .

# Sort imports with isort
isort .

# Lint with pylint
pylint metrics evaluators parsers

# Type check with mypy
mypy metrics evaluators parsers

# Run tests with pytest
pytest tests/
```

### Project Configuration

All project configuration is in `pyproject.toml`:
- Package metadata and dependencies
- Tool configurations (black, isort, pylint, mypy, pytest)
- Build system settings

### Adding a New Metric

To add a new metric:

1. Create metric class in `metrics/`:
```python
from deepeval.metrics import BaseMetric

class MyMetric(BaseMetric):
  def measure(self, test_case):
    # Evaluation logic
    return score
```

2. Add to evaluator in `evaluators/`:
```python
metrics.append(MyMetric(model=self.model))
```

3. Update configuration in `config.yaml`

## License

Copyright 2025 Google LLC. Licensed under Apache 2.0.
