# Multi-Workdir Collection & MLflow Tracking Guide

## Overview

The session collection and prompt optimization system has been enhanced with two major features:

1. **Multi-Workdir Aggregation**: Collect session data from multiple project directories and aggregate them into a single dataset
2. **MLflow Tracking**: Track and trace all collection and optimization experiments with comprehensive metrics and artifacts

## Features

### 1. Multi-Workdir Session Collection

#### Problem Solved
- Single workdirs typically have only 3-4 sessions, which is insufficient for effective optimization (10+ sessions recommended)
- Solution: Aggregate sessions from multiple experiment workdirs into a single training dataset

#### Usage

**Single Workdir (Original):**
```bash
python collect_session_data.py \
  --workdir /path/to/project \
  --output historical_sessions.json \
  --min-score 0.5
```

**Multiple Workdirs (New):**
```bash
python collect_session_data.py \
  --workdirs /path/to/project1 /path/to/project2 /path/to/project3 \
  --output historical_sessions.json \
  --min-score 0.5
```

**Via run_test.sh with EXTRA_WORKDIRS:**
```bash
EXTRA_WORKDIRS="/path/to/proj1 /path/to/proj2" ./run_test.sh my_project 2
```

#### Output
- Aggregated sessions from all workdirs
- Per-workdir statistics showing collection success/failure
- Source workdir tracked in each session's metadata

### 2. MLflow Integration

#### Tracking Features

**Session Collection Metrics:**
- `total_sessions`: Total sessions collected
- `avg_score`, `min_score`, `max_score`: Score statistics
- `num_workspaces`: Number of workdirs scanned
- `num_devices`: Unique device types
- `collection_time_seconds`: Collection duration
- Per-workdir stats: `workdir_<name>_collected`, `workdir_<name>_skipped`
- Per-device counts: `device_<name>_count`

**Optimization Metrics:**
- `num_sessions`: Sessions used for training
- `iterations`: Optimization iterations
- `optimization_time_seconds`: Optimization duration
- `original_lines`, `optimized_lines`: Instruction file sizes
- `lines_change`, `chars_change`: Delta metrics
- Weight parameters: `weight_correctness`, `weight_coverage`, etc.

**Artifacts Logged:**
- Input: `historical_sessions.json`, current instructions
- Output: Optimized instructions, diff file
- Statistics: Per-workdir collection stats (JSON)

#### Usage

**Collection with MLflow:**
```bash
python collect_session_data.py \
  --workdirs /path/to/proj1 /path/to/proj2 \
  --output historical_sessions.json \
  --scoring-mode hybrid \
  --mlflow \
  --mlflow-experiment-name "session-collection-2026-01"
```

**Different Scoring Modes:**
```bash
# Hybrid mode (default): 40% deterministic + 40% LLM code + 20% behavior
python collect_session_data.py \
  --workdirs /path/to/proj1 /path/to/proj2 \
  --output sessions.json \
  --scoring-mode hybrid

# Deterministic only: Fast, parser-based scoring
python collect_session_data.py \
  --workdirs /path/to/proj1 /path/to/proj2 \
  --output sessions.json \
  --scoring-mode deterministic

# LLM only: Comprehensive but slower
python collect_session_data.py \
  --workdirs /path/to/proj1 /path/to/proj2 \
  --output sessions.json \
  --scoring-mode llm
```

**Optimization with MLflow:**
```bash
python optimize_instructions.py \
  --historical-data historical_sessions.json \
  --current-instructions apply_agent_instruction.md \
  --output optimized_instructions.md \
  --algorithm copro \
  --iterations 5 \
  --mlflow \
  --mlflow-experiment-name "copro-optimization-2026-01"
```

**Via run_test.sh:**
```bash
ENABLE_MLFLOW=1 EXTRA_WORKDIRS="/path/to/proj1 /path/to/proj2" ./run_test.sh my_project 2
```

## Environment Variables (run_test.sh)

### Existing
- `SKIP_COLLECT=1`: Skip session data collection, use existing file
- `SKIP_OPTIMIZE=1`: Skip optimization, only collect data
- `FORCE_OPTIMIZE=1`: Force optimization with insufficient sessions
- `MIN_SESSIONS=N`: Set minimum session threshold (default: 5)
- `MAX_CONCURRENT=N`: Set max concurrent API calls (default: 1)
- `THROTTLE_SECONDS=N`: Set throttle delay (default: 30.0)

### New
- `EXTRA_WORKDIRS="<paths>"`: Space-separated additional workdirs to collect from
- `ENABLE_MLFLOW=1`: Enable MLflow tracking for both collection and optimization
- `SCORING_MODE=<mode>`: Set scoring mode - llm, deterministic, or hybrid (default: hybrid)

## Example Workflows

### Workflow 1: Collect from Multiple Projects

```bash
# Collect sessions from 3 different experiments
EXTRA_WORKDIRS="$HOME/experiment1/adk_openspec_project $HOME/experiment2/adk_openspec_project" \
  ./run_test.sh my_aggregated_project 2
```

### Workflow 2: Full Pipeline with MLflow

```bash
# Stage 0-2 with MLflow tracking and multi-workdir collection
ENABLE_MLFLOW=1 \
  EXTRA_WORKDIRS="$HOME/exp1/adk_openspec_project $HOME/exp2/adk_openspec_project" \
  ./run_test.sh my_project "0,1,2"
```

