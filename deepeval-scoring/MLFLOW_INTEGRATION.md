# MLflow Integration for DeepEval Scoring

## Overview

This document describes the MLflow integration added to the deepeval-scoring system for experiment tracking and result management.

## Features Implemented

### Core Integration
- **MLflowTracker**: Main class for tracking experiments, metrics, and artifacts
- **ExperimentManager**: Utilities for managing and comparing experiments
- **Configuration**: YAML-based configuration for MLflow settings
- **CLI Integration**: New command-line flags for MLflow functionality

### Key Capabilities
1. **Experiment Tracking**: Automatically organize runs by device and configuration
2. **Metrics Logging**: Track all evaluation scores (deterministic, LLM, behavior)
3. **Artifact Storage**: Store reports, raw results, and session logs
4. **Run Comparison**: Compare performance across different models and configurations
5. **Historical Analysis**: Track performance trends over time

## File Structure

```
deepeval-scoring/
├── tracking/                   # MLflow integration
│   ├── __init__.py
│   ├── mlflow_tracker.py      # Main tracking class
│   ├── experiment_manager.py  # Experiment management
│   └── utils.py              # Helper functions
├── config/
│   └── mlflow_config.yaml    # MLflow configuration
├── scripts/                   # Utility scripts
│   ├── compare_experiments.py # Compare runs and experiments
│   ├── export_results.py     # Export results to CSV/JSON
│   └── demo_mlflow.py        # Demonstration script
└── tests/
    └── test_mlflow_integration.py # Basic tests
```

## Usage Examples

### Basic Usage
```bash
# Enable MLflow tracking
python score.py --workdir /path --device wdt --model iflow/qwen3 --mlflow

# Custom tracking URI
python score.py --workdir /path --device wdt --model iflow/qwen3 \
  --mlflow --mlflow-tracking-uri http://localhost:5000

# Custom experiment name
python score.py --workdir /path --device wdt --model iflow/qwen3 \
  --mlflow --mlflow-experiment-name "wdt-evaluation-v2"
```

### Experiment Management
```bash
# List all experiments
python scripts/compare_experiments.py --list-experiments

# Compare runs
python scripts/compare_experiments.py --runs run_id_1 run_id_2

# Export results
python scripts/export_results.py --experiment "wdt-evaluation" --output results.csv
```

## Metrics Tracked

### Deterministic Metrics
- `deterministic_overall_score`: Overall deterministic score
- `deterministic_build_success`: Build success score
- `deterministic_register_coverage`: Register coverage score
- `deterministic_test_coverage`: Test coverage score
- `registers_found`: Number of registers found
- `methods_found`: Number of methods found
- `test_files_found`: Number of test files found

### LLM Code Quality Metrics
- `llm_code_overall_score`: Overall LLM code quality score
- `llm_code_code_correctness_score`: Code correctness score
- `llm_code_test_coverage_score`: Test coverage score
- `llm_code_code_style_score`: Code style score

### Behavior Metrics
- `behavior_overall_score`: Overall behavior score
- `behavior_*_score`: Individual behavior metric scores

### System Metrics
- `overall_score`: Combined overall score
- `evaluation_duration_seconds`: Time taken for evaluation
- `total_duration_seconds`: Total run duration

## Artifacts Stored

1. **Reports**: Generated evaluation reports (markdown, JSON, HTML)
2. **Raw Results**: Complete evaluation data in JSON format
3. **Session Logs**: DeepEval session logs and debugging information
4. **Configuration**: MLflow configuration used for the run

## Configuration

The system uses `config/mlflow_config.yaml` for configuration:

```yaml
mlflow:
  tracking_uri: "file:///tmp/mlruns"
  experiment_naming: "{device_name}-evaluation"
  auto_log_artifacts: true
  log_system_metrics: true
  default_tags:
    project: "adk-python"
    component: "deepeval-scoring"
```

## Integration Points

### In score.py
- Added MLflow CLI arguments
- Integrated tracking into main evaluation workflow
- Error handling for MLflow failures (graceful degradation)

### Backward Compatibility
- MLflow integration is completely optional
- All existing functionality works without MLflow
- No breaking changes to existing APIs

## Testing

- Basic unit tests for core functionality
- Integration tests with temporary MLflow backends
- Demo script for manual testing

## Dependencies

- MLflow (via submodule): Experiment tracking and artifact storage
- PyYAML: Configuration file parsing
- Existing deepeval-scoring dependencies

## Future Enhancements

### Phase 2 (Planned)
- Automated model performance regression detection
- Integration with CI/CD pipelines
- Enhanced experiment comparison utilities

### Phase 3 (Future)
- Trend analysis and performance insights
- Automated alerts for score degradation
- A/B testing capabilities for different models

## Benefits

1. **Historical Tracking**: Compare model performance over time
2. **Experiment Organization**: Organize evaluations by device, model, agent type
3. **Team Collaboration**: Share results across team members
4. **Reproducibility**: Track exact parameters and configurations
5. **Analytics**: Identify trends and performance regressions
6. **Integration**: Easy integration with existing ML workflows

## Notes

- MLflow UI can be started with: `mlflow ui --backend-store-uri <tracking_uri>`
- Default tracking URI is `file:///tmp/mlruns` for local development
- Experiments are automatically named using pattern: `{device_name}-evaluation`
- All MLflow operations include error handling to prevent evaluation failures