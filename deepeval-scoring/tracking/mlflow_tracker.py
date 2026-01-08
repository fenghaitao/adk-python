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
    
    # Set artifact root if specified
    if "artifact_root" in self.config["mlflow"]:
      import os
      os.environ["MLFLOW_DEFAULT_ARTIFACT_ROOT"] = self.config["mlflow"]["artifact_root"]
  
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
      
      # Resolve PROJECT_ROOT placeholder in artifact_root
      if "artifact_root" in config["mlflow"] and "{{ PROJECT_ROOT }}" in config["mlflow"]["artifact_root"]:
        project_root = Path(__file__).parent.parent.parent  # Go up to adk-python root
        artifact_root = config["mlflow"]["artifact_root"].replace(
          "{{ PROJECT_ROOT }}", str(project_root)
        )
        config["mlflow"]["artifact_root"] = artifact_root
      
      return config
    except FileNotFoundError:
      # Return default configuration if file not found
      project_root = Path(__file__).parent.parent.parent
      return {
        "mlflow": {
          "tracking_uri": f"sqlite:///{project_root}/deepeval-scoring/mlflow.db",
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
      
      # Log session logs if they exist
      if artifacts_config.get("log_session_logs", True):
        session_logs_dir = Path(workdir) / ".deepeval"
        if session_logs_dir.exists():
          for log_file in session_logs_dir.glob("*.log"):
            mlflow.log_artifact(str(log_file), "logs")
      
      # Log configuration files
      if artifacts_config.get("log_config_files", True):
        config_file = temp_path / "mlflow_config.yaml"
        config_file.write_text(yaml.dump(self.config, default_flow_style=False))
        mlflow.log_artifact(str(config_file), "config")
    
    print("📁 Logged artifacts to MLflow")
  
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