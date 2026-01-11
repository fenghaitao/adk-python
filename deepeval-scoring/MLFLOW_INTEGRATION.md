# MLflow Integration Guide

This document describes the MLflow integration for the DeepEval scoring system, which enables experiment tracking, artifact logging, and seamless integration with the optimization workflow.

## Overview

The MLflow integration automatically logs:
- **Metrics**: All evaluation scores (deterministic, LLM-based, behavior)
- **Parameters**: Device name, model, scoring mode, workdir, agent type
- **Artifacts**: 
  - Session data (for optimizer)
  - Implementation files (DML, tests)
  - Session logs
  - Score reports
  - Raw results (JSON)
  - Configuration files

## Quick Start

### Enable MLflow Tracking

```bash
# Run scoring with MLflow enabled
python score.py \
  --workdir /path/to/project \
  --device wdt \
  --model iflow/qwen3-coder-plus \
  --agent kiro-cli \
  --mlflow
```

### View Results

```bash
# Start MLflow UI
cd deepeval-scoring
mlflow ui

# Open browser to http://localhost:5000
```

## Configuration

MLflow settings are configured in `config/mlflow_config.yaml`:

```yaml
mlflow:
  # Tracking URI - where MLflow stores data
  tracking_uri: "file://{{ PROJECT_ROOT }}/deepeval-scoring/mlruns"
  
  # Experiment naming pattern
  experiment_naming: "{device_name}-evaluation"
  
  # Artifact logging settings
  artifacts:
    log_raw_results: true
    log_session_logs: true
    log_config_files: true
    log_score_file: true
    log_session_data: true  # For optimizer
    log_implementation_files: true  # DML and test files
```

### Override Configuration

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
  --mlflow-experiment-name my-custom-experiment
```

## Artifact Structure

Each MLflow run logs the following artifacts:

```
artifacts/
├── session_data/
│   └── session_data.json       # Session data for optimizer
├── implementation/
│   └── {device_name}/
│       ├── {device_name}.dml   # DML implementation
│       └── test/
│           └── s-*.py          # Test files
├── logs/
│   └── *.session.txt           # Session logs
├── reports/
│   └── score.md                # Score report
├── results/
│   └── raw_results.json        # Raw evaluation results
└── config/
    └── mlflow_config.yaml      # MLflow configuration
```

## Session Data Format

The `session_data.json` artifact contains data in the format expected by the optimizer tools:

```json
{
  "device_name": "wdt",
  "task_description": "Implement wdt device",
  "implementation": "// DML code...",
  "tests": "# Test code...",
  "spec": "# Spec content...",
  "session_log": "Session log content...",
  "score": 0.887,
  "metrics": {
    "code": {...},
    "behavior": {...},
    "deterministic": {...}
  },
  "dml_components": {...},
  "num_test_files": 3,
  "timestamp": "2025-01-11T10:30:00",
  "mlflow_run_id": "abc123..."
}
```

## Integration with Optimizer

### Extract Sessions from MLflow

Use `extract_mlflow_sessions.py` to extract session data from MLflow runs:

```bash
# Extract all sessions from an experiment
python extract_mlflow_sessions.py \
  --experiment wdt-evaluation \
  --output sessions.json

# Extract only low-scoring sessions (for optimization)
python extract_mlflow_sessions.py \
  --experiment wdt-evaluation \
  --max-score 0.8 \
  --output low_score_sessions.json

# Extract specific runs
python extract_mlflow_sessions.py \
  --run-ids abc123,def456 \
  --output sessions.json
```

### Optimize Instructions

```bash
# 1. Extract low-scoring sessions
python extract_mlflow_sessions.py \
  --experiment wdt-evaluation \
  --max-score 0.8 \
  --output sessions.json

# 2. Optimize instructions
python optimize_instructions.py \
  --sessions sessions.json \
  --instructions ../contributing/samples/openspec_integration/apply_agent_instruction.md \
  --output optimized_instructions.md \
  --algorithm miprov2
```

### Optimize Memory Files

```bash
# 1. Extract sessions
python extract_mlflow_sessions.py \
  --experiment wdt-evaluation \
  --output sessions.json

# 2. Analyze memory effectiveness
python analyze_memory_effectiveness.py \
  --sessions sessions.json \
  --memory-dir ../openspec-memories/dml

# 3. Optimize specific memory file
python optimize_memory_file.py \
  --sessions sessions.json \
  --memory-file ../openspec-memories/dml/01_dml_syntax_errors.md \
  --output optimized_memory.md
```

### Identify Memory Gaps

```bash
# 1. Extract sessions
python extract_mlflow_sessions.py \
  --experiment wdt-evaluation \
  --output sessions.json

# 2. Identify gaps
python identify_memory_gaps.py \
  --sessions sessions.json \
  --memory-dir ../openspec-memories/dml \
  --output gaps.json