### Workflow 3: Collection-Only with MLflow

```bash
# Only collect and track, skip optimization
ENABLE_MLFLOW=1 \
  SKIP_OPTIMIZE=1 \
  SCORING_MODE=hybrid \
  EXTRA_WORKDIRS="/path/to/proj1 /path/to/proj2 /path/to/proj3" \
  ./run_test.sh my_project 2
```

### Workflow 4: Fast Collection with Deterministic Scoring

```bash
# Use deterministic scoring for faster collection (no LLM calls)
SCORING_MODE=deterministic \
  EXTRA_WORKDIRS="/path/to/proj1 /path/to/proj2" \
  ./run_test.sh my_project 2
```

### Workflow 5: Standalone Collection

```bash
# Directly use collect_session_data.py for maximum control
python deepeval-scoring/collect_session_data.py \
  --workdirs \
    ~/simics-skills/myproject/openspec \
    ~/simics-skills/myproject2/openspec \
    ~/simics-skills/myproject3/openspec \
    ~/simics-skills/myproject4/openspec \
  --output aggregated_sessions.json \
  --min-score 0.6 \
  --model "github_copilot/gpt-4o" \
  --mlflow \
  --mlflow-experiment-name "multi-project-collection-2026-01"
```

## Benefits

### Multi-Workdir Collection
✅ Solves insufficient training data problem (10+ sessions)
✅ Aggregates successful sessions across multiple experiments
✅ Tracks source workdir for each session
✅ Provides detailed per-workdir statistics

### Comprehensive Scoring Modes
The scoring system now supports three modes, matching `score.py`:

**1. Hybrid Mode (Default - Recommended)**
- **Weight**: 40% deterministic + 40% LLM code + 20% behavior
- **Best for**: Balanced evaluation with objective and subjective metrics
- **Speed**: Moderate (includes LLM calls)
- **Usage**: `--scoring-mode hybrid` or `SCORING_MODE=hybrid`

**2. Deterministic Mode**
- **Weight**: 100% parser-based metrics
- **Best for**: Fast collection, objective metrics only
- **Speed**: Very fast (no LLM calls)
- **Metrics**: Register coverage, bank structure, connect implementation, import completeness, reset logic
- **Usage**: `--scoring-mode deterministic` or `SCORING_MODE=deterministic`

**3. LLM Mode**
- **Weight**: 50% LLM code quality + 50% behavior
- **Best for**: Comprehensive subjective evaluation
- **Speed**: Slow (multiple LLM calls per session)
- **Metrics**: Code correctness, test coverage, code style, agent behavior
- **Usage**: `--scoring-mode llm` or `SCORING_MODE=llm`

### MLflow Tracking
✅ Complete experiment tracking and reproducibility
✅ Compare different optimization runs
✅ Track parameter impact on results
✅ Store all artifacts (sessions, instructions, diffs)
✅ Visualize metrics over time

## MLflow UI

View tracked experiments:
```bash
cd $ADK_ROOT/deepeval-scoring
mlflow ui
# Open http://localhost:5000
```

## Architecture

```
collect_session_data.py
├── Multi-workdir support (--workdirs)
├── MLflow integration
│   ├── Track collection metrics
│   ├── Log per-workdir stats
│   ├── Store session artifacts
│   └── End run with status
└── Aggregate sessions with source tracking

optimize_instructions.py
├── MLflow integration
│   ├── Track optimization parameters
│   ├── Log iteration metrics
│   ├── Store instruction artifacts
│   ├── Generate and log diff
│   └── End run with status
└── Use aggregated session dataset

run_test.sh (Stage 2)
├── EXTRA_WORKDIRS support
├── ENABLE_MLFLOW flag
└── Pass through to Python scripts
```

## Configuration

MLflow configuration is loaded from `deepeval-scoring/config/mlflow_config.yaml`:
```yaml
mlflow:
  tracking_uri: "file://{{ PROJECT_ROOT }}/deepeval-scoring/mlruns"
  experiment_naming: "{device_name}-evaluation"
  auto_log_artifacts: true
  log_system_metrics: true
```

## Troubleshooting

### Issue: "No sessions found"
**Solution**: Verify session files exist with pattern `**/*.session.txt` in workdirs

### Issue: "MLflow not available"
**Solution**: `pip install mlflow`

### Issue: "Insufficient sessions" (< 10)
**Solutions**:
1. Add more workdirs via `EXTRA_WORKDIRS`
2. Use `FORCE_OPTIMIZE=1` to bypass check
3. Lower threshold with `MIN_SESSIONS=5`

### Issue: Rate limiting errors
**Solutions**:
1. Increase `THROTTLE_SECONDS=60`
2. Decrease `MAX_CONCURRENT=1`
3. Use `--no-async` flag

## Next Steps

1. Run multi-workdir collection to build sufficient training data (10+ sessions)
2. Enable MLflow to track all experiments
3. Compare different optimization algorithms (copro, miprov2, gepa, simba)
4. Analyze metrics in MLflow UI to identify best configurations
5. Deploy optimized instructions and measure improvement

## References

- DeepEval Documentation: https://docs.confident-ai.com/
- MLflow Documentation: https://mlflow.org/docs/latest/index.html
- COPRO Algorithm: Contextual Prompt Optimization
