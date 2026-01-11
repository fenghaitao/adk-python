# Copyright 2025 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""MLflow tracking integration for deepeval scoring."""

from __future__ import annotations

import json
import os
import tempfile
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, Optional, Any

import mlflow
import yaml


class MLflowTracker:
  """Handles MLflow tracking for deepeval scoring experiments."""
  
  def __init__(
      self,
      config_path: Optional[str] = None,
      tracking_uri: Optional[str] = None,
      experiment_name: Optional[str] = None
  ):
    """Initialize MLflow tracker.
    
    Args:
      config_path: Path to MLflow configuration file
      tracking_uri: MLflow tracking URI (overrides config)
      experiment_name: Experiment name (overrides config pattern)
    """
    self.config = self._load_config(config_path)
    self.tracking_uri = tracking_uri or self.config["mlflow"]["tracking_uri"]
    self.experiment_name = experiment_name
    self.run_id = None
    self.start_time = None
    
    # Set up MLflow
    mlflow.set_tracking_uri(self.tracking_uri)
    
    # Remove artifact root environment variable setting since it's not needed with file-based tracking
  
  def _load_config(self, config_path: Optional[str]) -> Dict[str, Any]:
    """Load MLflow configuration."""
    if config_path is None:
      # Default config path relative to this file
      config_path = Path(__file__).parent.parent / "config" / "mlflow_config.yaml"
    
    try:
      with open(config_path, 'r') as f:
        config = yaml.safe_load(f)
      
      # Resolve PROJECT_ROOT placeholder in tracking_uri
      if "{{ PROJECT_ROOT }}" in config["mlflow"]["tracking_uri"]:
        project_root = Path(__file__).parent.parent.parent  # Go up to adk-python root
        tracking_uri = config["mlflow"]["tracking_uri"].replace(
          "{{ PROJECT_ROOT }}", str(project_root)
        )
        config["mlflow"]["tracking_uri"] = tracking_uri
        
        # For file-based tracking, ensure the directory exists
        if tracking_uri.startswith("file://"):
          mlruns_path = Path(tracking_uri.replace("file://", ""))
          mlruns_path.mkdir(parents=True, exist_ok=True)
      
      return config
    except FileNotFoundError:
      # Return default configuration if file not found
      project_root = Path(__file__).parent.parent.parent
      return {
        "mlflow": {
          "tracking_uri": f"file://{project_root}/deepeval-scoring/mlruns",
          "experiment_naming": "{device_name}-evaluation",
          "auto_log_artifacts": True,
          "log_system_metrics": True,
          "default_tags": {
            "project": "adk-python",
            "component": "deepeval-scoring"
          },
          "metrics": {
            "log_component_scores": True,
            "log_timing_metrics": True,
            "log_model_metadata": True
          },
          "artifacts": {
            "log_reports": True,
            "log_raw_results": True
          }
        }
      }
  
  def start_run(
      self,
      device_name: str,
      model: str,
      scoring_mode: str,
      workdir: str,
      agent: Optional[str] = None,
      **kwargs
  ) -> str:
    """Start a new MLflow run.
    
    Args:
      device_name: Device being evaluated
      model: Model used for evaluation
      scoring_mode: Scoring mode (llm, deterministic, hybrid)
      workdir: Working directory path
      agent: Agent type (optional)
      **kwargs: Additional parameters to log
    
    Returns:
      MLflow run ID
    """
    # Create or get experiment
    if self.experiment_name:
      experiment_name = self.experiment_name
    else:
      experiment_name = self.config["mlflow"]["experiment_naming"].format(
        device_name=device_name
      )
    
    try:
      experiment = mlflow.get_experiment_by_name(experiment_name)
      if experiment is None:
        experiment_id = mlflow.create_experiment(experiment_name)
      else:
        experiment_id = experiment.experiment_id
    except Exception:
      # Fallback to default experiment
      experiment_id = "0"
    
    # Start run
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    run_name = f"{timestamp}_{model.replace('/', '_')}_{scoring_mode}"
    
    run = mlflow.start_run(
      experiment_id=experiment_id,
      run_name=run_name
    )
    
    self.run_id = run.info.run_id
    self.start_time = time.time()
    
    # Log parameters
    params = {
      "device_name": device_name,
      "model": model,
      "scoring_mode": scoring_mode,
      "workdir": workdir,
      "timestamp": timestamp,
    }
    
    if agent:
      params["agent"] = agent
    
    # Add any additional parameters
    params.update(kwargs)
    
    mlflow.log_params(params)
    
    # Log default tags
    tags = self.config["mlflow"]["default_tags"].copy()
    tags.update({
      "device_name": device_name,
      "model": model,
      "scoring_mode": scoring_mode,
    })
    
    if agent:
      tags["agent"] = agent
    
    mlflow.set_tags(tags)
    
    print(f"🔬 Started MLflow run: {self.run_id}")
    print(f"📊 Experiment: {experiment_name}")
    
    return self.run_id
  
  def log_metrics(
      self,
      code_results: Optional[Dict] = None,
      behavior_results: Optional[Dict] = None,
      deterministic_results: Optional[Dict] = None,
      scoring_mode: str = "llm"
  ):
    """Log evaluation metrics to MLflow.
    
    Args:
      code_results: LLM-based code evaluation results
      behavior_results: Behavior evaluation results  
      deterministic_results: Deterministic evaluation results
      scoring_mode: Scoring mode used
    """
    if not self.run_id:
      raise RuntimeError("No active MLflow run. Call start_run() first.")
    
    metrics = {}
    
    # Log deterministic metrics
    if deterministic_results:
      metrics["deterministic_overall_score"] = deterministic_results["overall_score"]
      
      # Log component scores with prefix
      for component, score in deterministic_results["component_scores"].items():
        metrics[f"deterministic_{component}"] = score
      
      # Log implementation details as metrics
      details = deterministic_results.get("details", {})
      metrics["registers_found"] = details.get("registers_found", 0)
      metrics["methods_found"] = details.get("methods_found", 0)
      metrics["events_found"] = details.get("events_found", 0)
      metrics["test_files_found"] = details.get("test_files_found", 0)
    
    # Log LLM code quality metrics
    if code_results:
      metrics["llm_code_overall_score"] = code_results["overall_score"]
      
      # Log individual metric scores
      for metric_name, result in code_results["metrics"].items():
        # Sanitize metric name for MLflow (remove invalid characters)
        clean_name = metric_name.replace("[", "").replace("]", "").replace(" ", "_")
        metrics[f"llm_code_{clean_name}_score"] = result["score"]
        metrics[f"llm_code_{clean_name}_success"] = 1.0 if result["success"] else 0.0
    
    # Log behavior metrics
    if behavior_results:
      metrics["behavior_overall_score"] = behavior_results["overall_score"]
      
      # Log individual behavior metric scores
      for metric_name, result in behavior_results["metrics"].items():
        # Sanitize metric name for MLflow (remove invalid characters)
        clean_name = metric_name.replace("[", "").replace("]", "").replace(" ", "_")
        metrics[f"behavior_{clean_name}_score"] = result["score"]
        metrics[f"behavior_{clean_name}_success"] = 1.0 if result["success"] else 0.0
    
    # Calculate and log overall score
    overall_score = self._calculate_overall_score(
      code_results, behavior_results, deterministic_results, scoring_mode
    )
    metrics["overall_score"] = overall_score
    
    # Log timing metrics if enabled
    if self.config["mlflow"]["metrics"]["log_timing_metrics"] and self.start_time:
      metrics["evaluation_duration_seconds"] = time.time() - self.start_time
    
    # Log all metrics
    mlflow.log_metrics(metrics)
    
    print(f"📈 Logged {len(metrics)} metrics to MLflow")
  
  def log_artifacts(
      self,
      workdir: str,
      code_results: Optional[Dict] = None,
      behavior_results: Optional[Dict] = None,
      deterministic_results: Optional[Dict] = None
  ):
    """Log artifacts to MLflow.
    
    Args:
      workdir: Working directory path
      code_results: Code evaluation results
      behavior_results: Behavior evaluation results
      deterministic_results: Deterministic evaluation results
    """
    if not self.run_id:
      raise RuntimeError("No active MLflow run. Call start_run() first.")
    
    artifacts_config = self.config["mlflow"]["artifacts"]
    
    with tempfile.TemporaryDirectory() as temp_dir:
      temp_path = Path(temp_dir)
      
      # Log the actual score.md file if it exists in workdir
      if artifacts_config.get("log_score_file", True):
        score_file_path = Path(workdir) / "score.md"
        if score_file_path.exists():
          mlflow.log_artifact(str(score_file_path), "reports")
      
      # Log raw results as JSON
      if artifacts_config.get("log_raw_results", True):
        raw_results = {
          "code_results": code_results,
          "behavior_results": behavior_results,
          "deterministic_results": deterministic_results,
          "timestamp": datetime.now().isoformat(),
        }
        
        results_file = temp_path / "raw_results.json"
        results_file.write_text(json.dumps(raw_results, indent=2))
        mlflow.log_artifact(str(results_file), "results")
      
      # Log session data for optimizer (NEW)
      if artifacts_config.get("log_session_data", True):
        session_data = self._collect_session_data(
          workdir, code_results, behavior_results, deterministic_results
        )
        if session_data:
          session_file = temp_path / "session_data.json"
          session_file.write_text(json.dumps(session_data, indent=2))
          mlflow.log_artifact(str(session_file), "session_data")
          print("📊 Logged session data for optimizer")
      
      # Log session logs if they exist
      if artifacts_config.get("log_session_logs", True):
        session_logs_dir = Path(workdir) / ".deepeval"
        if session_logs_dir.exists():
          for log_file in session_logs_dir.glob("*.log"):
            mlflow.log_artifact(str(log_file), "logs")
        
        # Also look for session logs in workdir root
        for log_file in Path(workdir).glob("*.session.txt"):
          mlflow.log_artifact(str(log_file), "logs")
      
      # Log implementation files (NEW)
      if artifacts_config.get("log_implementation_files", True):
        self._log_implementation_files(workdir, temp_path)
      
      # Log configuration files
      if artifacts_config.get("log_config_files", True):
        config_file = temp_path / "mlflow_config.yaml"
        config_file.write_text(yaml.dump(self.config, default_flow_style=False))
        mlflow.log_artifact(str(config_file), "config")
    
    print("📁 Logged artifacts to MLflow")
  
  def _collect_session_data(
      self,
      workdir: str,
      code_results: Optional[Dict],
      behavior_results: Optional[Dict],
      deterministic_results: Optional[Dict]
  ) -> Optional[Dict]:
    """Collect session data in format needed for optimizer.
    
    This creates a session data structure compatible with collect_session_data.py
    output, so MLflow artifacts can be used directly for optimization.
    
    Args:
      workdir: Working directory path
      code_results: Code evaluation results
      behavior_results: Behavior evaluation results
      deterministic_results: Deterministic evaluation results
      
    Returns:
      Session data dictionary or None if data incomplete
    """
    workdir_path = Path(workdir)
    
    # Try to find device name from workdir or results
    device_name = None
    if code_results and 'device_name' in code_results:
      device_name = code_results['device_name']
    else:
      # Try to extract from workdir path
      # Assuming workdir contains simics-project/modules/<device>
      modules_dir = workdir_path / "simics-project" / "modules"
      if modules_dir.exists():
        device_dirs = [d for d in modules_dir.iterdir() if d.is_dir()]
        if device_dirs:
          device_name = device_dirs[0].name
    
    if not device_name:
      return None
    
    # Find implementation file
    dml_file = workdir_path / f"simics-project/modules/{device_name}/{device_name}.dml"
    implementation = ""
    if dml_file.exists():
      implementation = dml_file.read_text()
    
    # Find test files
    test_dir = workdir_path / f"simics-project/modules/{device_name}/test"
    tests_content = ""
    if test_dir.exists():
      test_files = list(test_dir.glob("s-*.py"))
      if test_files:
        tests_content = "\n\n".join([f.read_text() for f in test_files])
    
    # Find spec file
    spec_file = workdir_path / f"specs/{device_name}/spec.md"
    spec_content = ""
    if spec_file.exists():
      spec_content = spec_file.read_text()
    
    # Find session log
    session_log = ""
    session_files = list(workdir_path.glob("*.session.txt"))
    if session_files:
      session_log = session_files[0].read_text()
    
    # Extract task description from spec or session log
    task_description = f"Implement {device_name} device"
    if spec_content:
      # Try to extract overview from spec
      lines = spec_content.split('\n')
      for i, line in enumerate(lines):
        if 'overview' in line.lower() or 'description' in line.lower():
          # Take next few lines
          task_description = '\n'.join(lines[i:min(i+5, len(lines))])
          break
    
    # Calculate overall score
    overall_score = self._calculate_overall_score(
      code_results, behavior_results, deterministic_results, "hybrid"
    )
    
    # Build session data structure
    session_data = {
      "device_name": device_name,
      "task_description": task_description,
      "implementation": implementation,
      "tests": tests_content,
      "spec": spec_content,
      "session_log": session_log,
      "score": overall_score,
      "metrics": {
        "code": code_results.get("metrics", {}) if code_results else {},
        "behavior": behavior_results.get("metrics", {}) if behavior_results else {},
        "deterministic": deterministic_results.get("component_scores", {}) if deterministic_results else {}
      },
      "dml_components": deterministic_results.get("details", {}) if deterministic_results else {},
      "num_test_files": len(list(test_dir.glob("s-*.py"))) if test_dir.exists() else 0,
      "timestamp": datetime.now().isoformat(),
      "mlflow_run_id": self.run_id
    }
    
    return session_data
  
  def _log_implementation_files(self, workdir: str, temp_path: Path):
    """Log implementation and test files as artifacts.
    
    Args:
      workdir: Working directory path
      temp_path: Temporary directory for staging files
    """
    workdir_path = Path(workdir)
    
    # Find simics-project directory
    simics_project = workdir_path / "simics-project"
    if not simics_project.exists():
      return
    
    # Find modules
    modules_dir = simics_project / "modules"
    if not modules_dir.exists():
      return
    
    # Log each device module
    for device_dir in modules_dir.iterdir():
      if not device_dir.is_dir():
        continue
      
      device_name = device_dir.name
      
      # Log DML file
      dml_file = device_dir / f"{device_name}.dml"
      if dml_file.exists():
        mlflow.log_artifact(str(dml_file), f"implementation/{device_name}")
      
      # Log test files
      test_dir = device_dir / "test"
      if test_dir.exists():
        for test_file in test_dir.glob("*.py"):
          mlflow.log_artifact(str(test_file), f"implementation/{device_name}/test")
  
  def end_run(self, status: str = "FINISHED"):
    """End the current MLflow run.
    
    Args:
      status: Run status (FINISHED, FAILED, KILLED)
    """
    if self.run_id:
      # Log final timing
      if self.start_time:
        total_duration = time.time() - self.start_time
        mlflow.log_metric("total_duration_seconds", total_duration)
      
      mlflow.end_run(status=status)
      print(f"🏁 Ended MLflow run: {self.run_id}")
      self.run_id = None
      self.start_time = None
  
  def _calculate_overall_score(
      self,
      code_results: Optional[Dict],
      behavior_results: Optional[Dict],
      deterministic_results: Optional[Dict],
      scoring_mode: str
  ) -> float:
    """Calculate overall score (same logic as in score.py)."""
    if scoring_mode == "deterministic":
      if deterministic_results:
        return deterministic_results["overall_score"]
      return 0.0
      
    elif scoring_mode == "llm":
      scores = []
      if code_results:
        scores.append(code_results["overall_score"])
      if behavior_results:
        scores.append(behavior_results["overall_score"])
      return sum(scores) / len(scores) if scores else 0.0
      
    elif scoring_mode == "hybrid":
      total_score = 0.0
      total_weight = 0.0
      
      if deterministic_results:
        total_score += deterministic_results["overall_score"] * 0.4
        total_weight += 0.4
      
      if code_results:
        total_score += code_results["overall_score"] * 0.4
        total_weight += 0.4
      
      if behavior_results:
        total_score += behavior_results["overall_score"] * 0.2
        total_weight += 0.2
      
      return total_score / total_weight if total_weight > 0 else 0.0
    
    return 0.0
  
  def get_tracking_uri(self) -> str:
    """Get the current tracking URI."""
    return self.tracking_uri
  
  def get_run_id(self) -> Optional[str]:
    """Get the current run ID."""
    return self.run_id