# 3. Generate new memory files
python generate_memory_file.py \
  --gap-analysis gaps.json \
  --gap-id 0 \
  --output new_memory.md
```

## Metrics Logged

### Deterministic Metrics
- `deterministic_overall_score`: Overall deterministic score
- `deterministic_registers`: Register implementation score
- `deterministic_methods`: Method implementation score
- `deterministic_events`: Event implementation score
- `deterministic_tests`: Test coverage score
- `registers_found`: Number of registers found
- `methods_found`: Number of methods found
- `events_found`: Number of events found
- `test_files_found`: Number of test files found

### LLM Code Quality Metrics
- `llm_code_overall_score`: Overall LLM code quality score
- `llm_code_Code_Correctness_score`: Correctness score
- `llm_code_Test_Coverage_score`: Test coverage score
- `llm_code_Code_Style_score`: Code style score

### Behavior Metrics
- `behavior_overall_score`: Overall behavior score
- `behavior_Agent_Behavior_score`: Agent behavior score

### Overall Metrics
- `overall_score`: Final combined score
- `evaluation_duration_seconds`: Time taken for evaluation
- `total_duration_seconds`: Total run duration

## Parameters Logged

- `device_name`: Device being evaluated
- `model`: LLM model used
- `scoring_mode`: Scoring mode (llm, deterministic, hybrid)
- `workdir`: Working directory path
- `agent`: Agent type (if specified)
- `timestamp`: Run timestamp
- `result_only`: Whether behavior evaluation was skipped
- `behavior_only`: Whether code evaluation was skipped
- `reference_dir`: Reference directory (if used)

## Tags

Default tags applied to all runs:
- `project`: adk-python
- `component`: deepeval-scoring
- `framework`: deepeval
- `device_name`: Device name
- `model`: Model name
- `scoring_mode`: Scoring mode
- `agent`: Agent type (if specified)

## Best Practices

### 1. Consistent Experiment Naming
Use the same experiment name for related evaluations:
```bash
--mlflow-experiment-name wdt-evaluation
```

### 2. Filter Sessions for Optimization
Extract only relevant sessions for optimization:
```bash
# Low-scoring sessions for instruction optimization
python extract_mlflow_sessions.py \
  --experiment wdt-evaluation \
  --max-score 0.8 \
  --output sessions.json

# High-scoring sessions for reference
python extract_mlflow_sessions.py \
  --experiment wdt-evaluation \
  --min-score 0.9 \
  --output reference_sessions.json
```

### 3. Track Optimization Iterations
Create separate experiments for optimization iterations:
```bash
# Baseline
python score.py --device wdt --mlflow --mlflow-experiment-name wdt-baseline

# After instruction optimization
python score.py --device wdt --mlflow --mlflow-experiment-name wdt-optimized-v1

# After memory optimization
python score.py --device wdt --mlflow --mlflow-experiment-name wdt-optimized-v2
```

### 4. Compare Results
Use MLflow UI to compare runs across experiments and track improvement over time.

## Troubleshooting

### MLflow Not Available
```bash
pip install mlflow
```

### Tracking URI Issues
Ensure the tracking URI directory exists and is writable:
```bash
mkdir -p deepeval-scoring/mlruns
```

### Missing Artifacts
Check that artifact logging is enabled in `config/mlflow_config.yaml`:
```yaml
artifacts:
  log_session_data: true
  log_implementation_files: true
```

### Session Data Extraction Fails
Ensure the run has the `session_data/session_data.json` artifact:
```bash
# List artifacts for a run
mlflow artifacts list --run-id <run_id>
```

## Advanced Usage

### Custom Tracking URI
Use a remote MLflow server:
```bash
python score.py \
  --device wdt \
  --mlflow \
  --mlflow-tracking-uri http://mlflow-server:5000
```

### Programmatic Access
```python
from tracking.mlflow_tracker import MLflowTracker

# Initialize tracker
tracker = MLflowTracker()

# Start run
tracker.start_run(
  device_name="wdt",
  model="iflow/qwen3-coder-plus",
  scoring_mode="hybrid",
  workdir="/path/to/project"
)

# Log metrics
tracker.log_metrics(
  code_results=code_results,
  behavior_results=behavior_results,
  deterministic_results=deterministic_results,
  scoring_mode="hybrid"
)

# Log artifacts
tracker.log_artifacts(
  workdir="/path/to/project",
  code_results=code_results,
  behavior_results=behavior_results,
  deterministic_results=deterministic_results
)

# End run
tracker.end_run(status="FINISHED")
```

## See Also

- [QUICKSTART.md](QUICKSTART.md) - Getting started with scoring
- [MEMORY_FILE_OPTIMIZATION_GUIDE.md](MEMORY_FILE_OPTIMIZATION_GUIDE.md) - Memory file optimization
- [optimize_instructions.py](optimize_instructions.py) - Instruction optimization
- [MLflow Documentation](https://mlflow.org/docs/latest/index.html)
