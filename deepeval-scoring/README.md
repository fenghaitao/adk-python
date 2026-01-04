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

### Option 1: Install from source (recommended)

```bash
cd deepeval-scoring
pip install -e .
```

This installs the package in editable mode with all dependencies.

### Option 2: Install with requirements.txt

```bash
cd deepeval-scoring
pip install -r requirements.txt
```

### Option 3: Install with development dependencies

```bash
cd deepeval-scoring
pip install -e ".[dev]"
```

This includes testing and linting tools (pytest, black, pylint, mypy).

## Usage

### Basic Usage

```bash
python score.py \
  --workdir /path/to/project \
  --device wdt \
  --model iflow/qwen3-coder-plus
```

This will:
1. Evaluate code quality (DML implementation and tests)
2. Evaluate agent behavior (if session logs available)
3. Generate a `score.md` report in the workdir

### Advanced Options

```bash
# Use different model
python score.py \
  --workdir /path/to/project \
  --device wdt \
  --model github_copilot/gpt-4.1

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
```

## Scoring Criteria

### Code Quality (90 points)

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

1. **Documentation Usage** (threshold: 0.8)
   - Proactive reading
   - Relevant sections
   - Best practices applied
   - Efficiency
   - Problem solving

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
